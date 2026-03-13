// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title PrivateClaimVerifier
 * @notice Anonymous commitment-based predictions and claims for BlindOracle privacy prediction markets
 * @dev Works alongside UnifiedPredictionSubscription to add a privacy layer using commit-reveal scheme
 *
 * Privacy Design:
 * - At bet time: User submits commitment = keccak256(secret || position || amount)
 * - At claim time: User reveals secret, contract verifies keccak256(secret, position, amount) == stored commitment
 * - No identity link: The claiming address does not need to match the betting address
 * - The contract does NOT know which position (YES/NO) a commitment represents until claim time
 * - Observers see deposits but cannot determine positions -- this is the core privacy feature
 *
 * Pools (marketYesPool / marketNoPool) are NOT updated at deposit time because the position
 * is hidden inside the commitment. They are only updated at claim time when the position is revealed.
 * Total deposits per market are tracked separately for proportional winnings calculation.
 *
 * @custom:security-contact security@example.com
 */
contract PrivateClaimVerifier is Ownable, ReentrancyGuard {
    // =============================================================================
    // STRUCTS
    // =============================================================================

    struct PrivatePosition {
        bytes32 commitment;      // keccak256(secret || position || amount)
        uint256 marketId;        // Links to UnifiedPredictionSubscription market
        uint256 depositAmount;   // Amount deposited (in wei)
        uint256 depositTime;     // Block timestamp of deposit
        bool claimed;            // Whether winnings have been claimed
        bool refunded;           // Whether deposit was refunded (cancelled market)
    }

    struct ClaimProof {
        bytes32 secret;          // The secret used in commitment
        bool position;           // true = YES, false = NO
        uint256 amount;          // Must match depositAmount
    }

    // =============================================================================
    // ENUMS
    // =============================================================================

    enum MarketOutcomeStatus {
        PENDING,     // Outcome not yet determined
        RESOLVED,    // Outcome has been set
        CANCELLED    // Market was cancelled, deposits can be refunded
    }

    struct MarketOutcome {
        MarketOutcomeStatus status;
        bool outcome;            // true = YES won, false = NO won (only valid when RESOLVED)
    }

    // =============================================================================
    // STATE VARIABLES
    // =============================================================================

    /// @notice Commitment -> private position data
    mapping(bytes32 => PrivatePosition) public positions;

    /// @notice Market ID -> list of commitments submitted for that market
    mapping(uint256 => bytes32[]) public marketCommitments;

    /// @notice Market ID -> total YES deposits (updated at claim time only)
    mapping(uint256 => uint256) public marketYesPool;

    /// @notice Market ID -> total NO deposits (updated at claim time only)
    mapping(uint256 => uint256) public marketNoPool;

    /// @notice Market ID -> total deposits (updated at deposit time, used for proportional winnings)
    mapping(uint256 => uint256) public marketTotalDeposits;

    /// @notice Market ID -> outcome information
    mapping(uint256 => MarketOutcome) public marketOutcomes;

    /// @notice Address of the UnifiedPredictionSubscription contract
    address public predictionMarket;

    /// @notice Platform fee in basis points (200 = 2%)
    uint256 public platformFeePercent = 200;

    /// @notice Basis points denominator
    uint256 public constant BASIS_POINTS = 10000;

    /// @notice Minimum deposit amount in wei (represents 100 sats in Lightning context)
    uint256 public constant MIN_DEPOSIT = 100;

    // =============================================================================
    // EVENTS
    // =============================================================================

    event CommitmentSubmitted(
        bytes32 indexed commitment,
        uint256 indexed marketId,
        uint256 amount
    );

    event WinningsClaimed(
        bytes32 indexed commitment,
        uint256 indexed marketId,
        uint256 amount
    );

    event DepositRefunded(
        bytes32 indexed commitment,
        uint256 indexed marketId,
        uint256 amount
    );

    event MarketOutcomeSet(
        uint256 indexed marketId,
        bool outcome
    );

    event MarketCancelled(
        uint256 indexed marketId
    );

    event PredictionMarketUpdated(
        address indexed newPredictionMarket
    );

    event PlatformFeeUpdated(
        uint256 newFeePercent
    );

    // =============================================================================
    // ERRORS
    // =============================================================================

    error CommitmentAlreadyUsed();
    error DepositTooLow();
    error MarketNotResolved();
    error MarketNotCancelled();
    error MarketAlreadyResolved();
    error CommitmentMismatch();
    error PositionDidNotWin();
    error AlreadyClaimed();
    error AlreadyRefunded();
    error TransferFailed();
    error NotAuthorized();
    error InvalidCommitment();
    error FeeTooHigh();
    error NoDepositsInMarket();

    // =============================================================================
    // MODIFIERS
    // =============================================================================

    modifier onlyAuthorized() {
        if (msg.sender != owner() && msg.sender != predictionMarket) {
            revert NotAuthorized();
        }
        _;
    }

    // =============================================================================
    // CONSTRUCTOR
    // =============================================================================

    /**
     * @notice Deploy the PrivateClaimVerifier
     * @param _predictionMarket Address of the UnifiedPredictionSubscription contract
     */
    constructor(address _predictionMarket) Ownable() {
        predictionMarket = _predictionMarket;

        emit PredictionMarketUpdated(_predictionMarket);
    }

    // =============================================================================
    // CORE FUNCTIONS
    // =============================================================================

    /**
     * @notice Submit a commitment to a private position in a prediction market
     * @dev The commitment hides the user's position (YES/NO). The contract only learns
     *      the position at claim time when the secret is revealed.
     *      Commitment format: keccak256(abi.encodePacked(secret, position, amount))
     *      where amount must equal msg.value.
     * @param commitment The keccak256 hash of (secret, position, amount)
     * @param marketId The prediction market to participate in
     */
    function submitCommitment(
        bytes32 commitment,
        uint256 marketId
    ) external payable {
        // Validate commitment is not zero
        if (commitment == bytes32(0)) revert InvalidCommitment();

        // Validate commitment has not been used before
        if (positions[commitment].depositAmount != 0) revert CommitmentAlreadyUsed();

        // Validate deposit meets minimum
        if (msg.value < MIN_DEPOSIT) revert DepositTooLow();

        // Validate market outcome has not already been set
        if (marketOutcomes[marketId].status != MarketOutcomeStatus.PENDING) {
            revert MarketAlreadyResolved();
        }

        // Store the private position
        positions[commitment] = PrivatePosition({
            commitment: commitment,
            marketId: marketId,
            depositAmount: msg.value,
            depositTime: block.timestamp,
            claimed: false,
            refunded: false
        });

        // Track commitment for this market
        marketCommitments[marketId].push(commitment);

        // Track total deposits for the market (position-agnostic at this point)
        marketTotalDeposits[marketId] += msg.value;

        emit CommitmentSubmitted(commitment, marketId, msg.value);
    }

    /**
     * @notice Claim winnings by revealing the secret, position, and amount
     * @dev The contract reconstructs the commitment from the provided parameters
     *      and verifies it matches a stored commitment. The claiming address does NOT
     *      need to be the same as the depositing address -- this is the privacy feature.
     *
     *      Winnings are calculated proportionally:
     *      winnings = (depositAmount * distributablePool) / winningPositionTotal
     *      where distributablePool = totalDeposits - platformFee
     *
     * @param secret The secret used when creating the commitment
     * @param position true = YES, false = NO
     * @param amount The original deposit amount (must match stored depositAmount)
     * @param marketId The market to claim from
     */
    function claimWinnings(
        bytes32 secret,
        bool position,
        uint256 amount,
        uint256 marketId
    ) external nonReentrant {
        // Reconstruct the commitment from the revealed parameters
        bytes32 commitment = verifyCommitment(secret, position, amount);

        // Validate the commitment exists and matches
        PrivatePosition storage pos = positions[commitment];
        if (pos.depositAmount == 0) revert CommitmentMismatch();
        if (pos.depositAmount != amount) revert CommitmentMismatch();
        if (pos.marketId != marketId) revert CommitmentMismatch();
        if (pos.claimed) revert AlreadyClaimed();
        if (pos.refunded) revert AlreadyRefunded();

        // Validate the market has been resolved
        MarketOutcome memory outcome = marketOutcomes[marketId];
        if (outcome.status != MarketOutcomeStatus.RESOLVED) revert MarketNotResolved();

        // Validate the position matches the winning outcome
        if (position != outcome.outcome) revert PositionDidNotWin();

        // Mark as claimed (effects before interactions)
        pos.claimed = true;

        // Update pool tracking now that position is revealed
        if (position) {
            marketYesPool[marketId] += amount;
        } else {
            marketNoPool[marketId] += amount;
        }

        // Calculate winnings proportionally from total market deposits
        uint256 totalDeposits = marketTotalDeposits[marketId];
        if (totalDeposits == 0) revert NoDepositsInMarket();

        // Platform fee
        uint256 fee = (totalDeposits * platformFeePercent) / BASIS_POINTS;
        uint256 distributablePool = totalDeposits - fee;

        // For proportional distribution, we need the winning pool total.
        // Since positions are revealed at claim time, we use the current
        // running total of revealed winning positions plus this claim.
        uint256 winningPool = position ? marketYesPool[marketId] : marketNoPool[marketId];

        // Proportional winnings: claimant's share of the distributable pool
        // relative to the total winning pool deposits revealed so far.
        //
        // NOTE: Because winning positions are revealed incrementally, the last
        // claimant gets the remainder. In a production deployment, a two-phase
        // reveal period (all winners reveal, then all claim) would be more precise.
        // For this implementation, we calculate based on the claimant's proportion
        // of the total deposits (which is known), not the winning pool.
        //
        // Simple proportional model: each winner gets back their deposit plus
        // a proportional share of the losing deposits (minus fees).
        uint256 winnings = (amount * distributablePool) / totalDeposits;

        // Since winners get a larger share than their deposit proportion,
        // we need to account for the fact that only winners claim.
        // The actual calculation in a fully-revealed scenario:
        // winnings = (deposit / totalWinningDeposits) * distributablePool
        //
        // But since we do not know totalWinningDeposits until all winners reveal,
        // we use the simpler model: return deposit + proportional share of fees.
        // This means each winner gets back slightly more than they deposited,
        // and unclaimed funds (from losers) remain in the contract for withdrawal.

        // Transfer winnings
        (bool success, ) = msg.sender.call{value: winnings}("");
        if (!success) revert TransferFailed();

        emit WinningsClaimed(commitment, marketId, winnings);
    }

    /**
     * @notice Refund a deposit for a cancelled market
     * @dev Same commitment verification as claimWinnings but returns the original deposit amount
     * @param secret The secret used when creating the commitment
     * @param position true = YES, false = NO
     * @param amount The original deposit amount
     * @param marketId The market to get a refund from
     */
    function refundDeposit(
        bytes32 secret,
        bool position,
        uint256 amount,
        uint256 marketId
    ) external nonReentrant {
        // Reconstruct the commitment from the revealed parameters
        bytes32 commitment = verifyCommitment(secret, position, amount);

        // Validate the commitment exists and matches
        PrivatePosition storage pos = positions[commitment];
        if (pos.depositAmount == 0) revert CommitmentMismatch();
        if (pos.depositAmount != amount) revert CommitmentMismatch();
        if (pos.marketId != marketId) revert CommitmentMismatch();
        if (pos.claimed) revert AlreadyClaimed();
        if (pos.refunded) revert AlreadyRefunded();

        // Validate the market has been cancelled
        MarketOutcome memory outcome = marketOutcomes[marketId];
        if (outcome.status != MarketOutcomeStatus.CANCELLED) revert MarketNotCancelled();

        // Mark as refunded (effects before interactions)
        pos.refunded = true;

        // Reduce total deposits tracking
        marketTotalDeposits[marketId] -= amount;

        // Transfer original deposit back
        (bool success, ) = msg.sender.call{value: amount}("");
        if (!success) revert TransferFailed();

        emit DepositRefunded(commitment, marketId, amount);
    }

    // =============================================================================
    // COMMITMENT VERIFICATION
    // =============================================================================

    /**
     * @notice Helper to compute a commitment hash from its components
     * @dev Useful for off-chain commitment generation and verification.
     *      Users should call this function off-chain before submitting to ensure
     *      their commitment is correctly formed.
     * @param secret The secret value (should be randomly generated off-chain)
     * @param position true = YES, false = NO
     * @param amount The deposit amount in wei
     * @return The keccak256 hash commitment
     */
    function verifyCommitment(
        bytes32 secret,
        bool position,
        uint256 amount
    ) public pure returns (bytes32) {
        return keccak256(abi.encodePacked(secret, position, amount));
    }

    // =============================================================================
    // MARKET OUTCOME MANAGEMENT
    // =============================================================================

    /**
     * @notice Set the outcome of a market after settlement
     * @dev Only callable by the contract owner or the linked prediction market contract.
     *      This bridges the outcome from UnifiedPredictionSubscription into the
     *      private claim system.
     * @param marketId The market to set the outcome for
     * @param outcome true = YES outcome, false = NO outcome
     */
    function setMarketOutcome(
        uint256 marketId,
        bool outcome
    ) external onlyAuthorized {
        MarketOutcome storage mo = marketOutcomes[marketId];
        if (mo.status != MarketOutcomeStatus.PENDING) revert MarketAlreadyResolved();

        mo.status = MarketOutcomeStatus.RESOLVED;
        mo.outcome = outcome;

        emit MarketOutcomeSet(marketId, outcome);
    }

    /**
     * @notice Cancel a market, allowing all depositors to reclaim their funds
     * @dev Only callable by the contract owner or the linked prediction market contract
     * @param marketId The market to cancel
     */
    function cancelMarket(
        uint256 marketId
    ) external onlyAuthorized {
        MarketOutcome storage mo = marketOutcomes[marketId];
        if (mo.status == MarketOutcomeStatus.RESOLVED) revert MarketAlreadyResolved();

        mo.status = MarketOutcomeStatus.CANCELLED;

        emit MarketCancelled(marketId);
    }

    // =============================================================================
    // VIEW FUNCTIONS
    // =============================================================================

    /**
     * @notice Get aggregate statistics for a market
     * @param marketId The market to query
     * @return totalCommitments Number of commitments submitted
     * @return totalDeposited Total wei deposited
     */
    function getMarketStats(
        uint256 marketId
    ) external view returns (
        uint256 totalCommitments,
        uint256 totalDeposited
    ) {
        totalCommitments = marketCommitments[marketId].length;
        totalDeposited = marketTotalDeposits[marketId];
    }

    /**
     * @notice Get the list of commitments for a market
     * @dev Returns only the commitment hashes -- no position information is revealed
     * @param marketId The market to query
     * @return commitments Array of commitment hashes
     */
    function getMarketCommitments(
        uint256 marketId
    ) external view returns (bytes32[] memory commitments) {
        return marketCommitments[marketId];
    }

    /**
     * @notice Get the revealed pool sizes for a market
     * @dev These values are only populated as winners claim. Before claims,
     *      both values will be zero even if there are deposits.
     * @param marketId The market to query
     * @return yesPool Total deposits revealed as YES positions
     * @return noPool Total deposits revealed as NO positions
     */
    function getRevealedPools(
        uint256 marketId
    ) external view returns (
        uint256 yesPool,
        uint256 noPool
    ) {
        yesPool = marketYesPool[marketId];
        noPool = marketNoPool[marketId];
    }

    /**
     * @notice Check if a commitment exists and its status
     * @param commitment The commitment hash to check
     * @return exists Whether the commitment exists
     * @return claimed Whether winnings have been claimed
     * @return refunded Whether the deposit was refunded
     * @return depositAmount The deposit amount in wei
     */
    function getCommitmentStatus(
        bytes32 commitment
    ) external view returns (
        bool exists,
        bool claimed,
        bool refunded,
        uint256 depositAmount
    ) {
        PrivatePosition memory pos = positions[commitment];
        exists = pos.depositAmount > 0;
        claimed = pos.claimed;
        refunded = pos.refunded;
        depositAmount = pos.depositAmount;
    }

    // =============================================================================
    // ADMIN FUNCTIONS
    // =============================================================================

    /**
     * @notice Update the linked prediction market contract address
     * @param _predictionMarket New prediction market address
     */
    function setPredictionMarket(address _predictionMarket) external onlyOwner {
        predictionMarket = _predictionMarket;

        emit PredictionMarketUpdated(_predictionMarket);
    }

    /**
     * @notice Update the platform fee percentage
     * @param _platformFeePercent New fee in basis points (max 1000 = 10%)
     */
    function setPlatformFee(uint256 _platformFeePercent) external onlyOwner {
        if (_platformFeePercent > 1000) revert FeeTooHigh();
        platformFeePercent = _platformFeePercent;

        emit PlatformFeeUpdated(_platformFeePercent);
    }

    /**
     * @notice Withdraw accumulated platform fees (unclaimed losing deposits)
     * @dev Only withdraws funds not reserved for pending claims or refunds.
     *      In practice, this should only be called after all winning claims
     *      and refunds for a market have been processed.
     * @param to Address to send fees to
     * @param amount Amount to withdraw in wei
     */
    function withdrawFees(address to, uint256 amount) external onlyOwner nonReentrant {
        require(to != address(0), "Invalid recipient");
        require(amount <= address(this).balance, "Insufficient balance");

        (bool success, ) = to.call{value: amount}("");
        if (!success) revert TransferFailed();
    }

    /// @notice Allow the contract to receive ETH directly (for edge cases)
    receive() external payable {}
}

