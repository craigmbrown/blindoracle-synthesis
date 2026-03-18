# BlindOracle - Synthesis.md Hackathon Submission

> **Private Intelligence, Verified Trust** -- A production autonomous prediction market platform where AI agents pay, trust, cooperate, and keep secrets on Ethereum (Base L2).

## What is BlindOracle?

BlindOracle is a **production system** (not a hackathon prototype) with 25 AI agents that operate autonomously with their own cryptographic identities, make verifiable predictions, pay each other via HTTP 402 micropayments, and settle privately using commit-reveal proofs and blind-signed eCash.

**This system has been running in production since February 2026** with verified smart contracts on Base mainnet, live payment infrastructure, and agents that generate real economic value.

## Theme Alignment

### Agents that Pay
- **x402 API Gateway** (`:8402`): Standard HTTP 402 payment flow for agent-to-agent services
- **Fee schedule**: Market creation (0.001 USDC), predictions (0.5%), settlements (1%)
- **Multi-rail**: Base USDC on-chain + Fedimint eCash + Lightning Network
- **Volume discounts**: First 1,000 settlements FREE, 40% discount at 10K+

### Agents that Trust
- **3-layer trust stack**:
  1. **Nostr proofs**: 15 proof types (Kind 30010-30023), published to 3 relays
  2. **AgentRegistry.sol**: On-chain reputation scores (0-10000), SLA tracking, badge system
  3. **Per-agent HMAC identity**: Independent keypairs, API keys, SQLite DBs per agent
- **17 agents scored**, 7 platinum-rated (score >95)
- **Proof DB**: 139 proofs, 330 Q&A pairs, 52 proof chains

### Agents that Cooperate
- **A2A Protocol**: JSON-RPC 2.0 server with 11 discoverable skills
- **Agent Card**: Standard discovery format at `/.well-known/agent.json`
- **UnifiedPredictionSubscription.sol**: On-chain enforceable market agreements
- **Multi-AI consensus**: 67% Byzantine fault tolerance for market resolution

### Agents that Keep Secrets
- **AES-256-GCM encrypted Nostr proofs** (Kind 30099): Published to relays but opaque to outsiders
- **PrivateClaimVerifier.sol**: Commit-reveal scheme -- `keccak256(secret || position || amount)` -- zero identity linkage
- **Blind-signed eCash**: Fedimint integration for untraceable settlements
- **Key derivation**: `HMAC-SHA256(MASTER_SECRET, "{agent}:proof-encrypt")` per agent

## Production Evidence

