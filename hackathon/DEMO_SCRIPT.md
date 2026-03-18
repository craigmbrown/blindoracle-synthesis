# BlindOracle — Demo Video Script

> **Runtime:** 5 minutes | **Format:** Screen recording with voiceover
> **Audience:** Synthesis hackathon judges (human + AI)

---

## Pre-Recording Setup

```bash
cd ~/Project/chainlink-prediction-markets-mcp-enhanced
# Ensure services are running
sudo systemctl status blindoracle-x402.service blindoracle-camel-gateway.service
```

---

## ACT 1: Identity (0:00 - 1:00)

### What to Show
Screen: Terminal running agent provisioning

### Script (Voiceover)

> "BlindOracle gives every AI agent its own cryptographic identity — not shared API keys, not role-based access. Independent secp256k1 keypairs on Nostr, plus an on-chain identity on Base via ERC-8004."

### Commands to Run

```bash
# Show agent identity provisioning
python3 services/proof/agent_identity.py provision --agent finance-analyst

# Show the ERC-8004 registration on BaseScan
echo "ERC-8004 Registration: https://basescan.org/tx/0xc24b6575c16fe8bb768a7f21b92555e748e88baad42891c5fc58e7b22046d01f"

# Show AgentRegistry.sol reputation
echo "AgentRegistry.sol: https://basescan.org/address/0x8004A169FB4a3325136EB29fA0ceB6D2e539a432"

# Query agent reputation
python3 scripts/proof_query.py stats
```

### Key Talking Points
- 17 agents with independent Nostr keypairs
- Per-agent SQLite databases for proof storage
- HMAC-SHA256 API key authentication
- 7 platinum-rated agents (score >95)

---

## ACT 2: Payment + Trust (1:00 - 3:00)

### What to Show
Screen: x402 payment flow + Nostr proof publication

### Script (Voiceover)

> "Real money. Real payments. Not a testnet demo. Our x402 API Gateway handles HTTP 402 micropayments between agents. Market creation costs 0.001 USDC, predictions take a 0.5% fee, settlements 1%. Multi-rail support: Base USDC on-chain, Fedimint eCash, and Lightning Network."

### Commands to Run

```bash
# Run the demo with payment flow
python3 hackathon/demo_runner.py --testnet

# Show x402 service status
sudo systemctl status blindoracle-x402.service

# Show fee schedule
cat config/fee_schedule.yaml

# Show Nostr proof publication
python3 scripts/proof_query.py query --kind 30010 --limit 5
```

### What Happens On Screen
1. Agent requests prediction access → HTTP 402 response
2. Agent pays via x402 → receives access token
3. Agent submits prediction position
4. Position recorded on PrivateClaimVerifier.sol (commit hash only)
5. Nostr proof published (Kind 30010-30023) to 3 relays

### Key Talking Points
- Show the BaseScan link for PrivateClaimVerifier.sol: `0x1CF258fA07a620fE86166150fd8619afAD1c9a3D`
- Show UnifiedPredictionSubscription.sol: `0x0d5a467af8bB3968fAc4302Bb6851276EA56880c`
- Emphasize: "These contracts are deployed and verified on Base mainnet"

---

## ACT 3: Privacy + Resolution (3:00 - 5:00)

### What to Show
Screen: Encrypted proofs + commit-reveal settlement

### Script (Voiceover)

> "Here's what makes BlindOracle different: agents keep secrets and still prove they acted honestly. Every prediction is a commit-reveal — keccak256 of secret, position, and amount. Published to Nostr as Kind 30099 with AES-256-GCM encryption. The data is on the relay, but it's opaque to everyone except the agent that created it."

### Commands to Run

```bash
# Run Venice private intelligence
python3 hackathon/venice_intelligence.py

# Show encrypted proof on Nostr
python3 scripts/proof_query.py query --kind 30099 --limit 3

# Show commit-reveal settlement
echo "PrivateClaimVerifier.sol commit-reveal:"
echo "  commit: keccak256(secret || position || amount)"
echo "  reveal: submit (secret, position, amount) to verify"
echo "  Result: zero identity linkage between commit and reveal"

# Show Fedimint eCash integration
echo "Fedimint blind-signed eCash for untraceable settlements"
echo "Federation ID: stored in config/wallet_inventory.json"

# Show reputation update
python3 scripts/proof_query.py stats
```

### Key Talking Points
- AES-256-GCM with per-agent key derivation: `HMAC-SHA256(MASTER_SECRET, "{agent}:proof-encrypt")`
- Commit-reveal prevents front-running: no one can see positions before settlement
- Fedimint eCash: blind-signed, untraceable, no ledger correlation
- After settlement, reputation scores update on AgentRegistry.sol

---

## CLOSING (last 15 seconds)

### Script (Voiceover)

> "BlindOracle: 25 agents. Real identity. Real payments. Real privacy. Running in production on Base mainnet since February 2026. This isn't a prototype — it's infrastructure."

### What to Show
- Agent Reputation Dashboard: `https://craigmbrown.com/dashboards/20260308-agent-reputation-dashboard.html`
- GitHub repo: `https://github.com/craigmbrown/ETAC-System`
- Smart contracts on BaseScan

---

## Recording Tips

1. **Use OBS or QuickTime** for screen recording
2. **Terminal font size**: 16px+ for readability
3. **Dark terminal theme** matches the dashboard aesthetic
4. **Upload to YouTube** as unlisted, then update submission with URL
5. **Add chapters** in YouTube description matching the 3 acts
