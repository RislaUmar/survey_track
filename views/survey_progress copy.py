import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
import pandas as pd
from io import BytesIO
from datetime import datetime
# ---- PAGE SETUP ----
st.set_page_config(page_title="HIES and TUS Progress", layout="wide")

# ---- DATA PATHS ----
island_data = "data/completion_island_all.dta"
psu_data = "data/completion_psu_all.dta"
all_samples = "data/progress_all.dta"

lq_ind_status = "data/lq_file_individual_status.dta"
file1 = "data/file1.dta"
file2 = "data/file2.dta"
tus = "data/tus.dta"

# TITLE
st.title("HIES and TUS Progress")

print(datetime.now())


fixed_time = datetime(2026,6,28 ,10,25,54)

st.markdown(
    f"***Last updated on: 📅 {fixed_time.strftime('%A, %d %B %Y %H:%M:%S')}***"
)
# SIDEBAR FILTERS
# QUARTERS
st.sidebar.header("Quarter Filter")

q1 = st.sidebar.checkbox("Quarter 1", value=True)
q2 = st.sidebar.checkbox("Quarter 2", value=True)

selected_quarters = []

if q1:
    selected_quarters.append("1")
if q2:
    selected_quarters.append("2")

if not q1 and not q2:
    selected_quarters.append("1")
    selected_quarters.append("2")

# Load data
@st.cache_data
def data_upload():
    df_island = pd.read_stata(island_data)
    df_psu = pd.read_stata(psu_data)
    df_sample = pd.read_stata(all_samples)

    
    #---------------------------------------#
    # rename and subset columns
    #---------------------------------------#

    #---------------------------------------#
    # ISLAND
    #---------------------------------------#
    df_island = df_island.rename(columns={
        "GHI_ISLAND_CODE": "ISLAND",
        "completed_HH": "COMPLETED HHs",
        "TUS_STATUS": "COMPLETED TUS",
        "completed_LQ": "COMPLETED LQs",
        "target": "TARGET",
        "completion_rate": "COMPLETION_RATE",
    })

    df_island = df_island[
        ["QUARTER", "ISLAND", "COMPLETED HHs", "COMPLETED TUS", "COMPLETED LQs", "TARGET",  "COMPLETION_RATE"]
    ]

    #---------------------------------------#
    # PSU / blocks
    #---------------------------------------#
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
            "QUARTER", "ISLAND", "BLOCKS", "COMPLETED HHs", "COMPLETED LQs", "TARGET",
            "COMPLETION_RATE", "TUS_STATUS", "TUS_MISSING", "INTERVIEWED LQ INDIVIDUALS",
            "TAB", "SUP"
        ]
    ]

    #---------------------------------------#
    # SAMPLE
    #---------------------------------------#
    df_sample = df_sample.rename(columns={
        "GHI_ISLAND_CODE": "ISLAND",
        "block": "BLOCKS",
        "nbslct": "SELECTED INDIVIDUALS",
        "total_ind_finished": "INTERVIEWED LQ INDIVIDUALS",
        "completed_LQ": "LQ_STATUS",
        "completed_LQ_ind": "COMPLETED_LQ_ind",
        "completed_LQ_listing": "COMPLETED_LQ_listing",
        "file1_status": "FILE1_STATUS",
        "file2_status": "FILE2_STATUS",
        "status_tus": "TUS_STATUS", 
        "interviewers" : "INTERVIEWERS",
        "supervisor" : "SUP",
        "PERSON_NAME":"TUS_PERSON_NAME",
        "PERSON_AGE":"TUS_PERSON_AGE",
        "PERSON_SEX":"TUS_PERSON_SEX"
    })
    
    df_sample = df_sample.sort_values(by="LQ_ID")
    df_sample = df_sample[["QUARTER", "ISLAND", "BLOCKS", "SELECTION",
                           "HOUSEHOLD_HD_ID", "HOUSEHOLD_KEY", 
                           "FILE1_STATUS", "FILE2_STATUS", "TUS_STATUS", 
                        #    "LQ_STATUS",
                           "LQ_ID","COMPLETED_LQ_ind","COMPLETED_LQ_listing",
                           "TUS_PERSON_NAME", "TUS_PERSON_AGE", "TUS_PERSON_SEX",
                           "SELECTED INDIVIDUALS", "INTERVIEWED LQ INDIVIDUALS", 
                           "INTERVIEWERS", "SUP"]]
    

    return df_island, df_psu, df_sample

