import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, CLAMP, EASE_IN_OUT, EASE_OUT, INTER, ML } from "../brand";
import { Background, Eyebrow, Footer, Header } from "../components/Chrome";
import { CompareBars, SameScaleLakes } from "../components/Kit";
import { kmToPx } from "../geo/geo";

/**
 * Scene 7 (episode 23.30 s → 28.60 s, 159 frames).
 * VO: "So Lake Volta must hold more water, right? … Not quite."
 * Both lakes on one equal-area scale; area bars use the exact published values (8,502 / 5,580).
 */
const K = 11800;

export const AreaQuestion: React.FC = () => {
  const frame = useCurrentFrame();
  const vIn = interpolate(frame, [0, 22], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const kIn = interpolate(frame, [8, 30], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const bars = interpolate(frame, [20, 56], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const q1 = interpolate(frame, [4, 20], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const q2 = interpolate(frame, [30, 46], [0, 1], { ...CLAMP, easing: EASE_OUT });
  // "Not quite." lands at episode 27.16 s = local frame 116
  const strike = interpolate(frame, [112, 122], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const notQuite = interpolate(frame, [116, 128], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const barPx = kmToPx(50, K);

  return (
    <AbsoluteFill style={{ fontFamily: INTER }}>
      <Background />
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        <SameScaleLakes k={K} vx={310} kx={765} y={980} vo={vIn} ko={kIn} vs={0.92 + 0.08 * vIn} ks={0.92 + 0.08 * kIn} />
        <text x={310} y={1385} fill={C.amber} fontSize={34} fontWeight={800} textAnchor="middle" opacity={vIn}>LAKE VOLTA</text>
        <text x={765} y={1385} fill={C.teal} fontSize={34} fontWeight={800} textAnchor="middle" opacity={kIn}>LAKE KARIBA</text>
        <g opacity={vIn}>
          <line x1={MRX - barPx} y1={612} x2={MRX} y2={612} stroke={C.ivory} strokeWidth={4} />
          <line x1={MRX - barPx} y1={600} x2={MRX - barPx} y2={624} stroke={C.ivory} strokeWidth={4} />
          <line x1={MRX} y1={600} x2={MRX} y2={624} stroke={C.ivory} strokeWidth={4} />
          <text x={MRX - barPx - 16} y={622} fill={C.muted} fontSize={24} fontWeight={700} textAnchor="end">50 KM · SAME SCALE</text>
        </g>
        <text x={ML} y={1452} fill={C.muted} fontSize={27} fontWeight={600} opacity={bars}>SURFACE AREA</text>
        <CompareBars
          x={ML}
          y={1520}
          width={600}
          max={8502}
          p={bars}
          gap={84}
          rows={[
            { name: "VOLTA", value: 8502, label: "8,500 KM²", color: C.amber },
            { name: "KARIBA", value: 5580, label: "5,600 KM²", color: C.teal },
          ]}
        />
      </svg>
      <Header />
      <Eyebrow>SAME SCALE · SURFACE AREA</Eyebrow>
      <div style={{ position: "absolute", left: ML, top: 340, fontSize: 72, fontWeight: 900, color: C.ivory, letterSpacing: -1, lineHeight: 1.08 }}>
        <div style={{ opacity: q1, translate: `0px ${(1 - q1) * 20}px` }}>MORE AREA</div>
        <div style={{ opacity: q2 * (1 - 0.55 * strike), translate: `0px ${(1 - q2) * 20}px`, position: "relative", display: "inline-block" }}>
          = MORE WATER?
          <div style={{ position: "absolute", left: 0, top: "52%", height: 8, width: `${strike * 100}%`, background: C.amber }} />
        </div>
      </div>
      <div style={{ position: "absolute", left: ML, top: 520, fontSize: 56, fontWeight: 900, color: C.amber, opacity: notQuite, translate: `0px ${(1 - notQuite) * 18}px` }}>
        NOT QUITE.
      </div>
      <Footer source="AREA: VRA, ZRA / WORLD LAKE DATABASE · MAPS: NATURAL EARTH, © OSM" />
    </AbsoluteFill>
  );
};

const MRX = 993;
