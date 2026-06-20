# -----------------------------------------------------------------------------
# SmartLead AI – Facebook Playwright Scraper
# Handles manual login (Option B), session storage, post scraping,
# comment extraction, and sending messages.
# -----------------------------------------------------------------------------

import os
import time
import random
import logging
from typing import List, Dict, Any, Optional
from playwright.sync_api import sync_playwright, Page, BrowserContext

logger = logging.getLogger("smartlead_fb")

class FBScraper:
    def __init__(self, session_path: str = "fb_session.json"):
        self.session_path = session_path
        self.is_logged_in = False
        
    def check_session_exists(self) -> bool:
        """Check if a saved session JSON exists on disk."""
        return os.path.exists(self.session_path)

    def login_manual(self) -> bool:
        """
        Open a visible browser window, direct to Facebook,
        and wait for the user to log in manually.
        Once the cookie 'c_user' is present, save the storage state.
        """
        logger.info("Opening browser for manual Facebook login (Option B)...")
        with sync_playwright() as p:
            # Launch headful browser so the user can interact with it
            browser = p.chromium.launch(headless=False, args=["--start-maximized"])
            # Create a clean context
            context = browser.new_context(viewport=None)
            page = context.new_page()
            
            logger.info("Navigating to Facebook login page...")
            page.goto("https://www.facebook.com")
            
            logger.info("Waiting for user to log in manually in the browser window...")
            # We check the cookies every 2 seconds for up to 5 minutes (150 iterations)
            logged_in = False
            for i in range(150):
                if page.is_closed():
                    logger.warning("Browser window was closed by the user.")
                    break
                    
                cookies = context.cookies()
                # If c_user is in cookies, the user has logged in
                if any(c['name'] == 'c_user' for c in cookies):
                    logger.info("Login detected! Saving storage state...")
                    # Give it a second to stabilize
                    time.sleep(2)
                    context.storage_state(path=self.session_path)
                    logged_in = True
                    self.is_logged_in = True
                    break
                
                time.sleep(2)
                
            browser.close()
            
            if logged_in:
                logger.info(f"Facebook session saved to {self.session_path} successfully.")
                return True
            else:
                logger.error("Manual Facebook login timed out or failed.")
                return False

    def test_connection(self) -> bool:
        """Verify if the saved session is valid by navigating to Facebook home."""
        if not self.check_session_exists():
            logger.warning("No Facebook session file found.")
            return False
            
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(storage_state=self.session_path)
                page = context.new_page()
                page.goto("https://www.facebook.com", wait_until="domcontentloaded")
                
                cookies = context.cookies()
                has_c_user = any(c['name'] == 'c_user' for c in cookies)
                browser.close()
                
                if has_c_user:
                    self.is_logged_in = True
                    return True
                else:
                    logger.warning("Facebook session is expired or invalid (c_user cookie missing).")
                    return False
        except Exception as e:
            logger.error(f"Error testing Facebook connection: {e}")
            return False

    def get_page_posts(self, page_url: str, count: int = 15) -> List[str]:
        """
        Navigate to a Facebook page, scroll down, and scrape post URLs.
        """
        if not self.check_session_exists():
            raise Exception("No Facebook session. Please log in first.")
            
        logger.info(f"Scraping Facebook posts from {page_url}...")
        post_urls = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(storage_state=self.session_path)
                page = context.new_page()
                
                # Navigate to the page
                page.goto(page_url, wait_until="domcontentloaded")
                time.sleep(3)
                
                # Scroll down several times to load posts
                scrolls = max(5, count // 2)
                logger.info(f"Scrolling page {scrolls} times to load posts...")
                for s in range(scrolls):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(random.uniform(2.0, 3.5))
                
                # Execute JavaScript to find all post links
                logger.info("Extracting post URLs from DOM...")
                raw_urls = page.evaluate("""
                    () => {
                        const links = Array.from(document.querySelectorAll('a'));
                        const matches = [];
                        for (const link of links) {
                            const href = link.href;
                            if (!href) continue;
                            const isPost = href.includes('/posts/') || 
                                           href.includes('/permalink.php') || 
                                           href.includes('/videos/') || 
                                           href.includes('/photos/') || 
                                           href.includes('/watch/?v=') ||
                                           href.includes('story.php');
                            if (isPost && !matches.includes(href)) {
                                matches.push(href);
                            }
                        }
                        return matches;
                    }
                """)
                
                # Clean up URLs (remove tracking query parameters)
                for href in raw_urls:
                    try:
                        # Parse and rebuild URL cleanly
                        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
                        parsed = urlparse(href)
                        query_params = parse_qs(parsed.query)
                        
                        # Keep only crucial query params like 'id', 'v', 'story_fbid' if present
                        keep_params = {}
                        for p_name in ['id', 'v', 'story_fbid', 'fbid']:
                            if p_name in query_params:
                                keep_params[p_name] = query_params[p_name]
                                
                        new_query = urlencode(keep_params, doseq=True)
                        clean_url = urlunparse((
                            parsed.scheme,
                            parsed.netloc,
                            parsed.path,
                            parsed.params,
                            new_query,
                            parsed.fragment
                        ))
                        if clean_url not in post_urls:
                            post_urls.append(clean_url)
                    except Exception:
                        if href not in post_urls:
                            post_urls.append(href)
                            
                browser.close()
                
            logger.info(f"Extracted {len(post_urls)} post URLs from {page_url}.")
            # Return up to count
            return post_urls[:count]
            
        except Exception as e:
            logger.error(f"Error scraping Facebook posts: {e}")
            return []

    def get_post_comments(self, post_url: str, max_comments: int = 200) -> List[Dict[str, Any]]:
        """
        Open a Facebook post, expand comments, and extract comment data.
        """
        if not self.check_session_exists():
            raise Exception("No Facebook session. Please log in first.")
            
        logger.info(f"Fetching comments from post: {post_url}...")
        comments = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(storage_state=self.session_path)
                page = context.new_page()
                
                page.goto(post_url, wait_until="domcontentloaded")
                time.sleep(3)
                
                # Try to switch comment view to "All comments" to show everything
                try:
                    # Look for the sorting selector which usually says "Most relevant"
                    sort_button = page.locator('div[role="button"]:has-text("Most relevant"), div[role="button"]:has-text("Relevant")').first
                    if sort_button.is_visible(timeout=3000):
                        sort_button.click()
                        time.sleep(1.5)
                        all_comments_opt = page.locator('div[role="menuitem"]:has-text("All comments"), span:has-text("All comments")').first
                        if all_comments_opt.is_visible(timeout=3000):
                            all_comments_opt.click()
                            logger.info("Switched view to 'All comments'.")
                            time.sleep(3)
                except Exception as e:
                    logger.debug(f"Could not change comment sorting: {e}")
                
                # Click "View more comments" or "View previous comments" to expand comments
                expansion_clicks = 0
                max_clicks = 15  # Limit expansions to prevent loops/blocks
                
                while expansion_clicks < max_clicks:
                    # Look for links or buttons that say "View more comments", "Write a reply", "View previous comments"
                    expand_button = page.locator('span:has-text("View more comments"), span:has-text("View previous comments"), span:has-text("View write-in replies"), span:has-text("replies")').first
                    if expand_button.is_visible(timeout=2000):
                        try:
                            expand_button.click()
                            expansion_clicks += 1
                            time.sleep(random.uniform(1.5, 3.0))
                        except Exception:
                            break
                    else:
                        break
                
                logger.info(f"Expanded comments with {expansion_clicks} clicks. Extracting comments...")
                
                # Execute Javascript to extract comments from DOM
                comments = page.evaluate("""
                    () => {
                        const results = [];
                        // Select comment containers: roles can be comment or article inside comment section
                        const containers = Array.from(document.querySelectorAll('div[role="comment"], div[role="article"]'));
                        
                        for (const container of containers) {
                            // Find commenter link: an 'a' tag that represents the commenter profile
                            const links = Array.from(container.querySelectorAll('a'));
                            let profileUrl = "";
                            let username = "";
                            
                            for (const link of links) {
                                const href = link.href;
                                if (!href) continue;
                                const text = link.textContent.trim();
                                if (!text) continue;
                                
                                // Profile links typically exclude common platform URLs
                                const isProfile = !href.includes('/posts/') && 
                                                  !href.includes('/permalink.php') && 
                                                  !href.includes('/groups/') && 
                                                  !href.includes('/sharer/') && 
                                                  !href.includes('/hashtag/') &&
                                                  !href.includes('facebook.com/policies') &&
                                                  !href.includes('facebook.com/help');
                                                  
                                if (isProfile) {
                                    profileUrl = href;
                                    username = text;
                                    break;
                                }
                            }
                            
                            if (!profileUrl || !username) continue;
                            
                            // Find comment text: div/span with dir="auto"
                            const dirAutos = Array.from(container.querySelectorAll('div[dir="auto"], span[dir="auto"]'));
                            let commentText = "";
                            for (const el of dirAutos) {
                                const t = el.textContent.trim();
                                if (t && t !== username && t.length > commentText.length) {
                                    commentText = t;
                                }
                            }
                            
                            if (commentText) {
                                // Prevent duplicate comments in extraction
                                const alreadyAdded = results.some(r => r.username === username && r.text === commentText);
                                if (!alreadyAdded) {
                                    results.push({
                                        username: username,
                                        text: commentText,
                                        profile_url: profileUrl
                                    });
                                }
                            }
                        }
                        return results;
                    }
                """)
                
                browser.close()
                
            logger.info(f"Successfully extracted {len(comments)} comments from {post_url}.")
            return comments
            
        except Exception as e:
            logger.error(f"Error extracting comments from {post_url}: {e}")
            return []

    def send_messenger_dm(self, profile_url: str, message: str) -> bool:
        """
        Send a Messenger DM to a user profile.
        Uses direct messages URL if possible, otherwise falls back to clicking "Message" on profile.
        """
        if not self.check_session_exists():
            raise Exception("No Facebook session. Please log in first.")
            
        logger.info(f"Initiating FB Messenger DM to: {profile_url}...")
        
        # 1. Parse username/id from profile URL to construct direct messages URL
        # Format can be: facebook.com/profile.php?id=123456 or facebook.com/username
        import urllib.parse
        parsed = urllib.parse.urlparse(profile_url)
        path_parts = [p for p in parsed.path.split('/') if p]
        
        identifier = ""
        if "profile.php" in parsed.path:
            params = urllib.parse.parse_qs(parsed.query)
            if 'id' in params:
                identifier = params['id'][0]
        elif len(path_parts) > 0:
            # e.g., facebook.com/john.doe -> identifier = john.doe
            # make sure to skip subfolders
            identifier = path_parts[0]
            
        if not identifier:
            logger.error(f"Could not parse identifier from profile URL: {profile_url}")
            return False
            
        direct_msg_url = f"https://www.facebook.com/messages/t/{identifier}/"
        logger.info(f"Direct messages chat URL: {direct_msg_url}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(storage_state=self.session_path)
                page = context.new_page()
                
                # Strategy 1: Open direct messages URL
                logger.info(f"Navigating to direct chat URL: {direct_msg_url}...")
                page.goto(direct_msg_url, wait_until="domcontentloaded")
                time.sleep(5)
                
                # Locate Messenger text box
                # Typically div[role="textbox"][aria-label="Message"]
                logger.info("Looking for Messenger text box...")
                textbox = page.locator('div[role="textbox"][aria-label="Message"], div[role="textbox"]').first
                
                if textbox.is_visible(timeout=5000):
                    logger.info("Text box found. Typing message...")
                    textbox.focus()
                    textbox.fill(message)
                    time.sleep(1)
                    # Press Enter to send
                    page.keyboard.press("Enter")
                    time.sleep(2)
                    logger.info("Message sent successfully via direct chat link!")
                    browser.close()
                    return True
                
                # Strategy 2: Fall back to profile page + clicking Message button
                logger.info("Direct chat link textbox not visible. Falling back to profile page...")
                page.goto(profile_url, wait_until="domcontentloaded")
                time.sleep(4)
                
                # Locate Message button
                # Typically aria-label="Message" or role="button" with text Message
                msg_btn = page.locator('div[role="button"][aria-label="Message"], div[role="button"]:has-text("Message")').first
                if msg_btn.is_visible(timeout=5000):
                    logger.info("Message button found on profile page. Clicking it...")
                    msg_btn.click()
                    time.sleep(4) # Wait for popup chat to open
                    
                    # Look for input box in the popup chat
                    popup_textbox = page.locator('div[role="textbox"][aria-label="Message"], div[role="textbox"]').first
                    if popup_textbox.is_visible(timeout=5000):
                        logger.info("Popup chat text box found. Typing message...")
                        popup_textbox.focus()
                        popup_textbox.fill(message)
                        time.sleep(1)
                        page.keyboard.press("Enter")
                        time.sleep(2)
                        logger.info("Message sent successfully via profile page popup!")
                        browser.close()
                        return True
                    else:
                        logger.error("Could not locate text box in popup chat.")
                else:
                    logger.error("Could not locate Message button on profile page.")
                    
                browser.close()
                return False
                
        except Exception as e:
            logger.error(f"Error sending Messenger DM: {e}")
            return False