# read data
df_island_og, df_psu_og , df_sample_og = data_upload()

df_island = df_island_og.copy()
df_psu = df_psu_og.copy()
df_sample = df_sample_og.copy()


if selected_quarters:
    df_island = df_island_og[
        df_island_og["QUARTER"].isin(selected_quarters)
    ].drop(columns="QUARTER").groupby("ISLAND", as_index=False, observed=True).sum(numeric_only=True)
    
    df_island["COMPLETION_RATE"] = ((df_island["COMPLETED HHs"] + df_island["COMPLETED LQs"] ) / df_island["TARGET"]) * 100
    df_psu = df_psu_og[
        df_psu_og["QUARTER"].isin(selected_quarters)
    ].sort_values(by=["QUARTER", "SUP"])
    
    df_sample = df_sample_og[
        df_sample_og["QUARTER"].isin(selected_quarters)
    ].sort_values(by=["QUARTER", "SELECTION", "FILE1_STATUS", "LQ_ID"])
    

def get_totals(df_i, df_p):
    target = df_i["TARGET"].sum()
    total_hh = df_i["COMPLETED HHs"].sum()
    total_lq = df_i["COMPLETED LQs"].sum()
    total_tus = df_i["COMPLETED TUS"].sum()
    total = total_hh + total_lq

    completion = (total / target) * 100 
    completion_tus = (total_tus / total_hh) * 100 
    return target, total_hh , total_lq, completion, total_tus, completion_tus

subheader = "All Quarters"
if len(selected_quarters) != 2:
    subheader = ",".join(selected_quarters)
    subheader = "Quarter " + subheader 


st.subheader(f"Summary for {subheader}")
target, total_hh , total_lq, completion, total_tus, completion_tus = get_totals(df_island, df_psu)
col1, col2, col3, col4 = st.columns(4)

col1.metric("TARGET", f"{target:,.0f}")
col2.metric("COMPLETED HHs", f"{total_hh:,.0f}")
col3.metric("COMPLETED LQs", f"{total_lq:,.0f}")
col4.metric("HIES COMPLETION RATE", f"{completion:.0f}%")

col1, col2, col3, col4 = st.columns(4)
col2.metric("COMPLETED TUS", f"{total_tus:.0f}")
col4.metric("TUS COMPLETION RATE", f"{completion_tus:.0f}%")

# ---- ISLAND SUMMARY ----
st.header("Island Summary")

island_event = st.dataframe(
    df_island,
    column_config={
        "COMPLETION_RATE": st.column_config.ProgressColumn(
            "COMPLETION",
            min_value=0,
            max_value=100,
            format="%d%%",
            width="medium",
            color="#4aac04da"
        )
    },
    hide_index=True,
    use_container_width=True,
    on_select="rerun",
    selection_mode="multi-row",
)

selected_rows = island_event.selection.rows
    
