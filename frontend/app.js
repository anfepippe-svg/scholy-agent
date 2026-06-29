// Lógica del frontend de SCHOLY: envía el formulario al backend y pinta los
// resultados. Sin frameworks: JS vanilla para mantener el MVP simple.

const form = document.getElementById("profile-form");

// Los dos checkboxes financieros son lógicamente opuestos: si tienes ingreso
// extra, no necesitas financiación completa, y viceversa. Los hacemos
// mutuamente excluyentes (marcar uno desmarca el otro).
const extraIncomeBox = form.querySelector('input[name="has_extra_income"]');
const fullFundingBox = form.querySelector('input[name="needs_full_funding"]');
extraIncomeBox.addEventListener("change", () => {
  if (extraIncomeBox.checked) fullFundingBox.checked = false;
});
fullFundingBox.addEventListener("change", () => {
  if (fullFundingBox.checked) extraIncomeBox.checked = false;
});
const loading = document.getElementById("loading");
const results = document.getElementById("results");
const submitBtn = document.getElementById("submit-btn");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  // Construye el payload a partir de los campos del formulario.
  const fd = new FormData(form);
  const payload = {
    academic_level: fd.get("academic_level"),
    field_of_study: fd.get("field_of_study"),
    target_country: fd.get("target_country") || null,
    nationality: fd.get("nationality") || null,
    certified_languages: fd.get("certified_languages") || null,
    has_extra_income: fd.get("has_extra_income") === "on",
    needs_full_funding: fd.get("needs_full_funding") === "on",
    gpa: fd.get("gpa") ? parseFloat(fd.get("gpa")) : null,
    study_mode: fd.get("study_mode") || null,
    notes: fd.get("notes") || null,
  };

  // UI: estado de carga.
  results.classList.add("hidden");
  results.innerHTML = "";
  loading.classList.remove("hidden");
  submitBtn.disabled = true;
  submitBtn.classList.add("opacity-60");

  try {
    const resp = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (resp.status === 429) {
      // Límite de cuota gratuita: mensaje amable y diferenciado.
      const data = await resp.json().catch(() => ({}));
      results.innerHTML = `<div class="bg-amber-50 border border-amber-200 text-amber-800 rounded-xl p-4">
        ⏳ ${escapeHtml(data.detail || "Se alcanzó el límite gratuito por hoy. Inténtalo más tarde.")}</div>`;
      results.classList.remove("hidden");
      return;
    }
    if (!resp.ok) throw new Error("El servidor respondió con un error.");
    const data = await resp.json();
    renderResults(data);
  } catch (err) {
    results.innerHTML = `<div class="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4">
      No se pudieron obtener resultados. ${escapeHtml(err.message)}</div>`;
    results.classList.remove("hidden");
  } finally {
    loading.classList.add("hidden");
    submitBtn.disabled = false;
    submitBtn.classList.remove("opacity-60");
  }
});

// Escapa texto para evitar inyección de HTML al pintar datos del agente (XSS).
function escapeHtml(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

// Badge de compatibilidad. Solo se muestra si hay un puntaje numérico > 0;
// así evitamos el confuso "0/100" cuando el puntaje no se calculó.
function scoreBadge(score) {
  if (typeof score !== "number" || score <= 0) return "";
  const color = score >= 70 ? "bg-emerald-100 text-emerald-700"
    : score >= 40 ? "bg-amber-100 text-amber-700"
    : "bg-rose-100 text-rose-700";
  return `<span class="px-2.5 py-1 rounded-full text-xs font-bold ${color} whitespace-nowrap">${score}/100 match</span>`;
}

// Valida que una URL sea http(s) y "limpia". Si no, no la mostramos como enlace.
function safeUrl(url) {
  if (!url) return null;
  const trimmed = String(url).trim();
  // Rechaza URLs con espacios o caracteres raros (típico de enlaces inventados).
  if (/\s/.test(trimmed)) return null;
  try {
    const u = new URL(trimmed);
    return (u.protocol === "http:" || u.protocol === "https:") ? trimmed : null;
  } catch {
    return null;
  }
}

function renderResults(data) {
  const scholarships = data.scholarships || [];

  let cards = scholarships.map((s) => {
    const url = safeUrl(s.url);
    return `
    <div class="bg-white rounded-2xl border border-seagreen/10 p-5 sm:p-6 shadow-lg shadow-teal-deep/5 hover:shadow-xl hover:border-seagreen/30 transition">
      <div class="flex items-start justify-between gap-3">
        <h3 class="font-bold text-teal-deep text-lg leading-snug">${escapeHtml(s.name)}</h3>
        ${scoreBadge(s.match_score)}
      </div>
      <p class="text-sm text-slate-500 mt-1">
        ${escapeHtml(s.institution || "")}${s.country ? " · " + escapeHtml(s.country) : ""}
      </p>
      <dl class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-x-5 gap-y-1.5 text-sm">
        ${s.coverage ? `<div><dt class="text-slate-400 inline font-medium">Cobertura:</dt> ${escapeHtml(s.coverage)}</div>` : ""}
        ${s.language_requirement ? `<div><dt class="text-slate-400 inline font-medium">Idioma:</dt> ${escapeHtml(s.language_requirement)}</div>` : ""}
        ${s.deadline ? `<div><dt class="text-slate-400 inline font-medium">Deadline:</dt> ${escapeHtml(s.deadline)}</div>` : ""}
        ${s.eligibility_notes ? `<div><dt class="text-slate-400 inline font-medium">Elegibilidad:</dt> ${escapeHtml(s.eligibility_notes)}</div>` : ""}
      </dl>
      ${s.financial_fit ? `<p class="mt-4 text-sm bg-seagreen/10 text-teal-deep rounded-xl p-3.5 leading-relaxed">💰 ${escapeHtml(s.financial_fit)}</p>` : ""}
      ${url
        ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer"
            class="inline-flex items-center gap-1 mt-4 text-seagreen font-semibold text-sm hover:text-teal-deep transition">Ver beca oficial →</a>`
        : `<span class="inline-block mt-4 text-xs text-slate-400 italic">Sin enlace oficial verificado — busca el nombre en Google.</span>`}
    </div>`;
  }).join("");

  if (scholarships.length === 0) {
    cards = `<div class="text-slate-500 text-center py-8 bg-white rounded-2xl border border-seagreen/10">No se encontraron becas elegibles con este perfil.</div>`;
  }

  results.innerHTML = `
    <div class="bg-teal-deep text-white rounded-2xl p-5 sm:p-6 mb-5 shadow-lg shadow-teal-deep/20">
      <h2 class="font-bold mb-1.5 flex items-center gap-2">Resumen</h2>
      <p class="text-sm text-white/90 leading-relaxed">${escapeHtml(data.summary)}</p>
    </div>
    <div class="grid grid-cols-1 gap-4">${cards}</div>
  `;
  results.classList.remove("hidden");
}
