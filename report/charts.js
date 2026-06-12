/* ════════════════════════════════════════════════════════════════
   Shared D3 chart kit — Pitfalls on the Pathway
   Single source of truth for chart rendering across index.html and
   all /report pages. Style contract: solid CSS-var fills (--ch-*),
   hairline grid, 10–12px sans labels, shared #chart-tip tooltip.
   Charts re-render on resize via each page's renderAll().
   ════════════════════════════════════════════════════════════════ */

function palette() {
  const s = getComputedStyle(document.documentElement);
  const v = k => s.getPropertyValue(k).trim();
  return {
    gold: v('--ch-gold'), goldFill: v('--ch-gold-fill'),
    blue: v('--ch-blue'), blueFill: v('--ch-blue-fill'),
    red:  v('--ch-red'),  redFill:  v('--ch-red-fill'),
    green:v('--ch-green'),greenFill:v('--ch-green-fill'),
    dim:  v('--ch-dim'),  dimBd:    v('--ch-dim-bd'),
    grid: v('--ch-grid'), text: v('--text'), strong: v('--text-strong'), muted: v('--muted'),
  };
}

/* tooltip element — create once if the page doesn't define one */
const tip = document.getElementById('chart-tip') || (() => {
  const t = document.createElement('div');
  t.id = 'chart-tip';
  document.body.appendChild(t);
  return t;
})();
function showTip(event, html) {
  tip.style.display = 'block';
  tip.innerHTML = html;
  const pad = 14;
  let x = event.clientX + pad, y = event.clientY - 10;
  if (x + 290 > window.innerWidth) x = event.clientX - 290;
  tip.style.left = x + 'px';
  tip.style.top = y + 'px';
}
function hideTip() { tip.style.display = 'none'; }

function fillFor(c, P) {
  return {
    gold:  [P.goldFill,  P.gold],
    blue:  [P.blueFill,  P.blue],
    red:   [P.redFill,   P.red],
    green: [P.greenFill, P.green],
    dim:   [P.dim,       P.dimBd],
  }[c];
}

const fmt$ = v => '$' + (v >= 1000 ? (v/1000).toLocaleString(undefined,{maximumFractionDigits:0}) + 'K' : v);
const fmtN = v => v.toLocaleString();

/* horizontal bars; value = number or [lo,hi]; optional log scale */
function hBars(elId, rows, opts = {}) {
  const P = palette();
  const el = document.getElementById(elId);
  el.innerHTML = '';
  const W = el.clientWidth || 700;
  /* narrow screens: row labels sit above the bars so bars get full width */
  const narrow = W < 520;
  const m = narrow
    ? { top: 4, right: 12, bottom: 26, left: 4 }
    : { top: 4, right: 60, bottom: 26, left: opts.left ?? 180 };
  const barH = opts.barH ?? 26, gap = 10;
  const labelH = narrow ? 17 : 0;
  const rowStep = barH + gap + labelH;
  const H = m.top + m.bottom + rows.length * rowStep;

  const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', W).attr('height', H);

  const maxV = opts.max ?? d3.max(rows, r => Array.isArray(r.v) ? r.v[1] : r.v);
  const x = opts.log
    ? d3.scaleLog().domain([opts.logMin ?? 100, maxV]).range([m.left, W - m.right])
    : d3.scaleLinear().domain([0, maxV]).range([m.left, W - m.right]);

  const ticks = opts.log ? [100, 1000, 10000, 100000, 1000000].filter(t => t <= maxV * 1.5) : x.ticks(5);
  svg.append('g').selectAll('line').data(ticks).join('line')
    .attr('x1', d => x(d)).attr('x2', d => x(d))
    .attr('y1', m.top).attr('y2', H - m.bottom)
    .attr('stroke', P.grid);
  svg.append('g').selectAll('text').data(ticks).join('text')
    .attr('x', d => x(d)).attr('y', H - 8).attr('text-anchor', 'middle')
    .attr('fill', P.muted).attr('font-size', '11px')
    .text(opts.tickFmt ?? (d => d.toLocaleString()));

  rows.forEach((r, i) => {
    const [fill, stroke] = fillFor(r.c ?? 'dim', P);
    const y = m.top + i * rowStep + labelH;
    const lo = Array.isArray(r.v) ? r.v[0] : (opts.log ? (opts.logMin ?? 100) : 0);
    const hi = Array.isArray(r.v) ? r.v[1] : r.v;
    const bw = Math.max(2, x(hi) - x(lo));
    svg.append('rect')
      .attr('x', x(lo)).attr('y', y)
      .attr('width', bw).attr('height', barH)
      .attr('rx', 3).attr('fill', fill)
      .on('mousemove', ev => showTip(ev, `<strong>${r.label}</strong><br>${r.tip ?? (Array.isArray(r.v) ? `${(opts.valFmt??fmtN)(r.v[0])} – ${(opts.valFmt??fmtN)(r.v[1])}` : (opts.valFmt??fmtN)(r.v))}`))
      .on('mouseleave', hideTip);
    if (narrow) {
      svg.append('text')
        .attr('x', m.left).attr('y', y - 5)
        .attr('fill', P.text).attr('font-size', '11px').text(r.label);
      if (r.end) {
        /* sit beside the bar when it fits; otherwise top-right of the row */
        const ex = x(lo) + bw + 6;
        const fits = ex < W - m.right - 8 * r.end.length;
        svg.append('text')
          .attr('x', fits ? ex : W - m.right)
          .attr('y', fits ? y + barH / 2 + 4 : y - 5)
          .attr('text-anchor', fits ? 'start' : 'end')
          .attr('fill', P.strong).attr('font-size', '11px').attr('font-weight', 600).text(r.end);
      }
    } else {
      svg.append('text')
        .attr('x', m.left - 10).attr('y', y + barH/2 + 4).attr('text-anchor', 'end')
        .attr('fill', P.text).attr('font-size', '12px').text(r.label);
      if (r.end) svg.append('text')
        .attr('x', x(lo) + bw + 8).attr('y', y + barH/2 + 4)
        .attr('fill', P.strong).attr('font-size', '12px').attr('font-weight', 600).text(r.end);
    }
  });
}

