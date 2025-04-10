import streamlit as st
import pandas as pd
import difflib

# Load your merged dataset
@st.cache_data
def load_data():
    # Load all five employee datasets    
    df1 = pd.read_csv("employees (1).csv")
    df2 = pd.read_csv("employees (2).csv")
    df3 = pd.read_csv("employees (3).csv")
    df4 = pd.read_csv("employees (4).csv")
    df5 = pd.read_csv("employees (5).csv")

    # Merge datasets on 'user_id'
    merged = df1.merge(df2, on='user_id', how='outer')
    merged = merged.merge(df3, on='user_id', how='outer')

    # Drop conflicting columns from df4 and merge
    df4 = df4.drop(columns=[col for col in df4.columns if col in merged.columns and col != 'user_id'])
    merged = merged.merge(df4, on='user_id', how='outer')

    # Drop conflicting columns from df5 and merge
    df5 = df5.drop(columns=[col for col in df5.columns if col in merged.columns and col != 'user_id'])
    merged = merged.merge(df5, on='user_id', how='outer')

    # Rename for consistency (only rename if the merged column names are present)
    merged = merged.rename(columns={
        'average_okr_score_df1': 'average_okr_score',
        'average_kpi_score_df2': 'average_kpi_score',
        'average_manager_score_df4': 'average_manager_score',
    })

    # Fill missing scores with 0
    for col in ['average_okr_score', 'average_kpi_score', 'average_manager_score']:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0)

    return merged

# Core recommendation function
def get_best_employees(team_name, df, top_n=5):
    team_name = team_name.strip().lower()
    team_names = df['team_name'].dropna().str.lower().unique()
    closest_matches = difflib.get_close_matches(team_name, team_names, n=1, cutoff=0.6)

    if not closest_matches:
        return pd.DataFrame(), [], []

    matched_team_name = closest_matches[0]
    team_df = df[df['team_name'].str.lower() == matched_team_name]

    # Sort by average OKR score
    team_df_sorted_okr = team_df.sort_values(by=['average_okr_score'], ascending=False)
    top_employees_okr = team_df_sorted_okr.head(top_n)

    # Sort by average KPI score
    team_df_sorted_kpi = team_df.sort_values(by=['average_kpi_score'], ascending=False)
    top_employees_kpi = team_df_sorted_kpi.head(top_n)

    # Sort by average Manager score
    team_df_sorted_manager = team_df.sort_values(by=['average_manager_score'], ascending=False)
    top_employees_manager = team_df_sorted_manager.head(top_n)

    return top_employees_okr[['user_id', 'full_name', 'average_okr_score', 'year_of_service', 'sum_tardy', 'sum_absent']], \
           top_employees_kpi[['user_id', 'full_name', 'average_kpi_score', 'year_of_service', 'sum_tardy', 'sum_absent']], \
           top_employees_manager[['user_id', 'full_name', 'average_manager_score', 'year_of_service', 'sum_tardy', 'sum_absent']], []

# Streamlit UI
st.title("\U0001F4BC Employee Recommendation Chatbot")
st.write("Enter a team name to get top performing employees based on OKR, KPI, and Manager scores.")

merged_df = load_data()

# Option for manager to select a team name
team_name_input = st.text_input("Enter the team name managed by you:")

if team_name_input:
    top_employees_okr, top_employees_kpi, top_employees_manager, suggestions = get_best_employees(team_name_input, merged_df)

    if top_employees_okr.empty:
        st.warning(f"No employees found for team '{team_name_input}'.")
        if suggestions:
            st.info("Did you mean one of these?")
            for s in suggestions:
                st.write(f"- {s}")
        else:
            st.error("No similar team names found.")
    else:
        st.success(f"Top employees in team '{team_name_input}':")

        st.subheader("Top Employees Ranked by Average OKR Score")
        st.dataframe(top_employees_okr)

        st.subheader("Top Employees Ranked by Average KPI Score")
        st.dataframe(top_employees_kpi)

        st.subheader("Top Employees Ranked by Average Manager Score")
        st.dataframe(top_employees_manager)
