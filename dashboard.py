import streamlit as st
import requests
import pandas as pd
import time
import altair as alt

API_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Smart Student Management System", layout="wide")
st.title("🎓 Smart Student Management Dashboard")

# --- Wait for API ---
for i in range(10):
    try:
        res = requests.get(f"{API_URL}/students")
        res.raise_for_status()
        st.success("✅ Connected to API")
        break
    except requests.exceptions.RequestException:
        st.warning("Waiting for API...")
        time.sleep(2)
else:
    st.error("❌ Failed to connect to API.")
    st.stop()

# --- Sidebar Menu ---
menu = ["Dashboard", "View Students", "Add Student", "Update Student", "Delete Student", 
        "Predict Grade"]
choice = st.sidebar.selectbox("Menu", menu)

# --- Helper: Fetch Students ---
def fetch_students():
    try:
        res = requests.get(f"{API_URL}/students")
        res.raise_for_status()
        data = res.json()
        if not data:
            st.info("No students in the database.")
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching students: {e}")
        return pd.DataFrame()

# --- DASHBOARD ---
if choice == "Dashboard":
    st.subheader("📊 Dashboard & Analytics")
    df = fetch_students()
    if df.empty:
        st.stop()

    # Compute average marks
    df['avg'] = df[['math','science','english']].mean(axis=1)

    # --- Filters ---
    st.sidebar.subheader("Filters")
    course_options = ["All"] + sorted(df['course'].unique().tolist())
    selected_course = st.sidebar.selectbox("Select Course", course_options)

    grade_options = ["All"] + sorted(df['grade'].dropna().unique().tolist())
    selected_grade = st.sidebar.selectbox("Select Grade", grade_options)

    # Apply filters
    filtered_df = df.copy()
    if selected_course != "All":
        filtered_df = filtered_df[filtered_df['course'] == selected_course]
    if selected_grade != "All":
        filtered_df = filtered_df[filtered_df['grade'] == selected_grade]

    if filtered_df.empty:
        st.warning("No data for selected filters.")
        st.stop()

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students", len(filtered_df))
    col2.metric("Average Marks", round(filtered_df['avg'].mean(), 2))
    top_student = filtered_df.sort_values('avg', ascending=False).iloc[0]
    col3.metric("Top Student", f"{top_student['name']} ({round(top_student['avg'],2)})")
    col4.metric("Average Attendance", round(filtered_df['attendance'].mean(), 2))

    # --- Top 5 Students ---
    st.subheader("Top 5 Students")
    top5 = filtered_df.sort_values('avg', ascending=False).head(5)
    chart_top = alt.Chart(top5).mark_bar(color="#4CAF50").encode(
        x=alt.X('name', sort='-y', title="Student"),
        y=alt.Y('avg', title="Average Marks"),
        tooltip=['name', 'math', 'science', 'english', 'avg', 'grade']
    )
    st.altair_chart(chart_top, use_container_width=True)
    st.table(top5[['name','math','science','english','avg','grade']])

    # --- Course-wise Average Marks ---
    st.subheader("Course-wise Average Marks")
    course_avg = filtered_df.groupby('course')['avg'].mean().reset_index()
    chart_course = alt.Chart(course_avg).mark_bar(color="#2196F3").encode(
        x=alt.X('course', title="Course"),
        y=alt.Y('avg', title="Average Marks"),
        tooltip=['course', 'avg']
    )
    st.altair_chart(chart_course, use_container_width=True)

    # --- Grade Distribution ---
    st.subheader("Grade Distribution")
    grade_counts = filtered_df['grade'].value_counts().reset_index()
    grade_counts.columns = ['grade', 'count']
    chart_grade = alt.Chart(grade_counts).mark_bar(color="#FF9800").encode(
        x='grade',
        y='count',
        tooltip=['grade','count']
    )
    st.altair_chart(chart_grade, use_container_width=True)

    # --- Weak Subjects Insight ---
    st.subheader("Weak Subjects Insight")
    filtered_df['weak_math'] = filtered_df['math'] < filtered_df['avg']
    filtered_df['weak_science'] = filtered_df['science'] < filtered_df['avg']
    filtered_df['weak_english'] = filtered_df['english'] < filtered_df['avg']

    weak_counts = {
        'Math': filtered_df['weak_math'].sum(),
        'Science': filtered_df['weak_science'].sum(),
        'English': filtered_df['weak_english'].sum()
    }
    weak_df = pd.DataFrame(list(weak_counts.items()), columns=['Subject','Count'])
    chart_weak = alt.Chart(weak_df).mark_bar(color="#E91E63").encode(
        x='Subject',
        y='Count',
        tooltip=['Subject','Count']
    )
    st.altair_chart(chart_weak, use_container_width=True)
