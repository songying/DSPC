"""
Data Generator for Privacy Data Protocol

This module generates synthetic browser history data for testing the privacy-preserving
computation capabilities of the protocol.
"""

import random
import json
import uuid
import time
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any, Tuple

WEBSITE_CATEGORIES = {
    "short_video": [
        "tiktok.com", "youtube.com/shorts", "instagram.com/reels", 
        "snapchat.com", "vimeo.com/shorts", "triller.co", "byte.co",
        "dubsmash.com", "likee.com", "funimate.com"
    ],
    "ecommerce": [
        "amazon.com", "ebay.com", "walmart.com", "aliexpress.com", 
        "etsy.com", "shopify.com", "bestbuy.com", "target.com",
        "newegg.com", "wayfair.com", "overstock.com", "homedepot.com"
    ],
    "social_media": [
        "facebook.com", "twitter.com", "instagram.com", "linkedin.com",
        "pinterest.com", "reddit.com", "tumblr.com", "quora.com",
        "discord.com", "telegram.org", "whatsapp.com", "signal.org"
    ],
    "news": [
        "cnn.com", "bbc.com", "nytimes.com", "reuters.com", 
        "apnews.com", "washingtonpost.com", "theguardian.com",
        "bloomberg.com", "wsj.com", "economist.com", "time.com"
    ],
    "entertainment": [
        "netflix.com", "hulu.com", "disneyplus.com", "hbomax.com",
        "primevideo.com", "spotify.com", "pandora.com", "twitch.tv",
        "crunchyroll.com", "funimation.com", "imdb.com", "rottentomatoes.com"
    ],
    "education": [
        "coursera.org", "udemy.com", "edx.org", "khanacademy.org",
        "duolingo.com", "brilliant.org", "skillshare.com", "codecademy.com",
        "udacity.com", "pluralsight.com", "lynda.com", "masterclass.com"
    ],
    "productivity": [
        "google.com/docs", "office.com", "notion.so", "evernote.com",
        "trello.com", "asana.com", "monday.com", "slack.com",
        "zoom.us", "dropbox.com", "box.com", "drive.google.com"
    ],
    "technology": [
        "github.com", "stackoverflow.com", "medium.com", "dev.to",
        "techcrunch.com", "wired.com", "theverge.com", "cnet.com",
        "engadget.com", "arstechnica.com", "hackernoon.com", "slashdot.org"
    ]
}

ALL_WEBSITES = []
for category, sites in WEBSITE_CATEGORIES.items():
    ALL_WEBSITES.extend(sites)

def generate_timestamp(start_date: datetime, end_date: datetime) -> int:
    """Generate a random timestamp between start_date and end_date."""
    delta = end_date - start_date
    random_days = random.randrange(delta.days)
    random_seconds = random.randrange(86400)  # Seconds in a day
    random_date = start_date + timedelta(days=random_days, seconds=random_seconds)
    return int(random_date.timestamp())

