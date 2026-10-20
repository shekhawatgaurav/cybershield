"use strict";
(() => {
  const data = window.CYBERSHIELD_DEMO;
  const byId = id => document.getElementById(id);
  let selected = "baseline";
  const siteNames = {original: "Original sample", store: "Northstar Store", portal: "Orbit Docs"};
  const currentName = () => siteNames[byId("sample-site").value];
  const escape = value => String(value).replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
  const badge = f => `<span class="badge ${f.status === "WARN" ? f.severity.toLowerCase() : f.status.toLowerCase()}">${f.status === "WARN" ? `${f.severity.toLowerCase()} · review` : f.status === "PASS" ? "Passed" : "Informational"}</span>`;
  function renderHeaders() {
    const filter = byId("filter").value;
    const query = byId("search").value.trim().toLowerCase();
    const findings = data[selected].findings.filter(f => !f.key.startsWith("cookie") && f.key !== "cors" && (filter === "ALL" || f.status === filter) && `${f.title} ${f.detail}`.toLowerCase().includes(query));
    byId("header-rows").innerHTML = findings.map(f => `<tr><td>${escape(f.title)}</td><td>${escape(f.detail)}</td><td>${badge(f)}</td></tr>`).join("");
    byId("empty").hidden = findings.length > 0;
  }
  function render() {
    const result = data[selected];
    byId("sample-target").textContent = new URL(result.final_url).hostname;
    byId("sample-response").textContent = `Sample path: ${new URL(result.final_url).pathname} | HTTP ${result.http_status}`;
    byId("overview-title").textContent = `${currentName()} / configuration overview`;
    byId("overview-context").textContent = `SIMULATED ${byId("scenario").value === "baseline" ? "baseline" : "improved"} findings for ${result.final_url}`;
    byId("sample-context").textContent = {original: "Original sample: deliberately incomplete headers and a session cookie needing review.", store: "Northstar Store: a fictional checkout with two cookies. Compare credentialed CORS reflection, short HSTS and cookie flags. A JavaScript-readable preferences cookie still needs context after improvements.", portal: "Orbit Docs: a fictional public documentation page with no cookies. Public wildcard CORS is intentional; the baseline needs an explicit referrer policy."}[byId("sample-site").value] + " All observations are simulated.";
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
    const cookies = result.findings.filter(f => f.key.startsWith("cookie"));
    byId("cookie-content").innerHTML = "";
    for (const [id, f] of [["cors-content", cors], ...cookies.map(f => ["cookie-content", f])]) {
      byId(id).innerHTML = (id === "cookie-content" ? byId(id).innerHTML : "") + `<div class="cookie-observation">${badge(f)}<p>${escape(f.detail)}</p><div class="evidence">${escape(f.evidence || (id === "cors-content" ? "Review the CORS observation above in the context of this endpoint." : "No cookie values are retained."))}</div><p class="detail-note">${id === "cors-content" ? "One synthetic Origin is tested. This does not confirm sensitive data exposure." : "Only cookie names and attribute observations are reported; cookie values are omitted."}</p></div>`;
    }
    const rank = {HIGH:0, MEDIUM:1, LOW:2};
    const warnings = result.findings.filter(f => f.status === "WARN").sort((a,b) => rank[a.severity] - rank[b.severity]);
    byId("recommendation-list").innerHTML = warnings.length ? warnings.map((f,i) => `<article class="recommendation"><span class="number">${String(i+1).padStart(2,"0")}</span><div><h3>${escape(f.title)}</h3><p>${escape(f.recommendation)}</p></div>${badge(f)}</article>`).join("") : '<p class="muted">No warnings in this improved fixture. Continue reviewing application behavior, policy values and authenticated routes; a score of 100 does not guarantee security.</p>';
    byId("status").textContent = `${currentName()} - simulated ${byId("scenario").value} configuration loaded. Score ${result.score} of 100; ${result.summary.warnings} warnings.`;
  }
  function changeSample() {
    const site = byId("sample-site").value;
    selected = (site === "original" ? "" : site + "-") + byId("scenario").value;
    byId("search").value = "";
    byId("filter").value = "ALL";
    render();
    byId("demo-progress").textContent = `${currentName()} loaded | Score ${data[selected].score}/100 | All findings and exports updated | Simulated data`;
  }
  byId("scenario").addEventListener("change", changeSample);
  byId("sample-site").addEventListener("change", changeSample);
  byId("filter").addEventListener("change", renderHeaders);
  byId("export").disabled = false;
  function htmlReport(result) {
    const rows = result.findings.map(f => `<article><h2>${escape(f.title)} <small>${escape(f.status)} / ${escape(f.severity)}</small></h2><p>${escape(f.detail)}</p><p><b>Recommendation:</b> ${escape(f.recommendation)}</p>${f.evidence ? `<p><b>Evidence:</b> ${escape(f.evidence)}</p>` : ""}</article>`).join("");
    return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CyberShield simulated audit report</title><style>body{font:15px/1.7 system-ui,sans-serif;color:#172436;max-width:960px;margin:40px auto;padding:0 24px}header{border-bottom:3px solid #126b5a;padding-bottom:24px}h1{font-size:32px}h2{font-size:18px}small{font-size:12px;color:#53657c}article{border-bottom:1px solid #ccd5e1;padding:16px 0;break-inside:avoid}.notice{padding:12px;background:#edf5eb}footer{margin:30px 0;color:#53657c}@media print{body{margin:0}}</style></head><body><header><small>CYBERSHIELD / AUTOMATED WEB SCANNER</small><h1>Security configuration report</h1><p class="notice"><strong>SIMULATED DATA.</strong> No real website was scanned. Scenario: ${escape(selected)}.</p><p>Sample target: ${escape(result.final_url)}<br>Configuration score: <b>${result.score}/100 | Grade ${escape(result.grade)}</b><br>Checks: ${result.summary.total_checks} | Warnings: ${result.summary.warnings} | Passed: ${result.summary.passed}</p></header>${rows}<footer>${escape(result.disclaimer)}<p>Scoring: start at 100; subtract 17 per high, 10 per medium and 5 per low warning, with a floor of zero. Fixture date: ${escape(result.scanned_at)} (not a live scan timestamp).</p></footer></body></html>`;
  }
  byId("search").addEventListener("input", renderHeaders);
  byId("print").addEventListener("click", () => window.print());
  byId("run-demo").addEventListener("click", async () => {
    const button = byId("run-demo");
    button.disabled = true;
    byId("scenario").disabled = true;
    byId("sample-site").disabled = true;
    byId("demo-progress").classList.add("running");
    const stages = ["SIMULATION 1/3 | Loading synthetic response headers...", "SIMULATION 2/3 | Reviewing header, CORS and cookie observations...", "SIMULATION 3/3 | Preparing score and recommendations..."];
    for (const stage of stages) {
      byId("demo-progress").textContent = stage;
      await new Promise(resolve => setTimeout(resolve, 400));
    }
    render();
    byId("demo-progress").textContent = `Demo complete | ${currentName()} | ${data[selected].summary.total_checks} checks | ${data[selected].summary.warnings} review items | No network scan performed`;
    byId("demo-progress").classList.remove("running");
    button.disabled = false;
    byId("scenario").disabled = false;
    byId("sample-site").disabled = false;
    button.textContent = "Run demo again";
  });
  byId("export").addEventListener("click", () => {
    const result = data[selected];
    const format = byId("export-format").value;
    const csvCell = value => '"' + String(value).replace(/"/g, '""') + '"';
    const csvRows = [["Mode", "Scenario", "Target", "Control", "Status", "Severity", "Observation", "Recommendation", "Evidence"], ...result.findings.map(f => ["SIMULATED", selected, result.final_url, f.title, f.status, f.severity, f.detail, f.recommendation, f.evidence])];
    const formats = {
      json: [JSON.stringify(result, null, 2), "application/json"],
      html: [htmlReport(result), "text/html"],
      csv: ["\ufeff" + csvRows.map(row => row.map(csvCell).join(",")).join("\r\n"), "text/csv;charset=utf-8"]
    };
    const [content, type] = formats[format];
    const url = URL.createObjectURL(new Blob([content], {type}));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `cybershield-${selected}-simulated.${format}`;
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    byId("demo-progress").textContent = `${format.toUpperCase()} sample report prepared | ${result.findings.length} observations | Simulated data only`;
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
