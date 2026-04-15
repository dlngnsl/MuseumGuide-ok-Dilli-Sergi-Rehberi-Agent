# MÜZEREHBERI - İnteligent Museum Guide

Müze rehberliği hizmetini yapay zeka kullanarak dijitalleştiren proje.

## Özellikler

- 🎨 Müze eserleri hakkında RAG tabanlı bilgi sorgulama
- 🎙️ Sesli rehberlik (TTS) ve ses girişi (STT)
- 📱 QR kod oluşturma ve takip
- 🤖 LM Studio entegrasyonu ile yerel LLM desteği
- 🔍 ChromaDB kullanarak vektör tabanlı arama

## Proje Yapısı

```
MÜZEREHBERI/
├── app.py                  # Ana uygulama arayüzü
├── rag_pipeline.py         # RAG işlemleri
├── llm_client.py          # LLM bağlantısı
├── qr_generator.py        # QR kod oluşturma
├── data/                  # Eser metinleri
├── vector_db/             # ChromaDB veritabanı
├── audio/                 # Ses dosyaları
├── qr_codes/              # QR kod görselleri
├── templates/             # HTML şablonları
└── static/                # CSS, JS, görseller
```

## Kurulum

1. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Uygulamayı çalıştırın:
```bash
python app.py
```

## Kullanım

Detaylı kullanım talimatları burada olacak.

## Lisans

MIT
