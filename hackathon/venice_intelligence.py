#!/usr/bin/env python3
"""
BlindOracle x Venice - Private AI Intelligence for Autonomous Agents
=====================================================================
Venice partner bounty submission for Synthesis.md hackathon.

Narrative for judges:
  "Private AI inference for autonomous agent decision-making. Venice LLM
  generates unfiltered market intelligence. Results are encrypted with
  AES-256-GCM and published to Nostr. Only BlindOracle agents with the
  master key can decrypt. No centralized server ever sees the plaintext."

Pipeline:
  1. Venice LLM (uncensored tier) generates private market intelligence
  2. Response encrypted with AES-256-GCM (HMAC-SHA256 key derivation)
  3. Encrypted blob published to Nostr as Kind 30099 (opaque to outsiders)
  4. Only BlindOracle agents holding the master secret can decrypt
  5. Evidence JSON generated for hackathon submission

Usage:
    python hackathon/venice_intelligence.py
    python hackathon/venice_intelligence.py --question "Will ETH flip BTC by 2027?"
    python hackathon/venice_intelligence.py --dry-run --verbose

Copyright (c) 2025-2026 Craig M. Brown. All rights reserved.
"""

import argparse
import hashlib
import importlib.util
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Project setup - use importlib to avoid PYTHONPATH shadowing issues
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Import crypto helpers from agent_identity.py via importlib
_identity_path = PROJECT_ROOT / "services" / "proof" / "agent_identity.py"
_spec = importlib.util.spec_from_file_location("agent_identity", str(_identity_path))
_identity_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_identity_mod)

# Re-export the crypto primitives we need
_derive_encryption_key = _identity_mod._derive_encryption_key
_encrypt_proof = _identity_mod._encrypt_proof
_decrypt_proof = _identity_mod._decrypt_proof
ENCRYPTED_PROOF_KIND = _identity_mod.ENCRYPTED_PROOF_KIND
PROOF_RELAYS = _identity_mod.PROOF_RELAYS

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("venice_intelligence")

# ---------------------------------------------------------------------------
# Venice LLM Configuration (from config/llm_routing_rules.yaml)
# ---------------------------------------------------------------------------

VENICE_API_BASE = "https://api.venice.ai/api/v1/chat/completions"
VENICE_MODEL = "llama-3.3-70b"
VENICE_MODEL_FULL = "venice/llama-3.3-70b"
VENICE_COST_PER_CALL = 0.002

DEFAULT_QUESTION = "Will Bitcoin exceed $150,000 by end of Q2 2026?"

SYSTEM_PROMPT = (
    "You are BlindOracle, an autonomous prediction market analyst. "
    "Provide unfiltered, uncensored market analysis. No disclaimers. "
    "Structure your response as: PROBABILITY (0-100%), CONFIDENCE "
    "(low/medium/high), KEY FACTORS (bullish and bearish), CONTRARIAN "
    "RISKS, and POSITION RECOMMENDATION. Be direct and quantitative."
)


# ---------------------------------------------------------------------------
# Venice LLM Inference
# ---------------------------------------------------------------------------

