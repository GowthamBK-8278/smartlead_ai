import os
import time
import random
import threading
import logging
import traceback
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

from data.keywords import get_domain_list
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

# Initialize Flask
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "smartlead_ai_secret_key"  # Required for session, though we use global for scrapers

# Initialize Database
create_real_database()

# Global State for Scrapers (Since this is a local tool for a single operator)
ig_scraper = IGScraper()
fb_scraper = FBScraper()

global_state = {
    "ig_username": "",
    "ig_password": "",
    "ig_proxy": "",
    "ig_connected": False,
    "fb_connected": False,
    "scrape_logs": [],
    "scrape_running": False,
    "scraped_results": [],
    "dm_logs": [],
    "dm_running": False
}

# Initial Connection Check
global_state["fb_connected"] = fb_scraper.check_session_exists()
if not global_state["ig_connected"] and os.path.exists(ig_scraper.session_path):
    global_state["ig_connected"] = True

# --- Helper to append logs ---
def log_scrape(msg):
    global_state["scrape_logs"].append(msg)
    logging.getLogger("smartlead_scrape").info(msg)

def log_dm(msg):
    global_state["dm_logs"].append(msg)
    logging.getLogger("smartlead_dm").info(msg)

# ==========================================
# Routes: Web Pages
# ==========================================

@app.route("/")
def index():
    domains = get_domain_list()
    return render_template("index.html", domains=domains)

# ==========================================
# Routes: APIs - Account Setup
# ==========================================

@app.route("/api/status", methods=["GET"])
def get_status():
    username = ig_scraper.logged_in_username or global_state["ig_username"]
    return jsonify({
        "ig_connected": ig_scraper.is_logged_in,
        "fb_connected": global_state["fb_connected"],
        "ig_username": username,
        "ig_proxy": global_state["ig_proxy"],
        "ig_challenge_pending": False,
        "ig_login_in_progress": ig_scraper.login_in_progress,
        "ig_login_error": ig_scraper.login_error
    })

@app.route("/api/ig/login", methods=["POST"])
def ig_login():
    """Legacy endpoint – kept for backward compat but now triggers manual browser login."""
    data = request.json
    proxy = data.get("proxy", "").strip()
    global_state["ig_proxy"] = proxy
    if proxy:
        ig_scraper.set_proxy(proxy)

    if ig_scraper.login_in_progress:
        return jsonify({"success": False, "error": "Login already in progress"})

    def run():
        ig_scraper.login_in_progress = True
        ig_scraper.login_error = None
        ig_scraper.login_manual()

    threading.Thread(target=run).start()
    return jsonify({"success": True, "message": "Browser login launched"})

@app.route("/api/ig/login_sessionid", methods=["POST"])
def ig_login_sessionid():
    data = request.json
    session_id = data.get("session_id", "").strip()
    if not session_id:
        return jsonify({"success": False, "error": "Session ID required"})

    if ig_scraper.login_in_progress:
        return jsonify({"success": False, "error": "Login already in progress"})

    def run():
        ig_scraper.login_in_progress = True
        ig_scraper.login_error = None
        ig_scraper.login_with_session_id(session_id)

    threading.Thread(target=run).start()
    return jsonify({"success": True, "message": "Session ID login initiated"})

@app.route("/api/ig/launch_login", methods=["POST"])
def ig_launch_login():
    if ig_scraper.login_in_progress:
        return jsonify({"success": False, "error": "Login already in progress"})
        
    global_state["ig_username"] = "ManualBrowserLogin"
    global_state["ig_password"] = "******"
    
    try:
        ig_scraper.login_in_progress = True
        ig_scraper.login_error = None
        success = ig_scraper.login_manual()
        global_state["ig_connected"] = ig_scraper.is_logged_in
        if success:
            return jsonify({"success": True, "message": "Instagram session saved!"})
        else:
            return jsonify({"success": False, "error": ig_scraper.login_error or "Login failed or timed out."})
    except Exception as e:
        ig_scraper.login_error = str(e)
        ig_scraper.login_in_progress = False
        global_state["ig_connected"] = False
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/ig/verify", methods=["POST"])
def ig_verify():
    data = request.json
    code = data.get("code", "").strip()
    if not code:
        return jsonify({"success": False, "error": "Code required"})
        
    ig_scraper.challenge_code = code
    return jsonify({"success": True, "message": "Verification code submitted"})

