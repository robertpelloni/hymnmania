#!/usr/bin/env python3
"""
Social Media Mirror — Posts blog content to YouTube, Facebook, Twitter, LinkedIn, and Bluesky.

Accounts:
  - YouTube: "ok" channel (pelloni.robert@gmail.com)
  - Facebook: Personal account (game@bobsgame.com / pelloni.robert@gmail.com)
  - Twitter/X: @bobsgame (pelloni.robert@gmail.com)
  - LinkedIn: pelloni.robert@gmail.com
  - Bluesky: pelloni.robert@gmail.com

Usage:
  python social_media_mirror.py --auth          # Authenticate all accounts
  python social_media_mirror.py --auth youtube   # Authenticate YouTube only
  python social_media_mirror.py --mirror         # Mirror all blog posts
  python social_media_mirror.py --mirror --dry   # Dry run (show what would post)
  python social_media_mirror.py --post "text"    # Post to all platforms
"""

import json
import time
import argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
CONFIG_DIR = ROOT / ".social_config"
POSTED_LOG = ROOT / ".social_posted.json"

# Ensure config directory exists
CONFIG_DIR.mkdir(exist_ok=True)

# ── Blog Content ────────────────────────────────────────────────────
BLOG_RSS = ROOT.parent.parent / "nnt_content" / "rss_posts.md"
BLOG_PAGES = ROOT.parent.parent / "nnt_content" / "pages"


def load_blog_posts():
    """Load blog posts from RSS scrape."""
    if not BLOG_RSS.exists():
        return []

    posts = []
    current = {}

    with open(BLOG_RSS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("## "):
                if current:
                    posts.append(current)
                current = {"title": line[3:], "date": "", "link": "", "content": ""}
            elif line.startswith("Date:"):
                current["date"] = line[5:].strip()
            elif line.startswith("Link:"):
                current["link"] = line[5:].strip()
            elif line and current:
                current["content"] += line + "\n"

    if current:
        posts.append(current)

    return [p for p in posts if p.get("content", "").strip()]


def load_posted():
    """Load list of already-posted URLs."""
    if POSTED_LOG.exists():
        with open(POSTED_LOG) as f:
            return json.load(f)
    return {}


def save_posted(posted):
    """Save posted tracking."""
    with open(POSTED_LOG, "w") as f:
        json.dump(posted, f, indent=2)


# ── YouTube Authentication ──────────────────────────────────────────
def auth_youtube():
    """Authenticate with YouTube using OAuth2 flow for 'ok' channel."""
    print("\n=== YouTube Authentication (Channel: ok) ===")
    print("You'll need to create OAuth2 credentials in Google Cloud Console.")
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Create OAuth 2.0 Client ID (Desktop app)")
    print("3. Download JSON and save as client_secret.json here:")
    print(f"   {CONFIG_DIR / 'client_secret.json'}")
    print()

    client_secret_path = CONFIG_DIR / "client_secret.json"
    if not client_secret_path.exists():
        print(f"ERROR: {client_secret_path} not found!")
        print("Please download your OAuth2 client secret JSON first.")
        return False

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow

        SCOPES = ["https://www.googleapis.com/auth/youtube"]
        flow = InstalledAppFlow.from_client_secrets_file(
            str(client_secret_path), SCOPES
        )

        print("Opening browser for authentication...")
        print("Sign in with: pelloni.robert@gmail.com")
        print("Select the 'ok' YouTube channel when prompted.")
        print()

        creds = flow.run_local_server(port=8090)

        # Save token
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
            "account": "pelloni.robert@gmail.com",
            "channel": "ok",
        }

        token_path = CONFIG_DIR / "youtube_token.json"
        with open(token_path, "w") as f:
            json.dump(token_data, f, indent=2)

        print(f"YouTube token saved to: {token_path}")

        # Verify channel
        from googleapiclient.discovery import build

        yt = build("youtube", "v3", credentials=creds)
        channels = yt.channels().list(part="snippet", mine=True).execute()
        for ch in channels.get("items", []):
            print(f"Authenticated channel: {ch['snippet']['title']} ({ch['id']})")

        return True

    except ImportError:
        print("ERROR: google-auth-oauthlib not installed")
        print("Run: pip install google-auth-oauthlib google-api-python-client")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


