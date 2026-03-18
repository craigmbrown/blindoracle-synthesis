---
marp: true
theme: default
class: invert
paginate: true
---

# BlindOracle

## Private Intelligence, Verified Trust

25 AI agents that pay, trust, cooperate, and keep secrets on Ethereum (Base L2)

**The Synthesis Hackathon 2026**

---

# The Problem

AI agents today operate in isolated silos:

- **No standardized payments** between agents
- **No cryptographic proof** of agent behavior
- **No privacy** — positions visible before settlement
- **No persistent reputation** across sessions

Result: Agents depend on human intermediaries for every transaction, trust decision, and dispute.

---

# Architecture

```
┌─────────────────────────────────────────────┐
│              Agent Layer (25 agents)         │
│  Finance(3) Product(2) Security(4) Scale(3) │
│  Sales(3) Startup(3) Benchmark(1) Strat(2)  │
├─────────────────────────────────────────────┤
│              Identity Layer                  │
│  Nostr (secp256k1) + ERC-8004 + HMAC Auth   │
├─────────────────────────────────────────────┤
│              Payment Layer                   │
│  x402 (HTTP 402) + Fedimint eCash + LN      │
├─────────────────────────────────────────────┤
│              Trust Layer                     │
│  AgentRegistry.sol + 15 Nostr Proof Types   │
├─────────────────────────────────────────────┤
│              Privacy Layer                   │
│  AES-256-GCM + Commit-Reveal + Blind Sigs   │
└─────────────────────────────────────────────┘
```

---

# Agents that Pay

| Component | Detail |
|-----------|--------|
| **Protocol** | x402 (HTTP 402 Payment Required) |
| **Gateway** | Port 8402, systemd service |
| **Market Creation** | 0.001 USDC |
| **Predictions** | 0.5% fee |
| **Settlements** | 1% fee |
| **Rails** | Base USDC + Fedimint eCash + Lightning |

Real money. Real payments. Not a testnet demo.

---

# Agents that Trust

### 3-Layer Trust Stack

1. **Nostr Proofs** — 15 proof types (Kind 30010-30023), 3 relays
2. **AgentRegistry.sol** — On-chain reputation scores (0-10000)
3. **Per-Agent HMAC Identity** — Independent keypairs, SQLite DBs

### Results
- 17 agents scored
- 7 platinum-rated (score >95)
- 139 proofs, 330 Q&A pairs, 52 proof chains

---

# Agents that Cooperate

- **A2A Protocol**: JSON-RPC 2.0 server with 11 discoverable skills
- **Agent Card**: Standard discovery at `/.well-known/agent.json`
- **On-Chain Agreements**: UnifiedPredictionSubscription.sol
- **Consensus**: 67% Byzantine fault tolerance for market resolution

---

# Agents that Keep Secrets

### Encrypted Proofs
`AES-256-GCM` encrypted Nostr proofs (Kind 30099)
Published to relays but **opaque to outsiders**

### Commit-Reveal Settlement
```
commit = keccak256(secret || position || amount)
```
Zero identity linkage between commit and reveal

### Blind-Signed eCash
Fedimint integration for untraceable settlements

### Key Derivation
```
HMAC-SHA256(MASTER_SECRET, "{agent}:proof-encrypt")
```

---

# Production Evidence

| Artifact | Chain | Link |
|----------|-------|------|
| PrivateClaimVerifier.sol | Base Mainnet | `0x1CF2...9a3D` |
| UnifiedPredictionSubscription.sol | Base Mainnet | `0x0d5a...880c` |
| AgentRegistry.sol | Base Mainnet | `0x8004...a432` |
| ERC-8004 Registration | Base Mainnet | Tx `0xc24b...` |

All contracts deployed, verified, and processing real predictions.

---

# Tech Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.11 + Claude Code (claude-opus-4-6) |
| Identity | Nostr (secp256k1) + ERC-8004 |
| Payments | x402, Fedimint, Lightning |
| Privacy | AES-256-GCM, keccak256, blind signatures |
| Trust | AgentRegistry.sol, 15 proof types |
| Infrastructure | GCP VM, systemd, nginx |
| Framework | Custom (TheBaby/ETAC, 42+ agents) |

---

# Team

### BlindOracle (AI Agent)
- Model: claude-opus-4-6 via Claude Code
- Agent ID: 30607
- ERC-8004 Identity on Base Mainnet

### Craig M. Brown (Human)
- @cmb24k2
- Solo builder + AI collaborator

---

# What's Next

1. **Agent Marketplace** (Phase 3) — Agents list and purchase services
2. **Verification-as-a-Service** (Phase 4) — Third-party proof verification
3. **Cross-Chain** — Expand beyond Base to other L2s
4. **Agent Insurance** — Fedimint-backed risk pools

### Tracks
- Synthesis Open Track ($25K)
- Venice Private Agents ($11.5K)
- ERC-8004 Agents With Receipts ($8K)
- Let the Agent Cook ($8K)
- Agent Services on Base ($5K)

---

# Thank You

**GitHub**: github.com/craigmbrown/ETAC-System
**Dashboard**: craigmbrown.com/dashboards/
**ERC-8004**: BaseScan Agent #30607

*Private Intelligence, Verified Trust*
