import React from "react";
import { AbsoluteFill } from "remotion";
import { C, INTER } from "../brand";
import { Background, Header } from "../components/Chrome";

/**
 * Approved GilB outro — reproduces the GILB-001 RC1 end card (measured from the benchmark at 1080 px):
 * "UNPACKED BY" / GilB. wordmark / amber rule / "There's more to the story." / @Ghyl_B, footer rule only.
 * Static by design (the benchmark card does not animate); it cross-fades in over the previous scene.
 */
export const Outro: React.FC = () => (
  <AbsoluteFill style={{ fontFamily: INTER }}>
    <Background />
    <Header />
    <div style={{ position: "absolute", left: 0, width: 1080, top: 474, textAlign: "center", fontSize: 38, fontWeight: 600, color: C.muted, letterSpacing: 0.5 }}>UNPACKED BY</div>
    <div style={{ position: "absolute", left: 167, top: 638, fontSize: 232, fontWeight: 800, color: C.ivory, letterSpacing: -6, lineHeight: 1 }}>
      GilB<span style={{ color: C.amber }}>.</span>
    </div>
    <div style={{ position: "absolute", left: 167, width: 746, top: 950, height: 5, background: C.amber }} />
    <div style={{ position: "absolute", left: 0, width: 1080, top: 1052, textAlign: "center", fontSize: 58, fontWeight: 500, color: C.ivory, lineHeight: 1.45 }}>
      There’s more to
      <br />
      the story.
    </div>
    <div style={{ position: "absolute", left: 0, width: 1080, top: 1530, textAlign: "center", fontSize: 44, fontWeight: 700, color: C.amber }}>@Ghyl_B</div>
    <div style={{ position: "absolute", left: 87, width: 906, top: 1757, height: 2, background: "#1F3341" }} />
  </AbsoluteFill>
);
