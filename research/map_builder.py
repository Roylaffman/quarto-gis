"""
Reusable Folium map builder for the Quarto GIS workflow.

Usage:
    from map_builder import create_base_map, add_geodataframe_layer, add_point_markers

Builds on Folium/Leaflet. All functions return the map object
so you can chain: create_base_map(...) → add layers → display in Quarto.
"""

import folium
import json
import geopandas as gpd


# --- Tile presets ---------------------------------------------------------- #

TILES = {
    "positron": "CartoDB positron",
    "dark": "CartoDB dark_matter",
    "osm": "OpenStreetMap",
    "satellite": "Esri.WorldImagery",
}


# --- Base map -------------------------------------------------------------- #

def create_base_map(center=None, zoom=10, tiles="positron", gdf=None):
    """Create a Folium base map.

    If a GeoDataFrame is passed via `gdf`, the map auto-centers on its bounds.
    Otherwise, supply `center` as [lat, lon].
    """
    if gdf is not None and center is None:
        bounds = gdf.to_crs(4326).total_bounds  # [minx, miny, maxx, maxy]
        center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]

    tile_name = TILES.get(tiles, tiles)
    m = folium.Map(location=center or [39.0, -98.0], zoom_start=zoom, tiles=tile_name)
    return m


# --- GeoDataFrame layer ---------------------------------------------------- #

def add_geodataframe_layer(m, gdf, name="Layer", tooltip_fields=None,
                           style=None, highlight=None, show=True):
    """Add a GeoDataFrame as a GeoJson layer with optional tooltips.

    Parameters
    ----------
    m : folium.Map
    gdf : GeoDataFrame
        Must have a geometry column and be in EPSG:4326.
    name : str
        Layer name shown in LayerControl.
    tooltip_fields : list[str] or None
        Column names to show on hover. None = no tooltip.
    style : dict or None
        Style dict, e.g. {"color": "#0ea5e9", "weight": 2, "fillOpacity": 0.3}.
    highlight : dict or None
        Highlight style on hover, e.g. {"weight": 4, "fillOpacity": 0.6}.
    show : bool
        Whether the layer is visible by default (True) or toggled off (False).
    """
    gdf = gdf.to_crs(4326)

    style_fn = None
    if style:
        style_fn = lambda feature, s=style: s

    highlight_fn = None
    if highlight:
        highlight_fn = lambda feature, h=highlight: h

    tooltip = None
    if tooltip_fields:
        tooltip = folium.GeoJsonTooltip(fields=tooltip_fields)

    folium.GeoJson(
        gdf,
        name=name,
        tooltip=tooltip,
        style_function=style_fn,
        highlight_function=highlight_fn,
        show=show,
    ).add_to(m)

    return m


# --- Point markers --------------------------------------------------------- #

def add_point_markers(m, df, lat_col="latitude", lon_col="longitude",
                      popup_col=None, tooltip_col=None, color="blue"):
    """Add circle markers from a DataFrame with lat/lon columns.

    Parameters
    ----------
    df : DataFrame
        Must contain latitude and longitude columns.
    popup_col : str or None
        Column name for click popup.
    tooltip_col : str or None
        Column name for hover tooltip.
    color : str
        Marker fill color.
    """
    for _, row in df.iterrows():
        popup = folium.Popup(str(row[popup_col]), max_width=300) if popup_col else None
        tip = str(row[tooltip_col]) if tooltip_col else None

        folium.CircleMarker(
            location=[row[lat_col], row[lon_col]],
            radius=6,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=popup,
            tooltip=tip,
        ).add_to(m)

    return m


# --- Photo popup builder --------------------------------------------------- #

def build_photo_popup(row, photo_url=None, photo_caption=None, max_width=420):
    """Build an HTML popup with optional photo for Folium markers.

    Parameters
    ----------
    row : dict-like
        Must contain 'name'. Optional: 'place_type'/'category', 'start_year',
        'end_year', 'description', 'url'.
    photo_url : str or None
        URL to a photo image. Hidden gracefully if broken.
    photo_caption : str or None
        Caption displayed below the photo.
    max_width : int
        Max width of the popup div in pixels.
    """
    name = row.get("name", "")
    html = f"<div style='min-width:280px; max-width:{max_width}px;'>"

    if photo_url:
        html += (
            "<img src='" + photo_url + "' "
            "style='width:100%; max-height:200px; object-fit:cover; "
            "border-radius:6px; margin-bottom:8px;' "
            "alt='" + name + "' "
            "onerror=\"this.style.display='none'\">"
        )
        if photo_caption:
            html += (
                "<div style='font-size:0.8em; color:#64748b; "
                f"margin-bottom:8px;'>{photo_caption}</div>"
            )

    html += f"<b style='font-size:1.1em;'>{name}</b><br>"

    ptype = row.get("place_type") or row.get("category")
    if ptype:
        html += f"<i style='color:#64748b;'>{ptype}</i><br>"

    sy = row.get("start_year")
    ey = row.get("end_year")
    if sy and ey:
        html += f"<span style='color:#0ea5e9;'>{sy} \u2013 {ey} CE</span><br>"

    desc = row.get("description")
    if desc:
        html += f"<br>{desc}"

    link = row.get("url")
    if link:
        html += (
            "<br><a href='" + link + "' target='_blank' "
            "style='color:#0ea5e9;'>More info \u2192</a>"
        )

    html += "</div>"
    return html


# --- Finalize -------------------------------------------------------------- #

def finalize_map(m):
    """Add LayerControl and return the map, ready for display."""
    folium.LayerControl().add_to(m)
    return m
