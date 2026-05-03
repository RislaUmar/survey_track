# import streamlit as st
# # from forms.contact import contact_form
# st.title("About", anchor=False)
# # @st.dialog("Cast your vote")
# # def show_contact_form():
# #     contact_form()

# # # creat columns
# # col1, col2 = st.columns(2, gap="small", vertical_alignment="center")

# # with col1:
# #     st.image("./assets/bunny.jpg", width=230)
# # with col2:
# #     st.title("Mr.Bunny", anchor=False)
# #     st.write("Just existing")

# #     if st.button("✉️ Contact Me"):
# #         show_contact_form()

# # st.write("\n")
# # st.subheader("Profession", anchor=False)
# # st.write("Gardening")

# # st.write("\n")
# # st.subheader("Favorite Food", anchor=False)
# # st.write("Carrots")
# import streamlit as st
# import pandas as pd

# st.set_page_config(page_title="HIES Progress Dashboard", layout="wide")

# TARGET_PER_REGION = 16

# df = pd.DataFrame({
#     "Region": ["Region A", "Region B", "Region C", "Region D"],
#     "Completed": [4, 10, 16, 7],
# })

# df["Target"] = TARGET_PER_REGION
# df["Progress"] = df["Completed"] / df["Target"]
# df["Progress Label"] = df["Completed"].astype(str) + " / " + df["Target"].astype(str)


# def color_region_by_progress(row):
#     progress = row["Progress"]

#     if progress < 0.40:
#         color = "#f8d7da"   # light red
#     elif progress < 0.75:
#         color = "#fff3cd"   # light yellow
#     else:
#         color = "#d4edda"   # light green

#     return [
#         f"background-color: {color}; font-weight: 600;"
#         if col == "Region"
#         else ""
#         for col in row.index
#     ]


# styled_df = df.style.apply(color_region_by_progress, axis=1)

# st.title("HIES Survey Progress")

# col1, col2, col3 = st.columns(3)

# total_completed = df["Completed"].sum()
# total_target = df["Target"].sum()
# completion_rate = total_completed / total_target

# col1.metric("Households Completed", total_completed)
# col2.metric("Completion Rate", f"{completion_rate:.1%}")
# col3.metric("Remaining", total_target - total_completed)

# st.subheader("Progress by Region")

# st.dataframe(
#     styled_df,
#     use_container_width=True,
#     hide_index=True,
#     column_config={
#         "Progress": st.column_config.ProgressColumn(
#             "Completion",
#             min_value=0,
#             max_value=1,
#             format="%.0f%%",
#         )
#     },
# )
import streamlit as st
import pandas as pd

df = pd.DataFrame({
    "task": ["A", "B", "C"],
    "progress": [20, 65, 90],
    "owner": ["Sam", "Riya", "Leo"]
})

event = st.dataframe(
    df,
    column_config={
        "progress": st.column_config.ProgressColumn(
            "Progress",
            min_value=0,
            max_value=100,
            format="%d%%",
        )
    },
    hide_index=True,
    use_container_width=True,
    on_select="rerun",
    selection_mode="single-row",
)

selected_rows = event.selection.rows

if selected_rows:
    selected = df.iloc[selected_rows[0]]

    st.subheader(f"Selected: {selected['task']}")
    st.write("Owner:", selected["owner"])
    st.write("Progress:", selected["progress"])

    # do whatever based on selected row
    if selected["progress"] < 50:
        st.warning("Needs attention")
    else:
        st.success("Looks good")