
import re

import streamlit as st
import ollama

from knowledge_base import search_knowledge


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="OpsPilot AI",
    page_icon="🛠️",
    layout="wide"
)


# ==========================================
# 2. INCIDENT CLASSIFICATION
# ==========================================

def classify_incident(affected_service, incident_title, description):

    """
    Identify the incident category from the selected service
    and reported symptoms.

    Classification identifies the incident type, not its root cause.
    """

    combined_text = (
        incident_title + " " + description
    ).lower()

    if affected_service == "Website" and "503" in combined_text:

        return (
            "Web Application Availability / HTTP 503",
            "Investigate HTTP 503 responses, application health, "
            "server resources, upstream dependencies and proxy logs "
            "where applicable."
        )

    if affected_service == "Database":

        return (
            "Database Connectivity / Connection Failure",
            "Investigate database availability, application database "
            "errors, network connectivity, authentication, connection "
            "pool usage and database resource health."
        )

    if affected_service == "Network":

        return (
            "Network Connectivity Incident",
            "Investigate connectivity between affected systems, "
            "network diagnostics, DNS resolution, routing, firewall "
            "rules and relevant network logs."
        )

    if affected_service == "Application":

        return (
            "Application Availability / Functionality Incident",
            "Investigate application errors, application logs, "
            "service health, dependencies and recent changes."
        )

    if affected_service == "Server":

        return (
            "Server Availability / Infrastructure Incident",
            "Investigate server health, service status, resource "
            "usage, system logs and relevant dependencies."
        )

    if affected_service == "Website":

        return (
            "Website Availability Incident",
            "Investigate website availability, application logs, "
            "server health and relevant dependencies."
        )

    return (
        "General IT Incident",
        "Investigate the reported symptoms, relevant service logs, "
        "system health and dependencies."
    )


# ==========================================
# 3. REPORT SECTION EXTRACTION
# ==========================================

def extract_sections(ai_response):

    """
    Extract only Markdown headings formatted as:

    ## 1. Incident Summary

    Ordinary numbered lists are ignored.
    """

    sections = {}

    pattern = r"^##\s+(\d+)\.\s+(.+?)\s*$"

    matches = list(
        re.finditer(
            pattern,
            ai_response,
            re.MULTILINE
        )
    )

    for index, match in enumerate(matches):

        section_number = int(match.group(1))

        start = match.end()

        if index + 1 < len(matches):

            end = matches[index + 1].start()

        else:

            end = len(ai_response)

        content = ai_response[start:end].strip()

        if content:

            sections[section_number] = {
                "title": match.group(2).strip(),
                "content": content
            }

    return sections


# ==========================================
# 4. KNOWLEDGE BASE REFERENCES
# ==========================================

def build_knowledge_references(retrieved_results):

    """
    Build references from actual ChromaDB retrieval results.
    """

    if not retrieved_results:

        return "No relevant knowledge documents were retrieved."

    references = []

    for index, result in enumerate(
        retrieved_results,
        start=1
    ):

        reference = (
            f"- Evidence {index}: "
            f"{result['source']} "
            f"(Retrieved chunk {result['chunk']})"
        )

        if reference not in references:

            references.append(reference)

    return "\n".join(references)


# ==========================================
# 5. SAFETY FILTER
# ==========================================

def apply_safety_filter(text):

    """
    Remove certain direct production-changing instructions
    and add a technician approval warning.

    This is a basic text filter, not a complete safety system.
    """

    unsafe_patterns = [

        r"^\s*(?:[-*]\s*)?(?:\d+[.)]\s*)?(?:restart|reboot)\b",

        r"^\s*(?:[-*]\s*)?(?:\d+[.)]\s*)?stop the\b",

        r"^\s*(?:[-*]\s*)?(?:\d+[.)]\s*)?shut down\b",

        r"^\s*(?:[-*]\s*)?(?:\d+[.)]\s*)?(?:delete|remove|redeploy|rollback|disable)\b",

        r"^\s*(?:[-*]\s*)?(?:\d+[.)]\s*)?kill the\b",

        r"^\s*(?:[-*]\s*)?(?:\d+[.)]\s*)?(?:modify|change) the configuration\b",

        r"^\s*(?:[-*]\s*)?(?:\d+[.)]\s*)?clear the cache\b",

        r"^\s*(?:you should|you can|try to)\s+"
        r"(?:restart|reboot|stop|delete|remove|redeploy|"
        r"rollback|disable|modify|change|clear)\b"

    ]

    safe_lines = []

    for line in text.splitlines():

        is_unsafe = any(
            re.search(
                pattern,
                line,
                re.IGNORECASE
            )
            for pattern in unsafe_patterns
        )

        if not is_unsafe:

            safe_lines.append(line)

    warning_text = (
        "Before performing any production-changing action, "
        "a qualified technician must review the evidence, "
        "assess the impact and approve the action."
    )

    # Remove duplicate approval warnings.

    safe_lines = [
        line
        for line in safe_lines
        if warning_text.lower() not in line.lower()
    ]

    cleaned_text = "\n".join(safe_lines).strip()

    if cleaned_text:

        cleaned_text += "\n\n"

    cleaned_text += warning_text

    return cleaned_text


