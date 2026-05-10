import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
import pandas as pd
from io import BytesIO

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

    # rename and subset columns
    df_island = df_island.rename(columns={
        "GHI_ISLAND_CODE": "ISLAND",
        "completed_HH": "COMPLETED HHs",
        "completed_LQ": "COMPLETED LQs",
        "target": "TARGET",
        "completion_rate": "COMPLETION_RATE",
    })

    df_island = df_island[
        ["QUARTER", "ISLAND", "COMPLETED HHs", "COMPLETED LQs", "TARGET", "COMPLETION_RATE"]
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
            "QUARTER", "ISLAND", "BLOCKS", "COMPLETED HHs", "COMPLETED LQs", "TARGET",
            "COMPLETION_RATE", "TUS_MISSING", "INTERVIEWED LQ INDIVIDUALS",
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
    
    df_sample["LQ_STATUS"] = df_sample["LQ_STATUS"].map({1: "Complete", 0: "Incomplete"}).fillna(df_sample["LQ_STATUS"])
    df_sample = df_sample.sort_values(by="LQ_ID")
    df_sample = df_sample[["QUARTER", "ISLAND", "BLOCKS",
                           "HOUSEHOLD_HD_ID", "HOUSEHOLD_KEY", "LQ_ID",
                           "FILE1_STATUS", "FILE2_STATUS", "TUS_STATUS", "LQ_STATUS",
                           "TUS_PERSON_NAME", "TUS_PERSON_AGE", "TUS_PERSON_SEX",
                           "SELECTED INDIVIDUALS", "INTERVIEWED LQ INDIVIDUALS", 
                           "INTERVIEWERS", "SUP"]]
    
    df_lq = pd.read_stata(lq_ind_status)
    
    df_lq = df_lq.rename(columns={
        "obs1": "Complete",
        "obs2": "Partially complete (refused)",
        "obs3": "Partially complete (unavailable)",
        "obs4": "Unable to identify household",
        "obs5": "Long term unavailable",
        "obs6": "Refused",
        "obs7": "Not used",
        "obs97": "Status Pending",
        "obs96": "No, Unable to interview due to language",
        "block": "BLOCKS",
    })
    
    df_f1 = pd.read_stata(file1)
    df_f1 = df_f1.rename(columns={
        "obs1": "Complete",
        "obs2": "Partially complete (refused)",
        "obs3": "Partially complete (unavailable)",
        "obs4": "Unable to identify household",
        "obs5": "Long term unavailable",
        "obs6": "Refused",
        "obs7": "Not used",
        "obs8":  "Labour quarter with 10 or more inhabitants, no interview",
        "obs97": "Status Pending",
        "block": "BLOCKS",
    })
    
    df_f2 = pd.read_stata(file2)
    df_f2 = df_f2.rename(columns={
        "obs1": "Complete",
        "obs2": "Partially complete (refused)",
        "obs3": "Partially complete (unavailable)",
        "obs4": "Unable to identify household",
        "obs5": "Long term unavailable",
        "obs6": "Refused",
        "obs7": "Not used",
        "obs8":  "Labour quarter with 10 or more inhabitants, no interview",
        "obs97": "Status Pending",
        "block": "BLOCKS",
    })
    df_tus = pd.read_stata(tus)
    df_tus = df_tus.rename(columns={
        "obs1": "Complete",
        "obs93": "Individual Refused",
        "obs94": "Individual Unavailable",
        "obs95": "Invalid",
        "obs96":  "In Progress",
        "obs97": "Status Pending",
        "block": "BLOCKS",
    })


    return df_island, df_psu, df_sample, df_lq, df_f1, df_f2, df_tus

# read data
df_island_og, df_psu_og , df_sample_og, df_lq_og, df_f1_og, df_f2_og, df_tus_og = data_upload()

df_island = df_island_og.copy()
df_psu = df_psu_og.copy()
df_sample = df_sample_og.copy()
df_lq = df_lq_og.copy()
df_f1 = df_f1_og.copy()
df_f2 = df_f2_og.copy()
df_tus = df_tus_og.copy()


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
    ].sort_values(by=["QUARTER", "LQ_ID"])
    
    df_lq = df_lq_og[
        df_lq_og["QUARTER"].isin(selected_quarters)
    ].sort_values(by="QUARTER")

    df_f1 = df_f1_og[
        df_f1_og["QUARTER"].isin(selected_quarters)
    ].sort_values(by="QUARTER")

    df_f2 = df_f2_og[
        df_f2_og["QUARTER"].isin(selected_quarters)
    ].sort_values(by="QUARTER")

    df_tus = df_tus_og[
        df_tus_og["QUARTER"].isin(selected_quarters)
    ].sort_values(by="QUARTER")

