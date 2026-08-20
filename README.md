# Netherlands Climate Risk Dashboard

Real flood, drought, heat, land-subsidence, and **nitrogen deposition** risk data for 34
locations across the Netherlands — nationwide, with extra density in Gelderland / the
Arnhem-Nijmegen region — sourced directly from two official Dutch government services: the
Climate Impact Atlas (klimaateffectatlas.nl) and RIVM's GCN/GDN nitrogen deposition service.
No modeling or prediction here: this reports exactly what the official sources report, with
the same categories and units as their own legends.

Author: **Maiwand Jan Alamzoi** — [m.alamzoi123@gmail.com](mailto:m.alamzoi123@gmail.com) · [github.com/maiwandalamzoi](https://github.com/maiwandalamzoi)

---

## Problem statement

Flood risk, drought stress, urban heat, and land subsidence are four of the most consequential
climate variables for Dutch property insurers, municipalities, and ESG reporting — and the
government publishes excellent open data on all four. But that data lives across dozens of
disconnected WMS map layers with Dutch-only legends, no single queryable interface, and no
plain-language risk summary per location. This project turns that into a queryable dataset and
an interactive dashboard: pick a place, see its real flood/drought/heat/subsidence profile.

**What this is**: a data-access and visualization layer over the government's own official
numbers — genuinely useful for a first-pass risk screen. **What this is not**: a replacement
for a certified flood-risk survey, insurance underwriting model, or engineering assessment —
several layers only cover part of the country (e.g. drought stress is agricultural land only;
flood depth only covers modeled flood-prone areas), and that's reported honestly rather than
papered over.

## Data source

**Climate Impact Atlas** ([klimaateffectatlas.nl](https://www.klimaateffectatlas.nl/en/), CC BY
4.0, attribution: Climate Impact Atlas, 2026) — queried live via its public WMS
`GetFeatureInfo` service, no API key required:

| Layer | Unit | Source scenario |
|---|---|---|
| Flood depth, small-probability | m | ~1/300/yr, primary dike breach |
| Flood depth, large-probability | m | Regional/local extreme rainfall |
| Drought stress, current | % annual grass-yield loss | Agricultural land |
| Drought stress, 2050 projection | % annual grass-yield loss | High-warming scenario |
| Urban heat island effect | °C added | — |
| Feels-like temperature, extreme heat | °C | Heatwave event |
| Land subsidence by 2050 | m | High estimate |
| Land subsidence by 2100 | m | High estimate |

**RIVM GCN/GDN** ([data.rivm.nl](https://www.rivm.nl/gcn-gdn-kaarten), the national nitrogen
concentration/deposition maps), queried via its own WMS `GetFeatureInfo` service, endpoint and
exact layer names found by intercepting the real network requests of RIVM's own official map
viewer (not guessed):

| Layer | Unit | Note |
|---|---|---|
| Total nitrogen deposition, 2025 | mol N/ha/yr | — |
| Potential acidification, 2025 | mol potential acid/ha/yr | — |
| Reduced nitrogen (NHx), 2025 | mol N/ha/yr | Predominantly agriculture/livestock-derived |
| Oxidized nitrogen (NOy), 2025 | mol N/ha/yr | Predominantly traffic/industry-derived |

Category thresholds and units in the dashboard's "About the data" tab are pulled **verbatim**
from each layer's own official legend (via `GetLegendGraphic`) — not estimated.

## Method

1. **`src/locations.py`** — 34 real Dutch locations: at least one per province, plus extra
   density in Gelderland / Arnhem-Nijmegen.
2. **`src/layers.py`** — the 8 layers above, with official category thresholds and 4 distinct
   nodata sentinel values discovered and confirmed empirically during development (not
   assumed): a plain "no data" code, a subsidence-specific "no prediction possible" code
   (bedrock/dune areas), a flood-specific "outside the modeled flood zone" code, and a
   layer-specific band-encoding sentinel unique to the heatwave layer. Each is labeled
   honestly and distinctly rather than being silently folded into "low risk."
3. **`src/extract_climate_risk.py`** — queries the live WMS service via `GetFeatureInfo` for
   every (location, layer) pair.
4. **`app_streamlit.py`** — interactive map (color by any of the 8 layers), a full data table,
   and an "About the data" tab documenting every category and unit.

## Real findings from the extracted data

- **Leuth** (Alamzoi Consultancy's own home base) shows **>5.0 m** flood depth in the
  small-probability dike-breach scenario — a genuinely striking, real result, not a cherry-picked
  example.
- The known low-lying reclaimed polder cities — **Almere (2.52 m), Lelystad (2.15 m),
  Dordrecht (0.97 m)** — all show real modeled flood depths matching their known geography,
  a useful sanity check that the pipeline is reading the right data correctly.
- Several major city centers (Amsterdam, Rotterdam, Den Haag, Utrecht) show "not a modeled
  flood-prone area" at their exact center points for the small-probability scenario — plausible
  given concentrated flood-defense investment in city centers, reported as-is rather than
  reinterpreted.
- **Nijmegen (2,027 mol N/ha/yr) has the highest total nitrogen deposition** of all 34
  locations, and **NHx (agriculture-derived ammonia) exceeds NOy (traffic/industry-derived)
  at every single location** — both consistent with the well-documented reality that
  agriculture, not traffic, is the dominant source of the Netherlands' nitrogen deposition,
  concentrated in livestock-dense Gelderland/Overijssel/Noord-Brabant.

## Reproduce it

```bash
git clone https://github.com/maiwandalamzoi/nl-climate-risk-dashboard.git
cd nl-climate-risk-dashboard
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt

python src/extract_climate_risk.py   # ~1-2 min: queries the live WMS service
streamlit run app_streamlit.py
```

Raw data (`data/raw/climate_risk.csv`) is committed, so `streamlit run app_streamlit.py` alone
works immediately without re-running extraction.

## License

MIT for the code — see [LICENSE](LICENSE). Underlying climate data: CC BY 4.0, Climate Impact
Atlas, 2026.
