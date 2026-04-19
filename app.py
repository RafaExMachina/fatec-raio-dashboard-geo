import math
from functools import reduce

import pandas as pd
import streamlit as st
import folium
from geopy.distance import geodesic
from streamlit_folium import st_folium

# 🔥 NOVOS IMPORTS (precisão)
from shapely.geometry import Point
from pyproj import Transformer


st.set_page_config(page_title="FATECs por raio + Região Válida (Precisa)", layout="wide")


# ---------- Utilitários ----------
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_json(path)
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)
    return df


# ---------- Projeção UTM ----------
def get_utm_zone(lat, lon):
    zone = int((lon + 180) / 6) + 1
    return f"EPSG:327{zone}" if lat < 0 else f"EPSG:326{zone}"


# ---------- Região válida precisa ----------
def compute_valid_region_precise(df_in, radius_km):
    if df_in.empty:
        return None

    lat0 = df_in["latitude"].mean()
    lon0 = df_in["longitude"].mean()

    utm_crs = get_utm_zone(lat0, lon0)

    to_utm = Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True)
    to_latlon = Transformer.from_crs(utm_crs, "EPSG:4326", always_xy=True)

    radius_m = radius_km * 1000

    circles = []

    for _, row in df_in.iterrows():
        x, y = to_utm.transform(row["longitude"], row["latitude"])
        pt = Point(x, y)
        circle = pt.buffer(radius_m)
        circles.append(circle)

    region = reduce(lambda a, b: a.intersection(b), circles)

    if region.is_empty:
        return None

    # converter de volta
    def convert_polygon(poly):
        return [(lat, lon) for lon, lat in [to_latlon.transform(x, y) for x, y in poly.exterior.coords]]

    if region.geom_type == "Polygon":
        return [convert_polygon(region)]

    elif region.geom_type == "MultiPolygon":
        return [convert_polygon(poly) for poly in region]

    return None


# ---------- Mapas ----------
def build_map(df_in, center_lat, center_lon, radius_km):
    m = folium.Map(location=[center_lat, center_lon], zoom_start=9)

    folium.Marker(
        [center_lat, center_lon],
        popup=f"Centro ({center_lat:.5f}, {center_lon:.5f})",
        icon=folium.Icon(color="red"),
    ).add_to(m)

    folium.Circle(
        [center_lat, center_lon],
        radius=radius_km * 1000,
        color="red",
        fill=True,
        fill_opacity=0.15,
    ).add_to(m)

    for _, row in df_in.iterrows():
        color = "green" if row["dentro_raio"] else "blue"
        folium.Marker(
            [row["latitude"], row["longitude"]],
            popup=f"{row.get('unidade','')}<br>{row['dist_km']:.2f} km",
            icon=folium.Icon(color=color),
        ).add_to(m)

    return m


def add_region_to_map(m, region_coords):
    if region_coords is None:
        return m

    for poly in region_coords:
        folium.Polygon(
            locations=poly,
            color="green",
            fill=True,
            fill_opacity=0.4,
        ).add_to(m)

    return m


# ---------- UI ----------
st.title("📍 FATECs dentro de um raio + Região válida (precisa)")

with st.sidebar:
    st.header("Configurações")
    center_lat = st.number_input("Centro - latitude", value=-23.50787, format="%.6f")
    center_lon = st.number_input("Centro - longitude", value=-46.78395, format="%.6f")
    radius_km = st.slider("Raio (km)", 5, 200, 30)


df = load_data("data/fatec_enderecos_geocodificados.json")

# cálculo de distância
df_local = df.copy()
df_local["dist_km"] = df_local.apply(
    lambda r: geodesic((center_lat, center_lon), (r["latitude"], r["longitude"])).km,
    axis=1,
)

df_local["dentro_raio"] = df_local["dist_km"] <= radius_km


# ---------- Layout ----------
col1, col2 = st.columns(2)

# 🔴 MAPA ORIGINAL
with col1:
    st.subheader("🗺️ Mapa original")
    m = build_map(df_local, center_lat, center_lon, radius_km)
    st_folium(m, height=600)

# 🟢 REGIÃO VÁLIDA
with col2:
    st.subheader("🟢 Região válida (precisa)")

    df_valid = df_local[df_local["dentro_raio"]]

    region_coords = compute_valid_region_precise(df_valid, radius_km)

    m2 = folium.Map(location=[center_lat, center_lon], zoom_start=9)

    m2 = add_region_to_map(m2, region_coords)

    st_folium(m2, height=600)


# ---------- Lista ----------
st.divider()

dentro = df_local[df_local["dentro_raio"]].sort_values("dist_km")

st.subheader("📋 Pontos dentro do raio")
st.write(f"{len(dentro)} pontos encontrados")

st.dataframe(dentro[["unidade", "dist_km"]])