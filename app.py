
import re
import textwrap
from pathlib import Path

import streamlit as st
import ollama
import pandas as pd
import plotly.express as px

from knowledge_base import search_knowledge
from incident_storage import save_incident, load_incidents


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="OpsPilot AI | Incident Command",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. HTML RENDERING HELPERS
# ============================================================

def _normalize_html_block(content):
    content = textwrap.dedent(content)
    return "\n".join(
        line.lstrip() for line in content.splitlines()
    ).strip()


def render_markdown(content, *args, **kwargs):
    if kwargs.get("unsafe_allow_html", False) and isinstance(content, str):
        content = _normalize_html_block(content)

    return st.markdown(content, *args, **kwargs)


def render_sidebar_markdown(content, *args, **kwargs):
    if kwargs.get("unsafe_allow_html", False) and isinstance(content, str):
        content = _normalize_html_block(content)

    return st.sidebar.markdown(content, *args, **kwargs)


# ============================================================
# 3. DESIGN SYSTEM
# ============================================================

render_markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        color-scheme: dark;
        --app-bg: #0b1117;
        --surface: #111a22;
        --surface-raised: #15212b;
        --border: #263640;
        --text: #edf4f3;
        --muted: #93a5a5;
        --teal: #42d6bd;
        --teal-strong: #20b99f;
        --teal-soft: rgba(66,214,189,.11);
        --danger: #f07878;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 80% -15%, rgba(38,111,103,.13), transparent 35%),
            var(--app-bg);
        color: var(--text);
    }

    header[data-testid="stHeader"] {
        display: none !important;
    }

    .block-container {
        max-width: 1540px;
        padding: 1.5rem 2.8rem 3.2rem;
    }

    h1, h2, h3, h4 {
        color: var(--text) !important;
        font-family: 'Manrope', sans-serif !important;
        letter-spacing: -.035em;
    }

    h1 {
        font-size: clamp(2rem,3vw,2.65rem) !important;
        font-weight: 800 !important;
    }

    h2 {
        font-size: 1.55rem !important;
        font-weight: 750 !important;
    }

    h3 {
        font-size: 1.12rem !important;
        font-weight: 700 !important;
    }

    p, li, label, [data-testid="stMarkdownContainer"] {
        color: #c5d1d0;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted) !important;
    }

    .eyebrow {
        color: var(--teal);
        font-size: .69rem;
        font-weight: 800;
        letter-spacing: .19em;
        text-transform: uppercase;
        margin-bottom: .65rem;
    }

    .page-subtitle {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.65;
        margin-top: -.35rem;
        margin-bottom: 1.55rem;
        max-width: 850px;
    }

    .section-heading {
        display: flex;
        align-items: center;
        gap: .65rem;
        color: #e7efed;
        font-family: 'Manrope', sans-serif;
        font-size: 1.02rem;
        font-weight: 750;
        margin: 1.35rem 0 .85rem;
    }

    .section-heading:before {
        content: "";
        width: 3px;
        height: 17px;
        border-radius: 4px;
        background: var(--teal);
        display: inline-block;
    }

    /* Sidebar */

    [data-testid="stSidebar"] {
        background: #0e171e;
        border-right: 1px solid #202e37;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 1.5rem 1rem 1.2rem;
    }

    [data-testid="stSidebar"] * {
        color: #dce7e5;
    }

    .brand-lockup {
        padding: .35rem .45rem 1.45rem;
        border-bottom: 1px solid #202e37;
        margin-bottom: 1.25rem;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: .72rem;
        margin-bottom: .35rem;
    }

    .brand-mark {
        width: 39px;
        height: 39px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        color: var(--teal);
        background: var(--teal-soft);
        border: 1px solid rgba(66,214,189,.22);
        font-size: 1.2rem;
    }

    .brand-name {
        color: #f2f7f6;
        font-family: 'Manrope', sans-serif;
        font-size: 1.22rem;
        font-weight: 800;
        letter-spacing: -.045em;
    }

    .brand-tag {
        color: #7f9694;
        font-size: .61rem;
        font-weight: 700;
        letter-spacing: .16em;
        padding-left: 3.15rem;
    }

    .sidebar-label {
        color: #708783;
        font-size: .65rem;
        font-weight: 800;
        letter-spacing: .16em;
        text-transform: uppercase;
        padding: .3rem .65rem .55rem;
    }

    [data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        min-height: 2.85rem;
        padding: .55rem .85rem;
        margin: .16rem 0;
        border-radius: 10px;
        text-align: left;
        justify-content: flex-start;
        background: transparent;
        border: 1px solid transparent;
        color: #9fb1ae;
        font-size: .91rem;
        font-weight: 600;
        box-shadow: none;
    }

    [data-testid="stSidebar"] div.stButton > button:hover {
        background: #17262d;
        border-color: #2a4146;
        color: #f1f7f5;
    }

    [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background: rgba(66,214,189,.11);
        border: 1px solid rgba(66,214,189,.25);
        color: #69e2cb;
        box-shadow: inset 3px 0 0 var(--teal);
    }

    .sidebar-status {
        margin-top: 1.5rem;
        padding: 1rem .9rem;
        border: 1px solid #263b40;
        border-radius: 12px;
        background: linear-gradient(145deg,#14242a,#111d23);
    }

    .status-line {
        display: flex;
        align-items: center;
        gap: .48rem;
        color: #cce5df;
        font-size: .82rem;
        font-weight: 700;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--teal);
        box-shadow: 0 0 10px rgba(66,214,189,.45);
    }

    .status-detail {
        color: #849a98;
        font-size: .73rem;
        line-height: 1.6;
        margin-top: .55rem;
    }

    /* Metrics */

    [data-testid="stMetric"] {
        background: linear-gradient(150deg,#15222a,#111b22);
        border: 1px solid #293a42;
        border-radius: 13px;
        padding: 1.05rem 1.15rem;
        min-height: 112px;
        box-shadow: 0 8px 22px rgba(0,0,0,.12);
        transition: border-color .18s ease, transform .18s ease;
    }

    [data-testid="stMetric"]:hover {
        border-color: rgba(66,214,189,.48);
        transform: translateY(-2px);
    }

    [data-testid="stMetricLabel"] {
        color: #91a5a2 !important;
        font-size: .78rem !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        color: #f1f7f5 !important;
        font-family: 'Manrope', sans-serif;
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        letter-spacing: -.04em;
    }

    [data-testid="stMetricDelta"] {
        color: var(--teal) !important;
    }

    /* Panels */

    .panel {
        background: #111b22;
        border: 1px solid #263740;
        border-radius: 14px;
        padding: 1.1rem 1.15rem;
        margin-bottom: .8rem;
    }

    .panel-title {
        color: #e5eeec;
        font-family: 'Manrope', sans-serif;
        font-size: .96rem;
        font-weight: 750;
        margin-bottom: .15rem;
    }

    .panel-caption {
        color: #809492;
        font-size: .76rem;
        margin-bottom: .8rem;
    }

    .hero-panel {
        background:
            radial-gradient(circle at 90% 15%,rgba(66,214,189,.12),transparent 30%),
            linear-gradient(125deg,#15262c,#111b22 68%);
        border: 1px solid #2b4648;
        border-radius: 16px;
        padding: 1.35rem 1.5rem;
        margin: .5rem 0 1.3rem;
    }

    .hero-kicker {
        color: var(--teal);
        font-size: .68rem;
        font-weight: 800;
        letter-spacing: .16em;
        text-transform: uppercase;
        margin-bottom: .55rem;
    }

    .hero-title {
        color: #f0f7f5;
        font-family: 'Manrope', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -.04em;
        margin-bottom: .35rem;
    }

    .hero-copy {
        color: #9bb0ad;
        font-size: .88rem;
        line-height: 1.65;
        max-width: 760px;
    }

    /* Inputs */

    div[data-testid="stForm"] {
        background: #111b22;
        border: 1px solid #293b43;
        border-radius: 14px;
        padding: 1.25rem;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: #0d171d !important;
        color: #edf4f3 !important;
        border: 1px solid #30434a !important;
        border-radius: 9px !important;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: var(--teal) !important;
        box-shadow: 0 0 0 1px rgba(66,214,189,.18) !important;
    }

    div[data-testid="stTextArea"] textarea {
        min-height: 145px;
    }

    /* Buttons */

    div.stButton > button,
    div.stFormSubmitButton > button,
    div[data-testid="stDownloadButton"] button {
        border-radius: 9px;
        min-height: 2.75rem;
        font-weight: 700;
        border: 1px solid #35bca6;
        background: #1c9d89;
        color: #071a18;
        transition: all .16s ease;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover,
    div[data-testid="stDownloadButton"] button:hover {
        background: #42d6bd;
        border-color: #42d6bd;
        color: #061714;
        box-shadow: 0 5px 18px rgba(32,185,159,.18);
        transform: translateY(-1px);
    }

    div.stButton > button[kind="secondary"] {
        background: #17242b;
        color: #c4d4d1;
        border: 1px solid #30434a;
    }

    div.stButton > button[kind="secondary"]:hover {
        background: #20343a;
        color: #f0f7f5;
        border-color: #4a6a6a;
    }

    /* Tables, charts and expanders */

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid #293b43;
        border-radius: 11px;
        overflow: hidden;
    }

    [data-testid="stPlotlyChart"] {
        background: #111b22;
        border: 1px solid #263740;
        border-radius: 13px;
        padding: .35rem;
    }

    [data-testid="stExpander"] {
        background: #111b22;
        border: 1px solid #293b43;
        border-radius: 11px;
    }

    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    .report-note {
        background: rgba(66,214,189,.08);
        border: 1px solid rgba(66,214,189,.22);
        border-left: 3px solid var(--teal);
        border-radius: 9px;
        padding: .85rem 1rem;
        color: #b9d9d2;
        font-size: .84rem;
        line-height: 1.6;
        margin: .7rem 0 1rem;
    }

    .footer {
        color: #647875;
        font-size: .72rem;
        text-align: center;
        padding: 1.2rem 0 .3rem;
        border-top: 1px solid #202e35;
        margin-top: 2rem;
    }

    hr {
        border-color: #263740 !important;
    }

    @media (max-width: 900px) {
        .block-container {
            padding: 1.3rem 1rem 2rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 4. SHARED HELPERS
# ============================================================

def page_header(eyebrow, title, subtitle):
    if eyebrow:
        render_markdown(
            f'<div class="eyebrow">{eyebrow}</div>',
            unsafe_allow_html=True
        )

    st.title(title)

    render_markdown(
        f'<div class="page-subtitle">{subtitle}</div>',
        unsafe_allow_html=True
    )


def section_heading(title):
    render_markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True
    )


def load_incident_dataframe():
    incidents = load_incidents() or []
    df = pd.DataFrame(incidents)

    required_columns = [
        "id", "title", "affected_service", "severity",
        "category", "retrieved_count", "created_at", "report"
    ]

    for column in required_columns:
        if column not in df.columns:
            df[column] = None

    if not df.empty:
        df["created_at"] = pd.to_datetime(
            df["created_at"], errors="coerce"
        )

        df["retrieved_count"] = pd.to_numeric(
            df["retrieved_count"], errors="coerce"
        ).fillna(0)

        df["affected_service"] = (
            df["affected_service"].fillna("Unknown")
        )

        df["severity"] = df["severity"].fillna("Unknown")
        df["title"] = df["title"].fillna("Untitled incident")
        df["category"] = df["category"].fillna("Unclassified")

    return incidents, df


def plotly_theme(height=320):
    return {
        "template": "plotly_dark",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "color": "#aebfbc",
            "family": "DM Sans, sans-serif",
            "size": 11
        },
        "margin": {
            "l": 16,
            "r": 16,
            "t": 22,
            "b": 18
        },
        "height": height,
        "colorway": [
            "#42d6bd",
            "#6a9e9a",
            "#83a6c2",
            "#c5a66a",
            "#a38acb"
        ]
    }


# ============================================================
# 5. INCIDENT CLASSIFICATION
# ============================================================

def classify_incident(
    affected_service,
    incident_title,
    description
):
    combined_text = (
        incident_title + " " + description
    ).lower()

    authentication_keywords = [
        "login", "log in", "logged in", "logging in",
        "sign in", "sign-in", "signin",
        "authentication", "auth service",
        "identity provider", "single sign-on",
        "sso", "oauth", "oidc", "token validation",
        "mfa", "multi-factor authentication",
        "session expiration", "session expired"
    ]

    is_authentication_incident = any(
        keyword in combined_text
        for keyword in authentication_keywords
    )

    if (
        is_authentication_incident
        and affected_service in ["Application", "Website", "Other"]
    ):
        return (
            "Authentication / Login Failure",
            "Investigate authentication service availability, "
            "identity provider health, login errors, SSO integration, "
            "token validation, session management and MFA availability."
        )

    # HTTP 503 is recognised for Website and Application.
    if (
        "503" in combined_text
        and affected_service in ["Website", "Application", "Other"]
    ):
        return (
            "Web Application Availability / HTTP 503",
            "Investigate HTTP 503 responses, application health, "
            "server resources, upstream dependencies and proxy logs."
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
        "Investigate reported symptoms, relevant service logs, "
        "system health and dependencies."
    )


# ============================================================
# 6. REPORT SECTION EXTRACTION
# ============================================================

def extract_sections(ai_response):
    sections = {}

    pattern = r"^##\s+(\d+)\.\s+(.+?)\s*$"

    matches = list(
        re.finditer(pattern, ai_response, re.MULTILINE)
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


# ============================================================
# 7. KNOWLEDGE BASE REFERENCES
# ============================================================

def build_knowledge_references(retrieved_results):
    if not retrieved_results:
        return "No relevant knowledge documents were retrieved."

    references = []

    for index, result in enumerate(retrieved_results, start=1):
        reference = (
            f"- Evidence {index}: "
            f"{result['source']} "
            f"(Retrieved chunk {result['chunk']})"
        )

        if reference not in references:
            references.append(reference)

    return "\n".join(references)


# ============================================================
# 8. SAFETY FILTER
# ============================================================

def apply_safety_filter(text):
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
            re.search(pattern, line, re.IGNORECASE)
            for pattern in unsafe_patterns
        )

        if not is_unsafe:
            safe_lines.append(line)

    warning_text = (
        "Before performing any production-changing action, "
        "a qualified technician must review the evidence, "
        "assess the impact and approve the action."
    )

    safe_lines = [
        line for line in safe_lines
        if warning_text.lower() not in line.lower()
    ]

    cleaned_text = "\n".join(safe_lines).strip()

    if cleaned_text:
        cleaned_text += "\n\n"

    return cleaned_text + warning_text


# ============================================================
# 9. BUILD FINAL REPORT
# ============================================================

def build_final_report(
    ai_response,
    retrieved_results,
    severity,
    incident_category,
    incident_title,
    description
):
    sections = extract_sections(ai_response)

    section_defaults = {
        1: (
            "Incident Summary",
            "The incident details require further analysis."
        ),
        2: (
            "Incident Category",
            "Further investigation is required."
        ),
        3: (
            "Severity Assessment",
            "Human validation is required."
        ),
        4: (
            "Possible Technical Causes",
            "Further technical evidence is required."
        ),
        5: (
            "Troubleshooting Steps",
            "Investigate relevant logs, service health, resource "
            "metrics and dependencies."
        ),
        7: (
            "Prevention Recommendations",
            "Establish appropriate monitoring, logging and documented "
            "incident response procedures."
        ),
        8: (
            "Additional Evidence Required",
            "Collect relevant application logs, service health "
            "information and dependency diagnostics."
        )
    }

    report = []

    # Build a confirmed-facts summary from the supplied incident.
    summary = (
        f"The reported incident is **{incident_title}**. "
        f"{description.strip()} "
        "The underlying root cause has not yet been established. "
        "The affected user scope and service status should be treated "
        "as unknown unless confirmed by investigation."
    )

    for section_number in range(1, 9):

        if section_number == 6:
            report.append(
                "## 6. Knowledge Base References\n\n"
                + build_knowledge_references(retrieved_results)
            )
            continue

        title, default_content = section_defaults[section_number]
        section = sections.get(section_number)

        if section:
            title = section["title"]
            content = section["content"]
        else:
            content = default_content

        if section_number == 1:
            title = "Incident Summary"
            content = summary

        elif section_number == 2:
            title = "Incident Category"
            content = (
                f"**{incident_category}**\n\n"
                "This category describes the reported incident type. "
                "It does not confirm the underlying technical root cause."
            )

        elif section_number == 3:
            title = "Severity Assessment"
            content = (
                f"Business Impact: {severity}\n\n"
                f"Initial Severity: {severity}\n\n"
                "Human validation is required. The initial severity "
                "should be reviewed as evidence about the incident "
                "scope and business impact becomes available."
            )

        elif section_number == 5:
            content = apply_safety_filter(content)

        if not content.strip():
            content = default_content

        report.append(
            f"## {section_number}. {title}\n\n{content}"
        )

    return "\n\n".join(report)


# ============================================================
# 10. DASHBOARD
# ============================================================

def show_dashboard():

    incidents, df = load_incident_dataframe()

    page_header(
        "",
        "Incident Command Center",
        "A focused view of incident volume, service impact and "
        "the evidence supporting technical investigations."
    )

    render_markdown(
        """
        <div class="hero-panel">
            <div class="hero-kicker">
                OpsPilot intelligence workspace
            </div>
            <div class="hero-title">
                Evidence-led diagnosis. Clearer decisions.
            </div>
            <div class="hero-copy">
                Review incident patterns, understand affected services
                and track the knowledge evidence used by local
                AI-assisted investigations. Every recommendation
                remains subject to qualified human review.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    section_heading("Incident overview")

    total_incidents = len(df)

    high_critical = (
        int(df["severity"].isin(["High", "Critical"]).sum())
        if total_incidents else 0
    )

    affected_services = (
        int(df["affected_service"].nunique())
        if total_incidents else 0
    )

    average_evidence = (
        float(df["retrieved_count"].mean())
        if total_incidents else 0.0
    )

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    c1.metric("Total incidents", f"{total_incidents:,}")
    c2.metric("High / critical", f"{high_critical:,}")
    c3.metric("Affected services", f"{affected_services:,}")
    c4.metric("Avg. evidence retrieved", f"{average_evidence:.1f}")

    section_heading("Incident analytics")

    left, right = st.columns([1.08, 1], gap="large")

    with left:

        render_markdown(
            """
            <div class="panel-title">Incidents by affected service</div>
            <div class="panel-caption">
                Distribution across recorded services
            </div>
            """,
            unsafe_allow_html=True
        )

        if total_incidents:

            service_counts = (
                df["affected_service"]
                .value_counts()
                .rename_axis("Affected service")
                .reset_index(name="Incidents")
            )

            chart = px.bar(
                service_counts,
                x="Affected service",
                y="Incidents",
                text="Incidents",
                color="Affected service",
                color_discrete_sequence=[
                    "#42d6bd", "#6d9c99", "#7899b5",
                    "#b49a70", "#9a8abd"
                ]
            )

            chart.update_layout(
                **plotly_theme(320),
                showlegend=False
            )

            chart.update_traces(
                marker_line_width=0,
                textposition="outside",
                cliponaxis=False
            )

            chart.update_yaxes(
                title=None,
                rangemode="tozero",
                gridcolor="rgba(145,175,170,.10)",
                zeroline=False
            )

            chart.update_xaxes(title=None, showgrid=False)

            st.plotly_chart(
                chart,
                use_container_width=True,
                config={"displayModeBar": False}
            )

        else:
            st.info(
                "Service analytics will appear after the first incident is saved."
            )

    with right:

        render_markdown(
            """
            <div class="panel-title">Severity distribution</div>
            <div class="panel-caption">
                Initial business-impact classification
            </div>
            """,
            unsafe_allow_html=True
        )

        if total_incidents:

            severity_order = [
                "Low", "Medium", "High", "Critical", "Unknown"
            ]

            severity_counts = (
                df["severity"]
                .value_counts()
                .reindex(severity_order, fill_value=0)
                .rename_axis("Severity")
                .reset_index(name="Incidents")
            )

            severity_counts = severity_counts[
                severity_counts["Incidents"] > 0
            ]

            chart = px.pie(
                severity_counts,
                names="Severity",
                values="Incidents",
                hole=.72,
                color="Severity",
                color_discrete_map={
                    "Low": "#42b995",
                    "Medium": "#d5ad65",
                    "High": "#e27a78",
                    "Critical": "#b28cda",
                    "Unknown": "#718484"
                }
            )

            chart.update_layout(
                **plotly_theme(320),
                legend=dict(
                    orientation="h",
                    y=-.12,
                    x=.5,
                    xanchor="center",
                    font=dict(size=10)
                )
            )

            chart.update_traces(
                textposition="inside",
                textinfo="percent",
                marker=dict(
                    line=dict(color="#111b22", width=3)
                )
            )

            st.plotly_chart(
                chart,
                use_container_width=True,
                config={"displayModeBar": False}
            )

        else:
            st.info(
                "Severity distribution will appear after the first incident is saved."
            )

    section_heading("Incident activity")

    if total_incidents:

        trend_data = df.dropna(subset=["created_at"]).copy()

        if not trend_data.empty:

            trend_data["Date"] = (
                trend_data["created_at"].dt.strftime("%d %b %Y")
            )

            daily_counts = (
                trend_data.groupby("Date", sort=False)
                .size()
                .reset_index(name="Incidents")
            )

            daily_counts["_sort"] = pd.to_datetime(
                daily_counts["Date"],
                format="%d %b %Y",
                errors="coerce"
            )

            daily_counts = daily_counts.sort_values("_sort")

            chart = px.line(
                daily_counts,
                x="Date",
                y="Incidents",
                markers=True
            )

            chart.update_layout(
                **plotly_theme(270),
                showlegend=False
            )

            chart.update_traces(
                line=dict(color="#42d6bd", width=2.7),
                marker=dict(
                    size=8,
                    color="#42d6bd",
                    line=dict(width=2, color="#10201f")
                )
            )

            chart.update_yaxes(
                title=None,
                rangemode="tozero",
                gridcolor="rgba(145,175,170,.10)",
                dtick=1
            )

            chart.update_xaxes(title=None, showgrid=False)

            st.plotly_chart(
                chart,
                use_container_width=True,
                config={"displayModeBar": False}
            )

        else:
            st.info("No valid incident timestamps are available yet.")

    else:
        st.info(
            "Incident activity will appear after an incident has been analysed and saved."
        )

    section_heading("Recent incidents")

    if total_incidents:

        recent = df.sort_values(
            "created_at",
            ascending=False,
            na_position="last"
        )

        recent_display = recent[
            [
                "created_at", "title", "affected_service",
                "severity", "category"
            ]
        ].head(8).copy()

        recent_display["created_at"] = (
            recent_display["created_at"].dt.strftime("%d %b %Y, %I:%M %p")
        )

        recent_display["created_at"] = (
            recent_display["created_at"].fillna("Date unavailable")
        )

        recent_display = recent_display.fillna("—")

        recent_display.columns = [
            "Date & time", "Incident", "Affected service",
            "Severity", "Category"
        ]

        st.dataframe(
            recent_display,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "No incident records yet. Open New Incident to analyse your first incident."
        )


# ============================================================
# 11. NEW INCIDENT PAGE
# ============================================================

def show_new_incident_page():

    page_header(
        "Investigation / Create",
        "New incident",
        "Capture the reported symptoms and let OpsPilot retrieve "
        "relevant technical knowledge for a structured investigation plan."
    )

    render_markdown(
        """
        <div class="report-note">
            <strong>Local analysis:</strong> Incident analysis uses your
            locally running Qwen model through Ollama and the documents
            indexed in your local knowledge base.
        </div>
        """,
        unsafe_allow_html=True
    )

    section_heading("Incident details")

    with st.form("incident_form", clear_on_submit=False):

        incident_title = st.text_input(
            "Incident title",
            placeholder="Example: Database Connection Failure"
        )

        description = st.text_area(
            "Incident description",
            placeholder=(
                "Explain what happened, when it started, what users "
                "are experiencing and what is currently known."
            ),
            height=160
        )

        col1, col2 = st.columns(2, gap="large")

        with col1:
            affected_service = st.selectbox(
                "Affected service",
                [
                    "Website", "Database", "Network",
                    "Application", "Server", "Other"
                ]
            )

        with col2:
            impact = st.selectbox(
                "Business impact",
                ["Low", "Medium", "High", "Critical"]
            )

        submitted = st.form_submit_button(
            "Analyse incident",
            type="primary",
            use_container_width=True
        )

    if not submitted:

        st.caption(
            "Complete the incident details above. No external AI API is used."
        )

        return

    # Validate and clean the two independent fields.
    incident_title = incident_title.strip()
    description = description.strip()

    if not incident_title or not description:

        st.warning(
            "Please enter both the incident title and description."
        )

        return

    # Do not combine the title and description in the saved title.
    severity = impact

    incident_category, investigation_focus = classify_incident(
        affected_service,
        incident_title,
        description
    )

    incident_facts = f"""
Incident Title: {incident_title}

Description: {description}

Affected Service: {affected_service}

Business Impact: {impact}

Initial Severity: {severity}

Incident Category: {incident_category}

Affected User Scope: Not confirmed unless explicitly established.

Root Cause: Not yet identified.

Service Status: Unknown unless explicitly confirmed.
"""

    render_markdown("---")
    section_heading("AI incident analysis")

    try:

        # ----------------------------------------------------
        # RETRIEVAL QUERY
        # ----------------------------------------------------

        if incident_category == "Authentication / Login Failure":

            retrieval_query = f"""
Authentication and login incident.

Incident Title: {incident_title}

Incident Description: {description}

Search for authentication service timeout, identity provider
availability, login failures, SSO, OAuth, OIDC, token validation,
session management, MFA and authentication logs.

Prioritise authentication-specific investigation steps,
possible causes and evidence requirements.
"""

        elif incident_category == "Web Application Availability / HTTP 503":

            retrieval_query = f"""
HTTP 503 Service Unavailable incident.

Incident Title: {incident_title}

Incident Description: {description}

Search for HTTP 503 troubleshooting, application availability,
upstream service health, reverse proxy, load balancer,
server resources and dependency failures.
"""

        elif incident_category == "Database Connectivity / Connection Failure":

            retrieval_query = f"""
Database connection failure incident.

Incident Title: {incident_title}

Incident Description: {description}

Search for database availability, connection errors,
network connectivity, database authentication,
connection pool exhaustion and database logs.
"""

        else:

            retrieval_query = f"""
Affected Service: {affected_service}

Incident Title: {incident_title}

Incident Description: {description}

Incident Category: {incident_category}

Investigation Focus: {investigation_focus}

Find technical information about possible causes,
investigation steps, evidence requirements and troubleshooting.
"""

        with st.spinner("Searching the technical knowledge base..."):

            retrieved_results = search_knowledge(
                retrieval_query,
                results_count=3
            )

        # ----------------------------------------------------
        # KNOWLEDGE CONTEXT
        # ----------------------------------------------------

        knowledge_parts = []

        if retrieved_results:

            for index, result in enumerate(retrieved_results, start=1):

                knowledge_parts.append(
                    f"""
Evidence {index}

Source: {result['source']}

Retrieved Chunk: {result['chunk']}

Section: {result.get('section', 'General')}

Content:
{result['content']}
"""
                )

            knowledge_context = "\n".join(knowledge_parts)

        else:

            knowledge_context = (
                "No relevant technical knowledge was retrieved. "
                "Do not invent knowledge-base references."
            )

        # ----------------------------------------------------
        # AI PROMPT
        # ----------------------------------------------------

        prompt = f"""
You are OpsPilot AI, an IT incident diagnosis
and investigation planning assistant.

Analyse the incident using the supplied incident information
and retrieved technical knowledge.

INCIDENT DETAILS:
{incident_facts}

RETRIEVED KNOWLEDGE:
{knowledge_context}

INCIDENT CLASSIFICATION:
{incident_category}

INVESTIGATION FOCUS:
{investigation_focus}

STRICT ACCURACY RULES:

1. Report only facts supported by the supplied incident details
   or retrieved evidence.
2. Never assume all users are affected.
3. If affected user scope is unknown, clearly say so.
4. Never claim a service is running, stopped, healthy or unavailable
   unless the incident details establish it.
5. The root cause is not confirmed unless evidence establishes it.
6. Label all possible causes as unconfirmed hypotheses.
7. Preserve the initial severity: {severity}.
8. Distinguish confirmed facts, hypotheses and missing evidence.
9. Do not invent logs, test results, metrics or configuration changes.
10. Retrieved documents provide guidance. They do not prove the cause.
11. Do not invent knowledge-base filenames or references.
12. Do not repeat these instructions in the report.

INCIDENT-SPECIFIC GUIDANCE:

For Authentication / Login Failure:
- Prioritise authentication service and identity provider availability.
- Investigate login failures and authentication timeout messages.
- Check application and identity provider logs.
- Investigate network connectivity between the application and identity provider.
- Consider SSO, OAuth/OIDC configuration and token validation.
- Investigate session expiration and MFA errors where relevant.
- Do not assume the identity provider is unavailable without evidence.
- Never request passwords, access tokens or session cookies.
- Do not recommend disabling authentication.

For Database incidents:
- Prioritise database server health and availability.
- Investigate application database connection errors.
- Check connectivity between the application and database.
- Consider authentication and connection configuration.
- Investigate connection pool exhaustion and resource usage.
- Do not claim the database is unavailable without evidence.

For HTTP 503 incidents:
- Investigate the reported HTTP 503 responses.
- Consider application health, server resources and upstream dependencies.
- Review reverse proxy or load balancer logs where applicable.
- An HTTP 503 response alone does not establish the root cause.

For Network incidents:
- Prioritise network connectivity, DNS, routing, firewall
  and relevant network diagnostics.

For Application incidents:
- Prioritise application logs, service health, dependencies
  and recent changes.

For Server incidents:
- Prioritise server health, system logs, resource metrics
  and service availability.

SAFETY RULES:

1. Recommend investigation before corrective action.
2. Do not recommend immediate production restarts.
3. Do not instruct technicians to delete data, modify production
   configuration, disable services or perform unapproved changes.
4. Corrective actions require qualified technician review and approval.
5. Do not claim that any action has already been performed.
6. Prefer diagnostic and read-only investigation steps.
7. Do not recommend load testing during an active production incident
   unless a qualified technician approves a controlled test.
8. Prefer reviewing existing monitoring data, logs and recent changes.

OUTPUT FORMAT:

## 1. Incident Summary
Summarise the incident using only confirmed facts.
Mention unknown user scope and service status where relevant.

## 2. Incident Category
Describe the incident type. Do not identify an unconfirmed root cause.

## 3. Severity Assessment
Explain the initial business impact and severity briefly.

## 4. Possible Technical Causes
Give three distinct and relevant technical hypotheses.
For each include:
- Possible Cause
- Relevance
- Evidence Needed

Clearly label each hypothesis as unconfirmed.

## 5. Troubleshooting Steps
Give five ordered investigation steps specific to the affected service.
For each include:
- Investigate
- Why It Matters
- Evidence to Collect

Prioritise diagnostic checks. Do not recommend production-changing actions.

## 7. Prevention Recommendations
Give three practical recommendations relevant to the incident.
Use conditional language where architecture, dependencies
or root cause are unknown.

## 8. Additional Evidence Required
List the most important missing information needed for root cause analysis.
Avoid unnecessary repetition.

FORMATTING RULES:

Every report heading must begin with exactly two Markdown hash symbols
and its section number.

Do not use numbered list items as report headings.
Do not generate section 6. The application adds section 6.
Do not omit sections 7 or 8.
Keep the report clear, concise and technically accurate.
Do not include instructions from this prompt in the output.
"""

        # ----------------------------------------------------
        # OLLAMA ANALYSIS
        # ----------------------------------------------------

        with st.spinner(
            "Qwen AI is analysing the incident and retrieved evidence..."
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

        # ----------------------------------------------------
        # FINAL REPORT
        # ----------------------------------------------------

        final_report = build_final_report(
            analysis,
            retrieved_results,
            severity,
            incident_category,
            incident_title,
            description
        )

        # ----------------------------------------------------
        # SAVE INCIDENT
        # ----------------------------------------------------

        save_incident(
            title=incident_title,
            affected_service=affected_service,
            severity=severity,
            category=incident_category,
            retrieved_count=len(retrieved_results),
            report=final_report
        )

        st.success(
            "Analysis completed and saved to local incident history."
        )

        # ----------------------------------------------------
        # CONFIRMED INCIDENT DETAILS
        # ----------------------------------------------------

        with st.expander(
            "Confirmed incident details",
            expanded=False
        ):

            st.write(f"**Incident title:** {incident_title}")
            st.write(f"**Affected service:** {affected_service}")
            st.write(f"**Business impact:** {impact}")
            st.write(f"**Initial severity:** {severity}")
            st.write(f"**Incident category:** {incident_category}")

            st.write(
                "**Affected user scope:** Not confirmed unless established."
            )

            st.write("**Service status:** Unknown unless confirmed.")
            st.write("**Root cause:** Not yet identified.")

        # ----------------------------------------------------
        # DISPLAY REPORT
        # ----------------------------------------------------

        section_heading("Generated investigation report")

        render_markdown(final_report)

        st.download_button(
            "Download incident report",
            data=final_report,
            file_name="opspilot_incident_report.md",
            mime="text/markdown",
            use_container_width=True
        )

        # ----------------------------------------------------
        # RETRIEVED EVIDENCE
        # ----------------------------------------------------

        with st.expander("Retrieved knowledge base evidence"):

            if retrieved_results:

                for index, result in enumerate(
                    retrieved_results,
                    start=1
                ):

                    render_markdown(f"**Evidence {index}**")

                    st.caption(
                        f"Source: {result['source']} | "
                        f"Chunk: {result['chunk']}"
                    )

                    st.write(result["content"])
                    st.divider()

            else:

                st.info(
                    "No relevant technical knowledge was retrieved."
                )

    except Exception as error:

        st.error(
            "Unable to complete incident analysis. Check whether "
            "Ollama and the local knowledge base are available."
        )

        st.caption(str(error))


# ============================================================
# 12. INCIDENT HISTORY
# ============================================================

def show_incident_history():

    page_header(
        "Records / Traceability",
        "Incident history",
        "Review previously analysed incidents, inspect their "
        "saved reports and download individual investigation records."
    )

    incidents, df = load_incident_dataframe()

    if not incidents:

        st.info(
            "No saved incidents yet. Completed analyses will appear here."
        )

        return

    section_heading("Record overview")

    st.metric("Saved incident records", len(df))

    display = df[
        [
            "created_at", "title", "affected_service",
            "severity", "category"
        ]
    ].copy()

    display["created_at"] = (
        display["created_at"].dt.strftime("%d %b %Y, %I:%M %p")
    )

    display["created_at"] = (
        display["created_at"].fillna("Date unavailable")
    )

    display = display.fillna("—")

    display.columns = [
        "Date & time", "Incident", "Service",
        "Severity", "Category"
    ]

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )

    section_heading("Saved reports")

    sorted_df = df.sort_values(
        "created_at",
        ascending=False,
        na_position="last"
    )

    for _, incident in sorted_df.iterrows():

        title = incident.get("title") or "Untitled incident"
        created_at = incident.get("created_at")

        created = (
            created_at.strftime("%d %b %Y, %I:%M %p")
            if pd.notna(created_at)
            else "Date unavailable"
        )

        with st.expander(f"{title}  ·  {created}"):

            col1, col2, col3 = st.columns(3)

            col1.write(
                f"**Service**\n\n"
                f"{incident.get('affected_service') or 'Unknown'}"
            )

            col2.write(
                f"**Severity**\n\n"
                f"{incident.get('severity') or 'Unknown'}"
            )

            col3.write(
                f"**Evidence retrieved**\n\n"
                f"{int(incident.get('retrieved_count') or 0)}"
            )

            st.caption(
                incident.get("category") or "Unclassified"
            )

            report = (
                incident.get("report")
                or "No report was saved for this record."
            )

            render_markdown(report)

            st.download_button(
                "Download this report",
                data=report,
                file_name="opspilot_incident_report.md",
                mime="text/markdown",
                key=f"download_{incident.get('id', created)}"
            )


# ============================================================
# 13. KNOWLEDGE BASE
# ============================================================

def show_knowledge_base():

    page_header(
        "Technical references",
        "Knowledge base",
        "The local troubleshooting library used by OpsPilot "
        "during retrieval-augmented incident analysis."
    )

    data_dir = Path("data")

    documents = (
        sorted(
            [
                path
                for path in data_dir.rglob("*")
                if path.is_file()
                and path.suffix.lower() in {
                    ".md", ".txt", ".pdf"
                }
            ]
        )
        if data_dir.exists()
        else []
    )

    if not documents:

        st.warning(
            "No supported knowledge documents were found in the local data folder."
        )

        st.caption(
            "Add Markdown, text or PDF troubleshooting guides to the data folder."
        )

        return

    section_heading("Library overview")

    st.metric("Available source documents", len(documents))

    for path in documents:

        with st.expander(f"{path.name}  ·  {path.suffix.upper()}"):

            if path.suffix.lower() in {".md", ".txt"}:

                try:
                    render_markdown(
                        path.read_text(encoding="utf-8")
                    )

                except OSError as error:
                    st.error(f"Could not read this document: {error}")

            else:

                try:
                    import fitz

                    with fitz.open(path) as pdf:

                        for page_number, page in enumerate(pdf, start=1):

                            page_text = page.get_text().strip()

                            if page_text:

                                render_markdown(f"**Page {page_number}**")
                                st.write(page_text)

                except Exception as error:
                    st.error(f"Could not read this PDF: {error}")


# ============================================================
# 14. ABOUT PAGE
# ============================================================

def show_about():

    page_header(
        "System / About",
        "About OpsPilot AI",
        "A local AI-assisted workspace for structured IT "
        "incident diagnosis and investigation planning."
    )

    render_markdown(
        """
        <div class="hero-panel">
            <div class="hero-kicker">Project overview</div>
            <div class="hero-title">
                From incident description to evidence-led investigation.
            </div>
            <div class="hero-copy">
                OpsPilot AI helps technical teams organise incident
                information, retrieve relevant troubleshooting knowledge
                and review structured investigation recommendations.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    section_heading("How it works")

    workflow = [
        (
            "01", "Capture",
            "A technician enters the incident title, description, "
            "affected service and business impact."
        ),
        (
            "02", "Classify",
            "Python identifies an initial incident category and "
            "retains the selected impact level."
        ),
        (
            "03", "Retrieve",
            "ChromaDB searches the local troubleshooting knowledge base."
        ),
        (
            "04", "Analyse",
            "The local Qwen model prepares possible causes and "
            "investigation steps using retrieved evidence."
        ),
        (
            "05", "Review",
            "The report is presented for qualified human review."
        ),
        (
            "06", "Record",
            "The completed analysis is saved to local incident history."
        )
    ]

    for number, heading, description in workflow:

        with st.container():

            col1, col2 = st.columns([.12, .88])

            with col1:

                render_markdown(
                    f"""
                    <div style="
                        color:#42d6bd;
                        font-family:Manrope,sans-serif;
                        font-weight:800;
                        font-size:1.05rem;
                        padding-top:.1rem;
                    ">
                        {number}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                render_markdown(f"**{heading}**")
                st.caption(description)

    section_heading("Technology stack")

    st.write(
        "Python · Streamlit · Ollama · Qwen 2.5 3B · "
        "ChromaDB · RAG · Plotly · Pandas · PyMuPDF"
    )

    render_markdown(
        """
        <div class="report-note">
            <strong>Prototype limitation:</strong>
            OpsPilot AI does not monitor live infrastructure or
            automatically repair incidents. Its recommendations
            are AI-generated and require technician verification.
            The safety filter is a basic prototype safeguard,
            not a complete production safety system.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 15. SIDEBAR NAVIGATION
# ============================================================

PAGES = {
    "Dashboard": "▦   Dashboard",
    "New Incident": "＋   New incident",
    "Incident History": "◷   Incident history",
    "Knowledge Base": "▤   Knowledge base",
    "About": "ⓘ   About"
}

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Dashboard"


def navigate_to(page):
    st.session_state.selected_page = page


render_sidebar_markdown(
    """
    <div class="brand-lockup">
        <div class="brand-row">
            <div class="brand-mark">✳</div>
            <div class="brand-name">OpsPilot AI</div>
        </div>
        <div class="brand-tag">
            IT INCIDENT INTELLIGENCE
        </div>
    </div>

    <div class="sidebar-label">
        Workspace
    </div>
    """,
    unsafe_allow_html=True
)

for page, label in PAGES.items():

    st.sidebar.button(
        label,
        key=f"nav_{page.lower().replace(' ', '_')}",
        type=(
            "primary"
            if st.session_state.selected_page == page
            else "secondary"
        ),
        use_container_width=True,
        on_click=navigate_to,
        args=(page,)
    )


render_sidebar_markdown(
    """
    <div class="sidebar-status">
        <div class="status-line">
            <span class="status-dot"></span>
            Local AI workspace
        </div>
        <div class="status-detail">
            Ollama · RAG · Human review<br>
            Prototype version 2.2
        </div>
    </div>

    <div style="
        padding:1rem .35rem;
        color:#748985;
        font-size:.75rem;
        line-height:1.65;
    ">
        Evidence-led diagnosis.<br>
        Human-approved resolution.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 16. PAGE ROUTING
# ============================================================

selected_page = st.session_state.selected_page

if selected_page == "Dashboard":
    show_dashboard()

elif selected_page == "New Incident":
    show_new_incident_page()

elif selected_page == "Incident History":
    show_incident_history()

elif selected_page == "Knowledge Base":
    show_knowledge_base()

elif selected_page == "About":
    show_about()


# ============================================================
# 17. FOOTER
# ============================================================

render_markdown(
    """
    <div class="footer">
        OpsPilot AI · Local AI prototype · Version 2.2
        · AI-generated recommendations require human review.
    </div>
    """,
    unsafe_allow_html=True
)