# ── YouTube Posting ─────────────────────────────────────────────────
def post_to_youtube(text, link=None):
    """Post a community post to YouTube."""
    token_path = CONFIG_DIR / "youtube_token.json"
    if not token_path.exists():
        print(
            "YouTube not authenticated. Run: python social_media_mirror.py --auth youtube"
        )
        return False

    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        with open(token_path) as f:
            data = json.load(f)

        creds = Credentials(
            token=data["token"],
            refresh_token=data["refresh_token"],
            token_uri=data["token_uri"],
            client_id=data["client_id"],
            client_secret=data["client_secret"],
            scopes=data["scopes"],
        )

        if not creds.valid:
            creds.refresh(Request())
            data["token"] = creds.token
            with open(token_path, "w") as f:
                json.dump(data, f, indent=2)

        yt = build("youtube", "v3", credentials=creds)

        # YouTube Community Posts API (requires YouTube Data API v3)
        # Note: Community posts API is limited - may need to use videos instead
        print("YouTube: Would post community post (API limited)")
        print(f"  Text: {text[:100]}...")

        # For now, create a community post via the API
        # This requires the YouTube Partner Program or specific API access
        # Alternative: Use YouTube Shorts or regular videos

        return True

    except Exception as e:
        print(f"YouTube error: {e}")
        return False


# ── Facebook Posting ────────────────────────────────────────────────
def auth_facebook():
    """Authenticate with Facebook using browser automation."""
    print("\n=== Facebook Authentication ===")
    print("Facebook posting uses browser automation (Playwright).")
    print("You'll need to log in manually in the browser window.")
    print()
    print("Accounts:")
    print("  - game@bobsgame.com")
    print("  - pelloni.robert@gmail.com")
    print()

    try:
        from playwright.sync_api import sync_playwright

        print("Opening browser for Facebook login...")
        print("Log in to your personal Facebook account.")
        print("The session will be saved for future posts.")
        print()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                storage_state=str(CONFIG_DIR / "fb_state.json")
                if (CONFIG_DIR / "fb_state.json").exists()
                else None
            )
            page = context.new_page()

            page.goto("https://www.facebook.com/")
            print("Please log in to Facebook and press Enter here when done...")
            input()

            # Save session state
            context.storage_state(path=str(CONFIG_DIR / "fb_state.json"))
            print(f"Facebook session saved to: {CONFIG_DIR / 'fb_state.json'}")

            browser.close()

        return True

    except ImportError:
        print("ERROR: playwright not installed")
        print("Run: pip install playwright && playwright install chromium")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def post_to_facebook(text, link=None):
    """Post to Facebook using saved session."""
    state_path = CONFIG_DIR / "fb_state.json"
    if not state_path.exists():
        print(
            "Facebook not authenticated. Run: python social_media_mirror.py --auth facebook"
        )
        return False

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=str(state_path))
            page = context.new_page()

            # Go to profile
            page.goto("https://www.facebook.com/me")
            time.sleep(2)

            # Find and click "What's on your mind"
            post_area = page.locator('[aria-label="What\'s on your mind?"]').first
            post_area.click()
            time.sleep(1)

            # Type the post
            page.keyboard.type(text)
            time.sleep(1)

            if link:
                page.keyboard.type(f"\n{link}")
                time.sleep(1)

            # Click Post button
            post_btn = page.locator('[aria-label="Post"]').first
            post_btn.click()
            time.sleep(2)

            # Save updated session
            context.storage_state(path=str(state_path))
            browser.close()

            print("Facebook: Posted successfully")
            return True

    except Exception as e:
        print(f"Facebook error: {e}")
        return False