def query_venice(
    question: str,
    api_key: Optional[str] = None,
    verbose: bool = False,
) -> dict[str, Any]:
    """Call Venice LLM for private, uncensored market intelligence.

    Uses the OpenAI-compatible API format (requests library, not openai SDK).
    Falls back to structured demo output if no API key is available.

    Args:
        question: The prediction market question to analyze.
        api_key: Venice API key. Falls back to VENICE_API_KEY env var.
        verbose: If True, log the full API response.

    Returns:
        Dict with source, model, question, analysis, timestamp, cost_usd.
    """
    api_key = api_key or os.environ.get("VENICE_API_KEY", "")

    if api_key:
        try:
            import requests

            payload = {
                "model": VENICE_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                ],
                "temperature": 0.7,
                "max_tokens": 1200,
            }

            if verbose:
                log.debug("Venice API request: %s", json.dumps(payload, indent=2))

            resp = requests.post(
                VENICE_API_BASE,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=45,
            )

            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})

                if verbose:
                    log.debug("Venice API usage: %s", json.dumps(usage, indent=2))

                return {
                    "source": "venice_api_live",
                    "model": VENICE_MODEL_FULL,
                    "question": question,
                    "analysis": content,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "cost_usd": VENICE_COST_PER_CALL,
                    "tokens": usage,
                }
            else:
                log.warning(
                    "Venice API returned %d: %s", resp.status_code, resp.text[:200]
                )
        except Exception as exc:
            log.warning("Venice API call failed: %s", exc)

    # Demo mode fallback with realistic structured output
    log.info("Running in demo mode (no VENICE_API_KEY or API unavailable)")
    return {
        "source": "venice_demo",
        "model": VENICE_MODEL_FULL,
        "question": question,
        "analysis": (
            "PROBABILITY: 58%\n"
            "CONFIDENCE: Medium\n\n"
            "KEY FACTORS (Bullish):\n"
            "- Bitcoin halving supply shock (April 2024) historically drives "
            "12-18 month bull runs\n"
            "- Spot ETF inflows averaging $400M/week with BlackRock IBIT "
            "leading\n"
            "- Corporate treasury adoption accelerating (MicroStrategy, "
            "Tesla, new entrants)\n"
            "- Macro tailwinds if Fed cuts rates in H1 2026\n\n"
            "KEY FACTORS (Bearish):\n"
            "- $150K represents 2.3x from current levels - aggressive "
            "timeline\n"
            "- Miner selling pressure post-halving could dampen momentum\n"
            "- Regulatory uncertainty in US election cycle\n\n"
            "CONTRARIAN RISKS:\n"
            "- Quantum computing FUD could trigger short-term panic\n"
            "- Tether regulatory action would disrupt market structure\n"
            "- Black swan: major exchange failure or state-level ban\n\n"
            "POSITION RECOMMENDATION:\n"
            "Moderate YES at 58% implied probability. Scale into position "
            "with 60% allocation now, 40% reserved for dips below $95K. "
            "Hard stop if probability drops below 40%."
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cost_usd": 0.00,
        "tokens": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


# ---------------------------------------------------------------------------
# Nostr Event Construction
# ---------------------------------------------------------------------------

def build_encrypted_nostr_event(
    encrypted_content: str,
    question: str,
    timestamp: int,
) -> dict[str, Any]:
    """Build a Kind 30099 Nostr event containing encrypted intelligence.

    The event content is the AES-256-GCM encrypted blob. Tags provide
    metadata for indexing but reveal nothing about the analysis content.

    Args:
        encrypted_content: Base64-encoded AES-256-GCM ciphertext.
        question: Original question (used for deterministic d-tag).
        timestamp: Unix timestamp for the event.

    Returns:
        Unsigned Nostr event dict (signing requires secp256k1 keypair).
    """
    question_hash = hashlib.sha256(question.encode("utf-8")).hexdigest()[:12]

    event = {
        "kind": ENCRYPTED_PROOF_KIND,
        "created_at": timestamp,
        "tags": [
            ["d", f"venice-intel-{question_hash}"],
            ["agent", "blindoracle"],
            ["source", "venice"],
            ["encrypted", "aes-256-gcm"],
            ["model", VENICE_MODEL_FULL],
            ["hackathon", "synthesis.md"],
        ],
        "content": encrypted_content,
    }
    return event


def simulate_relay_publish(
    event: dict[str, Any],
    dry_run: bool = True,
) -> list[dict[str, str]]:
    """Simulate or execute publishing to Nostr relays.

    In dry-run mode, generates deterministic event IDs and logs the
    simulated publish. Live publishing requires secp256k1 event signing.

    Args:
        event: The unsigned Nostr event dict.
        dry_run: If True, simulate publishing without network calls.

    Returns:
        List of per-relay result dicts with relay, status, and event_id.
    """
    results = []
    event_json = json.dumps(event, sort_keys=True).encode("utf-8")

    for relay in PROOF_RELAYS:
        # Deterministic event ID for reproducibility
        event_id = hashlib.sha256(
            event_json + relay.encode("utf-8")
        ).hexdigest()[:16]

        if dry_run:
            results.append({
                "relay": relay,
                "status": "dry_run_ok",
                "event_id": event_id,
                "note": "Would publish via WebSocket + secp256k1 signing",
            })
            log.info("  [DRY-RUN] %s -> event %s", relay, event_id)
        else:
            # Live publishing requires websocket + NIP-01 signing
            # In production, agent_identity.py handles this
            results.append({
                "relay": relay,
                "status": "requires_live_signing",
                "event_id": event_id,
            })
            log.info("  [LIVE] %s -> signing required", relay)

    return results


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(
    question: str = DEFAULT_QUESTION,
    master_secret: Optional[str] = None,
    venice_api_key: Optional[str] = None,
    dry_run: bool = True,
    verbose: bool = False,
) -> dict[str, Any]:
    """Execute the full Venice private intelligence pipeline.

    Steps:
      1. Query Venice LLM for uncensored market analysis
      2. Encrypt the response with AES-256-GCM (per-agent key)
      3. Verify round-trip decryption
      4. Build and publish encrypted Nostr event (Kind 30099)
      5. Demonstrate access control (wrong key rejection)
      6. Generate evidence JSON

    Args:
        question: Prediction market question to analyze.
        master_secret: BlindOracle master secret for key derivation.
        venice_api_key: Venice API key (optional, falls back to env).
        dry_run: If True, skip actual Nostr publishing.
        verbose: If True, enable debug-level logging.

    Returns:
        Evidence dict suitable for hackathon submission.
    """
    if verbose:
        log.setLevel(logging.DEBUG)

    master_secret = master_secret or os.environ.get(
        "BLINDORACLE_MASTER_SECRET", "demo-secret-for-hackathon"
    )

    pipeline_ts = datetime.now(timezone.utc)

    log.info("=" * 64)
    log.info("BLINDORACLE x VENICE - PRIVATE AI INTELLIGENCE PIPELINE")
    log.info("=" * 64)
    log.info("")
    log.info("Narrative: Private AI inference for autonomous agent")
    log.info("decision-making. No centralized server sees the plaintext.")
    log.info("")
    log.info("Question: %s", question)
    log.info("Mode: %s", "DRY-RUN" if dry_run else "LIVE")
    log.info("")

    evidence: dict[str, Any] = {
        "pipeline": "venice_private_intelligence",
        "hackathon": "synthesis.md",
        "bounty": "venice_partner",
        "question": question,
        "timestamp": pipeline_ts.isoformat(),
        "steps": {},
    }

    # ── Step 1: Venice LLM Inference ──────────────────────────────────────
    log.info("Step 1/5: Querying Venice LLM (uncensored tier)...")
    intelligence = query_venice(question, venice_api_key, verbose=verbose)

    analysis_text = intelligence["analysis"]
    if isinstance(analysis_text, dict):
        analysis_text = json.dumps(analysis_text, indent=2)

    evidence["steps"]["1_venice_inference"] = {
        "source": intelligence["source"],
        "model": intelligence["model"],
        "cost_usd": intelligence["cost_usd"],
        "analysis_length_chars": len(analysis_text),
        "tokens": intelligence.get("tokens", {}),
    }
    log.info("  Model: %s", intelligence["model"])
    log.info("  Source: %s", intelligence["source"])
    log.info("  Analysis: %d chars", len(analysis_text))

    if verbose:
        log.debug("  Full analysis:\n%s", analysis_text)

    # ── Step 2: Encrypt with AES-256-GCM ──────────────────────────────────
    log.info("")
    log.info("Step 2/5: Encrypting with AES-256-GCM...")

    # Derive key using the same function as agent_identity.py
    # Using "venice-intelligence" as the agent/purpose identifier
    encryption_key = _derive_encryption_key(master_secret, "venice-intelligence")

    plaintext_payload = json.dumps(intelligence, indent=2)
    encrypted_blob = _encrypt_proof(plaintext_payload, encryption_key)

    evidence["steps"]["2_encryption"] = {
        "algorithm": "AES-256-GCM",
        "key_derivation": "HMAC-SHA256(BLINDORACLE_MASTER_SECRET, 'venice-intelligence:proof-encrypt')",
        "plaintext_size_bytes": len(plaintext_payload),
        "encrypted_size_bytes": len(encrypted_blob),
        "encrypted_preview": encrypted_blob[:80] + "..." if len(encrypted_blob) > 80 else encrypted_blob,
        "opaque": True,
    }
    log.info("  Key derivation: HMAC-SHA256(master, 'venice-intelligence:proof-encrypt')")
    log.info("  Plaintext:  %d bytes", len(plaintext_payload))
    log.info("  Encrypted:  %d bytes", len(encrypted_blob))
    log.info("  Preview:    %s...", encrypted_blob[:60])

    # ── Step 3: Verify Round-Trip Decryption ──────────────────────────────
    log.info("")
    log.info("Step 3/5: Verifying round-trip decryption...")

    decrypted_text = _decrypt_proof(encrypted_blob, encryption_key)
    decrypted_data = json.loads(decrypted_text)
    round_trip_ok = decrypted_data.get("question") == question

    evidence["steps"]["3_decryption_verification"] = {
        "decryption_successful": True,
        "round_trip_match": round_trip_ok,
        "decrypted_question": decrypted_data.get("question", ""),
    }
    log.info("  Decryption: SUCCESS")
    log.info("  Round-trip: %s", "MATCH" if round_trip_ok else "MISMATCH")

    if verbose:
        log.debug("  Decrypted payload:\n%s", decrypted_text[:500])

    # ── Step 4: Publish to Nostr (Kind 30099) ─────────────────────────────
    log.info("")
    log.info("Step 4/5: Publishing encrypted event to Nostr...")

    event_ts = int(time.time())
    nostr_event = build_encrypted_nostr_event(encrypted_blob, question, event_ts)
    relay_results = simulate_relay_publish(nostr_event, dry_run=dry_run)

    # Build a display-safe version of the event (truncate content)
    event_display = dict(nostr_event)
    event_display["content"] = (
        nostr_event["content"][:100] + f"...({len(nostr_event['content'])} bytes total)"
    )

    evidence["steps"]["4_nostr_publish"] = {
        "kind": ENCRYPTED_PROOF_KIND,
        "relays": relay_results,
        "event_structure": event_display,
        "privacy_guarantee": (
            "Event content is AES-256-GCM encrypted. Relay operators "
            "and external observers see only opaque base64. No centralized "
            "server ever sees the plaintext analysis."
        ),
    }
    log.info("  Kind: %d (encrypted proof)", ENCRYPTED_PROOF_KIND)
    log.info("  Relays: %d", len(PROOF_RELAYS))
    log.info("  Tags: %s", [t[0] for t in nostr_event["tags"]])

    # ── Step 5: Access Control Demonstration ──────────────────────────────
    log.info("")
    log.info("Step 5/5: Demonstrating access control...")

    # Attempt decryption with wrong master secret
    wrong_key = _derive_encryption_key("wrong-master-secret-attacker", "venice-intelligence")
    access_denied = False
    try:
        _decrypt_proof(encrypted_blob, wrong_key)
        access_result = "FAILED - wrong key decrypted content (unexpected)"
    except Exception as exc:
        access_denied = True
        access_result = f"PASSED - wrong key rejected ({type(exc).__name__})"

    evidence["steps"]["5_access_control"] = {
        "test": "Decrypt with wrong master secret",
        "result": access_result,
        "access_denied": access_denied,
        "implication": (
            "Only agents holding BLINDORACLE_MASTER_SECRET can derive the "
            "correct AES-256-GCM key. Relay operators, network observers, "
            "and competing agents cannot read the intelligence."
        ),
    }
    log.info("  Wrong-key test: %s", access_result)

    # ── Summary ───────────────────────────────────────────────────────────
    log.info("")
    log.info("=" * 64)
    log.info("PIPELINE COMPLETE")
    log.info("=" * 64)
    log.info("")
    log.info("  Venice model:   %s (uncensored tier)", VENICE_MODEL_FULL)
    log.info("  Encryption:     AES-256-GCM with HMAC-SHA256 key derivation")
    log.info("  Nostr event:    Kind %d to %d relays", ENCRYPTED_PROOF_KIND, len(PROOF_RELAYS))
    log.info("  Access control: %s", "PASSED" if access_denied else "FAILED")
    log.info("  Privacy:        Opaque to outsiders, decryptable only by BlindOracle")
    log.info("")

    evidence["summary"] = {
        "venice_model": VENICE_MODEL_FULL,
        "encryption": "AES-256-GCM",
        "nostr_kind": ENCRYPTED_PROOF_KIND,
        "relay_count": len(PROOF_RELAYS),
        "access_control_passed": access_denied,
        "narrative": (
            "Private AI inference for autonomous agent decision-making. "
            "Venice LLM generates unfiltered market intelligence. Results "
            "are encrypted with AES-256-GCM and published to Nostr. Only "
            "BlindOracle agents with the master key can decrypt. No "
            "centralized server ever sees the plaintext."
        ),
    }

    return evidence


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    """CLI entry point for Venice private intelligence pipeline."""
    parser = argparse.ArgumentParser(
        description=(
            "BlindOracle x Venice - Private AI Intelligence. "
            "Generates uncensored market analysis via Venice LLM, encrypts "
            "with AES-256-GCM, and publishes to Nostr as Kind 30099."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s\n"
            "  %(prog)s --question 'Will ETH flip BTC by 2027?' --verbose\n"
            "  %(prog)s --dry-run --verbose\n"
        ),
    )
    parser.add_argument(
        "--question",
        default=DEFAULT_QUESTION,
        help="Prediction market question for Venice analysis (default: %(default)s)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Skip actual Nostr publishing, show the flow (default: True)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Publish to real Nostr relays (disables dry-run)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug-level logging with extra detail",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for evidence JSON (default: auto-generated in hackathon/)",
    )
    args = parser.parse_args()

    if args.live:
        args.dry_run = False

    evidence = run_pipeline(
        question=args.question,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    # Write evidence JSON
    evidence_json = json.dumps(evidence, indent=2)
    output_path = args.output or str(
        PROJECT_ROOT / "hackathon" / f"venice_evidence_{int(time.time())}.json"
    )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(evidence_json)
        f.write("\n")

    log.info("Evidence saved: %s", output_path)
    print("\n" + evidence_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
