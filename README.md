# 🏛️ MÜZEREHBERI — Çok Dilli İnteraktif Sergi Rehberi Agent

> Yapay zeka destekli, çok dilli, sesli müze rehberi. QR kod ile eserlere eriş, seçtiğin dilde dinle, sorularını sor.

---

## 🚀 Özellikler

| Özellik | Açıklama |
|---|---|
| 🌐 **7 Dil Desteği** | Türkçe, İngilizce, Almanca, Fransızca, Arapça, Japonca, Çince |
| 🔊 **Sesli Rehberlik** | Seçilen dilde LLM ile eser tanıtımı + gTTS seslendirme |
| 🎤 **Sesle Soru Sor** | Web Speech API ile sesli soru girişi |
| 💬 **AI Sohbet** | RAG + LLM ile esere özel soru-cevap |
| 📱 **QR Kod** | Her esere ait QR kod ile doğrudan erişim |
| 🔍 **Vektör Arama** | ChromaDB + sentence-transformers ile semantik arama |

---

## 🛠️ Teknoloji Yığını

- **Backend:** Python, Flask
- **LLM:** LM Studio (yerel) — `llm_client.py`
- **RAG:** ChromaDB + `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **TTS:** gTTS (Google Text-to-Speech)
- **STT:** Web Speech API (tarayıcı tabanlı)
- **Frontend:** HTML5, Vanilla CSS (premium dark theme), JavaScript

---

## 📁 Proje Yapısı

```
müzerehberi/
├── app.py              # Flask uygulaması, API endpoint'leri
├── rag_pipeline.py     # RAG: vektör DB yükleme & arama
├── llm_client.py       # LM Studio LLM istemcisi
├── qr_generator.py     # QR kod oluşturma
├── requirements.txt
├── data/               # Eser metin dosyaları (eser1.txt … eser10.txt)
├── qr_codes/           # Üretilen QR kod görselleri
├── templates/
│   ├── index.html      # Ana sayfa — eser listesi
│   └── exhibit.html    # Eser detay sayfası — chat + ses
└── static/
    ├── css/style.css   # Premium dark tema
    └── js/main.js      # Sesli rehberlik, chat, STT mantığı
```

---

## ⚙️ Kurulum

### 1. Gereksinimleri yükle

```bash
pip install -r requirements.txt
```

### 2. LM Studio'yu başlat

LM Studio uygulamasını açıp bir modeli yerel sunucuda çalıştır (varsayılan: `http://localhost:1234`).

### 3. Uygulamayı çalıştır

```bash
python app.py
```

Tarayıcıda aç: **http://127.0.0.1:5000**

---

## 🗺️ Kullanım

1. **Ana sayfa** — 10 müze eserini listeler, arama ve filtreleme yapabilirsin
2. **Eser sayfası** — Eserin detaylarını gör, dil seç
   - 🔊 **Sesli Rehberlik** → seçilen dilde AI açıklaması dinle
   - 🎤 **Sesle Soru Sor** → mikrofona konuş, AI yanıtlasın
   - ✍️ **Yazarak Soru Sor** → chat alanından yaz
3. **QR Kod** — Her eserin QR kodunu tara, doğrudan sayfasına git

---

## 🌍 Desteklenen Diller

🇹🇷 Türkçe · 🇬🇧 English · 🇩🇪 Deutsch · 🇫🇷 Français · 🇸🇦 العربية · 🇯🇵 日本語 · 🇨🇳 中文

---

## 📄 Lisans

MIT License
