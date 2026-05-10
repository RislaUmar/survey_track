import streamlit as st
import pandas as pd

df = pd.read_stata("data/status.dta")
df = df.rename(
    columns={
        "status":"STATUS",
        "form":"QUESTIONNAIRE",
        "block":"BLOCK"
    }
)

# ---- PAGE SETUP ----
st.title("HIES and TUS Status Summary")

pivot_df = df.pivot_table(
    index="BLOCK",
    columns=["STATUS", "QUESTIONNAIRE"],
    values="obs",
    aggfunc="sum",
    fill_value=0,
    observed=False,
)

pivot_df = pivot_df.astype(int)

valid_cols = (
    df.groupby(["STATUS", "QUESTIONNAIRE"], observed=False)["obs"]
      .size()
      .loc[lambda x: x > 0]
      .index
)

pivot_df = pivot_df.loc[:, pivot_df.columns.isin(valid_cols)]
pivot_df = pivot_df.sort_index(axis=1, level=[0, 1])

html = pivot_df.to_html(classes="pivot-table", border=0)

visible_cols = list(pivot_df.columns)

first_status_cols = []
prev_status = None

for i, (status, form) in enumerate(visible_cols):
    if status != prev_status:
        first_status_cols.append(i + 2)
    prev_status = status

status_border_css = ""
for col in first_status_cols:
    status_border_css += f"""

    .pivot-table tbody td:nth-child({col}) {{
        border-left: 3px solid #999 !important;
    }}

    .pivot-table thead tr:nth-child(2) th:nth-child({col}) {{
        border-left: 3px solid #999 !important;
    }}

    .pivot-table thead tr:nth-child(3) th:nth-child({col}) {{
        border-left: 3px solid #999 !important; 

    }}

    """

st.markdown(
    f"""
<style>
.table-wrap {{
    max-height: 650px;
    max-width: 100%;
    overflow: auto;
    border: 1px solid #bdbdbd;
    border-radius: 6px;
}}

.pivot-table {{
    border-collapse: separate;
    border-spacing: 0;
    width: max-content;
    min-width: 100%;
    font-size: 14px;
}}

.pivot-table th,
.pivot-table td {{
    padding: 7px 11px;
    white-space: nowrap;
    text-align: center;
    border-right: 1px solid #d6d6d6;
    border-bottom: 1px solid #d6d6d6;
}}

.pivot-table thead th {{
    position: sticky;
    background: #eeeeee !important;
    color: #111;
    font-weight: 700;
    z-index: 4;
    
}}

.pivot-table tbody tr {{
    background: #eeeeee !important;
    color: #111;
    font-weight: 700;
    z-index: 4;
    border-bottom: 3px solid #d6d6d6;
    
}}

.pivot-table thead tr:nth-child(1) th {{
    top: 0;
}}

/* left borders for TOP STATUS ROW */
.pivot-table thead tr:nth-child(1) th:not(:first-child) {{

    box-shadow:
        inset 3px 0 0 #999,
        inset 0 -1px 0 #999 !important;
}}

.pivot-table thead tr:nth-child(2) th {{
    top: 35px;
}}

.pivot-table thead tr:nth-child(3) th,
.pivot-table thead tr:last-child th {{
    top: 70px;
    box-shadow: inset 0 -2px 0 #777;
    border-bottom: 3px solid #d6d6d6;
}}

.pivot-table tbody th {{
    position: sticky;
    left: 0;
    text-align: left;
    background: #f3f3f3 !important;
    font-weight: 600;
    z-index: 3;
    border-right: 2px solid #999;
}}

.pivot-table thead th:first-child {{
    position: sticky;
    left: 0;
    z-index: 6;
    text-align: left;
    background: #eeeeee !important;
    border-right: 2px solid #999;
}}

.pivot-table td {{
    background: white;
}}

.pivot-table tbody tr:hover td,
.pivot-table tbody tr:hover th {{
    background: #f8f8f8 !important;
}}

{status_border_css}

</style>

<div class="table-wrap">
    {html}
</div>
""",
    unsafe_allow_html=True
)