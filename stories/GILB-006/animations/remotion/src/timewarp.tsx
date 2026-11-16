import React, { createContext, useContext } from "react";
import { interpolate, useCurrentFrame } from "remotion";

/**
 * Time-warp for re-timing an approved proof scene to the mastered narration without
 * rewriting its animation. Anchors are [episodeFrame, sceneFrame] pairs (both relative to the
 * scene's Sequence start), mapped piecewise-linearly. With no provider, scenes run at 1:1, so the
 * standalone Phase A proof compositions are unchanged.
 */
type Anchors = [number, number][];
const WarpCtx = createContext<Anchors | null>(null);

export const TimeWarp: React.FC<{ anchors: Anchors; children: React.ReactNode }> = ({ anchors, children }) => (
  <WarpCtx.Provider value={anchors}>{children}</WarpCtx.Provider>
);

export const useSceneFrame = (): number => {
  const f = useCurrentFrame();
  const a = useContext(WarpCtx);
  if (!a) return f;
  return interpolate(
    f,
    a.map((p) => p[0]),
    a.map((p) => p[1]),
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
};
