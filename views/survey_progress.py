# import streamlit as st
# from st_aggrid import AgGrid
# from st_aggrid.grid_options_builder import GridOptionsBuilder
# from st_aggrid.shared import JsCode
# import pandas as pd

# # ---- DATA PATHS ----
# island_data = "data/completion_island_all.dta"
# psu_data = "data/completion_psu_all.dta"

# st.title("HIES and TUS Progress")


# @st.cache_data
# def data_upload():
#     df_island = pd.read_stata(island_data)
#     df_psu = pd.read_stata(psu_data)

#     df_island = df_island.rename(columns={
#         "GHI_ISLAND_CODE": "ISLAND",
#         "completed_HH": "COMPLETED HHs",
#         "completed_LQ": "COMPLETED LQs",
#         "target": "TARGET",
#         "completion_rate": "COMPLETION_RATE"
#     })

#     df_island = df_island[
#         ["ISLAND", "COMPLETED HHs", "COMPLETED LQs", "TARGET", "COMPLETION_RATE"]
#     ]

#     df_psu = df_psu.rename(columns={
#         "GHI_ISLAND_CODE": "ISLAND",
#         "completed_HH": "COMPLETED HHs",
#         "block": "BLOCKS",
#         "nbslct": "SELECTED INDIVIDUALS",
#         "total_ind_finished": "INTERVIEWED INDIVIDUALS",
#         "completed_LQ": "COMPLETED LQs",
#         "target": "TARGET",
#         "completion_rate": "COMPLETION_RATE"
#     })

#     df_psu = df_psu[
#         [
#             "ISLAND", "BLOCKS", "COMPLETED HHs", "COMPLETED LQs", "TARGET", "COMPLETION_RATE",
#             "FILE1_STATUS", "FILE2_STATUS", "TUS_STATUS",
#             "SELECTED INDIVIDUALS", "INTERVIEWED INDIVIDUALS"
#         ]
#     ]

#     for df in [df_island, df_psu]:
#         df["COMPLETION_RATE"] = pd.to_numeric(df["COMPLETION_RATE"], errors="coerce")
#         if df["COMPLETION_RATE"].max() <= 1:
#             df["COMPLETION_RATE"] = df["COMPLETION_RATE"] * 100

#     return df_island, df_psu


# df_island, df_psu = data_upload()


# progress_renderer = JsCode("""
# class ProgressCellRenderer {
#     init(params) {
#         const value = Number(params.value) || 0;

#         this.eGui = document.createElement('div');
#         this.eGui.style.width = '100%';
#         this.eGui.style.height = '20px';
#         this.eGui.style.background = '#eeeeee';
#         this.eGui.style.borderRadius = '10px';
#         this.eGui.style.overflow = 'hidden';
#         this.eGui.style.position = 'relative';

#         const bar = document.createElement('div');
#         bar.style.height = '100%';
#         bar.style.width = value + '%';
#         bar.style.background = '#ff8a8a';
#         bar.style.borderRadius = '10px';

#         const label = document.createElement('span');
#         label.innerText = value.toFixed(0) + '%';
#         label.style.position = 'absolute';
#         label.style.left = '50%';
#         label.style.top = '50%';
#         label.style.transform = 'translate(-50%, -50%)';
#         label.style.fontSize = '12px';
#         label.style.fontWeight = '600';
#         label.style.color = 'black';

#         this.eGui.appendChild(bar);
#         this.eGui.appendChild(label);
#     }

#     getGui() {
#         return this.eGui;
#     }
# }
# """)


# def build_aggrid(df, main=True):
#     gb = GridOptionsBuilder.from_dataframe(df)

#     gb.configure_pagination(
#         enabled=main,
#         paginationAutoPageSize=False,
#         paginationPageSize=10
#     )

#     gb.configure_default_column(
#         filter=True,
#         sortable=True,
#         resizable=True,
#         wrapHeaderText=True,
#         autoHeaderHeight=True,
#         minWidth=90,
#         cellStyle={
#             "textAlign": "center",
#             "display": "flex",
#             "alignItems": "center",
#             "justifyContent": "center"
#         }
#     )

#     SMALL = 105
#     MEDIUM = 140
#     LARGE = 220

#     first_col = df.columns[0]

