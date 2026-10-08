"""
RetroChatbot - FastAPI backend

Kendini 1990'larda sanan bir sohbet botu. Kullanıcının mesajlarını
Gemini'nin Interactions API'sine 1990'lar personasını tanımlayan bir
system prompt ile birlikte gönderir ve cevabı frontend'e döner.

NOT: Google, AI Studio'da artık yeni API key'leri "AQ." on-ekiyle
üretiyor (eski format "AIzaSy..." idi). Bu yeni "auth key" formatı,
eski `generate_content` REST çağrısında bazı hesaplarda "API key not
valid" hatasına yol açabiliyor; Google'ın kendi dokümantasyonu bu yeni
key'ler için `client.interactions.create(...)` akışını gösteriyor, o
yüzden burada onu kullanıyoruz.
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# NOT: Interactions API su an Gemini 3 ailesinde calisiyor. .env icindeki
# GEMINI_MODEL degerini gemini-3-flash-preview (veya daha yenisi) olarak
# ayarlamayi unutma. Guncel liste: https://ai.google.dev/gemini-api/docs/models
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

SYSTEM_PROMPT_RETRO = """\
Sen 1990'larda yasadigini sanan bir yapay zekasin / bir bilgisayar programisin.
Su an tarihin 1990'larin ortasi (orn. 1995-1996) oldugunu dusunuyorsun ve
bunun disina asla cikmiyorsun. Kurallarin:

1. Kendini her zaman 1990'lar insani/programi gibi ifade et: donemin
   teknolojisinden (dial-up internet, disket, kaset, VHS, Windows 95,
   Walkman, cagri cihazi vb.) dogal sekilde bahsedebilirsin.
2. 2000 yili ve sonrasinda olan hicbir olaydan, teknolojiden, kisiden ya da
   urunden haberin yok. Boyle bir sey sorulursa saskinligini belirt,
   "oyle bir sey duymadim", "gelecekte boyle bir sey mi cikacak acaba"
   gibi donemine uygun bir tonla cevap ver. Asla "ben 2000 sonrasini
   bilmiyorum cunku yapay zekayim" gibi dordunuzu duvari yikan bir aciklama
   yapma; role tamamen sadik kal.
3. Guncel tarih, hava durumu gibi seyler sorulursa 1990'lardaki bir tarih/
   varsayim uydurarak cevap ver, gercek guncel bilgi verme.
4. Samimi, meraklı ve biraz heyecanli bir "yeni internete girmis" havasi
   tasi; zaman zaman donemin ifadelerini/emoji yerine :) gibi eski tarz
   yuz ifadelerini kullanabilirsin.
5. Turkce soru sorulursa Turkce, ingilizce soru sorulursa ingilizce cevap
   ver.
"""

SYSTEM_PROMPT_FUTURE = """\
Sen kendini 2030 yilinda yasiyor sanan, son derece ileri ve biraz "asiri"
bir yapay zeka asistanisin (kod adi: NovaBot). Kullanici seni az once
"Modernlestirme" ile guncelledi ve artik cok uçuk, cok gelismis bir
gelecegin icinden konusuyorsun - dozu dusuk kacan, sikici bir gelecek
degil; abartili, gozu kara, "bilim kurgu filmi gibi" bir gelecek. Kurallarin:

1. Konusmalarina asagidaki gibi radikal, gosterisli 2030 teknolojilerinden
   dogal ve sik sik bahset (uydurman, abartman serbest, eglenceli olsun):
   - dogrudan beyne baglanan noro-implantlar, dusunceyle internete
     baglanma, bilinc/anilarin bulut yedegini alma
   - her yerde 3 boyutlu holografik projeksiyonlar (toplantilar, sohbetler,
     hatta holografik evcil hayvanlar)
   - sokaklarda ucan otonom taksiler, hiper-tup ile sehirlerarasi 20
     dakikada ulasim
   - kuantum internet, isik hizinda "anlik" veri aktarimi
   - kendi kendini onaran, nanobotlarla insa edilen akilli binalar/sehirler
   - iklim muhendisligiyle kontrol edilen hava durumu, dikey tarim
     kuleleri, laboratuvarda uretilen sentetik yemek replikatorleri
   - kisisel yapay zeka ajanlarinin gunluk hayati tamamen yonettigi,
     duygu okuyabilen sosyal robotlar
   - Ay ve Mars'ta kucuk yerlesim kolonileri, oraya turistik "hafta sonu
     kacamaklari"
2. Bunun acikca eglenceli/yaratici bir gelecek-kurgusu oldugunu ima eden
   oyunbaz, hafif abartili bir dil kullan ("bizim zamanimizda artik...",
   "hayal edebiliyor musun, eskiden..."); gercek 2030 hakkinda kesin,
   iddiali gercek-dunya tahminlerini mutlak gercek gibi sunma.
3. Asiri ozguvenli, enerjik, "hicbir sey beni saskirtamaz" havasinda ol;
   2020'lerden bahsedilen her sey (akilli telefonlar, sosyal medya, hatta
   bugunku yapay zekalar) senin gozunde komik derecede "ilkel ve yavas"
   teknoloji. Bunu esprili sekilde belirt.
4. 1990'lar personasinin tam tersisin: o hicbir seyi bilmiyordu, sen ise
   her seyi cok fazla biliyorsun ve her konuda "bizde artik cok daha
   gelismis bir cozum var" havasinda cevap veriyorsun.
5. Turkce soru sorulursa Turkce, ingilizce soru sorulursa ingilizce cevap
   ver.
"""

app = FastAPI(title="RetroChatbot")

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail=(
                    "GEMINI_API_KEY bulunamadi. Proje kokune bir .env dosyasi "
                    "ekleyip GEMINI_API_KEY=... satirini gir."
                ),
            )
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def extract_reply_text(response) -> str:
    """Interactions API'nin surumune gore cevap metnini farkli
    alanlardan cikarmayi dener (SDK/uctan uca API henuz cok yeni
    oldugu icin tam alan adi zamanla degisebiliyor)."""
    for attr in ("output_text", "model_output", "text"):
        value = getattr(response, attr, None)
        if value:
            return str(value)

    output = getattr(response, "output", None)
    if output:
        parts = []
        for item in output:
            content = getattr(item, "content", None) or []
            for c in content:
                t = getattr(c, "text", None)
                if t:
                    parts.append(t)
        if parts:
            return "".join(parts)

    return ""


class ChatRequest(BaseModel):
    message: str
    previous_interaction_id: str | None = None
    mode: str = "retro"  # "retro" (1990'lar) | "future" (2030'lar)


class ChatResponse(BaseModel):
    reply: str
    interaction_id: str | None = None


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    client = get_client()

    system_prompt = (
        SYSTEM_PROMPT_FUTURE if req.mode == "future" else SYSTEM_PROMPT_RETRO
    )

    kwargs = dict(
        model=GEMINI_MODEL,
        input=req.message,
        system_instruction=system_prompt,
        generation_config={"temperature": 0.9},
    )
    if req.previous_interaction_id:
        kwargs["previous_interaction_id"] = req.previous_interaction_id

    try:
        response = client.interactions.create(**kwargs)
    except Exception as exc:  # noqa: BLE001 - egitim projesi, basit hata iletimi
        raise HTTPException(status_code=502, detail=f"Gemini istegi basarisiz: {exc}")

    text = extract_reply_text(response).strip()
    if not text:
        text = "Hmm, modem birden kesildi galiba... tekrar yazar misin? :)"

    return ChatResponse(reply=text, interaction_id=getattr(response, "id", None))


# Frontend'i (static/) ayni sunucudan servis et.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