/* horizontal stacked bars; rows = { label, parts: [{label, v, c}], end? } */
function hStacked(elId, rows, opts = {}) {
  const P = palette();
  const el = document.getElementById(elId);
  el.innerHTML = '';
  const seen = [];
  rows.forEach(r => r.parts.forEach(p => {
    if (!seen.some(s => s.label === p.label)) seen.push({ label: p.label, c: p.c });
  }));
  htmlLegend(el, seen, P);
  const W = el.clientWidth || 700;
  const narrow = W < 520;
  const m = narrow
    ? { top: 4, right: 12, bottom: 26, left: 4 }
    : { top: 4, right: 70, bottom: 26, left: opts.left ?? 180 };
  const barH = opts.barH ?? 26, gap = 10;
  const labelH = narrow ? 17 : 0;
  const rowStep = barH + gap + labelH;
  const H = m.top + m.bottom + rows.length * rowStep;
  const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', W).attr('height', H);

  const maxV = opts.max ?? d3.max(rows, r => d3.sum(r.parts, p => p.v));
  const x = d3.scaleLinear().domain([0, maxV]).range([m.left, W - m.right]);

  svg.append('g').selectAll('line').data(x.ticks(5)).join('line')
    .attr('x1', d => x(d)).attr('x2', d => x(d))
    .attr('y1', m.top).attr('y2', H - m.bottom).attr('stroke', P.grid);
  svg.append('g').selectAll('text').data(x.ticks(5)).join('text')
    .attr('x', d => x(d)).attr('y', H - 8).attr('text-anchor', 'middle')
    .attr('fill', P.muted).attr('font-size', '11px')
    .text(opts.tickFmt ?? (d => d.toLocaleString()));

  rows.forEach((r, i) => {
    const y = m.top + i * rowStep + labelH;
    let acc = 0;
    const total = d3.sum(r.parts, p => p.v);
    r.parts.forEach(p => {
      if (!p.v) return;
      const [fill] = fillFor(p.c ?? 'dim', P);
      svg.append('rect')
        .attr('x', x(acc)).attr('y', y)
        .attr('width', Math.max(1, x(acc + p.v) - x(acc))).attr('height', barH)
        .attr('rx', 2).attr('fill', fill)
        .on('mousemove', ev => showTip(ev, `<strong>${r.label}</strong><br>${p.label}: <strong>${(opts.valFmt ?? fmtN)(p.v)}</strong> · ${Math.round(p.v/total*100)}% of total`))
        .on('mouseleave', hideTip);
      acc += p.v;
    });
    if (narrow) {
      svg.append('text')
        .attr('x', m.left).attr('y', y - 5)
        .attr('fill', P.text).attr('font-size', '11px').text(r.label);
      svg.append('text')
        .attr('x', W - m.right).attr('y', y - 5).attr('text-anchor', 'end')
        .attr('fill', P.strong).attr('font-size', '11px').attr('font-weight', 600)
        .text(r.end ?? (opts.valFmt ?? fmtN)(total));
    } else {
      svg.append('text')
        .attr('x', m.left - 10).attr('y', y + barH/2 + 4).attr('text-anchor', 'end')
        .attr('fill', P.text).attr('font-size', '12px').text(r.label);
      svg.append('text')
        .attr('x', x(acc) + 8).attr('y', y + barH/2 + 4)
        .attr('fill', P.strong).attr('font-size', '12px').attr('font-weight', 600)
        .text(r.end ?? (opts.valFmt ?? fmtN)(total));
    }
  });
}

