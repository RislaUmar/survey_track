import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd

st.title("Time Use Survey Summary")

tus_s_data ="data//all_person_s.dta"
tus_w_data = "data/all_weekday.dta"

@st.cache_data
def data_upload():
    df_tus_s = pd.read_stata(tus_s_data)
    df_tus_w = pd.read_stata(tus_w_data)

    islands = df_tus_s["GHI_ISLAND_CODE"].unique().tolist()
    islands.remove("All")
    return df_tus_s , df_tus_w, islands


df_tus_s , df_tus_w, islands= data_upload()

# initialize once
if "select_all" not in st.session_state:
    st.session_state.select_all = True

if "selected_options" not in st.session_state:
    st.session_state.selected_options = islands.copy()


def toggle_select_all():
    if st.session_state.select_all:
        st.session_state.selected_options = islands.copy()
    else:
        st.session_state.selected_options = []


def update_select_all():
    st.session_state.select_all = (
        len(st.session_state.selected_options) == len(islands)
    )


st.checkbox(
    "Select all",
    key="select_all",
    on_change=toggle_select_all,
)

import streamlit as st

def apply_custom_css(css_dict):
    css = "<style>"
    for selector, rules in css_dict.items():
        css += f"{selector} {{"
        for prop, value in rules.items():
            css += f"{prop}: {value};"
        css += "}"
    css += "</style>"
    st.markdown(css, unsafe_allow_html=True)


custom_css = {
    'div[data-baseweb="select"] > div': {
        "background-color": "#4F4F4D",
        "border": "2px solid gray",
    },
    'span[data-baseweb="tag"]': {
        "background-color": "#F5F5F5",
        "color": "black",
        "font-weight":"bold"
    },
    'div[role="listbox"]': {
        "background-color": "#262730",
    }
}


selected = st.multiselect(
    "Choose:",
    islands,
    key="selected_options",
    on_change=update_select_all,
)

apply_custom_css(custom_css)
df_s_filtered = df_tus_s[df_tus_s["GHI_ISLAND_CODE"].isin(selected)]
selected.append("")
df_w_filtered = df_tus_w[df_tus_w["GHI_ISLAND_CODE"].isin(selected)]

# ISLAND LEVEL TABLE
p1,p2= st.columns([1,2])
   
if len(df_s_filtered) > 0:
    fig = px.pie(
        df_s_filtered,
        names="TU_PERSON_SEX",
        values="n",
        color="TU_PERSON_SEX"
    )

    fig.update_traces(
        textinfo="percent+label",
        textfont_size=14,
        hole=0.4
    )

    fig.update_layout(
        title={
            "text": "Category Distribution",
            "x": 0.3,
            "xanchor": "center",
            "font": {"size": 22}
        },
        annotations=[
            dict(
                text="Categories",
                x=0.5,
                y=0.5,
                showarrow=False,
                font_size=16
            )
        ],
        legend_title_text="Category"
    )
    with p1:
        st.plotly_chart(fig, use_container_width=True)

    df_bar = df_w_filtered.groupby("TU_WDAY")["n"].sum().reset_index()
    df_bar = df_bar.sort_values("n", ascending=False)
    color_map = {
        "Sunday":    "#f1efbd",
        "Monday":    "#f1efbd",
        "Tuesday":   "#f1efbd",
        "Wednesday": "#e9f1b9",
        "Thursday":  "#dff3b7",
        "Friday":    "#d3f6b6",
        "Saturday":  "#c5f9b7"
    }
    
    fig = px.bar(
        df_bar,
        x="TU_WDAY",
        y="n",
        color="TU_WDAY",
        text="n",
        color_discrete_map=color_map
    )
    fig.update_traces(
        textposition="outside",
        marker_line_color="#333333",
        marker_line_width=1     
    )
    fig.update_layout(
        title={
            "text": "Weekday Distribution",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 22}
        },
        xaxis_title="Category",
        yaxis_title="Count",
        showlegend=False
    )
    with p2:
        st.plotly_chart(fig, use_container_width=True)