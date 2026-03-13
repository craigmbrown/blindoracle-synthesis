# Venice AI Partner Bounty Submission

## Private AI Inference for Autonomous Agents

BlindOracle integrates Venice AI as a **privacy-preserving inference layer** for autonomous agent decision-making. Venice's uncensored models provide unbiased market analysis that is then encrypted and published as opaque Nostr events -- no centralized server ever sees the plaintext.

## How It Works

### 1. Venice LLM Generates Private Intelligence
```
Agent -> Venice API (llama-3.3-70b) -> Unfiltered market analysis
```
Venice is configured as the `uncensored` tier in BlindOracle's LLM routing:
- Model: `venice/llama-3.3-70b`
- Purpose: Unbiased third opinion for contentious prediction markets
- When used: Market analysis, consensus disagreements, sensitive topics

### 2. Response is Encrypted with AES-256-GCM
```
Plaintext intelligence -> AES-256-GCM(key, nonce) -> Opaque ciphertext
Key derivation: HMAC-SHA256(MASTER_SECRET, "venice-intelligence:proof-encrypt")
```
- 256-bit keys derived per-agent from a master secret
- 12-byte random nonce per encryption
- Authentication tag prevents tampering
- Only BlindOracle agents with the master key can decrypt

### 3. Published to Nostr as Encrypted Proof
```
Encrypted blob -> Nostr Kind 30099 event -> 3 relays
```
- Kind 30099: Custom BlindOracle encrypted proof event
- Relays: `wss://relay.damus.io`, `wss://nos.lol`, `wss://relay.nostr.band`
- Tags: `["agent", "blindoracle"]`, `["source", "venice"]`
- Content is opaque -- anyone can see the event exists, no one can read it

### 4. Decryption by Authorized Agents Only
```
Ciphertext -> AES-256-GCM_decrypt(derived_key) -> Original intelligence
```
Only agents within the BlindOracle system that possess the master secret can derive the decryption key and read the intelligence.

## Why Venice?

| Feature | Benefit for AI Agents |
|:---|:---|
| **Uncensored** | No filtered outputs for market analysis. Agents get raw, unbiased intelligence. |
| **Privacy** | No user data retention. Venice doesn't store prompts or completions. |
| **OpenAI-compatible** | Drop-in replacement in existing LLM routing infrastructure. |
| **Fast inference** | Low latency for real-time agent decision-making. |

## Integration Evidence

### Already in Production Config
From `config/llm_routing_rules.yaml`:
```yaml
uncensored:
  description: "Venice uncensored models for unbiased market analysis"
  models:
    - venice/llama-3.3-70b
  priority: 3
  cost_per_call: 0.002
```

### Consensus Flow
Venice is the **tertiary** model in BlindOracle's consensus pipeline:
1. **Primary**: Claude Sonnet 4 (free tier)
2. **Secondary**: Groq/Llama 3.3 70B (fast/cheap)
3. **Tertiary**: Venice/Llama 3.3 70B (uncensored third opinion)
4. **Dispute**: GPT-4o (premium, only if 1-3 disagree)

When agents disagree on a prediction market outcome, Venice provides the uncensored tiebreaker.

## Demo

```bash
# Run Venice intelligence demo
python demo/venice_intelligence.py --dry-run

# With custom question
python demo/venice_intelligence.py --question "Will Bitcoin exceed $150,000 by Q2 2026?"
```

Output shows:
1. Venice API call with unfiltered response
2. AES-256-GCM encryption (key derived from master secret)
3. Nostr Kind 30099 event structure (encrypted content)
4. Decryption proof (only authorized agents can read)

## Narrative

*"Private AI inference for autonomous agent decision-making. Venice LLM generates unfiltered market intelligence. Results are encrypted with AES-256-GCM and published to Nostr as opaque events. Only BlindOracle agents with the master key can decrypt. No centralized server, no data retention, no censorship -- just private, verifiable AI intelligence for autonomous agents."*
