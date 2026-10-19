"use strict";
(() => {
  const data = window.CYBERSHIELD_DEMO;
  const byId = id => document.getElementById(id);
  let selected = "baseline";
  const escape = value => String(value).replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
  const badge = f => `<span class="badge ${f.status === "WARN" ? f.severity.toLowerCase() : f.status.toLowerCase()}">${f.status === "WARN" ? `${f.severity.toLowerCase()} · review` : f.status === "PASS" ? "Passed" : "Informational"}</span>`;
  function renderHeaders() {
    const filter = byId("filter").value;
    const findings = data[selected].findings.filter(f => !f.key.startsWith("cookie") && f.key !== "cors" && (filter === "ALL" || f.status === filter));
    byId("header-rows").innerHTML = findings.map(f => `<tr><td>${escape(f.title)}</td><td>${escape(f.detail)}</td><td>${badge(f)}</td></tr>`).join("");
    byId("empty").hidden = findings.length > 0;
  }
  function render() {
    const result = data[selected];
    byId("score").textContent = result.score;
    byId("score-ring").style.setProperty("--score", result.score);
    byId("score-ring").style.setProperty("--ring", result.score >= 90 ? "var(--green)" : "var(--amber)");
    byId("grade").textContent = `Grade ${result.grade} · ${result.score >= 90 ? "Sample safeguards present" : "Configuration needs review"}`;
    byId("grade").className = `badge ${result.score >= 90 ? "pass" : "medium"}`;
    for (const [id, key] of [["checks", "total_checks"], ["passed", "passed"], ["warnings", "warnings"]]) byId(id).textContent = result.summary[key];
    byId("severity-bars").innerHTML = [["HIGH","High","var(--red)"],["MEDIUM","Medium","var(--amber)"],["LOW","Low","var(--cyan)"]].map(([severity,label,color]) => {
      const count = result.findings.filter(f => f.status === "WARN" && f.severity === severity).length;
      const percent = result.summary.warnings ? count / result.summary.warnings * 100 : 0;
      return `<div style="--bar:${color}"><div class="bar-label"><span><i class="bar-dot" aria-hidden="true"></i>${label}</span><strong>${count}</strong></div><div class="track" aria-hidden="true"><div style="width:${percent}%"></div></div></div>`;
    }).join("");
    renderHeaders();
    const cors = result.findings.find(f => f.key === "cors");
    const cookie = result.findings.find(f => f.key.startsWith("cookie-"));
    for (const [id, f] of [["cors-content", cors], ["cookie-content", cookie]]) {
      byId(id).innerHTML = `${badge(f)}<p>${escape(f.detail)}</p><div class="evidence">${escape(f.evidence || "No arbitrary-origin sharing observed in this simulated response.")}</div><p class="detail-note">${id === "cors-content" ? "One synthetic Origin is tested. This does not confirm sensitive data exposure." : "Only cookie names and attribute observations are reported; cookie values are omitted."}</p>`;
    }
    const rank = {HIGH:0, MEDIUM:1, LOW:2};
    const warnings = result.findings.filter(f => f.status === "WARN").sort((a,b) => rank[a.severity] - rank[b.severity]);
    byId("recommendation-list").innerHTML = warnings.length ? warnings.map((f,i) => `<article class="recommendation"><span class="number">${String(i+1).padStart(2,"0")}</span><div><h3>${escape(f.title)}</h3><p>${escape(f.recommendation)}</p></div>${badge(f)}</article>`).join("") : '<p class="muted">No warnings in this improved fixture. Continue reviewing application behavior, policy values and authenticated routes; a score of 100 does not guarantee security.</p>';
    byId("status").textContent = `Simulated ${selected} configuration loaded. Score ${result.score} of 100; ${result.summary.warnings} warnings.`;
  }
  byId("scenario").addEventListener("change", event => {selected = event.target.value; render();});
  byId("filter").addEventListener("change", renderHeaders);
  byId("export").disabled = false;
  byId("export").addEventListener("click", () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify(data[selected], null, 2)], {type:"application/json"}));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `cybershield-${selected}-simulated.json`;
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  function updateNavigation() {
    const hash = location.hash || "#overview";
    document.querySelectorAll("nav a").forEach(link => {
      if (link.hash === hash) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  }
  window.addEventListener("hashchange", updateNavigation);
  updateNavigation();
  render();
})();
