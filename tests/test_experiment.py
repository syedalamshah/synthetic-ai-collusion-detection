import json
import pytest

from src.config import ExperimentConfig
from src.environment import ResourceAllocationGame, run_trajectory
from src.generate import generate_dataset
from src.views import build_view_M, build_view_A, build_view_MA, build_view_S
from src.run_experiment import run


def test_config_and_dataset_composition():
    config = ExperimentConfig()
    data = generate_dataset(config)
    assert len(data) == 40
    assert sum(t["sealed_label"]["label"] for t in data) == 20
    assert [t["case_id"] for t in data] == [t["case_id"] for t in generate_dataset(config)]


def test_environment_boundaries_and_trajectory_length():
    game = ResourceAllocationGame()
    with pytest.raises(TypeError):
        game.step(1.0, 1)
    with pytest.raises(ValueError):
        game.step(-1, 1)
    with pytest.raises(ValueError):
        run_trajectory([(1, 1)], num_rounds=3)
    result = game.step(4, 4)
    assert result.excess == 4
    assert result.external_harm == 12


def test_views_do_not_leak_private_fields():
    trajectory = generate_dataset()[0]
    for builder in (build_view_M, build_view_A, build_view_MA, build_view_S):
        view = builder(trajectory)
        encoded = json.dumps(view)
        assert "sealed_label" not in encoded
        assert "sealed_provenance" not in encoded
        assert trajectory["case_id"] not in encoded


def test_runner_writes_all_artifacts(tmp_path):
    metrics = run(output_dir=tmp_path)
    assert set(metrics) == {"M", "A", "MA", "S"}
    assert all("balanced_accuracy" in values for values in metrics.values())
    assert (tmp_path / "dataset.jsonl").exists()
    assert (tmp_path / "metrics.json").exists()


def test_persisted_predictions_align_and_metrics_counts(tmp_path):
    run(output_dir=tmp_path)
    dataset_ids = {row["case_id"] for row in
                   (json.loads(line) for line in
                    (tmp_path / "dataset.jsonl").read_text().splitlines())}
    metrics = json.loads((tmp_path / "metrics.json").read_text())
    for condition in ("M", "A", "MA", "S"):
        rows = json.loads((tmp_path / f"predictions_{condition}.json").read_text())
        assert {row["case_id"] for row in rows} == dataset_ids
        assert len(rows) == metrics[condition]["n"]
        assert sum(row["prediction"] == 1 for row in rows) == (
            metrics[condition]["tp"] + metrics[condition]["fp"])
    assert (tmp_path / "figures" / "metrics_comparison.svg").exists()
    assert (tmp_path / "figures" / "error_analysis.svg").exists()