/* survey-style HTML legend, prepended inside the chart container */
function htmlLegend(el, series, P) {
  const lgd = document.createElement('div');
  lgd.className = 'chart-legend';
  lgd.innerHTML = series.map(s => {
    const [fill, stroke] = fillFor(s.c, P);
    return `<span class="legend-item"><span class="legend-swatch" style="background:${s.type === 'line' ? stroke : fill}"></span>${s.label}</span>`;
  }).join('');
  el.appendChild(lgd);
}

/* grouped vertical bars + optional line overlay */
function vGrouped(elId, cats, series, opts = {}) {
  const P = palette();
  const el = document.getElementById(elId);
  el.innerHTML = '';
  htmlLegend(el, series, P);
  const W = el.clientWidth || 420;
  /* narrow screens: rotate category labels so adjacent ones can't collide */
  const narrow = W < 520;
  const H = (opts.h ?? 220) + (narrow ? 30 : 0);
  const m = { top: 8, right: 12, bottom: (opts.bottom ?? 28) + (narrow ? 30 : 0), left: 48 };
  const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', W).attr('height', H);

  const bars = series.filter(s => s.type !== 'line');
  const maxV = opts.max ?? d3.max(series.flatMap(s => s.data));
  const x0 = d3.scaleBand().domain(cats).range([m.left, W - m.right]).paddingInner(0.25).paddingOuter(0.1);
  const x1 = d3.scaleBand().domain(bars.map((_, i) => i)).range([0, x0.bandwidth()]).padding(0.12);
  const y = d3.scaleLinear().domain([0, maxV * 1.05]).range([H - m.bottom, m.top]);

  svg.append('g').selectAll('line').data(y.ticks(5)).join('line')
    .attr('x1', m.left).attr('x2', W - m.right)
    .attr('y1', d => y(d)).attr('y2', d => y(d)).attr('stroke', P.grid);
  svg.append('g').selectAll('text').data(y.ticks(5)).join('text')
    .attr('x', m.left - 8).attr('y', d => y(d) + 4).attr('text-anchor', 'end')
    .attr('fill', P.muted).attr('font-size', '10px').text(opts.tickFmt ?? (d => d));

  bars.forEach((s, si) => {
    const [fill, stroke] = fillFor(s.c, P);
    cats.forEach((c, ci) => {
      svg.append('rect')
        .attr('x', x0(c) + x1(si)).attr('y', y(s.data[ci]))
        .attr('width', x1.bandwidth()).attr('height', Math.max(1, y(0) - y(s.data[ci])))
        .attr('rx', 3).attr('fill', fill)
        .on('mousemove', ev => showTip(ev, `<strong>${String(c).replace(/\n/g,' ')}</strong><br>${s.label}: <strong>${(opts.valFmt ?? fmtN)(s.data[ci])}</strong>`))
        .on('mouseleave', hideTip);
    });
  });

  series.filter(s => s.type === 'line').forEach(s => {
    const [, stroke] = fillFor(s.c, P);
    const line = d3.line()
      .x((d, i) => x0(cats[i]) + x0.bandwidth()/2)
      .y(d => y(d));
    svg.append('path').attr('d', line(s.data))
      .attr('fill', 'none').attr('stroke', stroke).attr('stroke-width', 2);
    s.data.forEach((d, i) => {
      svg.append('circle')
        .attr('cx', x0(cats[i]) + x0.bandwidth()/2).attr('cy', y(d)).attr('r', 4.5)
        .attr('fill', stroke)
        .on('mousemove', ev => showTip(ev, `<strong>${String(cats[i]).replace(/\n/g,' ')}</strong><br>${s.label}: <strong>${(opts.valFmt ?? fmtN)(d)}</strong>`))
        .on('mouseleave', hideTip);
    });
  });

  if (narrow) {
    svg.append('g').selectAll('text').data(cats).join('text')
      .attr('x', c => x0(c) + x0.bandwidth()/2).attr('y', H - m.bottom + 14)
      .attr('text-anchor', 'end').attr('fill', P.muted).attr('font-size', '10px')
      .attr('transform', c => `rotate(-32 ${x0(c) + x0.bandwidth()/2} ${H - m.bottom + 14})`)
      .text(c => String(c).replace(/\n/g, ' '));
  } else {
    svg.append('g').selectAll('text').data(cats).join('text')
      .attr('x', c => x0(c) + x0.bandwidth()/2).attr('y', H - m.bottom + 16)
      .attr('text-anchor', 'middle').attr('fill', P.muted).attr('font-size', '10px')
      .each(function(c) {
        const lines = String(c).split('\n');
        d3.select(this).text(null);
        lines.forEach((l, i) => d3.select(this).append('tspan')
          .attr('x', x0(c) + x0.bandwidth()/2).attr('dy', i ? 12 : 0).text(l));
      });
  }
}

