import React from "react";
import { useSceneFrame } from "../timewarp";
import { AbsoluteFill, interpolate, spring, useVideoConfig } from "remotion";
import { C, CLAMP, EASE_IN_OUT, EASE_OUT, INTER, ML } from "../brand";
import { Background, Eyebrow, Footer, Header } from "../components/Chrome";
import { LAKES, makeProjection, pathOf } from "../geo/geo";

/**
 * PROOF 2 — Polytank multiplication (provisional timing).
 * VO: "At full capacity, Lake Volta can hold about one hundred and forty-eight cubic kilometres of water.
 *      To put that into perspective, imagine those big five-thousand-litre Polytanks you see around Ghana.
 *      You'd need almost thirty billion of them to hold that much water."
 * Maths: 148 km³ = 148 × 10^12 L; ÷ 5,000 L = 29.6 × 10^9 tanks. Every grid count shown is exact.
 * The tank is an original generic drawing (no logo or trade dress).
 */

const CX = 540;
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// --- Generic 5,000 L vertical water tank, original vector drawing (front view). Box: 300 x 420.
const HeroTank: React.FC<{ fill: number }> = ({ fill }) => (
  <g>
    <defs>
      <linearGradient id="tankBody" x1="0" x2="1">
        <stop offset="0" stopColor="#07090C" />
        <stop offset="0.28" stopColor="#2B343F" />
        <stop offset="0.42" stopColor="#3A4552" />
        <stop offset="0.6" stopColor="#161C23" />
        <stop offset="1" stopColor="#050608" />
      </linearGradient>
      <linearGradient id="tankTop" x1="0" x2="1">
        <stop offset="0" stopColor="#0B0E12" />
        <stop offset="0.4" stopColor="#36414D" />
        <stop offset="1" stopColor="#090B0E" />
      </linearGradient>
      <clipPath id="tankInside">
        <path d="M-142 -128 L142 -128 L142 188 Q142 206 0 210 Q-142 206 -142 188 Z" />
      </clipPath>
    </defs>
    <ellipse cx={0} cy={214} rx={170} ry={16} fill="#000" opacity={0.45} />
    {/* body */}
    <path d="M-150 -120 Q-150 -170 -112 -186 Q-60 -206 0 -208 Q60 -206 112 -186 Q150 -170 150 -120 L150 190 Q150 212 0 216 Q-150 212 -150 190 Z" fill="url(#tankBody)" />
    {/* water seen through a cut-away gauge strip */}
    <g clipPath="url(#tankInside)">
      <rect x={-34} y={-128} width={68} height={338} fill="#0B1118" />
      <rect x={-34} y={lerp(210, -110, fill)} width={68} height={338} fill={C.amber} opacity={0.95} />
    </g>
    <rect x={-34} y={-128} width={68} height={338} fill="none" stroke="#56636F" strokeWidth={3} rx={4} />
    {/* moulded ribs */}
    {[-70, -10, 50, 110, 166].map((y) => (
      <g key={y}>
        <path d={`M-150 ${y} Q0 ${y + 20} 150 ${y}`} fill="none" stroke="#000" strokeOpacity={0.6} strokeWidth={9} />
        <path d={`M-150 ${y + 7} Q0 ${y + 27} 150 ${y + 7}`} fill="none" stroke="#6A7784" strokeOpacity={0.35} strokeWidth={2.5} />
      </g>
    ))}
    {/* shoulder + lid */}
    <path d="M-150 -120 Q0 -96 150 -120" fill="none" stroke="#6A7784" strokeOpacity={0.45} strokeWidth={3} />
    <rect x={-58} y={-236} width={116} height={36} rx={9} fill="url(#tankTop)" stroke="#4D5965" strokeWidth={2.5} />
    {[-40, -20, 0, 20, 40].map((x) => (
      <line key={x} x1={x} y1={-232} x2={x} y2={-204} stroke="#000" strokeOpacity={0.45} strokeWidth={3} />
    ))}
    {/* outlet + tap */}
    <rect x={148} y={168} width={40} height={18} rx={4} fill="#1A2028" />
    <rect x={180} y={160} width={12} height={34} rx={3} fill="#8C9AA6" />
    {/* rim light */}
    <path d="M-118 -150 L-118 196" stroke={C.ivory} strokeOpacity={0.08} strokeWidth={16} strokeLinecap="round" />
  </g>
);

