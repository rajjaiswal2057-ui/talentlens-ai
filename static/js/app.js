const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

function toast(msg, type) {
  const d = document.createElement("div");
  d.className = "toast" + (type === "err" ? " err" : "");
  d.textContent = msg;
  $("#toasts").append(d);
  setTimeout(() => d.remove(), 3500);
}

async function api(url, opts) {
  const r = await fetch(url, opts);
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.error || "Request failed");
  return d;
}

const jsonOpts = (method, body) => ({method, headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)});
const icons = () => window.lucide && lucide.createIcons();

document.addEventListener("DOMContentLoaded", () => {
  $("#themeBtn").onclick = () => {
    const t = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = t;
    localStorage.setItem("tl-theme", t);
  };
  document.querySelectorAll(".nav nav a").forEach(a => {
    if (location.pathname.startsWith(a.getAttribute("href"))) a.classList.add("active");
  });
  icons();
});