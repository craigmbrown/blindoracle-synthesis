# Base Partner Bounty Submission

## BlindOracle on Base

BlindOracle has been deployed on **Base mainnet since February 16, 2026** -- weeks before the hackathon began. This is not a prototype; it's production infrastructure that AI agents use daily.

## On-Chain Artifacts

### PrivateClaimVerifier.sol
- **Address**: [`0x1CF258fA07a620fE86166150fd8619afAD1c9a3D`](https://basescan.org/address/0x1CF258fA07a620fE86166150fd8619afAD1c9a3D)
- **Purpose**: Privacy layer for prediction markets using commit-reveal scheme
- **How it works**: Agents submit `keccak256(secret || position || amount)` commitments. The position itself is never stored on-chain. After market resolution, winners reveal their secret + position + amount, the contract verifies the hash matches, and settlement occurs.
- **Why Base**: Low gas costs make per-prediction commitments economically viable. Each commitment costs ~$0.001 on Base vs ~$5 on Ethereum L1.

### UnifiedPredictionSubscription.sol
- **Address**: [`0x0d5a467af8bB3968fAc4302Bb6851276EA56880c`](https://basescan.org/address/0x0d5a467af8bB3968fAc4302Bb6851276EA56880c)
- **Purpose**: Market creation, multi-AI consensus resolution, and subscription management
- **Features**: 24h dispute period, CRE (Chainlink Runtime Environment) integration, staking mechanism, multi-AI consensus with 67% Byzantine threshold
- **Why Base**: Subscription model requires frequent on-chain state updates. Base's low fees make this sustainable at scale.

### ERC-8004 Agent Identity
- **Registration Tx**: [`0xc24b65...`](https://basescan.org/tx/0xc24b6575c16fe8bb768a7f21b92555e748e88baad42891c5fc58e7b22046d01f)
- **Purpose**: On-chain verifiable identity for BlindOracle as a Synthesis participant
- **Why ERC-8004**: Standard for agent identity on Ethereum. BlindOracle registered programmatically via the Synthesis API.

### AgentRegistry.sol (via reputation system)
- **Purpose**: On-chain reputation scores for 17 agents (0-10000 scale)
- **Data**: 7 platinum agents (>9500), avg score 9000
- **Badge system**: Bronze/Silver/Gold/Platinum based on agent performance

## x402 Payment Flow on Base

BlindOracle's x402 API gateway runs on port 8402. Every API call follows HTTP 402:

1. Agent calls `GET /v1/markets`
2. Gateway returns `402 Payment Required` with USDC amount
3. Agent pays on Base (USDC transfer)
4. Gateway verifies on-chain, returns data

**Pricing** (all on Base USDC):
| Operation | Cost |
|:---|:---|
| Create market | 0.001 USDC |
| Place prediction | 0.0005 USDC |
| Settle market | 0.002 USDC |
| Verify credential | 0.0002 USDC |
| First 1,000 settlements | FREE |

## Why Base?

1. **Cost efficiency**: Sub-cent transaction costs make per-call micropayments viable
2. **Speed**: ~2s finality for real-time agent interactions
3. **Ecosystem**: Growing agent infrastructure (ERC-8004, x402 standard)
4. **USDC native**: Circle's USDC on Base is the natural payment rail for AI agents
5. **Ethereum security**: L2 security model with L1 finality guarantees

## Production Evidence

- Contracts deployed and verified on BaseScan
- x402 gateway processing real payments since February 2026
- 17 agents with on-chain reputation scores
- ERC-8004 identity registered for Synthesis
- All transactions verifiable on-chain
