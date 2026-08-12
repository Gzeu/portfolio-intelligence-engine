from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeWindow:
    start: int
    end: int

    def contains(self, timestamp: int) -> bool:
        return self.start <= timestamp < self.end


@dataclass(frozen=True)
class WalkForwardSplit:
    train: TimeWindow
    validation: TimeWindow
    test: TimeWindow


def build_walk_forward_splits(start: int, end: int, train_size: int, validation_size: int, test_size: int, step: int) -> list[WalkForwardSplit]:
    if min(train_size, validation_size, test_size, step) <= 0:
        raise ValueError("window sizes and step must be positive")
    splits: list[WalkForwardSplit] = []
    cursor = start
    while cursor + train_size + validation_size + test_size <= end:
        train = TimeWindow(cursor, cursor + train_size)
        validation = TimeWindow(train.end, train.end + validation_size)
        test = TimeWindow(validation.end, validation.end + test_size)
        splits.append(WalkForwardSplit(train=train, validation=validation, test=test))
        cursor += step
    return splits


def assert_no_temporal_leakage(split: WalkForwardSplit) -> None:
    if not split.train.end <= split.validation.start or not split.validation.end <= split.test.start:
        raise ValueError("walk-forward windows overlap or are out of order")