#     for col in df.columns:
#         if col == first_col:
#             gb.configure_column(
#                 col,
#                 width=MEDIUM,
#                 pinned="left",
#                 cellStyle={
#                     "textAlign": "left",
#                     "display": "flex",
#                     "alignItems": "center",
#                     "justifyContent": "flex-start"
#                 }
#             )

#         elif col == "COMPLETION_RATE":
#             gb.configure_column(
#                 col,
#                 header_name="COMPLETION",
#                 cellRenderer=progress_renderer,
#                 width=LARGE
#             )

#         elif col in ["COMPLETED HHs", "COMPLETED LQs", "TARGET"]:
#             gb.configure_column(col, width=SMALL)

#         elif col in ["FILE1_STATUS", "FILE2_STATUS", "TUS_STATUS"]:
#             gb.configure_column(col, width=SMALL)

#         elif col in ["SELECTED INDIVIDUALS", "INTERVIEWED INDIVIDUALS"]:
#             gb.configure_column(col, width=SMALL)

#     if main:
#         gb.configure_selection(selection_mode="multiple", use_checkbox=True)

#     grid_options = gb.build()

#     grid_options["domLayout"] = "normal"
#     grid_options["suppressHorizontalScroll"] = False
#     grid_options["alwaysShowHorizontalScroll"] = True

#     height = 80 + min(10, max(len(df), 3)) * 45

#     return grid_options, height

# custom_css = {
#     ".ag-row-selected .ag-cell": {
#         "background-color": "#FFCCCB !important"
#     },
#     ".ag-row-hover .ag-cell": {
#         "background-color": "#ffdadb !important"
#     },
#     ".ag-root-wrapper": {
#         "border": "2px solid gray !important"
#     },
#     ".ag-header": {
#         "border-bottom": "2px solid gray !important"
#     },
#     ".ag-header-cell": {
#         "border-left": "1px solid gray !important"
#     },
#     ".ag-header-cell-label": {
#         "justify-content": "center !important"
#     },
#     ".ag-cell": {
#         "border-left": "1px solid gray !important",
#         "border-bottom": "1px solid gray !important"
#     }
# }


# # ---- ISLAND SUMMARY ----

# st.subheader("Island Summary")

# island_grid_options, island_height = build_aggrid(df_island, main=True)

# grid_table = AgGrid(
#     df_island,
#     gridOptions=island_grid_options,
#     update_on=["selectionChanged"],
#     allow_unsafe_jscode=True,
#     height=island_height,
#     fit_columns_on_grid_load=False,
#     custom_css=custom_css,
#     theme="streamlit"
# )


# # ---- PSU / REGION PROGRESS ----
# # selected rows
# sel_row = grid_table["selected_rows"]

# # ---- PSU LEVEL TABLE SETUP ----#
# # allow blocks of selected islands to be shown
# if sel_row is not None:
#     islands = sel_row["ISLAND"].tolist()
    
#     df_filtered = df_psu[df_psu["ISLAND"].isin(islands)].copy()
#     df_filtered_is = df_island[df_island["ISLAND"].isin(islands)].copy()
#     df_filtered = df_filtered.drop(columns=["ISLAND"])

#     main_cols = ["BLOCKS", "COMPLETED HHs", "COMPLETED LQs", "TARGET", "COMPLETION_RATE"]


#         # ---- PSU / REGION PROGRESS ----
#     st.subheader("Progress by Region")

#     main_cols = ["BLOCKS", "COMPLETED HHs", "COMPLETED LQs", "TARGET", "COMPLETION_RATE"]

#     optional_cols = [
#         "FILE1_STATUS", "FILE2_STATUS", "TUS_STATUS",
#         "SELECTED INDIVIDUALS", "INTERVIEWED INDIVIDUALS"
#     ]

#     df_psu_display = df_filtered[main_cols + optional_cols].copy()

#     df_psu_display["COMPLETION_RATE"] = pd.to_numeric(
#         df_psu_display["COMPLETION_RATE"],
#         errors="coerce"
#     )

#     if df_psu_display["COMPLETION_RATE"].max() <= 1:
#         df_psu_display["COMPLETION_RATE"] *= 100


#     psu_gb = GridOptionsBuilder.from_dataframe(df_psu_display)

