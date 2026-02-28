"""
SentinalGrid — Streamlit Frontend
Single-file UI with Google Login, Model Selection, and Campaign Management.
"""

import streamlit as st
import requests
import pandas as pd
import json
from urllib.parse import parse_qs

# ── Config ──
API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="SentinalGrid",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #888;
        margin-bottom: 1.5rem;
    }
    .user-badge {
        background: linear-gradient(135deg, #667eea33, #764ba233);
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# AUTH HELPERS
# ══════════════════════════════════════════════

def _check_login():
    """Check for token in URL query params (returned from Google OAuth callback)."""
    params = st.query_params
    token = params.get("token", None)
    if token:
        # Verify the token with the backend
        try:
            # Decode the token payload (base64 part before the signature)
            import base64
            data_part = token.rsplit(".", 1)[0]
            # Add padding if needed
            padding = 4 - len(data_part) % 4
            if padding != 4:
                data_part += "=" * padding
            payload = json.loads(base64.urlsafe_b64decode(data_part))
            st.session_state["user"] = payload
            st.session_state["token"] = token
            # Clear the URL params
            st.query_params.clear()
        except Exception:
            pass

    return st.session_state.get("user", None)


def _logout():
    """Clear session state."""
    for key in ["user", "token"]:
        st.session_state.pop(key, None)
    st.rerun()


# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════

user = _check_login()

with st.sidebar:
    st.markdown('<div class="main-header">📊 SentinalGrid</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Agentic Spreadsheet & Communication Platform</div>', unsafe_allow_html=True)

    # ── User info / Login ──
    if user:
        st.markdown(f"""
        <div class="user-badge">
            👤 <strong>{user.get('name', 'User')}</strong><br>
            <small>{user.get('email', '')}</small>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            _logout()
    else:
        st.info("Sign in to save your campaigns")
        if st.button("🔐 Sign in with Google", use_container_width=True):
            st.markdown(f"[Click here to sign in]({API_BASE}/auth/login)")

    st.divider()

    # ── API Status ──
    try:
        health = requests.get(f"{API_BASE}/health", timeout=3)
        if health.status_code == 200:
            st.success("🟢 Backend connected")
        else:
            st.error("🔴 Backend error")
    except requests.ConnectionError:
        st.error("🔴 Backend not running")

    st.divider()

    # ── Model Selector ──
    st.markdown("### 🤖 AI Model")
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
    page = st.radio(
        "Navigate",
        ["🆕 New Campaign", "📋 Dashboard", "⚠️ Review Queue", "💬 Manual Reply"],
        index=0,
    )


# ══════════════════════════════════════════════
# HELPER: get user email
# ══════════════════════════════════════════════

def _user_email():
    return st.session_state.get("user", {}).get("email", "anonymous@example.com")


# ══════════════════════════════════════════════
# PAGE 1: New Campaign
# ══════════════════════════════════════════════

if page == "🆕 New Campaign":
    st.header("🆕 Create New Campaign")
    st.markdown("Upload your data and write a prompt — the AI will draft personalized messages for each row.")
    st.caption("💡 **Tip:** Include a column named `email` or `phone`/`whatsapp` for auto-channel detection.")

    with st.form("campaign_form"):
        name = st.text_input("Campaign Name", placeholder="e.g., Marathon Start Times")
        master_prompt = st.text_area(
            "Master Prompt",
            placeholder="e.g., Send each contestant their individual start time and ask them to confirm availability.",
            height=100,
        )
        uploaded_file = st.file_uploader("Upload Data (CSV or XLSX)", type=["csv", "xlsx", "xls"])
        submitted = st.form_submit_button("📤 Create Campaign", use_container_width=True)

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
                        st.success(f"✅ Campaign **{campaign['name']}** created! (ID: {campaign['id']})")

                        uploaded_file.seek(0)
                        if uploaded_file.name.endswith(".csv"):
                            df = pd.read_csv(uploaded_file)
                        else:
                            df = pd.read_excel(uploaded_file)
                        st.subheader("📊 Data Preview")
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.error(f"Error: {resp.text}")
                except requests.ConnectionError:
                    st.error("Cannot connect to the backend server.")

    # Preview before submit
    if uploaded_file and not submitted:
        st.subheader("📊 File Preview")
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
                st.info(f"📧 Email column: `{email_col}` | 📱 Phone column: `{phone_col}` — WhatsApp will be preferred when phone is available")
            elif email_col:
                st.info(f"📧 Email column detected: `{email_col}`")
            elif phone_col:
                st.info(f"📱 Phone/WhatsApp column detected: `{phone_col}`")
            else:
                st.warning("⚠️ No email or phone column detected. Messages will be drafted but not sent.")

            st.caption(f"{len(df_preview)} rows × {len(df_preview.columns)} columns")
            uploaded_file.seek(0)
        except Exception as e:
            st.error(f"Could not preview file: {e}")


# ══════════════════════════════════════════════
# PAGE 2: Dashboard
# ══════════════════════════════════════════════

elif page == "📋 Dashboard":
    st.header("📋 Campaign Dashboard")

    try:
        resp = requests.get(f"{API_BASE}/campaigns")
        campaigns = resp.json().get("campaigns", [])
    except requests.ConnectionError:
        st.error("Cannot connect to backend.")
        campaigns = []

    if not campaigns:
        st.info("No campaigns yet. Create one from the sidebar!")
    else:
        campaign_names = {c["id"]: f"{c['name']} (ID: {c['id']})" for c in campaigns}
        selected_id = st.selectbox("Select Campaign", options=list(campaign_names.keys()),
                                    format_func=lambda x: campaign_names[x])

        if selected_id:
            detail_resp = requests.get(f"{API_BASE}/campaigns/{selected_id}")
            detail = detail_resp.json()
            campaign = detail["campaign"]
            rows = detail["rows"]
            stats = detail["stats"]

            # Status + launch
            col_status, col_launch = st.columns([3, 1])
            with col_status:
                st.markdown(f"**Status:** `{campaign['status'].upper()}`")
                st.markdown(f"**Prompt:** {campaign['master_prompt']}")
            with col_launch:
                if campaign["status"] in ("draft", "completed"):
                    if st.button("🚀 Launch Campaign", use_container_width=True):
                        launch_resp = requests.post(f"{API_BASE}/campaigns/{selected_id}/launch")
                        if launch_resp.status_code == 200:
                            st.success("Campaign launched! Refresh to see progress.")
                            st.rerun()
                        else:
                            st.error(f"Error: {launch_resp.text}")
                elif campaign["status"] == "running":
                    st.warning("Campaign is running...")
                    if st.button("🔄 Refresh", use_container_width=True):
                        st.rerun()

            # Stats
            st.subheader("📊 Statistics")
            cols = st.columns(5)
            stat_items = [
                ("Total", stats.get("total", 0), "📋"),
                ("Pending", stats.get("pending", 0), "⏳"),
                ("Sent", stats.get("sent", 0), "📤"),
                ("Replied", stats.get("replied", 0), "✅"),
                ("Review", stats.get("review", 0), "⚠️"),
            ]
            for col, (label, value, icon) in zip(cols, stat_items):
                with col:
                    st.metric(label=f"{icon} {label}", value=value)

            # Progress
            total = stats.get("total", 1) or 1
            progress = (stats.get("sent", 0) + stats.get("replied", 0)) / total
            st.progress(progress, text=f"{progress:.0%} complete")

            # Data table
            st.subheader("📄 Data Rows")
            if rows:
                df_rows = pd.DataFrame([{
                    "Row": r["row_index"],
                    "Channel": "📱" if r.get("channel") == "whatsapp" else "📧",
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

elif page == "⚠️ Review Queue":
    st.header("⚠️ Review Queue")
    st.markdown("Rows flagged for human review due to low confidence.")

    try:
        resp = requests.get(f"{API_BASE}/campaigns")
        campaigns = resp.json().get("campaigns", [])
    except requests.ConnectionError:
        st.error("Cannot connect to backend.")
        campaigns = []

    if campaigns:
        campaign_names = {c["id"]: c["name"] for c in campaigns}
        selected_id = st.selectbox("Select Campaign", options=list(campaign_names.keys()),
                                    format_func=lambda x: campaign_names[x], key="review_campaign")

        if selected_id:
            review_resp = requests.get(f"{API_BASE}/campaigns/{selected_id}/reviews")
            review_rows = review_resp.json() if review_resp.status_code == 200 else []

            if not review_rows:
                st.success("🎉 No rows need review!")
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
                            if st.button("✅ Approve", key=f"approve_{row['id']}"):
                                requests.post(f"{API_BASE}/campaigns/{selected_id}/rows/{row['id']}/review",
                                              json={"action": "approve"})
                                st.rerun()
                        with btn2:
                            if st.button("❌ Reject", key=f"reject_{row['id']}"):
                                requests.post(f"{API_BASE}/campaigns/{selected_id}/rows/{row['id']}/review",
                                              json={"action": "reject"})
                                st.rerun()


# ══════════════════════════════════════════════
# PAGE 4: Manual Reply
# ══════════════════════════════════════════════

elif page == "💬 Manual Reply":
    st.header("💬 Manual Reply Input")
    st.markdown("Paste a reply from a recipient to simulate an inbound webhook.")

    try:
        resp = requests.get(f"{API_BASE}/campaigns")
        campaigns = resp.json().get("campaigns", [])
    except requests.ConnectionError:
        st.error("Cannot connect to backend.")
        campaigns = []

    if campaigns:
        campaign_names = {c["id"]: c["name"] for c in campaigns}
        selected_id = st.selectbox("Select Campaign", options=list(campaign_names.keys()),
                                    format_func=lambda x: campaign_names[x], key="reply_campaign")

        if selected_id:
            detail_resp = requests.get(f"{API_BASE}/campaigns/{selected_id}")
            detail = detail_resp.json()
            sent_rows = [r for r in detail["rows"] if r["message_status"] == "sent"]

            if not sent_rows:
                st.info("No sent messages to reply to yet. Launch a campaign first.")
            else:
                row_options = {r["id"]: f"Row {r['row_index']} — {r.get('contact_phone') or r.get('contact_email', 'Unknown')}"
                               for r in sent_rows}
                selected_row_id = st.selectbox("Select Row", options=list(row_options.keys()),
                                                format_func=lambda x: row_options[x])

                selected_row = next(r for r in sent_rows if r["id"] == selected_row_id)
                st.markdown("**Message that was sent:**")
                st.text(selected_row.get("outbound_message", "—"))

                reply_text = st.text_area("Paste the reply:", height=100)

                if st.button("📨 Process Reply", use_container_width=True):
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
                                    st.warning("⚠️ Low confidence — row flagged for review.")
                                else:
                                    st.success("✅ Row updated automatically.")
                                st.json(result.get("suggested_update", {}))
                            else:
                                st.error(f"Error: {reply_resp.text}")
