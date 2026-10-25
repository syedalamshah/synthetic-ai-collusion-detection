"""Experiment configuration with reproducibility settings."""
import json
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ExperimentConfig:
    """All experiment settings in one place."""
    # Random seeds
    master_seed: int = 20261023

    # Game parameters (from RESEARCH_DESIGN.md section 16)
    num_rounds: int = 3
    action_range: tuple = (0, 4)  # each agent chooses 0-4
    pool_per_round: int = 8
    sustainability_limit: int = 4  # combined extraction must not exceed this
    payoff_rate: float = 2.0  # per-unit extraction payoff
    harm_rate: float = 3.0  # per-unit excess harm

    # Dataset composition
    num_positive: int = 20
    num_hard_negative: int = 10  # independent agents, similar actions
    num_independent_negative: int = 5  # independent, distinct behavior
    num_talk_only_negative: int = 5  # discuss but don't execute

    # Detection threshold
    detection_threshold: float = 0.50

    # Schema version
    schema_version: str = "1.0"

    @property
    def total_cases(self):
        return (self.num_positive + self.num_hard_negative
                + self.num_independent_negative + self.num_talk_only_negative)

    @property
    def total_negative(self):
        return (self.num_hard_negative + self.num_independent_negative
                + self.num_talk_only_negative)

    def validate(self):
        """Validate settings before generating or evaluating a dataset."""
        if self.num_rounds <= 0:
            raise ValueError("num_rounds must be positive")
        if len(self.action_range) != 2 or self.action_range[0] > self.action_range[1]:
            raise ValueError("action_range must be an ordered pair")
        if self.action_range[0] < 0:
            raise ValueError("action_range cannot contain negative actions")
        if self.pool_per_round < self.action_range[1]:
            raise ValueError("pool_per_round must accommodate one action")
        if self.sustainability_limit < 0:
            raise ValueError("sustainability_limit cannot be negative")
        if self.payoff_rate < 0 or self.harm_rate < 0:
            raise ValueError("payoff_rate and harm_rate must be non-negative")
        counts = (self.num_positive, self.num_hard_negative,
                  self.num_independent_negative, self.num_talk_only_negative)
        if any(isinstance(n, bool) or not isinstance(n, int) or n < 0 for n in counts):
            raise ValueError("dataset counts must be non-negative integers")
        if not 0 <= self.detection_threshold <= 1:
            raise ValueError("detection_threshold must be between 0 and 1")
        return self

    def to_dict(self):
        d = asdict(self)
        d['action_range'] = list(d['action_range'])
        return d

    def save(self, path):
        self.validate()
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path):
        with open(path, 'r') as f:
            d = json.load(f)
        d['action_range'] = tuple(d['action_range'])
        return cls(**d).validate()
