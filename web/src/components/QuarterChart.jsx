import { useEffect, useRef, useState } from 'react';
import { CATEGORY_COLOR, quarter } from '../format.js';

const KEYS = ['project', 'policy', 'incentive', 'utility'];

function niceMax(v) {
  const mag = 10 ** Math.floor(Math.log10(v || 1));
  return [1, 2, 5, 10].map((m) => m * mag).find((m) => m >= v) || 1;
}

/** Stacked columns: records per quarter, split by category. One axis, counts. */
export default function QuarterChart({ rows, labels }) {
  const ref = useRef(null);
  const [width, setWidth] = useState(720);
  const [hover, setHover] = useState(null);
  useEffect(() => {
    if (!ref.current) return undefined;
    const ro = new ResizeObserver(([e]) => setWidth(Math.max(280, Math.round(e.contentRect.width))));
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, []);
  if (!rows.length) return <div className="skeleton">No activity yet.</div>;

  const height = 260;
  const m = { top: 10, right: 8, bottom: 26, left: 34 };
  const w = width - m.left - m.right;
  const h = height - m.top - m.bottom;
  const max = niceMax(Math.max(...rows.map((r) => KEYS.reduce((s, k) => s + r[k], 0))));
  const band = w / rows.length;
  const bar = Math.min(34, band * 0.7);
  const y = (v) => h - (v / max) * h;
  const every = Math.ceil(rows.length / (width < 520 ? 4 : 8));

  return (
    <div className="viz" ref={ref}>
      <div className="legend">{KEYS.map((k) => <span key={k}><i style={{ background: CATEGORY_COLOR[k] }} />{labels[k]}</span>)}</div>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Siting records per quarter by category">
        <g transform={`translate(${m.left},${m.top})`}>
          {[0, 0.5, 1].map((f) => (
            <g key={f}>
              <line className="gridline" x1="0" x2={w} y1={y(max * f)} y2={y(max * f)} />
              <text className="axis" x="-8" y={y(max * f)} dy="0.32em" textAnchor="end">{Math.round(max * f)}</text>
            </g>
          ))}
          {rows.map((r, i) => {
            const cx = i * band + band / 2;
            let acc = 0;
            return (
              <g key={r.quarter} onMouseEnter={() => setHover({ r, left: ((m.left + cx) / width) * 100, flip: i > rows.length / 2 })} onMouseLeave={() => setHover(null)}>
                <rect x={i * band} y="0" width={band} height={h} fill={hover?.r.quarter === r.quarter ? 'var(--surface-2)' : 'transparent'} />
                {KEYS.map((k) => {
                  if (!r[k]) return null;
                  const top = y(acc + r[k]);
                  const segH = y(acc) - top;
                  acc += r[k];
                  // 2px surface gap between stacked segments.
                  return <rect key={k} x={cx - bar / 2} y={top + 1} width={bar} height={Math.max(1, segH - 2)} rx="2" fill={CATEGORY_COLOR[k]} />;
                })}
                {i % every === 0 && <text className="axis" x={cx} y={h + 18} textAnchor="middle">{quarter(r.quarter)}</text>}
              </g>
            );
          })}
        </g>
      </svg>
      {hover && (
        <div className="tooltip" style={{ top: 40, left: hover.flip ? undefined : `calc(${hover.left}% + 14px)`, right: hover.flip ? `calc(${100 - hover.left}% + 14px)` : undefined }}>
          <div className="t">{quarter(hover.r.quarter)}</div>
          {KEYS.map((k) => <div className="r" key={k}><span><i style={{ background: CATEGORY_COLOR[k] }} />{labels[k]}</span><b>{hover.r[k]}</b></div>)}
          <div className="r" style={{ marginTop: 4 }}><span>of which restrictive</span><b>{hover.r.restrictive}</b></div>
        </div>
      )}
    </div>
  );
}
