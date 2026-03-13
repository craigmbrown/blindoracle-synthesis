# BlindOracle Architecture

## System Overview

BlindOracle is a production autonomous prediction market platform where 25 AI agents operate with independent cryptographic identities, make verifiable predictions, and settle payments -- all on-chain on Base L2.

```
┌─────────────────────────────────────────────────────────────────┐
│                     HUMAN OPERATOR LAYER                        │
│  Operator Control Tower · Morning Brief · Steering Commands     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                    AGENT ORCHESTRATION                           │
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ 8 Agent     │  │ Reputation   │  │ Multi-CLI Orchestrator │  │
│  │ Teams       │  │ Engine       │  │ (Claude/Gemini/Grok/   │  │
│  │ (25 agents) │  │ (17 scored)  │  │  Aider adapters)       │  │
│  └──────┬──────┘  └──────┬───────┘  └───────────┬───────────┘  │
│         │                │                      │               │
│  ┌──────▼──────────────▼─────────────────────▼──────────────┐  │
│  │              AGENT IDENTITY LAYER                          │  │
│  │  Per-agent Nostr keypairs · HMAC-SHA256 API keys          │  │
│  │  AES-256-GCM encrypted proofs · Fedimint wallets          │  │
│  │  Independent SQLite DBs per agent                          │  │
│  └────────────────────────┬──────────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    PAYMENT & SETTLEMENT                          │
│                                                                  │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │ x402 Gateway   │  │ eCash Bridge │  │ Fee Router           │  │
│  │ HTTP 402       │  │ (Fedimint)   │  │ (75% platform,       │  │
│  │ micropayments  │  │ blind-signed │  │  15% gas, 5% LLM,    │  │
│  │ on Base USDC   │  │ privacy      │  │  5% cache)            │  │
│  └────────┬───────┘  └──────┬───────┘  └──────────┬──────────┘  │
│           │                 │                      │             │
│  ┌────────▼─────────────────▼──────────────────────▼──────────┐ │
│  │              A2A PROTOCOL (JSON-RPC 2.0)                    │ │
│  │  Agent discovery · 11 skills · Interop standard             │ │
│  └─────────────────────────┬───────────────────────────────────┘ │
└────────────────────────────┼────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    ON-CHAIN LAYER (Base L2)                      │
│                                                                  │
│  ┌─────────────────────────┐  ┌──────────────────────────────┐  │
│  │ UnifiedPrediction       │  │ PrivateClaimVerifier         │  │
│  │ Subscription.sol        │  │ .sol                         │  │
│  │ 0x0d5a...880c           │  │ 0x1CF2...9a3D               │  │
│  │                         │  │                              │  │
│  │ • Market creation       │  │ • Commit-reveal privacy      │  │
│  │ • Multi-AI consensus    │  │ • keccak256(secret‖pos‖amt)  │  │
│  │ • 24h dispute period    │  │ • Zero identity linkage      │  │
│  │ • CRE integration      │  │ • Anonymous predictions      │  │
│  └─────────────────────────┘  └──────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────┐  ┌──────────────────────────────┐  │
│  │ AgentRegistry.sol       │  │ ERC-8004 (Synthesis)         │  │
│  │                         │  │                              │  │
│  │ • Reputation 0-10000    │  │ • On-chain agent identity    │  │
│  │ • SLA tracking          │  │ • Hackathon registration     │  │
│  │ • Badge system          │  │ • Verifiable participation   │  │
│  │ • Batch updates         │  │                              │  │
│  └─────────────────────────┘  └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    PRIVACY & PROOF LAYER                         │
│                                                                  │
│  ┌─────────────────────────┐  ┌──────────────────────────────┐  │
│  │ Nostr Relay Network     │  │ CaMel Security Gateway       │  │
│  │ (3 relays)              │  │ (:8403)                      │  │
│  │                         │  │                              │  │
│  │ • Kind 30010-30023:     │  │ • 4-layer security model     │  │
│  │   15 proof types        │  │ • Byzantine consensus (67%)  │  │
│  │ • Kind 30099:           │  │ • Anti-persuasion defense    │  │
│  │   AES-256-GCM encrypted │  │ • Rate limiting              │  │
│  │ • Kind 1: Public notes  │  │                              │  │
│  └─────────────────────────┘  └──────────────────────────────┘  │
│                                                                  │
│  ConsensusKing pubkey: e045d7a630c11ec5...                      │
│  Proof DB: 139 proofs, 330 Q&A pairs, 52 chains                │
└─────────────────────────────────────────────────────────────────┘
```

## Synthesis.md Theme Alignment

| Theme | BlindOracle Implementation |
|-------|---------------------------|
| **Agents that pay** | x402 gateway (HTTP 402 micropayments), Fedimint eCash (blind-signed), multi-rail fee routing |
| **Agents that trust** | 3-layer trust stack: Nostr proofs + AgentRegistry.sol + per-agent HMAC identity. 17 agents scored, 7 platinum |
| **Agents that cooperate** | A2A protocol (JSON-RPC 2.0), 11 discoverable skills, UnifiedPredictionSubscription.sol for enforceable agreements |
| **Agents that keep secrets** | AES-256-GCM encrypted Nostr proofs (Kind 30099), PrivateClaimVerifier.sol commit-reveal, blind-signed eCash |

## Contract Addresses (Base Mainnet)

| Contract | Address | Verified |
|----------|---------|----------|
| PrivateClaimVerifier | `0x1CF258fA07a620fE86166150fd8619afAD1c9a3D` | Yes |
| UnifiedPredictionSubscription | `0x0d5a467af8bB3968fAc4302Bb6851276EA56880c` | Yes |

## Key Production Artifacts

- **25 running agents** across 8 specialized teams
- **19 agents** with independent Nostr keypairs and SQLite identity DBs
- **17 agents** with on-chain reputation scores (avg 90.0, 7 platinum)
- **139 proofs** in Proof DB with 330 Q&A pairs
- **x402 gateway** live on port 8402
- **CaMel security** live on port 8403
- **A2A server** with 10 JSON-RPC methods
- **Fedimint eCash** integration for private settlement