def get_totals(df_i, df_p):
    target = len(df_p["BLOCKS"].unique()) * 16
    total_hh = df_i["COMPLETED HHs"].sum()
    total_lq = df_i["COMPLETED LQs"].sum()

    total = total_hh + total_lq

    completion = (total / target) * 100 
    return target, total_hh , total_lq, completion

target, total_hh , total_lq, completion = get_totals(df_island, df_psu)
col1, col2, col3, col4 = st.columns(4)

col1.metric("TARGET", f"{target:,.0f}")
col2.metric("COMPLETED HHs", f"{total_hh:,.0f}")
col3.metric("COMPLETED LQs", f"{total_lq:,.0f}")
col4.metric("COMPLETION RATE", f"{completion:.0f}%")

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
    elif files != "nan":
        print(files)
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
            lq_status  = str(row["LQ_STATUS"]).strip()
            comp_status = ["Complete", "Partially complete (refused)", "Partially complete (unavailable)"]
            
            color(row, file1, comp_status, styles, "FILE1_STATUS")
            color(row, file2, comp_status, styles, "FILE2_STATUS")
            color(row, lq_status, comp_status, styles, "LQ_STATUS")
            
    except:
        pass

    return styles

if selected_rows:
    islands = df_island.iloc[selected_rows]["ISLAND"].tolist()

    st.sidebar.header("Supervisor Filter")
    supervisors = [
        "HIES_SUP_01",
        "HIES_SUP_02",
        "HIES_SUP_03",
        "HIES_SUP_04",
        "HIES_SUP_05",
        "HIES_SUP_06",
    ]
    selected_sups = []

    for sup in supervisors:

        checked = st.sidebar.checkbox(sup, value=True, key=sup)

        if checked:
            selected_sups.append(sup)

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
        
        df_lq = df_filter(df_lq, to_filter)
        df_f1 = df_filter(df_f1, to_filter)
        df_f2 = df_filter(df_f2, to_filter)
        df_tus = df_filter(df_tus, to_filter)
        df_sample = df_filter(df_sample, to_filter)
        
    

    df_filtered = df_psu[df_psu["ISLAND"].isin(islands)].copy()
    df_filtered = df_filtered.drop(columns=["ISLAND"])

    st.header("Progress by Blocks")

    main_cols = ["BLOCKS", "QUARTER", "COMPLETED HHs", "COMPLETED LQs", "TARGET", "COMPLETION_RATE"]
    optional_cols = [
        # "FILE1_STATUS",
        # "FILE2_STATUS",
        # "TUS_STATUS",
        "TUS_MISSING",
        "INTERVIEWED LQ INDIVIDUALS",
        "INTERVIEWERS",
        "SUP"
    ]

    df_psu_display = df_filtered[main_cols + optional_cols].copy()

    styled_df = df_psu_display.style.apply(color_tus_if_less, flag=True,  axis=1)
    
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
    
    download(styled_df, "Block Progress", "Download Block ProgressTable")
    st.info("🔴 Red TUS cells = TUS form does not match HIES forms. Select a block to view details.")

    selected_block_rows = blocks_event.selection.rows
    if selected_block_rows:
        blocks = df_psu_display.iloc[selected_block_rows]["BLOCKS"].tolist()

        df_filtered_all = df_sample[df_sample["BLOCKS"].isin(blocks)].copy()

        st.subheader(f"Sample detail for Block : {blocks[0]}")

        styled_sample =  df_filtered_all.style.apply(color_tus_if_less,  axis=1)
        st.dataframe(
            styled_sample,
            column_config={
                "TUS_PERSON_AGE": st.column_config.NumberColumn(format="%d"),
                "LQ_ID": st.column_config.NumberColumn(format="%d")},
                
            hide_index=True
            )
        
else:
    st.info("Select one or more islands to see Progress by Blocks.")
 