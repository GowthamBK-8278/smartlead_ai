# -----------------------------------------------------------------------------
# SmartLead AI – Instagram Scraper
# Login Strategy: Manual Browser (Playwright) → Session Cookie → instagrapi API
# This avoids all checkpoint/block issues by having the user log in normally.
# -----------------------------------------------------------------------------

import os
import time
import random
import logging
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

logger = logging.getLogger("smartlead_ig")


class IGScraper:
    def __init__(self, session_path: str = "session_ig.json"):
        self.session_path = session_path
        self.cl = Client()
        self.is_logged_in = False
        self.proxy = None  # Optional proxy string e.g. "http://user:pass@host:port"

        # State tracking for the UI
        self.login_in_progress = False
        self.login_error = None
        self.logged_in_username = None

        # Try to restore a previously saved session on startup
        self._try_load_session()

    # ──────────────────────────────────────────────────────────────────────────
    # Internal Helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _try_load_session(self):
        """Try to reuse a saved instagrapi session silently on startup."""
        if not os.path.exists(self.session_path):
            return
        try:
            logger.info("Attempting to restore saved Instagram session...")
            self.cl.load_settings(self.session_path)
            self.cl.get_timeline_feed()
            self.logged_in_username = self.cl.username
            self.is_logged_in = True
            logger.info(f"Instagram session restored for @{self.logged_in_username}.")
        except Exception as e:
            logger.warning(f"Saved session is invalid or expired ({e}). Fresh login required.")
            self.is_logged_in = False
            try:
                os.remove(self.session_path)
            except Exception:
                pass

    def format_proxy_url(self, proxy_str: str) -> str:
        """Normalize common proxy formats to a standard URL."""
        if not proxy_str:
            return ""
        proxy_str = proxy_str.strip().strip("'\"()[]{}<>,-;")
        if proxy_str.startswith(("http://", "https://", "socks5://", "socks4://")):
            return proxy_str
        parts = proxy_str.split(":")
        if len(parts) == 4:
            # Could be IP:PORT:USER:PASS or USER:PASS:IP:PORT
            is_ip_first = "." in parts[0] or parts[0].replace(".", "").isdigit()
            if is_ip_first:
                ip, port, user, password = parts
            else:
                user, password, ip, port = parts
            return f"http://{user}:{password}@{ip}:{port}"
        elif len(parts) == 2:
            return f"http://{parts[0]}:{parts[1]}"
        return proxy_str

    def set_proxy(self, proxy_url: str) -> None:
        """Set a proxy for all Instagram requests."""
        normalized = self.format_proxy_url(proxy_url)
        self.proxy = normalized if normalized else None
        if self.proxy:
            self.cl.set_proxy(self.proxy)
            logger.info(f"Instagram proxy set: {self.proxy}")
        else:
            self.cl.set_proxy(None)
            logger.info("Instagram proxy cleared.")

    # ──────────────────────────────────────────────────────────────────────────
    # Login Methods
    # ──────────────────────────────────────────────────────────────────────────

    def login_manual(self) -> bool:
        """
        PRIMARY login method.
        Opens a visible Chromium browser to instagram.com.
        Waits for the user to log in manually, then captures ALL cookies
        and uses them to authenticate the instagrapi client.
        """
        logger.info("Launching browser for manual Instagram login...")
        self.login_in_progress = True
        self.login_error = None
        self.is_logged_in = False

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=False,
                    args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
                )
                context = browser.new_context(
                    viewport=None,
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/125.0.0.0 Safari/537.36"
                    )
                )
                page = context.new_page()

                logger.info("Navigating to Instagram...")
                page.goto("https://www.instagram.com", wait_until="domcontentloaded")

                captured_cookies = None

                # Poll cookies every 2 seconds for up to 5 minutes
                for _ in range(150):
                    try:
                        if page.is_closed():
                            logger.warning("Browser window was closed by the user.")
                            break
                        cookies = context.cookies()
                        cookie_dict = {c["name"]: c["value"] for c in cookies}
                        if cookie_dict.get("sessionid"):
                            logger.info("sessionid cookie detected – login successful!")
                            # Wait a moment for all cookies to stabilize
                            time.sleep(3)
                            cookies = context.cookies()
                            captured_cookies = {c["name"]: c["value"] for c in cookies}
                            break
                    except Exception:
                        break
                    time.sleep(2)

                browser.close()

            if captured_cookies and captured_cookies.get("sessionid"):
                return self._connect_with_cookies(captured_cookies)
            else:
                self.login_error = "Login timed out or browser was closed before logging in."
                logger.error(self.login_error)
                self.login_in_progress = False
                return False

        except Exception as e:
            self.login_error = f"Error launching browser: {e}"
            logger.error(self.login_error)
            self.login_in_progress = False
            return False

    def login_with_session_id(self, session_id: str) -> bool:
        """
        ALTERNATIVE login method.
        Directly inject a session ID copied from the browser's cookies.
        """
        logger.info("Connecting via manually provided Session ID...")
        self.login_in_progress = True
        self.login_error = None
        return self._connect_with_cookies({"sessionid": session_id})

    def _connect_with_cookies(self, cookies: dict) -> bool:
        """
        Internal: authenticate instagrapi using browser cookies.
        Builds the session settings manually for maximum compatibility.
        Tries cookie injection first, then falls back to login_by_sessionid.
        """
        session_id = cookies.get("sessionid", "")
        if not session_id:
            self.login_error = "No sessionid found in cookies."
            self.login_in_progress = False
            return False

        try:
            logger.info("Building instagrapi session from browser cookies...")
            self.cl = Client()
            if self.proxy:
                self.cl.set_proxy(self.proxy)

            # Extract key values from cookies
            ds_user_id = cookies.get("ds_user_id", "")
            csrftoken = cookies.get("csrftoken", "")
            mid = cookies.get("mid", "")

            # Strategy 1: Try login_by_sessionid (cleanest approach)
            connected = False
            try:
                logger.info("Trying login_by_sessionid...")
                self.cl.login_by_sessionid(session_id)
                connected = True
                logger.info("login_by_sessionid succeeded.")
            except Exception as e_sid:
                logger.warning(f"login_by_sessionid failed ({e_sid}), trying manual cookie injection...")

            # Strategy 2: Fallback – manually inject all browser cookies
            if not connected:
                self.cl = Client()
                if self.proxy:
                    self.cl.set_proxy(self.proxy)
                self.cl.settings["cookies"] = dict(cookies)
                self.cl.settings["authorization_data"] = {
                    "ds_user_id": ds_user_id,
                    "sessionid": session_id,
                    "mid": mid,
                }
                if csrftoken:
                    self.cl.settings["cookies"]["csrftoken"] = csrftoken
                    self.cl.token = csrftoken
                logger.info("Manual cookie injection applied.")

            # Validate the session – try lightest methods first
            try:
                user_info = self.cl.account_info()
                self.logged_in_username = user_info.username
                logger.info(f"Validated session – logged in as @{self.logged_in_username}")
            except Exception as e1:
                logger.warning(f"account_info failed ({e1}), trying user_info_v1...")
                try:
                    if ds_user_id:
                        user_info = self.cl.user_info_v1(int(ds_user_id))
                        self.logged_in_username = user_info.username
                        logger.info(f"Validated via user_info_v1 – @{self.logged_in_username}")
                    else:
                        raise Exception("No ds_user_id available")
                except Exception as e2:
                    logger.warning(f"user_info_v1 also failed ({e2}). Trusting session cookie...")
                    self.logged_in_username = ds_user_id or "unknown"

            self.cl.dump_settings(self.session_path)
            self.is_logged_in = True
            self.login_in_progress = False
            logger.info(f"Instagram connected successfully as @{self.logged_in_username}.")
            return True

        except Exception as e:
            logger.error(f"Session authentication failed: {e}")
            self.login_error = f"Could not connect with that session. Error: {e}"
            self.is_logged_in = False
            self.login_in_progress = False
            return False

    def disconnect(self):
        """Clear the saved session and log out."""
        self.is_logged_in = False
        self.logged_in_username = None
        self.cl = Client()
        if os.path.exists(self.session_path):
            try:
                os.remove(self.session_path)
            except Exception:
                pass
        logger.info("Instagram disconnected and session cleared.")

    # ──────────────────────────────────────────────────────────────────────────
    # Scraping Methods
    # ──────────────────────────────────────────────────────────────────────────

    def get_user_posts(self, target_username: str, count: int = 15) -> List[Dict[str, Any]]:
        """
        Fetch recent posts from a target account.
        Returns a list of posts: media_id, url, caption, comment_count
        """
        if not self.is_logged_in:
            raise LoginRequired("Must be logged in to scrape Instagram.")

        try:
            logger.info(f"Fetching posts from @{target_username}...")
            time.sleep(random.uniform(2.0, 4.0))
            target_user_id = self.cl.user_id_from_username(target_username)

            time.sleep(random.uniform(2.0, 4.0))
            medias = self.cl.user_medias(target_user_id, amount=count)

            posts = []
            for media in medias:
                posts.append({
                    "media_id": media.id,
                    "url": f"https://instagram.com/p/{media.code}/",
                    "caption": media.caption_text or "",
                    "comment_count": media.comment_count,
                })
            logger.info(f"Got {len(posts)} posts from @{target_username}.")
            return posts

        except Exception as e:
            logger.error(f"Error fetching posts for @{target_username}: {e}")
            raise

    def get_post_comments(self, media_id: str, max_comments: int = 200) -> List[Dict[str, Any]]:
        """
        Fetch comments from a specific post.
        Returns a list of comments: username, text, profile_url, created_at
        """
        if not self.is_logged_in:
            raise LoginRequired("Must be logged in to scrape Instagram.")

        try:
            logger.info(f"Fetching comments for post {media_id}...")
            time.sleep(random.uniform(2.0, 4.0))
            comments = self.cl.media_comments(media_id, amount=max_comments)

            result = []
            for comment in comments:
                username = comment.user.username
                result.append({
                    "username": username,
                    "text": comment.text,
                    "profile_url": f"https://instagram.com/{username}/",
                    "created_at": str(comment.created_at_utc),
                })
            logger.info(f"Got {len(result)} comments from post {media_id}.")
            return result

        except Exception as e:
            logger.error(f"Error fetching comments for post {media_id}: {e}")
            return []

    # ──────────────────────────────────────────────────────────────────────────
    # DM Sending
    # ──────────────────────────────────────────────────────────────────────────

    def send_dm(self, target_username: str, message: str) -> bool:
        """
        Send a direct message to a target username.
        Returns True if successful, False otherwise.
        """
        if not self.is_logged_in:
            raise LoginRequired("Must be logged in to send Instagram DMs.")

        try:
            logger.info(f"Sending DM to @{target_username}...")
            time.sleep(random.uniform(3.0, 6.0))
            user_id = self.cl.user_id_from_username(target_username)

            time.sleep(random.uniform(3.0, 6.0))
            self.cl.direct_send(message, user_ids=[user_id])
            logger.info(f"DM sent successfully to @{target_username}.")
            return True

        except Exception as e:
            logger.error(f"Failed to send DM to @{target_username}: {e}")
            return False
