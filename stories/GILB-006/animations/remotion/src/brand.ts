import { loadFont } from "@remotion/google-fonts/Inter";
import { Easing } from "remotion";

// GilB house style, taken from the approved GILB-001 benchmark (renderer + RC1 frames).
export const { fontFamily: INTER } = loadFont("normal", {
  weights: ["500", "600", "700", "800", "900"],
  subsets: ["latin"],
});

export const C = {
  ivory: "#F3F0E8",
  muted: "#8FA3B5",
  amber: "#E0AB52", // Lake Volta
  teal: "#2FA3A1", // Lake Kariba
  track: "#1E3244",
  rule: "#2F414E",
  land: "#0F2030",
  landEdge: "#2A4256",
  bgTop: "#08131F",
  bgBottom: "#10202F",
  river: "#7E9DB3",
};

// 1080 x 1920 layout, GILB-001 x1.5
export const W = 1080;
export const H = 1920;
export const ML = 87;
export const MR = 993;

// Motion vocabulary
export const EASE_OUT = Easing.bezier(0.16, 1, 0.3, 1);
export const EASE_IN_OUT = Easing.bezier(0.65, 0, 0.35, 1);
export const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
