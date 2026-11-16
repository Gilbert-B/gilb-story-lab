import React from "react";
import { useSceneFrame } from "../timewarp";
import { AbsoluteFill, interpolate } from "remotion";
import { C, CLAMP, EASE_IN_OUT, EASE_OUT, INTER, ML, MR } from "../brand";
import { Background, Eyebrow, Footer, Header } from "../components/Chrome";
import { LAKES, RIVERS, kmToPx, lineString, makeProjection, pathOf } from "../geo/geo";

/**
 * PROOF 3 — Area vs depth (scenes 12–14; provisional timing).
 * VO: "How is that possible? Think of two containers. One is very wide, but relatively shallow. The other is
 *      narrower, but much deeper. The wider container covers more surface area. But the deeper one can hold
 *      more water. And that's essentially what's happening with these two lakes. Lake Volta spreads across a
 *      vast network of flooded river valleys. Lake Kariba fills a deeper basin. On average, it's about one
 *      and a half times as deep."
 *
 * Containers are an ILLUSTRATION (footprint ratio exaggerated to 2.4 for legibility), but their volumes
 * are drawn in the published 148 : 181 capacity proportion, so the equal-rate fill is honest.
 * The real-lake depth gauges show PUBLISHED MEAN DEPTHS (18.8 m, 29.2 m) and are not surveyed profiles.
 */

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const COS = Math.cos(Math.PI / 6);
const SIN = 0.5;

// iso point (x right-back, y left-back, z up) -> screen
const iso = (ox: number, oy: number, x: number, y: number, z: number): [number, number] => [ox + (x - y) * COS, oy + (x + y) * SIN - z];
const pts = (a: [number, number][]) => a.map((p) => p.join(",")).join(" ");

// Container dims (units = px at scale 1)
// Illustration: footprint ratio exaggerated to 2.4 for clarity; heights chosen so the two
// volumes stay in the published 148 : 181 capacity proportion (the fill bars are honest).
const FOOT = 2.4;
const S1 = 292; // wide footprint side
const S2 = S1 / Math.sqrt(FOOT); // narrow footprint side
const H1 = 72; // shallow
const H2 = H1 * (181 / 148) * FOOT; // deep -> V2 / V1 = 181 / 148

type BoxProps = { ox: number; oy: number; s: number; h: number; level: number; col: string; draw: number; dim: number; surfaceGlow: number };

const Box: React.FC<BoxProps> = ({ ox, oy, s, h, level, col, draw, dim, surfaceGlow }) => {
  const wz = h * level;
  const P = (x: number, y: number, z: number) => iso(ox, oy, x, y, z);
  // water volume faces (front two + top)
  const waterLeft = pts([P(0, s, 0), P(s, s, 0), P(s, s, wz), P(0, s, wz)]);
  const waterRight = pts([P(s, 0, 0), P(s, s, 0), P(s, s, wz), P(s, 0, wz)]);
  const waterTop = pts([P(0, 0, wz), P(s, 0, wz), P(s, s, wz), P(0, s, wz)]);
  const edges: [number, number, number, number, number, number][] = [
    [0, 0, 0, s, 0, 0], [s, 0, 0, s, s, 0], [s, s, 0, 0, s, 0], [0, s, 0, 0, 0, 0],
    [0, 0, h, s, 0, h], [s, 0, h, s, s, h], [s, s, h, 0, s, h], [0, s, h, 0, 0, h],
    [0, 0, 0, 0, 0, h], [s, 0, 0, s, 0, h], [s, s, 0, s, s, h], [0, s, 0, 0, s, h],
  ];
  return (
    <g opacity={dim}>
      {/* back glass faces */}
      <polygon points={pts([P(0, 0, 0), P(s, 0, 0), P(s, 0, h), P(0, 0, h)])} fill={C.ivory} fillOpacity={0.03 * draw} />
      <polygon points={pts([P(0, 0, 0), P(0, s, 0), P(0, s, h), P(0, 0, h)])} fill={C.ivory} fillOpacity={0.04 * draw} />
      {level > 0.001 ? (
        <g>
          <polygon points={waterLeft} fill={col} fillOpacity={0.78} />
          <polygon points={waterRight} fill={col} fillOpacity={0.6} />
          <polygon points={waterTop} fill={col} />
          <polygon points={waterTop} fill="none" stroke={C.ivory} strokeOpacity={0.35 + 0.65 * surfaceGlow} strokeWidth={2 + 4 * surfaceGlow} />
        </g>
      ) : null}
      {edges.map((e, i) => {
        const a = P(e[0], e[1], e[2]);
        const b = P(e[3], e[4], e[5]);
        const back = i === 0 || i === 3 || i === 8;
        return <line key={i} x1={a[0]} y1={a[1]} x2={lerp(a[0], b[0], draw)} y2={lerp(a[1], b[1], draw)} stroke={C.ivory} strokeOpacity={back ? 0.25 : 0.85} strokeWidth={back ? 2 : 3} strokeDasharray={back ? "8 8" : undefined} strokeLinecap="round" />;
      })}
    </g>
  );
};

