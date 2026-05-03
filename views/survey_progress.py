import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
import pandas as pd

# ---- PAGE SETUP ----
st.set_page_config(page_title="HIES and TUS Progress", layout="wide")

# ---- DATA PATHS ----
island_data = "data/completion_island_all.dta"
psu_data = "data/completion_psu_all.dta"
all_samples = "data/progress_all.dta"

st.title("HIES and TUS Progress")

# Load data
@st.cache_data
def data_upload():
    df_island = pd.read_stata(island_data)
    df_psu = pd.read_stata(psu_data)
    df_sample = pd.read_stata(all_samples)

    # rename and subset columns
    df_island = df_island.rename(columns={
        "GHI_ISLAND_CODE": "ISLAND",
        "completed_HH": "COMPLETED HHs",
        "completed_LQ": "COMPLETED LQs",
        "target": "TARGET",
        "completion_rate": "COMPLETION_RATE",
    })

    df_island = df_island[
        ["ISLAND", "COMPLETED HHs", "COMPLETED LQs", "TARGET", "COMPLETION_RATE"]
    ]

    df_psu = df_psu.rename(columns={
        "GHI_ISLAND_CODE": "ISLAND",
        "completed_HH": "COMPLETED HHs",
        "block": "BLOCKS",
        "nbslct": "SELECTED INDIVIDUALS",
        "total_ind_finished": "INTERVIEWED LQ INDIVIDUALS",
        "completed_LQ": "COMPLETED LQs",
        "target": "TARGET",
        "completion_rate": "COMPLETION_RATE",
        "interviewers" : "INTERVIEWERS",
        "supervisors" : "SUP"
    })

    df_psu = df_psu[
        [
            "ISLAND", "BLOCKS", "COMPLETED HHs", "COMPLETED LQs", "TARGET",
            "COMPLETION_RATE", "FILE1_STATUS", "FILE2_STATUS", "TUS_STATUS", "INTERVIEWED LQ INDIVIDUALS",
            "INTERVIEWERS", "SUP"
        ]
    ]

    df_sample = df_sample.rename(columns={
        "GHI_ISLAND_CODE": "ISLAND",
        "block": "BLOCKS",
        "nbslct": "SELECTED INDIVIDUALS",
        "total_ind_finished": "INTERVIEWED LQ INDIVIDUALS",
        "completed_LQ": "LQ_STATUS",
        "file1_status": "FILE1_STATUS",
        "file2_status": "FILE2_STATUS",
        "status_tus": "TUS_STATUS", 
        "interviewers" : "INTERVIEWERS",
        "supervisor" : "SUP",
        "PERSON_NAME":"TUS_PERSON_NAME",
        "PERSON_AGE":"TUS_PERSON_AGE",
        "PERSON_SEX":"TUS_PERSON_SEX"
    })

    df_sample = df_sample[["ISLAND", "BLOCKS",
                           "HOUSEHOLD_HD_ID", "HOUSEHOLD_KEY", "LQ_ID",
                           "FILE1_STATUS", "FILE2_STATUS", "TUS_STATUS", "LQ_STATUS",
                           "TUS_PERSON_NAME", "TUS_PERSON_AGE", "TUS_PERSON_SEX",
                           "SELECTED INDIVIDUALS", "INTERVIEWED LQ INDIVIDUALS", 
                           "INTERVIEWERS", "SUP"]]
    return df_island, df_psu, df_sample

# read data
df_island, df_psu , df_sample= data_upload()

def get_totals(df_i, df_p):
    target = len(df_p["BLOCKS"].unique()) * 16
    total_hh = df_i["COMPLETED HHs"].sum()
    total_lq = df_i["COMPLETED LQs"].sum()

    total = total_hh + total_lq

    completion = (total / target) * 100 
    return target, total_hh , total_lq, completion

target, total_hh , total_lq, completion = get_totals(df_island, df_psu)
col1, col2, col3, col4 = st.columns(4)

col1.metric("Target", f"{target:,.0f}")
col2.metric("Completed HHs", f"{total_hh:,.0f}")
col3.metric("Completed LQs", f"{total_lq:,.0f}")
col4.metric("Completion rATE", f"{completion:.0f}%")

def get_color_map(df):
    color_map = {
        "HIES_SUP_01": "#fde2e4",
        "HIES_SUP_02": "#e2f0cb",
        "HIES_SUP_03": "#cde7f0",
        "HIES_SUP_04": "#fff1c1",
        "HIES_SUP_05": "#d0f4de",
        "HIES_SUP_06": "#ffd6a5",
    }

    df = df[["BLOCKS", "SUP"]]
    df["colour"] = df["SUP"].map(color_map)
    color_map = dict(zip(df['BLOCKS'], df['colour']))
    return color_map

color_map = get_color_map(df_psu)

# ---- ISLAND SUMMARY ----
st.subheader("Island Summary")

