"""
Query the Climate Impact Atlas (klimaateffectatlas.nl) WMS service via
GetFeatureInfo for every (location, layer) pair, and save the raw values.

Usage:
    python src/extract_climate_risk.py
"""
import csv
import time
from pathlib import Path

import requests

from layers import LAYERS, NODATA_INT32, NODATA_NO_PREDICTION
from locations import LOCATIONS

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "climate_risk.csv"
DELTA = 0.0015  # ~150m half-width query box around each point -- small enough
                 # to sample close to the exact coordinate, large enough to
                 # avoid missing the raster's own pixel grid entirely.


def query_point(layer_name, lat, lon, retries=3):
    bbox = f"{lon-DELTA},{lat-DELTA},{lon+DELTA},{lat+DELTA}"
    params = {
        "SERVICE": "WMS", "VERSION": "1.1.1", "REQUEST": "GetFeatureInfo",
        "LAYERS": layer_name, "QUERY_LAYERS": layer_name,
        "BBOX": bbox, "WIDTH": 3, "HEIGHT": 3, "X": 1, "Y": 1,
        "SRS": "EPSG:4326", "INFO_FORMAT": "application/json",
    }
    from layers import WMS_URL
    for attempt in range(retries):
        try:
            resp = requests.get(WMS_URL, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            feats = data.get("features", [])
            if not feats:
                return None
            props = feats[0].get("properties", {})
            if not props:
                return None
            # Different layers on this service use different raster band
            # property names (GRAY_INDEX, RED_BAND, ...) -- confirmed by
            # direct inspection rather than assumed, so read whichever
            # numeric property is actually present instead of hardcoding one.
            val = next(iter(props.values()), None)
            if val is None or val == NODATA_INT32:
                return None
            return float(val)
        except Exception as e:
            if attempt == retries - 1:
                print(f"  ! failed {layer_name} @ ({lat},{lon}): {e}")
                return None
            time.sleep(2 * (attempt + 1))


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fields = ["name", "province", "lat", "lon", "featured"] + list(LAYERS.keys())

    rows_written = 0
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for i, (name, province, lat, lon, featured) in enumerate(LOCATIONS):
            row = {"name": name, "province": province, "lat": lat, "lon": lon, "featured": featured}
            for key, meta in LAYERS.items():
                val = query_point(meta["layer"], lat, lon)
                row[key] = val
            writer.writerow(row)
            rows_written += 1
            print(f"[{i+1}/{len(LOCATIONS)}] {name}: "
                  + ", ".join(f"{k}={row[k]}" for k in list(LAYERS.keys())[:2]))
            f.flush()

    print(f"\nDone. Wrote {rows_written} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