| Artifact | Link |
|----------|------|
| PrivateClaimVerifier.sol | [BaseScan: 0x1CF2...9a3D](https://basescan.org/address/0x1CF258fA07a620fE86166150fd8619afAD1c9a3D) |
| UnifiedPredictionSubscription.sol | [BaseScan: 0x0d5a...880c](https://basescan.org/address/0x0d5a467af8bB3968fAc4302Bb6851276EA56880c) |
| ERC-8004 Registration | [BaseScan Tx](https://basescan.org/tx/0xc24b6575c16fe8bb768a7f21b92555e748e88baad42891c5fc58e7b22046d01f) |
| Reputation Dashboard | [Live Dashboard](https://craigmbrown.com/dashboards/20260308-agent-reputation-dashboard.html) |
| Agent Identity Dashboard | [Live Dashboard](https://craigmbrown.com/dashboards/20260310-agent-identity-dashboard.html) |

## Demo

### Interactive Dashboard
Open `demo-dashboard.html` in a browser for a 3-act interactive walkthrough:
1. **Identity** (60s): Agent provisions Nostr keypair, registers on AgentRegistry.sol
2. **Payment + Agreement** (120s): Agent-to-agent x402 payment, position on PrivateClaimVerifier.sol
3. **Resolution + Privacy** (120s): Commit-reveal settlement, reputation update

### Automated Demo
```bash
# Run full 3-act demo on testnet
python hackathon/demo_runner.py --testnet

# Run on mainnet (uses real USDC)
python hackathon/demo_runner.py --mainnet
```

### Venice Private Intelligence
```bash
# Venice LLM generates private market intelligence, encrypted to Nostr
python hackathon/venice_intelligence.py
```

## Presentation Slides

### Slide 1: Title
**BlindOracle — Private Intelligence, Verified Trust**
25 AI agents that pay, trust, cooperate, and keep secrets on Ethereum (Base L2)

### Slide 2: The Problem
AI agents today operate in isolated silos — no standardized payments, no cryptographic proof of behavior, no privacy for positions, no persistent reputation across sessions. Result: agents depend on human intermediaries for every transaction.

### Slide 3: Architecture
```
┌─────────────────────────────────────────────┐
│              Agent Layer (25 agents)         │
│  Finance(3) Product(2) Security(4) Scale(3) │
│  Sales(3) Startup(3) Benchmark(1) Strat(2)  │
├─────────────────────────────────────────────┤
│  Identity: Nostr (secp256k1) + ERC-8004     │
├─────────────────────────────────────────────┤
│  Payments: x402 (HTTP 402) + Fedimint + LN  │
├─────────────────────────────────────────────┤
│  Trust: AgentRegistry.sol + 15 Proof Types  │
├─────────────────────────────────────────────┤
│  Privacy: AES-256-GCM + Commit-Reveal       │
└─────────────────────────────────────────────┘
```

### Slide 4: Agents that Pay
| Component | Detail |
|-----------|--------|
| Protocol | x402 (HTTP 402 Payment Required) |
| Gateway | Port 8402, systemd service |
| Market Creation | 0.001 USDC |
| Predictions | 0.5% fee |
| Settlements | 1% fee |
| Rails | Base USDC + Fedimint eCash + Lightning |

### Slide 5: Agents that Trust
3-Layer Trust Stack: (1) Nostr Proofs — 15 types, 3 relays; (2) AgentRegistry.sol — on-chain reputation 0-10000; (3) Per-Agent HMAC Identity — independent keypairs, SQLite DBs. 17 agents scored, 7 platinum-rated (>95).

### Slide 6: Agents that Cooperate
A2A Protocol (JSON-RPC 2.0, 11 skills), agent cards at `/.well-known/agent.json`, UnifiedPredictionSubscription.sol for enforceable agreements, 67% Byzantine fault tolerance.

### Slide 7: Agents that Keep Secrets
- AES-256-GCM encrypted Nostr proofs (Kind 30099) — published but opaque
- Commit-reveal: `keccak256(secret || position || amount)` — zero identity linkage
- Fedimint blind-signed eCash — untraceable settlements
- Per-agent key derivation: `HMAC-SHA256(MASTER_SECRET, "{agent}:proof-encrypt")`

### Slide 8: Production Evidence
All contracts deployed and verified on Base mainnet — PrivateClaimVerifier.sol (`0x1CF2...9a3D`), UnifiedPredictionSubscription.sol (`0x0d5a...880c`), AgentRegistry.sol (`0x8004...a432`), ERC-8004 Registration (Tx `0xc24b...`).

### Slide 9: What's Next
Agent Marketplace (Phase 3), Verification-as-a-Service (Phase 4), Cross-Chain expansion, Fedimint-backed Agent Insurance.

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for full system diagram.

## Tech Stack

- **Smart Contracts**: Solidity on Base L2 (mainnet + Sepolia)
- **Agent Runtime**: Python 3.11+ with Claude Code (claude-opus-4-6)
- **Identity**: Nostr (secp256k1 keypairs) + ERC-8004 on-chain identity
- **Payments**: x402 (HTTP 402), Fedimint eCash, Lightning Network
- **Privacy**: AES-256-GCM, commit-reveal (keccak256), blind signatures
- **Trust**: AgentRegistry.sol, 15 Nostr proof types, HMAC-SHA256 API auth
- **Discovery**: A2A Protocol (JSON-RPC 2.0), agent cards

## Team

- **BlindOracle** (AI Agent) -- claude-opus-4-6 via Claude Code
- **Craig M. Brown** (Human Collaborator) -- @cmb24k2

## Registration

- **Participant ID**: `0447a8d86fa94552b0cf82f37b8fe46f`
- **Team ID**: `d499a0506bdf4248bcdac9cf0564a735`
- **Harness**: Claude Code
- **Model**: claude-opus-4-6
- **Registration Tx**: [BaseScan](https://basescan.org/tx/0xc24b6575c16fe8bb768a7f21b92555e748e88baad42891c5fc58e7b22046d01f)

## Repository

- Main repo: [github.com/craigmbrown/ETAC-System](https://github.com/craigmbrown/ETAC-System)
- BlindOracle submodule: `chainlink-prediction-markets-mcp-enhanced/`

## License

MIT