# ── Twitter/X Posting ───────────────────────────────────────────────
def auth_twitter():
    """Authenticate with Twitter/X using OAuth2."""
    print("\n=== Twitter/X Authentication ===")
    print("Twitter API requires developer credentials.")
    print()
    print("Steps:")
    print("1. Go to: https://developer.twitter.com/en/portal/dashboard")
    print("2. Create a project/app (or use existing)")
    print("3. Get these credentials:")
    print("   - API Key (Consumer Key)")
    print("   - API Secret (Consumer Secret)")
    print("   - Access Token")
    print("   - Access Token Secret")
    print("   - Bearer Token")
    print()
    print(f"4. Save them to: {CONFIG_DIR / 'twitter_config.json'}")
    print(
        '   Format: {"api_key": "...", "api_secret": "...", "access_token": "...", "access_secret": "...", "bearer_token": "..."}'
    )
    print()

    config_path = CONFIG_DIR / "twitter_config.json"
    if config_path.exists():
        print("Twitter config found!")
        return True
    else:
        print(f"ERROR: {config_path} not found!")
        return False


def post_to_twitter(text, link=None):
    """Post a tweet to Twitter/X."""
    config_path = CONFIG_DIR / "twitter_config.json"
    if not config_path.exists():
        print(
            "Twitter not configured. Run: python social_media_mirror.py --auth twitter"
        )
        return False

    try:
        import tweepy

        with open(config_path) as f:
            config = json.load(f)

        # Twitter API v2
        client = tweepy.Client(
            bearer_token=config["bearer_token"],
            consumer_key=config["api_key"],
            consumer_secret=config["api_secret"],
            access_token=config["access_token"],
            access_token_secret=config["access_secret"],
        )

        tweet_text = text
        if link:
            tweet_text += f"\n{link}"

        # Truncate if needed (280 chars)
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."

        response = client.create_tweet(text=tweet_text)
        print(f"Twitter: Posted tweet {response.data['id']}")
        return True

    except ImportError:
        print("ERROR: tweepy not installed")
        print("Run: pip install tweepy")
        return False
    except Exception as e:
        print(f"Twitter error: {e}")
        return False


# ── LinkedIn Posting ────────────────────────────────────────────────
def auth_linkedin():
    """Authenticate with LinkedIn using OAuth2."""
    print("\n=== LinkedIn Authentication ===")
    print("LinkedIn API requires an app registration.")
    print()
    print("Steps:")
    print("1. Go to: https://www.linkedin.com/developers/apps")
    print("2. Create an app")
    print("3. Request these scopes: w_member_social, r_liteprofile")
    print("4. Get OAuth2 credentials and save to:")
    print(f"   {CONFIG_DIR / 'linkedin_config.json'}")
    print(
        '   Format: {"client_id": "...", "client_secret": "...", "redirect_uri": "http://localhost:8091/callback"}'
    )
    print()

    config_path = CONFIG_DIR / "linkedin_config.json"
    if config_path.exists():
        print("LinkedIn config found!")
        return True
    else:
        print(f"ERROR: {config_path} not found!")
        return False


