
import streamlit as st
import ollama

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

    submitted = st.form_submit_button("Analyse Incident")

if submitted:

    if incident_title.strip() and description.strip():

        st.success("Incident details captured successfully!")

        prompt = f"""
        You are an IT incident analysis assistant.

        Analyse the following incident.

        Incident Title: {incident_title}
        Description: {description}
        Affected Service: {affected_service}
        Business Impact: {impact}

        Provide your response using these sections:

        1. Incident Summary
        2. Incident Category
        3. Severity Assessment
        4. Three Possible Technical Causes
        5. Troubleshooting Steps
        6. Prevention Recommendations

        Important:
        - Explain your reasoning.
        - Do not claim possible causes are confirmed facts.
        - Do not recommend unsafe automatic system changes.
        - Mention when additional technical evidence is needed.
        """

        st.header("AI Incident Analysis")

        with st.spinner("Qwen AI is analysing the incident..."):

            try:
                response = ollama.chat(
                    model="qwen2.5:3b",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                analysis = response["message"]["content"]

                st.markdown(analysis)

            except Exception as e:

                st.error(
                    "Unable to connect to Ollama. "
                    "Please check whether Ollama is running."
                )

                st.caption(str(e))

    else:
        st.warning(
            "Please enter both the incident title and description."
        )

st.divider()

st.caption("OpsPilot AI | Local AI Prototype | Version 1.0")