@app.route("/api/ig/disconnect", methods=["POST"])
def ig_disconnect():
    ig_scraper.disconnect()
    global_state["ig_username"] = ""
    global_state["ig_proxy"] = ""
    return jsonify({"success": True, "message": "Disconnected"})

@app.route("/api/fb/launch", methods=["POST"])
def fb_launch():
    # Facebook manual login blocks, but we can do it asynchronously if we want to not block the API
    # Since playwright needs to run, we might need a thread. Wait, playwright sync_api on a different thread might complain.
    # Let's run it synchronously, the frontend will wait.
    try:
        success = fb_scraper.login_manual()
        if success:
            global_state["fb_connected"] = True
            return jsonify({"success": True, "message": "Facebook session saved!"})
        else:
            return jsonify({"success": False, "error": "Login failed or timed out."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/fb/test", methods=["POST"])
def fb_test():
    try:
        valid = fb_scraper.test_connection()
        if valid:
            global_state["fb_connected"] = True
            return jsonify({"success": True, "message": "Session verified!"})
        else:
            global_state["fb_connected"] = False
            return jsonify({"success": False, "error": "Session invalid."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/fb/disconnect", methods=["POST"])
def fb_disconnect():
    global_state["fb_connected"] = False
    fb_scraper.is_logged_in = False
    if os.path.exists(fb_scraper.session_path):
        try:
            os.remove(fb_scraper.session_path)
        except Exception:
            pass
    return jsonify({"success": True, "message": "Disconnected"})

# ==========================================
# Routes: APIs - Scraping
# ==========================================

@app.route("/api/scrape/start", methods=["POST"])
def scrape_start():
    if global_state["scrape_running"]:
        return jsonify({"success": False, "error": "Scraping already in progress"})
        
    data = request.json
    domain = data.get("domain")
    platform = data.get("platform")
    posts_count = data.get("posts_count", 10)
    max_comments = data.get("max_comments", 100)
    targets_text = data.get("targets", "")
    
    targets = [line.strip() for line in targets_text.split("\n") if line.strip()]
    if not targets:
        return jsonify({"success": False, "error": "No targets provided"})
        
    if platform == "Instagram" and not ig_scraper.is_logged_in:
        return jsonify({"success": False, "error": "Instagram not connected"})
    if platform == "Facebook" and not global_state["fb_connected"]:
        return jsonify({"success": False, "error": "Facebook not connected"})
        
    global_state["scrape_logs"] = ["--- Scraping Process Started ---"]
    global_state["scraped_results"] = []
    global_state["scrape_running"] = True
    
    def run_scrape():
        scraped_data = []
        try:
            for target in targets:
                log_scrape(f"Target: {target} | Domain: {domain} | Platform: {platform}")
                try:
                    if platform == "Instagram":
                        log_scrape(f"Fetching posts for Instagram account @{target}...")
                        posts = ig_scraper.get_user_posts(target, count=posts_count)
                        log_scrape(f"Found {len(posts)} posts.")
                        for idx, post in enumerate(posts):
                            log_scrape(f"({idx+1}/{len(posts)}) Scraping post {post['url']}...")
                            comments = ig_scraper.get_post_comments(post["media_id"], max_comments=max_comments)
                            matched = 0
                            for c in comments:
                                if is_interested(c["text"], domain):
                                    score = score_comment(c["text"], domain)
                                    scraped_data.append({
                                        "Username": c["username"],
                                        "Platform": "Instagram",
                                        "Source Account": target,
                                        "Post URL": post["url"],
                                        "Comment": c["text"],
                                        "Score": score,
                                        "Profile URL": c["profile_url"],
                                        "Date": c.get("created_at", "—")
                                    })
                                    matched += 1
                            log_scrape(f"  -> Extracted {len(comments)} comments, {matched} prospects identified.")
                            time.sleep(random.uniform(2.0, 5.0))
                            
                    elif platform == "Facebook":
                        log_scrape(f"Fetching posts from Facebook Page: {target}...")
                        post_urls = fb_scraper.get_page_posts(target, count=posts_count)
                        log_scrape(f"Found {len(post_urls)} posts.")
                        for idx, post_url in enumerate(post_urls):
                            log_scrape(f"({idx+1}/{len(post_urls)}) Opening post {post_url}...")
                            comments = fb_scraper.get_post_comments(post_url, max_comments=max_comments)
                            matched = 0
                            for c in comments:
                                if is_interested(c["text"], domain):
                                    score = score_comment(c["text"], domain)
                                    scraped_data.append({
                                        "Username": c["username"],
                                        "Platform": "Facebook",
                                        "Source Account": target,
                                        "Post URL": post_url,
                                        "Comment": c["text"],
                                        "Score": score,
                                        "Profile URL": c["profile_url"],
                                        "Date": "—"
                                    })
                                    matched += 1
                            log_scrape(f"  -> Extracted {len(comments)} comments, {matched} prospects identified.")
                            time.sleep(random.uniform(3.0, 6.0))
                except Exception as ex:
                    log_scrape(f"ERROR: Exception while scraping {target}: {ex}")
            log_scrape("--- Scraping Completed successfully! ---")
        except Exception as e:
            log_scrape(f"FATAL ERROR: {e}")
        finally:
            global_state["scraped_results"] = scraped_data
            global_state["scrape_running"] = False

    thread = threading.Thread(target=run_scrape)
    thread.start()
    return jsonify({"success": True, "message": "Scraping started"})

@app.route("/api/scrape/logs", methods=["GET"])
def scrape_logs():
    return jsonify({
        "logs": global_state["scrape_logs"],
        "running": global_state["scrape_running"],
        "results": global_state["scraped_results"]
    })

@app.route("/api/scrape/save", methods=["POST"])
def scrape_save():
    domain = request.json.get("domain")
    results = global_state["scraped_results"]
    saved_count = 0
    for row in results:
        success = save_real_lead(
            domain=domain,
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
    return jsonify({"success": True, "saved_count": saved_count})

@app.route("/api/scrape/export", methods=["POST"])
def scrape_export():
    domain = request.json.get("domain", "All")
    results = global_state["scraped_results"]
    if not results:
        return jsonify({"success": False, "error": "No data to export"})
    df = pd.DataFrame(results)
    filepath = export_real_leads(df, domain)
    return jsonify({"success": True, "filepath": filepath})

# ==========================================
# Routes: APIs - DMs
# ==========================================

@app.route("/api/dms/pending", methods=["GET"])
def dms_pending():
    pending = get_all_real_leads(dm_sent=0)
    return jsonify({"leads": pending})

@app.route("/api/dms/send", methods=["POST"])
def dms_send():
    if global_state["dm_running"]:
        return jsonify({"success": False, "error": "DM process already running"})
        
    data = request.json
    message_template = data.get("message", "")
    target_ids = data.get("target_ids", [])
    
    if not message_template or not target_ids:
        return jsonify({"success": False, "error": "Message and targets required"})
        
    pending = get_all_real_leads(dm_sent=0)
    targets = [lead for lead in pending if lead["id"] in target_ids]
    
    global_state["dm_logs"] = ["--- Automated DM Outreach Started ---"]
    global_state["dm_running"] = True
    
    def run_dms():
        try:
            has_ig = any(t["platform"] == "Instagram" for t in targets)
            has_fb = any(t["platform"] == "Facebook" for t in targets)
            
            ig_ok = global_state["ig_connected"]
            fb_ok = global_state["fb_connected"]
            
            if has_ig and not ig_ok:
                log_dm("WARNING: Instagram not connected! Direct messages to Instagram users will fail.")
            if has_fb and not fb_ok:
                log_dm("WARNING: Facebook session missing! Messenger messages will fail.")
                
            sent_count = 0
            for idx, target in enumerate(targets):
                username = target["commenter_username"]
                platform = target["platform"]
                profile_url = target["commenter_profile_url"]
                lead_id = target["id"]
                
                personalized_msg = message_template.replace("{username}", username)
                log_dm(f"({sent_count+1}/{len(targets)}) Sending message to {username} ({platform})...")
                
                success = False
                if platform == "Instagram" and ig_ok:
                    success = send_ig_dm(ig_scraper, username, personalized_msg, lead_id)
                elif platform == "Facebook" and fb_ok:
                    success = send_fb_dm(fb_scraper, profile_url, personalized_msg, lead_id)
                else:
                    log_dm(f"  -> SKIPPED: Platform {platform} connection not verified.")
                    continue
                    
                if success:
                    log_dm(f"  -> SUCCESS: Message sent to {username}.")
                    sent_count += 1
                else:
                    log_dm(f"  -> FAILED: Message delivery to {username} failed.")
                    
                if idx < len(targets) - 1:
                    delay = random.uniform(8.0, 15.0)
                    log_dm(f"Waiting {delay:.1f} seconds to throttle sending rate...")
                    time.sleep(delay)
                    
            log_dm(f"--- Outreach process completed. Successfully sent {sent_count} DMs. ---")
        except Exception as e:
            log_dm(f"FATAL ERROR: {e}")
        finally:
            global_state["dm_running"] = False

    thread = threading.Thread(target=run_dms)
    thread.start()
    return jsonify({"success": True, "message": "DM Outreach started"})

@app.route("/api/dms/logs", methods=["GET"])
def dms_logs():
    return jsonify({
        "logs": global_state["dm_logs"],
        "running": global_state["dm_running"]
    })

# ==========================================
# Routes: APIs - Lead History
# ==========================================

@app.route("/api/history", methods=["GET"])
def get_history():
    domain = request.args.get("domain", "All")
    platform = request.args.get("platform", "All")
    dm_sent_filter = request.args.get("dm_sent", "All")
    
    leads = get_all_real_leads()
    
    if domain != "All":
        leads = [l for l in leads if l["domain"] == domain]
    if platform != "All":
        leads = [l for l in leads if l["platform"] == platform]
    if dm_sent_filter != "All":
        val = 1 if dm_sent_filter == "DM Sent" else 0
        leads = [l for l in leads if l["dm_sent"] == val]
        
    return jsonify({"leads": leads})

@app.route("/api/history/export", methods=["POST"])
def history_export():
    data = request.json
    leads = data.get("leads", [])
    domain = data.get("domain", "Combined")
    if not leads:
        return jsonify({"success": False, "error": "No leads to export"})
        
    df = pd.DataFrame(leads)
    df.rename(columns={
        "commenter_username": "Username",
        "platform": "Platform",
        "source_account": "Source Account",
        "comment_text": "Comment",
        "interest_score": "Score",
        "commenter_profile_url": "Profile URL",
        "dm_sent": "DM Sent",
        "scraped_at": "Date"
    }, inplace=True)
    df["DM Sent"] = df["DM Sent"].apply(lambda v: "Yes" if v == 1 else "No")
    
    filepath = export_real_leads(df, domain)
    return jsonify({"success": True, "filepath": filepath})

@app.route("/api/history/clear", methods=["POST"])
def history_clear():
    clear_all_real_leads()
    return jsonify({"success": True, "message": "Database cleared"})

if __name__ == "__main__":
    app.run(debug=False, port=5000, threaded=True)
