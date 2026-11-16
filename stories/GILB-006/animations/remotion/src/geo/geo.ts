import { geoAzimuthalEqualArea, geoPath, GeoProjection } from "d3-geo";
import lakesJson from "./lakes.json";
import africaJson from "./africa.json";
import regionJson from "./region.json";
import riversJson from "./rivers.json";
import metaJson from "./meta.json";

type MP = { type: "MultiPolygon"; coordinates: number[][][][] };
export const LAKES = lakesJson as unknown as { volta: MP; kariba: MP };
export const AFRICA = africaJson as unknown as { name: string; iso: string; geometry: MP }[];
export const REGION = regionJson as unknown as { name: string; iso: string; geometry: MP }[];
export const RIVERS = riversJson as unknown as { name: string; featurecla: string; lines: number[][][] }[];
export const META = metaJson as unknown as { dams: { akosombo: [number, number]; kariba: [number, number] } };

export const EARTH_R_KM = 6371.0088;

/**
 * Lambert azimuthal equal-area projection centred on `center`.
 * `k` = projection scale (px per radian). Equal-area => areas on screen are proportional
 * to true areas everywhere, so side-by-side lakes at the same k are a fair size comparison.
 */
export const makeProjection = (center: [number, number], k: number, tx: number, ty: number): GeoProjection =>
  geoAzimuthalEqualArea()
    .rotate([-center[0], -center[1]])
    .scale(k)
    .translate([tx, ty])
    .clipExtent([
      [-200, -200],
      [1280, 2120],
    ]);

export const pathOf = (p: GeoProjection) => geoPath(p);

/** km -> px at the projection centre (exact for equal-area at the centre). */
export const kmToPx = (km: number, k: number) => (km / EARTH_R_KM) * k;

export const lineString = (coords: number[][]) => ({ type: "LineString" as const, coordinates: coords });
