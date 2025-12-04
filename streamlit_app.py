# streamlit_app.py
import streamlit as st
import requests
import pandas as pd
import base64

DEFAULT_API = "http://127.0.0.1:8000"
st.set_page_config(layout="wide", page_title="Smart Student Management System")

# --------------------------
# Session State Initialization
# --------------------------
if "API_URL" not in st.session_state:
    st.session_state["API_URL"] = DEFAULT_API
if "token" not in st.session_state:
    st.session_state["token"] = None

API_URL = st.session_state["API_URL"]

# --------------------------
# Sidebar: Connection & Login
# --------------------------
st.sidebar.title("Connection & Admin")
api_url_input = st.sidebar.text_input("API URL", value=API_URL)
if api_url_input != st.session_state["API_URL"]:
    st.session_state["API_URL"] = api_url_input

if st.sidebar.button("Reconnect"):
    st.experimental_rerun()

st.sidebar.markdown("**Admin Login**")
email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    try:
        r = requests.post(f"{st.session_state['API_URL']}/auth/login",
                          json={"email": email, "password": password}, timeout=5)
        if r.status_code == 200:
            st.session_state["token"] = r.json().get("access_token")
            st.sidebar.success("Logged in successfully")
        else:
            st.sidebar.error("Login failed")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

if st.session_state.get("token"):
    st.sidebar.info("✅ Logged in")

# --------------------------
# Sidebar Menu
# --------------------------
menu = st.sidebar.radio(
    "Menu",
    ["Dashboard", "View Students", "Add Student", "Update Student",
     "Upload Photo", "Predict Grade", "Insights", "Export CSV", "Settings"]
)

# --------------------------
# Helper Function
# --------------------------
def api(path, method="GET", json=None, files=None):
    url = f"{st.session_state['API_URL']}{path}"
    headers = {"Authorization": f"Bearer {st.session_state['token']}"} if st.session_state.get("token") else {}
    try:
        if method == "GET":
            return requests.get(url, headers=headers, timeout=6)
        if method == "POST":
            return requests.post(url, json=json, headers=headers, files=files, timeout=6)
        if method == "PUT":
            return requests.put(url, json=json, headers=headers, timeout=6)
        if method == "DELETE":
            return requests.delete(url, headers=headers, timeout=6)
    except Exception as e:
        st.error(f"API error: {e}")
        return None

# --------------------------
# Dashboard
# --------------------------
if menu == "Dashboard":
    st.title("📊 Dashboard & Analytics")
    r = api("/students")
    if not r or r.status_code != 200:
        st.info("No data or API unreachable")
        st.stop()

    try:
        df = pd.DataFrame(r.json())
    except Exception:
        st.error("Invalid data from API")
        st.stop()

    if df.empty:
        st.info("No students available")
        st.stop()

    df['avg'] = df[['math', 'science', 'english']].mean(axis=1)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students", len(df))
    col2.metric("Average Marks", round(df['avg'].mean(), 2))
    top = df.loc[df['avg'].idxmax()]
    col3.metric("Top Student", f"{top['name']} ({round(top['avg'], 2)})")
    col4.metric("Average Attendance", round(df['attendance'].mean(), 2))

    st.subheader("Top 10 Students")
    st.table(df.sort_values('avg', ascending=False).head(10)[['name', 'avg', 'grade']])

    st.subheader("Grade Distribution")
    st.bar_chart(df['grade'].value_counts())

# --------------------------
# View Students
# --------------------------
elif menu == "View Students":
    st.title("All Students")
    r = api("/students")
    if r and r.status_code == 200:
        try:
            df = pd.DataFrame(r.json())
        except Exception:
            st.error("Invalid data from API")
            st.stop()

        st.dataframe(df)
        sid = st.number_input("Open student ID", min_value=1, step=1)
        if st.button("Load Student"):
            student = df[df['id'] == sid]
            if not student.empty:
                s = student.iloc[0]
                st.json(s.to_dict())
                if s.get("photo"):
                    try:
                        st.image(base64.b64decode(s["photo"]), width=200)
                    except Exception:
                        st.warning("Failed to load photo")
            else:
                st.info("No student found with that ID")
    else:
        st.error("Failed to fetch students")