def generate_browsing_session(
    user_id: str, 
    start_date: datetime, 
    end_date: datetime,
    min_sites: int = 5,
    max_sites: int = 20,
    short_video_preference: float = 0.0,
    ecommerce_after_video_preference: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Generate a browsing session with multiple site visits.
    
    Args:
        user_id: Unique identifier for the user
        start_date: Start date for the browsing session
        end_date: End date for the browsing session
        min_sites: Minimum number of sites to visit in the session
        max_sites: Maximum number of sites to visit in the session
        short_video_preference: Probability of visiting short video sites (None for random)
        ecommerce_after_video_preference: Probability of visiting ecommerce after video (None for random)
    
    Returns:
        List of browsing events
    """
    if short_video_preference is None:
        short_video_preference = random.random() * 0.7  # 0-70% preference
    
    if ecommerce_after_video_preference is None:
        ecommerce_after_video_preference = random.random() * 0.6  # 0-60% preference
    
    num_sites = random.randint(min_sites, max_sites)
    browsing_events = []
    
    timestamps = sorted([generate_timestamp(start_date, end_date) for _ in range(num_sites)])
    
    last_was_video = False
    
    for i, timestamp in enumerate(timestamps):
        if random.random() < short_video_preference:
            site = random.choice(WEBSITE_CATEGORIES["short_video"])
            last_was_video = True
        elif last_was_video and random.random() < ecommerce_after_video_preference:
            site = random.choice(WEBSITE_CATEGORIES["ecommerce"])
            last_was_video = False
        else:
            site = random.choice(ALL_WEBSITES)
            last_was_video = site in WEBSITE_CATEGORIES["short_video"]
        
        duration = random.randint(10, 1800)
        
        browsing_events.append({
            "user_id": user_id,
            "timestamp": timestamp,
            "site": site,
            "duration": duration,
            "referrer": browsing_events[-1]["site"] if i > 0 else "direct"
        })
    
    return browsing_events

def generate_user_profile() -> Tuple[str, float, float]:
    """
    Generate a user profile with preferences.
    
    Returns:
        Tuple of (user_id, short_video_preference, ecommerce_after_video_preference)
    """
    user_id = str(uuid.uuid4())
    
    short_video_preference = random.betavariate(2, 2)  # Beta distribution for more realistic distribution
    
    ecommerce_after_video_preference = random.betavariate(2, 3)
    
    return (user_id, short_video_preference, ecommerce_after_video_preference)

def generate_user_browsing_history(
    user_id: str,
    short_video_preference: float,
    ecommerce_after_video_preference: float,
    min_sessions: int = 10,
    max_sessions: int = 100,
    start_date: datetime = datetime(2024, 1, 1),
    end_date: datetime = datetime(2025, 3, 31)
) -> List[Dict[str, Any]]:
    """
    Generate complete browsing history for a user across multiple sessions.
    
    Args:
        user_id: Unique identifier for the user
        short_video_preference: User's preference for short video content
        ecommerce_after_video_preference: User's tendency to visit ecommerce after videos
        min_sessions: Minimum number of browsing sessions
        max_sessions: Maximum number of browsing sessions
        start_date: Start date for the browsing history
        end_date: End date for the browsing history
    
    Returns:
        List of browsing events across all sessions
    """
    num_sessions = random.randint(min_sessions, max_sessions)
    all_events = []
    
    for _ in range(num_sessions):
        session_events = generate_browsing_session(
            user_id,
            start_date,
            end_date,
            min_sites=5,
            max_sites=20,
            short_video_preference=short_video_preference,
            ecommerce_after_video_preference=ecommerce_after_video_preference
        )
        all_events.extend(session_events)
    
    all_events.sort(key=lambda x: x["timestamp"])
    
    return all_events

def generate_dataset(
    num_users: int = 1000,
    min_events_per_user: int = 1000,
    max_events_per_user: int = 10000,
    output_file: str = "browser_history_dataset.json"
) -> Dict[str, Any]:
    """
    Generate a complete dataset of browser history for multiple users.
    
    Args:
        num_users: Number of users to generate data for
        min_events_per_user: Minimum number of browsing events per user
        max_events_per_user: Maximum number of browsing events per user
        output_file: File to save the dataset to
    
    Returns:
        Dictionary with dataset metadata and statistics
    """
    print(f"Generating browser history dataset for {num_users} users...")
    start_time = time.time()
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 3, 31)
    
    dataset = {
        "metadata": {
            "description": "Synthetic browser history dataset for privacy-preserving computation",
            "num_users": num_users,
            "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "generated_at": datetime.now().isoformat(),
            "version": "1.0"
        },
        "users": {},
        "statistics": {
            "total_events": 0,
            "avg_events_per_user": 0,
            "short_video_percentage": 0,
            "ecommerce_after_video_percentage": 0
        }
    }
    
    total_events = 0
    short_video_visits = 0
    ecommerce_after_video = 0
    video_visits = 0
    
    os.makedirs("data", exist_ok=True)
    
    for i in range(num_users):
        if i % 100 == 0:
            print(f"Generated data for {i} users...")
        
        user_id, short_video_pref, ecommerce_after_video_pref = generate_user_profile()
        
        num_events = random.randint(min_events_per_user, max_events_per_user)
        
        user_events = []
        while len(user_events) < num_events:
            sessions_needed = (num_events - len(user_events)) // 10 + 1  # Rough estimate
            sessions_to_generate = min(sessions_needed, 10)  # Generate in batches
            
            for _ in range(sessions_to_generate):
                session_events = generate_browsing_session(
                    user_id,
                    start_date,
                    end_date,
                    min_sites=5,
                    max_sites=20,
                    short_video_preference=short_video_pref,
                    ecommerce_after_video_preference=ecommerce_after_video_pref
                )
                user_events.extend(session_events)
        
        user_events = user_events[:num_events]
        
        user_events.sort(key=lambda x: x["timestamp"])
        
        user_file = f"data/user_{user_id}.json"
        with open(user_file, 'w') as f:
            json.dump(user_events, f)
        
        dataset["users"][user_id] = {
            "short_video_preference": short_video_pref,
            "ecommerce_after_video_preference": ecommerce_after_video_pref,
            "num_events": len(user_events),
            "data_file": user_file
        }
        
        total_events += len(user_events)
        
        for i, event in enumerate(user_events):
            if any(video_site in event["site"] for video_site in WEBSITE_CATEGORIES["short_video"]):
                short_video_visits += 1
                video_visits += 1
                
                if i < len(user_events) - 1:
                    next_event = user_events[i + 1]
                    if any(ecomm_site in next_event["site"] for ecomm_site in WEBSITE_CATEGORIES["ecommerce"]):
                        ecommerce_after_video += 1
    
    dataset["statistics"]["total_events"] = total_events
    dataset["statistics"]["avg_events_per_user"] = total_events / num_users
    dataset["statistics"]["short_video_percentage"] = short_video_visits / total_events * 100
    dataset["statistics"]["ecommerce_after_video_percentage"] = ecommerce_after_video / video_visits * 100 if video_visits > 0 else 0
    
    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    end_time = time.time()
    print(f"Dataset generation complete in {end_time - start_time:.2f} seconds")
    print(f"Generated {total_events} browsing events for {num_users} users")
    print(f"Dataset metadata saved to {output_file}")
    
    return dataset

def generate_small_test_dataset(num_users: int = 100, events_per_user: int = 1000):
    """Generate a small test dataset for development and testing."""
    return generate_dataset(
        num_users=num_users,
        min_events_per_user=events_per_user,
        max_events_per_user=events_per_user,
        output_file="browser_history_test_dataset.json"
    )

if __name__ == "__main__":
    generate_small_test_dataset()