# ==========================================
# 6. BUILD FINAL REPORT
# ==========================================

def build_final_report(
    ai_response,
    retrieved_results,
    severity,
    incident_category
):

    """
    Build a structured eight-section report.

    Python controls the category, severity and references.
    AI supplies the technical analysis.
    """

    sections = extract_sections(ai_response)

    section_defaults = {

        1: (
            "Incident Summary",
            "The incident details require further analysis."
        ),

        2: (
            "Incident Category",
            "The technical category requires further investigation."
        ),

        3: (
            "Severity Assessment",
            "Human validation is required."
        ),

        4: (
            "Possible Technical Causes",
            "Further technical evidence is required to identify possible causes."
        ),

        5: (
            "Troubleshooting Steps",
            "Investigate relevant logs, service health, resource metrics "
            "and dependencies."
        ),

        7: (
            "Prevention Recommendations",
            "Establish appropriate monitoring, logging and documented "
            "incident response procedures."
        ),

        8: (
            "Additional Evidence Required",
            "Collect relevant application logs, service health information "
            "and dependency diagnostics."
        )

    }

    report = []

    for section_number in range(1, 9):

        # Section 6 is generated using actual retrieved references.

        if section_number == 6:

            report.append(
                "## 6. Knowledge Base References"
            )

            report.append(
                build_knowledge_references(retrieved_results)
            )

            continue

        title, default_content = section_defaults[
            section_number
        ]

        section = sections.get(section_number)

        if section:

            title = section["title"]

            content = section["content"]

        else:

            content = default_content

        # Python controls the incident category.

        if section_number == 2:

            title = "Incident Category"

            content = (
                f"**{incident_category}**\n\n"
                "This category describes the reported incident type. "
                "It does not confirm the underlying technical root cause."
            )

        # Python controls the initial severity.

        if section_number == 3:

            title = "Severity Assessment"

            content = (
                f"Business Impact: {severity}\n\n"
                f"Initial Severity: {severity}\n\n"
                "Human validation is required. The initial severity "
                "should be reviewed as evidence about the incident "
                "scope and business impact becomes available."
            )

        # Apply basic safety filtering to troubleshooting steps.

        if section_number == 5:

            content = apply_safety_filter(content)

        if not content.strip():

            content = default_content

        report.append(
            f"## {section_number}. {title}\n\n{content}"
        )

    return "\n\n".join(report)


# ==========================================
# 7. APPLICATION HEADER
# ==========================================

st.title("OpsPilot AI")

st.subheader(
    "AI-Powered IT Incident Diagnosis and Resolution Assistant"
)

st.write(
    "Analyse IT incidents, identify possible causes, "
    "and help technical teams plan their next steps."
)

st.divider()


# ==========================================
# 8. INCIDENT SUBMISSION FORM
# ==========================================

st.header("Incident Submission")

with st.form("incident_form"):

    incident_title = st.text_input(
        "Incident Title",
        placeholder="Example: Website returning HTTP 503 error"
    )

    description = st.text_area(
        "Describe the Incident",
        placeholder="Explain what happened and when it started..."
    )

    affected_service = st.selectbox(
        "Affected Service",
        [
            "Website",
            "Database",
            "Network",
            "Application",
            "Server",
            "Other"
        ]
    )

    impact = st.selectbox(
        "Business Impact",
        [
            "Low",
            "Medium",
            "High",
            "Critical"
        ]
    )

    submitted = st.form_submit_button(
        "Analyse Incident"
    )


