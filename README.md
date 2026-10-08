# RetroBot 95 — 1990'lardan Kalma Chatbot (artık 2030'a da ışınlanabiliyor)

Kendini 1990'larda sanan bir sohbet botu. Python + FastAPI backend, Google
Gemini'nin Interactions API'si ile konuşuyor; frontend düz HTML/CSS/JS ve
dönemin web sitelerini andırıyor. Üstteki "Modernleştir" butonuyla hem bot
hem arayüz 2030'un (VR/holografik tarzda tasarlanmış) bir versiyonuna
dönüşüyor.

## Özellikler

- **İki persona:** varsayılan "RetroBot" (1990'lar, 2000 sonrasından
  habersiz) ve "NovaBot" (2030, nöro-implant/holografik/uçan-taksi
  temalı, abartılı bir gelecek karakteri).
- **İki tema:** retro (marquee, "yapım aşamasında" rozeti, table layout)
  ve future (camsı/holografik paneller, ikon-rayı navigasyon, neon
  parlamalar).
- Gemini ile konuşma sürekliliği sunucu tarafında `previous_interaction_id`
  üzerinden sağlanıyor.

## Kurulum

1. Sanal ortamı aktive et (PyCharm zaten `.venv` oluşturmuş, terminalde de
   aktive edebilirsin):

   ```bash
   source .venv/bin/activate      # macOS / Linux
   ```

2. Bağımlılıkları kur:

   ```bash
   pip install -r requirements.txt
   ```

3. `.env.example` dosyasını `.env` olarak kopyala ve kendi Gemini API
   key'ini gir:

   ```bash
   cp .env.example .env
   ```

   `.env` içine:

   ```
   GEMINI_API_KEY=senin_api_keyin
   GEMINI_MODEL=gemini-3-flash-preview
   ```

   Not: Google AI Studio artık `AQ.` ön ekli yeni nesil "auth key"ler
   üretiyor. Bu proje Gemini'nin Interactions API'sini kullandığı için bu
   yeni key formatıyla uyumlu; `gemini-3-flash-preview` (veya daha
   yenisi) Interactions API'yi destekleyen bir model olmalı.

## Çalıştırma

```bash
python -m uvicorn main:app --reload
```

(`python -m uvicorn ...` kullanmak, venv aktifken global bir uvicorn
kurulumuyla karışmasını önlüyor.)

Sonra tarayıcıda aç: http://127.0.0.1:8000

## Yapı

```
RetroChatbotProject/
  main.py            # FastAPI backend + Gemini Interactions API entegrasyonu (/api/chat)
                      #   - SYSTEM_PROMPT_RETRO / SYSTEM_PROMPT_FUTURE iki persona
                      #   - ChatRequest.mode: "retro" | "future"
  requirements.txt
  .env.example        # placeholder - gercek key asla buraya girilmemeli
  .gitignore           # .venv, __pycache__, .env
  static/
    index.html       # Retro arayüz + "Modernleştir" butonu, ikon+metin nav yapısı
    style.css         # Retro tema + body.theme-future altında 2030 tema override'ları
    script.js         # fetch ile /api/chat çağrısı, previous_interaction_id ile süreklilik,
                       #   THEME_TEXT sözlüğü ile mod değişince tüm metinleri/temayı günceller
  README.md
```

## Notlar

- `main.py` içindeki `SYSTEM_PROMPT_RETRO` / `SYSTEM_PROMPT_FUTURE`,
  botun iki personasını tanımlıyor; ton/karakter ince ayarları buradan
  yapılır.
- `GEMINI_MODEL` değeri `.env` içinden değiştirilebilir; Google'ın güncel
  model listesi için https://ai.google.dev/gemini-api/docs/models
  adresine bak.
- `.env` dosyası `.gitignore` ile korunuyor; gerçek API key'in asla
  repoya girmediğinden emin ol (`.env.example` sadece placeholder
  içermeli).