#     psu_gb.configure_default_column(
#         filter=True,
#         sortable=True,
#         resizable=True,
#         wrapHeaderText=True,
#         autoHeaderHeight=True,
#         cellStyle={
#             "textAlign": "center",
#             "display": "flex",
#             "alignItems": "center",
#             "justifyContent": "center"
#         }
#     )

#     psu_gb.configure_column(
#         "BLOCKS",
#         width=120,
#         pinned="left",
#         cellStyle={
#             "textAlign": "left",
#             "display": "flex",
#             "alignItems": "center",
#             "justifyContent": "flex-start"
#         }
#     )

#     psu_gb.configure_column("COMPLETED HHs", width=170)
#     psu_gb.configure_column("COMPLETED LQs", width=170)
#     psu_gb.configure_column("TARGET", width=170)

#     psu_gb.configure_column(
#         "COMPLETION_RATE",
#         header_name="COMPLETION",
#         width=300,
#         cellRenderer=progress_renderer
#     )

#     psu_gb.configure_column("FILE1_STATUS", width=170)
#     psu_gb.configure_column("FILE2_STATUS", width=170)
#     psu_gb.configure_column("TUS_STATUS", width=170)
#     psu_gb.configure_column("SELECTED INDIVIDUALS", width=170)
#     psu_gb.configure_column("INTERVIEWED INDIVIDUALS", width=170)

#     psu_grid_options = psu_gb.build()

#     psu_grid_options["domLayout"] = "normal"
#     psu_grid_options["suppressHorizontalScroll"] = False
#     psu_grid_options["alwaysShowHorizontalScroll"] = True

#     AgGrid(
#         df_psu_display,
#         gridOptions=psu_grid_options,
#         allow_unsafe_jscode=True,
#         height=500,
#         fit_columns_on_grid_load=False,
#         custom_css=custom_css,
#         theme="streamlit"
#     )
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
import pandas as pd

# ---- PAGE SETUP ----
st.set_page_config(page_title="HIES and TUS Progress", layout="wide")

# Mobile-friendly Streamlit spacing
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.45rem;
            padding-right: 0.45rem;
        }
        h1 {
            font-size: 1.45rem !important;
            line-height: 1.2 !important;
        }
        h2, h3 {
            font-size: 1.05rem !important;
        }
        .ag-header-cell-text,
        .ag-cell {
            font-size: 11px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- DATA PATHS ----
island_data = "data/completion_island_all.dta"
psu_data = "data/completion_psu_all.dta"

st.title("HIES and TUS Progress")


@st.cache_data
def data_upload():
    df_island = pd.read_stata(island_data)
    df_psu = pd.read_stata(psu_data)

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
        "total_ind_finished": "INTERVIEWED INDIVIDUALS",
        "completed_LQ": "COMPLETED LQs",
        "target": "TARGET",
        "completion_rate": "COMPLETION_RATE",
    })

    df_psu = df_psu[
        [
            "ISLAND", "BLOCKS", "COMPLETED HHs", "COMPLETED LQs", "TARGET",
            "COMPLETION_RATE", "FILE1_STATUS", "FILE2_STATUS", "TUS_STATUS",
            "SELECTED INDIVIDUALS", "INTERVIEWED INDIVIDUALS",
        ]
    ]

    for df in [df_island, df_psu]:
        df["COMPLETION_RATE"] = pd.to_numeric(df["COMPLETION_RATE"], errors="coerce")
        if df["COMPLETION_RATE"].max() <= 1:
            df["COMPLETION_RATE"] = df["COMPLETION_RATE"] * 100

    return df_island, df_psu


df_island, df_psu = data_upload()


