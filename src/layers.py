"""
Layer definitions for the Climate Impact Atlas (klimaateffectatlas.nl) WMS
service, with the official category thresholds pulled directly from each
layer's own GetLegendGraphic response -- not guessed. Source:
https://cas.cloud.sogelink.com/public/data/org/gws/YWFMLMWERURF/kea_public/wms

Each layer's `categories` list is [(upper_bound, label), ...] in ascending
order, taken verbatim (translated) from the government legend, so risk
labels shown downstream match the official Climate Impact Atlas wording.
"""

WMS_URL = "https://cas.cloud.sogelink.com/public/data/org/gws/YWFMLMWERURF/kea_public/wms"

# NODATA sentinels seen in practice, confirmed empirically against the live
# service (not assumed):
#   - int32 max: genuinely no data at this pixel (outside the raster extent).
#   - -1: subsidence layers' own "no prediction possible" code (bedrock/dune
#     areas with no soft-soil subsidence risk -- distinct from "no data").
#   - -9999: seen on the flood-depth layers, which only carry values inside
#     modeled flood-prone areas -- everywhere else (high/dry ground outside
#     any flood scenario) is -9999. Treated as its own category below rather
#     than folded into "<0.5m", since "not a modeled flood area" is a
#     meaningfully different, more honest statement than "shallow flooding."
NODATA_INT32 = 2147483647
NODATA_NO_PREDICTION = -1
NODATA_OUTSIDE_FLOOD_ZONE = -9999
# gevoelstemperatuur_2022 (feels_like_heatwave) uses a RED_BAND property
# (0-255-style byte encoding, unlike the GRAY_INDEX float layers) and returns
# this exact value consistently at points outside its coverage -- confirmed
# empirically at two independent locations, not assumed.
NODATA_HEATWAVE_BAND = 55537
# Values this implausible for any of this service's layers (max real
# category tops out around 60cm subsidence / >50C heat / >5m flood) are
# artifacts, not real readings -- a safety net for sentinel values not yet
# individually confirmed.
IMPLAUSIBLE_MAGNITUDE = 10000

LAYERS = {
    "flood_depth_small_prob": {
        "layer": "maximale_waterdiepte_nederland_kleine_kans_20260128",
        "label": "Flood depth, small-probability scenario (~1/300/yr, dike breach)",
        "unit": "m",
        "categories": [
            (0.5, "< 0.5 m"), (1.0, "0.5-1.0 m"), (1.5, "1.0-1.5 m"),
            (2.0, "1.5-2.0 m"), (5.0, "2.0-5.0 m"), (999, "> 5.0 m"),
        ],
    },
    "flood_depth_large_prob": {
        "layer": "maximale_waterdiepte_nederland_grote_kans_20260128",
        "label": "Flood depth, large-probability scenario (regional/local extreme rainfall)",
        "unit": "m",
        "categories": [
            (0.5, "< 0.5 m"), (1.0, "0.5-1.0 m"), (1.5, "1.0-1.5 m"),
            (2.0, "1.5-2.0 m"), (5.0, "2.0-5.0 m"), (999, "> 5.0 m"),
        ],
    },
    "drought_stress_now": {
        "layer": "droogtestress_huidig",
        "label": "Agricultural drought stress, current climate",
        "unit": "% annual grass-yield loss",
        "categories": [(20, "Low (<10%)"), (30, "Moderate (10-20%)"), (999, "High (>20%)")],
    },
    "drought_stress_2050": {
        "layer": "droogtestress_2050hoog",
        "label": "Agricultural drought stress, 2050 projection (high scenario)",
        "unit": "% annual grass-yield loss",
        "categories": [(20, "Low (<10%)"), (30, "Moderate (10-20%)"), (999, "High (>20%)")],
    },
    "heat_island": {
        "layer": "hitteeiland",
        "label": "Urban heat island effect",
        "unit": "°C added",
        "categories": [
            (0.2, "0-0.2°C"), (0.4, "0.2-0.4°C"), (0.6, "0.4-0.6°C"), (0.8, "0.6-0.8°C"),
            (1.0, "0.8-1.0°C"), (1.2, "1.0-1.2°C"), (1.4, "1.2-1.4°C"), (1.6, "1.4-1.6°C"),
            (1.8, "1.6-1.8°C"), (2.0, "1.8-2.0°C"), (9999, "> 2.0°C"),
        ],
    },
    "feels_like_heatwave": {
        "layer": "gevoelstemperatuur_2022",
        "label": "Feels-like temperature during an extreme heat event",
        "unit": "°C",
        "categories": [
            (32, "Moderate heat stress: <32°C"), (35, "Moderate: 32-34°C"),
            (38, "Strong: 35-37°C"), (41, "Strong: 38-40°C"),
            (44, "Extreme (level 1): 41-43°C"), (46, "Extreme (level 1): 44-45°C"),
            (49, "Extreme (level 2): 46-48°C"), (51, "Extreme (level 2): 49-50°C"),
            (999, "Extreme (level 3): >50°C"),
        ],
    },
    "subsidence_2050": {
        "layer": "bodemdaling_2020_2050hoog",
        "label": "Predicted land subsidence by 2050 (high estimate)",
        "unit": "m",
        "categories": [
            (0.03, "Negligible (<3cm)"), (0.10, "Limited (3-10cm)"), (0.20, "Moderate (10-20cm)"),
            (0.40, "Fairly strong (20-40cm)"), (0.60, "Strong (40-60cm)"), (999, "Very strong (>60cm)"),
        ],
    },
    "subsidence_2100": {
        "layer": "bodemdaling_2020_2100hoog",
        "label": "Predicted land subsidence by 2100 (high estimate)",
        "unit": "m",
        "categories": [
            (0.03, "Negligible (<3cm)"), (0.10, "Limited (3-10cm)"), (0.20, "Moderate (10-20cm)"),
            (0.40, "Fairly strong (20-40cm)"), (0.60, "Strong (40-60cm)"), (999, "Very strong (>60cm)"),
        ],
    },
}


def categorize(key, value):
    """Map a raw pixel value to its official category label for this layer."""
    if value is None:
        return "No data"
    if value == NODATA_NO_PREDICTION:
        return "No prediction possible (e.g. bedrock/dune, no soft-soil subsidence risk)"
    if value == NODATA_OUTSIDE_FLOOD_ZONE:
        return "Not a modeled flood-prone area (high/dry ground for this scenario)"
    if value == NODATA_HEATWAVE_BAND or abs(value) >= IMPLAUSIBLE_MAGNITUDE:
        return "No data"
    for upper, label in LAYERS[key]["categories"]:
        if value <= upper:
            return label
    return "Unknown"
