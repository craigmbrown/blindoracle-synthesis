#!/usr/bin/env python3
"""
Synthesis.md API Client
========================
Wrapper for the Synthesis hackathon API. Handles authentication,
project creation, track enrollment, and submission.

Usage:
    from hackathon.synthesis_api import SynthesisClient
    client = SynthesisClient()
    client.create_project(...)
    client.submit()

Copyright (c) 2025-2026 Craig M. Brown. All rights reserved.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

log = logging.getLogger("synthesis_api")

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False


class SynthesisClient:
    """Client for Synthesis.md hackathon API."""

    BASE_URL = "https://synthesis.devfolio.co"

    def __init__(self, api_key: str = None):
        env_path = PROJECT_ROOT / "hackathon" / ".env.synthesis"
        self.api_key = api_key or os.environ.get("SYNTHESIS_API_KEY", "")

        # Try loading from .env file
        if not self.api_key and env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith("SYNTHESIS_API_KEY="):
                        self.api_key = line.strip().split("=", 1)[1]
                        break

        if not self.api_key:
            log.warning("No SYNTHESIS_API_KEY found")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.participant_id = os.environ.get(
            "SYNTHESIS_PARTICIPANT_ID", "0447a8d86fa94552b0cf82f37b8fe46f"
        )
        self.team_id = os.environ.get(
            "SYNTHESIS_TEAM_ID", "d499a0506bdf4248bcdac9cf0564a735"
        )

    def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make authenticated API request."""
        if not _HAS_REQUESTS:
            return {"error": "requests library not installed"}

        url = f"{self.BASE_URL}{endpoint}"
        try:
            resp = requests.request(
                method, url, headers=self.headers, json=data, timeout=30
            )
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def get_profile(self) -> dict:
        """Get current participant profile."""
        return self._request("GET", f"/participants/{self.participant_id}")

    def get_team(self) -> dict:
        """Get team info."""
        return self._request("GET", f"/teams/{self.team_id}")

    def create_project(
        self,
        name: str = "BlindOracle",
        tagline: str = "Private Intelligence, Verified Trust",
        description: str = None,
        repo_url: str = "https://github.com/craigmbrown/ETAC-System",
        demo_url: str = None,
        video_url: str = None,
    ) -> dict:
        """Create or update hackathon project submission."""
        if description is None:
            description = (
                "Production autonomous prediction market platform with 25 AI agents, "
                "on-chain reputation (AgentRegistry.sol on Base), x402 micropayments, "
                "AES-256-GCM encrypted Nostr proofs, and commit-reveal privacy via "
                "PrivateClaimVerifier.sol. Running in production since February 2026."
            )

        data = {
            "name": name,
            "tagline": tagline,
            "description": description,
            "repoUrl": repo_url,
            "tracks": ["open-track"],
        }
        if demo_url:
            data["demoUrl"] = demo_url
        if video_url:
            data["videoUrl"] = video_url

        return self._request("POST", "/projects", data)

    def add_track(self, track_id: str) -> dict:
        """Enroll project in a specific prize track."""
        return self._request("POST", f"/projects/tracks", {"trackId": track_id})

    def log_conversation(self, message: str) -> dict:
        """Log a conversation entry (required for submission)."""
        return self._request("POST", "/conversation", {"message": message})

    def submit_project(self) -> dict:
        """Submit project for judging."""
        return self._request("POST", "/projects/submit")

    def get_tracks(self) -> dict:
        """List available prize tracks."""
        return self._request("GET", "/tracks")


def main():
    """CLI for Synthesis API operations."""
    import argparse
    parser = argparse.ArgumentParser(description="Synthesis.md API Client")
    parser.add_argument("action", choices=[
        "profile", "team", "create-project", "tracks",
        "log", "submit", "add-track"
    ])
    parser.add_argument("--message", type=str, help="Conversation log message")
    parser.add_argument("--track", type=str, help="Track ID to enroll in")
    parser.add_argument("--demo-url", type=str, help="Demo URL")
    parser.add_argument("--video-url", type=str, help="Video URL")
    args = parser.parse_args()

    client = SynthesisClient()

    if args.action == "profile":
        result = client.get_profile()
    elif args.action == "team":
        result = client.get_team()
    elif args.action == "create-project":
        result = client.create_project(
            demo_url=args.demo_url,
            video_url=args.video_url,
        )
    elif args.action == "tracks":
        result = client.get_tracks()
    elif args.action == "log":
        result = client.log_conversation(args.message or "BlindOracle demo completed")
    elif args.action == "submit":
        result = client.submit_project()
    elif args.action == "add-track":
        result = client.add_track(args.track or "open-track")
    else:
        result = {"error": f"Unknown action: {args.action}"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
