/* Playground website prototype: shared behaviour.
   No dependencies. Everything degrades gracefully without JS. */
(function () {
  var doc = document;
  var lang = (doc.documentElement.lang || "pt").slice(0, 2);
  var T = {
    pt: { showNotes: "Mostrar notas da proposta", hideNotes: "Esconder notas da proposta", sent: "Pedido enviado (simulação). No site real, o pedido entra no CRM e a equipa responde dentro do prazo indicado.", required: "Preencha os campos obrigatórios assinalados." },
    en: { showNotes: "Show proposal notes", hideNotes: "Hide proposal notes", sent: "Request sent (prototype). On the live site this goes straight to the CRM and the team replies within the stated time.", required: "Please complete the required fields." }
  }[lang] || {};

  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  /* dataLayer: what Google Tag Manager would receive on the live site */
  window.dataLayer = window.dataLayer || [];
  var toastTimer;
  function track(event, params) {
    var payload = Object.assign({ event: event, page_language: lang }, params || {});
    window.dataLayer.push(payload);
    if (doc.body.classList.contains("hide-notes")) return;
    var t = doc.querySelector(".track-toast");
    if (!t) { t = doc.createElement("div"); t.className = "track-toast"; t.setAttribute("role", "status"); doc.body.appendChild(t); }
    t.textContent = "GTM: " + event + (params ? " " + JSON.stringify(params) : "");
    t.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.hidden = true; }, 3200);
  }
  window.pgTrack = track;

  /* Mobile navigation */
  var toggle = doc.querySelector(".nav-toggle");
  var nav = doc.querySelector(".nav-primary");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* Proposal notes toggle (on by default) */
  var btn = doc.createElement("button");
  btn.type = "button"; btn.className = "notes-toggle";
  function syncNotes() {
    var hidden = doc.body.classList.contains("hide-notes");
    btn.textContent = hidden ? T.showNotes : T.hideNotes;
    btn.setAttribute("aria-pressed", hidden ? "false" : "true");
  }
  if (store("pg-notes") === "off") doc.body.classList.add("hide-notes");
  btn.addEventListener("click", function () {
    doc.body.classList.toggle("hide-notes");
    store("pg-notes", doc.body.classList.contains("hide-notes") ? "off" : "on");
    syncNotes();
  });
  syncNotes();
  doc.body.appendChild(btn);

  /* Click tracking: any element with data-track="event_name" */
  doc.addEventListener("click", function (e) {
    var el = e.target.closest("[data-track]");
    if (!el) return;
    track(el.getAttribute("data-track"), { label: el.getAttribute("data-track-label") || (el.textContent || "").trim().slice(0, 40) });
  });

  /* Case study filters: .chip[data-filter] inside [data-filter-group], items [data-tags] */
  doc.querySelectorAll("[data-filter-scope]").forEach(function (scope) {
    var items = scope.querySelectorAll("[data-tags]");
    var empty = scope.querySelector("[data-filter-empty]");
    function apply() {
      var active = {};
      scope.querySelectorAll("[data-filter-group]").forEach(function (g) {
        var on = g.querySelector('.chip[aria-pressed="true"]');
        active[g.getAttribute("data-filter-group")] = on ? on.getAttribute("data-filter") : "all";
      });
      var shown = 0;
      items.forEach(function (it) {
        var tags = (it.getAttribute("data-tags") || "").split(/\s+/);
        var ok = Object.keys(active).every(function (k) { return active[k] === "all" || tags.indexOf(active[k]) > -1; });
        it.hidden = !ok; if (ok) shown++;
      });
      if (empty) empty.hidden = shown > 0;
    }
    scope.querySelectorAll("[data-filter-group] .chip").forEach(function (chip) {
      chip.addEventListener("click", function () {
        chip.closest("[data-filter-group]").querySelectorAll(".chip").forEach(function (c) { c.setAttribute("aria-pressed", "false"); });
        chip.setAttribute("aria-pressed", "true");
        apply();
        track("filter_cases", { filter: chip.getAttribute("data-filter") });
      });
    });
    apply();
  });

  /* Forms: validate, simulate submission, push the conversion event */
  doc.querySelectorAll("form[data-form]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = true;
      form.querySelectorAll("[required]").forEach(function (f) {
        var bad = f.type === "checkbox" ? !f.checked : !String(f.value || "").trim();
        f.setAttribute("aria-invalid", bad ? "true" : "false");
        if (bad && ok) { f.focus(); ok = false; }
      });
      var err = form.querySelector(".form-error");
      if (!ok) { if (err) { err.textContent = T.required; err.hidden = false; } return; }
      if (err) err.hidden = true;
      var data = {};
      ["type", "country", "attendees", "budget", "city", "sector"].forEach(function (k) { var f = form.elements[k]; if (f && f.value) data[k] = f.value; });
      data.form = form.getAttribute("data-form");
      track("generate_lead", data);
      var done = form.parentNode.querySelector(".form-success");
      if (done) { form.hidden = true; done.hidden = false; done.focus && done.focus(); }
      else { form.insertAdjacentHTML("beforeend", '<p class="form-success" role="status">' + T.sent + "</p>"); }
    });
  });

  /* Cookie consent (Consent Mode v2 on the live site) */
  var cookie = doc.querySelector(".cookie");
  if (cookie) {
    if (!store("pg-consent")) cookie.hidden = false;
    cookie.querySelectorAll("[data-consent]").forEach(function (b) {
      b.addEventListener("click", function () {
        var v = b.getAttribute("data-consent");
        store("pg-consent", v);
        cookie.hidden = true;
        track("consent_update", { analytics: v === "accept" ? "granted" : "denied" });
      });
    });
  }
})();