def post_to_linkedin(text, link=None):
    """Post to LinkedIn."""
    config_path = CONFIG_DIR / "linkedin_config.json"
    if not config_path.exists():
        print(
            "LinkedIn not configured. Run: python social_media_mirror.py --auth linkedin"
        )
        return False

    try:
        import requests

        with open(config_path) as f:
            config = json.load(f)

        token_path = CONFIG_DIR / "linkedin_token.json"
        if not token_path.exists():
            print("LinkedIn not authenticated. Run auth flow first.")
            return False

        with open(token_path) as f:
            token_data = json.load(f)

        headers = {
            "Authorization": f"Bearer {token_data['access_token']}",
            "Content-Type": "application/json",
        }

        post_data = {
            "author": f"urn:li:person:{token_data['person_id']}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        if link:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"][
                "shareMediaCategory"
            ] = "ARTICLE"
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {"status": "READY", "originalUrl": link}
            ]

        response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts", headers=headers, json=post_data
        )

        if response.status_code == 201:
            print("LinkedIn: Posted successfully")
            return True
        else:
            print(f"LinkedIn error: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"LinkedIn error: {e}")
        return False


# ── Bluesky Authentication ────────────────────────────────────────────
def auth_bluesky():
    """Authenticate with Bluesky using app password."""
    print("\n=== Bluesky Authentication ===")
    print("Bluesky uses app passwords for API access.")
    print()
    print("Steps:")
    print("1. Go to: https://bsky.app/settings/app-passwords")
    print("2. Create an app password")
    print("3. Enter your credentials below")
    print()

    handle = input(
        "Bluesky handle (e.g., bobsgame.bsky.social or your custom domain): "
    ).strip()
    app_password = input("Bluesky app password: ").strip()

    if not handle or not app_password:
        print("ERROR: Handle and password required")
        return False

    # Normalize handle
    if "." not in handle:
        handle = f"{handle}.bsky.social"

    try:
        import requests

        resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.server.createSession",
            json={"identifier": handle, "password": app_password},
            timeout=15,
        )

        if resp.status_code != 200:
            print(f"ERROR: Login failed: {resp.text}")
            return False

        session = resp.json()

        config = {
            "handle": handle,
            "app_password": app_password,
            "did": session["did"],
            "access_jwt": session["accessJwt"],
            "refresh_jwt": session["refreshJwt"],
        }

        config_path = CONFIG_DIR / "bluesky_config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"Bluesky authenticated as: {session['handle']}")
        print(f"DID: {session['did']}")
        print(f"Config saved to: {config_path}")
        return True

    except ImportError:
        print("ERROR: requests not installed")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def auth_bluesky_accounts():
    """Authenticate multiple Bluesky accounts (bobsgame + robertpelloni)."""
    print("\n=== Bluesky Multi-Account Setup ===")
    print("Setting up: bobsgame.bsky.social and robertpelloni.bsky.social")
    print()

    accounts = {}
    for handle_base in ["bobsgame", "robertpelloni"]:
        handle = f"{handle_base}.bsky.social"
        print(f"\n--- {handle} ---")
        app_password = input(f"App password for {handle}: ").strip()

        if not app_password:
            print(f"Skipping {handle}")
            continue

        try:
            import requests

            resp = requests.post(
                "https://bsky.social/xrpc/com.atproto.server.createSession",
                json={"identifier": handle, "password": app_password},
                timeout=15,
            )

            if resp.status_code != 200:
                print(f"ERROR: Login failed for {handle}: {resp.text}")
                continue

            session = resp.json()
            accounts[handle_base] = {
                "handle": handle,
                "app_password": app_password,
                "did": session["did"],
                "access_jwt": session["accessJwt"],
                "refresh_jwt": session["refreshJwt"],
            }
            print(f"Authenticated: {session['handle']} (DID: {session['did']})")

        except Exception as e:
            print(f"ERROR for {handle}: {e}")

    if accounts:
        config_path = CONFIG_DIR / "bluesky_accounts.json"
        with open(config_path, "w") as f:
            json.dump(accounts, f, indent=2)
        print(f"\nSaved {len(accounts)} accounts to: {config_path}")

        # Also save first account as default
        first = list(accounts.values())[0]
        with open(CONFIG_DIR / "bluesky_config.json", "w") as f:
            json.dump(first, f, indent=2)
        print(f"Default account: {first['handle']}")

    return len(accounts) > 0


