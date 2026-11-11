
import streamlit as st

st.set_page_config(
    page_title="OpsPilot AI",
    page_icon="🛠️",
    layout="wide"
)

st.title("OpsPilot AI")
st.subheader("AI-Powered IT Incident Diagnosis and Resolution Assistant")

st.write(
    "Analyse IT incidents, identify possible causes, "
    "and help technical teams plan their next steps."
)

st.divider()

st.header("Incident Submission")

with st.form("incident_form"):
    incident_title = st.text_input(
        "Incident Title",
        placeholder="Example: Website returning 503 error"
    )

    description = st.text_area(
        "Describe the Incident",
        placeholder="Explain what happened and when it started..."
    )

    affected_service = st.selectbox(
        "Affected Service",
        ["Website", "Database", "Network", "Application", "Server", "Other"]
    )

    impact = st.selectbox(
        "Business Impact",
        ["Low", "Medium", "High", "Critical"]
    )

    submitted = st.form_submit_button("Submit Incident")

if submitted:
    if incident_title.strip() and description.strip():
        st.success("Incident details captured successfully!")

        st.subheader("Submitted Incident")
        st.write("**Title:**", incident_title)
        st.write("**Description:**", description)
        st.write("**Affected Service:**", affected_service)
        st.write("**Business Impact:**", impact)

        st.info(
            "AI-powered incident analysis will be added "
            "in the next development stage."
        )
    else:
        st.warning("Please enter both the incident title and description.")

st.divider()

st.caption("OpsPilot AI | Project Prototype | Version 1.0")
