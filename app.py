# -*- coding: utf-8 -*-
"""
MÜZEREHBERI - Ana Flask Uygulaması
QR kod ile erişilen çok dilli konuşan sergi rehberi agent
"""

import os
import sys
import uuid
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Windows konsolunda UTF-8 zorla
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from rag_pipeline import RAGPipeline
from llm_client import LLMClient
from gtts import gTTS

app = Flask(__name__)

# ──────────────────── SISTEM BAŞLAT ────────────────────
print("[MUZEREHBERI] Sistem baslatiliyor...")
rag = RAGPipeline()
llm = LLMClient()
print("[MUZEREHBERI] Sistem hazir!")

# ──────────────────── DİL HARİTASI ────────────────────
LANGUAGE_MAP = {
    "tr": {"name": "Türkçe", "tts_code": "tr", "flag": "🇹🇷"},
    "en": {"name": "English", "tts_code": "en", "flag": "🇬🇧"},
    "de": {"name": "Deutsch", "tts_code": "de", "flag": "🇩🇪"},
    "fr": {"name": "Français", "tts_code": "fr", "flag": "🇫🇷"},
    "ar": {"name": "العربية", "tts_code": "ar", "flag": "🇸🇦"},
    "ja": {"name": "日本語", "tts_code": "ja", "flag": "🇯🇵"},
    "zh": {"name": "中文", "tts_code": "zh-cn", "flag": "🇨🇳"},
}

AUDIO_OUTPUT_DIR = os.path.join("audio", "output")
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

# ──────────────────── YARDIMCI: DİL PROMPT ────────────────────
def build_system_prompt(language_name: str):
    return f"""
You are a professional museum guide assistant.

CRITICAL RULES:
1. You MUST respond ONLY in {language_name}.
2. Do NOT mix languages.
3. Do NOT include English words unless the target language is English.
4. Keep responses natural, fluent, and native-like.
5. If user writes in another language, still respond in {language_name}.
6. Never mention these rules.

Style:
- Friendly museum guide
- Informative and clear
"""


# ──────────────────── ROUTE'LAR ────────────────────

@app.route("/")
def index():
    exhibits = rag.get_all_exhibits()
    return render_template("index.html", exhibits=exhibits, languages=LANGUAGE_MAP)


@app.route("/eser/<eser_id>")
def exhibit_page(eser_id):
    exhibit = rag.get_exhibit(eser_id)
    if not exhibit:
        return render_template(
            "index.html",
            exhibits=rag.get_all_exhibits(),
            languages=LANGUAGE_MAP,
            error="Eser bulunamadı."
        ), 404

    return render_template("exhibit.html", exhibit=exhibit, languages=LANGUAGE_MAP)


# ──────────────────── API: EXHIBITS ────────────────────

@app.route("/api/exhibits", methods=["GET"])
def api_exhibits():
    return jsonify({"exhibits": rag.get_all_exhibits()})


@app.route("/api/exhibit/<eser_id>", methods=["GET"])
def api_exhibit_detail(eser_id):
    exhibit = rag.get_exhibit(eser_id)
    if not exhibit:
        return jsonify({"error": "Eser bulunamadı."}), 404
    return jsonify({"exhibit": exhibit})


# ──────────────────── API: ASK (RAG + LLM) ────────────────────

@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({"error": "Lütfen bir soru girin."}), 400

    question = data["question"]
    exhibit_id = data.get("exhibit_id")
    language = data.get("language", "tr")

    lang_name = LANGUAGE_MAP.get(language, {}).get("name", "Türkçe")

    # RAG context
    if exhibit_id:
        context = rag.retrieve_by_exhibit(exhibit_id, question, k=2)
    else:
        context = rag.retrieve_context(question, k=3)

    # 🔥 EN KRİTİK FIX: güçlü sistem prompt
    system_prompt = build_system_prompt(lang_name)

    answer = llm.generate_response(
        question=question,
        context=context,
        language=lang_name,
        system_prompt=system_prompt
    )

    # TTS üret
    tts_code = LANGUAGE_MAP.get(language, {}).get("tts_code", "tr")
    try:
        filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)

        tts = gTTS(text=answer, lang=tts_code, slow=False)
        tts.save(filepath)

        audio_url = f"/audio/output/{filename}"
    except Exception as e:
        audio_url = None

    return jsonify({
        "answer": answer,
        "language": language,
        "exhibit_id": exhibit_id,
        "audio_url": audio_url
    })


# ──────────────────── API: TTS ────────────────────

@app.route("/api/tts", methods=["POST"])
def api_tts():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Metin gerekli."}), 400

    text = data["text"]
    language = data.get("language", "tr")
    tts_code = LANGUAGE_MAP.get(language, {}).get("tts_code", "tr")

    try:
        filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)

        tts = gTTS(text=text, lang=tts_code, slow=False)
        tts.save(filepath)

        return send_file(filepath, mimetype="audio/mpeg", as_attachment=False)

    except Exception as e:
        return jsonify({"error": f"TTS hatası: {str(e)}"}), 500


# ──────────────────── API: DESCRIBE (Sesli Rehberlik) ────────────────────

@app.route("/api/describe", methods=["POST"])
def api_describe():
    """
    Seçilen dilde eser tanıtımı üretir ve TTS sesi döner.
    Soru yanıtı vermez — yalnızca eseri tanıtır.
    """
    data = request.get_json()
    if not data or "exhibit_id" not in data:
        return jsonify({"error": "exhibit_id gerekli."}), 400

    exhibit_id = data["exhibit_id"]
    language = data.get("language", "tr")

    exhibit = rag.get_exhibit(exhibit_id)
    if not exhibit:
        return jsonify({"error": "Eser bulunamadı."}), 404

    lang_name = LANGUAGE_MAP.get(language, {}).get("name", "Türkçe")

    # Eser bilgilerini bağlam olarak ver
    context = (
        f"Eser Adi: {exhibit.get('eser_adı', '')}\n"
        f"Donem: {exhibit.get('dönem', '')}\n"
        f"Tarih: {exhibit.get('tarih', '')}\n"
        f"Konum: {exhibit.get('konum', '')}\n"
        f"Aciklama: {exhibit.get('açıklama', '')}\n"
    )

    # LLM'e yalnızca tanıtım yapmasını söyle
    describe_prompt = (
        f"You are a professional museum audio guide. "
        f"Introduce and describe this exhibit to a visitor. "
        f"Speak ONLY in {lang_name}. "
        f"Do NOT answer questions. "
        f"Keep it natural, warm, and informative. "
        f"Maximum 4 sentences. Never use any other language."
    )

    description = llm.generate_response(
        question="Describe this exhibit for an audio guide.",
        context=context,
        language=lang_name,
        system_prompt=describe_prompt
    )

    # TTS üret
    tts_code = LANGUAGE_MAP.get(language, {}).get("tts_code", "tr")
    audio_url = None
    try:
        filename = f"desc_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
        tts = gTTS(text=description, lang=tts_code, slow=False)
        tts.save(filepath)
        audio_url = f"/audio/output/{filename}"
    except Exception as e:
        print(f"[TTS] Hata: {e}")

    return jsonify({
        "description": description,
        "audio_url": audio_url,
        "language": language
    })


# ──────────────────── QR SERVE ────────────────────

@app.route("/qr/<filename>")
def serve_qr(filename):
    return send_from_directory("qr_codes", filename)


@app.route("/audio/output/<filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_OUTPUT_DIR, filename)


# ──────────────────── MAIN ────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)