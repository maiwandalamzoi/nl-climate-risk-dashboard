"""
Netherlands Climate Risk Dashboard.

Real flood, drought, heat, and land-subsidence risk data for 34 Dutch
locations, sourced directly from the government's official Climate Impact
Atlas (klimaateffectatlas.nl) WMS service. No modeling or prediction here --
this shows exactly what the official service reports, with the same
category thresholds and units as its own legend.

Run:
    streamlit run app_streamlit.py
"""
import sys
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from layers import LAYERS, categorize  # noqa: E402

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "raw" / "climate_risk.csv"

RISK_COLORS = {
    # Low risk -> high risk, used for the map marker color per selected layer.
    0: "#2f855a", 1: "#68a357", 2: "#c9a227", 3: "#d97f2f", 4: "#c9542f", 5: "#c53030",
}

st.set_page_config(page_title="NL Climate Risk Dashboard", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    return df


def risk_rank(key, raw_value):
    """0 (low/no risk) .. 5 (high risk), for map coloring. None/no-data -> -1 (grey)."""
    if pd.isna(raw_value):
        return -1
    label = categorize(key, raw_value)
    if "No data" in label or "No prediction" in label or "Not a modeled" in label:
        return 0  # treated as "no elevated risk detected" for map coloring, not "unknown"
    cats = LAYERS[key]["categories"]
    idx = next((i for i, (upper, _) in enumerate(cats) if raw_value <= upper), len(cats) - 1)
    return min(round(idx / max(len(cats) - 1, 1) * 5), 5)


def main():
    st.title("🇳🇱 Netherlands Climate Risk Dashboard")
    st.caption(
        "Real flood, drought, heat and land-subsidence risk data for 34 locations, sourced "
        "directly from the Dutch government's official Climate Impact Atlas "
        "(klimaateffectatlas.nl). No prediction or modeling here -- this shows exactly what "
        "the official service reports."
    )

    df = load_data()
    layer_options = {meta["label"]: key for key, meta in LAYERS.items()}

    selected_label = st.sidebar.selectbox("Risk layer (map color)", list(layer_options.keys()))
    selected_key = layer_options[selected_label]
    meta = LAYERS[selected_key]
    st.sidebar.caption(f"Unit: {meta['unit']}")

    scope = st.sidebar.radio("Scope", ["All of the Netherlands", "Gelderland / Arnhem-Nijmegen (featured)"])
    df_view = df if scope == "All of the Netherlands" else df[df["featured"] == True]  # noqa: E712

    tab_map, tab_table, tab_about = st.tabs(["🗺️ Map", "📋 All locations & risk factors", "ℹ️ About the data"])

    with tab_map:
        st.subheader(selected_label)
        center = [df_view["lat"].mean(), df_view["lon"].mean()]
        fmap = folium.Map(location=center, zoom_start=7 if scope.startswith("All") else 9,
                           tiles="CartoDB positron")
        for _, row in df_view.iterrows():
            raw = row[selected_key]
            rank = risk_rank(selected_key, raw)
            color = "#999999" if rank < 0 else RISK_COLORS[rank]
            cat_label = categorize(selected_key, raw) if pd.notna(raw) else "No data"
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=9, color=color, fill=True, fill_opacity=0.85,
                popup=f"<b>{row['name']}</b> ({row['province']})<br>{selected_label}:<br>{cat_label}",
            ).add_to(fmap)
        st_folium(fmap, width=1100, height=560)
        st.caption("Marker color: green = lower risk band -> red = higher risk band, per the "
                    "official Climate Impact Atlas categories for this layer. Grey = no data at this point.")

    with tab_table:
        st.subheader(f"All risk factors, {scope.lower()}")
        display_rows = []
        for _, row in df_view.iterrows():
            r = {"Location": row["name"], "Province": row["province"]}
            for key, m in LAYERS.items():
                r[m["label"]] = categorize(key, row[key])
            display_rows.append(r)
        st.dataframe(pd.DataFrame(display_rows), width="stretch", height=500)

    with tab_about:
        st.subheader("Where this data comes from")
        st.markdown(
            "All values are pulled live from the Dutch government's official "
            "[Climate Impact Atlas](https://www.klimaateffectatlas.nl/en/) WMS service "
            "(CC BY 4.0, attribution: Climate Impact Atlas, 2026), queried at each location's "
            "coordinates via the standard OGC `GetFeatureInfo` operation. Category thresholds "
            "and units below are taken **verbatim from each layer's own official legend** -- "
            "not estimated or guessed."
        )
        for key, m in LAYERS.items():
            with st.expander(f"{m['label']} ({m['unit']})"):
                for upper, label in m["categories"]:
                    st.write(f"- {label}")
        st.caption(
            "Note: several layers only carry data within their own modeled extent (e.g. flood "
            "depth is only mapped inside flood-prone areas; drought stress only over "
            "agricultural/vegetated land) -- points outside that extent are reported as-is "
            "('not a modeled area' / 'no data'), not silently treated as zero risk."
        )


if __name__ == "__main__":
    main()
