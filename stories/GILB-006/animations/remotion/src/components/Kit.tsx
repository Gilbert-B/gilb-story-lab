import React from "react";
import { C, ML } from "../brand";
import { LAKES, makeProjection, pathOf } from "../geo/geo";

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const clamp01 = (v: number) => Math.max(0, Math.min(1, v));

/** Camera key for genuine re-projection: centre lon/lat, scale k (px/rad), screen y of centre. */
export type CamKey = { c: [number, number]; k: number; y: number };

/** Zoom on a log scale, pan weighted by 1/k so the destination stays steady (no off-screen swing). */
export const flight = (from: CamKey, to: CamKey, t: number): CamKey => {
  const k = Math.exp(lerp(Math.log(from.k), Math.log(to.k), t));
  const u = Math.abs(1 / to.k - 1 / from.k) < 1e-12 ? t : (1 / k - 1 / from.k) / (1 / to.k - 1 / from.k);
  return { c: [lerp(from.c[0], to.c[0], u), lerp(from.c[1], to.c[1], u)], k, y: lerp(from.y, to.y, u) };
};

/** Big data number + unit + source-style subline (GILB-001 grammar). */
export const BigCounter: React.FC<{ top: number; value: string; unit: string; sub?: string; color: string; o: number; size?: number }> = ({ top, value, unit, sub, color, o, size = 230 }) => (
  <div style={{ position: "absolute", left: ML - 6, top, opacity: o }}>
    <div style={{ fontSize: size, fontWeight: 800, color, letterSpacing: -size / 30, lineHeight: 1, fontVariantNumeric: "tabular-nums" }}>{value}</div>
    <div style={{ fontSize: 52, fontWeight: 800, color: C.ivory, marginTop: 6 }}>{unit}</div>
    {sub ? <div style={{ fontSize: 27, fontWeight: 600, color: C.muted, marginTop: 8 }}>{sub}</div> : null}
  </div>
);

/** Volta centre / Kariba centre for side-by-side equal-area views. */
export const VOLTA_C: [number, number] = [-0.69, 7.73];
export const KARIBA_C: [number, number] = [28.04, -17.22];

/** Both lakes on ONE equal-area scale k (fair size comparison). s = per-lake entrance scale. */
export const SameScaleLakes: React.FC<{ k: number; vx: number; kx: number; y: number; vo?: number; ko?: number; vs?: number; ks?: number }> = ({
  k,
  vx,
  kx,
  y,
  vo = 1,
  ko = 1,
  vs = 1,
  ks = 1,
}) => {
  const pV = makeProjection(VOLTA_C, k, vx, y);
  const pK = makeProjection(KARIBA_C, k, kx, y);
  return (
    <g>
      <g opacity={vo} transform={`translate(${vx} ${y}) scale(${vs}) translate(${-vx} ${-y})`}>
        <path d={pathOf(pV)(LAKES.volta as never) ?? ""} fill={C.amber} />
      </g>
      <g opacity={ko} transform={`translate(${kx} ${y}) scale(${ks}) translate(${-kx} ${-y})`}>
        <path d={pathOf(pK)(LAKES.kariba as never) ?? ""} fill={C.teal} fillRule="evenodd" />
      </g>
    </g>
  );
};

/** Zero-based horizontal comparison bars. Values drawn exactly; labels may be rounded to match narration. */
export const CompareBars: React.FC<{
  x: number;
  y: number;
  width: number;
  max: number;
  rows: { name: string; value: number; label: string; color: string }[];
  p: number;
  gap?: number;
}> = ({ x, y, width, max, rows, p, gap = 92 }) => (
  <g>
    {rows.map((r, i) => {
      const ry = y + i * gap;
      const w = width * (r.value / max) * p;
      return (
        <g key={r.name}>
          <text x={x} y={ry - 12} fill={C.ivory} fontSize={28} fontWeight={800} letterSpacing={0.5}>
            {r.name}
          </text>
          <rect x={x} y={ry} width={width} height={40} rx={8} fill={C.track} />
          <rect x={x} y={ry} width={Math.max(0, w)} height={40} rx={8} fill={r.color} />
          <text x={x + w + 14} y={ry + 31} fill={r.color} fontSize={32} fontWeight={800} opacity={p > 0.6 ? (p - 0.6) / 0.4 : 0}>
            {r.label}
          </text>
        </g>
      );
    })}
  </g>
);