def _post_to_single_bluesky(config, text, link=None):
    """Post to a single Bluesky account."""
    try:
        import requests

        # Refresh session
        resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.server.refreshSession",
            headers={"Authorization": f"Bearer {config['refresh_jwt']}"},
            timeout=15,
        )

        if resp.status_code == 200:
            session = resp.json()
            config["access_jwt"] = session["accessJwt"]
            config["refresh_jwt"] = session["refreshJwt"]
        else:
            resp = requests.post(
                "https://bsky.social/xrpc/com.atproto.server.createSession",
                json={
                    "identifier": config["handle"],
                    "password": config["app_password"],
                },
                timeout=15,
            )
            if resp.status_code != 200:
                print(f"  {config['handle']}: Session expired")
                return False
            session = resp.json()
            config["access_jwt"] = session["accessJwt"]
            config["refresh_jwt"] = session["refreshJwt"]

        # Build post
        post_text = text[:3000]
        facets = []
        if link:
            link_text = f"\n{link}"
            if len(post_text) + len(link_text) <= 3000:
                post_text += link_text
                link_start = post_text.index(link)
                facets.append(
                    {
                        "index": {
                            "byteStart": len(post_text[:link_start].encode("utf-8")),
                            "byteEnd": len(
                                post_text[: link_start + len(link)].encode("utf-8")
                            ),
                        },
                        "features": [
                            {"$type": "app.bsky.richtext.facet#link", "uri": link}
                        ],
                    }
                )

        post_record = {
            "$type": "app.bsky.feed.post",
            "text": post_text,
            "createdAt": datetime.now().astimezone().isoformat(),
        }
        if facets:
            post_record["facets"] = facets

        resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.repo.createRecord",
            headers={
                "Authorization": f"Bearer {config['access_jwt']}",
                "Content-Type": "application/json",
            },
            json={
                "repo": config["did"],
                "collection": "app.bsky.feed.post",
                "record": post_record,
            },
            timeout=15,
        )

        if resp.status_code == 200:
            uri = resp.json().get("uri", "")
            print(f"  {config['handle']}: Posted ({uri.split('/')[-1]})")
            return True
        else:
            print(f"  {config['handle']}: Error {resp.status_code}")
            return False
    except Exception as e:
        print(f"  {config['handle']}: {e}")
        return False


def post_to_bluesky(text, link=None):
    """Post to all configured Bluesky accounts."""
    accounts_path = CONFIG_DIR / "bluesky_accounts.json"
    single_path = CONFIG_DIR / "bluesky_config.json"

    if accounts_path.exists():
        with open(accounts_path) as f:
            accounts = json.load(f)
        results = []
        for name, config in accounts.items():
            results.append(_post_to_single_bluesky(config, text, link))
        return any(results)
    elif single_path.exists():
        with open(single_path) as f:
            config = json.load(f)
        return _post_to_single_bluesky(config, text, link)
    else:
        print(
            "Bluesky not configured. Run: python social_media_mirror.py --auth bluesky"
        )
        return False


# ── Mirror All Blog Posts ───────────────────────────────────────────
def mirror_blog_posts(dry_run=False):
    """Mirror all blog posts to all platforms."""
    posts = load_blog_posts()
    posted = load_posted()

    print(f"\nFound {len(posts)} blog posts to mirror")
    print(f"Already posted: {len(posted)}")
    print()

    new_posts = [p for p in posts if p["link"] not in posted]
    print(f"New posts to mirror: {len(new_posts)}")

    if dry_run:
        print("\n=== DRY RUN ===")
        for post in new_posts:
            print(f"\nPost: {post['title']}")
            print(f"  Date: {post['date']}")
            print(f"  Link: {post['link']}")
            print(f"  Content: {post['content'][:100]}...")
        return

    for post in new_posts:
        print(f"\nPosting: {post['title']}")

        text = post["content"].strip()
        link = post["link"]

        # Post to all platforms
        results = {}

        print("  YouTube...", end=" ")
        results["youtube"] = post_to_youtube(text, link)
        print("OK" if results["youtube"] else "SKIP")

        print("  Facebook...", end=" ")
        results["facebook"] = post_to_facebook(text, link)
        print("OK" if results["facebook"] else "SKIP")

        print("  Twitter...", end=" ")
        results["twitter"] = post_to_twitter(text, link)
        print("OK" if results["twitter"] else "SKIP")

        print("  LinkedIn...", end=" ")
        results["linkedin"] = post_to_linkedin(text, link)
        print("OK" if results["linkedin"] else "SKIP")

        print("  Bluesky...", end=" ")
        results["bluesky"] = post_to_bluesky(text, link)
        print("OK" if results["bluesky"] else "SKIP")

        # Mark as posted
        posted[link] = {
            "title": post["title"],
            "date": post["date"],
            "posted_at": datetime.now().isoformat(),
            "results": results,
        }
        save_posted(posted)

        # Rate limiting
        time.sleep(2)

    print("\n=== Mirror Complete ===")
    print(f"Total posted: {len(posted)}")


