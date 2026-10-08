// RetroBot 95 / NovaBot 2030 - frontend logic

const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const statusLine = document.getElementById("status-line");
const counterEl = document.getElementById("counter");
const modernizeBtn = document.getElementById("modernize-btn");
const modeToggleLabel = document.querySelector(".mode-toggle-label");
const sendBtn = document.getElementById("send-btn");
const chatAvatar = document.getElementById("chat-avatar");

// The id of the previous Gemini interaction (for conversation continuity)
let previousInteractionId = null;

// "retro" (1990s) or "future" (2030s)
let mode = "retro";

const BOT_NAME = {
  retro: "RetroBot",
  future: "NovaBot",
};

// Texts that change depending on the mode
const THEME_TEXT = {
  retro: {
    docTitle: "~*~ RetroBot 95 ~*~ Kisisel Bilgisayar Asistaniniz ~*~",
    pageTitle: "☆ RetroBot 95 ☆",
    pageSubtitle: "\"1990'lardan sizlere internet üzerinden merhaba diyoruz!\"",
    chatHeader: "RetroBot ile Sohbet Et 💾",
    sidebarTitle: "Site Haritasi",
    counterLabel: "Ziyaretci Sayaci:",
    inputPlaceholder: "Mesajini yaz ve ENTER'a bas...",
    sendBtnLabel: "Gonder >>",
    avatar: "💾",
    statusReady: "Baglanti hazir. (28.8k modem simulasyonu)",
    statusConnecting: "Baglaniliyor... modem sesi cikariyor (lutfen bekleyin) ...",
    footerCopyright: "© 1996 RetroBot Industries — Tum haklari saklidir.",
    footerNote: "Bu sayfa en iyi 800x600 cozunurlukte goruntulenir.",
    footerBookmark: "Bizi yer imlerine (bookmark) eklemeyi unutmayin!",
    modeLabel: "Zaman makinesi hazir mi?",
    modeBtn: "🚀 2030'a Gec",
    badge: "🚧 SITE HALA YAPIM ASAMASINDA 🚧",
    welcome:
      "Merhaba! Ben RetroBot, senin dijital arkadasin :) Modemin baglanmasini bekliyordum, simdi konusabiliriz! Bana ne sormak istersin?",
  },
  future: {
    docTitle: "NovaBot // 2030 Noro-Asistan Arayuzu",
    pageTitle: "⚡ NovaBot 2030 ⚡",
    pageSubtitle: "2030'un yapay zeka asistanina hos geldin.",
    chatHeader: "🧠 NovaBot ile Baglanti Kuruldu",
    sidebarTitle: "Hizli Erisim",
    counterLabel: "Aktif Noro-Baglanti:",
    inputPlaceholder: "Mesajini yaz veya sesli komut ver...",
    sendBtnLabel: "➤",
    avatar: "🛰️",
    statusReady: "Baglanti kuruldu. (kuantum agi - gecikme yok)",
    statusConnecting: "Isleniyor... noro-agi senkronize ediliyor ...",
    footerCopyright: "© 2030 NovaBot Sistemleri — Tum haklari saklidir.",
    footerNote: "Bu arayuz her cozunurluk ve her noro-arayuz icin optimize edildi.",
    footerBookmark: "Bu asistani favori ajanin olarak isaretle!",
    modeLabel: "Eski gunlere ozlem mi geldi?",
    modeBtn: "📼 1990'a Don",
    badge: "⚡ NORO-BAGLANTI AKTIF · KUANTUM CEKIRDEK CEVRIMICI ⚡",
    welcome:
      "Merhaba, ben NovaBot 🛰️ Beyin-arayuz senkronizasyonu tamamlandi, holografik ekranim aktif, kuantum cekirdegim hazir. Ay kolonisindeki kahvemi bile bu sirada icebiliyorum :) Bugun sana nasil yardimci olayim?",
  },
};

function appendMessage(text, cssClass, label) {
  const div = document.createElement("div");
  div.className = `msg ${cssClass}`;
  div.innerHTML = `<b>${escapeHtml(label)}:</b> ${escapeHtml(text)}`;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function escapeHtml(str) {
  const d = document.createElement("div");
  d.innerText = str;
  return d.innerHTML;
}

async function sendMessage(message) {
  const t = THEME_TEXT[mode];
  statusLine.textContent = t.statusConnecting;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        previous_interaction_id: previousInteractionId,
        mode,
      }),
    });

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.detail || `Sunucu hatasi (${res.status})`);
    }

    const data = await res.json();
    appendMessage(data.reply, "bot-msg", BOT_NAME[mode]);

    if (data.interaction_id) {
      previousInteractionId = data.interaction_id;
    }

    statusLine.textContent = t.statusReady;
  } catch (err) {
    appendMessage(
      `Baglanti koptu! (${err.message}) Belki de telefon hattini biri mesguldu?`,
      "error-msg",
      "SISTEM"
    );
    statusLine.textContent = "HATA: Baglanti basarisiz.";
  }
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;

  appendMessage(message, "user-msg", "Sen");
  chatInput.value = "";
  sendMessage(message);
});

// Retro "visitor counter" - a fake but fun counter using localStorage
(function initCounter() {
  const key = "retrobot_visit_count";
  let count = parseInt(localStorage.getItem(key) || "133742", 10);
  count += 1;
  localStorage.setItem(key, String(count));
  counterEl.textContent = String(count).padStart(6, "0");
})();

function applyTheme(newMode) {
  mode = newMode;
  const t = THEME_TEXT[mode];

  document.body.classList.toggle("theme-future", mode === "future");
  document.title = t.docTitle;

  document.getElementById("page-title").textContent = t.pageTitle;
  document.getElementById("page-subtitle").textContent = t.pageSubtitle;
  document.getElementById("under-construction").textContent = t.badge;
  document.getElementById("chat-header-text").textContent = t.chatHeader;
  document.getElementById("sidebar-title").textContent = t.sidebarTitle;
  document.getElementById("counter-label").textContent = t.counterLabel;
  document.getElementById("footer-copyright").textContent = t.footerCopyright;
  document.getElementById("footer-note").textContent = t.footerNote;
  document.getElementById("footer-bookmark").textContent = t.footerBookmark;
  chatInput.placeholder = t.inputPlaceholder;
  statusLine.textContent = t.statusReady;
  modeToggleLabel.textContent = t.modeLabel;
  modernizeBtn.textContent = t.modeBtn;
  sendBtn.textContent = t.sendBtnLabel;
  chatAvatar.textContent = t.avatar;

  // Reset the chat when the mode changes (new persona, new interaction)
  previousInteractionId = null;
  chatLog.innerHTML = "";
  appendMessage(t.welcome, "bot-msg", BOT_NAME[mode]);
}

modernizeBtn.addEventListener("click", () => {
  applyTheme(mode === "retro" ? "future" : "retro");
});

// Sync all texts with THEME_TEXT on startup (single source of truth).
applyTheme("retro");