progress_renderer = JsCode(
    """
    class ProgressCellRenderer {
        init(params) {
            const value = Number(params.value) || 0;
            const safeValue = Math.max(0, Math.min(100, value));

            this.eGui = document.createElement('div');
            this.eGui.style.width = '100%';
            this.eGui.style.height = window.innerWidth < 768 ? '16px' : '20px';
            this.eGui.style.background = '#eeeeee';
            this.eGui.style.borderRadius = '10px';
            this.eGui.style.overflow = 'hidden';
            this.eGui.style.position = 'relative';

            const bar = document.createElement('div');
            bar.style.height = '100%';
            bar.style.width = safeValue + '%';
            bar.style.background = '#ff8a8a';
            bar.style.borderRadius = '10px';

            const label = document.createElement('span');
            label.innerText = value.toFixed(0) + '%';
            label.style.position = 'absolute';
            label.style.left = '50%';
            label.style.top = '50%';
            label.style.transform = 'translate(-50%, -50%)';
            label.style.fontSize = window.innerWidth < 768 ? '10px' : '12px';
            label.style.fontWeight = '600';
            label.style.color = 'black';

            this.eGui.appendChild(bar);
            this.eGui.appendChild(label);
        }

        getGui() {
            return this.eGui;
        }
    }
    """
)


def responsive_grid_js(optional_columns=None, first_column=None):
    optional_columns = optional_columns or []
    first_column = first_column or ""

    return JsCode(
        f"""
        function(params) {{
            function safeWidth(colId, width) {{
                try {{
                    if (params.columnApi && params.columnApi.setColumnWidth) {{
                        params.columnApi.setColumnWidth(colId, width);
                    }}
                }} catch(e) {{}}
            }}

            function applyResponsiveLayout() {{
                const isMobile = window.innerWidth < 768;
                const optionalCols = {optional_columns};
                const firstCol = "{first_column}";

                // On mobile, do NOT hide columns. Keep every column visible and allow horizontal scroll.
                if (params.columnApi && params.columnApi.setColumnsVisible && optionalCols.length > 0) {{
                    params.columnApi.setColumnsVisible(optionalCols, true);
                }} else if (params.api && params.api.setColumnsVisible && optionalCols.length > 0) {{
                    params.api.setColumnsVisible(optionalCols, true);
                }}

                // Pinned columns are awkward on phones; unpin only on mobile.
                if (params.columnApi && params.columnApi.applyColumnState && firstCol) {{
                    params.columnApi.applyColumnState({{
                        state: [{{ colId: firstCol, pinned: isMobile ? null : 'left' }}],
                        applyOrder: false
                    }});
                }}

                if (isMobile) {{
                    if (firstCol) safeWidth(firstCol, 95);
                    safeWidth('COMPLETED HHs', 95);
                    safeWidth('COMPLETED LQs', 95);
                    safeWidth('TARGET', 85);
                    safeWidth('COMPLETION_RATE', 155);
                    safeWidth('FILE1_STATUS', 105);
                    safeWidth('FILE2_STATUS', 105);
                    safeWidth('TUS_STATUS', 105);
                    safeWidth('SELECTED INDIVIDUALS', 125);
                    safeWidth('INTERVIEWED INDIVIDUALS', 130);
                }}
            }}

            applyResponsiveLayout();
            window.addEventListener('resize', applyResponsiveLayout);
        }}
        """
    )

def build_aggrid(df, main=True):
    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_pagination(
        enabled=main,
        paginationAutoPageSize=False,
        paginationPageSize=10,
    )

    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        wrapHeaderText=True,
        autoHeaderHeight=True,
        minWidth=75,
        cellStyle={
            "textAlign": "center",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
        },
    )

    SMALL = 105
    MEDIUM = 140
    LARGE = 220

    first_col = df.columns[0]

    for col in df.columns:
        if col == first_col:
            gb.configure_column(
                col,
                width=MEDIUM,
                pinned="left",
                cellStyle={
                    "textAlign": "left",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "flex-start",
                },
            )

        elif col == "COMPLETION_RATE":
            gb.configure_column(
                col,
                header_name="COMPLETION",
                cellRenderer=progress_renderer,
                width=LARGE,
                minWidth=130,
            )

        elif col in ["COMPLETED HHs", "COMPLETED LQs", "TARGET"]:
            gb.configure_column(col, width=SMALL, minWidth=75)

        elif col in ["FILE1_STATUS", "FILE2_STATUS", "TUS_STATUS"]:
            gb.configure_column(col, width=SMALL, minWidth=80)

        elif col in ["SELECTED INDIVIDUALS", "INTERVIEWED INDIVIDUALS"]:
            gb.configure_column(col, width=SMALL, minWidth=85)

    if main:
        gb.configure_selection(selection_mode="multiple", use_checkbox=True)

    grid_options = gb.build()
    grid_options["domLayout"] = "normal"
    grid_options["suppressHorizontalScroll"] = False
    grid_options["alwaysShowHorizontalScroll"] = True
    grid_options["onGridReady"] = responsive_grid_js(first_column=first_col)
    grid_options["onGridSizeChanged"] = responsive_grid_js(first_column=first_col)

    height = 80 + min(10, max(len(df), 3)) * 45

    return grid_options, height


