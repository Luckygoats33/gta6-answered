/* Ask Unc chat widget. Talks to the Cloudflare Worker named in data-api. No dependencies. */
(function () {
  var script = document.currentScript;
  var API = script && script.getAttribute("data-api");
  if (!API) return;

  var UNC = '<svg viewBox="0 0 256 256" aria-hidden="true" focusable="false"><g fill="currentColor">' +
    '<path d="M60 104 C60 56 90 30 128 30 C166 30 196 56 196 104 Z"/>' +
    '<path d="M40 98 L216 98 Q234 100 236 128 Q216 118 200 118 L56 118 Q40 118 20 128 Q22 100 40 98 Z"/>' +
    '<path d="M36 126 L124 134 Q128 135 127 141 L121 172 Q119 182 108 182 L66 182 Q56 182 52 174 L33 134 Q31 126 36 126 Z M220 126 L132 134 Q128 135 129 141 L135 172 Q137 182 148 182 L190 182 Q200 182 204 174 L223 134 Q225 126 220 126 Z M120 133 L136 133 L136 146 L120 146 Z"/>' +
    '<path d="M62 222 Q90 194 128 206 Q166 194 194 222 Q162 216 128 224 Q94 216 62 222 Z"/>' +
    '<path fill-rule="nonzero" d="M48 192 Q62 206 84 206 L172 206 Q194 206 208 192 C206 236 170 254 128 254 C86 254 50 236 48 192 Z M100 226 L100 236 L156 236 L156 226 Z M149.9 217.1 L146.1 244.9 L245.1 258.8 L248.9 231 Z"/>' +
    '<g transform="rotate(8 148 231)"><rect x="148" y="222" width="62" height="18" rx="6"/><rect x="214" y="222" width="12" height="18" rx="3"/></g></g>' +
    '<path d="M228 226 C238 214 222 204 233 191 C241 181 233 173 239 165" fill="none" stroke="currentColor" stroke-width="7" stroke-linecap="round"/></svg>';

  var CHIPS = ["What time does GTA 6 unlock for me?", "How much space do I need?", "Is GTA 6 on PC?"];
  var KEY = "askunc-v1";
  var history = [];
  try { history = JSON.parse(sessionStorage.getItem(KEY) || "[]") || []; } catch (err) { history = []; }
  function save() { try { sessionStorage.setItem(KEY, JSON.stringify(history.slice(-10))); } catch (err) { /* private mode */ } }

  function el(tag, cls, html) { var n = document.createElement(tag); if (cls) n.className = cls; if (html != null) n.innerHTML = html; return n; }
  function esc(t) { return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }
  // Safe, tiny markdown: escape everything, then allow https links, **bold**, list dashes and line breaks.
  function render(t) {
    var h = esc(t);
    h = h.replace(/\[([^\]]{1,120})\]\((https:\/\/[^\s)]{1,300})\)/g, function (_, label, url) {
      var internal = url.indexOf("https://callunc.com/") === 0;
      return '<a href="' + url + '"' + (internal ? "" : ' target="_blank" rel="noopener noreferrer"') + ">" + label + "</a>";
    });
    h = h.replace(/\*\*([^*]{1,200})\*\*/g, "<strong>$1</strong>");
    return h.split(/\n{2,}/).map(function (p) { return "<p>" + p.replace(/\n/g, "<br>") + "</p>"; }).join("");
  }

  var fab = el("button", "ask-fab", '<span class="ask-face">' + UNC + "</span><span>Ask Unc</span>");
  fab.type = "button";
  fab.setAttribute("aria-expanded", "false");
  fab.setAttribute("aria-controls", "ask-panel");

  var panel = el("section", "ask-panel");
  panel.id = "ask-panel";
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-label", "Ask Unc about GTA 6");
  panel.hidden = true;
  panel.innerHTML =
    '<header class="ask-head"><span class="ask-face">' + UNC + '</span><div><p class="ask-title">Ask Unc</p>' +
    '<p class="ask-sub">AI answers about GTA 6. Can be wrong, so check Rockstar before you buy.</p></div>' +
    '<button type="button" class="ask-close" aria-label="Close chat">Close</button></header>' +
    '<div class="ask-log" role="log" aria-live="polite"></div>' +
    '<div class="ask-chips"></div>' +
    '<form class="ask-form"><label class="visually-hidden" for="ask-input">Your GTA 6 question</label>' +
    '<textarea id="ask-input" rows="1" maxlength="600" placeholder="Ask a GTA 6 question" required></textarea>' +
    '<button type="submit" class="ask-send">Ask</button></form>';
  document.body.appendChild(fab);
  document.body.appendChild(panel);

  var log = panel.querySelector(".ask-log");
  var chips = panel.querySelector(".ask-chips");
  var form = panel.querySelector(".ask-form");
  var input = panel.querySelector("#ask-input");
  var sendBtn = panel.querySelector(".ask-send");
  var busy = false;

  function bubble(role, text) {
    var b = el("div", "ask-msg ask-msg--" + role);
    if (role === "assistant") b.appendChild(el("span", "ask-face ask-face--sm", UNC));
    var body = el("div", "ask-body");
    body.innerHTML = role === "user" ? "<p>" + esc(text) + "</p>" : render(text);
    b.appendChild(body);
    log.appendChild(b);
    log.scrollTop = log.scrollHeight;
    return body;
  }

  function drawChips() {
    chips.innerHTML = "";
    if (history.length) return;
    CHIPS.forEach(function (q) {
      var c = el("button", "ask-chip"); c.type = "button"; c.textContent = q;
      c.addEventListener("click", function () { ask(q); });
      chips.appendChild(c);
    });
  }

  function open() {
    panel.hidden = false; fab.setAttribute("aria-expanded", "true"); fab.hidden = true;
    if (!log.childElementCount) {
      if (history.length) history.forEach(function (m) { bubble(m.role, m.content); });
      else bubble("assistant", "Unc here. Ask me anything about GTA 6: unlock times, storage, editions, rumors.");
    }
    drawChips();
    input.focus();
  }
  function close() { panel.hidden = true; fab.hidden = false; fab.setAttribute("aria-expanded", "false"); fab.focus(); }

  fab.addEventListener("click", open);
  panel.querySelector(".ask-close").addEventListener("click", close);
  panel.addEventListener("keydown", function (ev) { if (ev.key === "Escape") close(); });
  input.addEventListener("keydown", function (ev) { if (ev.key === "Enter" && !ev.shiftKey) { ev.preventDefault(); form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event("submit")); } });
  form.addEventListener("submit", function (ev) { ev.preventDefault(); var q = input.value.trim(); if (q) ask(q); });

  function setBusy(on) { busy = on; sendBtn.disabled = on; input.disabled = on; panel.classList.toggle("is-busy", on); }

  function ask(q) {
    if (busy) return;
    input.value = "";
    chips.innerHTML = "";
    bubble("user", q);
    history.push({ role: "user", content: q });
    save();
    var body = bubble("assistant", "");
    var status = el("p", "ask-status", "Unc is thinking");
    body.appendChild(status);
    var text = "", cites = [], errored = false;
    setBusy(true);

    fetch(API, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ messages: history.slice(-10) }) })
      .then(function (res) {
        if (!res.ok || !res.body) {
          return res.json().catch(function () { return {}; }).then(function (j) { throw new Error(j.error || "Unc lost the signal. Try again in a moment."); });
        }
        var reader = res.body.getReader(), dec = new TextDecoder(), buf = "";
        function pump() {
          return reader.read().then(function (r) {
            if (r.done) return;
            buf += dec.decode(r.value, { stream: true });
            var lines = buf.split("\n"); buf = lines.pop();
            lines.forEach(function (line) {
              if (!line) return;
              var m; try { m = JSON.parse(line); } catch (err) { return; }
              if (m.t === "text") { text += m.v; body.innerHTML = render(text); }
              else if (m.t === "status") { status.textContent = m.v; if (!status.isConnected) body.appendChild(status); }
              else if (m.t === "cite") { cites.push(m); }
              else if (m.t === "error") { errored = true; text += (text ? "\n\n" : "") + m.v; body.innerHTML = render(text); }
            });
            log.scrollTop = log.scrollHeight;
            return pump();
          });
        }
        return pump();
      })
      .catch(function (err) { errored = true; text = err.message; body.innerHTML = render(text); })
      .then(function () {
        if (cites.length) {
          var s = el("p", "ask-sources", "Sources: ");
          cites.slice(0, 4).forEach(function (c, i) {
            var a = el("a"); a.href = c.url; a.target = "_blank"; a.rel = "noopener noreferrer"; a.textContent = c.title;
            if (i) s.appendChild(document.createTextNode(", "));
            s.appendChild(a);
          });
          body.appendChild(s);
        }
        if (text && !errored) { history.push({ role: "assistant", content: text }); save(); }
        else if (errored) { history.pop(); save(); }
        else { history.pop(); save(); body.innerHTML = render("No answer came back. Try asking again."); }
        setBusy(false);
        input.focus();
      });
  }
})();
