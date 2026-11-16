import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, CLAMP, EASE_IN_OUT, EASE_OUT, INTER, ML } from "../brand";
import { Background, Eyebrow, Footer, Header } from "../components/Chrome";
import { BigCounter, CamKey, flight, lerp } from "../components/Kit";
import { AFRICA, LAKES, META, REGION, kmToPx, makeProjection, pathOf } from "../geo/geo";

/**
 * Scenes 5–6 (episode 14.33 s → 23.30 s, 269 frames).
 * VO: "Now, look at Lake Kariba, between Zambia and Zimbabwe. It covers a smaller area —
 *      about five thousand six hundred square kilometres."
 * Camera flies by genuine re-projection from the Lake Volta view to Lake Kariba and lands at the SAME
 * scale (k) as the Volta measurement in scene 4, so the 1,000 km² squares are directly comparable.
 * Published area 5,580 km² (ZRA / World Lake Database); narration rounds to 5,600.
 */

const VOLTA: CamKey = { c: [-0.62, 7.72], k: 19800, y: 1110 }; // = end camera of the opening scene
const MID: CamKey = { c: [13, -4.5], k: 1250, y: 1010 };
const KAR: CamKey = { c: [28.05, -17.2], k: 19800, y: 1040 };

const camAt = (f: number): CamKey => {
  const t1 = interpolate(f, [0, 46], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const t2 = interpolate(f, [42, 100], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  return f < 44 ? flight(VOLTA, MID, t1) : flight(MID, KAR, t2);
};

export const KaribaIntro: React.FC = () => {
  const frame = useCurrentFrame();
  const cam = camAt(frame);
  const proj = makeProjection(cam.c, cam.k, 540, cam.y);
  const path = pathOf(proj);
  const dam = proj(META.dams.kariba) ?? [0, 0];

  const africaOp = interpolate(Math.log(cam.k), [Math.log(2500), Math.log(9000)], [1, 0.3], CLAMP);
  const regionOp = interpolate(Math.log(cam.k), [Math.log(2000), Math.log(7000)], [0, 1], CLAMP);
  const floodKm = interpolate(frame, [64, 118], [0, 300], { ...CLAMP, easing: (t) => 1 - Math.pow(1 - t, 2.2) });
  const damOn = interpolate(frame, [96, 110], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const labelsOn = interpolate(frame, [70, 92, 112, 124], [0, 1, 1, 0], CLAMP);
  const headline = interpolate(frame, [18, 34, 106, 116], [0, 1, 1, 0], { ...CLAMP, easing: EASE_OUT });
  const sub = interpolate(frame, [40, 56, 106, 116], [0, 1, 1, 0], { ...CLAMP, easing: EASE_OUT });

  // measurement — identical method and scale to the Lake Volta squares
  const sqPx = kmToPx(Math.sqrt(1000), KAR.k);
  const measureOn = interpolate(frame, [114, 126], [0, 1], CLAMP);
  const firstSq = interpolate(frame, [120, 138], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const slide = interpolate(frame, [142, 160], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const nSquares = interpolate(frame, [160, 196], [1, 5.6], { ...CLAMP, easing: EASE_OUT });
  const counter = Math.round(interpolate(frame, [160, 196], [1000, 5600], { ...CLAMP, easing: EASE_OUT }) / 10) * 10;
  const lakeCentre = proj([27.95, -17.05]) ?? [540, 1040];
  const blockX = ML + 4;
  const blockY = 1395;

  return (
    <AbsoluteFill style={{ fontFamily: INTER }}>
      <Background />
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <clipPath id="karFlood">
            <circle cx={dam[0]} cy={dam[1]} r={Math.max(0.01, kmToPx(floodKm, cam.k))} />
          </clipPath>
        </defs>
        <g opacity={africaOp}>
          {AFRICA.map((c) => (
            <path key={c.name} d={path(c.geometry as never) ?? ""} fill={C.land} stroke={C.landEdge} strokeWidth={1.6} />
          ))}
        </g>
        <g opacity={regionOp}>
          {REGION.map((r) => (
            <path
              key={r.name}
              d={path(r.geometry as never) ?? ""}
              fill={r.name === "Zambia" || r.name === "Zimbabwe" ? "#132A40" : C.land}
              stroke={r.name === "Zambia" || r.name === "Zimbabwe" ? C.ivory : C.landEdge}
              strokeOpacity={r.name === "Zambia" || r.name === "Zimbabwe" ? 0.45 : 1}
              strokeWidth={2}
            />
          ))}
        </g>
        {/* Lake Volta stays on the map as the plane leaves */}
        <path d={path(LAKES.volta as never) ?? ""} fill={C.amber} />
        {/* Lake Kariba floods from Kariba Dam (north-east end) */}
        <g clipPath="url(#karFlood)">
          <path d={path(LAKES.kariba as never) ?? ""} fill={C.teal} fillRule="evenodd" />
        </g>

        <g opacity={labelsOn}>
          {(
            [
              ["ZAMBIA", [27.35, -16.45]],
              ["ZIMBABWE", [28.35, -17.95]],
            ] as [string, [number, number]][]
          ).map(([n, at]) => {
            const p = proj(at);
            return p ? (
              <text key={n} x={p[0]} y={p[1]} fill={C.ivory} fontSize={36} fontWeight={800} letterSpacing={7} textAnchor="middle">
                {n}
              </text>
            ) : null;
          })}
        </g>
        <g opacity={damOn * (1 - measureOn)}>
          <circle cx={dam[0]} cy={dam[1]} r={9} fill={C.ivory} />
          <line x1={dam[0] - 14} y1={dam[1]} x2={dam[0] - 70} y2={dam[1]} stroke={C.ivory} strokeWidth={2} />
          <text x={dam[0] - 80} y={dam[1] + 10} fill={C.ivory} fontSize={28} fontWeight={700} letterSpacing={1} textAnchor="end">
            KARIBA DAM
          </text>
        </g>

        {/* 1,000 km² squares at the same projected scale as Lake Volta's */}
        <g opacity={measureOn}>
          {Array.from({ length: 6 }).map((_, i) => {
            const vis = interpolate(nSquares - i, [0, 1], [0, 1], CLAMP);
            const partial = i === 5 ? 0.6 : 1; // 5.6 squares = 5,600 km²
            if (i === 0) {
              const sx = lerp(lakeCentre[0] - sqPx / 2, blockX, slide);
              const sy = lerp(lakeCentre[1] - sqPx / 2, blockY, slide);
              return <rect key={i} x={sx} y={sy} width={sqPx} height={sqPx} fill={C.ivory} fillOpacity={0.9 * firstSq} stroke={C.bgTop} strokeWidth={3} />;
            }
            return (
              <rect
                key={i}
                x={blockX + (i % 3) * sqPx}
                y={blockY + Math.floor(i / 3) * sqPx}
                width={sqPx * partial * vis}
                height={sqPx}
                fill={C.ivory}
                fillOpacity={0.9}
                stroke={C.bgTop}
                strokeWidth={3}
              />
            );
          })}
          <text x={blockX} y={blockY + 2 * sqPx + 44} fill={C.muted} fontSize={26} fontWeight={600} letterSpacing={0.5} opacity={slide}>
            <tspan x={blockX}>EACH SQUARE = 1,000 KM²</tspan>
            <tspan x={blockX} dy={34}>SAME SCALE AS LAKE VOLTA</tspan>
          </text>
          <text
            x={lerp(lakeCentre[0] + sqPx / 2 + 16, blockX + sqPx + 16, slide)}
            y={lerp(lakeCentre[1] + 10, blockY + sqPx / 2 + 10, slide)}
            fill={C.ivory}
            fontSize={28}
            fontWeight={800}
            opacity={firstSq * (1 - slide)}
          >
            1,000 KM²
          </text>
        </g>
      </svg>

      <AbsoluteFill style={{ background: `linear-gradient(180deg, ${C.bgTop} 0%, ${C.bgTop} 300px, rgba(8,19,31,0.9) 560px, rgba(8,19,31,0) 720px)` }} />
      <Header />
      <Eyebrow opacity={1 - measureOn}>NOW, LOOK AT</Eyebrow>
      <div style={{ position: "absolute", left: ML, top: 330, opacity: headline, translate: `0px ${(1 - headline) * 24}px` }}>
        <div style={{ fontSize: 84, fontWeight: 900, color: C.ivory, letterSpacing: -1, lineHeight: 1.06 }}>LAKE KARIBA.</div>
      </div>
      <div style={{ position: "absolute", left: ML, top: 440, opacity: sub, fontSize: 40, fontWeight: 800, color: C.teal }}>BETWEEN ZAMBIA AND ZIMBABWE</div>
      <BigCounter top={270} value={counter.toLocaleString("en-GB")} unit="KM² OF SURFACE AREA" sub="LAKE KARIBA · SMALLER THAN LAKE VOLTA" color={C.teal} o={measureOn} />
      <Footer source={frame > 114 ? "AREA: ZRA / WORLD LAKE DATABASE (5,580 KM²) · OUTLINE: © OSM" : "MAP: NATURAL EARTH · © OPENSTREETMAP CONTRIBUTORS"} />
    </AbsoluteFill>
  );
};
