import { useEffect, useMemo, useRef, useState } from 'react';
import { day, fullDay } from '../format.js';

function niceTicks(max, count = 4) {
  if (!(max > 0)) return [0, 1];
  const raw = max / count;
  const mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw);
  const ticks = [];
  for (let v = 0; v <= max + step * 0.999; v += step) ticks.push(v);
  return ticks;
}

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

/**
 * Multi-series line chart on one shared axis.
 * series: [{ name, color, values }] aligned to `dates`; `markers`: [{ date, label }].
 */
export default function LineChart({ dates, series, format, height = 280, markers = [], ariaLabel }) {
  const [ref, width] = useWidth();
  const [hover, setHover] = useState(null);
  const labelEnds = series.length >= 2 && series.length <= 4 && width > 520;
  const m = { top: 12, right: labelEnds ? 128 : 14, bottom: 26, left: 46 };
  const w = width - m.left - m.right;
  const h = height - m.top - m.bottom;

  const { ticks, x, y } = useMemo(() => {
    const max = Math.max(0, ...series.flatMap((s) => s.values.filter((v) => v !== null)));
    const t = niceTicks(max);
    const top = t.at(-1);
    return {
      ticks: t,
      x: (i) => (dates.length > 1 ? (i / (dates.length - 1)) * w : w / 2),
      y: (v) => h - (v / top) * h,
    };
  }, [dates, series, w, h]);

  if (!dates.length) return <div className="skeleton">Not enough history yet.</div>;

  const path = (values) => {
    let d = '';
    let pen = false;
    values.forEach((v, i) => {
      if (v === null || v === undefined) {
        pen = false;
        return;
      }
      d += `${pen ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`;
      pen = true;
    });
    return d;
  };

  const xTickCount = Math.min(dates.length, width < 480 ? 3 : 6);
  const xTicks = Array.from({ length: xTickCount }, (_, k) => Math.round((k * (dates.length - 1)) / Math.max(1, xTickCount - 1)));

  // End labels, nudged apart so they never overlap.
  const ends = labelEnds
    ? series
        .map((s) => ({ s, y: y(s.values.at(-1) ?? 0) }))
        .sort((a, b) => a.y - b.y)
        .map((e, i, arr) => {
          if (i > 0 && e.y - arr[i - 1].y < 15) e.y = arr[i - 1].y + 15;
          return e;
        })
    : [];

  const onMove = (e) => {
    const box = e.currentTarget.getBoundingClientRect();
    const px = ((e.clientX - box.left) / box.width) * width - m.left;
    const i = Math.max(0, Math.min(dates.length - 1, Math.round((px / w) * (dates.length - 1))));
    setHover({ i, left: ((m.left + x(i)) / width) * box.width, flip: x(i) > w * 0.6 });
  };

  const hovered = hover && series.map((s) => ({ ...s, v: s.values[hover.i] })).filter((s) => s.v !== null && s.v !== undefined).sort((a, b) => b.v - a.v);

  return (
    <div className="viz" ref={ref}>
      {series.length >= 2 && (
        <div className="legend">
          {series.map((s) => (
            <span key={s.name}><i style={{ background: s.color }} />{s.name}</span>
          ))}
        </div>
      )}
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={ariaLabel} onMouseMove={onMove} onMouseLeave={() => setHover(null)}>
        <g transform={`translate(${m.left},${m.top})`}>
          {ticks.map((t) => (
            <g key={t}>
              <line className="gridline" x1="0" x2={w} y1={y(t)} y2={y(t)} />
              <text className="axis" x="-8" y={y(t)} dy="0.32em" textAnchor="end">{format(t)}</text>
            </g>
          ))}
          {xTicks.map((i, k) => (
            <text key={i} className="axis" x={x(i)} y={h + 18} textAnchor={k === 0 ? 'start' : k === xTicks.length - 1 ? 'end' : 'middle'}>{day(dates[i])}</text>
          ))}
          {markers.map((mk) => {
            const i = dates.indexOf(mk.date);
            return i < 0 ? null : (
              <g key={mk.date}>
                <line x1={x(i)} x2={x(i)} y1="0" y2={h} stroke="var(--text-tertiary)" strokeDasharray="3 4" />
                <text className="axis" x={x(i) + 5} y="10">{mk.label}</text>
              </g>
            );
          })}
          {series.map((s) => (
            <path key={s.name} d={path(s.values)} fill="none" stroke={s.color} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
          ))}
          {ends.map((e) => (
            <text key={e.s.name} className="endlabel" x={w + 8} y={e.y} dy="0.32em">{e.s.name.length > 17 ? `${e.s.name.slice(0, 16)}…` : e.s.name}</text>
          ))}
          {hover && (
            <g>
              <line x1={x(hover.i)} x2={x(hover.i)} y1="0" y2={h} stroke="var(--text-tertiary)" strokeWidth="1" />
              {hovered.map((s) => (
                <circle key={s.name} cx={x(hover.i)} cy={y(s.v)} r="4.5" fill={s.color} stroke="var(--surface-1)" strokeWidth="2" />
              ))}
            </g>
          )}
        </g>
      </svg>
      {hover && (
        <div className="tooltip" style={{ top: 34, left: hover.flip ? undefined : hover.left + 12, right: hover.flip ? `calc(100% - ${hover.left - 12}px)` : undefined }}>
          <div className="t">{fullDay(dates[hover.i])}</div>
          {hovered.slice(0, 10).map((s) => (
            <div className="r" key={s.name}><span><i style={{ background: s.color }} />{s.name}</span><b>{format(s.v)}</b></div>
          ))}
        </div>
      )}
    </div>
  );
}
