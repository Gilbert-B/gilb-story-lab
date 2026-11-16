import React from "react";
import { Composition } from "remotion";
import { OpeningVolta } from "./scenes/OpeningVolta";
import { PolytankScale } from "./scenes/PolytankScale";
import { AreaVsDepth } from "./scenes/AreaVsDepth";
import { Episode, EPISODE_FRAMES } from "./Episode";

// GILB Lake Volta. "Episode" = full cut locked to the approved narration (Phase B).
// P1–P3 = the approved Phase A proofs at their original (proof) timing.
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="Episode" component={Episode} durationInFrames={EPISODE_FRAMES} fps={30} width={1080} height={1920} />
      <Composition id="P1-VoltaOpening" component={OpeningVolta} durationInFrames={420} fps={30} width={1080} height={1920} />
      <Composition id="P2-Polytank" component={PolytankScale} durationInFrames={480} fps={30} width={1080} height={1920} />
      <Composition id="P3-AreaVsDepth" component={AreaVsDepth} durationInFrames={720} fps={30} width={1080} height={1920} />
    </>
  );
};