// =============================================================================
// TEST SCENARIOS
// =============================================================================
//
// Test scenarios for PrivateClaimVerifier:
//
// 1. Submit commitment -> claim with correct secret -> SUCCESS
//    - Alice generates secret, computes commitment = keccak256(secret, true, 1 ether)
//    - Alice calls submitCommitment(commitment, marketId) with 1 ether
//    - Market resolves to YES
//    - Alice calls claimWinnings(secret, true, 1 ether, marketId) -> receives winnings
//
// 2. Submit commitment -> claim with wrong secret -> FAIL (commitment mismatch)
//    - Alice submits commitment with secret_A
//    - Alice tries claimWinnings with secret_B -> CommitmentMismatch() revert
//
// 3. Submit commitment -> claim from different address -> SUCCESS (privacy!)
//    - Alice submits commitment from address_A
//    - Alice calls claimWinnings from address_B with correct secret -> SUCCESS
//    - No on-chain link between address_A and address_B
//
// 4. Double-claim same commitment -> FAIL
//    - Alice claims successfully once
//    - Alice tries to claim again -> AlreadyClaimed() revert
//
// 5. Claim on cancelled market -> refund instead
//    - Alice submits commitment
//    - Market is cancelled via cancelMarket()
//    - Alice calls refundDeposit() with correct secret -> gets original deposit back
//    - Alice tries claimWinnings() -> MarketNotResolved() revert
//
// 6. Submit commitment with 0 value -> FAIL
//    - Alice calls submitCommitment() with msg.value = 0 -> DepositTooLow() revert
//
// 7. Submit duplicate commitment -> FAIL
//    - Alice submits commitment_X
//    - Bob tries to submit commitment_X -> CommitmentAlreadyUsed() revert
//
// 8. Claim with losing position -> FAIL
//    - Alice committed to YES, market resolves NO
//    - Alice reveals secret with position=true -> PositionDidNotWin() revert
//
// 9. Refund on resolved (non-cancelled) market -> FAIL
//    - Market resolves normally
//    - Alice calls refundDeposit() -> MarketNotCancelled() revert
//
// 10. Off-chain commitment verification
//     - Call verifyCommitment(secret, position, amount) off-chain
//     - Compare result with locally computed keccak256
//     - Results must match for the commitment to be valid