def download(df, name, label):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="LQ", index=False)

    excel_data = output.getvalue()

    st.download_button(
        label=label,
        data=excel_data,
        file_name=f"{name}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def color(row, files, comp_status, styles, name):
    if (files == comp_status[0]):
        tus_idx = row.index.get_loc(name)
        styles[tus_idx] = "background-color: lightgreen; color: black; font-weight: 600;"
    elif (files in comp_status[1:]):
        tus_idx = row.index.get_loc(name)
        styles[tus_idx] = "background-color: #FFD580; color: black; font-weight: 600;"
    elif (files == "Status Pending"):
        tus_idx = row.index.get_loc(name)
        styles[tus_idx] = "background-color: black; color: white; font-weight: 600;"
    elif str(files) != "nan":
        tus_idx = row.index.get_loc(name)
        styles[tus_idx] = "background-color: #ffb09c; color: black; font-weight: 600;"

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
            file2 = str(row["FILE2_STATUS"]).strip()
            tus = str(row["TUS_STATUS"]).strip()
            # lq_status  = str(row["LQ_STATUS"]).strip()
            lq_status_inds  = row["COMPLETED_LQ_ind"]
            lq_status_listing = str(row["COMPLETED_LQ_listing"]).strip()

            comp_status = ["Complete", "Partially complete (refused)", "Partially complete (unavailable)"]

            color(row, file1, comp_status, styles, "FILE1_STATUS")
            color(row, file2, comp_status, styles, "FILE2_STATUS")
            # color(row, lq_status, comp_status, styles, "LQ_STATUS")
            color(row, tus, comp_status, styles, "TUS_STATUS")
            color(row, lq_status_listing, comp_status, styles, "COMPLETED_LQ_listing")

            comp_status = [0]
            color(row, lq_status_inds, comp_status, styles, "COMPLETED_LQ_ind")
            
            
    except:
        pass

    return styles

if selected_rows:
    islands = df_island.iloc[selected_rows]["ISLAND"].tolist()
    print(islands)
    st.sidebar.header("Supervisor Filter")
    supervisors = [
        "HIES_SUP_01",
        "HIES_SUP_02",
        "HIES_SUP_03",
        "HIES_SUP_04",
        "HIES_SUP_05",
        "HIES_SUP_06",
        "HIES_SUP_07",
        "HIES_SUP_08",
        "HIES_SUP_09",
        "HIES_SUP_10",
        "HIES_SUP_11"
    ]
    
    supervisors_dict = {
        "HIES_SUP_01 - Nooh" : "HIES_SUP_01",
        "HIES_SUP_02 - Mary" : "HIES_SUP_02",
        "HIES_SUP_03 - Khalaf" : "HIES_SUP_03",
        "HIES_SUP_04 - Aroo" : "HIES_SUP_04",
        "HIES_SUP_05 - Habeeb" : "HIES_SUP_05",
        "HIES_SUP_06 - Mibu" : "HIES_SUP_06",        
        "HIES_SUP_07 - Ashham": "HIES_SUP_07",
        "HIES_SUP_08 - Rayan" : "HIES_SUP_08",
        "HIES_SUP_09 - Shaz" : "HIES_SUP_09",
        "HIES_SUP_10 - Adhila" : "HIES_SUP_10",
        "HIES_SUP_11 - Saaiga" : "HIES_SUP_11"
    }

    selected_sups = []

    for sup in supervisors_dict.keys():

        checked = st.sidebar.checkbox(sup, value=True, key=sup)

        if checked:
            selected_sups.append(supervisors_dict[sup])

    if selected_sups:
        df_psu = df_psu[df_psu["SUP"].isin(selected_sups)]

        to_filter = df_psu[["QUARTER", "BLOCKS"]]

        def df_filter(df, main_df):

            df = df.merge(
                main_df[["BLOCKS", "QUARTER"]].drop_duplicates(),
                on=["BLOCKS", "QUARTER"],
                how="inner"
            )
            return df
        
        df_sample = df_filter(df_sample, to_filter)
        
    

    df_filtered = df_psu[df_psu["ISLAND"].isin(islands)].copy()
    df_filtered = df_filtered.drop(columns=["ISLAND"])
    st.header("Progress by Blocks")

    main_cols = ["BLOCKS", "QUARTER", "COMPLETED HHs", "COMPLETED LQs", "TARGET", "COMPLETION_RATE"]
    optional_cols = [
        # "FILE1_STATUS",
        # "FILE2_STATUS",
        "TUS_MISSING",
        # "TUS_STATUS",
        "INTERVIEWED LQ INDIVIDUALS",
        "TAB",
        "SUP"
    ]

    df_psu_display = df_filtered[main_cols + optional_cols].copy()
    search_text = st.text_input(
            "Filter block table",
            placeholder="Type to filter......"
        )

    df_psu_display_view = df_psu_display.copy()
    if search_text:
        mask = df_psu_display_view.astype(str).apply(
            lambda row: row.str.contains(search_text, case=False, na=False).any(),
            axis=1
        )
        df_psu_display_view = df_psu_display_view[mask]
    
    styled_df = df_psu_display_view.style.apply(color_tus_if_less, flag=True,  axis=1)
    
    blocks_event = st.dataframe(
        styled_df,
        column_config={
            "BLOCKS": st.column_config.TextColumn(width="small"),

            "COMPLETED HHs": st.column_config.NumberColumn(format="%d"),
            "COMPLETED LQs": st.column_config.NumberColumn(format="%d"),
            "TARGET": st.column_config.NumberColumn(format="%d"),

            "COMPLETION_RATE": st.column_config.ProgressColumn(
                "COMPLETION",
                min_value=0,
                max_value=100,
                format="%d%%",
                width="large", 
                color="#4aac04da"
            ),

            # "FILE1_STATUS": st.column_config.NumberColumn(format="%d"),
            # "FILE2_STATUS": st.column_config.NumberColumn(format="%d"),
            # "TUS_STATUS": st.column_config.NumberColumn(format="%d"),
            
            "TUS_MISSING": st.column_config.NumberColumn(format="%d"),
            
            "INTERVIEWED LQ INDIVIDUALS": st.column_config.NumberColumn(
                "INTERVIEWED LQ\n INDIVIDUALS",
                    format="%d",
                    # width="medium",
                ),
        },
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
    )
    
    # download(styled_df, "Block Progress", "Download Block ProgressTable")
    # st.info("🔴 Red TUS cells = TUS form does not match HIES forms. Select a block to view details.")

    selected_block_rows = blocks_event.selection.rows
    if selected_block_rows:        
        
        blocks = df_psu_display_view.iloc[selected_block_rows]["BLOCKS"].tolist()
        # print(blocks)
        df_filtered_all = df_sample[df_sample["BLOCKS"].isin(blocks)].copy()

        st.subheader(f"Sample detail for Block : {blocks[0]}")
        search_text = st.text_input(
            "Filter sample table",
            placeholder="Type to filter......"
        )

        df_filtered_all_view = df_filtered_all.copy()
        if search_text:
            mask = df_filtered_all_view.astype(str).apply(
                lambda row: row.str.contains(search_text, case=False, na=False).any(),
                axis=1
            )
            df_filtered_all_view = df_filtered_all_view[mask]
        
        # def get_col_width(series, min_px=80, max_px=400):
        #     max_len = series.astype(str).map(len).max()
        #     return min(max(max_len * 10, min_px), max_px)

        # block_width = get_col_width(df_filtered_all_view["BLOCKS"])    
        column_config = {}

        for col in df_filtered_all_view.columns:

            max_len = df_filtered_all_view[col].astype(str).map(len).max()

            width = min(max(max_len * 10, 80), 400)

            if width < 120:
                size = "small"
            elif width < 220:
                size = "medium"
            else:
                size = "large"

            column_config[col] = size
        styled_sample =  df_filtered_all_view.style.apply(color_tus_if_less,  axis=1)

        
        st.dataframe(
            styled_sample,
            column_config={
                "TUS_PERSON_AGE": st.column_config.NumberColumn(format="%d"),
                "LQ_ID": st.column_config.TextColumn(width=column_config["LQ_ID"]),
                "COMPLETED_LQ_ind": st.column_config.NumberColumn(format="%d"),
                "SELECTED INDIVIDUALS": st.column_config.NumberColumn(format="%d"),
                "INTERVIEWED LQ INDIVIDUALS": st.column_config.NumberColumn(format="%d")
                },
            # column_config=column_config,
            use_container_width=True,
            hide_index=True
            )
        
else:
    st.info("Select one or more islands to see Progress by Blocks.")

    