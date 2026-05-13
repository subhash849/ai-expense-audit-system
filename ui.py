import streamlit as st
import requests
from datetime import date
from storage import load_claims, update_claim, save_claims

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ExpenseIQ",
    page_icon="🧾",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  GLOBAL STYLES  — light, clean, mobile-first
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    background: #f7f8fa !important;
    color: #1a1d23;
}
.stApp { background: #f7f8fa; }
section[data-testid="stSidebar"] { display: none !important; }

.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0 1.5rem;
    border-bottom: 1px solid #e8eaef;
    margin-bottom: 1.5rem;
}
.nav-logo { font-size: 1.1rem; font-weight: 600; color: #1a1d23; letter-spacing: -0.3px; }
.nav-logo span { color: #4f6ef7; }

div[data-testid="stRadio"] { margin-bottom: 1.5rem; }
div[data-testid="stRadio"] > label { display: none; }
div[data-testid="stRadio"] > div {
    display: flex !important;
    gap: 0.5rem;
    background: #eef0f5;
    padding: 4px;
    border-radius: 10px;
    width: 100%;
}
div[data-testid="stRadio"] label {
    flex: 1 !important;
    text-align: center;
    padding: 0.45rem 0.75rem !important;
    border-radius: 7px;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #6b7280 !important;
    cursor: pointer;
    transition: all 0.15s;
    margin: 0 !important;
}
div[data-testid="stRadio"] label:has(input:checked) {
    background: #fff !important;
    color: #1a1d23 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

.sec-title {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 0.75rem;
    margin-top: 1.5rem;
}

.stat-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.6rem;
    margin-bottom: 1.25rem;
}
.stat-tile {
    background: #fff;
    border: 1px solid #e8eaef;
    border-radius: 10px;
    padding: 0.85rem 1rem;
}
.stat-val { font-size: 1.6rem; font-weight: 600; line-height: 1; margin-bottom: 0.2rem; }
.stat-lbl { font-size: 0.72rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.07em; }

.badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-family: 'IBM Plex Mono', monospace;
}
.badge-approved { background: #edf7f2; color: #1a7a48; border: 1px solid #b6e8cf; }
.badge-flagged  { background: #fef9ec; color: #92620a; border: 1px solid #fcd97a; }
.badge-rejected { background: #fef0f0; color: #b91c1c; border: 1px solid #fca5a5; }
.badge-pending  { background: #f0f1fd; color: #4338ca; border: 1px solid #c7d2fe; }

.claim-card {
    background: #fff;
    border: 1px solid #e8eaef;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.65rem;
}
.claim-card.flagged  { border-left: 3px solid #f59e0b; border-radius: 0 12px 12px 0; }
.claim-card.rejected { border-left: 3px solid #ef4444; border-radius: 0 12px 12px 0; }
.claim-card.approved { border-left: 3px solid #22c55e; border-radius: 0 12px 12px 0; }
.claim-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.4rem; }
.claim-id { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: #9ca3af; }
.claim-merchant { font-weight: 600; font-size: 0.95rem; color: #1a1d23; margin-bottom: 0.15rem; }
.claim-meta { font-size: 0.78rem; color: #6b7280; }
.claim-amount { font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem; color: #1a1d23; margin-top: 0.45rem; }
.claim-reason {
    font-size: 0.79rem;
    color: #6b7280;
    background: #f7f8fa;
    border-radius: 6px;
    padding: 0.5rem 0.7rem;
    border-left: 2px solid #e8eaef;
    margin-top: 0.6rem;
    line-height: 1.5;
}

.status-banner {
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin: 1rem 0;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
}
.status-banner.approved { background: #edf7f2; border: 1px solid #b6e8cf; }
.status-banner.flagged  { background: #fef9ec; border: 1px solid #fcd97a; }
.status-banner.rejected { background: #fef0f0; border: 1px solid #fca5a5; }
.banner-icon { font-size: 1.1rem; margin-top: 0.05rem; }
.banner-title { font-weight: 600; font-size: 0.9rem; margin-bottom: 0.1rem; }
.banner-title.approved { color: #1a7a48; }
.banner-title.flagged  { color: #92620a; }
.banner-title.rejected { color: #b91c1c; }
.banner-reason { font-size: 0.8rem; color: #6b7280; line-height: 1.4; }

.data-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.6rem;
    margin: 0.75rem 0;
}
.data-item { background: #f7f8fa; border-radius: 8px; padding: 0.6rem 0.75rem; }
.data-key { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; color: #9ca3af; margin-bottom: 0.2rem; }
.data-val { font-size: 0.88rem; font-weight: 500; color: #1a1d23; word-break: break-word; }

.policy-block {
    background: #f3f4fd;
    border: 1px solid #dde0fb;
    border-radius: 8px;
    padding: 0.7rem 0.9rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem;
    color: #4338ca;
    line-height: 1.6;
    margin-top: 0.5rem;
    white-space: pre-wrap;
    word-break: break-word;
}

.notif-item {
    display: flex;
    align-items: flex-start;
    gap: 0.65rem;
    padding: 0.7rem 0.9rem;
    border-radius: 9px;
    margin-bottom: 0.5rem;
    font-size: 0.82rem;
    line-height: 1.4;
}
.notif-approved { background: #edf7f2; border: 1px solid #b6e8cf; color: #1a7a48; }
.notif-rejected { background: #fef0f0; border: 1px solid #fca5a5; color: #b91c1c; }
.notif-flagged  { background: #fef9ec; border: 1px solid #fcd97a; color: #92620a; }
.notif-id { font-family: 'IBM Plex Mono', monospace; font-weight: 600; }

.override-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.72rem;
    color: #92620a;
    background: #fef9ec;
    border: 1px solid #fcd97a;
    border-radius: 6px;
    padding: 2px 8px;
    margin-top: 0.5rem;
}

.stTextInput input, .stTextArea textarea {
    background: #fff !important;
    border: 1px solid #dde0e8 !important;
    border-radius: 8px !important;
    color: #1a1d23 !important;
    font-size: 0.88rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #4f6ef7 !important;
    box-shadow: 0 0 0 3px rgba(79,110,247,0.1) !important;
}

[data-testid="stFileUploader"] {
    border: 1.5px dashed #d1d5db !important;
    border-radius: 10px !important;
    background: #fff !important;
}
[data-testid="stFileUploader"]:hover { border-color: #4f6ef7 !important; }

.stButton > button {
    background: #4f6ef7 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    width: 100%;
    transition: background 0.15s !important;
}
.stButton > button:hover { background: #3b5ce4 !important; }
.stButton > button:disabled { background: #c7d2fe !important; color: #fff !important; }

.stSelectbox [data-baseweb="select"] > div {
    background: #fff !important;
    border: 1px solid #dde0e8 !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
}

details {
    background: #fff;
    border: 1px solid #e8eaef !important;
    border-radius: 10px !important;
    margin-bottom: 0.65rem;
}
summary { font-size: 0.88rem !important; font-weight: 500 !important; }

hr { border-color: #e8eaef !important; margin: 1.25rem 0 !important; }

@media (max-width: 640px) {
    .stat-val { font-size: 1.35rem; }
    .data-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def badge_html(status: str) -> str:
    s = (status or "").lower()
    if s == "approved":
        return '<span class="badge badge-approved">✓ Approved</span>'
    elif s == "rejected":
        return '<span class="badge badge-rejected">✕ Rejected</span>'
    elif s == "flagged":
        return '<span class="badge badge-flagged">⚑ Flagged</span>'
    return '<span class="badge badge-pending">· Pending</span>'

def border_cls(status: str) -> str:
    return {"approved": "approved", "rejected": "rejected", "flagged": "flagged"}.get(
        (status or "").lower(), ""
    )


# ─────────────────────────────────────────────
#  TOP NAV + MODE SWITCH
# ─────────────────────────────────────────────
st.markdown("""
<div class="top-nav">
    <div class="nav-logo">Expense<span>IQ</span></div>
    <div style="font-size:.74rem;color:#9ca3af;">Policy-First Auditing</div>
</div>
""", unsafe_allow_html=True)

mode = st.radio(
    "Mode",
    ["👤 Employee", "🔍 Auditor"],
    horizontal=True,
    label_visibility="collapsed",
)

claims = load_claims()


# ─────────────────────────────────────────────
#  EMPLOYEE PORTAL
# ─────────────────────────────────────────────
if "Employee" in mode:

    # Notifications
    unnotified = [c for c in reversed(claims) if not c.get("Notified")]
    if unnotified:
        st.markdown('<div class="sec-title">Notifications</div>', unsafe_allow_html=True)
        for c in unnotified:
            s    = c.get("Final_Status", "")
            css  = {"Approved": "notif-approved", "Rejected": "notif-rejected"}.get(s, "notif-flagged")
            icon = {"Approved": "✅", "Rejected": "❌"}.get(s, "⚑")
            msg  = {"Approved": "approved.", "Rejected": "rejected."}.get(s, "flagged for review.")
            st.markdown(f"""
            <div class="notif-item {css}">
                <span>{icon}</span>
                <span>Claim <span class="notif-id">#{c['id']}</span> has been {msg}</span>
            </div>
            """, unsafe_allow_html=True)
            c["Notified"] = True
        save_claims(claims)

    # Submit form
    st.markdown('<div class="sec-title">Submit New Claim</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Receipt",
        type=["jpg", "jpeg", "png", "pdf"],
        label_visibility="collapsed",
    )
    st.markdown(
        '<div style="font-size:.74rem;color:#9ca3af;margin-top:.25rem;margin-bottom:.75rem;">JPG · PNG · PDF accepted</div>',
        unsafe_allow_html=True,
    )

    purpose      = st.text_input("Business Purpose", placeholder="e.g. Client dinner with Acme Corp")
    claimed_date = st.date_input("Expense Date", value=date.today())

    analyze_btn = st.button(
        "Analyze Receipt",
        disabled=not (uploaded_file and purpose),
        use_container_width=True,
    )

    if analyze_btn and uploaded_file and purpose:
        with st.spinner("Scanning receipt and checking policy…"):
            try:
                response = requests.post(
                    "http://127.0.0.1:5000/process",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue())},
                    data={"purpose": purpose, "claimed_date": str(claimed_date)},
                    timeout=60,
                )
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach the audit server. Make sure app.py is running on port 5000.")
                st.stop()

        if response.status_code == 200:
            r = response.json()
            s = r.get("Status", "")

            cfg = {
                "Approved": ("approved", "✅", "Claim Approved"),
                "Flagged":  ("flagged",  "⚑",  "Flagged for Review"),
                "Rejected": ("rejected", "✕",  "Claim Rejected"),
            }
            cls, icon, title = cfg.get(s, ("pending", "·", "Status Unknown"))

            st.markdown(f"""
            <div class="status-banner {cls}">
                <span class="banner-icon">{icon}</span>
                <div>
                    <div class="banner-title {cls}">{title}</div>
                    <div class="banner-reason">{r.get('Reason', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="sec-title">Extracted Data</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="data-grid">
                <div class="data-item"><div class="data-key">Merchant</div><div class="data-val">{r.get('Merchant','—')}</div></div>
                <div class="data-item"><div class="data-key">Amount</div><div class="data-val">{r.get('Currency','')} {r.get('Amount','—')}</div></div>
                <div class="data-item"><div class="data-key">Date</div><div class="data-val">{r.get('Date','—')}</div></div>
                <div class="data-item"><div class="data-key">Currency</div><div class="data-val">{r.get('Currency','—')}</div></div>
            </div>
            """, unsafe_allow_html=True)

            if r.get("Policy"):
                st.markdown('<div class="sec-title">Policy Applied</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="policy-block">{r["Policy"]}</div>', unsafe_allow_html=True)
        else:
            st.error(f"Server error {response.status_code}: {response.text}")

    # Recent claims
    st.markdown('<div class="sec-title">Recent Claims</div>', unsafe_allow_html=True)
    recent = list(reversed(claims[-5:])) if claims else []

    if recent:
        for c in recent:
            s   = c.get("Final_Status", "")
            cls = border_cls(s)
            st.markdown(f"""
            <div class="claim-card {cls}">
                <div class="claim-header">
                    <span class="claim-id">#{c.get('id','?')}</span>
                    {badge_html(s)}
                </div>
                <div class="claim-merchant">{c.get('Merchant', 'Unknown')}</div>
                <div class="claim-meta">{c.get('Purpose', '')}</div>
                <div class="claim-amount">{c.get('Currency','')} {c.get('Amount','—')}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="font-size:.85rem;color:#9ca3af;padding:.5rem 0;">No previous claims.</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
#  AUDITOR DASHBOARD
# ─────────────────────────────────────────────
if "Auditor" in mode:

    if not claims:
        st.markdown("""
        <div style="text-align:center;padding:4rem 1rem;color:#9ca3af;">
            <div style="font-size:2rem;margin-bottom:.6rem;">📭</div>
            <div style="font-size:.95rem;font-weight:500;color:#6b7280;">No claims yet</div>
            <div style="font-size:.82rem;margin-top:.3rem;">Submitted receipts appear here.</div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # Stats
    flagged_n  = sum(1 for c in claims if c.get("Final_Status") == "Flagged")
    rejected_n = sum(1 for c in claims if c.get("Final_Status") == "Rejected")
    approved_n = sum(1 for c in claims if c.get("Final_Status") == "Approved")

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-tile">
            <div class="stat-val" style="color:#1a1d23;">{len(claims)}</div>
            <div class="stat-lbl">Total</div>
        </div>
        <div class="stat-tile">
            <div class="stat-val" style="color:#f59e0b;">{flagged_n}</div>
            <div class="stat-lbl">Flagged</div>
        </div>
        <div class="stat-tile">
            <div class="stat-val" style="color:#ef4444;">{rejected_n}</div>
            <div class="stat-lbl">Rejected</div>
        </div>
        <div class="stat-tile">
            <div class="stat-val" style="color:#22c55e;">{approved_n}</div>
            <div class="stat-lbl">Approved</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filter
    filter_status = st.selectbox(
        "Filter by status",
        ["All", "Flagged", "Rejected", "Approved"],
        label_visibility="collapsed",
    )

    def risk_order(c):
        return {"Flagged": 0, "Rejected": 1, "Approved": 2}.get(c.get("Final_Status", ""), 3)

    filtered = sorted(claims, key=risk_order)
    if filter_status != "All":
        filtered = [c for c in filtered if c.get("Final_Status") == filter_status]

    if not filtered:
        st.markdown(
            '<div style="font-size:.85rem;color:#9ca3af;padding:.5rem 0;">No claims match this filter.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="sec-title">Claims Queue</div>', unsafe_allow_html=True)

    for claim in filtered:
        s   = claim.get("Final_Status", "")
        cid = claim.get("id", "?")

        with st.expander(
            f"#{cid} · {claim.get('Merchant','Unknown')} · {claim.get('Currency','')} {claim.get('Amount','—')}",
            expanded=(s in ("Flagged", "Rejected")),
        ):
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.5rem;flex-wrap:wrap;gap:.5rem;">
                <div>
                    {badge_html(s)}
                    <div class="claim-merchant" style="margin-top:.35rem;">{claim.get('Merchant','Unknown')}</div>
                    <div class="claim-meta">📅 {claim.get('Date','—')} · {claim.get('Purpose','—')}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;color:#9ca3af;">Amount</div>
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:1.05rem;font-weight:600;color:#1a1d23;">
                        {claim.get('Currency','')} {claim.get('Amount','—')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if claim.get("Reason"):
                st.markdown(f'<div class="claim-reason">{claim["Reason"]}</div>', unsafe_allow_html=True)

            if claim.get("Policy"):
                st.markdown('<div class="sec-title" style="margin-top:1rem;">Policy Applied</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="policy-block">{claim["Policy"]}</div>', unsafe_allow_html=True)

            if claim.get("Overridden"):
                comment_txt = f' · {claim.get("Auditor_Comment","")}' if claim.get("Auditor_Comment") else ""
                st.markdown(
                    f'<div class="override-tag">⚑ Overridden{comment_txt}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            st.markdown('<div class="sec-title">Override Decision</div>', unsafe_allow_html=True)

            override_status = st.selectbox(
                "New status",
                ["Keep AI Decision", "Approved", "Rejected"],
                key=f"status_{cid}",
                label_visibility="collapsed",
            )
            comment = st.text_input(
                "Comment",
                placeholder="Reason for override (optional)",
                key=f"comment_{cid}",
                label_visibility="collapsed",
            )

            if st.button("Submit Override", key=f"btn_{cid}", use_container_width=True):
                if override_status != "Keep AI Decision":
                    update_claim(cid, {
                        "Final_Status":    override_status,
                        "Auditor_Comment": comment,
                        "Overridden":      True,
                        "Notification":    f"Claim updated to {override_status}",
                        "Notified":        False,
                    })
                    st.success(f"Claim #{cid} updated to {override_status}.")
                    st.rerun()
                else:
                    st.info("No changes made.")

    save_claims(claims)