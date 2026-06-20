# -----------------------------------------------------------------------------
# SmartLead AI – DM Sender Engine
# Coordinates DM sending on Instagram and Facebook and updates database.
# -----------------------------------------------------------------------------

import logging
from datetime import datetime
from database.db_manager import mark_dm_sent_real_lead  # We will define this next

logger = logging.getLogger("smartlead_dm")

def send_ig_dm(scraper, username: str, message: str, lead_id: int = None) -> bool:
    """
    Send an Instagram DM to a target username and update DB if successful.
    """
    success = scraper.send_dm(username, message)
    if success and lead_id is not None:
        try:
            mark_dm_sent_real_lead(lead_id)
            logger.info(f"Updated lead {lead_id} status to DM Sent in database.")
        except Exception as e:
            logger.error(f"Failed to update database for lead {lead_id}: {e}")
    return success

def send_fb_dm(scraper, profile_url: str, message: str, lead_id: int = None) -> bool:
    """
    Send a Facebook Messenger DM to a profile URL and update DB if successful.
    """
    success = scraper.send_messenger_dm(profile_url, message)
    if success and lead_id is not None:
        try:
            mark_dm_sent_real_lead(lead_id)
            logger.info(f"Updated lead {lead_id} status to DM Sent in database.")
        except Exception as e:
            logger.error(f"Failed to update database for lead {lead_id}: {e}")
    return success
