import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, CLAMP, EASE_OUT, INTER, ML, MR } from "../brand";
import { Background, Eyebrow, Footer, Header } from "../components/Chrome";
import { KARIBA_C, VOLTA_C } from "../components/Kit";
import { LAKES, makeProjection, pathOf } from "../geo/geo";

/**
 * Scene 14 (episode 90.90 s → 100.90 s, 300 frames). "Takeaway" rows in the GILB-001 grammar.
 * VO: "So Lake Volta holds the record for the largest man-made lake by surface area.
 *      But Lake Kariba has the greater water storage capacity."
 * Kariba's row says GREATER (than Volta), never "largest" — it is not claimed to be the world's largest by volume.
 * Both thumbnails share one equal-area scale.
 */
const KT = 6000;

const Row: React.FC<{ top: number; o: number; label: string; name: string; color: string; stat: string; vs: string; lake: "volta" | "kariba" }> = ({ top, o, label, name, color, stat, vs, lake }) => {
  const cx = MR - 150;
  const cy = top + 205;
  const p = makeProjection(lake === "volta" ? VOLTA_C : KARIBA_C, KT, cx, cy);
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 1920, opacity: o }}>
      <div style={{ position: "absolute", left: ML, top, fontSize: 27, fontWeight: 600, color: C.muted }}>{label}</div>
      <div style={{ position: "absolute", left: ML, top: top + 44, fontSize: 84, fontWeight: 900, color, letterSpacing: -2, lineHeight: 1, translate: `${(1 - o) * -30}px 0px` }}>{name}</div>
      <div style={{ position: "absolute", left: ML, top: top + 160, fontSize: 40, fontWeight: 800, color: C.ivory }}>
        {stat} <span style={{ color: C.muted, fontWeight: 700, fontSize: 32 }}>{vs}</span>
      </div>
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        <path d={pathOf(p)(LAKES[lake] as never) ?? ""} fill={color} fillRule="evenodd" />
      </svg>
      <div style={{ position: "absolute", left: ML, width: MR - ML, top: top + 420, height: 2, background: C.rule }} />
    </div>
  );
};

export const Verdict: React.FC = () => {
  const frame = useCurrentFrame();
  const r1 = interpolate(frame, [8, 30], [0, 1], { ...CLAMP, easing: EASE_OUT });
  // "But Lake Kariba…" starts 97.00 s = local 183
  const r2 = interpolate(frame, [180, 202], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const dim1 = interpolate(frame, [180, 200], [1, 0.55], CLAMP);
  return (
    <AbsoluteFill style={{ fontFamily: INTER }}>
      <Background />
      <Header />
      <Eyebrow>THE VERDICT</Eyebrow>
      <div style={{ opacity: dim1 }}>
        <Row top={450} o={r1} label="LARGEST MAN-MADE LAKE BY SURFACE AREA" name="LAKE VOLTA" color={C.amber} stat="8,500 KM²" vs="vs 5,600 KM²" lake="volta" />
      </div>
      <Row top={930} o={r2} label="GREATER STORAGE CAPACITY" name="LAKE KARIBA" color={C.teal} stat="181 KM³" vs="vs 148 KM³" lake="kariba" />
      <div style={{ position: "absolute", left: ML, top: 1400, fontSize: 24, fontWeight: 600, color: C.muted, opacity: r1 }}>LAKE OUTLINES AT THE SAME SCALE</div>
      <Footer source="AREA & FULL CAPACITY: VRA, ZRA / WORLD LAKE DATABASE" />
    </AbsoluteFill>
  );
};