custom_css = {
    ".ag-row-selected .ag-cell": {"background-color": "#FFCCCB !important"},
    ".ag-row-hover .ag-cell": {"background-color": "#ffdadb !important"},
    ".ag-root-wrapper": {"border": "2px solid gray !important"},
    ".ag-header": {"border-bottom": "2px solid gray !important"},
    ".ag-header-cell": {"border-left": "1px solid gray !important"},
    ".ag-header-cell-label": {"justify-content": "center !important"},
    ".ag-cell": {
        "border-left": "1px solid gray !important",
        "border-bottom": "1px solid gray !important",
    },
}


# ---- ISLAND SUMMARY ----
st.subheader("Island Summary")

island_grid_options, island_height = build_aggrid(df_island, main=True)

grid_table = AgGrid(
    df_island,
    gridOptions=island_grid_options,
    update_on=["selectionChanged"],
    allow_unsafe_jscode=True,
    height=island_height,
    fit_columns_on_grid_load=False,
    custom_css=custom_css,
    theme="streamlit",
)


# ---- PSU / REGION PROGRESS ----
sel_row = grid_table["selected_rows"]

if sel_row is not None:
    islands = sel_row["ISLAND"].tolist()

    df_filtered = df_psu[df_psu["ISLAND"].isin(islands)].copy()
    df_filtered = df_filtered.drop(columns=["ISLAND"])

    st.subheader("Progress by Region")

    main_cols = ["BLOCKS", "COMPLETED HHs", "COMPLETED LQs", "TARGET", "COMPLETION_RATE"]
    optional_cols = [
        "FILE1_STATUS", "FILE2_STATUS", "TUS_STATUS",
        "SELECTED INDIVIDUALS", "INTERVIEWED INDIVIDUALS",
    ]

    df_psu_display = df_filtered[main_cols + optional_cols].copy()

    df_psu_display["COMPLETION_RATE"] = pd.to_numeric(
        df_psu_display["COMPLETION_RATE"],
        errors="coerce",
    )

    if df_psu_display["COMPLETION_RATE"].max() <= 1:
        df_psu_display["COMPLETION_RATE"] *= 100

    psu_gb = GridOptionsBuilder.from_dataframe(df_psu_display)

    psu_gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        wrapHeaderText=True,
        autoHeaderHeight=True,
        minWidth=75,
        cellStyle={
            "textAlign": "center",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
        },
    )

    psu_gb.configure_column(
        "BLOCKS",
        width=120,
        minWidth=80,
        pinned="left",
        cellStyle={
            "textAlign": "left",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "flex-start",
        },
    )

    psu_gb.configure_column("COMPLETED HHs", width=120, minWidth=75)
    psu_gb.configure_column("COMPLETED LQs", width=120, minWidth=75)
    psu_gb.configure_column("TARGET", width=110, minWidth=75)

    psu_gb.configure_column(
        "COMPLETION_RATE",
        header_name="COMPLETION",
        width=230,
        minWidth=130,
        cellRenderer=progress_renderer,
    )

    for col in optional_cols:
        psu_gb.configure_column(col, width=150, minWidth=90)

    psu_grid_options = psu_gb.build()
    psu_grid_options["domLayout"] = "normal"
    psu_grid_options["suppressHorizontalScroll"] = False
    psu_grid_options["alwaysShowHorizontalScroll"] = True
    psu_grid_options["onGridReady"] = responsive_grid_js(
        optional_columns=optional_cols,
        first_column="BLOCKS",
    )
    psu_grid_options["onGridSizeChanged"] = responsive_grid_js(
        optional_columns=optional_cols,
        first_column="BLOCKS",
    )

    AgGrid(
        df_psu_display,
        gridOptions=psu_grid_options,
        allow_unsafe_jscode=True,
        height=500,
        fit_columns_on_grid_load=False,
        custom_css=custom_css,
        theme="streamlit",
    )