const Arrow: React.FC<{ a: [number, number]; b: [number, number]; label: string; o: number; col: string; side?: "left" | "right" | "below" }> = ({ a, b, label, o, col, side = "below" }) => {
  const mx = (a[0] + b[0]) / 2;
  const my = (a[1] + b[1]) / 2;
  const off = side === "left" ? [-18, 10] : side === "right" ? [18, 10] : [0, 46];
  return (
    <g opacity={o}>
      <line x1={a[0]} y1={a[1]} x2={lerp(a[0], b[0], o)} y2={lerp(a[1], b[1], o)} stroke={col} strokeWidth={4} />
      <circle cx={a[0]} cy={a[1]} r={6} fill={col} />
      <circle cx={lerp(a[0], b[0], o)} cy={lerp(a[1], b[1], o)} r={6} fill={col} />
      <text x={mx + off[0]} y={my + off[1]} fill={col} fontSize={34} fontWeight={800} letterSpacing={1} textAnchor={side === "left" ? "end" : side === "right" ? "start" : "middle"}>
        {label}
      </text>
    </g>
  );
};

export const AreaVsDepth: React.FC = () => {
  const frame = useSceneFrame();

  // ---------- Part A: containers ----------
  const sc = 1.0;
  const O1: [number, number] = [ML + S1 * COS * sc - 6, 870]; // wide: back corner
  const O2: [number, number] = [MR - S2 * COS * sc + 4, 700];
  const drawA = interpolate(frame, [18, 80], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const focusWide = interpolate(frame, [105, 120, 190, 205], [0, 1, 1, 0], CLAMP);
  const focusNarrow = interpolate(frame, [195, 210, 280, 295], [0, 1, 1, 0], CLAMP);
  const dimWide = 1 - 0.65 * focusNarrow;
  const dimNarrow = 1 - 0.65 * focusWide;

  // Equal pour rate: volume poured per frame identical for both. Wide (V1) fills in 66 frames.
  const pourStart = 300;
  const T1 = 66;
  const T2 = T1 * (181 / 148);
  const lvl1 = interpolate(frame, [pourStart, pourStart + T1], [0, 1], CLAMP);
  const lvl2 = interpolate(frame, [pourStart, pourStart + T2], [0, 1], CLAMP);
  const pouring1 = frame >= pourStart && lvl1 < 1;
  const pouring2 = frame >= pourStart && lvl2 < 1;
  const surfaceGlow = interpolate(frame, [326, 342], [0, 1], CLAMP);
  const moreWater = interpolate(frame, [386, 400], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const partAOut = interpolate(frame, [440, 470], [1, 0], { ...CLAMP, easing: EASE_IN_OUT });

  // ---------- Part B: real lakes at the same equal-area scale ----------
  const K = 12400;
  const LAKE_Y = 760;
  const pV = makeProjection([-0.69, 7.73], K, 300, LAKE_Y);
  const pK = makeProjection([28.04, -17.22], K, 790, LAKE_Y);
  const lakesIn = interpolate(frame, [458, 500], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const valleys = interpolate(frame, [500, 560], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const basin = interpolate(frame, [560, 590], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const gauges = interpolate(frame, [600, 650], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const ratioOn = interpolate(frame, [660, 676], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const barKm = 50;
  const barPx = kmToPx(barKm, K);

  // depth gauges: 1 m = 13 px (true proportion between the two published means)
  const MPX = 12;
  const surfY = 1210;
  const dV = 18.8 * MPX * gauges;
  const dK = 29.2 * MPX * gauges;

  return (
    <AbsoluteFill style={{ fontFamily: INTER }}>
      <Background />
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        {/* ===== Part A ===== */}
        <g opacity={partAOut}>
          <Box ox={O1[0]} oy={O1[1]} s={S1} h={H1} level={lvl1} col={C.amber} draw={drawA} dim={dimWide} surfaceGlow={surfaceGlow} />
          <Box ox={O2[0]} oy={O2[1]} s={S2} h={H2} level={lvl2} col={C.teal} draw={drawA} dim={dimNarrow} surfaceGlow={0} />
          {/* pour streams (same rate) */}
          {pouring1 ? <rect x={iso(O1[0], O1[1], S1 / 2, S1 / 2, 0)[0] - 5} y={480} width={10} height={iso(O1[0], O1[1], S1 / 2, S1 / 2, H1 * lvl1)[1] - 480} fill={C.amber} opacity={0.9} /> : null}
          {pouring2 ? <rect x={iso(O2[0], O2[1], S2 / 2, S2 / 2, 0)[0] - 5} y={480} width={10} height={iso(O2[0], O2[1], S2 / 2, S2 / 2, H2 * lvl2)[1] - 480} fill={C.teal} opacity={0.9} /> : null}

          {/* dimension callouts */}
          <Arrow a={iso(O1[0], O1[1], 0, S1, 0)} b={iso(O1[0], O1[1], S1, S1, 0)} label="WIDE" o={focusWide} col={C.amber} />
          <Arrow a={iso(O1[0], O1[1], S1, S1, 0)} b={iso(O1[0], O1[1], S1, S1, H1)} label="SHALLOW" o={interpolate(frame, [130, 150, 190, 205], [0, 1, 1, 0], CLAMP)} col={C.amber} side="right" />
          <Arrow a={iso(O2[0], O2[1], 0, S2, 0)} b={iso(O2[0], O2[1], S2, S2, 0)} label="NARROWER" o={focusNarrow} col={C.teal} />
          <Arrow a={iso(O2[0], O2[1], 0, S2, 0)} b={iso(O2[0], O2[1], 0, S2, H2)} label="DEEPER" o={interpolate(frame, [220, 240, 280, 295], [0, 1, 1, 0], CLAMP)} col={C.teal} side="left" />

          {/* outcome labels */}
          <text x={iso(O1[0], O1[1], S1 / 2, S1 / 2, H1)[0]} y={iso(O1[0], O1[1], 0, 0, H1)[1] - 40} fill={C.amber} fontSize={40} fontWeight={900} textAnchor="middle" opacity={surfaceGlow}>
            MORE SURFACE.
          </text>
          <text x={iso(O2[0], O2[1], S2 / 2, S2 / 2, H2)[0]} y={iso(O2[0], O2[1], 0, 0, H2)[1] - 40} fill={C.teal} fontSize={40} fontWeight={900} textAnchor="middle" opacity={moreWater}>
            MORE WATER.
          </text>

          {/* water-held bars: zero-based, same pour rate, true 148:181 */}
          <g opacity={interpolate(frame, [292, 304], [0, 1], CLAMP)}>
            <text x={ML} y={1300} fill={C.muted} fontSize={27} fontWeight={600}>WATER HELD WHEN FULL</text>
            {[
              { y: 1340, v: lvl1 * 148, col: C.amber, name: "WIDE" },
              { y: 1430, v: lvl2 * 181, col: C.teal, name: "DEEP" },
            ].map((b) => (
              <g key={b.name}>
                <text x={ML} y={b.y + 36} fill={C.ivory} fontSize={30} fontWeight={800}>{b.name}</text>
                <rect x={ML + 130} y={b.y} width={760} height={48} rx={9} fill={C.track} />
                <rect x={ML + 130} y={b.y} width={760 * (b.v / 181)} height={48} rx={9} fill={b.col} />
              </g>
            ))}
          </g>
          <text x={MR} y={1250} fill={C.muted} fontSize={26} fontWeight={700} letterSpacing={3} textAnchor="end" opacity={drawA}>
            ILLUSTRATION
          </text>
        </g>

        {/* ===== Part B ===== */}
        <g opacity={lakesIn}>
          {/* rivers feeding Volta (clipped below the header) */}
          <defs>
            <clipPath id="belowHeader">
              <rect x={0} y={450} width={1080} height={700} />
            </clipPath>
          </defs>
          <g clipPath="url(#belowHeader)">
          {RIVERS.filter((r) => r.featurecla === "River").flatMap((r, i) =>
            r.lines.map((l, j) => (
              <path key={`${i}-${j}`} d={pathOf(pV)(lineString(l) as never) ?? ""} fill="none" stroke={C.river} strokeWidth={2.5} opacity={0.5 + 0.5 * valleys} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - valleys} />
            )),
          )}
          </g>
          <path d={pathOf(pV)(LAKES.volta as never) ?? ""} fill={C.amber} />
          {/* valley arms trace */}
          <path d={pathOf(pV)(LAKES.volta as never) ?? ""} fill="none" stroke="#FFE2A6" strokeWidth={3} pathLength={1} strokeDasharray={`${0.22} 1`} strokeDashoffset={-valleys * 1.1} opacity={valleys > 0 && valleys < 1 ? 1 : 0} />
          <path d={pathOf(pK)(LAKES.kariba as never) ?? ""} fill={C.teal} fillRule="evenodd" />
          <text x={300} y={1095} fill={C.amber} fontSize={34} fontWeight={800} textAnchor="middle">LAKE VOLTA</text>
          <text x={790} y={1095} fill={C.teal} fontSize={34} fontWeight={800} textAnchor="middle">LAKE KARIBA</text>
          {/* scale bar */}
          <g transform="translate(0 0)">
            <line x1={ML} y1={410} x2={ML + barPx} y2={410} stroke={C.ivory} strokeWidth={4} />
            <line x1={ML} y1={398} x2={ML} y2={422} stroke={C.ivory} strokeWidth={4} />
            <line x1={ML + barPx} y1={398} x2={ML + barPx} y2={422} stroke={C.ivory} strokeWidth={4} />
            <text x={ML + barPx + 16} y={420} fill={C.muted} fontSize={26} fontWeight={700}>50 KM · SAME SCALE</text>
          </g>
          <text x={300} y={1135} fill={C.ivory} fontSize={27} fontWeight={600} textAnchor="middle" opacity={valleys}>FLOODED RIVER VALLEYS</text>
          <text x={790} y={1135} fill={C.ivory} fontSize={27} fontWeight={600} textAnchor="middle" opacity={basin}>A DEEPER BASIN</text>
        </g>

        {/* published mean-depth gauges */}
        <g opacity={gauges > 0 ? 1 : 0}>
          <line x1={ML} y1={surfY + 40} x2={MR} y2={surfY + 40} stroke={C.ivory} strokeOpacity={0.7} strokeWidth={3} />
          <text x={ML + 90} y={surfY + 22} fill={C.muted} fontSize={24} fontWeight={600}>WATER SURFACE</text>
          <rect x={220} y={surfY + 40} width={160} height={dV} fill={C.amber} />
          <rect x={660} y={surfY + 40} width={160} height={dK} fill={C.teal} />
          {[0, 10, 20, 30].map((m) => (
            <g key={m} opacity={gauges}>
              <line x1={ML + 40} y1={surfY + 40 + m * MPX} x2={ML + 70} y2={surfY + 40 + m * MPX} stroke={C.muted} strokeWidth={2} />
              <text x={ML + 30} y={surfY + 48 + m * MPX} fill={C.muted} fontSize={22} fontWeight={600} textAnchor="end">{m}M</text>
            </g>
          ))}
          <text x={400} y={surfY + 40 + dV - 8} fill={C.amber} fontSize={48} fontWeight={800} opacity={gauges}>18.8 M</text>
          <text x={645} y={surfY + 40 + dK - 8} fill={C.teal} fontSize={48} fontWeight={800} opacity={gauges} textAnchor="end">29.2 M</text>
          <g opacity={ratioOn}>
            <path d={`M ${834} ${surfY + 40 + 18.8 * MPX} h 24 V ${surfY + 40 + 29.2 * MPX} h -24`} fill="none" stroke={C.ivory} strokeWidth={3} />
            <text x={872} y={surfY + 50 + 24 * MPX} fill={C.ivory} fontSize={34} fontWeight={900}>≈1.5×</text>
          </g>
          <text x={ML} y={1658} fill={C.muted} fontSize={22} fontWeight={600} opacity={gauges}>
            PUBLISHED MEAN DEPTHS · NOT SURVEYED LAKE PROFILES
          </text>
        </g>
      </svg>

      <Header />
      <Eyebrow>{frame < 450 ? "SURFACE AREA VS DEPTH" : "BACK TO THE REAL LAKES"}</Eyebrow>
      {/* episode: shown while the narrator asks the question (proof frames 0-10 are stretched by the TimeWarp) */}
      <div style={{ position: "absolute", left: ML, top: 340, fontSize: 64, fontWeight: 900, color: C.ivory, letterSpacing: -0.5, opacity: interpolate(frame, [0, 2, 8, 10], [0, 1, 1, 0], CLAMP) }}>
        HOW IS THAT POSSIBLE?
      </div>
      <div style={{ position: "absolute", left: ML, top: 340, fontSize: 64, fontWeight: 900, color: C.ivory, letterSpacing: -0.5, opacity: interpolate(frame, [10, 26, 96, 110], [0, 1, 1, 0], CLAMP) }}>
        THINK OF TWO CONTAINERS.
      </div>
      <Footer source={frame < 450 ? "ILLUSTRATIVE CONTAINERS · VOLUMES IN 148 : 181 PROPORTION" : "DEPTHS: VRA / ZRA / WLD · MAPS: NATURAL EARTH, © OSM"} />
    </AbsoluteFill>
  );
};
