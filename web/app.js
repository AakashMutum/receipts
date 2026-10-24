/* Receipts command center. Plain JavaScript, no build step, so a judge can read it. */
(() => {
  "use strict";

  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const DIM_NAMES = { CITY: "City", CATEGORY_NAME: "Category", CHANNEL: "Channel", GATEWAY: "Gateway", CURRENCY_CODE: "Currency", TIER: "Merchant tier" };
  const VERDICT_TEXT = { NO_INCIDENT: "No incident", REAL_CHANGE: "Real change", PROVEN_FAULT: "Proven fault", UNEXPLAINED: "Unexplained" };
  const state = { overview: null, selected: "ist_utc", case: null, busy: false };

  // number formatting in Indian units --------------------------------------------------
  function inrParts(v) {
    if (v == null || isNaN(v)) return ["n/a", ""];
    const a = Math.abs(v), sign = v < 0 ? "-" : "";
    if (a >= 1e7) return [sign + "₹" + (a / 1e7).toFixed(2), "crore"];
    if (a >= 1e5) return [sign + "₹" + (a / 1e5).toFixed(2), "lakh"];
    return [sign + "₹" + Math.round(a).toLocaleString("en-IN"), ""];
  }
  const inr = (v) => inrParts(v).join(" ").trim();
  const inrShort = (v) => { const [n, u] = inrParts(v); return n + (u === "crore" ? " cr" : u === "lakh" ? " L" : ""); };
  const pct = (v, d = 1) => (v == null ? "n/a" : (v > 0 ? "+" : "") + (v * 100).toFixed(d) + "%");
  const num = (v) => Number(v || 0).toLocaleString("en-IN");
  const dayLabel = (iso, long) => {
    const d = new Date(iso + "T00:00:00");
    const dm = d.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
    return long ? d.toLocaleDateString("en-GB", { weekday: "short" }) + " " + dm : dm;
  };
  const ms = (v) => (v >= 1000 ? (v / 1000).toFixed(2) + " s" : Math.round(v) + " ms");

  function toast(msg) {
    const t = $("#toast");
    t.textContent = msg;
    t.hidden = false;
    clearTimeout(toast._t);
    toast._t = setTimeout(() => (t.hidden = true), 6000);
  }

  async function api(path, opts = {}) {
    const r = await fetch(path, { headers: { "content-type": "application/json" }, ...opts });
    if (!r.ok) {
      let msg = r.statusText;
      try { msg = (await r.json()).detail || msg; } catch (e) { /* keep status text */ }
      throw new Error(msg);
    }
    return r.json();
  }

  // header chips --------------------------------------------------------------------------
  function renderChips(o) {
    const b = o.backend;
    const chips = [];
    if (b.backend === "exasol" && !b.standin) {
      chips.push(`<span class="chip live"><b>Exasol</b> ${esc(b.version || "")}</span>`);
      chips.push(`<span class="chip">Python UDF <b>${b.udf === "in-database" ? "in the database" : esc(b.udf)}</b></span>`);
    } else {
      chips.push(`<span class="chip standin"><b>Local stand-in</b> (${esc(b.backend === "exasol-shadow" ? "Exasol SQL on DuckDB" : "DuckDB")})</span>`);
    }
    chips.push(`<span class="chip"><b>${num(o.raw_payment_rows)}</b> payment rows</span>`);
    $("#chips").innerHTML = chips.join("");
  }

  // scenario picker --------------------------------------------------------------------------
  function renderScenarios(list) {
    if (!$("#scenarios")) return;  // lab only: absent in normal mode
    const kinds = { control: "control", fault: "planted fault", unknown: "no detector" };
    $("#scenarios").innerHTML = list.map((s) => `
      <button type="button" class="sc" role="radio" aria-checked="${s.id === state.selected}" data-id="${s.id}" tabindex="${s.id === state.selected ? 0 : -1}">
        <span class="pip" aria-hidden="true"></span>
        <span class="name">${esc(s.title)}</span>
        <span class="kind">${kinds[s.kind] || ""}</span>
        <span class="story">${esc(s.story)}</span>
      </button>`).join("");
  }

  function select(id, focus) {
    state.selected = id;
    document.querySelectorAll(".sc").forEach((b) => {
      const on = b.dataset.id === id;
      b.setAttribute("aria-checked", on);
      b.tabIndex = on ? 0 : -1;
      if (on && focus) b.focus();
    });
  }

  if ($("#scenarios")) $("#scenarios").addEventListener("click", (e) => {
    const b = e.target.closest(".sc");
    if (b) select(b.dataset.id, false);
  });
  if ($("#scenarios")) $("#scenarios").addEventListener("keydown", (e) => {
    if (!["ArrowDown", "ArrowUp", "ArrowRight", "ArrowLeft"].includes(e.key)) return;
    e.preventDefault();
    const ids = [...document.querySelectorAll(".sc")].map((b) => b.dataset.id);
    const i = ids.indexOf(state.selected);
    const n = (i + (e.key === "ArrowDown" || e.key === "ArrowRight" ? 1 : -1) + ids.length) % ids.length;
    select(ids[n], true);
  });

  // hero: the number and its status -----------------------------------------------------------
  function renderHero(board, c) {
    const pts = board.points;
    const today = pts[pts.length - 1];
    const day = state.overview.incoming_day;
    $("#day-label").textContent = dayLabel(day, true);
    const status = $("#status");
    const big = $("#big");
    const [n, u] = inrParts(today && today.day === day ? today.value : null);
    $("#big-value").innerHTML = `${esc(n)}<span class="unit">${esc(u)}</span>`;

    if (state.overview.stale) {  // the database holds another day than the one the page should show
      big.classList.remove("is-held");
      status.className = "status";
      status.innerHTML = `<span class="flag">STALE</span><span class="msg">${esc(state.overview.stale.message)}</span>`;
      return;
    }
    if (!today || today.day !== day) {
      big.classList.remove("is-held");
      status.className = "status";
      status.innerHTML = `<span class="flag">WAITING</span><span class="msg">Tonight's batch has not landed. ${state.overview.lab ? "Pick a scenario and run the gate, or break the pipeline." : "Run receipts demo, or load a batch."}</span>`;
      return;
    }
    const prev = pts.filter((p) => p.day < day && !p.held).slice(-1)[0];
    const cand = c ? c.values.candidate : board.candidate_today;
    big.classList.toggle("is-held", today.held);
    if (today.status === "HELD") {
      status.className = "status held";
      status.innerHTML = `<span class="flag">HELD</span><span class="msg"><span>Showing ${esc(dayLabel(prev.day, true))}'s trusted value. The pipeline says <s>${esc(inr(cand))}</s>${c ? ` and ${c.verdict === "PROVEN_FAULT" ? "the cause is proven" : "the cause is not proven yet"}` : ""}.</span></span>`;
    } else if (today.status === "REAL_CHANGE") {
      status.className = "status real";
      status.innerHTML = `<span class="flag">PUBLISHED</span><span class="msg">A real change of ${esc(pct(c ? c.values.change_pct : null))}. Investigated, no data fault found.</span>`;
    } else if (today.status === "CORRECTED") {
      status.className = "status corrected";
      status.innerHTML = `<span class="flag">CORRECTED</span><span class="msg"><span>Proven correction approved by a person. The pipeline said <s>${esc(inr(cand))}</s>.</span></span>`;
    } else {
      status.className = "status trusted";
      status.innerHTML = `<span class="flag">PUBLISHED</span><span class="msg">Trusted. All six checks passed on tonight's batch.</span>`;
    }
  }

  // trend chart ------------------------------------------------------------------------------------
  function renderTrend(board, c) {
    const W = 760, H = 230, L = 52, R = 104, T = 14, B = 26;
    const pts = board.points.slice(-29);
    const day = state.overview.incoming_day;
    const vals = pts.map((p) => p.value);
    let cand = c ? c.values.candidate : board.candidate_today;
    const fix = c && c.values.corrected;
    const todayPt = pts[pts.length - 1];
    const held = todayPt && todayPt.day === day && todayPt.held;
    const scope = vals.concat(fix ? [fix] : []);
    if (c) scope.push(c.values.band_low, c.values.band_high);
    let lo = Math.min(...scope), hi = Math.max(...scope);
    let off = false;
    if (held && cand != null) {
      if (cand > hi * 1.6 || cand < lo * 0.4) off = true; else { lo = Math.min(lo, cand); hi = Math.max(hi, cand); }
    }
    const pad = (hi - lo) * 0.12 || hi * 0.05;
    lo -= pad; hi += pad;
    const n = pts.length + (held ? 0 : 0);
    const x = (i) => L + (i * (W - L - R)) / Math.max(n - 1, 1);
    const y = (v) => T + (H - T - B) * (1 - (v - lo) / (hi - lo));
    const g = [];
    for (let k = 0; k <= 3; k++) {
      const v = lo + ((hi - lo) * k) / 3;
      g.push(`<line class="t-grid" x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}"/><text class="t-axis" x="${L - 8}" y="${y(v) + 4}" text-anchor="end">${esc(inrShort(v))}</text>`);
    }
    if (c) {
      const i0 = Math.max(0, n - 15);
      g.push(`<rect class="t-band" x="${x(i0)}" width="${x(n - 1) - x(i0)}" y="${y(c.values.band_high)}" height="${Math.max(2, y(c.values.band_low) - y(c.values.band_high))}" rx="3"/>`);
    }
    const line = pts.map((p, i) => (held && i === n - 1 ? null : `${x(i)},${y(p.value)}`)).filter(Boolean).join(" ");
    g.push(`<polyline class="t-line" points="${line}"/>`);
    [0, Math.floor((n - 1) / 2), n - 1].forEach((i) => g.push(`<text class="t-axis" x="${x(i)}" y="${H - 6}" text-anchor="middle">${esc(dayLabel(pts[i].day))}</text>`));
    const xi = x(n - 1);
    if (todayPt && todayPt.day === day) {
      if (held) {
        const yc = off ? T + 4 : y(cand);
        if (off) g.push(`<path d="M${xi - 7},${yc + 10} L${xi},${yc} L${xi + 7},${yc + 10}" fill="none" stroke="var(--hold)" stroke-width="3"/>`);
        else g.push(`<circle class="t-dot-cand" cx="${xi}" cy="${yc}" r="6"/>`);
        g.push(`<text class="t-label" x="${xi + 12}" y="${yc + 5}" fill="var(--hold)">Pipeline ${esc(inrShort(cand))}</text>`);
        if (fix) {
          g.push(`<circle class="t-dot-fix" cx="${xi}" cy="${y(fix)}" r="6"/>`);
          g.push(`<text class="t-label" x="${xi + 12}" y="${y(fix) + 5}" fill="var(--green)">Proven ${esc(inrShort(fix))}</text>`);
        }
      } else {
        g.push(`<circle class="t-dot-ok" cx="${xi}" cy="${y(todayPt.value)}" r="6"/>`);
        g.push(`<text class="t-label" x="${xi + 12}" y="${y(todayPt.value) + 5}" fill="var(--green)">${esc(inrShort(todayPt.value))}</text>`);
      }
    }
    $("#trend").innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Daily revenue for the last four weeks">${g.join("")}</svg>`;
    $("#trend-cap").textContent = c ? "Shaded: the normal range, from the last 14 trusted days." : "Published daily revenue, last four weeks.";
  }

  // the receipt ----------------------------------------------------------------------------------------
  function ruleList(rules) {
    return `<ul class="r-rules">${rules.map((r) => `<li><span class="${r.passed ? "ok" : "no"}">${r.passed ? "✓" : "✗"}</span><span>${esc(r.rule)}<br><span class="r-small">${esc(r.detail)}</span></span></li>`).join("")}</ul>`;
  }

  function renderPaper(c, animate) {
    const v = c.values;
    const fired = c.suspects.filter((s) => s.fired);
    const order = { CONFIRMED: 0, PARTIAL: 1, REJECTED: 2 };
    fired.sort((a, b) => order[a.outcome] - order[b.outcome]);
    const clean = c.suspects.filter((s) => !s.fired);
    const outcomeWord = { CONFIRMED: "CONFIRMED", PARTIAL: "PARTIAL", REJECTED: "RULED OUT" };
    const items = fired.map((s) => `
      <div class="r-item ${s.outcome.toLowerCase()}">
        <div class="r-row"><span>${esc(s.title)}</span><span class="v">${outcomeWord[s.outcome]}</span></div>
        <div class="r-note">${esc(s.blamed.table)}.${esc(s.blamed.column)}<br>${esc(s.slice_text)}</div>
        <div class="r-note">${esc(s.summary)}</div>
        ${ruleList(s.rules)}
        ${s.reason ? `<div class="r-note"><b>${esc(s.reason)}</b></div>` : ""}
        <details><summary>Evidence SQL, ${esc(ms(s.ms))}${s.engine && s.engine !== "sql" ? ", " + esc(s.engine) : ""}</summary><pre>${esc(s.sql)}</pre></details>
      </div>`).join("");
    const real = c.verdict === "REAL_CHANGE" ? `
      <hr class="r-rule">
      <div class="r-sec">CHECKS BEHIND A REAL CHANGE</div>
      <div class="r-row"><span>Volume moved with value</span><span class="v">ticket ${pct(c.checks.volume.ticket_ratio - 1)}</span></div>
      <div class="r-row"><span>Raw payments reconcile</span><span class="v">${c.checks.reconciliation.ok ? "1 to 1" : "no"}</span></div>` : "";
    const stamp = c.trust_status === "HELD" ? `<div class="stamp held">HELD</div>` :
      c.trust_status === "CORRECTED" ? `<div class="stamp ok">CORRECTED</div>` : `<div class="stamp ok">PUBLISHED</div>`;
    const d = c.decomposition;
    const llmBtn = state.overview.llm ? `<button type="button" id="explain-btn">Explain with AI</button>` : "";
    const src = c.explanation.source === "llm" ? `Written by ${esc(c.explanation.model || "an LLM")} from the aggregated case. The verdict above is not its decision.` :
      (state.overview.llm ? "Template text." : "Template text. Set ANTHROPIC_API_KEY for a written explanation.");
    const p = $("#paper");
    p.innerHTML = `
      ${stamp}
      <div class="r-head">
        <div class="r-brand">Receipts</div>
        <div class="r-small">case ${esc(c.case_id)}</div>
        <div class="r-small">${esc(c.metric_label)}, ${esc(c.day_label)}</div>
      </div>
      <hr class="r-rule">
      <div class="r-row big-row"><span>Pipeline value</span><span class="v">${esc(inr(v.candidate))}</span></div>
      <div class="r-row"><span>${v.seasonal ? "Usual for this weekday" : "Usual, last 14 days"}</span><span class="v">${esc(inr(v.baseline))}</span></div>
      <div class="r-row"><span>Normal range</span><span class="v">${esc(inrShort(v.band_low))} to ${esc(inrShort(v.band_high))}</span></div>
      <div class="r-row"><span>Change</span><span class="v">${esc(pct(v.change_pct))}</span></div>
      <hr class="r-rule">
      <div class="r-sec">SUSPECTS</div>
      ${items || `<div class="r-clean">No detector fired on tonight's batch.</div>`}
      ${clean.length ? `<div class="r-clean">Clean: ${clean.map((s) => esc(s.title.toLowerCase())).join(", ")}.</div>` : ""}
      ${real}
      <hr class="r-rule">
      ${v.corrected != null ? `<div class="r-row big-row"><span>Corrected value</span><span class="v">${esc(inr(v.corrected))}</span></div>` : ""}
      <div class="r-row"><span>Slices tested</span><span class="v">${num(d.hypotheses)}</span></div>
      <div class="r-row"><span>Rows in scope</span><span class="v">${num(d.rows_in_scope)}</span></div>
      <div class="r-row"><span>SQL statements</span><span class="v">${num(c.statements)}</span></div>
      <div class="r-row"><span>Total time</span><span class="v">${esc(ms(c.total_ms))}</span></div>
      <div class="r-row"><span>Measured by Exasol</span><span class="v">${esc(c.exasol_measured && c.exasol_measured.source && c.exasol_measured.source.startsWith("EXA_") ? ms(c.exasol_measured.db_ms) : c.exasol_measured && c.exasol_measured.source === "client" ? "unavailable" : "n/a")}</span></div>
      <hr class="r-rule double">
      <div class="r-row"><span class="r-verdict">Verdict</span><span class="r-verdict">${esc(VERDICT_TEXT[c.verdict])}</span></div>
      <div class="r-explain" id="explain-text">${esc(c.explanation.text)}<span class="src">${src}</span>${llmBtn}</div>
      <div class="r-small" style="margin-top:16px;text-align:center">Written back to RECEIPTS.CASES and RECEIPTS.EVIDENCE</div>`;
    if (animate) { p.classList.remove("printing"); void p.offsetWidth; p.classList.add("printing"); }
    const eb = $("#explain-btn");
    if (eb) eb.addEventListener("click", async () => {
      eb.disabled = true; eb.textContent = "Writing";
      try {
        const r = await api(`/api/case/${c.case_id}/explain`, { method: "POST" });
        $("#explain-text").innerHTML = `${esc(r.text)}<span class="src">${r.source === "llm" ? `Written by ${esc(r.model)} from the aggregated case. The verdict is not its decision.` : esc(r.note || "Template text.")}</span>`;
      } catch (e) { toast(e.message); eb.disabled = false; eb.textContent = "Explain with AI"; }
    });
  }

  // where it moved ---------------------------------------------------------------------------------------
  function renderWhere(c) {
    const d = c.decomposition;
    const dims = Object.entries(d.by_dimension);
    const maxAbs = Math.max(1, ...dims.flatMap(([, x]) => x.values.map((v) => Math.abs(v.delta))));
    const top = d.top_single[0];
    const hotKey = top ? Object.entries(top.dims)[0].join("=") : "";
    $("#where-sub").textContent = `${num(d.hypotheses)} slices tested in one GROUP BY CUBE over ${num(d.rows_in_scope)} rows, ${ms(d.ms)} in the database. Bars show each slice's change against its usual level.`;
    const html = dims.map(([dim, x]) => `
      <div class="dim"><h4>${esc(DIM_NAMES[dim] || dim)}</h4>
      ${x.values.slice(0, 5).map((v) => {
        const w = (Math.abs(v.delta) / maxAbs) * 50;
        const left = v.delta >= 0 ? 50 : 50 - w;
        const hot = `${dim}=${v.value}` === hotKey;
        return `<div class="bar-row"><span class="lbl" title="${esc(v.value)}">${esc(v.value)}</span>
          <span class="track"><span class="mid"></span><span class="fill${hot ? " hot" : ""}" style="left:${left}%;width:${Math.max(w, 0.6)}%"></span></span>
          <span class="pct">${esc(pct(v.pct_change, 0))}</span></div>`;
      }).join("")}</div>`).join("");
    const pair = d.top_pairs[0];
    const pairTxt = pair && Math.abs(d.total.delta) > 0 ? `<p class="top-pair">${pairText(pair, c.values.change_pct)}</p>` : "";
    $("#where").innerHTML = `<div class="dims">${html}</div>${pairTxt}`;
  }

  // a share of a small total is meaningless (two faults that cancel give -620%), so below 5% use the slice's own change
  function pairText(pair, totalChange) {
    const name = Object.entries(pair.dims).map(([k, v]) => `${esc((DIM_NAMES[k] || k).toLowerCase())} ${esc(v)}`).join(" and ");
    if (Math.abs(totalChange || 0) >= 0.05) return `Largest two-way slice: <b>${name}</b>, ${Math.round(pair.share * 100)}% of the total change.`;
    if (pair.pct_change == null) return `Largest two-way slice: <b>${name}</b>, new today with no usual level.`;
    const p = Math.round(Math.abs(pair.pct_change) * 100);
    const how = p === 0 ? "level with" : `${pair.pct_change > 0 ? "up" : "down"} ${p}% against`;
    return `Largest two-way slice: <b>${name}</b>, ${how} its usual level.`;
  }

  // undo test chart ----------------------------------------------------------------------------------------
  function renderUndo(c) {
    const pub = c.series.published;
    const days = Object.keys(pub).sort();
    let fixed = c.series.corrected, label = "Proven correction", ruled = false;
    let note = "";
    if (!fixed) {
      const tried = c.suspects.filter((s) => s.undo).sort((a, b) => Math.abs(b.move_pct || 0) - Math.abs(a.move_pct || 0))[0];
      if (tried) { fixed = tried.undo.series; label = `Undo of ${tried.title.toLowerCase()} (ruled out)`; note = tried.reason; ruled = true; }
    }
    if (c.verdict === "PROVEN_FAULT") {
      const h = c.combined_undo.history_check === "RESTORED" ? "History comes back to exactly what was published" : "History is untouched";
      $("#undo-sub").textContent = `Re-run in a sandbox schema with the fault removed. Today returns to ${inr(c.values.corrected)}, inside the normal range. ${h}.`;
    } else if (fixed) {
      $("#undo-sub").textContent = note || "Undoing the suspect did not bring the number back.";
    } else {
      $("#undo-sub").textContent = c.verdict === "NO_INCIDENT" ? "Nothing to undo. The batch is clean." : "No detector produced something to undo. Receipts holds the value instead of guessing.";
    }
    const all = days.concat([c.day]);
    const vals = days.map((d) => pub[d]).concat([c.values.candidate]);
    const fx = fixed ? all.map((d) => fixed[d]).filter((v) => v != null) : [];
    let lo = Math.min(...vals, ...fx), hi = Math.max(...vals, ...fx);
    const capHi = Math.max(...days.map((d) => pub[d])) * 1.8;
    const off = c.values.candidate > capHi;
    if (off) hi = Math.max(...days.map((d) => pub[d]), ...fx.filter((v) => v < capHi));
    const pad = (hi - lo) * 0.15 || hi * 0.05; lo -= pad; hi += pad;
    const W = 640, H = 190, L = 50, R = 16, T = 12, B = 24;
    const x = (i) => L + (i * (W - L - R)) / (all.length - 1);
    const y = (v) => T + (H - T - B) * (1 - (Math.min(v, hi) - lo) / (hi - lo));
    const g = [];
    [lo + pad, hi - pad].forEach((v) => g.push(`<text class="t-axis" x="${L - 6}" y="${y(v) + 4}" text-anchor="end">${esc(inrShort(v))}</text><line class="t-grid" x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}"/>`));
    g.push(`<polyline class="u-pub" points="${days.map((d, i) => `${x(i)},${y(pub[d])}`).join(" ")}"/>`);
    if (fixed) g.push(`<polyline class="u-fix${ruled ? " ruled" : ""}" points="${all.map((d, i) => (fixed[d] != null ? `${x(i)},${y(fixed[d])}` : null)).filter(Boolean).join(" ")}"/>`);
    const ci = all.length - 1;
    g.push(`<circle class="u-cand" cx="${x(ci)}" cy="${off ? T + 6 : y(c.values.candidate)}" r="6"/>`);
    if (fixed && fixed[c.day] != null && !ruled) g.push(`<circle class="u-fixdot" cx="${x(ci)}" cy="${y(fixed[c.day])}" r="5"/>`);
    g.push(`<text class="t-axis" x="${x(0)}" y="${H - 5}">${esc(dayLabel(all[0]))}</text><text class="t-axis" x="${x(ci)}" y="${H - 5}" text-anchor="end">${esc(dayLabel(c.day))}</text>`);
    $("#undo").innerHTML = `<div class="undo-svg"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Published history, today's value and the value with the fault undone">${g.join("")}</svg></div>
      <div class="legend"><span><i style="background:var(--ink-faint)"></i>Published history</span><span><i style="background:var(--hold)"></i>Pipeline today${off ? " (off the chart)" : ""}</span>${fixed ? `<span><i style="background:${ruled ? "var(--ink-soft)" : "var(--green)"}"></i>${esc(label)}</span>` : ""}</div>`;
  }

  // lineage strip ---------------------------------------------------------------------------------------------
  function renderLineage(c) {
    const lin = c.lineage;
    const blamed = {};
    c.suspects.filter((s) => s.outcome === "CONFIRMED" || s.outcome === "PARTIAL").forEach((s) => { blamed[s.blamed.table] = (blamed[s.blamed.table] || []).concat(s.blamed.column); });
    const views = new Set(lin.edges.flat().filter((t) => t.startsWith("PIPE.")));
    const staging = [...views].filter((v) => !/FCT_|DAILY_/.test(v)).sort();
    const node = (t, cls = "") => `<div class="node ${cls}${blamed[t] ? " blamed" : ""}">${esc(t)}${blamed[t] ? `<small>${esc(blamed[t].join(", "))}</small>` : ""}</div>`;
    const src = c.backend.backend === "exasol" && !c.backend.standin ? "SYS.EXA_ALL_VIEWS" : (c.backend.backend === "exasol-shadow" ? "the Exasol view text" : "duckdb_views()");
    $("#lineage-sub").textContent = `${lin.views_parsed} view definitions read from ${src} and parsed in ${ms(lin.ms)}. No external catalog.`;
    $("#lineage").innerHTML = `
      <div class="lin-col"><h4>Raw sources</h4>${lin.raw_tables.map((t) => node(t)).join("")}</div>
      <div class="lin-col"><h4>Staging and dimensions</h4>${staging.map((t) => node(t)).join("")}</div>
      <div class="lin-col"><h4>Fact</h4>${node("PIPE.FCT_REVENUE")}</div>
      <div class="lin-col"><h4>Metric</h4>${node(lin.metric, "metric")}</div>`;
    $("#lineage").insertAdjacentHTML("afterend", "");
    const extra = document.getElementById("lin-cols") || Object.assign(document.createElement("p"), { id: "lin-cols", className: "lin-cols" });
    extra.innerHTML = `Feeds the value: ${lin.value_columns.map((x) => `<code>${esc(x)}</code>`).join(" ")}<br>Decides which rows and which day: ${lin.row_columns.map((x) => `<code>${esc(x)}</code>`).join(" ")}`;
    $("#lineage").after(extra);
  }

  // fix diff + approval -------------------------------------------------------------------------------------------
  function renderFix(c) {
    const card = $("#fix-card");
    if (!c.fix_diff) { card.hidden = true; return; }
    card.hidden = false;
    $("#diff").innerHTML = c.fix_diff.split("\n").map((l) => {
      const cls = l.startsWith("+") && !l.startsWith("+++") ? "add" : l.startsWith("-") && !l.startsWith("---") ? "del" : l.startsWith("@@") ? "hunk" : "";
      return `<span class="${cls}">${esc(l)}</span>`;
    }).join("\n");
    const btn = $("#approve");
    const done = c.trust_status === "CORRECTED";
    btn.disabled = done;
    btn.textContent = done ? "Approved" : `Approve and publish ${inr(c.values.corrected)}`;
    $("#approve-note").textContent = done ? "Published as CORRECTED. Agents now see it as safe to use." : "Logged in RECEIPTS.APPROVALS.";
  }

  $("#approve").addEventListener("click", async () => {
    const c = state.case;
    if (!c) return;
    $("#approve").disabled = true;
    try {
      const r = await api(`/api/case/${c.case_id}/approve`, { method: "POST", body: JSON.stringify({ note: "Approved from the command center" }) });
      state.case = r.case;
      state.overview.board = r.board;
      renderAll(false);
    } catch (e) { toast(e.message); $("#approve").disabled = false; }
  });

  // timings and evaluation ------------------------------------------------------------------------------------------
  // what Exasol itself recorded for the run, from EXA_STATISTICS.EXA_SQL_LAST_DAY
  function measuredText(c) {
    const m = c.exasol_measured;
    if (!m) return "Measured by Exasol: not recorded for this case.";
    if (m.source === "n/a") return "Measured by Exasol: n/a on the local stand-in.";
    if (m.source === "client") return `Measured by Exasol: unavailable (${m.note}) Client-side: ${ms(m.db_ms)}.`;
    return `Measured by Exasol: ${num(m.statements)} statements, ${ms(m.db_ms)} inside the database` +
      (m.temp_ram_peak_mib != null ? `, peak temporary memory ${num(m.temp_ram_peak_mib)} MiB` : "") + `, from ${m.source}.`;
  }

  function renderTimings(c) {
    const max = Math.max(...c.timings.map((t) => t.ms), 1);
    const m = c.exasol_measured && c.exasol_measured.steps ? c.exasol_measured.steps : null;
    $("#time-sub").textContent = `${ms(c.total_ms)} from batch landed to verdict, ${num(c.statements)} SQL statements, ${ms(c.db_ms)} of it inside the database as seen by the client. ${measuredText(c)}`;
    $("#timings").innerHTML = c.timings.map((t, i) => {
      const x = m && m[i] && m[i].step === t.step ? m[i] : null;
      const ex = x ? `<span class="detail exa">Measured by Exasol: ${esc(ms(x.db_ms))} in ${x.statements} statement${x.statements === 1 ? "" : "s"}${x.temp_ram_peak_mib ? `, peak ${num(x.temp_ram_peak_mib)} MiB` : ""}</span>` : "";
      return `<li><span>${esc(t.step)}</span><span class="ms">${esc(ms(t.ms))}</span>
      <span class="tb"><span style="width:${(t.ms / max) * 100}%"></span></span>${t.detail ? `<span class="detail">${esc(t.detail)}</span>` : ""}${ex}</li>`;
    }).join("");
  }

  function renderEval(ev) {
    if (!ev) { $("#eval-sub").textContent = "Run `make eval` to score Receipts against ground truth."; $("#score").innerHTML = ""; return; }
    $("#eval-sub").textContent = `${ev.runs} runs: ${ev.scenarios} scenarios on ${ev.seeds.length} freshly generated datasets. Receipts passed ${ev.passed} of ${ev.runs}. Corrected values land within ${ev.corrected_value_error_pct.max}% of the true clean value.`;
    const rows = [["Receipts", ev.systems.receipts, "us"], ["Detectors without the undo test", ev.systems.detectors_only, ""], ["Threshold alert", ev.systems.threshold_alert, ""]];
    const f = (v) => Math.round(v * 100) + "%";
    $("#score").innerHTML = `<thead><tr><th>System</th><th>Right call to hold or publish</th><th>Named causes that were right</th><th>Planted causes found</th><th>Wrong causes named</th></tr></thead>
      <tbody>${rows.map(([n, m, cls]) => `<tr class="${cls}"><td>${n}</td><td>${f(m.hold_decision_accuracy)}</td><td>${f(m.cause_precision)}</td><td>${f(m.cause_recall)}</td><td>${m.false_causes}</td></tr>`).join("")}</tbody>`;
  }

  // agents ------------------------------------------------------------------------------------------------------------
  async function askAgents() {
    $("#ask").disabled = true;
    try {
      const r = await api("/api/agent");
      $("#question").textContent = `"${r.question}"`;
      $("#naive-answer").textContent = r.naive.answer;
      $("#naive-sql").textContent = r.naive.sql;
      $("#trusted-answer").textContent = r.trusted.answer;
      $("#trusted-sql").textContent = r.trusted.sql;
      document.querySelector(".agent.naive").classList.toggle("wrong", r.trusted.status === "HELD");
    } catch (e) { toast(e.message); }
    $("#ask").disabled = false;
  }
  $("#ask").addEventListener("click", askAgents);

  // run (lab only) -------------------------------------------------------------------------------------------------------
  if ($("#go")) $("#go").addEventListener("click", async () => {
    if (state.busy) return;
    state.busy = true;
    const go = $("#go");
    go.disabled = true;
    go.textContent = "Running the gate";
    try {
      const r = await api("/api/run", { method: "POST", body: JSON.stringify({ scenario: state.selected }) });
      state.case = r.case;
      state.overview.board = r.board;
      renderAll(true);
      resetAgents();
    } catch (e) { toast(e.message); }
    go.disabled = false;
    go.textContent = "Land batch and run the gate";
    state.busy = false;
  });

  function resetAgents() {
    $("#question").textContent = "";
    $("#naive-answer").textContent = $("#trusted-answer").textContent = "Ask a question to see the answer.";
    document.querySelector(".agent.naive").classList.remove("wrong");
  }

  // lab: break the pipeline and watch the gate live ----------------------------------------------------------------------
  function renderLab(o) {
    if (!$("#lab") || !o.faults) return;
    const sel = $("#lab-fault");
    const opts = o.faults.map((f) => `<option value="${esc(f.id)}">${esc(f.title)}</option>`).join("");
    if (!sel.options.length) sel.innerHTML = opts;
    if ($("#rt-fault") && !$("#rt-fault").options.length) $("#rt-fault").innerHTML = opts;
    syncLab();
  }
  function syncLab() {
    const f = state.overview.faults.find((x) => x.id === $("#lab-fault").value);
    const share = $("#lab-share"), gw = $("#lab-gw");
    share.disabled = !f.share_of;
    $("#lab-share-out").textContent = f.share_of ? `${share.value}%` : "all";
    $("#lab-of").textContent = f.share_of ? `of ${f.share_of}` : "One rate is either there or not, so this fault has no share.";
    gw.hidden = $("#lab-gw-label").hidden = !f.gateways;
    if (f.gateways) gw.innerHTML = f.gateways.map((g) => `<option${g === f.gateway ? " selected" : ""}>${esc(g)}</option>`).join("");
  }
  function timeline(steps, running) {
    const li = steps.map((s) => `<li><span>${esc(s.step)}</span><span class="ms">${esc(ms(s.ms))}</span></li>`);
    if (running) li.push(`<li class="running"><span>Working</span><span class="ms"></span></li>`);
    $("#lab-timeline").innerHTML = li.join("") || `<li class="running"><span>Starting</span><span class="ms"></span></li>`;
  }
  if ($("#lab")) {
    $("#lab-fault").addEventListener("change", syncLab);
    $("#lab-share").addEventListener("input", () => { $("#lab-share-out").textContent = `${$("#lab-share").value}%`; });
    $("#lab-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      if (state.busy) return;
      state.busy = true;
      const btn = $("#lab-break");
      btn.disabled = true;
      $("#lab-result").textContent = "";
      const t0 = performance.now();
      try {
        const f = $("#lab-fault").value;
        const body = { fault: f, share: Number($("#lab-share").value) / 100, gateway: $("#lab-gw").hidden ? null : $("#lab-gw").value };
        const { job } = await api("/api/lab/break", { method: "POST", body: JSON.stringify(body) });
        let j;
        for (;;) {
          j = await api(`/api/lab/job/${job}`);
          timeline(j.steps, j.status === "running");
          if (j.status !== "running") break;
          await new Promise((r) => setTimeout(r, 250));
        }
        if (j.status === "error") throw new Error(j.error);
        state.case = j.case;
        state.overview.board = j.board;
        renderAll(false);
        resetAgents();
        const clickMs = performance.now() - t0;
        const held = j.case.trust_status === "HELD";
        $("#lab-result").innerHTML = `<span class="flag${held ? "" : " ok"}">${held ? "HELD" : "PUBLISHED"}</span>${esc(VERDICT_TEXT[j.case.verdict])}${j.case.confirmed.length ? ", cause " + esc(j.case.confirmed.join(" and ")) : ""}. Click to ${held ? "HELD" : "verdict"} in <b>${esc(ms(clickMs))}</b> (server ${esc(ms(j.server_ms))}).`;
        window.receiptsLastClickMs = clickMs;  // read by the screenshot script
      } catch (err) { toast(err.message); $("#lab-timeline").innerHTML = `<li class="idle">${esc(err.message)}</li>`; }
      btn.disabled = false;
      state.busy = false;
    });
    $("#lab-reset").addEventListener("click", async () => {
      if (state.busy) return;
      try {
        const r = await api("/api/lab/reset", { method: "POST" });
        state.overview.board = r.board;
        state.case = null;
        $("#case").hidden = true;
        resetAgents();
        $("#lab-timeline").innerHTML = `<li class="idle">Reset. Tonight's batch is not landed and nothing is published for it.</li>`;
        $("#lab-result").textContent = "";
        renderAll(false);
      } catch (err) { toast(err.message); }
    });
  }

  // lab: red team tab -----------------------------------------------------------------------------------------------------
  const OUTCOME_TEXT = { caught: "Proven, right cause", held: "Held, nothing proven", held_partial: "Held, part of the cause proven", wrong_cause: "Named a cause that was not planted", small: "Published, under 4% off", WRONG: "Published a number more than 4% off" };
  function floorChart(classes) {
    const rows = Object.entries(classes);
    const W = 600, rowH = 34, L = 190, R = 110, H = rows.length * rowH + 24;
    const x = (v) => L + (W - L - R) * v;
    const g = [0, 0.25, 0.5, 1].map((v) => `<line class="t-grid" x1="${x(v)}" x2="${x(v)}" y1="0" y2="${H - 18}"/><text x="${x(v)}" y="${H - 4}" text-anchor="middle">${v * 100}%</text>`);
    rows.forEach(([id, c], i) => {
      const y = i * rowH + 6;
      const none = c.floor == null;
      const w = none ? (W - L - R) : Math.max(3, x(c.floor) - L);
      const label = none ? "not proven" : (c.binary ? "binary" : `${Math.round(c.floor * 100)}%`) + (c.holes ? `, ${c.holes} hole${c.holes > 1 ? "s" : ""}` : "");
      g.push(`<text x="${L - 10}" y="${y + 17}" text-anchor="end">${esc(c.title)}</text>`,
        `<rect class="rt-bar${none || c.holes ? " none" : ""}" x="${L}" y="${y + 4}" width="${w}" height="18" rx="3"><title>${esc(c.title)}: ${esc(label)}</title></rect>`,
        `<text class="rt-val" x="${L + w + 6}" y="${y + 17}">${esc(label)}</text>`);
    });
    return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Detection floor per fault class">${g.join("")}</svg>`;
  }
  async function loadRedteam() {
    try {
      const r = await api("/api/lab/redteam");
      const b = r.backend;
      $("#rt-sub").textContent = `From ${r.file}: ${b.backend === "exasol" && !b.standin ? "Exasol " + (b.version || "") : "the DuckDB stand-in"}, ${num(r.orders_per_day)} orders a day, ${r.generated_at}. Run receipts redteam on synthetic data or a sandbox copy, never on live production tables.`;
      $("#rt-chart").innerHTML = floorChart(r.summary.classes);
      const holes = r.summary.holes;
      $("#rt-holes").innerHTML = holes.length ? `<b>${holes.length} hole${holes.length > 1 ? "s" : ""} found:</b><ul>${holes.map((h) => `<li>${esc(h.where)}: ${esc(OUTCOME_TEXT[h.outcome])} (${esc(pct(h.error_pct / 100, 2))})</li>`).join("")}</ul>` : "No attack got a wrong number published or a wrong cause named.";
    } catch (e) { $("#rt-chart").textContent = e.message; }
  }
  if ($("#redteam")) {
    const tabs = [["#tab-break", "#lab-break-panel"], ["#tab-redteam", "#redteam"]];
    const show = (i) => tabs.forEach(([t, p], k) => { $(t).setAttribute("aria-selected", k === i); $(t).tabIndex = k === i ? 0 : -1; $(p).hidden = k !== i; if (k === i && k === 1) loadRedteam(); });
    tabs.forEach(([t], i) => $(t).addEventListener("click", () => show(i)));
    document.querySelector(".lab-tabs").addEventListener("keydown", (e) => {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      const i = $("#tab-break").getAttribute("aria-selected") === "true" ? 1 : 0;
      show(i); $(tabs[i][0]).focus();
    });
    $("#rt-share").addEventListener("input", () => { $("#rt-share-out").textContent = `${$("#rt-share").value}%`; });
    $("#rt-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      if (state.busy) return;
      state.busy = true;
      $("#rt-go").disabled = true;
      $("#rt-result").textContent = "Attacking";
      try {
        const r = await api("/api/lab/redteam/attack", { method: "POST", body: JSON.stringify({ fault: $("#rt-fault").value, share: Number($("#rt-share").value) / 100 }) });
        const hole = r.outcome === "wrong_cause" || r.outcome === "WRONG";
        $("#rt-result").innerHTML = `<span class="flag${r.outcome === "caught" ? " ok" : ""}">${hole ? "HOLE" : r.outcome === "caught" ? "CAUGHT" : r.trust === "HELD" ? "HELD" : "MISSED"}</span>${esc(OUTCOME_TEXT[r.outcome])}. Verdict ${esc(r.verdict)}, causes ${esc(r.confirmed.join(", ") || "none")}, the pipeline was ${esc(pct(r.error_pct / 100, 2))} off. ${esc(ms(r.ms))}.`;
      } catch (err) { $("#rt-result").textContent = err.message; }
      $("#rt-go").disabled = false;
      state.busy = false;
    });
  }

  function renderAll(animate) {
    const o = state.overview, c = state.case;
    renderHero(o.board, c);
    renderTrend(o.board, c);
    if (!c) {
      $("#time-sub").textContent = "No run yet. The time of every step shows here after the gate first runs.";
      $("#timings").innerHTML = `<li class="none">No run yet</li>`;
    }
    if (c) {
      $("#case").hidden = false;
      renderPaper(c, animate);
      renderWhere(c);
      renderUndo(c);
      renderLineage(c);
      renderFix(c);
      renderTimings(c);
      if (animate) $("#case").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
    }
    renderEval(o.eval);
  }

  // alerts raised by the watcher (receipts serve --watch) ---------------------------------------------------------
  const seenAlerts = new Set();
  async function loadAlerts() {
    let list;
    try { list = await api("/api/alerts"); } catch (e) { return; }
    const box = $("#alerts");
    box.hidden = list.length === 0;
    box.innerHTML = list.length ? `<div class="wrap alerts-in"><span class="flag">ALERTS</span><ul>${list.map((a) => `
      <li><b>${esc(a.day_label)} held</b> (${esc(VERDICT_TEXT[a.verdict] || a.verdict)}). ${esc(a.cause)}
        Last trusted value: ${esc(a.last_trusted_value == null ? "none yet" : inr(a.last_trusted_value))}.
        <button type="button" data-open="${esc(a.case_id)}">Open receipt</button><button type="button" data-dismiss="${esc(a.case_id)}">Dismiss</button></li>`).join("")}</ul></div>` : "";
    const fresh = list.some((a) => !seenAlerts.has(a.case_id));
    list.forEach((a) => seenAlerts.add(a.case_id));
    if (fresh && state.overview && !state.busy) {  // the watcher judged a batch: show it without a reload
      try {
        const o = await api("/api/overview");
        state.overview = o;
        state.case = o.case;
        renderAll(false);
      } catch (e) { /* keep the page as it is */ }
    }
  }
  async function openCase(id) {
    try {
      const c = await api(`/api/case/${encodeURIComponent(id)}`);
      state.overview = await api("/api/overview");
      state.case = c;
      renderAll(true);
    } catch (e) { toast(e.message); }
  }
  $("#alerts").addEventListener("click", async (e) => {
    const open = e.target.closest("[data-open]"), dis = e.target.closest("[data-dismiss]");
    if (open) await openCase(open.dataset.open);
    if (dis) {
      try { await api(`/api/alerts/${encodeURIComponent(dis.dataset.dismiss)}/dismiss`, { method: "POST" }); } catch (err) { toast(err.message); }
      loadAlerts();
    }
  });

  async function boot() {
    try {
      const o = await api("/api/overview");
      state.overview = o;
      state.case = o.case;
      if (o.case && o.case.scenario && o.case.scenario.id) state.selected = o.case.scenario.id;
      renderChips(o);
      renderScenarios(o.scenarios);
      renderLab(o);
      renderAll(false);
      const linked = new URLSearchParams(location.search).get("case");  // the link in an alert file
      if (linked) await openCase(linked);
      await loadAlerts();
      setInterval(loadAlerts, 20000);
    } catch (e) {
      $("#status").innerHTML = `<span class="flag">OFFLINE</span><span class="msg">${esc(e.message)}</span>`;
      $("#time-sub").textContent = "No run yet.";
    }
  }
  boot();
})();
