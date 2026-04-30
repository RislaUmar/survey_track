import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

import matplotlib.pyplot as plt
import pandas as pd

# ---- 1. DATA LOADING ----#
#  Data file path
island_data = "data/completion_island.dta"
psu_data = "data/completion_psu.dta"

# Page title
st.title("HIES and TUS Progress")

# To read and cache loaded dataset
@st.cache_data
def data_upload():
    df_island = pd.read_stata(island_data)
    df_psu = pd.read_stata(psu_data)
    return df_island, df_psu


df_island, df_psu = data_upload()

total = df_island[df_island["GHI_ISLAND_CODE"]=="All"]["all_completed"].sum()

df_island = df_island.drop(columns=["all_completed"])

# ---- ISLAND LEVEL TABLE SETUP ----#
def build_tables(df, main=True):
    gd = GridOptionsBuilder.from_dataframe(df)

    # page or scrolling
    pagination = True
    gd.configure_pagination(enabled=pagination)

    # Allow text filtering
    gd.configure_default_column(filter="agTextColumnFilter",sortable=True, resizable = True)

    # allow selection# select multiple or single
    if main:
        sel_mode = "multiple"
        gd.configure_selection(selection_mode=sel_mode, use_checkbox=True)

    # Build grid table
    grid_options = gd.build()

    max_rows_visible = min(10, max(len(df),3))
    row_height = 45
    header_height = 30
    
    height = header_height + (max_rows_visible * row_height)

    return grid_options, height

# generate grid configs
grid_options, height = build_tables(df_island)

# custom css design
custom_css = { 
    ".ag-row-selected": { "background-color": "#FFCCCB" }, 
    ".ag-root-wrapper": { "border": "2px solid gray !important" }, 
    ".ag-header": { "border-bottom": "2px solid gray !important", }, 
    ".ag-header-cell": { "border-left": "1px solid gray !important", }, 
    ".ag-cell": { "border-left": "1px solid gray !important", 
                "border-bottom": "1px solid gray !important", }
}  

# ISLAND LEVEL TABLE
left, center, right = st.columns([1, 4, 1])  # adjust ratios
    
with center:
    grid_table = AgGrid(
        df_island,
        gridOptions=grid_options,
        update_on=["selectionChanged"],
        allow_unsafe_jscode=True, 
        height=height,
        fit_columns_on_grid_load=False,
        custom_css=custom_css
    )
# selected rows
sel_row = grid_table["selected_rows"]
st.dataframe(df_island)
AgGrid(df_island)
# ---- PSU LEVEL TABLE SETUP ----#
# allow blocks of selected islands to be shown
if sel_row is not None:
    islands = sel_row["GHI_ISLAND_CODE"].tolist()
    
    df_filtered = df_psu[df_psu["GHI_ISLAND_CODE"].isin(islands)].copy()
    df_filtered = df_filtered.drop(columns=["GHI_ISLAND_CODE", "interviewers"])

    grid_options_psu, height_psu = build_tables(df_filtered)
    custom_css_psu = { 
        # borders
        ".ag-root-wrapper": { "border": "2px solid gray !important" }, 
        ".ag-header": { "border-bottom": "2px solid gray !important"}, 
        ".ag-header-cell": { "border-left": "1px solid gray !important"}, 
        ".ag-cell": { "border-left": "1px solid gray !important", "border-bottom": "1px solid gray !important", },
        ".ag-header-cell": { "background-color": "#fffff4", "color": "black", "font-weight": "bold", }, 
        ".ag-row": { "background-color": "#fffff4" }, 
        ".ag-body-viewport": {
            "background-color": "#fffff4", 
        },
        ".ag-root-wrapper": { "background-color": "#fffff4", "border": "2px solid black !important" },
        ".ag-row-hover": {
            "background-color": "#FFFFE0 !important",  # hover color
        },
        ".ag-row-selected": { "background-color": "#F3F699" }, 
    }  
    
    left, center, right = st.columns([1, 4, 1])  # adjust ratios
    
    with center:
        grid_table_block = AgGrid(
            df_filtered,
            gridOptions=grid_options_psu,
            update_on=["selectionChanged"],
            allow_unsafe_jscode=True, 
            height=height_psu,
            fit_columns_on_grid_load=False,
            custom_css=custom_css_psu,
            width=75
        )
