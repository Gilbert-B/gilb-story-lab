import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, CLAMP, EASE_IN_OUT, EASE_OUT, INTER, ML } from "../brand";
import { Background, Eyebrow, Footer, Header } from "../components/Chrome";
import { CamKey, flight } from "../components/Kit";
import { AFRICA, LAKES, REGION, makeProjection, pathOf } from "../geo/geo";

/**
 * Scenes 16–17 (episode 105.67 s → 115.40 s, 292 frames; the outro cross-fades over the last 14).
 * VO: "So the next time you hear that Ghana has the world's largest man-made lake,
 *      there's one question worth asking. / Largest by what?"
 * Callback to the opening headline; words land on the narration (world's 108.14 s, largest 108.62 s, …).
 */
const GH: CamKey = { c: [-1.0, 7.95], k: 8600, y: 1190 };
const GH2: CamKey = { c: [-1.0, 7.95], k: 7600, y: 1230 };

// local frames of each headline word (episode s × 30 − 3170)
const WORD_AT = [62, 74, 89, 104, 119];

export const Callback: React.FC = () => {
  const frame = useCurrentFrame();
  const cam = flight(GH, GH2, interpolate(frame, [0, 210], [0, 1], { ...CLAMP, easing: EASE_IN_OUT })); // slow genuine pull-back
  const proj = makeProjection(cam.c, cam.k, 540, cam.y);
  const path = pathOf(proj);
  const mapIn = interpolate(frame, [0, 18], [0, 1], CLAMP);
  const words = ["THE", "WORLD'S", "LARGEST", "MAN-MADE", "LAKE."];
  const wordIn = (i: number) => interpolate(frame, [WORD_AT[i] - 6, WORD_AT[i] + 6], [0, 1], { ...CLAMP, easing: EASE_OUT });
  // "one question worth asking" 110.74 s = local 152
  const asterisk = interpolate(frame, [150, 162], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const pulse = 1 + 0.12 * Math.max(0, Math.sin(((frame - 162) / 18) * Math.PI)) * (frame > 162 && frame < 216 ? 1 : 0);
  // "Largest by what?" 112.92 s = local 218
  const out1 = interpolate(frame, [204, 216], [1, 0], { ...CLAMP, easing: EASE_IN_OUT });
  const big1 = interpolate(frame, [212, 224], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const big2 = interpolate(frame, [224, 236], [0, 1], { ...CLAMP, easing: EASE_OUT });

  return (
    <AbsoluteFill style={{ fontFamily: INTER }}>
      <Background />
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, opacity: mapIn * (0.35 + 0.65 * out1) }}>
        <g opacity={0.35}>
          {AFRICA.map((c) => (
            <path key={c.name} d={path(c.geometry as never) ?? ""} fill={C.land} stroke={C.landEdge} strokeWidth={1.6} />
          ))}
          {REGION.filter((r) => r.name !== "Ghana").map((r) => (
            <path key={r.name} d={path(r.geometry as never) ?? ""} fill={C.land} stroke={C.landEdge} strokeWidth={2} />
          ))}
        </g>
        {REGION.filter((r) => r.name === "Ghana").map((r) => (
          <path key="gh" d={path(r.geometry as never) ?? ""} fill="#16304A" stroke={C.ivory} strokeOpacity={0.6} strokeWidth={3} />
        ))}
        <path d={path(LAKES.volta as never) ?? ""} fill={C.amber} />
      </svg>
      <AbsoluteFill style={{ background: `linear-gradient(180deg, ${C.bgTop} 0%, ${C.bgTop} 300px, rgba(8,19,31,0.92) 560px, rgba(8,19,31,0) 740px)` }} />
      <Header />
      <Eyebrow opacity={out1}>NEXT TIME YOU HEAR…</Eyebrow>
      <div style={{ position: "absolute", left: ML, top: 330, width: 900, opacity: out1 }}>
        <div style={{ fontSize: 84, fontWeight: 900, lineHeight: 1.06, color: C.ivory, letterSpacing: -1 }}>
          {words.map((w, i) => (
            <span key={w} style={{ display: "inline-block", marginRight: 22, opacity: wordIn(i), translate: `0px ${(1 - wordIn(i)) * 24}px` }}>
              {w}
              {w === "LARGEST" ? <span style={{ color: C.amber, display: "inline-block", opacity: asterisk, scale: `${interpolate(asterisk, [0, 1], [2.2, 1]) * pulse}` }}>*</span> : null}
            </span>
          ))}
        </div>
      </div>
      {/* Largest by what? */}
      <div style={{ position: "absolute", left: ML - 6, top: 720, lineHeight: 0.95, letterSpacing: -6, whiteSpace: "nowrap" }}>
        <div style={{ fontSize: 166, fontWeight: 900, color: C.ivory, opacity: big1, translate: `0px ${(1 - big1) * 30}px` }}>LARGEST</div>
        <div style={{ fontSize: 166, fontWeight: 900, color: C.amber, opacity: big2, translate: `0px ${(1 - big2) * 30}px` }}>BY WHAT?</div>
      </div>
      <Footer source={frame < 204 ? "MAP: NATURAL EARTH" : undefined} />
    </AbsoluteFill>
  );
};