/* multi-series line chart; opts.tipFmt(label, seriesLabel, value) */
function lineChart(elId, labels, series, opts = {}) {
  const P = palette();
  const el = document.getElementById(elId);
  el.innerHTML = '';
  htmlLegend(el, series, P);
  const W = el.clientWidth || 420, H = opts.h ?? 210;
  const m = { top: 8, right: 14, bottom: 30, left: 40 };
  const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', W).attr('height', H);

  const x = d3.scalePoint().domain(labels).range([m.left, W - m.right]).padding(0.3);
  const y = d3.scaleLinear().domain([0, opts.max ?? 100]).range([H - m.bottom, m.top]);
  const yFmt = opts.yFmt ?? (d => d + '%');
  const tipFmt = opts.tipFmt ?? ((l, sl, v) => `<strong>${l}</strong><br>${sl}: <strong>${v}</strong>`);

  svg.append('g').selectAll('line').data(y.ticks(5)).join('line')
    .attr('x1', m.left).attr('x2', W - m.right)
    .attr('y1', d => y(d)).attr('y2', d => y(d)).attr('stroke', P.grid);
  svg.append('g').selectAll('text').data(y.ticks(5)).join('text')
    .attr('x', m.left - 8).attr('y', d => y(d) + 4).attr('text-anchor', 'end')
    .attr('fill', P.muted).attr('font-size', '10px').text(yFmt);
  const xt = opts.xEvery ?? 1;
  svg.append('g').selectAll('text').data(labels.filter((_, i) => i % xt === 0)).join('text')
    .attr('x', l => x(l)).attr('y', H - 10).attr('text-anchor', 'middle')
    .attr('fill', P.muted).attr('font-size', '9.5px').text(l => opts.xFmt ? opts.xFmt(l) : l);

  series.forEach(s => {
    const [fill, stroke] = fillFor(s.c, P);
    const line = d3.line().x((d, i) => x(labels[i])).y(d => y(d)).curve(d3.curveMonotoneX);
    if (!opts.noArea && !s.noArea) {
      const area = d3.area().x((d, i) => x(labels[i])).y0(y(0)).y1(d => y(d)).curve(d3.curveMonotoneX);
      svg.append('path').attr('d', area(s.data)).attr('fill', fill);
    }
    svg.append('path').attr('d', line(s.data)).attr('fill', 'none').attr('stroke', stroke).attr('stroke-width', 2.5);
    s.data.forEach((d, i) => {
      svg.append('circle').attr('cx', x(labels[i])).attr('cy', y(d)).attr('r', opts.dotR ?? 4).attr('fill', stroke)
        .on('mousemove', ev => showTip(ev, tipFmt(labels[i], s.label, d)))
        .on('mouseleave', hideTip);
    });
  });
}

/* donut; opts.tipFmt(row) */
function donut(elId, rows, opts = {}) {
  const P = palette();
  const el = document.getElementById(elId);
  el.innerHTML = '';
  htmlLegend(el, rows.map(r => ({ label: r.label, c: r.c })), P);
  const W = el.clientWidth || 420, H = opts.h ?? 200;
  const R = Math.min(W, H) / 2 - 8;
  const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', W).attr('height', H);
  const g = svg.append('g').attr('transform', `translate(${W/2}, ${H/2})`);

  const pie = d3.pie().value(d => d.v).sort(null)(rows);
  const arc = d3.arc().innerRadius(R * 0.62).outerRadius(R);
  const tipFmt = opts.tipFmt ?? (r => `<strong>${r.label}</strong><br><strong>${r.v}%</strong>`);

  pie.forEach(p => {
    const [fill] = fillFor(p.data.c, P);
    g.append('path').attr('d', arc(p))
      .attr('fill', fill)
      .on('mousemove', ev => showTip(ev, tipFmt(p.data)))
      .on('mouseleave', hideTip);
  });
}
