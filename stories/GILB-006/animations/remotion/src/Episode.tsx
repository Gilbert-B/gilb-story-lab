import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { TimeWarp } from "./timewarp";
import { OpeningVolta } from "./scenes/OpeningVolta";
import { KaribaIntro } from "./scenes/KaribaIntro";
import { AreaQuestion } from "./scenes/AreaQuestion";
import { PolytankScale } from "./scenes/PolytankScale";
import { KaribaCapacity } from "./scenes/KaribaCapacity";
import { CapacityGap } from "./scenes/CapacityGap";
import { AreaVsDepth } from "./scenes/AreaVsDepth";
import { Verdict } from "./scenes/Verdict";
import { BothEnormous } from "./scenes/BothEnormous";
import { Callback } from "./scenes/Callback";
import { Outro } from "./scenes/Outro";

/**
 * GILB Lake Volta — "Largest by what?" full episode, LOCKED to the approved mastered narration
 * (public/narration_v1.wav, 119.34 s; sha256 00e66b3b…e334e). Cue times come from word timestamps in
 * timing/words.json (faster-whisper small, local). Scene starts are in frames at 30 fps.
 *
 * Proof scenes (opening, Polytank, area-vs-depth) keep their approved animation and are re-timed with a
 * piecewise-linear TimeWarp: [episode frame within scene, proof frame] anchors on spoken words.
 */
export const FPS = 30;
export const EPISODE_FRAMES = 3581; // ceil(119.34 s × 30)
const XF = 8; // cross-fade frames between scenes

type Cue = { id: string; from: number; to: number; el: React.ReactNode };

const CUES: Cue[] = [
  {
    // 0.00–14.33 s: "Ghana is home… / …record you might not know. / Lake Volta is the largest by surface area. / It covers about 8,500 km²."
    id: "01-04 Opening",
    from: 0,
    to: 430,
    el: (
      <TimeWarp anchors={[[0, 0], [125, 104], [263, 212], [318, 300], [378, 400], [438, 420]]}>
        <OpeningVolta />
      </TimeWarp>
    ),
  },
  { id: "05-06 Kariba", from: 430, to: 699, el: <KaribaIntro /> }, // 14.33–23.30 s
  { id: "07 Question", from: 699, to: 858, el: <AreaQuestion /> }, // 23.30–28.60 s
  {
    // 28.60–46.20 s: "At full capacity… 148 km³ … Polytanks … almost thirty billion of them…"
    id: "08-09 Polytank",
    from: 858,
    to: 1386,
    el: (
      <TimeWarp anchors={[[0, 0], [125, 60], [216, 112], [272, 134], [320, 186], [437, 392], [470, 440], [536, 480]]}>
        <PolytankScale />
      </TimeWarp>
    ),
  },
  { id: "10 Kariba capacity", from: 1386, to: 1588, el: <KaribaCapacity /> }, // 46.20–52.93 s
  { id: "11 Capacity gap", from: 1588, to: 1770, el: <CapacityGap /> }, // 52.93–59.00 s
  {
    // 59.00–90.90 s: "How's that possible? … two containers … deeper basin … one and a half times as deep."
    id: "12-13 Area vs depth",
    from: 1770,
    to: 2727,
    el: (
      <TimeWarp
        anchors={[
          [0, 0], [73, 10], [133, 105], [182, 135], [231, 195], [278, 222], [332, 300], [376, 326], [470, 386],
          [530, 440], [600, 500], [625, 505], [738, 560], [766, 562], [828, 590], [840, 600], [885, 650], [890, 660], [910, 676], [965, 720],
        ]}
      >
        <AreaVsDepth />
      </TimeWarp>
    ),
  },
  { id: "14 Verdict", from: 2727, to: 3027, el: <Verdict /> }, // 90.90–100.90 s
  { id: "15 Both enormous", from: 3027, to: 3170, el: <BothEnormous /> }, // 100.90–105.67 s
  { id: "16-17 Largest by what", from: 3170, to: 3462, el: <Callback /> }, // 105.67–115.40 s
  { id: "18 Outro", from: 3448, to: EPISODE_FRAMES, el: <Outro /> }, // 114.93 s → end ("Unpacked by GilB" 115.40 s)
];

const FadeIn: React.FC<{ frames: number; children: React.ReactNode }> = ({ frames, children }) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{ opacity: interpolate(f, [0, frames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{children}</AbsoluteFill>;
};

export const Episode: React.FC = () => (
  <AbsoluteFill style={{ background: "#08131F" }}>
    {CUES.map((c, i) => {
      // Scene local frame 0 = its cue. The incoming scene fades in on top while the previous one
      // runs XF frames past its cue, so in-scene word timings are not shifted.
      const last = i === CUES.length - 1;
      return (
        <Sequence key={c.id} name={c.id} from={c.from} durationInFrames={c.to - c.from + (last ? 0 : XF)}>
          {i === 0 ? c.el : <FadeIn frames={last ? 14 : XF}>{c.el}</FadeIn>}
        </Sequence>
      );
    })}
    {/* narration (untouched) + original music bed + effects, pre-mixed by audio/mix.sh */}
    <Audio src={staticFile("mix_v1.wav")} />
  </AbsoluteFill>
);