island_event = st.dataframe(
    df_island,
    column_config={
        "COMPLETION_RATE": st.column_config.ProgressColumn(
            "COMPLETION",
            min_value=0,
            max_value=100,
            format="%d%%",
            width="medium",
        )
    },
    hide_index=True,
    use_container_width=True,
    on_select="rerun",
    selection_mode="multi-row",
    # height=500,
)

selected_rows = island_event.selection.rows

def color_blocks(col): 
    return [
        f"background-color: {color_map.get(v, 'white')}"
        for v in col
    ]

def color_tus_if_less(row):
    styles = [""] * len(row)

    try:
        tus = int(row["TUS_STATUS"])
        file1 = int(row["COMPLETED HHs"])

        if tus != file1:
            tus_idx = row.index.get_loc("TUS_STATUS")
            styles[tus_idx] = "background-color: #ffcccc; color: black; font-weight: 600;"
    except:
        pass

    return styles

def color_tus_if_less(row, flag=False):
    styles = [""] * len(row)

    try:

        if flag:         
            tus = int(row["TUS_STATUS"])
            file1 = int(row["FILE1_STATUS"])
            if tus != file1:
                tus_idx = row.index.get_loc("TUS_STATUS")
                styles[tus_idx] = "background-color: #ffcccc; color: black; font-weight: 600;"
        else:
            file1 = str(row["FILE1_STATUS"]).strip()
            tus = str(row["TUS_STATUS"]).strip()
            if (file1 == "Complete" and tus != "Complete") | (file1 != "Complete" and tus == "Complete"):
                tus_idx = row.index.get_loc("TUS_STATUS")
                styles[tus_idx] = "background-color: #ffcccc; color: black; font-weight: 600;"
    except:
        pass

    return styles
 
if selected_rows:
    islands = df_island.iloc[selected_rows]["ISLAND"].tolist()

    df_filtered = df_psu[df_psu["ISLAND"].isin(islands)].copy()
    df_filtered = df_filtered.drop(columns=["ISLAND"])

    st.subheader("Progress by Blocks")

    legend_html = ""
    for sup, color in {
        "HIES_SUP_01": "#fde2e4",
        "HIES_SUP_02": "#e2f0cb",
        "HIES_SUP_03": "#cde7f0",
        "HIES_SUP_04": "#fff1c1",
        "HIES_SUP_05": "#d0f4de",
        "HIES_SUP_06": "#ffd6a5",
    }.items():
        legend_html += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background-color: {color};
                        border: 1px solid #999; margin-right: 8px;"></div>
            <span>{sup}</span>
        </div>
        """

    with st.expander("Show Supervisor Legend"):
        st.markdown(legend_html, unsafe_allow_html=True)
    
    main_cols = ["BLOCKS", "COMPLETED HHs", "COMPLETED LQs", "TARGET", "COMPLETION_RATE"]
    optional_cols = [
        "FILE1_STATUS",
        "FILE2_STATUS",
        "TUS_STATUS",
        "INTERVIEWED LQ INDIVIDUALS",
        "INTERVIEWERS",
        "SUP"
    ]

    df_psu_display = df_filtered[main_cols + optional_cols].copy()

    styled_df = df_psu_display.style.apply(
        color_blocks,
        subset=["BLOCKS"]
    ).apply(color_tus_if_less, flag=True,  axis=1)
    
    blocks_event = st.dataframe(
        styled_df,
        column_config={
            "BLOCKS": st.column_config.TextColumn(width="small"),

            "COMPLETED HHs": st.column_config.NumberColumn(format="%d", width="small"),
            "COMPLETED LQs": st.column_config.NumberColumn(format="%d", width="small"),
            "TARGET": st.column_config.NumberColumn(format="%d", width="small"),

            "COMPLETION_RATE": st.column_config.ProgressColumn(
                "COMPLETION",
                min_value=0,
                max_value=100,
                format="%d%%",
                width="large", 
            ),

            "FILE1_STATUS": st.column_config.NumberColumn(format="%d", width="small"),
            "FILE2_STATUS": st.column_config.NumberColumn(format="%d", width="small"),
            "TUS_STATUS": st.column_config.NumberColumn(format="%d", width="small"),
            
            "INTERVIEWED LQ INDIVIDUALS": st.column_config.NumberColumn(
                "INTERVIEWED LQ\n INDIVIDUALS",
                    format="%d",
                    width="small",
                ),
        },
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    
    selected_block_rows = blocks_event.selection.rows
    if selected_block_rows:
        blocks = df_psu_display.iloc[selected_block_rows]["BLOCKS"].tolist()

        df_filtered_all = df_sample[df_sample["BLOCKS"].isin(blocks)].copy()

        st.subheader(f"Sample detail for Block : {blocks[0]}")

        styled_sample =  df_filtered_all.style.apply(color_tus_if_less,  axis=1)
        st.dataframe(
            styled_sample,
            column_config={
                "TUS_PERSON_AGE": st.column_config.NumberColumn(format="%d")}
            )
        
else:
    st.info("Select one or more islands to see Progress by Blocks.")