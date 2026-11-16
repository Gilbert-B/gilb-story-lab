import React from "react";
import { AbsoluteFill } from "remotion";
import { C, INTER, ML, MR } from "../brand";

// Background + GilB header/footer exactly as the GILB-001 benchmark (scaled 1.5x to 1080 wide).
export const Background: React.FC = () => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(75% 60% at 100% 100%, rgba(27,74,92,0.55) 0%, rgba(27,74,92,0) 100%), linear-gradient(180deg, ${C.bgTop} 0%, ${C.bgBottom} 100%)`,
    }}
  />
);

export const Header: React.FC = () => (
  <AbsoluteFill style={{ fontFamily: INTER, pointerEvents: "none" }}>
    <div style={{ position: "absolute", left: ML, top: 104, fontSize: 56, fontWeight: 800, color: C.ivory, letterSpacing: -1, lineHeight: 1 }}>
      GilB<span style={{ color: C.amber }}>.</span>
    </div>
    <div style={{ position: "absolute", right: 1080 - MR, top: 128, fontSize: 30, fontWeight: 600, color: C.muted }}>@Ghyl_B</div>
    <div style={{ position: "absolute", left: ML, width: MR - ML, top: 217, height: 3, background: C.rule }} />
  </AbsoluteFill>
);

export const Footer: React.FC<{ source?: string }> = ({ source }) => (
  <AbsoluteFill style={{ fontFamily: INTER, pointerEvents: "none" }}>
    {source ? (
      <div style={{ position: "absolute", left: ML, width: MR - ML, top: 1700, fontSize: 22, fontWeight: 600, color: C.muted, letterSpacing: 0.3, opacity: 0.85 }}>{source}</div>
    ) : null}
    <div style={{ position: "absolute", left: ML, width: MR - ML, top: 1757, height: 2, background: "#1F3341" }} />
    <div style={{ position: "absolute", left: ML, top: 1790, fontSize: 24, fontWeight: 600, color: C.muted, letterSpacing: 0.5 }}>UNPACKED BY GILB</div>
  </AbsoluteFill>
);

export const Eyebrow: React.FC<{ children: React.ReactNode; opacity?: number }> = ({ children, opacity = 1 }) => (
  <div style={{ position: "absolute", left: ML, top: 292, fontFamily: INTER, fontSize: 27, fontWeight: 600, color: C.muted, letterSpacing: 0.3, opacity }}>{children}</div>
);
