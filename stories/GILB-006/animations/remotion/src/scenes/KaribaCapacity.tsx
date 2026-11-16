import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, CLAMP, EASE_OUT, INTER, ML } from "../brand";
import { Background, Eyebrow, Footer, Header } from "../components/Chrome";
import { BigCounter } from "../components/Kit";
import { LAKES, META, kmToPx, makeProjection, pathOf } from "../geo/geo";

/**
 * Scene 10 (episode 46.20 s → 52.93 s, 202 frames). Mirrors the Lake Volta capacity beat.
 * VO: "Now, Lake Kariba? At full capacity, it can hold about one hundred and eighty-one cubic kilometres."
 * 181 km³ is the full-supply storage capacity (ZRA / World Lake Database), not the current level.
 */
const K = 19000;

export const KaribaCapacity: React.FC = () => {
  const frame = useCurrentFrame();
  const proj = makeProjection([27.95, -17.2], K, 560, 1130);
  const dam = proj(META.dams.kariba) ?? [0, 0];
  const lakeIn = interpolate(frame, [0, 14], [0, 1], CLAMP);
  // fill rises to full capacity while the counter runs; "181" is spoken at 50.22 s = local 120
  const fillKm = interpolate(frame, [40, 124], [0, 300], { ...CLAMP, easing: (t) => 1 - Math.pow(1 - t, 2) });
  const count = Math.round(interpolate(frame, [52, 122], [0, 181], { ...CLAMP, easing: EASE_OUT }));
  const fullCap = interpolate(frame, [44, 60], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const litres = interpolate(frame, [150, 166], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const ref = interpolate(frame, [160, 176], [0, 1], { ...CLAMP, easing: EASE_OUT });

  return (
    <AbsoluteFill style={{ fontFamily: INTER }}>
      <Background />
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <clipPath id="karCap">
            <circle cx={dam[0]} cy={dam[1]} r={Math.max(0.01, kmToPx(fillKm, K))} />
          </clipPath>
        </defs>
        {/* empty basin outline, then water fills from the dam */}
        <path d={pathOf(proj)(LAKES.kariba as never) ?? ""} fill={C.track} fillRule="evenodd" stroke={C.teal} strokeOpacity={0.5} strokeWidth={1.5} opacity={lakeIn} />
        <g clipPath="url(#karCap)">
          <path d={pathOf(proj)(LAKES.kariba as never) ?? ""} fill={C.teal} fillRule="evenodd" />
        </g>
      </svg>
      <Header />
      <Eyebrow>MEASURE 2 · STORAGE CAPACITY</Eyebrow>
      <BigCounter top={336} size={190} value={String(count)} unit="KM³ OF WATER" sub="LAKE KARIBA · AT FULL CAPACITY" color={C.teal} o={fullCap} />
      <div style={{ position: "absolute", left: ML, top: 700, fontSize: 64, fontWeight: 900, color: C.ivory, opacity: litres, letterSpacing: -0.5 }}>= 181 TRILLION LITRES.</div>
      <div style={{ position: "absolute", left: ML, top: 1560, opacity: ref, fontSize: 30, fontWeight: 700, color: C.muted }}>
        LAKE VOLTA: <span style={{ color: C.amber }}>148 KM³</span>
      </div>
      <Footer source="CAPACITY: ZRA / WORLD LAKE DATABASE · OUTLINE: © OSM" />
    </AbsoluteFill>
  );
};