// Small icon: same silhouette, flat ivory (so it reads at 20-60 px)
const TankIcon: React.FC<{ x: number; y: number; s: number; o?: number }> = ({ x, y, s, o = 1 }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`} opacity={o}>
    <path d="M-15 -14 Q-15 -20 0 -21 Q15 -20 15 -14 L15 19 Q15 21 0 21.5 Q-15 21 -15 19 Z" fill={C.ivory} />
    <rect x={-6} y={-25} width={12} height={5} rx={1.5} fill={C.ivory} />
    <path d="M-15 -2 Q0 1 15 -2 M-15 9 Q0 12 15 9" stroke={C.bgTop} strokeOpacity={0.55} strokeWidth={1.6} fill="none" />
  </g>
);

const Counter: React.FC<{ big: string; unit: string; sub: string; o: number }> = ({ big, unit, sub, o }) => (
  <div style={{ position: "absolute", left: ML - 6, top: 336, opacity: o }}>
    <div style={{ fontSize: 190, fontWeight: 800, color: C.amber, letterSpacing: -7, lineHeight: 1, fontVariantNumeric: "tabular-nums" }}>{big}</div>
    <div style={{ fontSize: 52, fontWeight: 800, color: C.ivory, marginTop: 6 }}>{unit}</div>
    <div style={{ fontSize: 27, fontWeight: 600, color: C.muted, marginTop: 8 }}>{sub}</div>
  </div>
);

// Grid of N cells (cols x rows), revealed in reading order by progress p (0..1)
const IconGrid: React.FC<{ cols: number; rows: number; cell: number; cx: number; cy: number; p: number; s: number; tile?: boolean }> = ({ cols, rows, cell, cx, cy, p, s, tile }) => {
  const n = cols * rows;
  const shown = p * n;
  const x0 = cx - (cols * cell) / 2 + cell / 2;
  const y0 = cy - (rows * cell) / 2 + cell / 2;
  return (
    <g>
      {Array.from({ length: n }).map((_, i) => {
        const v = Math.max(0, Math.min(1, shown - i));
        if (v <= 0) return null;
        const x = x0 + (i % cols) * cell;
        const y = y0 + Math.floor(i / cols) * cell;
        return tile ? (
          <rect key={i} x={x - cell * 0.42} y={y - cell * 0.42} width={cell * 0.84} height={cell * 0.84} rx={cell * 0.12} fill={C.amber} opacity={v} />
        ) : (
          <TankIcon key={i} x={x} y={y} s={s * (0.6 + 0.4 * v)} o={v} />
        );
      })}
    </g>
  );
};

export const PolytankScale: React.FC = () => {
  const frame = useSceneFrame();
  const { fps } = useVideoConfig();

  // Lake silhouette (accurate shape) as the starting point
  const proj = makeProjection([-0.62, 7.72], 13500, CX, 1130);
  const lakePath = pathOf(proj)(LAKES.volta as never) ?? "";
  const lakeOn = interpolate(frame, [0, 24, 104, 124], [0, 1, 1, 0], { ...CLAMP, easing: EASE_OUT });
  const capCount = Math.round(interpolate(frame, [6, 54], [0, 148], { ...CLAMP, easing: EASE_OUT }));
  const litresOn = interpolate(frame, [62, 80], [0, 1], { ...CLAMP, easing: EASE_OUT });

  // Hero tank
  const tankIn = spring({ frame: frame - 116, fps, config: { damping: 200 } });
  const tankFill = interpolate(frame, [134, 176], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const tankShrink = interpolate(frame, [186, 206], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const heroScale = lerp(1.25, 72 / 430, tankShrink) * (0.9 + 0.1 * tankIn);
  const heroY = lerp(1150, 1150 - 4.5 * 80, tankShrink);
  const heroX = lerp(CX, CX - 4.5 * 80, tankShrink);

  // Grids: 10 -> 100 -> 1,000 tanks
  const g10 = interpolate(frame, [204, 224], [0.1, 1], CLAMP);
  const g100 = interpolate(frame, [226, 252], [0.1, 1], CLAMP);
  const shrink100 = interpolate(frame, [256, 272], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const g1000 = interpolate(frame, [272, 296], [0.1, 1], CLAMP);

  // Nested units: 1,000 tanks -> tile; tile x1,000 = 1 million; x1,000 = 1 billion
  const collapse1 = interpolate(frame, [302, 316], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const m1 = interpolate(frame, [318, 336], [0, 1], CLAMP);
  const collapse2 = interpolate(frame, [340, 352], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const b1 = interpolate(frame, [354, 370], [0, 1], CLAMP);
  const collapse3 = interpolate(frame, [374, 386], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const finalP = interpolate(frame, [392, 440], [1, 29.6], { ...CLAMP, easing: EASE_OUT }); // starts at the 1 billion already shown

  // Counter state
  let big = String(capCount);
  let unit = "KM³ OF WATER";
  let sub = "LAKE VOLTA · AT FULL CAPACITY";
  if (frame >= 116) {
    const n = frame < 204 ? 1 : frame < 226 ? Math.max(1, Math.round(g10 * 10)) : frame < 272 ? Math.max(10, Math.round(g100 * 100)) : Math.max(100, Math.round(g1000 * 1000));
    big = n.toLocaleString("en-GB");
    unit = n === 1 ? "TANK" : "TANKS";
    sub = `5,000 LITRES EACH = ${(n * 5000).toLocaleString("en-GB")} L`;
  }
  if (frame >= 316) {
    big = "1";
    unit = frame < 352 ? "MILLION TANKS" : "BILLION TANKS";
    sub = frame < 352 ? "= 5 BILLION LITRES" : "= 5 TRILLION LITRES · STILL NOT ENOUGH";
  }
  if (frame >= 388) {
    big = finalP.toFixed(1);
    unit = "BILLION TANKS";
    sub = "148 TRILLION L ÷ 5,000 L = 29.6 BILLION";
  }
  const counterO = interpolate(frame, [0, 10], [0, 1], CLAMP) * (frame >= 108 && frame < 122 ? interpolate(frame, [108, 114, 116, 122], [1, 0, 0, 1], CLAMP) : 1);

  return (
    <AbsoluteFill style={{ fontFamily: INTER }}>
      <Background />
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        {/* Lake silhouette */}
        <path d={lakePath} fill={C.amber} opacity={lakeOn} />

        {/* Hero tank → becomes first grid cell */}
        {frame >= 112 && frame < 272 ? (
          <g transform={`translate(${heroX} ${heroY}) scale(${heroScale})`} opacity={tankIn * (frame < 226 ? 1 : 0)}>
            {tankShrink < 0.98 ? <HeroTank fill={tankFill} /> : null}
          </g>
        ) : null}
        {frame >= 112 && frame < 206 ? (
          <g opacity={tankIn * Math.max(0, 1 - tankShrink * 4)}>
            <line x1={CX + 230} y1={930} x2={CX + 300} y2={880} stroke={C.amber} strokeWidth={3} />
            <text x={CX + 310} y={880} fill={C.amber} fontSize={40} fontWeight={800}>
              5,000 L
            </text>
          </g>
        ) : null}

        {/* 10 then 100 tanks (10 x 10, cell 80) */}
        {frame >= 204 && frame < 274 ? (
          <g transform={`translate(${CX} 1150) scale(${lerp(1, 0.24, shrink100)}) translate(${-CX} -1150)`}>
            <IconGrid cols={10} rows={frame < 226 ? 1 : 10} cell={80} cx={CX} cy={frame < 226 ? 1150 - 4.5 * 80 : 1150} p={frame < 226 ? g10 : g100} s={1.5} />
          </g>
        ) : null}

        {/* 1,000 tanks = 10 blocks of 100 */}
        {frame >= 272 && frame < 318 ? (
          <g transform={`translate(${CX} 1150) scale(${lerp(1, 0.12, collapse1)}) translate(${-CX} -1150)`} opacity={1 - collapse1 * 0.2}>
            {Array.from({ length: 10 }).map((_, b) => {
              const v = Math.max(0, Math.min(1, g1000 * 10 - b));
              const bx = CX + ((b % 5) - 2) * 182;
              const by = 1150 + (Math.floor(b / 5) - 0.5) * 205;
              return v > 0 ? (
                <g key={b} transform={`translate(${bx} ${by}) scale(0.22) translate(${-CX} -1150)`} opacity={v}>
                  <IconGrid cols={10} rows={10} cell={80} cx={CX} cy={1150} p={1} s={1.5} />
                </g>
              ) : null;
            })}
          </g>
        ) : null}

        {/* nested tiles: 1,000 tiles = 1 million tanks; 1,000 = 1 billion */}
        {frame >= 316 && frame < 388 ? (
          <g>
            {(() => {
              const p = frame < 352 ? m1 : b1;
              const c = frame < 352 ? collapse2 : collapse3;
              return (
                <g transform={`translate(${CX} 1150) scale(${lerp(1, 0.04, c)}) translate(${-CX} -1150)`}>
                  <IconGrid cols={40} rows={25} cell={21} cx={CX} cy={1150} p={Math.max(0.001, p)} s={1} tile />
                </g>
              );
            })()}
            <text x={ML} y={1500} fill={C.muted} fontSize={28} fontWeight={700} letterSpacing={0.5}>
              {frame < 352 ? "EACH SQUARE = 1,000 TANKS" : "EACH SQUARE = 1 MILLION TANKS"}
            </text>
          </g>
        ) : null}

        {/* 29.6 one-billion blocks */}
        {frame >= 386 ? (
          <g>
            {Array.from({ length: 30 }).map((_, i) => {
              const v = Math.max(0, Math.min(1, finalP - i));
              const col = i % 6;
              const row = Math.floor(i / 6);
              const size = 128;
              const x = CX - 3 * 146 + col * 146 + 9;
              const y = 830 + row * 146;
              return (
                <g key={i}>
                  <rect x={x} y={y} width={size} height={size} rx={14} fill="none" stroke={C.track} strokeWidth={3} />
                  {v > 0 ? <rect x={x} y={y} width={size * (i === 29 ? Math.min(v, 0.6) / 0.6 * 0.6 : v)} height={size} rx={14} fill={C.amber} opacity={0.35 + 0.65 * Math.min(1, v * 2)} /> : null}
                </g>
              );
            })}
            <text x={ML} y={1580} fill={C.muted} fontSize={28} fontWeight={700} letterSpacing={0.5}>
              EACH BLOCK = 1 BILLION TANKS
            </text>
          </g>
        ) : null}
      </svg>

      <Header />
      <Eyebrow>{frame < 112 ? "MEASURE 2 · STORAGE CAPACITY" : "TO PUT THAT IN PERSPECTIVE"}</Eyebrow>
      <Counter big={big} unit={unit} sub={sub} o={counterO} />
      <div style={{ position: "absolute", left: ML, top: 700, fontSize: 64, fontWeight: 900, color: C.ivory, opacity: litresOn * interpolate(frame, [104, 116], [1, 0], CLAMP), letterSpacing: -0.5 }}>
        = 148 TRILLION LITRES.
      </div>
      <Footer source="CAPACITY: VRA / WORLD LAKE DATABASE · GENERIC 5,000 L TANK" />
    </AbsoluteFill>
  );
};