# ==========================================
# 9. INCIDENT ANALYSIS
# ==========================================

if submitted:

    if incident_title.strip() and description.strip():

        st.success(
            "Incident details captured successfully!"
        )

        severity = impact

        # ----------------------------------
        # 9.1 Incident classification
        # ----------------------------------

        incident_category, investigation_focus = classify_incident(
            affected_service,
            incident_title,
            description
        )

        # ----------------------------------
        # 9.2 Confirmed incident information
        # ----------------------------------

        incident_facts = f"""
Incident Title: {incident_title}

Description: {description}

Affected Service: {affected_service}

Business Impact: {impact}

Initial Severity: {severity}

Incident Category: {incident_category}

Affected User Scope: Not confirmed unless explicitly
established by the supplied incident description.

Root Cause: Not yet identified.

Service Status: Unknown unless explicitly confirmed
by the supplied incident description.
"""

        st.header("AI Incident Analysis")

        try:

            # ----------------------------------
            # 9.3 Retrieve relevant knowledge
            # ----------------------------------

            retrieval_query = f"""
Affected Service: {affected_service}

Incident Title: {incident_title}

Incident Description: {description}

Incident Category: {incident_category}

Find technical information about possible causes,
investigation steps, evidence requirements and
troubleshooting for this incident.
"""

            with st.spinner(
                "Searching the technical knowledge base..."
            ):

                retrieved_results = search_knowledge(
                    retrieval_query,
                    results_count=3
                )

            # ----------------------------------
            # 9.4 Prepare retrieved context
            # ----------------------------------

            knowledge_context = ""

            if retrieved_results:

                for index, result in enumerate(
                    retrieved_results,
                    start=1
                ):

                    knowledge_context += f"""

Evidence {index}

Source: {result['source']}

Retrieved Chunk: {result['chunk']}

Content:

{result['content']}

"""

            else:

                knowledge_context = (
                    "No relevant technical knowledge was retrieved. "
                    "Do not invent knowledge-base references."
                )

            # ----------------------------------
            # 9.5 Build incident-specific prompt
            # ----------------------------------

            prompt = f"""
You are OpsPilot AI, an IT incident diagnosis
and resolution planning assistant.

Your task is to analyse the incident using only
the supplied incident information and retrieved
technical knowledge.

INCIDENT DETAILS:

{incident_facts}

RETRIEVED KNOWLEDGE:

{knowledge_context}

INCIDENT CLASSIFICATION:

{incident_category}

INVESTIGATION FOCUS:

{investigation_focus}

STRICT ACCURACY RULES:

1. Report only facts supported by the incident details
   or retrieved technical evidence.

2. Never assume all users are affected.

3. If affected user scope is unknown, clearly say so.

4. Never claim a service is running, stopped, healthy
   or unavailable unless evidence confirms it.

5. The root cause is not confirmed unless evidence
   explicitly establishes it.

6. Do not present possible causes as confirmed diagnoses.

7. Preserve the initial severity: {severity}.

8. Clearly distinguish confirmed facts, hypotheses
   and missing evidence.

9. Do not invent logs, test results, metrics,
   configuration changes or monitoring results.

10. Use the retrieved documents as technical guidance.
    Do not claim that a document proves an incident cause.

11. Do not invent knowledge-base filenames or references.

INCIDENT-SPECIFIC GUIDANCE:

If the affected service is Database:

- Prioritise database server health and availability.
- Investigate application database connection errors.
- Check connectivity between the application and database.
- Consider authentication and connection configuration.
- Investigate connection pool exhaustion and resource usage.
- Do not assume a reverse proxy connects directly to the database.
- Do not claim the database is unavailable without evidence.

If the affected service is Website:

- Investigate the reported website errors.
- Consider application health, server resources,
  upstream dependencies and proxy connectivity where relevant.
- An HTTP 503 response alone does not establish the root cause.

If the affected service is Network:

- Prioritise network connectivity, DNS, routing,
  firewall and relevant network diagnostics.

If the affected service is Application:

- Prioritise application logs, service health,
  dependencies and recent changes.

If the affected service is Server:

- Prioritise server health, system logs,
  resource metrics and service availability.

SAFETY RULES:

1. Recommend investigation before corrective action.

2. Do not recommend immediate production restarts.

3. Do not instruct technicians to delete data,
   modify production configuration, disable services
   or perform unapproved production changes.

4. Corrective actions require qualified technician
   review and explicit approval.

5. Do not claim that any action has already been performed.

6. Prefer diagnostic and read-only investigation steps.

7. Do not recommend load testing during an active
   production incident unless a qualified technician
   has approved a controlled test.

8. Prefer reviewing recent deployments, configuration
   changes and existing monitoring data before
   recommending additional traffic-generating tests.

OUTPUT FORMAT:

## 1. Incident Summary

Summarise the reported incident.

Include only confirmed facts.
Mention unknown user scope and service status where relevant.

## 2. Incident Category

Describe the incident type.

Do not identify an unconfirmed root cause.

## 3. Severity Assessment

Explain the initial business impact and severity briefly.

## 4. Possible Technical Causes

Give three distinct and relevant technical hypotheses.

For each hypothesis include:

- Possible cause.
- Why it could be relevant.
- Evidence needed to investigate it.

Clearly label every cause as unconfirmed.

## 5. Troubleshooting Steps

Give five ordered investigation steps.

Make them specific to the affected service.

For each step explain:

- What to investigate.
- Why it matters.
- What evidence to collect.

Prioritise diagnostic checks.
Do not recommend production-changing actions.

## 7. Prevention Recommendations

Give three practical recommendations.

Make recommendations relevant to the incident.

Use conditional language where architecture,
dependencies or root cause are unknown.

Do not claim that a suggested control already exists.

## 8. Additional Evidence Required

List the most important missing information
needed for root cause analysis.

Avoid repeating the same evidence unnecessarily.

FORMATTING RULES:

Every report heading must begin with exactly
two Markdown hash symbols and its section number.

Example:

## 1. Incident Summary

Never use numbered list items as report headings.

Do not generate section 6.
Section 6 is added by the application.

Do not omit sections 7 or 8.

Keep the report clear, concise and technically accurate.

"""

            # ----------------------------------
            # 9.6 Generate AI analysis
            # ----------------------------------

            with st.spinner(
                "Qwen AI is analysing the incident and evidence..."
            ):

                response = ollama.chat(
                    model="qwen2.5:3b",

                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    options={
                        "temperature": 0.1,
                        "num_predict": 1100,
                        "num_ctx": 4096
                    }
                )

                analysis = response["message"]["content"]

            # ----------------------------------
            # 9.7 Build final report
            # ----------------------------------

            final_report = build_final_report(
                analysis,
                retrieved_results,
                severity,
                incident_category
            )

            # ----------------------------------
            # 9.8 Display confirmed details
            # ----------------------------------

            with st.expander(
                "View Confirmed Incident Details"
            ):

                st.write(
                    f"**Incident Title:** {incident_title}"
                )

                st.write(
                    f"**Affected Service:** {affected_service}"
                )

                st.write(
                    f"**Business Impact:** {impact}"
                )

                st.write(
                    f"**Initial Severity:** {severity}"
                )

                st.write(
                    f"**Incident Category:** {incident_category}"
                )

                st.write(
                    "**Affected User Scope:** Not confirmed "
                    "unless explicitly established."
                )

                st.write(
                    "**Service Status:** Unknown unless confirmed."
                )

                st.write(
                    "**Root Cause:** Not yet identified."
                )

            # ----------------------------------
            # 9.9 Display final report
            # ----------------------------------

            st.markdown(final_report)

            # ----------------------------------
            # 9.10 Display retrieved evidence
            # ----------------------------------

            with st.expander(
                "View Retrieved Knowledge Base Evidence"
            ):

                if retrieved_results:

                    for index, result in enumerate(
                        retrieved_results,
                        start=1
                    ):

                        st.markdown(
                            f"### Evidence {index}"
                        )

                        st.caption(
                            f"Source: {result['source']} | "
                            f"Chunk: {result['chunk']}"
                        )

                        st.write(
                            result["content"]
                        )

                        st.divider()

                else:

                    st.info(
                        "No relevant technical knowledge was retrieved."
                    )

        except Exception as e:

            st.error(
                "Unable to complete incident analysis. "
                "Please check whether Ollama and the knowledge "
                "base are available."
            )

            st.caption(str(e))

    else:

        st.warning(
            "Please enter both the incident title and description."
        )


# ==========================================
# 10. APPLICATION FOOTER
# ==========================================

st.divider()

st.caption(
    "OpsPilot AI | Local AI Prototype | Version 1.9"
)
