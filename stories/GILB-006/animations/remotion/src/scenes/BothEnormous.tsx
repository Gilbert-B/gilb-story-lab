import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, CLAMP, EASE_IN_OUT, EASE_OUT, INTER, ML, MR } from "../brand";
import { Background, Eyebrow, Footer, Header } from "../components/Chrome";
import { SameScaleLakes } from "../components/Kit";
import { kmToPx } from "../geo/geo";

/**
 * Scene 15 (episode 100.90 s → 105.67 s, 143 frames).
 * VO: "Both are enormous. They're just enormous in different ways."
 * Same-scale lakes; WIDER / DEEPER tags restate the explained finding (no new claim).
 */
const K = 11800;

export const BothEnormous: React.FC = () => {
  const frame = useCurrentFrame();
  const lakes = interpolate(frame, [0, 24], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const h1 = interpolate(frame, [12, 28], [0, 1], { ...CLAMP, easing: EASE_OUT });
  // "different ways" ≈ 104.08 s = local 95
  const h2 = interpolate(frame, [62, 80], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const tags = interpolate(frame, [80, 104], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const barPx = kmToPx(50, K);
  const drift = interpolate(frame, [0, 143], [0, 1]);

  return (
    <AbsoluteFill style={{ fontFamily: INTER }}>
      <Background />
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        <SameScaleLakes k={K} vx={300 - 6 * drift} kx={775 + 6 * drift} y={1060} vo={lakes} ko={lakes} />
        <text x={300} y={1470} fill={C.amber} fontSize={34} fontWeight={800} textAnchor="middle" opacity={lakes}>LAKE VOLTA</text>
        <text x={775} y={1470} fill={C.teal} fontSize={34} fontWeight={800} textAnchor="middle" opacity={lakes}>LAKE KARIBA</text>
        {/* tags: what makes each enormous */}
        <g opacity={tags}>
          <rect x={300 - 110} y={1500} width={220} height={58} rx={29} fill="none" stroke={C.amber} strokeWidth={3} />
          <text x={300} y={1540} fill={C.amber} fontSize={30} fontWeight={900} textAnchor="middle" letterSpacing={2}>WIDER</text>
          <rect x={775 - 110} y={1500} width={220} height={58} rx={29} fill="none" stroke={C.teal} strokeWidth={3} />
          <text x={775} y={1540} fill={C.teal} fontSize={30} fontWeight={900} textAnchor="middle" letterSpacing={2}>DEEPER</text>
        </g>
        <g opacity={lakes}>
          <line x1={MR - barPx} y1={640} x2={MR} y2={640} stroke={C.ivory} strokeWidth={4} />
          <line x1={MR - barPx} y1={628} x2={MR - barPx} y2={652} stroke={C.ivory} strokeWidth={4} />
          <line x1={MR} y1={628} x2={MR} y2={652} stroke={C.ivory} strokeWidth={4} />
          <text x={MR - barPx - 16} y={650} fill={C.muted} fontSize={24} fontWeight={700} textAnchor="end">50 KM · SAME SCALE</text>
        </g>
      </svg>
      <Header />
      <Eyebrow>TWO RECORDS, TWO MEASURES</Eyebrow>
      <div style={{ position: "absolute", left: ML, top: 340, fontSize: 80, fontWeight: 900, color: C.ivory, letterSpacing: -1, lineHeight: 1.06 }}>
        <div style={{ opacity: h1, translate: `0px ${(1 - h1) * 20}px` }}>BOTH ENORMOUS.</div>
        <div style={{ opacity: h2, translate: `0px ${(1 - h2) * 20}px`, color: C.amber }}>
          IN DIFFERENT <span style={{ color: C.teal }}>WAYS.</span>
        </div>
      </div>
      <Footer source="MAPS: NATURAL EARTH, © OPENSTREETMAP CONTRIBUTORS · EQUAL-AREA PROJECTION" />
    </AbsoluteFill>
  );
};
