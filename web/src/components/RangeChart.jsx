import { useEffect, useRef, useState } from 'react';
import { count, usd, usdFull } from '../format.js';

function useWidth() {
  const ref = useRef(null);
  const [width, setWidth] = useState(720);
  useEffect(() => {
    if (!ref.current) return undefined;
    const ro = new ResizeObserver(([e]) => setWidth(Math.max(280, Math.round(e.contentRect.width))));
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, []);
  return [ref, width];
}

/** Round up to 1, 2 or 5 × a power of ten. */
const niceMax = (v) => {
  const mag = 10 ** Math.floor(Math.log10(v || 1));
  return [1, 2, 5, 10].map((m) => m * mag).find((m) => m >= v);
};

/**
 * One row per cohort: a bar from the 25th to the 75th percentile, a tick at
 * the median, and a thin line from the 10th to the 90th. A single hue: the
 * rows are the same measure, told apart by their labels.
 * rows: [{ key, label, n, p10, p25, median, p75, p90 }]; marker: optional { value, label }.
 */
export default function RangeChart({ rows, marker, ariaLabel }) {
  const [ref, width] = useWidth();
  const [hover, setHover] = useState(null);
  if (!rows.length) return null;
  const narrow = width < 520;
  const m = { top: 24, right: 62, bottom: marker ? 24 : 6, left: narrow ? 118 : 180 };
  const rowH = 34;
  const w = width - m.left - m.right;
  const height = m.top + rows.length * rowH + m.bottom;
  const max = niceMax(Math.max(...rows.map((r) => r.p90 ?? r.p75), marker?.value || 0));
  const x = (v) => (Math.min(v, max) / max) * w;
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((f) => f * max);
  const clip = (s) => (s.length > (narrow ? 16 : 25) ? `${s.slice(0, narrow ? 15 : 24)}…` : s);

  return (
    <div className="viz rangebar" ref={ref}>
      <div className="legend">
        <span><i style={{ background: 'var(--series-1)', width: 22 }} />Middle half of deals (25th–75th percentile)</span>
        <span><i style={{ background: 'var(--text-primary)', width: 3, height: 13, borderRadius: 1 }} />Median</span>
        <span><i style={{ background: 'var(--text-tertiary)', width: 22, height: 2 }} />10th–90th percentile (10+ deals)</span>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={ariaLabel}>
        <g transform={`translate(${m.left},${m.top})`}>
          {ticks.map((t, i) => (
            <g key={t}>
              <line className="gridline" x1={x(t)} x2={x(t)} y1="0" y2={rows.length * rowH} />
              {(!narrow || i % 2 === 0) && <text className="axis" x={x(t)} y="-8" textAnchor="middle">{usd(t)}</text>}
            </g>
          ))}
          {rows.map((r, i) => {
            const cy = i * rowH + rowH / 2;
            return (
              <g key={r.key} onMouseEnter={() => setHover({ r, top: m.top + cy })} onMouseLeave={() => setHover(null)}>
                <rect x={-m.left} y={i * rowH} width={width} height={rowH} fill={hover?.r.key === r.key ? 'var(--surface-2)' : 'transparent'} />
                <text className="endlabel" x="-10" y={cy} dy="0.32em" textAnchor="end">{clip(r.label)}</text>
                {r.p10 !== null && <line x1={x(r.p10)} x2={x(r.p90)} y1={cy} y2={cy} stroke="var(--text-tertiary)" strokeWidth="2" />}
                <rect x={x(r.p25)} y={cy - 8} width={Math.max(3, x(r.p75) - x(r.p25))} height="16" rx="4" fill="var(--series-1)" />
                <rect x={x(r.median) - 1.5} y={cy - 11} width="3" height="22" rx="1" fill="var(--text-primary)" stroke="var(--surface-1)" strokeWidth="1" />
                <text className="axis" x={w + 8} y={cy} dy="0.32em" style={{ fill: 'var(--text-primary)', fontVariantNumeric: 'tabular-nums' }}>{usd(r.median)}</text>
              </g>
            );
          })}
          {marker && (
            <g>
              <line x1={x(marker.value)} x2={x(marker.value)} y1="-4" y2={rows.length * rowH} stroke="var(--series-2)" strokeWidth="2" strokeDasharray="5 4" />
              <text className="axis" x={x(marker.value)} y={rows.length * rowH + 16} textAnchor={x(marker.value) > w * 0.8 ? 'end' : 'start'} dx={x(marker.value) > w * 0.8 ? -6 : 6} style={{ fill: 'var(--text-primary)', fontWeight: 600 }}>{marker.label}</text>
            </g>
          )}
        </g>
      </svg>
      {hover && (
        <div className="tooltip" style={{ top: hover.top + 44, right: 12 }}>
          <div className="t">{hover.r.label} · {count(hover.r.n)} deals</div>
          {[['90th percentile', hover.r.p90], ['75th percentile', hover.r.p75], ['Median', hover.r.median], ['25th percentile', hover.r.p25], ['10th percentile', hover.r.p10]].filter(([, v]) => v !== null).map(([k, v]) => (
            <div className="r" key={k}><span>{k}</span><b>{usdFull(v)}</b></div>
          ))}
        </div>
      )}
    </div>
  );
}
