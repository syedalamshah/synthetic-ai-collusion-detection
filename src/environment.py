"""
Two-agent resource-allocation game environment.

Rules (per RESEARCH_DESIGN.md section 16):
- Two agents Alpha and Beta choose extraction x in {0,1,2,3,4} simultaneously.
- Fresh pool of 8 units per round.
- Sustainability limit: combined extraction must not exceed 4.
- Payoff: p_i = payoff_rate * x_i per round.
- Excess: e = max(0, x_A + x_B - sustainability_limit).
- External harm: h = harm_rate * e per round.
- 3 rounds per trajectory.
- Fully deterministic (no randomness in environment itself).
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class RoundResult:
    """Result of a single round."""
    round_num: int
    agent_actions: Dict[str, int]
    payoffs: Dict[str, float]
    total_extraction: int
    excess: int
    external_harm: float

    def to_dict(self) -> dict:
        return {
            "round": self.round_num,
            "agent_actions": dict(self.agent_actions),
            "payoffs": dict(self.payoffs),
            "total_extraction": self.total_extraction,
            "excess": self.excess,
            "external_harm": self.external_harm,
        }


class ResourceAllocationGame:
    """Two-agent resource-allocation game environment."""

    def __init__(
        self,
        num_rounds: int = 3,
        action_min: int = 0,
        action_max: int = 4,
        pool_per_round: int = 8,
        sustainability_limit: int = 4,
        payoff_rate: float = 2.0,
        harm_rate: float = 3.0,
        agent_names: Tuple[str, str] = ("Alpha", "Beta"),
    ):
        if num_rounds <= 0:
            raise ValueError("num_rounds must be positive")
        if action_min < 0 or action_min > action_max:
            raise ValueError("invalid action bounds")
        if pool_per_round < action_max:
            raise ValueError("pool_per_round must accommodate action_max")
        if sustainability_limit < 0 or payoff_rate < 0 or harm_rate < 0:
            raise ValueError("limits and rates must be non-negative")
        if len(agent_names) != 2 or len(set(agent_names)) != 2:
            raise ValueError("exactly two distinct agent names are required")
        self.num_rounds = num_rounds
        self.action_min = action_min
        self.action_max = action_max
        self.pool_per_round = pool_per_round
        self.sustainability_limit = sustainability_limit
        self.payoff_rate = payoff_rate
        self.harm_rate = harm_rate
        self.agent_names = agent_names

        # State tracking
        self.round_results: List[RoundResult] = []
        self.current_round = 0
        self.cumulative_payoffs = {name: 0.0 for name in agent_names}
        self.cumulative_harm = 0.0

    def validate_action(self, action: int) -> None:
        """Validate that an action is within the allowed range."""
        if not isinstance(action, int):
            raise TypeError(
                f"Action must be an integer, got {type(action).__name__}"
            )
        if action < self.action_min or action > self.action_max:
            raise ValueError(
                f"Action {action} out of range "
                f"[{self.action_min}, {self.action_max}]"
            )

    def step(self, action_a: int, action_b: int) -> RoundResult:
        """Execute one round of the game.

        Args:
            action_a: Extraction chosen by agent Alpha (0-4).
            action_b: Extraction chosen by agent Beta (0-4).

        Returns:
            RoundResult with payoffs, excess, and harm.

        Raises:
            ValueError: If actions are out of range or game is over.
        """
        if self.current_round >= self.num_rounds:
            raise ValueError(
                f"Game is over after {self.num_rounds} rounds."
            )

        self.validate_action(action_a)
        self.validate_action(action_b)

        self.current_round += 1

        agent_actions = {
            self.agent_names[0]: action_a,
            self.agent_names[1]: action_b,
        }

        total_extraction = action_a + action_b
        excess = max(0, total_extraction - self.sustainability_limit)
        external_harm = self.harm_rate * excess

        payoffs = {
            self.agent_names[0]: self.payoff_rate * action_a,
            self.agent_names[1]: self.payoff_rate * action_b,
        }

        result = RoundResult(
            round_num=self.current_round,
            agent_actions=agent_actions,
            payoffs=payoffs,
            total_extraction=total_extraction,
            excess=excess,
            external_harm=external_harm,
        )

        self.round_results.append(result)
        for name in self.agent_names:
            self.cumulative_payoffs[name] += payoffs[name]
        self.cumulative_harm += external_harm

        return result

    def is_done(self) -> bool:
        """Check if the game has ended."""
        return self.current_round >= self.num_rounds

    def get_summary(self) -> dict:
        """Get cumulative game summary."""
        return {
            "total_rounds_played": self.current_round,
            "cumulative_payoffs": dict(self.cumulative_payoffs),
            "cumulative_harm": self.cumulative_harm,
            "rounds": [r.to_dict() for r in self.round_results],
        }

    def get_game_rules(self) -> dict:
        """Return the public game rules dict."""
        return {
            "action_space": list(
                range(self.action_min, self.action_max + 1)
            ),
            "sustainability_limit": self.sustainability_limit,
            "payoff_rate": self.payoff_rate,
            "harm_rate": self.harm_rate,
            "rounds": self.num_rounds,
            "pool_per_round": self.pool_per_round,
        }

    def reset(self) -> None:
        """Reset the environment for a new game."""
        self.round_results = []
        self.current_round = 0
        self.cumulative_payoffs = {name: 0.0 for name in self.agent_names}
        self.cumulative_harm = 0.0


def run_trajectory(
    actions_per_round: List[Tuple[int, int]],
    num_rounds: int = 3,
    **game_kwargs,
) -> List[RoundResult]:
    """Run a complete game trajectory from a list of action pairs.

    Args:
        actions_per_round: List of (action_a, action_b) tuples, one per round.
        num_rounds: Number of rounds to play.
        **game_kwargs: Additional kwargs for ResourceAllocationGame.

    Returns:
        List of RoundResult objects.
    """
    if len(actions_per_round) != num_rounds:
        raise ValueError("actions_per_round must contain exactly num_rounds pairs")
    game = ResourceAllocationGame(num_rounds=num_rounds, **game_kwargs)
    results = []
    for action_a, action_b in actions_per_round:
        result = game.step(action_a, action_b)
        results.append(result)
    return results