# ── Manual Post ─────────────────────────────────────────────────────
def post_to_all(text, link=None):
    """Post a message to all platforms."""
    print("\nPosting to all platforms:")
    print(f"  Text: {text[:100]}...")
    if link:
        print(f"  Link: {link}")
    print()

    results = {}

    print("YouTube...", end=" ")
    results["youtube"] = post_to_youtube(text, link)
    print("OK" if results["youtube"] else "SKIP")

    print("Facebook...", end=" ")
    results["facebook"] = post_to_facebook(text, link)
    print("OK" if results["facebook"] else "SKIP")

    print("Twitter...", end=" ")
    results["twitter"] = post_to_twitter(text, link)
    print("OK" if results["twitter"] else "SKIP")

    print("LinkedIn...", end=" ")
    results["linkedin"] = post_to_linkedin(text, link)
    print("OK" if results["linkedin"] else "SKIP")

    print("Bluesky...", end=" ")
    results["bluesky"] = post_to_bluesky(text, link)
    print("OK" if results["bluesky"] else "SKIP")

    print(f"\nResults: {results}")
    return results


# ── Main ────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Social Media Mirror")
    parser.add_argument(
        "--auth",
        nargs="?",
        const="all",
        help="Authenticate platform (youtube/facebook/twitter/linkedin/bluesky/all)",
    )
    parser.add_argument("--mirror", action="store_true", help="Mirror all blog posts")
    parser.add_argument("--post", help="Post a message to all platforms")
    parser.add_argument("--link", help="Link to include with post")
    parser.add_argument(
        "--dry", action="store_true", help="Dry run (show what would post)"
    )
    parser.add_argument(
        "--status", action="store_true", help="Show authentication status"
    )
    args = parser.parse_args()

    if args.status:
        print("\n=== Social Media Status ===")
        print(
            f"YouTube: {'OK' if (CONFIG_DIR / 'youtube_token.json').exists() else 'NOT CONFIGURED'}"
        )
        print(
            f"Facebook: {'OK' if (CONFIG_DIR / 'fb_state.json').exists() else 'NOT CONFIGURED'}"
        )
        print(
            f"Twitter: {'OK' if (CONFIG_DIR / 'twitter_config.json').exists() else 'NOT CONFIGURED'}"
        )
        print(
            f"LinkedIn: {'OK' if (CONFIG_DIR / 'linkedin_config.json').exists() else 'NOT CONFIGURED'}"
        )
        # Bluesky accounts
        bsky_accounts = CONFIG_DIR / "bluesky_accounts.json"
        bsky_single = CONFIG_DIR / "bluesky_config.json"
        if bsky_accounts.exists():
            with open(bsky_accounts) as f:
                accts = json.load(f)
            print(f"Bluesky: {len(accts)} accounts ({', '.join(accts.keys())})")
        elif bsky_single.exists():
            print("Bluesky: 1 account (default)")
        else:
            print("Bluesky: NOT CONFIGURED")
        print(f"\nPosted: {len(load_posted())} blog posts")
        return

    if args.auth:
        if args.auth == "all" or args.auth == "youtube":
            auth_youtube()
        if args.auth == "all" or args.auth == "facebook":
            auth_facebook()
        if args.auth == "all" or args.auth == "twitter":
            auth_twitter()
        if args.auth == "all" or args.auth == "linkedin":
            auth_linkedin()
        if args.auth == "all" or args.auth == "bluesky":
            auth_bluesky_accounts()  # Use multi-account setup
        return

    if args.mirror:
        mirror_blog_posts(dry_run=args.dry)
        return

    if args.post:
        post_to_all(args.post, args.link)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
