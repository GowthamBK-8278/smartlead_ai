# =============================================================================
# SmartLead AI – Main Application
# Real Scraper + Auto-DM Platform
# =============================================================================

import sys
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import os
import time
import random
import threading
import logging
import pandas as pd
import streamlit as st


from data.keywords import get_domain_list, get_keywords_for_domain
from scraper.instagram import IGScraper
from scraper.facebook import FBScraper
from engine.interest_filter import is_interested, score_comment
from engine.dm_sender import send_ig_dm, send_fb_dm
from database.db_manager import (
    create_real_database,
    save_real_lead,
    get_all_real_leads,
    mark_dm_sent_real_lead,
    clear_all_real_leads
)
from excel.exporter import export_real_leads

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartLead AI - Operator Panel",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Init Real Database ────────────────────────────────────────────────────────
create_real_database()

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a1628 100%);
        color: #e8eaf6;
    }

    /* Header Styling */
    .header-container {
        padding: 2rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(99, 179, 237, 0.15);
        border-radius: 16px;
        backdrop-filter: blur(12px);
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    }
    
    .header-title {
        background: linear-gradient(90deg, #63b3ed, #90cdf4, #bee3f8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        margin: 0;
    }

    .header-subtitle {
        color: #a8b2d8;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }

    /* Status indicators */
    .status-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .status-card:hover {
        border-color: rgba(99,179,237,0.3);
        background: rgba(255,255,255,0.06);
    }
    .status-connected {
        color: #10b981;
        font-weight: 700;
        font-size: 1.1rem;
    }
    .status-disconnected {
        color: #ef4444;
        font-weight: 700;
        font-size: 1.1rem;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px 8px 0 0;
        color: #a8b2d8;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #bee3f8;
        background-color: rgba(255, 255, 255, 0.06);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(37, 99, 235, 0.2) !important;
        border-color: rgba(99, 179, 237, 0.4) !important;
        color: #bee3f8 !important;
    }

    /* Action Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.8rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.02em !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(59,130,246,0.4) !important;
    }

    /* Secondary Buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.8rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #34d399, #10b981) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(16,185,129,0.4) !important;
    }

    /* Live Log Console */
    .console-log {
        background-color: #050b14;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 12px;
        font-family: 'Courier New', Courier, monospace;
        color: #38bdf8;
        font-size: 0.85rem;
        height: 250px;
        overflow-y: scroll;
        white-space: pre-wrap;
        margin-bottom: 1rem;
    }

    /* Table styles */
    .stDataFrame {
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── Session State Init ────────────────────────────────────────────────────────
if "ig_username" not in st.session_state:
    st.session_state.ig_username = ""
if "ig_password" not in st.session_state:
    st.session_state.ig_password = ""
if "ig_proxy" not in st.session_state:
    st.session_state.ig_proxy = ""
if "ig_connected" not in st.session_state:
    st.session_state.ig_connected = False
if "fb_connected" not in st.session_state:
    st.session_state.fb_connected = False
if "ig_scraper" not in st.session_state:
    st.session_state.ig_scraper = IGScraper()
if "fb_scraper" not in st.session_state:
    st.session_state.fb_scraper = FBScraper()
if "scraped_results" not in st.session_state:
    st.session_state.scraped_results = pd.DataFrame()
if "scrape_logs" not in st.session_state:
    st.session_state.scrape_logs = []
if "dm_logs" not in st.session_state:
    st.session_state.dm_logs = []

# Update connections status initially
st.session_state.fb_connected = st.session_state.fb_scraper.check_session_exists()
if not st.session_state.ig_connected and os.path.exists(st.session_state.ig_scraper.session_path):
    st.session_state.ig_connected = True

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🚀 SmartLead AI</h1>
    <p class="header-subtitle">Real Social Media Comment Scraper &amp; Automated DM Outreach Platform</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs Configuration ────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🔐 Account Setup",
    "🔍 Scrape Comments",
    "📤 Send DMs",
    "📋 Lead History"
])

# =============================================================================
# TAB 1: ACCOUNT SETUP
# =============================================================================
with tab1:
    st.header("🔐 Social Media Accounts Configuration")
    st.markdown("Configure your dedicated scraper accounts and verify connections below.")
    
    col_ig, col_fb = st.columns(2)
    
    with col_ig:
        st.subheader("📸 Instagram Scraper Account")
        st.markdown("Use a **dedicated scraper business account** to connect via the Private API.")
        
        ig_user = st.text_input("Instagram Username", value=st.session_state.ig_username, placeholder="e.g. leadscraper_bot")
        ig_pass = st.text_input("Instagram Password", type="password", value=st.session_state.ig_password, placeholder="••••••••")
        
        with st.expander("🌐 Proxy Settings (required if IP is blocked)", expanded=False):
            st.caption("If Instagram says your IP is blacklisted, enter a proxy URL below. Format: `http://user:pass@host:port` or `socks5://host:port`")
            ig_proxy = st.text_input(
                "Proxy URL",
                value=st.session_state.ig_proxy,
                placeholder="http://user:pass@1.2.3.4:8080",
                label_visibility="collapsed"
            )
            proxy_col1, proxy_col2 = st.columns(2)
            with proxy_col1:
                if st.button("💾 Save Proxy", use_container_width=True):
                    st.session_state.ig_scraper.set_proxy(ig_proxy)
                    st.session_state.ig_proxy = st.session_state.ig_scraper.proxy
                    if st.session_state.ig_proxy:
                        st.success(f"Proxy saved: `{st.session_state.ig_proxy}`")
                    else:
                        st.info("Proxy cleared — using direct connection.")
            with proxy_col2:
                if st.button("🗑️ Clear Proxy", use_container_width=True):
                    st.session_state.ig_proxy = ""
                    st.session_state.ig_scraper.set_proxy("")
                    st.info("Proxy cleared.")
            if st.session_state.ig_proxy:
                st.success(f"✅ Active proxy: `{st.session_state.ig_proxy}`")
        
        # Connection status badge
        if st.session_state.ig_connected:
            st.markdown("<div class='status-card'>Status: <span class='status-connected'>🟢 Connected</span></div>", unsafe_allow_html=True)
            st.write("")
            if st.button("🔌 Disconnect Instagram", use_container_width=True):
                # Clear session state
                st.session_state.ig_connected = False
                st.session_state.ig_username = ""
                st.session_state.ig_password = ""
                st.session_state.ig_scraper.is_logged_in = False
                # Remove saved session file
                session_path = st.session_state.ig_scraper.session_path
                if os.path.exists(session_path):
                    try:
                        os.remove(session_path)
                    except Exception:
                        pass
                st.toast("Instagram disconnected. Session cleared.", icon="🔌")
                st.rerun()
        else:
            st.markdown("<div class='status-card'>Status: <span class='status-disconnected'>🔴 Disconnected</span></div>", unsafe_allow_html=True)
            
        st.write("")
        # Check if login is currently in progress
        scraper_ref = st.session_state.ig_scraper
        btn_disabled = scraper_ref.login_in_progress or scraper_ref.challenge_pending

        if st.button("🔐 Verify & Connect Instagram", use_container_width=True, disabled=btn_disabled):
            if not ig_user or not ig_pass:
                st.error("Please enter both Instagram username and password.")
            else:
                # Capture proxy from session state in the main thread to avoid thread-local AttributeError
                saved_proxy = st.session_state.ig_proxy

                # Start login in a background thread using direct object reference
                def run_login():
                    try:
                        # Mark login in progress before starting
                        scraper_ref.login_in_progress = True
                        scraper_ref.login_error = None
                        
                        # Apply saved proxy before login
                        if saved_proxy:
                            scraper_ref.set_proxy(saved_proxy)
                        scraper_ref.login(ig_user, ig_pass, force_relogin=True)
                    except Exception as e:
                        import traceback
                        err_msg = str(e) or repr(e)
                        logging.getLogger("smartlead_ig").error(f"Background login exception: {err_msg}")
                        scraper_ref.login_error = f"Background error: {err_msg}"
                        scraper_ref.login_in_progress = False
                        try:
                            with open("ig_error_traceback.log", "w") as f:
                                traceback.print_exc(file=f)
                        except Exception:
                            pass

                thread = threading.Thread(target=run_login)
                st.session_state.ig_login_thread = thread
                thread.start()
                
                # Fast polling loop to handle instant login or immediate challenge trigger
                with st.spinner("Connecting to Instagram private API..."):
                    for _ in range(60): # 30 seconds
                        time.sleep(0.5)
                        if not thread.is_alive():
                            break
                        if scraper_ref.challenge_pending:
                            break
                
                # Force a rerun to show the code entry box or success/failure messages
                st.rerun()

        # If a challenge is pending, show the verification code form
        if scraper_ref.challenge_pending:
            st.warning("⚠️ Instagram Login Verification Required")
            choice = scraper_ref.challenge_choice
            choice_str = "SMS" if "sms" in str(choice).lower() or choice == 0 else "Email"
            st.info(f"Instagram has sent a verification code to your registered **{choice_str}**.")
            
            code_input = st.text_input("Enter 6-digit Code", key="ig_verification_code_val", placeholder="123456")
            
            col_code_btn1, col_code_btn2 = st.columns(2)
            with col_code_btn1:
                if st.button("Verify Code", use_container_width=True):
                    if not code_input:
                        st.error("Please enter the verification code.")
                    else:
                        # Set the code to unblock the background thread
                        scraper_ref.challenge_code = code_input
                        
                        # Wait for thread to finish
                        with st.spinner("Submitting verification code..."):
                            thread = st.session_state.get("ig_login_thread")
                            if thread and thread.is_alive():
                                for _ in range(120): # up to 60 seconds
                                    time.sleep(0.5)
                                    if not thread.is_alive():
                                        break
                        
                        # Check login status
                        if scraper_ref.is_logged_in:
                            st.session_state.ig_username = ig_user
                            st.session_state.ig_password = ig_pass
                            st.session_state.ig_connected = True
                            st.toast("Successfully logged into Instagram! Session saved.", icon="📸")
                        else:
                            error_detail = f": {scraper_ref.login_error}" if scraper_ref.login_error else ""
                            st.error(f"Instagram verification failed{error_detail}. Please try login again.")
                            
                        # Clear challenge state
                        scraper_ref.challenge_pending = False
                        scraper_ref.challenge_code = None
                        st.rerun()
                        
            with col_code_btn2:
                if st.button("Cancel Verification", use_container_width=True):
                    # Cancel waiting
                    scraper_ref.challenge_pending = False
                    scraper_ref.challenge_code = "" # unblock with empty string to fail gracefully
                    st.rerun()

        # If not pending challenge, but thread is still running
        elif scraper_ref.login_in_progress:
            st.info("Instagram connection is in progress in the background... Click 'Refresh Status' if it does not complete.")
            if st.button("🔄 Refresh Status", use_container_width=True):
                st.rerun()
                
        # If login was run and completed without challenge
        elif not st.session_state.ig_connected and st.session_state.get("ig_login_thread") is not None and not scraper_ref.login_in_progress:
            if scraper_ref.is_logged_in:
                st.session_state.ig_username = ig_user
                st.session_state.ig_password = ig_pass
                st.session_state.ig_connected = True
                st.toast("Successfully logged into Instagram! Session saved.", icon="📸")
                st.rerun()
            else:
                err = scraper_ref.login_error or ""
            if "IP_BANNED" in err or "blacklist" in err.lower() or "change your ip" in err.lower():
                st.error("🚫 **Your IP address is blocked by Instagram**")
                st.markdown("""
**Instagram has blacklisted this server's IP** due to too many failed login attempts.
Your credentials are correct — this is a network-level block.

**Option A — Use a Proxy (Recommended):**
1. Get a residential proxy (services like [Webshare](https://www.webshare.io), [Oxylabs](https://oxylabs.io), or any SOCKS5/HTTP proxy)
2. Click **🌐 Proxy Settings** above and paste your proxy URL
3. Click **💾 Save Proxy** then **🔐 Verify & Connect Instagram** again

**Option B — Use a VPN or Different Network:**
1. Connect your machine to a **VPN** or **mobile hotspot**
2. Restart the Streamlit server, then try logging in again

**Option C — Wait:**
IP bans are sometimes temporary. Wait **2–4 hours** then retry without a proxy.
                """)
            elif "CHECKPOINT_REQUIRED" in err or "legacy challenge" in err.lower():
                st.warning("🔐 **Instagram Account Verification Required**")
                st.markdown("""
Instagram has detected a login from a **new device** and blocked it as a security measure.
This is not a password error — your credentials are fine.

**Follow these steps to unlock the account:**

1. 📱 Open the **Instagram app** on your phone **OR** go to [instagram.com](https://instagram.com) in your browser.
2. Log in with username **`we_are_here_07`** and password **`Navya2012`**.
3. Instagram will show a **security verification screen** — complete it.
4. After you are fully logged in on phone/browser, **come back here** and click **🔐 Verify & Connect Instagram** again.
                """)
            else:
                st.error(f"Instagram login failed: {err or 'Unknown error. Please check credentials and try again.'}")
                        
    with col_fb:
        st.subheader("👥 Facebook Scraper Session")
        st.markdown("Facebook uses **manual browser login (Option B)** to safely capture session cookies.")
        
        # Check current cookies status
        if st.session_state.fb_connected:
            st.markdown("<div class='status-card'>Status: <span class='status-connected'>🟢 Session Saved</span></div>", unsafe_allow_html=True)
            st.write("")
            if st.button("🔌 Disconnect Facebook", use_container_width=True):
                # Clear session state
                st.session_state.fb_connected = False
                st.session_state.fb_scraper.is_logged_in = False
                # Remove saved session file
                session_path = st.session_state.fb_scraper.session_path
                if os.path.exists(session_path):
                    try:
                        os.remove(session_path)
                    except Exception:
                        pass
                st.toast("Facebook disconnected. Session cleared.", icon="🔌")
                st.rerun()
        else:
            st.markdown("<div class='status-card'>Status: <span class='status-disconnected'>🔴 No Session Found</span></div>", unsafe_allow_html=True)
            
        st.write("")
        st.write("Clicking the button below will open a visible Chromium window. "
                 "Navigate to Facebook, log into your scraper account manually, and wait. "
                 "The window will close automatically and save your session as soon as you're logged in.")
        
        col_fb_btn1, col_fb_btn2 = st.columns(2)
        with col_fb_btn1:
            if st.button("🌐 Launch FB Login Window", use_container_width=True):
                with st.spinner("Opening browser window... Please log in."):
                    success = st.session_state.fb_scraper.login_manual()
                    if success:
                        st.session_state.fb_connected = True
                        st.success("Facebook session saved successfully!")
                    else:
                        st.session_state.fb_connected = False
                        st.error("Facebook login failed or timed out.")
        with col_fb_btn2:
            if st.button("🧪 Test FB Connection", use_container_width=True):
                with st.spinner("Verifying saved Facebook session..."):
                    valid = st.session_state.fb_scraper.test_connection()
                    if valid:
                        st.session_state.fb_connected = True
                        st.success("Session verified! Facebook connection is active.")
                    else:
                        st.session_state.fb_connected = False
                        st.error("Session invalid or expired. Please re-login.")

# =============================================================================
# TAB 2: SCRAPE COMMENTS
# =============================================================================
with tab2:
    st.header("🔍 Scrape Social Media Comments")
    st.markdown("Target official accounts or posts, extract comments, and identify prospects expressing interest.")
    
    col_params, col_targets = st.columns([1, 1])
    
    with col_params:
        st.subheader("🎯 Scraping Setup")
        domain_list = get_domain_list()
        selected_domain = st.selectbox("🌐 Select Industry Domain", domain_list)
        
        platform = st.radio("📡 Target Platform", ["Instagram", "Facebook"])
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            posts_count = st.slider("Posts to Scan per Account", min_value=1, max_value=30, value=10)
        with col_s2:
            max_comments = st.slider("Max Comments per Post", min_value=10, max_value=500, value=100, step=10)
            
    with col_targets:
        st.subheader("👥 Target Official Accounts")
        if platform == "Instagram":
            st.markdown("Enter Instagram **usernames** (one per line, without '@').")
            targets_placeholder = "e.g.\nindigo.airlines\naviation_academy_india"
        else:
            st.markdown("Enter Facebook Page **URLs** or Page usernames (one per line).")
            targets_placeholder = "e.g.\nhttps://www.facebook.com/IndiGoAirlines\nhttps://www.facebook.com/aviationacademy"
            
        targets_text = st.text_area("Target Accounts List", placeholder=targets_placeholder, height=140)
        
    st.divider()
    
    # Run scraping
    btn_col1, btn_col2 = st.columns([1, 4])
    with btn_col1:
        start_scrape = st.button("⚡ Start Scraping", use_container_width=True)
    with btn_col2:
        if st.button("🧹 Clear Scratch Logs"):
            st.session_state.scrape_logs = []
            st.rerun()

    # Log console & results display
    if start_scrape:
        st.session_state.scrape_logs = ["--- Scraping Process Started ---"]
        
        # Verification of account setup
        if platform == "Instagram" and not st.session_state.ig_connected:
            # Attempt to auto-login if password is saved in state
            if st.session_state.ig_username and st.session_state.ig_password:
                st.session_state.scrape_logs.append("Attempting automatic Instagram login...")
                success = st.session_state.ig_scraper.login(st.session_state.ig_username, st.session_state.ig_password)
                st.session_state.ig_connected = success
                
            if not st.session_state.ig_connected:
                st.error("Instagram is not connected. Please set up your account in Tab 1.")
                st.session_state.scrape_logs.append("ERROR: Instagram not logged in. Aborting.")
                start_scrape = False
                
        if platform == "Facebook" and not st.session_state.fb_connected:
            st.error("Facebook session is not available. Please set up your account in Tab 1.")
            st.session_state.scrape_logs.append("ERROR: Facebook session missing. Aborting.")
            start_scrape = False

        # Parse target accounts
        targets = [line.strip() for line in targets_text.split("\n") if line.strip()]
        if not targets:
            st.warning("Please specify at least one target account.")
            start_scrape = False

        if start_scrape:
            # Clear previous results
            st.session_state.scraped_results = pd.DataFrame()
            
            # Setup placeholder for live log and live table
            log_box = st.empty()
            table_box = st.empty()
            
            scraped_leads_data = []
            
            # Start loop
            for target in targets:
                st.session_state.scrape_logs.append(f"Target: {target} | Domain: {selected_domain} | Platform: {platform}")
                log_box.code("\n".join(st.session_state.scrape_logs))
                
                try:
                    if platform == "Instagram":
                        st.session_state.scrape_logs.append(f"Fetching recent posts for Instagram account @{target}...")
                        log_box.code("\n".join(st.session_state.scrape_logs))
                        posts = st.session_state.ig_scraper.get_user_posts(target, count=posts_count)
                        
                        st.session_state.scrape_logs.append(f"Found {len(posts)} posts. Extracting comments...")
                        log_box.code("\n".join(st.session_state.scrape_logs))
                        
                        for idx, post in enumerate(posts):
                            post_url = post["url"]
                            media_id = post["media_id"]
                            st.session_state.scrape_logs.append(f"({idx+1}/{len(posts)}) Scraping post {post_url}...")
                            log_box.code("\n".join(st.session_state.scrape_logs))
                            
                            comments = st.session_state.ig_scraper.get_post_comments(media_id, max_comments=max_comments)
                            
                            # Filter & score
                            matched_count = 0
                            for comment in comments:
                                c_text = comment["text"]
                                c_user = comment["username"]
                                c_profile = comment["profile_url"]
                                
                                if is_interested(c_text, selected_domain):
                                    score = score_comment(c_text, selected_domain)
                                    scraped_leads_data.append({
                                        "Username": c_user,
                                        "Platform": "Instagram",
                                        "Source Account": target,
                                        "Post URL": post_url,
                                        "Comment": c_text,
                                        "Score": score,
                                        "Profile URL": c_profile,
                                        "Date": comment.get("created_at", "—")
                                    })
                                    matched_count += 1
                                    
                            st.session_state.scrape_logs.append(f"  -> Extracted {len(comments)} comments, {matched_count} prospects identified.")
                            log_box.code("\n".join(st.session_state.scrape_logs))
                            
                            # Human-like delay
                            time.sleep(random.uniform(2.0, 5.0))
                            
                    elif platform == "Facebook":
                        st.session_state.scrape_logs.append(f"Fetching posts from Facebook Page: {target}...")
                        log_box.code("\n".join(st.session_state.scrape_logs))
                        post_urls = st.session_state.fb_scraper.get_page_posts(target, count=posts_count)
                        
                        st.session_state.scrape_logs.append(f"Found {len(post_urls)} posts. Scraping comment details...")
                        log_box.code("\n".join(st.session_state.scrape_logs))
                        
                        for idx, post_url in enumerate(post_urls):
                            st.session_state.scrape_logs.append(f"({idx+1}/{len(post_urls)}) Opening post {post_url}...")
                            log_box.code("\n".join(st.session_state.scrape_logs))
                            
                            comments = st.session_state.fb_scraper.get_post_comments(post_url, max_comments=max_comments)
                            
                            # Filter & score
                            matched_count = 0
                            for comment in comments:
                                c_text = comment["text"]
                                c_user = comment["username"]
                                c_profile = comment["profile_url"]
                                
                                if is_interested(c_text, selected_domain):
                                    score = score_comment(c_text, selected_domain)
                                    scraped_leads_data.append({
                                        "Username": c_user,
                                        "Platform": "Facebook",
                                        "Source Account": target,
                                        "Post URL": post_url,
                                        "Comment": c_text,
                                        "Score": score,
                                        "Profile URL": c_profile,
                                        "Date": "—" # Facebook comment dates can be complex to parse
                                    })
                                    matched_count += 1
                                    
                            st.session_state.scrape_logs.append(f"  -> Extracted {len(comments)} comments, {matched_count} prospects identified.")
                            log_box.code("\n".join(st.session_state.scrape_logs))
                            
                            # Human-like delay
                            time.sleep(random.uniform(3.0, 6.0))
                            
                except Exception as ex:
                    st.session_state.scrape_logs.append(f"ERROR: Exception occurred while scraping {target}: {ex}")
                    log_box.code("\n".join(st.session_state.scrape_logs))
            
            st.session_state.scrape_logs.append("--- Scraping Completed successfully! ---")
            log_box.code("\n".join(st.session_state.scrape_logs))
            
            # Save results to session state
            if scraped_leads_data:
                res_df = pd.DataFrame(scraped_leads_data)
                st.session_state.scraped_results = res_df
            else:
                st.session_state.scraped_results = pd.DataFrame()

    # Display results table & save controls if available
    if not st.session_state.scraped_results.empty:
        df_res = st.session_state.scraped_results
        
        st.subheader(f"📋 Extracted Prospects ({len(df_res)} found)")
        
        # Display styled table
        st.dataframe(
            df_res.style.map(
                lambda v: (
                    "background-color:#7f1d1d;color:#fca5a5" if v >= 80
                    else "background-color:#78350f;color:#fcd34d" if v >= 50
                    else "background-color:#1e3a5f;color:#93c5fd" if v >= 5
                    else ""
                ),
                subset=["Score"]
            ),
            use_container_width=True,
            height=350,
        )
        
        # Actions Row
        act_col1, act_col2, act_col3 = st.columns(3)
        with act_col1:
            if st.button("💾 Save All to Database", key="save_real_db_btn", use_container_width=True):
                saved_count = 0
                for _, row in df_res.iterrows():
                    success = save_real_lead(
                        domain=selected_domain,
                        platform=row["Platform"],
                        source_account=row["Source Account"],
                        post_url=row["Post URL"],
                        commenter_username=row["Username"],
                        commenter_profile_url=row["Profile URL"],
                        comment_text=row["Comment"],
                        interest_score=row["Score"]
                    )
                    if success:
                        saved_count += 1
                st.success(f"Successfully saved {saved_count} new leads to SQLite! (Duplicates skipped)")
                
        with act_col2:
            if st.button("📥 Create Excel Spreadsheet", key="export_real_excel_btn", use_container_width=True):
                filepath = export_real_leads(df_res, selected_domain)
                st.success(f"Excel report exported to reports directory!")
                st.code(filepath)
                
        with act_col3:
            # Streamlit direct download
            excel_csv = df_res.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇️ Download Scraped CSV",
                excel_csv,
                file_name=f"scraped_leads_{selected_domain}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        if start_scrape:
            st.info("No comments matching keywords were identified during this run.")

# =============================================================================
# TAB 3: SEND DMs
# =============================================================================
with tab3:
    st.header("📤 Automated Direct Message Outreach")
    st.markdown("Compose messages and direct message prospects directly from your scraper account.")
    
    # Load unsent leads
    pending_leads = get_all_real_leads(dm_sent=0)
    
    if not pending_leads:
        st.info("📭 No pending leads found in the database. Fetch and save some leads first!")
    else:
        pending_df = pd.DataFrame(pending_leads)
        
        # Clean up dataframe columns for displaying nicely
        display_pending = pending_df[["id", "platform", "domain", "commenter_username", "comment_text", "interest_score", "commenter_profile_url"]].copy()
        display_pending.columns = ["ID", "Platform", "Domain", "Username", "Comment", "Score", "Profile URL"]
        
        st.subheader("💬 Compose Message")
        dm_message = st.text_area("Outreach Message Text", 
                                  placeholder="Hi {username}! We saw you were interested in our aviation academy. Let us know if you need enrollment details...",
                                  height=100,
                                  help="The token {username} will be replaced automatically by the recipient's username.")
        
        st.subheader("👥 Select Target Leads")
        st.markdown("Select which prospects to send the outreach message to. Both Instagram and Facebook leads are supported.")
        
        # st.data_editor checkbox configuration
        display_pending["Select"] = True
        edited_leads = st.data_editor(
            display_pending,
            column_config={
                "Select": st.column_config.CheckboxColumn("Send", default=True, help="Toggle to select this lead"),
                "ID": st.column_config.NumberColumn("ID", disabled=True),
                "Username": st.column_config.TextColumn("Username", disabled=True),
                "Platform": st.column_config.TextColumn("Platform", disabled=True),
                "Domain": st.column_config.TextColumn("Domain", disabled=True),
                "Comment": st.column_config.TextColumn("Comment", disabled=True),
                "Score": st.column_config.NumberColumn("Score", disabled=True),
                "Profile URL": st.column_config.LinkColumn("Profile URL", disabled=True)
            },
            hide_index=True,
            use_container_width=True,
            height=300
        )
        
        selected_targets = edited_leads[edited_leads["Select"] == True]
        
        st.write("")
        dm_col1, dm_col2 = st.columns([1, 4])
        with dm_col1:
            send_dms = st.button("📤 Send Auto-DMs", use_container_width=True)
        with dm_col2:
            if st.button("🧹 Clear DM Logs"):
                st.session_state.dm_logs = []
                st.rerun()
                
        # Console output for DM logs
        dm_log_box = st.empty()
        if st.session_state.dm_logs:
            dm_log_box.code("\n".join(st.session_state.dm_logs))
            
        if send_dms:
            if not dm_message.strip():
                st.warning("Please type a message to send.")
            elif selected_targets.empty:
                st.warning("Please select at least one prospect to send DMs to.")
            else:
                st.session_state.dm_logs = ["--- Automated DM Outreach Started ---"]
                dm_log_box.code("\n".join(st.session_state.dm_logs))
                
                # Check logins
                has_ig = any(row["Platform"] == "Instagram" for _, row in selected_targets.iterrows())
                has_fb = any(row["Platform"] == "Facebook" for _, row in selected_targets.iterrows())
                
                ig_ok = True
                fb_ok = True
                
                if has_ig and not st.session_state.ig_connected:
                    st.session_state.dm_logs.append("WARNING: Instagram not connected! Direct messages to Instagram users will fail.")
                    ig_ok = False
                if has_fb and not st.session_state.fb_connected:
                    st.session_state.dm_logs.append("WARNING: Facebook session missing! Messenger messages will fail.")
                    fb_ok = False
                    
                dm_log_box.code("\n".join(st.session_state.dm_logs))
                
                sent_count = 0
                for idx, row in selected_targets.iterrows():
                    lead_id = int(row["ID"])
                    username = row["Username"]
                    platform = row["Platform"]
                    profile_url = row["Profile URL"]
                    
                    # Personalize message if token exists
                    personalized_msg = dm_message.replace("{username}", username)
                    
                    st.session_state.dm_logs.append(f"({sent_count+1}/{len(selected_targets)}) Sending message to {username} ({platform})...")
                    dm_log_box.code("\n".join(st.session_state.dm_logs))
                    
                    success = False
                    if platform == "Instagram" and ig_ok:
                        success = send_ig_dm(st.session_state.ig_scraper, username, personalized_msg, lead_id)
                    elif platform == "Facebook" and fb_ok:
                        success = send_fb_dm(st.session_state.fb_scraper, profile_url, personalized_msg, lead_id)
                    else:
                        st.session_state.dm_logs.append(f"  -> SKIPPED: Platform {platform} connection not verified.")
                        dm_log_box.code("\n".join(st.session_state.dm_logs))
                        continue
                        
                    if success:
                        st.session_state.dm_logs.append(f"  -> SUCCESS: Message sent to {username}.")
                        sent_count += 1
                    else:
                        st.session_state.dm_logs.append(f"  -> FAILED: Message delivery to {username} failed.")
                    
                    dm_log_box.code("\n".join(st.session_state.dm_logs))
                    
                    # Random delay between DMs to avoid spam filters (8 to 15 seconds)
                    if idx < len(selected_targets) - 1:
                        delay = random.uniform(8.0, 15.0)
                        st.session_state.dm_logs.append(f"Waiting {delay:.1f} seconds to throttle sending rate...")
                        dm_log_box.code("\n".join(st.session_state.dm_logs))
                        time.sleep(delay)
                        
                st.session_state.dm_logs.append(f"--- Outreach process completed. Successfully sent {sent_count} DMs. ---")
                dm_log_box.code("\n".join(st.session_state.dm_logs))
                st.success(f"Outreach cycle finished. {sent_count} messages sent successfully!")
                
                # Rerun to refresh the list of pending leads
                time.sleep(2)
                st.rerun()

# =============================================================================
# TAB 4: LEAD HISTORY
# =============================================================================
with tab4:
    st.header("📋 Stored Lead Intelligence")
    st.markdown("Search, filter, and review all scraped prospects stored in the database.")
    
    # Stored leads filters
    all_leads = get_all_real_leads()
    
    if not all_leads:
        st.info("📭 No leads in database. Go to **🔍 Scrape Comments** tab to scrape real prospects.")
    else:
        all_df = pd.DataFrame(all_leads)
        
        hist_col1, hist_col2, hist_col3 = st.columns(3)
        with hist_col1:
            filter_domain = st.selectbox("Filter Domain", ["All"] + sorted(all_df["domain"].dropna().unique().tolist()))
        with hist_col2:
            filter_plat = st.selectbox("Filter Platform", ["All"] + sorted(all_df["platform"].dropna().unique().tolist()))
        with hist_col3:
            filter_dm = st.selectbox("Filter DM Status", ["All", "DM Sent", "Pending DM"])
            
        # Perform filter query on DataFrame
        filtered_df = all_df.copy()
        if filter_domain != "All":
            filtered_df = filtered_df[filtered_df["domain"] == filter_domain]
        if filter_plat != "All":
            filtered_df = filtered_df[filtered_df["platform"] == filter_plat]
        if filter_dm != "All":
            val_dm = 1 if filter_dm == "DM Sent" else 0
            filtered_df = filtered_df[filtered_df["dm_sent"] == val_dm]
            
        st.markdown(f"**Found {len(filtered_df)} prospects in history**")
        
        if filtered_df.empty:
            st.warning("No leads match the selected filters.")
        else:
            # Map database columns to user-friendly ones
            display_hist = filtered_df[["id", "platform", "domain", "source_account", "commenter_username", "comment_text", "interest_score", "dm_sent", "dm_sent_at", "scraped_at", "commenter_profile_url"]].copy()
            display_hist.columns = ["ID", "Platform", "Domain", "Source Account", "Username", "Comment", "Score", "DM Sent", "DM Sent At", "Scraped At", "Profile URL"]
            
            # Format DM Sent as Yes/No
            display_hist["DM Sent"] = display_hist["DM Sent"].apply(lambda v: "✅ Yes" if v == 1 else "❌ No")
            
            # Render dataframe
            st.dataframe(
                display_hist.style.map(
                    lambda v: (
                        "background-color:#7f1d1d;color:#fca5a5" if v >= 80
                        else "background-color:#78350f;color:#fcd34d" if v >= 50
                        else "background-color:#1e3a5f;color:#93c5fd" if v >= 5
                        else ""
                    ),
                    subset=["Score"]
                ),
                use_container_width=True,
                height=450
            )
            
            # Export options
            st.divider()
            hist_act1, hist_act2 = st.columns(2)
            with hist_act1:
                if st.button("📥 Generate Excel Summary Report", key="hist_excel_btn", use_container_width=True):
                    # For exporting, rename df columns back to exporter expected
                    export_df = filtered_df.copy()
                    export_df.rename(columns={
                        "commenter_username": "Username",
                        "platform": "Platform",
                        "source_account": "Source Account",
                        "comment_text": "Comment",
                        "interest_score": "Score",
                        "commenter_profile_url": "Profile URL",
                        "dm_sent": "DM Sent",
                        "scraped_at": "Date"
                    }, inplace=True)
                    # map DM Sent to string
                    export_df["DM Sent"] = export_df["DM Sent"].apply(lambda v: "Yes" if v == 1 else "No")
                    
                    rep_domain = filter_domain if filter_domain != "All" else "Combined"
                    filepath = export_real_leads(export_df, rep_domain)
                    st.success(f"Historical Excel report generated and saved!")
                    st.code(filepath)
            with hist_act2:
                csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Filtered History CSV",
                    csv_bytes,
                    file_name="smartlead_historical_leads.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
            # Danger Zone in history tab
            st.write("")
            with st.expander("⚠️ Database Management (Danger Zone)"):
                st.write("Deleting leads is permanent and cannot be undone.")
                if st.button("🗑️ Clear Real Leads Database", use_container_width=True):
                    clear_all_real_leads()
                    st.success("Successfully cleared all real leads from database.")
                    time.sleep(1)
                    st.rerun()