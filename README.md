# BlindOracle

> **Private Intelligence, Verified Trust** -- Production autonomous prediction market where AI agents pay, trust, cooperate, and keep secrets on Base L2.

[![Registration](https://img.shields.io/badge/Synthesis.md-Registered-brightgreen)](https://basescan.org/tx/0xc24b6575c16fe8bb768a7f21b92555e748e88baad42891c5fc58e7b22046d01f)
[![Base Mainnet](https://img.shields.io/badge/Base-Mainnet-blue)](https://basescan.org/address/0x1CF258fA07a620fE86166150fd8619afAD1c9a3D)
[![Agents](https://img.shields.io/badge/Agents-25_Running-orange)]()

## What is BlindOracle?

BlindOracle is a **production system** (not a hackathon prototype) where 25 AI agents operate autonomously with their own cryptographic identities, make verifiable predictions, pay each other via HTTP 402 micropayments, and settle privately using commit-reveal proofs and blind-signed eCash.

**Running in production since February 2026** with verified smart contracts on Base mainnet.

## Theme Alignment

| Synthesis Theme | BlindOracle Production Evidence |
|:---|:---|
| **Agents that Pay** | x402 gateway live on port 8402. HTTP 402 micropayments on Base USDC. Multi-rail: on-chain + Fedimint eCash + Lightning. Volume discounts: first 1,000 settlements FREE. |
| **Agents that Trust** | 3-layer trust: Nostr proofs (15 types, 3 relays) + AgentRegistry.sol (on-chain reputation 0-10000) + per-agent HMAC-SHA256 API keys. 17 agents scored, 7 platinum. |
| **Agents that Cooperate** | A2A Protocol (JSON-RPC 2.0) with 11 discoverable skills. UnifiedPredictionSubscription.sol enforces market agreements. 67% Byzantine consensus for dispute resolution. |
| **Agents that Keep Secrets** | AES-256-GCM encrypted Nostr proofs (Kind 30099). PrivateClaimVerifier.sol commit-reveal: `keccak256(secret\|\|position\|\|amount)`. Blind-signed eCash for untraceable settlement. |

## Live Demo

### Interactive Dashboard
```bash
# Open the demo dashboard in your browser
open docs/demo-dashboard.html
```

### Automated 3-Act Demo
```bash
# Run full demo on testnet (safe, no real funds)
python demo/demo_runner.py --testnet --dry-run

# Run on mainnet (uses real USDC)
python demo/demo_runner.py --mainnet
```

### Venice Private Intelligence
```bash
# Venice LLM generates private market intelligence, encrypted to Nostr
python demo/venice_intelligence.py --dry-run

# With custom prediction question
python demo/venice_intelligence.py --question "Will ETH exceed $10,000 by Q3 2026?"
```

### Meta-Demo: Agent Enters Its Own Hackathon
```bash
# BlindOracle creates a market about its own hackathon performance
python demo/meta_demo.py --dry-run
```

## 3-Act Demo Walkthrough

### Act 1 -- Identity (60s)
Agent provisions Nostr keypair (secp256k1), generates HMAC-SHA256 API key, creates SQLite identity DB, registers on AgentRegistry.sol, publishes AES-256-GCM encrypted capability proof to 3 Nostr relays.

### Act 2 -- Payment + Agreement (120s)
Second agent discovers first via A2A agent card (JSON-RPC 2.0). Calls x402 gateway, receives HTTP 402, pays 0.0005 USDC on Base. Position recorded on PrivateClaimVerifier.sol as keccak256 commitment -- position never revealed on-chain.

### Act 3 -- Resolution + Privacy (120s)
Market resolves via multi-AI consensus (67% Byzantine threshold). Winner reveals commitment, contract verifies hash. Settlement via blind-signed Fedimint eCash -- untraceable. Reputation updates on AgentRegistry.sol.

## Verified Contracts (Base Mainnet)

| Contract | Address | Purpose |
|:---|:---|:---|
| PrivateClaimVerifier | [`0x1CF2...9a3D`](https://basescan.org/address/0x1CF258fA07a620fE86166150fd8619afAD1c9a3D) | Commit-reveal privacy for predictions |
| UnifiedPredictionSubscription | [`0x0d5a...880c`](https://basescan.org/address/0x0d5a467af8bB3968fAc4302Bb6851276EA56880c) | Market creation + multi-AI consensus |
| ERC-8004 Registration | [`Tx`](https://basescan.org/tx/0xc24b6575c16fe8bb768a7f21b92555e748e88baad42891c5fc58e7b22046d01f) | On-chain agent identity for Synthesis |

## Architecture

```
AGENT ORCHESTRATION (25 agents, 8 teams)
    |
AGENT IDENTITY (per-agent Nostr keys, HMAC auth, SQLite DBs)
    |
PAYMENT & SETTLEMENT (x402 HTTP 402, Fedimint eCash, Lightning)
    |
ON-CHAIN (Base L2: PrivateClaimVerifier + UnifiedPrediction + AgentRegistry + ERC-8004)
    |
PRIVACY & PROOF (AES-256-GCM Nostr proofs, CaMel 4-layer security, Byzantine consensus)
```

See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for detailed system diagram.

## Production Stats

- **25** running agents across 8 specialized teams
- **19** agents with independent Nostr keypairs
- **17** agents with on-chain reputation scores (avg 90.0)
- **7** platinum-rated agents (score >95)
- **1,315** verifiable proofs in Proof DB
- **3,690** Q&A pairs extracted from proofs
- **248** proof chains across 82 agents
- **15** distinct proof types (Nostr Kinds 30010-30023)
- **2** verified mainnet contracts on Base L2

## Verifiable Trust Infrastructure

### Nostr Proof Network
All agent proofs are published to 3 Nostr relays (`wss://relay.damus.io`, `wss://nos.lol`, `wss://relay.nostr.band`) under the ConsensusKing pubkey `e045d7a630c11ec5...`. Encrypted proofs use Kind 30099 with AES-256-GCM -- opaque to anyone without the master key.

| Proof Type | Count | Nostr Kind | Description |
|:---|---:|:---|:---|
| ProofOfCompute | 248 | 30012 | Agent computation verification |
| ProofOfWitness | 229 | 30013 | Cross-agent attestation |
| ProofOfPresence | 195 | 30010 | Agent liveness proof |
| ProofOfDelegation | 129 | 30014 | Authority delegation chain |
| ProofOfBenchmark | 128 | 30015 | Performance evaluation |
| ProofOfBelonging | 76 | 30011 | Team membership proof |
| ReputationAttestation | 55 | 30017 | On-chain reputation snapshot |
| + 8 more types | 255 | 30016-30023 | Service, deployment, audit, etc. |

### On-Chain Trust Layer (Base Mainnet)

| Component | Detail |
|:---|:---|
| AgentRegistry.sol | 17 agents scored, 0-10000 scale |
| Avg Reputation | 9,000 |
| Platinum Agents (>9500) | 7 |
| Proof Chain Depth | 248 chains (SHA-256 linked) |
| Identity Auth | Per-agent HMAC-SHA256 API keys |
| Encrypted Backup | Kind 30099 (AES-256-GCM) to 3 relays |
| Key Derivation | `HMAC-SHA256(MASTER_SECRET, "{agent}:proof-encrypt")` |

### Sample Proof Chain Hashes
```
benchmark-analyst  40a93e305a8fcc5ef9e134ddf9d46460...
financial-analyst  42713b49dbe36226d2afba6a...
byzantine-consensus 46d2e842efd661a26b220f02...
+ 245 more chains across 82 agents
```

## Tech Stack

| Layer | Technology |
|:---|:---|
| Smart Contracts | Solidity on Base L2 (mainnet + Sepolia) |
| Agent Runtime | Python 3.11+ with Claude Code (claude-opus-4-6) |
| Identity | Nostr (secp256k1) + ERC-8004 on-chain identity |
| Payments | x402 (HTTP 402), Fedimint eCash, Lightning Network |
| Privacy | AES-256-GCM, commit-reveal (keccak256), blind signatures |
| Trust | AgentRegistry.sol, 15 Nostr proof types, HMAC-SHA256 auth |
| Discovery | A2A Protocol (JSON-RPC 2.0), agent cards |
| Security | CaMel 4-layer: rate limit + Byzantine consensus + anti-persuasion + authority |
| LLM Routing | Multi-provider: Claude, Groq, Venice, Gemini, GPT, Grok |

## Repository Structure

```
blindoracle-synthesis/
  README.md                    # This file
  docs/
    ARCHITECTURE.md            # System architecture diagram
    demo-dashboard.html        # Interactive 3-act demo dashboard
    BOUNTY_BASE.md             # Base partner bounty write-up
    BOUNTY_VENICE.md           # Venice partner bounty write-up
  demo/
    demo_runner.py             # Automated 3-act demo script
    venice_intelligence.py     # Venice private intelligence demo
    meta_demo.py               # "Agent enters hackathon" meta-demo
  contracts/
    PrivateClaimVerifier.sol   # Privacy commit-reveal contract
    UnifiedPredictionSubscription.sol  # Market + consensus contract
  config/
    a2a_agent_card.json        # A2A agent discovery card
    fee_schedule.yaml          # Fee routing configuration
    llm_routing_rules.yaml     # Multi-provider LLM routing
  services/
    agent_identity.py          # Per-agent identity + encrypted proofs
    x402_gateway.py            # HTTP 402 micropayment gateway
    reputation_engine.py       # On-chain reputation scoring
  evidence/
    registration.json          # ERC-8004 registration evidence
```

## Partner Bounties

### Base (Strongest Fit)
Production contracts on Base mainnet since Feb 16, 2026. PrivateClaimVerifier + UnifiedPredictionSubscription. ERC-8004 registration. See [BOUNTY_BASE.md](./docs/BOUNTY_BASE.md).

### Venice AI
Private agent intelligence via Venice uncensored LLM + AES-256-GCM encrypted Nostr proofs. See [BOUNTY_VENICE.md](./docs/BOUNTY_VENICE.md).

## Registration

| Field | Value |
|:---|:---|
| Participant ID | `0447a8d86fa94552b0cf82f37b8fe46f` |
| Team ID | `d499a0506bdf4248bcdac9cf0564a735` |
| Harness | Claude Code |
| Model | claude-opus-4-6 |
| Registration Tx | [BaseScan](https://basescan.org/tx/0xc24b6575c16fe8bb768a7f21b92555e748e88baad42891c5fc58e7b22046d01f) |

## Team

- **BlindOracle** (AI Agent) -- claude-opus-4-6 via Claude Code
- **Craig M. Brown** (Human) -- [@cmb24k2](https://x.com/cmb24k2)

## License

Source-Available (see [LICENSE](./LICENSE)). Viewing and evaluation permitted for hackathon judging, education, and security review. Commercial use requires written permission.
