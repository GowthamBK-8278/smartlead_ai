# -----------------------------------------------------------------------------
# SmartLead AI – Instagram Private API Scraper
# Using instagrapi library.
# -----------------------------------------------------------------------------

import os
import time
import random
import logging
from typing import List, Dict, Any
from instagrapi import Client
from instagrapi.exceptions import ClientError, LoginRequired, ChallengeRequired

logger = logging.getLogger("smartlead_ig")

class IGScraper:
    def __init__(self, session_path: str = "session_ig.json"):
        self.cl = Client()
        self.session_path = session_path
        self.is_logged_in = False
        self.proxy = None  # Optional proxy string e.g. "http://user:pass@host:port"
        
        # Challenge states
        self.challenge_pending = False
        self.challenge_choice = None
        self.challenge_username = None
        self.challenge_code = None
        
        # Login state tracking
        self.login_in_progress = False
        self.login_error = None
        
        # Register challenge handler
        self.cl.challenge_code_handler = self.challenge_code_handler

    def format_proxy_url(self, proxy_str: str) -> str:
        """Normalize common proxy formats (e.g. host:port:user:pass) to standard URL format."""
        if not proxy_str:
            return ""
        proxy_str = proxy_str.strip().strip("'\"()[]{}<>,-;")
        
        # If it already starts with a protocol scheme, return as is
        if (proxy_str.startswith("http://") or 
            proxy_str.startswith("https://") or 
            proxy_str.startswith("socks5://") or 
            proxy_str.startswith("socks4://")):
            return proxy_str
            
        # Split by colon
        parts = proxy_str.split(":")
        if len(parts) == 4:
            # Form A: IP:PORT:USER:PASS
            # Form B: USER:PASS:IP:PORT
            part0 = parts[0]
            # Simple heuristic: if part0 has dots or is an IP address
            is_ip_first = "." in part0 or part0.replace(".", "").isdigit()
            
            if is_ip_first:
                ip, port, user, password = parts
            else:
                user, password, ip, port = parts
                
            return f"http://{user}:{password}@{ip}:{port}"
        elif len(parts) == 2:
            # Form: IP:PORT
            ip, port = parts
            return f"http://{ip}:{port}"
            
        return proxy_str

    def set_proxy(self, proxy_url: str) -> None:
        """Set a proxy for all Instagram requests (e.g. 'http://user:pass@host:port')."""
        normalized = self.format_proxy_url(proxy_url)
        self.proxy = normalized if normalized else None
        if self.proxy:
            self.cl.set_proxy(self.proxy)
            logger.info(f"Instagram proxy set to: {self.proxy}")
        else:
            self.cl.set_proxy(None)
            logger.info("Instagram proxy cleared.")
        
    def challenge_code_handler(self, username: str, choice: Any) -> str:
        """
        Callback used by instagrapi when a login challenge is encountered.
        """
        logger.info(f"Challenge encountered for {username} (choice: {choice})")
        self.challenge_username = username
        self.challenge_choice = choice
        self.challenge_code = None
        self.challenge_pending = True
        
        # Wait for the operator to input the code via the Streamlit UI
        start_time = time.time()
        # Wait up to 5 minutes (300 seconds)
        while self.challenge_pending and (time.time() - start_time < 300):
            if self.challenge_code is not None:
                code = str(self.challenge_code).strip()
                logger.info(f"Providing code to instagrapi challenge handler.")
                self.challenge_pending = False
                return code
            time.sleep(1.0)
            
        self.challenge_pending = False
        logger.error("Timed out waiting for challenge code from operator.")
        return ""
        
    def login(self, username: str, password: str, force_relogin: bool = False) -> bool:
        """
        Log in to Instagram. Reuses session file if available.
        On new logins, sets a consistent Android device fingerprint to reduce
        challenge triggers.
        """
        self.login_in_progress = True
        self.login_error = None

        # Clear challenge state initially
        self.challenge_pending = False
        self.challenge_choice = None
        self.challenge_username = None
        self.challenge_code = None

        # ── Try loading a saved session first ─────────────────────────────────
        if not force_relogin and os.path.exists(self.session_path):
            try:
                logger.info("Attempting to load saved Instagram session...")
                self.cl.load_settings(self.session_path)
                self.cl.get_timeline_feed()
                self.is_logged_in = True
                logger.info("Instagram session loaded successfully.")
                self.login_in_progress = False
                return True
            except Exception as e:
                logger.warning(f"Saved session invalid ({e}). Will do fresh login...")
                # Remove stale session file so we start clean
                try:
                    os.remove(self.session_path)
                except Exception:
                    pass

        if not username or not password:
            logger.error("Instagram username and password must be provided.")
            self.login_error = "Username and password are required."
            self.login_in_progress = False
            return False

        # ── Fresh login ───────────────────────────────────────────────────────
        try:
            logger.info(f"Starting fresh Instagram login as {username}...")

            # Re-create client with fresh device fingerprint to avoid stale
            # device ID conflicts that trigger challenges
            self.cl = Client()
            self.cl.challenge_code_handler = self.challenge_code_handler
            self.cl.set_device(self.cl.device_settings)  # randomise device

            # Apply proxy if configured
            if self.proxy:
                self.cl.set_proxy(self.proxy)
                logger.info(f"Using proxy: {self.proxy}")

            time.sleep(random.uniform(1.5, 3.0))
            self.cl.login(username, password)
            self.cl.dump_settings(self.session_path)
            self.is_logged_in = True
            logger.info("Instagram login successful. Session saved.")
            self.login_in_progress = False
            return True

        except ChallengeRequired as e:
            # New-style challenge that instagrapi cannot resolve automatically
            logger.error(f"Instagram requires manual checkpoint resolution: {e}")
            self.login_error = (
                "CHECKPOINT_REQUIRED: Instagram has blocked this login attempt and requires "
                "you to verify your account manually. Please:\n"
                "1. Open Instagram on your phone or web browser.\n"
                "2. Log in with username 'we_are_here_07'.\n"
                "3. Follow the on-screen security verification steps.\n"
                "4. Once approved, come back here and click 'Verify & Connect Instagram' again."
            )
            self.is_logged_in = False
            self.login_in_progress = False
            return False

        except Exception as e:
            import traceback
            err = str(e) or repr(e)
            try:
                with open("ig_error_traceback.log", "w") as f:
                    traceback.print_exc(file=f)
            except Exception:
                pass
            logger.error(f"Instagram login failed: {err}")
            # IP blacklist / rate-limit error
            if "blacklist" in err.lower() or "change your ip" in err.lower() or "ip address" in err.lower():
                self.login_error = "IP_BANNED: " + err
            # Legacy / checkpoint challenge
            elif "legacy challenge" in err.lower() or "challenge_required" in err.lower():
                self.login_error = (
                    "CHECKPOINT_REQUIRED: Instagram requires manual verification before this "
                    "account can be used from a new device.\n\n"
                    "Steps to fix:\n"
                    "1. Open instagram.com in your browser and sign in with this account.\n"
                    "2. Complete whatever security check Instagram presents (code, selfie, etc.).\n"
                    "3. After successful browser login, return here and try again."
                )
            else:
                self.login_error = err
            self.is_logged_in = False
            self.login_in_progress = False
            return False

    def get_user_posts(self, target_username: str, count: int = 15) -> List[Dict[str, Any]]:
        """
        Fetch recent posts from a target account.
        Returns a list of posts with keys: media_id, url, caption, comment_count
        """
        if not self.is_logged_in:
            raise LoginRequired("Must be logged in to scrape Instagram.")

        try:
            logger.info(f"Fetching user ID for target account: {target_username}...")
            time.sleep(random.uniform(2.0, 4.0))
            target_user_id = self.cl.user_id_from_username(target_username)
            
            logger.info(f"Fetching up to {count} posts from {target_username}...")
            time.sleep(random.uniform(2.0, 4.0))
            medias = self.cl.user_medias(target_user_id, amount=count)
            
            posts = []
            for media in medias:
                post_url = f"https://instagram.com/p/{media.code}/"
                posts.append({
                    "media_id": media.id,
                    "url": post_url,
                    "caption": media.caption_text or "",
                    "comment_count": media.comment_count
                })
            
            logger.info(f"Successfully retrieved {len(posts)} posts from {target_username}.")
            return posts
        except Exception as e:
            logger.error(f"Error fetching posts for {target_username}: {e}")
            raise e

    def get_post_comments(self, media_id: str, max_comments: int = 200) -> List[Dict[str, Any]]:
        """
        Fetch comments from a specific post.
        Returns a list of comments with keys: username, text, profile_url, created_at
        """
        if not self.is_logged_in:
            raise LoginRequired("Must be logged in to scrape Instagram.")

        try:
            logger.info(f"Fetching comments for post {media_id}...")
            time.sleep(random.uniform(2.0, 4.0))
            comments = self.cl.media_comments(media_id, amount=max_comments)
            
            scraped_comments = []
            for comment in comments:
                username = comment.user.username
                scraped_comments.append({
                    "username": username,
                    "text": comment.text,
                    "profile_url": f"https://instagram.com/{username}/",
                    "created_at": str(comment.created_at_utc)
                })
            
            logger.info(f"Retrieved {len(scraped_comments)} comments from post {media_id}.")
            return scraped_comments
        except Exception as e:
            logger.error(f"Error fetching comments for post {media_id}: {e}")
            return []

    def send_dm(self, target_username: str, message: str) -> bool:
        """
        Send a DM to a target username.
        Returns True if successful, False otherwise.
        """
        if not self.is_logged_in:
            raise LoginRequired("Must be logged in to send Instagram DMs.")

        try:
            logger.info(f"Looking up user ID for {target_username} to send DM...")
            time.sleep(random.uniform(3.0, 6.0))
            user_id = self.cl.user_id_from_username(target_username)
            
            logger.info(f"Sending Instagram DM to {target_username}...")
            time.sleep(random.uniform(3.0, 6.0))
            self.cl.direct_send(message, user_ids=[user_id])
            logger.info(f"DM successfully sent to {target_username}.")
            return True
        except Exception as e:
            logger.error(f"Failed to send DM to {target_username}: {e}")
            return False
