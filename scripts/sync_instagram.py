#!/usr/bin/env python3
"""Regenerate _data/instagram.yml (and the images under static/img/instagram/)
from the latest posts of the ComCom's Instagram account, so the home page's
cartelera follows the feed without anyone editing the site.

Usage: IG_TOKEN=... scripts/sync_instagram.py [--limit N] [--dry-run] [--token-out FILE]

Runs daily from .github/workflows/instagram.yml. Setup, done once:

1. In https://developers.facebook.com/apps create an app of type "Business"
   and add the "Instagram" product (API setup with Instagram business login).
2. Under "Generate access tokens", add the comcom.exactas.uba account and
   click "Generate token". Dashboard tokens are long-lived (60 days).
3. Store it as the repo secret IG_TOKEN (Settings > Secrets and variables >
   Actions).
4. Create a fine-grained personal access token with resource owner
   "comcomUBA" (the org may have to approve it), access to this repo only,
   permission "Secrets: Read and write" and the longest expiration allowed.
   Store it as the secret SECRETS_PAT. The workflow uses it to save the
   refreshed IG_TOKEN back, so the 60 days restart on every run; when the PAT
   expires, IG_TOKEN dies 60 days later.

If "Generate token" fails while the app is in development mode, give the
account the "Instagram Tester" role under App roles and accept the invite
from Instagram's settings.

If the token ever expires (the workflow fails and GitHub emails whoever last
touched it), repeat step 2 and overwrite IG_TOKEN.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "_data" / "instagram.yml"
IMG_DIR = REPO_ROOT / "static" / "img" / "instagram"
IMG_URL_PREFIX = "/static/img/instagram/"

API = "https://graph.instagram.com"
API_VERSION = "v25.0"
FIELDS = "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp"

SITE_LINK_RE = re.compile(r"(?:https?://)?comcom\.dc\.uba\.ar(/[^\s)\"'<>]*)?")
TITLE_MAX = 80


def get_json(url, params):
    query = urllib.parse.urlencode(params)
    with urllib.request.urlopen(f"{url}?{query}", timeout=30) as resp:
        return json.load(resp)


def fetch_media(token, limit):
    data = get_json(
        f"{API}/{API_VERSION}/me/media",
        {"fields": FIELDS, "limit": limit, "access_token": token},
    )
    return data.get("data", [])[:limit]


def refresh_token(token):
    data = get_json(
        f"{API}/refresh_access_token",
        {"grant_type": "ig_refresh_token", "access_token": token},
    )
    return data["access_token"]


def titulo(caption):
    first = next((l.strip() for l in caption.splitlines() if l.strip()), "")
    if len(first) <= TITLE_MAX:
        return first
    cut = first[: TITLE_MAX - 1]
    # Cut at the last space so a word isn't split in half.
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,.;:-") + "…"


def site_link(caption):
    # A post that points to a page of the site (e.g. comcom.dc.uba.ar/talleres/oktubre)
    # sends the card there, where the full info lives; otherwise to the post.
    match = SITE_LINK_RE.search(caption)
    path = (match.group(1) or "").rstrip(".,;:!?") if match else ""
    # A bare "comcom.dc.uba.ar" would just send the card back to the home.
    return path if path not in ("", "/") else None


def image_source(media):
    # Videos and reels have no still in media_url; carousels expose their
    # first image there.
    if media["media_type"] in ("VIDEO", "REELS"):
        return media.get("thumbnail_url")
    return media.get("media_url")


def to_post(media):
    caption = media.get("caption") or ""
    return {
        "id": media["id"],
        "fecha": media["timestamp"][:10],
        "titulo": titulo(caption),
        "link": site_link(caption) or media["permalink"],
        "permalink": media["permalink"],
        "imagen": f"{IMG_URL_PREFIX}{media['id']}.jpg",
    }


def sync_images(medias, dry_run):
    wanted = {f"{m['id']}.jpg": image_source(m) for m in medias}
    if not dry_run:
        IMG_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in wanted.items():
        path = IMG_DIR / name
        if path.exists():
            continue
        if dry_run:
            print(f"would download {path}")
            continue
        urllib.request.urlretrieve(url, path)
        print(f"downloaded {path}")
    # Only the latest posts are shown, so older images just bloat the repo.
    for path in IMG_DIR.glob("*.jpg") if IMG_DIR.is_dir() else []:
        if path.name in wanted:
            continue
        if dry_run:
            print(f"would remove {path}")
            continue
        path.unlink()
        print(f"removed {path}")


def write_data_file(posts, dry_run):
    text = yaml.dump(
        {"posts": posts},
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    if dry_run:
        print(f"--- would write {DATA_FILE} ---")
        print(text)
        return
    DATA_FILE.write_text(text, encoding="utf-8")
    print(f"wrote {DATA_FILE}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--token-out",
        type=Path,
        help="write a refreshed IG token to this file (never to stdout: CI logs are public)",
    )
    args = parser.parse_args()

    token = os.environ.get("IG_TOKEN")
    if not token:
        parser.error("IG_TOKEN is not set")

    medias = [m for m in fetch_media(token, args.limit) if image_source(m)]
    if not medias:
        sys.exit("the API returned no posts; refusing to empty the cartelera")

    sync_images(medias, args.dry_run)
    write_data_file([to_post(m) for m in medias], args.dry_run)

    if args.token_out:
        # Meta refuses to refresh tokens younger than 24 hours; that's fine,
        # the next daily run will.
        try:
            args.token_out.write_text(refresh_token(token), encoding="utf-8")
        except urllib.error.HTTPError as err:
            print(f"warning: could not refresh token: {err}", file=sys.stderr)


if __name__ == "__main__":
    main()
