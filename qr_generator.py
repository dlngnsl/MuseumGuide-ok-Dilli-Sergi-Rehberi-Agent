# -*- coding: utf-8 -*-
"""
QR Kod Oluşturucu
Her müze eseri için QR kod oluşturma scripti
"""

import os
import qrcode
from qrcode.image.styledpil import StyledPilImage
from PIL import Image, ImageDraw, ImageFont

# Yapılandırma
BASE_URL = "http://localhost:5000"
OUTPUT_DIR = "qr_codes"
DATA_DIR = "data"


def load_exhibits():
    """data/ klasöründeki eser dosyalarını okur."""
    exhibits = {}
    for file in sorted(os.listdir(DATA_DIR)):
        if file.endswith(".txt"):
            eser_id = file.replace(".txt", "")
            filepath = os.path.join(DATA_DIR, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                info = {"id": eser_id}
                for line in content.split("\n"):
                    line = line.strip()
                    if ":" in line:
                        key, val = line.split(":", 1)
                        key = key.strip().lower().replace(" ", "_")
                        info[key] = val.strip()
                exhibits[eser_id] = info
            except Exception as e:
                print(f"⚠️  {file} okunamadı: {e}")
    return exhibits


def generate_qr_code(eser_id, eser_name, url):
    """Tek bir eser için QR kod oluşturur."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # QR kodu oluştur
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # QR görselini oluştur
    qr_img = qr.make_image(fill_color="#1a1a2e", back_color="#ffffff").convert("RGB")

    # QR kodun altına eser adını yaz
    qr_width, qr_height = qr_img.size
    label_height = 60
    final_img = Image.new("RGB", (qr_width, qr_height + label_height), "#1a1a2e")
    final_img.paste(qr_img, (0, 0))

    # Metin ekle
    draw = ImageDraw.Draw(final_img)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except IOError:
        font = ImageFont.load_default()

    # Metin ortala
    text = f"🏛️ {eser_name}"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (qr_width - text_width) // 2
    y = qr_height + 15

    draw.text((x, y), text, fill="#d4af37", font=font)

    # Kaydet
    filepath = os.path.join(OUTPUT_DIR, f"{eser_id}.png")
    final_img.save(filepath)
    print(f"  ✅ {filepath} → {url}")
    return filepath


def generate_all_qr_codes():
    """Tüm eserler için QR kodları oluşturur."""
    exhibits = load_exhibits()

    if not exhibits:
        print("❌ Hiç eser bulunamadı.")
        return

    print(f"\n🏛️  MÜZEREHBERI — QR Kod Oluşturucu")
    print(f"{'='*50}")
    print(f"📋 {len(exhibits)} eser için QR kodlar oluşturuluyor...\n")

    for eser_id, info in exhibits.items():
        eser_name = info.get("eser_adı", eser_id)
        url = f"{BASE_URL}/eser/{eser_id}"
        generate_qr_code(eser_id, eser_name, url)

    print(f"\n{'='*50}")
    print(f"✅ Tüm QR kodlar '{OUTPUT_DIR}/' klasörüne kaydedildi.")
    print(f"💡 QR kodları telefonunuzla tarayarak eserlere ulaşabilirsiniz.")


if __name__ == "__main__":
    generate_all_qr_codes()
