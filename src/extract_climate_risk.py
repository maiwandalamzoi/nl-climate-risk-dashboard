"""
Query two official Dutch government WMS services via GetFeatureInfo for
every (location, layer) pair, and save the raw values: the Climate Impact
Atlas (klimaateffectatlas.nl) and RIVM's GCN/GDN nitrogen deposition
service. See layers.py for source details.

Usage:
    python src/extract_climate_risk.py
"""
import csv
import time
from pathlib import Path

import requests

from layers import LAYERS, WMS_URL, NODATA_INT32, NODATA_NO_PREDICTION
from locations import LOCATIONS

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "climate_risk.csv"
DELTA = 0.0015  # ~150m half-width query box around each point -- small enough
                 # to sample close to the exact coordinate, large enough to
                 # avoid missing the raster's own pixel grid entirely.


def query_point(layer_name, lat, lon, wms_url=WMS_URL, retries=3):
    bbox = f"{lon-DELTA},{lat-DELTA},{lon+DELTA},{lat+DELTA}"
    params = {
        "SERVICE": "WMS", "VERSION": "1.1.1", "REQUEST": "GetFeatureInfo",
        "LAYERS": layer_name, "QUERY_LAYERS": layer_name,
        "BBOX": bbox, "WIDTH": 3, "HEIGHT": 3, "X": 1, "Y": 1,
        "SRS": "EPSG:4326", "INFO_FORMAT": "application/json",
    }
    for attempt in range(retries):
        try:
            resp = requests.get(wms_url, params=params, timeout=30)
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
                val = query_point(meta["layer"], lat, lon, wms_url=meta.get("wms_url", WMS_URL))
                row[key] = val
            writer.writerow(row)
            rows_written += 1
            print(f"[{i+1}/{len(LOCATIONS)}] {name}: "
                  + ", ".join(f"{k}={row[k]}" for k in list(LAYERS.keys())[:2]))
            f.flush()

    print(f"\nDone. Wrote {rows_written} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