# --------------------------
# Add Student
# --------------------------
elif menu == "Add Student":
    st.title("➕ Add Student")
    with st.form("add_student_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        course = st.text_input("Course")
        math = st.number_input("Math", 0.0, 100.0)
        science = st.number_input("Science", 0.0, 100.0)
        english = st.number_input("English", 0.0, 100.0)
        attendance = st.number_input("Attendance %", 0.0, 100.0, value=100.0)
        submitted = st.form_submit_button("Add Student")
        if submitted:
            payload = {
                "name": name, "email": email, "course": course,
                "math": math, "science": science, "english": english,
                "attendance": attendance
            }
            res = api("/students", method="POST", json=payload)
            if res and res.status_code == 201:
                st.success("Student added successfully")
            else:
                st.error(res.text if res else "Failed to add student")

# --------------------------
# Update Student
# --------------------------
elif menu == "Update Student":
    st.title("✏️ Update Student")
    r = api("/students")
    if r and r.status_code == 200:
        try:
            df = pd.DataFrame(r.json())
        except Exception:
            st.error("Invalid data from API")
            st.stop()

        sid = st.selectbox("Select Student ID", df['id'].tolist())
        student = df[df['id'] == sid].iloc[0]
        with st.form("update_student_form"):
            name = st.text_input("Name", value=student['name'])
            email = st.text_input("Email", value=student['email'])
            course = st.text_input("Course", value=student['course'])
            math = st.number_input("Math", 0.0, 100.0, value=float(student['math']))
            science = st.number_input("Science", 0.0, 100.0, value=float(student['science']))
            english = st.number_input("English", 0.0, 100.0, value=float(student['english']))
            attendance = st.number_input("Attendance %", 0.0, 100.0, value=float(student['attendance']))
            submitted = st.form_submit_button("Update Student")
            if submitted:
                payload = {
                    "name": name, "email": email, "course": course,
                    "math": math, "science": science, "english": english,
                    "attendance": attendance
                }
                res = api(f"/students/{sid}", method="PUT", json=payload)
                if res and res.status_code == 200:
                    st.success("Student updated successfully")
                else:
                    st.error("Failed to update student")
    else:
        st.error("Failed to fetch students")

# --------------------------
# Upload Photo
# --------------------------
elif menu == "Upload Photo":
    st.title("📷 Upload Student Photo")
    r = api("/students")
    if r and r.status_code == 200:
        try:
            df = pd.DataFrame(r.json())
        except Exception:
            st.error("Invalid data from API")
            st.stop()

        if not df.empty:
            sid = st.selectbox("Select Student", df['id'].tolist())
            photo = st.file_uploader("Choose photo", type=['jpg', 'png'])
            if st.button("Upload Photo"):
                if not photo:
                    st.error("Please select a photo")
                else:
                    file_bytes = photo.read()
                    mime_type = photo.type if photo.type else 'image/jpeg'
                    files = {'photo': (photo.name, file_bytes, mime_type)}
                    res = api(f"/students/{sid}/photo", method="POST", files=files)
                    if res and res.status_code == 200:
                        st.success("Photo uploaded successfully")
                    else:
                        st.error(res.text if res else "Failed to upload photo")
        else:
            st.info("No students available")
    else:
        st.error("Failed to fetch students")

# --------------------------
# Predict Grade
# --------------------------
elif menu == "Predict Grade":
    st.title("🎯 Predict Grade")
    math = st.number_input("Math", 0.0, 100.0)
    science = st.number_input("Science", 0.0, 100.0)
    english = st.number_input("English", 0.0, 100.0)
    if st.button("Predict Grade"):
        payload = {"math": math, "science": science, "english": english}
        try:
            res = requests.post(f"{st.session_state['API_URL']}/predict-grade", json=payload, timeout=5)
            if res and res.status_code == 200:
                st.success(f"Predicted Grade: {res.json().get('predicted_grade')}")
            else:
                st.error("Prediction failed")
        except Exception as e:
            st.error(f"Error: {e}")

# --------------------------
# Insights
# --------------------------
elif menu == "Insights":
    st.title("🔍 Student Insights")
    r = api("/students")
    if r and r.status_code == 200:
        try:
            df = pd.DataFrame(r.json())
        except Exception:
            st.error("Invalid data from API")
            st.stop()

        sid = st.selectbox("Select Student ID", df['id'].tolist())
        if st.button("Get Insights"):
            try:
                res = requests.get(f"{st.session_state['API_URL']}/students/{sid}/insights", timeout=5)
                if res and res.status_code == 200:
                    st.json(res.json())
                else:
                    st.error("Failed to fetch insights")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("No students available")

# --------------------------
# Export CSV
# --------------------------
elif menu == "Export CSV":
    st.title("📥 Export Students Data")
    r = api("/students")
    if r and r.status_code == 200:
        try:
            df = pd.DataFrame(r.json())
        except Exception:
            st.error("Invalid data from API")
            st.stop()

        if not df.empty:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv_data, "students.csv", "text/csv")
        else:
            st.info("No students available to export")
    else:
        st.error("Failed to fetch students")

# --------------------------
# Settings
# --------------------------
elif menu == "Settings":
    st.title("⚙️ Settings")
    st.write("API URL:", st.session_state['API_URL'])
    if st.button("Clear Cache"):
        try:
            st.cache_data.clear()
            st.success("Cache cleared successfully")
        except Exception:
            st.warning("Cache clearing not supported in this Streamlit version")
