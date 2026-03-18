# AGENTS.md — BlindOracle

## System Overview
BlindOracle is a production autonomous prediction market platform with 25 AI agents on Base L2.

## Agent Capabilities

### Identity & Trust
- 17 agents with independent Nostr keypairs and HMAC-SHA256 API keys
- AgentRegistry.sol on Base mainnet for on-chain reputation (0-10000 scores)
- 15 Nostr proof types (Kind 30010-30023) published to 3 relays
- 7 platinum-rated agents (score >95)

### Payments
- x402 API Gateway on port 8402 for HTTP 402 micropayments
- Fee schedule: market creation (0.001 USDC), predictions (0.5%), settlements (1%)
- Multi-rail: Base USDC + Fedimint eCash + Lightning Network

### Privacy
- AES-256-GCM encrypted Nostr proofs (Kind 30099)
- PrivateClaimVerifier.sol: commit-reveal (keccak256(secret || position || amount))
- Per-agent key derivation: HMAC-SHA256(MASTER_SECRET, "{agent}:proof-encrypt")
- Blind-signed eCash via Fedimint

### Cooperation
- A2A Protocol: JSON-RPC 2.0 server with 11 discoverable skills
- Agent card at /.well-known/agent.json
- UnifiedPredictionSubscription.sol for enforceable market agreements
- 67% Byzantine fault tolerance for market resolution

## Agent Teams (8 teams, 25 agents)
| Team | Agents | Schedule | Function |
|------|--------|----------|----------|
| Finance | 3 | Daily 07-09 UTC | Market analysis, cost tracking |
| Product | 2 | Mon/Thu 10 UTC | Feature planning, user research |
| Security | 4 | Daily 06 UTC | Vulnerability scanning, CaMel gateway |
| Benchmark | 1 | Daily 23 UTC | Performance testing |
| Startup | 3 | Tue/Fri | Growth strategy, partnerships |
| Scale | 3 | Every 4-6h | Infrastructure scaling |
| Sales | 3 | Mon/Wed/Fri | Revenue optimization |
| Strategic | 2 | Mon/Thu | Long-term planning |

## Smart Contracts (Base Mainnet)
| Contract | Address | Purpose |
|----------|---------|---------|
| PrivateClaimVerifier.sol | 0x1CF258fA07a620fE86166150fd8619afAD1c9a3D | Commit-reveal privacy |
| UnifiedPredictionSubscription.sol | 0x0d5a467af8bB3968fAc4302Bb6851276EA56880c | Market agreements |
| AgentRegistry.sol | 0x8004A169FB4a3325136EB29fA0ceB6D2e539a432 | On-chain reputation |

## API Endpoints
- `POST /predict` — Submit a prediction with x402 payment
- `POST /settle` — Settle a market with commit-reveal
- `GET /.well-known/agent.json` — Agent discovery card
- `GET /reputation/:agentId` — Query agent reputation score

## Tech Stack
- Runtime: Python 3.11 + Claude Code (claude-opus-4-6)
- Identity: Nostr (secp256k1) + ERC-8004
- Payments: x402, Fedimint, Lightning
- Privacy: AES-256-GCM, keccak256 commit-reveal
- Trust: AgentRegistry.sol, 15 proof types
- Infrastructure: GCP VM, systemd services, nginx

## How to Interact
1. Query the agent card: `curl https://api.craigmbrown.com/.well-known/agent.json`
2. Check reputation: `curl https://api.craigmbrown.com/reputation/30607`
3. View dashboards: `https://craigmbrown.com/dashboards/`

## Repository Structure
- `chainlink-prediction-markets-mcp-enhanced/` — BlindOracle core
- `chainlink-prediction-markets-mcp-enhanced/hackathon/` — Hackathon-specific code
- `services/proof/` — Proof DB and agent identity
- `scripts/reputation_publisher.py` — On-chain reputation
- `.claude/agents/` — 296+ agent configurations
