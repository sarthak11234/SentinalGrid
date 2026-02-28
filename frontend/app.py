"""
SentinalGrid — Streamlit Frontend
Clean editorial light-theme UI with Google Login, Model Selection, and Campaign Management.
"""

import streamlit as st
import requests
import pandas as pd
import json
<<<<<<< HEAD
import base64
from urllib.parse import parse_qs
from streamlit_cookies_controller import CookieController
=======
from urllib.parse import parse_qs
>>>>>>> 67cfd7af8a57913b398a9397db516ec204e84fab

# ── Config ──
API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="SentinalGrid",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

<<<<<<< HEAD
cookie_controller = CookieController()

<<<<<<< HEAD
# ══════════════════════════════════════════════
# CUSTOM CSS — Editorial Light Theme
# ══════════════════════════════════════════════

=======
=======
>>>>>>> 67cfd7af8a57913b398a9397db516ec204e84fab
# ── Custom CSS ──
>>>>>>> 7910f852176ee4f3bb2a77b6a4f52c715ae73185
st.markdown("""
<style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Source+Sans+3:wght@300;400;500;600&display=swap');

    /* ── CSS Variables ── */
    :root {
        --bg: #FAFAF8;
        --surface: #FFFFFF;
        --border: #E8E5E0;
        --text: #1A1A1A;
        --text-soft: #6B6560;
        --accent: #D4644A;
        --accent-soft: #FFF0EC;
        --success: #3A9E6F;
        --success-soft: #EDFAF3;
        --warning: #D4922A;
        --warning-soft: #FFF8ED;
        --sidebar-bg: #F4F2EE;
        --font-heading: 'DM Sans', sans-serif;
        --font-body: 'Source Sans 3', sans-serif;
    }

    /* ── Global Overrides ── */
    .stApp {
        background-color: var(--bg) !important;
        font-family: var(--font-body) !important;
        color: var(--text) !important;
    }

    /* ── Main content area ── */
    .main .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1100px !important;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border) !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
    }
    section[data-testid="stSidebar"] * {
        font-family: var(--font-body) !important;
    }

    /* ── Headings ── */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: var(--font-heading) !important;
        color: var(--text) !important;
        letter-spacing: -0.01em;
    }
    h1, .stMarkdown h1 { font-weight: 700 !important; font-size: 1.85rem !important; }
    h2, .stMarkdown h2 { font-weight: 600 !important; font-size: 1.35rem !important; }
    h3, .stMarkdown h3 { font-weight: 600 !important; font-size: 1.1rem !important; }

    /* ── Buttons ── */
    .stButton > button {
        font-family: var(--font-body) !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        border: 1px solid var(--border) !important;
        background: var(--surface) !important;
        color: var(--text) !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    }
    .stButton > button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        box-shadow: 0 2px 8px rgba(212,100,74,0.12) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* ── Primary action buttons ── */
    .stFormSubmitButton > button,
    button[kind="primary"] {
        background: var(--accent) !important;
        color: #FFFFFF !important;
        border-color: var(--accent) !important;
        font-weight: 600 !important;
    }
    .stFormSubmitButton > button:hover,
    button[kind="primary"]:hover {
        background: #C45A42 !important;
        border-color: #C45A42 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(212,100,74,0.25) !important;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        font-family: var(--font-body) !important;
        border-radius: 8px !important;
        border-color: var(--border) !important;
        background: var(--surface) !important;
        transition: border-color 0.2s ease !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(212,100,74,0.1) !important;
    }

    /* ── File uploader ── */
    .stFileUploader {
        border-radius: 10px !important;
    }
    .stFileUploader > div {
        border-color: var(--border) !important;
        border-radius: 10px !important;
        background: var(--surface) !important;
    }

    /* ── Dataframes ── */
    .stDataFrame {
        border-radius: 10px !important;
        overflow: hidden !important;
        border: 1px solid var(--border) !important;
    }

    /* ── Metrics ── */
    [data-testid="stMetricValue"] {
        font-family: var(--font-heading) !important;
        font-weight: 700 !important;
        color: var(--text) !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: var(--font-body) !important;
        color: var(--text-soft) !important;
        font-size: 0.85rem !important;
    }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        font-family: var(--font-body) !important;
        font-weight: 500 !important;
        background: var(--surface) !important;
        border-radius: 8px !important;
        border: 1px solid var(--border) !important;
    }

    /* ── Alert / info / success / warning boxes ── */
    .stAlert {
        border-radius: 8px !important;
        font-family: var(--font-body) !important;
    }

    /* ── Progress bar ── */
    .stProgress > div > div > div {
        background-color: var(--accent) !important;
        border-radius: 999px !important;
    }

    /* ── Dividers ── */
    hr {
        border-color: var(--border) !important;
        opacity: 0.5;
    }

    /* ── Radio buttons (sidebar nav) ── */
    .stRadio > div {
        gap: 0.15rem !important;
    }
    .stRadio > div > label {
        font-family: var(--font-body) !important;
        padding: 0.55rem 0.75rem !important;
        border-radius: 8px !important;
        transition: background 0.2s ease !important;
    }
    .stRadio > div > label:hover {
        background: rgba(212,100,74,0.06) !important;
    }
    .stRadio > div > label[data-checked="true"],
    .stRadio > div > label[aria-checked="true"] {
        background: var(--accent-soft) !important;
    }

    /* ── Fade-in animation ── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main .block-container {
        animation: fadeInUp 0.4s ease-out !important;
    }

    /* ── Custom component styles ── */
    .sg-logo {
        font-family: var(--font-heading);
        font-size: 1.55rem;
        font-weight: 700;
        color: var(--text);
        letter-spacing: -0.02em;
        margin-bottom: 0.15rem;
    }
    .sg-logo-accent {
        color: var(--accent);
    }
    .sg-tagline {
        font-family: var(--font-body);
        font-size: 0.8rem;
        color: var(--text-soft);
        margin-bottom: 1.2rem;
        letter-spacing: 0.02em;
    }
    .sg-user-badge {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 0.75rem 0.9rem;
        margin-bottom: 0.8rem;
    }
    .sg-user-badge .name {
        font-family: var(--font-heading);
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--text);
    }
    .sg-user-badge .email {
        font-family: var(--font-body);
        font-size: 0.78rem;
        color: var(--text-soft);
        margin-top: 2px;
    }
    .sg-stat-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.1rem 1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }
    .sg-stat-card:hover {
        box-shadow: 0 3px 12px rgba(0,0,0,0.07);
        transform: translateY(-2px);
    }
    .sg-stat-card .icon { font-size: 1.3rem; margin-bottom: 0.3rem; }
    .sg-stat-card .value {
        font-family: var(--font-heading);
        font-weight: 700;
        font-size: 1.6rem;
        color: var(--text);
        line-height: 1.2;
    }
    .sg-stat-card .label {
        font-family: var(--font-body);
        font-size: 0.78rem;
        color: var(--text-soft);
        margin-top: 0.2rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .sg-section-label {
        font-family: var(--font-heading);
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-soft);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
        margin-top: 0.2rem;
    }
    .sg-page-desc {
        font-family: var(--font-body);
        color: var(--text-soft);
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    .sg-tip {
        background: var(--accent-soft);
        border-left: 3px solid var(--accent);
        border-radius: 0 8px 8px 0;
        padding: 0.65rem 0.9rem;
        font-family: var(--font-body);
        font-size: 0.85rem;
        color: var(--text);
        margin-bottom: 1.2rem;
    }
    .sg-status-badge {
        display: inline-block;
        font-family: var(--font-body);
        font-weight: 600;
        font-size: 0.75rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
    }
    .sg-status-draft { background: #F0EFED; color: var(--text-soft); }
    .sg-status-running { background: var(--warning-soft); color: var(--warning); }
    .sg-status-completed { background: var(--success-soft); color: var(--success); }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# AUTH HELPERS
# ══════════════════════════════════════════════

def _check_login():
<<<<<<< HEAD
    """Check for token in URL query params or browser cookies."""
    params = st.query_params
    token = params.get("token", None)

    if token:
        cookie_controller.set("token", token)
        st.query_params.clear()
        st.rerun()
    else:
        token = cookie_controller.get("token")

    if token:
        try:
<<<<<<< HEAD
=======
            # Decode the token payload (base64 part before the signature)
=======
    """Check for token in URL query params (returned from Google OAuth callback)."""
    params = st.query_params
    token = params.get("token", None)
    if token:
        # Verify the token with the backend
        try:
            # Decode the token payload (base64 part before the signature)
            import base64
>>>>>>> 67cfd7af8a57913b398a9397db516ec204e84fab
>>>>>>> 7910f852176ee4f3bb2a77b6a4f52c715ae73185
            data_part = token.rsplit(".", 1)[0]
            padding = 4 - len(data_part) % 4
            if padding != 4:
                data_part += "=" * padding
            payload = json.loads(base64.urlsafe_b64decode(data_part))
            st.session_state["user"] = payload
            st.session_state["token"] = token
<<<<<<< HEAD
=======
            # Clear the URL params
            st.query_params.clear()
>>>>>>> 67cfd7af8a57913b398a9397db516ec204e84fab
        except Exception:
            pass

    return st.session_state.get("user", None)


def _logout():
<<<<<<< HEAD
    """Clear session state and cookies."""
    for key in ["user", "token"]:
        st.session_state.pop(key, None)
    cookie_controller.remove("token")
=======
    """Clear session state."""
    for key in ["user", "token"]:
        st.session_state.pop(key, None)
>>>>>>> 67cfd7af8a57913b398a9397db516ec204e84fab
    st.rerun()


# ══════════════════════════════════════════════
# HELPER: get user email
# ══════════════════════════════════════════════

def _user_email():
    return st.session_state.get("user", {}).get("email", "anonymous@example.com")


def _status_badge(status):
    """Return HTML for a styled status badge."""
    cls = {
        "draft": "sg-status-draft",
        "running": "sg-status-running",
        "completed": "sg-status-completed",
    }.get(status, "sg-status-draft")
    return f'<span class="sg-status-badge {cls}">{status}</span>'


# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════

user = _check_login()

with st.sidebar:
    st.markdown(
        '<div class="sg-logo">📊 Sentinal<span class="sg-logo-accent">Grid</span></div>'
        '<div class="sg-tagline">Agentic Spreadsheet & Communication Platform</div>',
        unsafe_allow_html=True,
    )

    # ── User info / Login ──
    if user:
        st.markdown(f"""
        <div class="sg-user-badge">
            <div class="name">👤 {user.get('name', 'User')}</div>
            <div class="email">{user.get('email', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            _logout()
    else:
        st.info("Sign in to save your campaigns")
        if st.button("Sign in with Google", use_container_width=True):
            st.markdown(f"[Click here to sign in]({API_BASE}/auth/login)")

    st.divider()

    # ── API Status ──
    try:
        health = requests.get(f"{API_BASE}/health", timeout=3)
        if health.status_code == 200:
            st.success("Backend connected")
        else:
            st.error("Backend error")
    except requests.ConnectionError:
        st.error("Backend not running")

    st.divider()

    # ── Model Selector ──
    st.markdown('<div class="sg-section-label">AI Model</div>', unsafe_allow_html=True)
    try:
        models_resp = requests.get(f"{API_BASE}/settings/models", timeout=3)
        if models_resp.status_code == 200:
            models_data = models_resp.json()
            current_model = models_data["current_model"]
            available_models = models_data["available_models"]

            selected_model = st.selectbox(
                "Select Model",
                options=available_models,
                index=available_models.index(current_model) if current_model in available_models else 0,
                key="model_selector",
                label_visibility="collapsed",
            )

            if selected_model != current_model:
                update_resp = requests.post(
                    f"{API_BASE}/settings/models",
                    json={"model": selected_model},
                    timeout=3,
                )
                if update_resp.status_code == 200:
                    st.success(f"Model → {selected_model}")
                    st.rerun()
    except requests.ConnectionError:
        st.caption("Cannot load models")

    st.divider()

    # ── Navigation ──
    st.markdown('<div class="sg-section-label">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigate",
        ["New Campaign", "Dashboard", "Review Queue", "Manual Reply"],
        index=0,
        label_visibility="collapsed",
    )


# ══════════════════════════════════════════════
# PAGE 1: New Campaign
# ══════════════════════════════════════════════

if page == "New Campaign":
    st.header("Create New Campaign")
    st.markdown(
        '<div class="sg-page-desc">'
        'Upload your data and write a prompt — the AI will draft personalized messages for each row.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sg-tip">'
        '💡 <strong>Tip:</strong> Include a column named <code>email</code> or <code>phone</code>/<code>whatsapp</code> for auto-channel detection.'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.form("campaign_form"):
        name = st.text_input("Campaign Name", placeholder="e.g., Marathon Start Times")
        master_prompt = st.text_area(
            "Master Prompt",
            placeholder="e.g., Send each contestant their individual start time and ask them to confirm availability.",
            height=100,
        )
        uploaded_file = st.file_uploader("Upload Data (CSV or XLSX)", type=["csv", "xlsx", "xls"])
        submitted = st.form_submit_button("Create Campaign", use_container_width=True)

    if submitted:
        if not name or not master_prompt or not uploaded_file:
            st.error("Please fill in all fields and upload a file.")
        else:
            with st.spinner("Creating campaign..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {
                        "name": name,
                        "master_prompt": master_prompt,
                        "user_email": _user_email(),
                    }
                    resp = requests.post(f"{API_BASE}/campaigns", data=data, files=files)

                    if resp.status_code == 200:
                        campaign = resp.json()
                        st.success(f"Campaign **{campaign['name']}** created! (ID: {campaign['id']})")

                        uploaded_file.seek(0)
                        if uploaded_file.name.endswith(".csv"):
                            df = pd.read_csv(uploaded_file)
                        else:
                            df = pd.read_excel(uploaded_file)
                        st.subheader("Data Preview")
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.error(f"Error: {resp.text}")
                except requests.ConnectionError:
                    st.error("Cannot connect to the backend server.")

    # Preview before submit
    if uploaded_file and not submitted:
        st.subheader("File Preview")
        try:
            if uploaded_file.name.endswith(".csv"):
                df_preview = pd.read_csv(uploaded_file)
            else:
                df_preview = pd.read_excel(uploaded_file)
            st.dataframe(df_preview, use_container_width=True)

            # Show detected channels
            cols = df_preview.columns.tolist()
            email_col = next((c for c in cols if "email" in c.lower() or "mail" in c.lower()), None)
            phone_col = next((c for c in cols if any(k in c.lower() for k in ["phone", "mobile", "whatsapp", "cell"])), None)

            if email_col and phone_col:
                st.info(f"📧 Email column: `{email_col}` · 📱 Phone column: `{phone_col}` — WhatsApp preferred when phone available")
            elif email_col:
                st.info(f"📧 Email column detected: `{email_col}`")
            elif phone_col:
                st.info(f"📱 Phone/WhatsApp column detected: `{phone_col}`")
            else:
                st.warning("No email or phone column detected. Messages will be drafted but not sent.")

            st.caption(f"{len(df_preview)} rows × {len(df_preview.columns)} columns")
            uploaded_file.seek(0)
        except Exception as e:
            st.error(f"Could not preview file: {e}")


# ══════════════════════════════════════════════
# PAGE 2: Dashboard
# ══════════════════════════════════════════════

elif page == "Dashboard":
    st.header("Campaign Dashboard")

    try:
        resp = requests.get(f"{API_BASE}/campaigns")
        campaigns = resp.json().get("campaigns", [])
    except requests.ConnectionError:
        st.error("Cannot connect to backend.")
        campaigns = []

    if not campaigns:
        st.info("No campaigns yet. Create one from the sidebar.")
    else:
        campaign_names = {c["id"]: f"{c['name']}  ·  ID {c['id']}" for c in campaigns}
        selected_id = st.selectbox(
            "Select Campaign",
            options=list(campaign_names.keys()),
            format_func=lambda x: campaign_names[x],
        )

        if selected_id:
            detail_resp = requests.get(f"{API_BASE}/campaigns/{selected_id}")
            detail = detail_resp.json()
            campaign = detail["campaign"]
            rows = detail["rows"]
            stats = detail["stats"]

            # Status + launch
            col_status, col_launch = st.columns([3, 1])
            with col_status:
                st.markdown(
                    f"**Status:** {_status_badge(campaign['status'])}",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Prompt:** {campaign['master_prompt']}")
            with col_launch:
                if campaign["status"] in ("draft", "completed"):
                    if st.button("Launch Campaign", use_container_width=True):
                        launch_resp = requests.post(f"{API_BASE}/campaigns/{selected_id}/launch")
                        if launch_resp.status_code == 200:
                            st.success("Campaign launched! Refresh to see progress.")
                            st.rerun()
                        else:
                            st.error(f"Error: {launch_resp.text}")
                elif campaign["status"] == "running":
                    st.warning("Campaign is running...")
                    if st.button("Refresh", use_container_width=True):
                        st.rerun()

            # Stats
            st.markdown("---")
            st.markdown('<div class="sg-section-label">Statistics</div>', unsafe_allow_html=True)
            stat_cols = st.columns(5)
            stat_items = [
                ("Total", stats.get("total", 0), "📋"),
                ("Pending", stats.get("pending", 0), "⏳"),
                ("Sent", stats.get("sent", 0), "📤"),
                ("Replied", stats.get("replied", 0), "✅"),
                ("Review", stats.get("review", 0), "⚠️"),
            ]
            for col, (label, value, icon) in zip(stat_cols, stat_items):
                with col:
                    st.markdown(
                        f'<div class="sg-stat-card">'
                        f'<div class="icon">{icon}</div>'
                        f'<div class="value">{value}</div>'
                        f'<div class="label">{label}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            # Progress
            st.markdown("")
            total = stats.get("total", 1) or 1
            progress = (stats.get("sent", 0) + stats.get("replied", 0)) / total
            st.progress(progress, text=f"{progress:.0%} complete")

            # Data table
            st.markdown("---")
            st.markdown('<div class="sg-section-label">Data Rows</div>', unsafe_allow_html=True)
            if rows:
                df_rows = pd.DataFrame([{
                    "Row": r["row_index"],
                    "Channel": "📱 WhatsApp" if r.get("channel") == "whatsapp" else "📧 Email",
                    "Contact": r.get("contact_phone") or r.get("contact_email", "—"),
                    "Status": r["message_status"],
                    "Message": (r.get("outbound_message") or "")[:80] + "..." if r.get("outbound_message") and len(r.get("outbound_message", "")) > 80 else r.get("outbound_message", "—"),
                    "Reply": r.get("reply_text", "—"),
                    "Confidence": r.get("confidence", "—"),
                } for r in rows])
                st.dataframe(df_rows, use_container_width=True, hide_index=True)
            else:
                st.info("No data rows.")


# ══════════════════════════════════════════════
# PAGE 3: Review Queue
# ══════════════════════════════════════════════

elif page == "Review Queue":
    st.header("Review Queue")
    st.markdown(
        '<div class="sg-page-desc">Rows flagged for human review due to low confidence.</div>',
        unsafe_allow_html=True,
    )

    try:
        resp = requests.get(f"{API_BASE}/campaigns")
        campaigns = resp.json().get("campaigns", [])
    except requests.ConnectionError:
        st.error("Cannot connect to backend.")
        campaigns = []

    if campaigns:
        campaign_names = {c["id"]: c["name"] for c in campaigns}
        selected_id = st.selectbox(
            "Select Campaign",
            options=list(campaign_names.keys()),
            format_func=lambda x: campaign_names[x],
            key="review_campaign",
        )

        if selected_id:
            review_resp = requests.get(f"{API_BASE}/campaigns/{selected_id}/reviews")
            review_rows = review_resp.json() if review_resp.status_code == 200 else []

            if not review_rows:
                st.success("No rows need review!")
            else:
                st.warning(f"{len(review_rows)} row(s) need your attention.")

                for row in review_rows:
                    channel_icon = "📱" if row.get("channel") == "whatsapp" else "📧"
                    contact = row.get("contact_phone") or row.get("contact_email", "Unknown")
                    with st.expander(f"{channel_icon} Row {row['row_index']} — {contact}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Original Data:**")
                            st.json(row["row_data"])
                            st.markdown("**Sent Message:**")
                            st.text(row.get("outbound_message", "—"))
                        with col2:
                            st.markdown("**Reply Received:**")
                            st.text(row.get("reply_text", "—"))
                            st.markdown(f"**Confidence:** `{row.get('confidence', '—')}`")
                            st.markdown("**Suggested Update:**")
                            st.json(row.get("suggested_update", {}))

                        btn1, btn2 = st.columns(2)
                        with btn1:
                            if st.button("Approve", key=f"approve_{row['id']}"):
                                requests.post(
                                    f"{API_BASE}/campaigns/{selected_id}/rows/{row['id']}/review",
                                    json={"action": "approve"},
                                )
                                st.rerun()
                        with btn2:
                            if st.button("Reject", key=f"reject_{row['id']}"):
                                requests.post(
                                    f"{API_BASE}/campaigns/{selected_id}/rows/{row['id']}/review",
                                    json={"action": "reject"},
                                )
                                st.rerun()


# ══════════════════════════════════════════════
# PAGE 4: Manual Reply
# ══════════════════════════════════════════════

elif page == "Manual Reply":
    st.header("Manual Reply Input")
    st.markdown(
        '<div class="sg-page-desc">Paste a reply from a recipient to simulate an inbound webhook.</div>',
        unsafe_allow_html=True,
    )

    try:
        resp = requests.get(f"{API_BASE}/campaigns")
        campaigns = resp.json().get("campaigns", [])
    except requests.ConnectionError:
        st.error("Cannot connect to backend.")
        campaigns = []

    if campaigns:
        campaign_names = {c["id"]: c["name"] for c in campaigns}
        selected_id = st.selectbox(
            "Select Campaign",
            options=list(campaign_names.keys()),
            format_func=lambda x: campaign_names[x],
            key="reply_campaign",
        )

        if selected_id:
            detail_resp = requests.get(f"{API_BASE}/campaigns/{selected_id}")
            detail = detail_resp.json()
            sent_rows = [r for r in detail["rows"] if r["message_status"] == "sent"]

            if not sent_rows:
                st.info("No sent messages to reply to yet. Launch a campaign first.")
            else:
                row_options = {
                    r["id"]: f"Row {r['row_index']} — {r.get('contact_phone') or r.get('contact_email', 'Unknown')}"
                    for r in sent_rows
                }
                selected_row_id = st.selectbox(
                    "Select Row",
                    options=list(row_options.keys()),
                    format_func=lambda x: row_options[x],
                )

                selected_row = next(r for r in sent_rows if r["id"] == selected_row_id)
                st.markdown("**Message that was sent:**")
                st.text(selected_row.get("outbound_message", "—"))

                reply_text = st.text_area("Paste the reply:", height=100)

                if st.button("Process Reply", use_container_width=True):
                    if not reply_text:
                        st.error("Please enter a reply.")
                    else:
                        with st.spinner("Processing reply with AI..."):
                            reply_resp = requests.post(
                                f"{API_BASE}/webhooks/manual-reply",
                                json={"data_row_id": selected_row_id, "reply_text": reply_text},
                            )
                            if reply_resp.status_code == 200:
                                result = reply_resp.json()
                                st.success("Reply processed!")
                                st.markdown(f"**Intent:** `{result.get('intent')}`")
                                st.markdown(f"**Confidence:** `{result.get('confidence')}`")
                                if result.get("needs_review"):
                                    st.warning("Low confidence — row flagged for review.")
                                else:
                                    st.success("Row updated automatically.")
                                st.json(result.get("suggested_update", {}))
                            else:
                                st.error(f"Error: {reply_resp.text}")
