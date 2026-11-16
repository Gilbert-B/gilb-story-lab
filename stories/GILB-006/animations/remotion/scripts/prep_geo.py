"""GILB Lake Volta episode - geometry preparation (reproducible).

Inputs (downloaded 2026-11-15, kept untouched in ../_geo_raw):
  - Natural Earth 1:10m v5 lakes, admin-0 countries, rivers+lake centerlines (public domain)
    https://github.com/nvkelso/natural-earth-vector/tree/master/geojson
  - OpenStreetMap relation 318675 (Lake Kariba), fetched via Nominatim polygon_geojson,
    polygon_threshold=0.0003 deg. (c) OpenStreetMap contributors, ODbL 1.0.

Choice of geometry (see PROVENANCE.md): Lake Volta = Natural Earth 10m (7,994 km2 measured,
94% of the published 8,502); Lake Kariba = OSM (5,371 km2 measured, 96% of 5,580). The OSM Volta
relation measured only 6,692 km2 (79%), and Natural Earth Kariba 4,724 km2 (85%), so the chosen
pair is the one whose measured area ratio (1.49) is closest to the published ratio (1.52).

Outputs lon/lat GeoJSON-like JSON in src/geo/. Projection happens in the composition (d3-geo).
Run:  python -I scripts/prep_geo.py ../_geo_raw src/geo
"""
import json, math, sys, os

RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
R = 6371.0088


def ring_area(r):
    a = 0.0
    for i in range(len(r) - 1):
        lon1, lat1 = map(math.radians, r[i]); lon2, lat2 = map(math.radians, r[i + 1])
        a += (lon2 - lon1) * (2 + math.sin(lat1) + math.sin(lat2))
    return abs(a * R * R / 2)


def polys_of(g):
    return g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]


def area(g):
    return sum(ring_area(p[0]) - sum(ring_area(h) for h in p[1:]) for p in polys_of(g))


