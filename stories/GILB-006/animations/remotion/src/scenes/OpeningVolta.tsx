import React, { useMemo } from "react";
import { useSceneFrame } from "../timewarp";
import { AbsoluteFill, interpolate } from "remotion";
import { C, CLAMP, EASE_IN_OUT, EASE_OUT, INTER, ML } from "../brand";
import { Background, Eyebrow, Footer, Header } from "../components/Chrome";
import { AFRICA, LAKES, META, REGION, RIVERS, kmToPx, lineString, makeProjection, pathOf } from "../geo/geo";

/**
 * PROOF 1 — Geographic opening (provisional timing; re-time to mastered narration).
 * VO: "Ghana is home to the world's largest man-made lake. / But there's something about that record
 *      you might not know. / Lake Volta is the largest by surface area. / It covers about eight
 *      thousand five hundred square kilometres."
 * Camera = genuine re-projection of real geography (equal-area), not an image zoom.
 */

// Camera keys: [frame, centre lon, centre lat, k(px/rad), screenY]
const AF = { c: [17, 3] as [number, number], k: 900, y: 1090 };
const GH = { c: [-1.0, 7.95] as [number, number], k: 8600, y: 1190 };
const LK = { c: [-0.62, 7.72] as [number, number], k: 19800, y: 1110 };

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const camAt = (f: number) => {
  const t1 = interpolate(f, [52, 140], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const t2 = interpolate(f, [236, 300], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const from = t2 > 0 ? GH : AF;
  const to = t2 > 0 ? LK : GH;
  const t = t2 > 0 ? t2 : t1;
  // Zoom on a log scale; pan in proportion to 1/k so the destination stays steady on screen
  // (avoids the off-screen swing of naive centre interpolation).
  const k = Math.exp(lerp(Math.log(from.k), Math.log(to.k), t));
  const u = (1 / k - 1 / from.k) / (1 / to.k - 1 / from.k);
  return {
    c: [lerp(from.c[0], to.c[0], u), lerp(from.c[1], to.c[1], u)] as [number, number],
    k,
    y: lerp(from.y, to.y, u),
  };
};

const NEIGHBOURS: Record<string, { label: string; at: [number, number] }> = {
  Togo: { label: "TOGO", at: [1.02, 8.9] },
  "Ivory Coast": { label: "CÔTE D'IVOIRE", at: [-3.75, 6.35] },
};

const RIVER_LABELS: { name: string; at: [number, number] }[] = [
  { name: "BLACK VOLTA", at: [-1.5, 8.5] },
  { name: "WHITE VOLTA", at: [-0.12, 8.86] },
  { name: "OTI", at: [0.46, 8.25] },
];

export const OpeningVolta: React.FC = () => {
  const frame = useSceneFrame();
  const cam = camAt(frame);
  const proj = makeProjection(cam.c, cam.k, 540, cam.y);
  const path = pathOf(proj);

  const dam = proj(META.dams.akosombo) ?? [0, 0];

  // --- reveals
  const africaDraw = interpolate(frame, [0, 46], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const ghanaOn = interpolate(frame, [30, 60], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const neighboursOn = interpolate(frame, [120, 150, 236, 262], [0, 1, 1, 0], CLAMP);
  const riverDraw = interpolate(frame, [138, 196], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const floodKm = interpolate(frame, [168, 252], [0, 360], { ...CLAMP, easing: Easing2 });
  const floodPx = kmToPx(floodKm, cam.k);
  const damOn = interpolate(frame, [196, 214], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const riverLabelsOn = interpolate(frame, [270, 284, 300, 310], [0, 1, 1, 0], CLAMP);
  const contextDim = interpolate(frame, [240, 300], [1, 0.35], CLAMP);

  // --- headline (house grammar)
  const words = ["THE", "WORLD'S", "LARGEST", "MAN-MADE", "LAKE."];
  const wordIn = (i: number) => interpolate(frame, [10 + i * 7, 22 + i * 7], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const asterisk = interpolate(frame, [104, 116], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const qualifier = interpolate(frame, [212, 230], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const headlineOut = interpolate(frame, [292, 306], [1, 0], CLAMP);

  // --- measurement (1,000 km² squares at true projected scale)
  const sqPx = kmToPx(Math.sqrt(1000), cam.k);
  const measureOn = interpolate(frame, [300, 312], [0, 1], CLAMP);
  const firstSq = interpolate(frame, [306, 326], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const slide = interpolate(frame, [334, 352], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const nSquares = interpolate(frame, [352, 400], [1, 8.5], { ...CLAMP, easing: EASE_OUT });
  const counter = Math.round(interpolate(frame, [352, 400], [1000, 8500], { ...CLAMP, easing: EASE_OUT }) / 10) * 10;

  const lakeCentre = proj([-0.45, 7.75]) ?? [540, 1100];
  const blockX = ML + 4;
  const blockY = 1170;

  const africaPaths = useMemo(() => AFRICA.map((c) => c.name), []);

  return (
    <AbsoluteFill style={{ fontFamily: INTER }}>
      <Background />
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <clipPath id="flood">
            <circle cx={dam[0]} cy={dam[1]} r={Math.max(0.01, floodPx)} />
          </clipPath>
        </defs>

        {/* Africa context */}
        <g opacity={contextDim}>
          {AFRICA.map((c, i) =>
            c.name === "Ghana" ? null : (
              <path
                key={africaPaths[i]}
                d={path(c.geometry as never) ?? ""}
                fill={C.land}
                fillOpacity={africaDraw}
                stroke={C.landEdge}
                strokeWidth={1.6}
                pathLength={1}
                strokeDasharray={1}
                strokeDashoffset={1 - africaDraw}
              />
            ),
          )}
        </g>
        {/* higher-detail neighbours + Ghana once zoomed in */}
        <g opacity={interpolate(frame, [70, 110], [0, 1], CLAMP) * contextDim}>
          {REGION.filter((r) => r.name !== "Ghana").map((r) => (
            <path key={r.name} d={path(r.geometry as never) ?? ""} fill={C.land} stroke={C.landEdge} strokeWidth={2} />
          ))}
        </g>
        {REGION.filter((r) => r.name === "Ghana").map((r) => (
          <path
            key="gh"
            d={path(r.geometry as never) ?? ""}
            fill="#16304A"
            fillOpacity={ghanaOn}
            stroke={C.ivory}
            strokeOpacity={0.25 + 0.5 * ghanaOn * (frame > 240 ? contextDim : 1)}
            strokeWidth={interpolate(frame, [0, 140], [1.5, 3], CLAMP)}
          />
        ))}

        {/* Volta river system (Natural Earth centerlines) */}
        <g opacity={interpolate(frame, [290, 320], [1, 0.55], CLAMP)}>
          {RIVERS.filter((r) => r.featurecla === "River").flatMap((r, i) =>
            r.lines.map((l, j) => (
              <path
                key={`${i}-${j}`}
                d={path(lineString(l) as never) ?? ""}
                fill="none"
                stroke={C.river}
                strokeWidth={3}
                strokeLinecap="round"
                pathLength={1}
                strokeDasharray={1}
                strokeDashoffset={1 - riverDraw}
              />
            )),
          )}
        </g>

        {/* Lake Volta floods from Akosombo northward */}
        <g clipPath="url(#flood)">
          <path d={path(LAKES.volta as never) ?? ""} fill={C.amber} />
        </g>
        {/* shoreline crisp edge once full */}
        <path d={path(LAKES.volta as never) ?? ""} fill="none" stroke="#F2C877" strokeWidth={1.4} opacity={interpolate(frame, [246, 262], [0, 0.9], CLAMP)} />

        {/* Dam marker */}
        <g opacity={damOn * (1 - measureOn)}>
          <circle cx={dam[0]} cy={dam[1]} r={9} fill={C.ivory} />
          <circle cx={dam[0]} cy={dam[1]} r={9 + 18 * damOn} fill="none" stroke={C.ivory} strokeOpacity={0.5 * (1 - damOn)} strokeWidth={2} />
          <line x1={dam[0] + (dam[0] > 760 ? -14 : 14)} y1={dam[1]} x2={dam[0] + (dam[0] > 760 ? -70 : 70)} y2={dam[1]} stroke={C.ivory} strokeWidth={2} />
          <text x={dam[0] + (dam[0] > 760 ? -80 : 80)} y={dam[1] + 10} fill={C.ivory} fontSize={28} fontWeight={700} letterSpacing={1} textAnchor={dam[0] > 760 ? "end" : "start"}>
            AKOSOMBO DAM
          </text>
        </g>

        {/* Neighbour labels */}
        <g opacity={neighboursOn}>
          {Object.entries(NEIGHBOURS).map(([k, v]) => {
            const p = proj(v.at);
            return p ? (
              <text key={k} x={p[0]} y={p[1]} fill={C.muted} fontSize={26} fontWeight={600} letterSpacing={3} textAnchor="middle">
                {v.label}
              </text>
            ) : null;
          })}
          {(() => {
            const p = proj([-1.75, 7.35]);
            return p ? (
              <text x={p[0]} y={p[1]} fill={C.ivory} fontSize={40} fontWeight={800} letterSpacing={8} textAnchor="middle">
                GHANA
              </text>
            ) : null;
          })()}
        </g>

        {/* River labels */}
        <g opacity={riverLabelsOn}>
          {RIVER_LABELS.map((r) => {
            const p = proj(r.at);
            return p ? (
              <text key={r.name} x={p[0]} y={p[1]} fill={C.river} fontSize={26} fontWeight={700} letterSpacing={2} textAnchor="middle">
                {r.name}
              </text>
            ) : null;
          })}
        </g>

        {/* Measurement: 1,000 km² squares at true scale (equal-area projection) */}
        <g opacity={measureOn}>
          {Array.from({ length: 9 }).map((_, i) => {
            const vis = interpolate(nSquares - i, [0, 1], [0, 1], CLAMP);
            const partial = i === 8 ? 0.5 : 1; // 8.5 squares = 8,500 km²
            if (i === 0) {
              const sx = lerp(lakeCentre[0] - sqPx / 2, blockX, slide);
              const sy = lerp(lakeCentre[1] - sqPx / 2, blockY, slide);
              return (
                <rect key={i} x={sx} y={sy} width={sqPx} height={sqPx} fill={C.ivory} fillOpacity={0.9 * firstSq} stroke={C.bgTop} strokeWidth={3} />
              );
            }
            const col = i % 3;
            const row = Math.floor(i / 3);
            return (
              <rect
                key={i}
                x={blockX + col * sqPx}
                y={blockY + row * sqPx}
                width={sqPx * partial * vis}
                height={sqPx}
                fill={C.ivory}
                fillOpacity={0.9}
                stroke={C.bgTop}
                strokeWidth={3}
              />
            );
          })}
          <text x={blockX} y={blockY + 3 * sqPx + 44} fill={C.muted} fontSize={26} fontWeight={600} letterSpacing={0.5} opacity={slide}>
            <tspan x={blockX}>EACH SQUARE = 1,000 KM²</tspan>
            <tspan x={blockX} dy={34}>SAME SCALE AS MAP</tspan>
          </text>
          {(() => {
            const lx = lerp(lakeCentre[0] + sqPx / 2 + 16, blockX + sqPx + 16, slide);
            const ly = lerp(lakeCentre[1] + 10, blockY + sqPx / 2 + 10, slide);
            return (
              <text x={lx} y={ly} fill={C.ivory} fontSize={28} fontWeight={800} opacity={firstSq * (1 - slide)}>
                1,000 KM²
              </text>
            );
          })()}
        </g>
      </svg>

      {/* keeps map linework from running under the headline */}
      <AbsoluteFill style={{ background: `linear-gradient(180deg, ${C.bgTop} 0%, ${C.bgTop} 300px, rgba(8,19,31,0.92) 520px, rgba(8,19,31,0) 700px)`, opacity: interpolate(frame, [40, 90], [0, 1], CLAMP) }} />
      <Header />

      {/* Headline */}
      <div style={{ position: "absolute", left: ML, top: 330, width: 900, opacity: headlineOut }}>
        <div style={{ fontSize: 84, fontWeight: 900, lineHeight: 1.06, color: C.ivory, letterSpacing: -1 }}>
          {words.map((w, i) => (
            <span key={w} style={{ display: "inline-block", marginRight: 22, opacity: wordIn(i), translate: `0px ${(1 - wordIn(i)) * 24}px` }}>
              {w}
              {w === "LARGEST" ? (
                <span style={{ color: C.amber, display: "inline-block", opacity: asterisk, scale: `${interpolate(asterisk, [0, 1], [2.2, 1])}` }}>*</span>
              ) : null}
            </span>
          ))}
        </div>
        <div style={{ marginTop: 18, fontSize: 40, fontWeight: 800, color: C.amber, opacity: qualifier, translate: `0px ${(1 - qualifier) * 16}px` }}>
          *BY SURFACE AREA.
        </div>
      </div>

      {/* Measurement number */}
      <div style={{ position: "absolute", left: ML - 6, top: 270, opacity: measureOn }}>
        <div style={{ fontSize: 230, fontWeight: 800, color: C.amber, letterSpacing: -8, lineHeight: 1, fontVariantNumeric: "tabular-nums" }}>
          {counter.toLocaleString("en-GB")}
        </div>
        <div style={{ fontSize: 52, fontWeight: 800, color: C.ivory, marginTop: 6 }}>KM² OF SURFACE AREA</div>
        <div style={{ fontSize: 27, fontWeight: 600, color: C.muted, marginTop: 8 }}>LAKE VOLTA · LARGEST RESERVOIR BY AREA</div>
      </div>

      <Eyebrow opacity={interpolate(frame, [0, 12, 290, 300], [1, 1, 1, 0], CLAMP)}>{frame < 236 ? "GHANA" : "LAKE VOLTA"}</Eyebrow>
      <Footer source={frame > 300 ? "AREA: VRA / WORLD LAKE DATABASE · OUTLINE: NATURAL EARTH" : "MAP: NATURAL EARTH"} />
    </AbsoluteFill>
  );
};

// Flood easing: fast through the main channel, slower as the water creeps up the valley arms.
function Easing2(t: number) {
  return 1 - Math.pow(1 - t, 2.2);
}
// fps currently unused but kept for timing conversions when narration is locked
export const OPENING_DURATION = 14;
