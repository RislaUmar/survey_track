import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

import matplotlib.pyplot as plt
import pandas as pd

# ---- 1. DATA LOADING ----#
#  Data file path
island_data = "data/completion_island_all.dta"
psu_data = "data/completion_psu_all.dta"

# Page title
st.title("HIES and TUS Progress")

# To read and cache loaded dataset
@st.cache_data
def data_upload():
    df_island = pd.read_stata(island_data)
    df_psu = pd.read_stata(psu_data)

    df_island = df_island.rename(columns={"GHI_ISLAND_CODE": "ISLAND",
                                          "nbslct":"SELECTED INDIVIDUALS", 
                                          "total_finished":"INTERVIEWED INDIVIDUALS",
                                          "completed":"COMPLETED LQs"})
    df_psu = df_psu.rename(columns={"GHI_ISLAND_CODE": "ISLAND",
                                    "block": "BLOCK",
                                    "nbslct":"SELECTED INDIVIDUALS", 
                                    "total_finished":"INTERVIEWED INDIVIDUALS",
                                     "completed":"COMPLETED LQs"})
    
    return df_island, df_psu

def total_hh_lq(df):
    return df[df["ISLAND"]!="All"]["FILE1_STATUS"].sum(), df["COMPLETED LQs"].sum()


df_island, df_psu = data_upload()
df_island = df_island.drop(columns=["all_completed"])

total_hh , total_lq  = total_hh_lq(df_island)

# ---- ISLAND LEVEL TABLE SETUP ----#
def build_tables(df, main=True):
    gd = GridOptionsBuilder.from_dataframe(df)

    gd.configure_pagination(enabled=main)

    gd.configure_default_column(
        filter="agTextColumnFilter",
        sortable=True,
        resizable=True,
        wrapHeaderText=True,
        autoHeaderHeight=True,
        minWidth=120
    )

    for col in df.columns:
        gd.configure_column(col, minWidth=120)

    # optional: make first column sticky
    if len(df.columns) > 0:
        gd.configure_column(df.columns[0], pinned="left", minWidth=120)
    for col in ["SELECTED INDIVIDUALS", "INTERVIEWED INDIVIDUALS", "COMPLETED LQs"]:
        gd.configure_column(
            col, 
            cellStyle={"backgroundColor":"#e7f8d5"}, 
            headerStyle={"backgroundColor":"#dcfbbb"}
        )
    for col in ["FILE1_STATUS", "FILE2_STATUS", "TUS_STATUS"]:
        gd.configure_column(
            col, 
            cellStyle={"backgroundColor":"#cae8f3"}, 
            headerStyle={"backgroundColor":"#a1eefe"}
        )
    if main:
        gd.configure_selection(selection_mode="multiple", use_checkbox=True)

    grid_options = gd.build()

    grid_options["domLayout"] = "normal"
    grid_options["suppressHorizontalScroll"] = False
    grid_options["alwaysShowHorizontalScroll"] = True

    max_rows_visible = min(10, max(len(df), 3))
    height = 30 + max_rows_visible * 50

    return grid_options, height

# generate grid configs
grid_options, height = build_tables(df_island)

# custom css design
custom_css = { 
    ".ag-row-selected .ag-cell": { "background-color": "#FFCCCB !important" }, 
     ".ag-row-hover .ag-cell": {
            "background-color": "#ffdadb !important",
     },
    ".ag-root-wrapper": { "border": "2px solid gray !important" }, 
    ".ag-header": { "border-bottom": "2px solid gray !important", }, 
    ".ag-header-cell": { "border-left": "1px solid gray !important", }, 
    ".ag-cell": { "border-left": "1px solid gray !important", 
                "border-bottom": "1px solid gray !important", }
}  

# ISLAND LEVEL TABLE
st.subheader("Island Summary")
grid_table = AgGrid(

    df_island,

    gridOptions=grid_options,

    update_on=["selectionChanged"],

    allow_unsafe_jscode=True,

    height=height,

    fit_columns_on_grid_load=False,

    custom_css=custom_css,

    theme="streamlit")

# selected rows
sel_row = grid_table["selected_rows"]

# ---- PSU LEVEL TABLE SETUP ----#
# allow blocks of selected islands to be shown
if sel_row is not None:
    islands = sel_row["ISLAND"].tolist()
    
    df_filtered = df_psu[df_psu["ISLAND"].isin(islands)].copy()
    df_filtered_is = df_island[df_island["ISLAND"].isin(islands)].copy()
    df_filtered = df_filtered.drop(columns=["ISLAND"])
    total_hh, total_lq = total_hh_lq(df_filtered_is)

    grid_options_psu, height_psu = build_tables(df_filtered, False)
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
        ".ag-row-hover .ag-cell": {
            "background-color": "#F3F699 !important",
        },
        ".ag-row-selected .ag-cell": { "background-color": "#F3F699 !important" }, 
    }  
    
    st.subheader("Block Summary")
    grid_table_block = AgGrid(

        df_filtered,

        gridOptions=grid_options_psu,

        update_on=["selectionChanged"],

        allow_unsafe_jscode=True,

        height=height_psu,

        fit_columns_on_grid_load=False,

        custom_css=custom_css_psu,
        
        theme="streamlit")