def dp(pts, tol):
    """Douglas-Peucker on lon/lat (tol in degrees)."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]; bx, by = pts[b]; dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy) or 1e-12
        best, bi = -1, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            d = abs(dy * px - dx * py + bx * ay - by * ax) / L
            if d > best:
                best, bi = d, i
        if best > tol:
            keep[bi] = True; stack += [(a, bi), (bi, b)]
    return [p for p, k in zip(pts, keep) if k]


def dp_ring(r, tol):
    """Closed ring: split at the vertex farthest from the start, simplify both halves."""
    pts = r[:-1] if r[0] == r[-1] else r[:]
    if len(pts) < 4:
        return r
    x0, y0 = pts[0]
    k = max(range(len(pts)), key=lambda i: (pts[i][0] - x0) ** 2 + (pts[i][1] - y0) ** 2)
    a = dp(pts[:k + 1], tol); b = dp(pts[k:] + [pts[0]], tol)
    return a + b[1:]


def simplify_geom(g, tol, min_hole_km2=0.0, min_part_km2=0.0, dec=4):
    out = []
    for p in polys_of(g):
        if ring_area(p[0]) < min_part_km2:
            continue
        rings = [dp_ring(p[0], tol)]
        for h in p[1:]:
            if ring_area(h) >= min_hole_km2:
                s = dp_ring(h, tol)
                if len(s) >= 4:
                    rings.append(s)
        if len(rings[0]) >= 4:
            rings = [close(r) for r in rings]
            # d3-geo winding: exterior clockwise, holes counter-clockwise (planar lon/lat, y up)
            rings = [orient(r, cw=(i == 0)) for i, r in enumerate(rings)]
            out.append([[[round(x, dec), round(y, dec)] for x, y in r] for r in rings])
    return {'type': 'MultiPolygon', 'coordinates': out}


def close(r):
    return r if r[0] == r[-1] else r + [r[0]]


def orient(r, cw):
    s = sum(r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1] for i in range(len(r) - 1))  # >0 = counter-clockwise
    is_cw = s < 0
    return r if is_cw == cw else r[::-1]


def npts(g):
    return sum(len(r) for p in polys_of(g) for r in p)


lakes = json.load(open(os.path.join(RAW, 'ne_10m_lakes.geojson'), encoding='utf-8'))
volta_ne = next(f for f in lakes['features'] if f['properties'].get('name') == 'Lake Volta')['geometry']
kariba_osm = json.load(open(os.path.join(RAW, 'osm_kariba.geojson'), encoding='utf-8'))['features'][0]['geometry']

volta = simplify_geom(volta_ne, 0.0015)
kariba = simplify_geom(kariba_osm, 0.0025, min_hole_km2=2.0, min_part_km2=1.0)

countries = json.load(open(os.path.join(RAW, 'ne_10m_admin_0_countries.geojson'), encoding='utf-8'))
africa, region = [], []
for f in countries['features']:
    p = f['properties']
    if p.get('CONTINENT') != 'Africa':
        continue
    name = p.get('NAME_EN') or p.get('NAME')
    africa.append({'name': name, 'iso': p.get('ISO_A3_EH') or p.get('ADM0_A3'), 'geometry': simplify_geom(f['geometry'], 0.03, min_part_km2=150)})
    if name in ('Ghana', 'Togo', 'Burkina Faso', 'Ivory Coast', "Côte d'Ivoire", 'Zambia', 'Zimbabwe'):
        region.append({'name': name, 'iso': p.get('ISO_A3_EH') or p.get('ADM0_A3'), 'geometry': simplify_geom(f['geometry'], 0.004, min_part_km2=5)})

rivers_src = json.load(open(os.path.join(RAW, 'ne_10m_rivers_lake_centerlines.geojson'), encoding='utf-8'))
rivers = []
for f in rivers_src['features']:
    n = f['properties'].get('name') or ''
    g = f['geometry']
    if g is None:
        continue
    lines = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
    lines = [l for l in lines if l]
    if not lines:
        continue
    xs = [p[0] for l in lines for p in l]; ys = [p[1] for l in lines for p in l]
    if not (-3.5 < min(xs) and max(xs) < 2.5 and 5.5 < min(ys) and max(ys) < 14.5):
        continue
    label = {'Mouhoun': 'Black Volta', 'Oti': 'Oti', 'Volta': 'Volta'}.get(n)
    if n.startswith('Nakanb'):
        label = 'White Volta'
    if not label:
        continue
    rivers.append({'name': label, 'featurecla': f['properties'].get('featurecla'), 'lines': [[[round(x, 4), round(y, 4)] for x, y in dp(l, 0.003)] for l in lines]})

AKOSOMBO = [0.0569, 6.2994]   # Akosombo Dam crest, approx. (verify against VRA before final)
KARIBA_DAM = [28.7614, -16.5225]

meta = {
    'lakes': {
        'volta': {'source': 'Natural Earth 1:10m lakes v5 (public domain)', 'measured_km2_source': round(area(volta_ne)), 'measured_km2_simplified': round(area(volta)), 'published_km2': 8502, 'points': npts(volta)},
        'kariba': {'source': 'OpenStreetMap relation 318675 (c) OpenStreetMap contributors, ODbL', 'measured_km2_source': round(area(kariba_osm)), 'measured_km2_simplified': round(area(kariba)), 'published_km2': 5580, 'points': npts(kariba)},
    },
    'dams': {'akosombo': AKOSOMBO, 'kariba': KARIBA_DAM},
}
json.dump({'volta': volta, 'kariba': kariba}, open(os.path.join(OUT, 'lakes.json'), 'w'), separators=(',', ':'))
json.dump(africa, open(os.path.join(OUT, 'africa.json'), 'w'), separators=(',', ':'))
json.dump(region, open(os.path.join(OUT, 'region.json'), 'w'), separators=(',', ':'))
json.dump(rivers, open(os.path.join(OUT, 'rivers.json'), 'w'), separators=(',', ':'))
json.dump(meta, open(os.path.join(OUT, 'meta.json'), 'w'), indent=1)
print(json.dumps(meta, indent=1))
print('africa', len(africa), 'region', [c['name'] for c in region], 'rivers', [(r['name'], r['featurecla']) for r in rivers])
for fn in ('lakes', 'africa', 'region', 'rivers'):
    print(fn, os.path.getsize(os.path.join(OUT, fn + '.json')))
