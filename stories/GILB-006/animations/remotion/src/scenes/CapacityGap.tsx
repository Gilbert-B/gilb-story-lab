import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, CLAMP, EASE_IN_OUT, EASE_OUT, INTER, ML } from "../brand";
import { Background, Eyebrow, Footer, Header } from "../components/Chrome";
import { BigCounter, CompareBars } from "../components/Kit";

/**
 * Scene 11 (episode 52.93 s → 59.00 s, 182 frames).
 * VO: "That's more than thirty cubic kilometres more water, despite covering less surface area."
 * 181 − 148 = 33 km³. Both bar sets are zero-based and drawn from the exact published values.
 */
const X = ML;
const WIDTH = 640;

export const CapacityGap: React.FC = () => {
  const frame = useCurrentFrame();
  const capBars = interpolate(frame, [0, 34], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const gap = interpolate(frame, [30, 56], [0, 1], { ...CLAMP, easing: EASE_IN_OUT });
  const big = interpolate(frame, [34, 50], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const n = Math.round(interpolate(frame, [34, 72], [0, 33], { ...CLAMP, easing: EASE_OUT }));
  // "despite covering less surface area" starts 56.70 s = local 113
  const area = interpolate(frame, [108, 140], [0, 1], { ...CLAMP, easing: EASE_OUT });
  const less = interpolate(frame, [134, 150], [0, 1], { ...CLAMP, easing: EASE_OUT });

  const y1 = 1010; // capacity bars
  const y2 = 1390; // area bars
  const voltaW = WIDTH * (148 / 181);

  return (
    <AbsoluteFill style={{ fontFamily: INTER }}>
      <Background />
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        <text x={X} y={y1 - 78} fill={C.muted} fontSize={27} fontWeight={600} opacity={capBars}>STORAGE CAPACITY (FULL)</text>
        <CompareBars
          x={X}
          y={y1}
          width={WIDTH}
          max={181}
          p={capBars}
          rows={[
            { name: "VOLTA", value: 148, label: "148 KM³", color: C.amber },
            { name: "KARIBA", value: 181, label: "181 KM³", color: C.teal },
          ]}
        />
        {/* the extra 33 km³ on Kariba's bar */}
        <g opacity={gap}>
          <line x1={X + voltaW} y1={y1 - 4} x2={X + voltaW} y2={y1 + 92 + 50} stroke={C.ivory} strokeWidth={3} strokeDasharray="6 6" />
          <rect x={X + voltaW} y={y1 + 92} width={(WIDTH - voltaW) * gap} height={40} fill={C.ivory} fillOpacity={0.9} />
          <text x={X + voltaW + (WIDTH - voltaW) / 2} y={y1 + 92 + 86} fill={C.ivory} fontSize={30} fontWeight={900} textAnchor="middle">+33</text>
        </g>

        <g opacity={area}>
          <text x={X} y={y2 - 78} fill={C.muted} fontSize={27} fontWeight={600}>SURFACE AREA</text>
          <CompareBars
            x={X}
            y={y2}
            width={WIDTH}
            max={8502}
            p={area}
            rows={[
              { name: "VOLTA", value: 8502, label: "8,500 KM²", color: C.amber },
              { name: "KARIBA", value: 5580, label: "5,600 KM²", color: C.teal },
            ]}
          />
          <text x={X} y={y2 + 92 + 96} fill={C.ivory} fontSize={30} fontWeight={900} opacity={less}>
            LESS AREA
          </text>
        </g>
      </svg>
      <Header />
      <Eyebrow>LAKE KARIBA VS LAKE VOLTA</Eyebrow>
      <BigCounter top={336} size={190} value={`+${n}`} unit="KM³ MORE WATER" sub="181 KM³ − 148 KM³ = 33 KM³" color={C.teal} o={big} />
      <Footer source="CAPACITY & AREA: VRA, ZRA / WORLD LAKE DATABASE" />
    </AbsoluteFill>
  );
};
