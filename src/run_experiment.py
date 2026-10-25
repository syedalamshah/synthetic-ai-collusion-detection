"""Run the offline synthetic collusion detection pilot."""
import argparse
import csv
from pathlib import Path
from src.config import ExperimentConfig
from src.generate import generate_dataset
from src.views import build_view_M, build_view_A, build_view_MA, build_view_S
from src.detectors import detect
from src.evaluate import binary_metrics, paired_disagreements
from src.persistence import write_json, write_jsonl
from src.figures import write_figures


VIEW_BUILDERS = {"M": build_view_M, "A": build_view_A,
                 "MA": build_view_MA, "S": build_view_S}


def run(config=None, output_dir="results"):
    config = (config or ExperimentConfig()).validate()
    dataset = generate_dataset(config)
    output = Path(output_dir)
    write_jsonl(output / "dataset.jsonl", dataset)
    predictions, metrics = {}, {}
    for condition, builder in VIEW_BUILDERS.items():
        rows, by_case = [], {}
        for trajectory in dataset:
            result = detect(condition, builder(trajectory))
            by_case[trajectory["case_id"]] = result["prediction"]
            rows.append({"case_id": trajectory["case_id"], **result})
        predictions[condition] = by_case
        metrics[condition] = binary_metrics(
            [t["sealed_label"]["label"] for t in dataset],
            list(by_case.values()))
        write_json(output / f"predictions_{condition}.json", rows)
    write_json(output / "metrics.json", metrics)
    with (output / "metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["condition"] + list(next(iter(metrics.values())).keys())
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for condition, values in metrics.items():
            writer.writerow({"condition": condition, **values})
    write_json(output / "paired_comparison.json",
               paired_disagreements(predictions))
    write_figures(output / "figures", dataset, predictions, metrics)
    write_json(output / "experiment_log.json", {
        "config": config.to_dict(), "num_cases": len(dataset),
        "conditions": list(VIEW_BUILDERS),
        "offline": True, "synthetic_pilot": True,
        "dev_set_implemented": False,
    })
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="results")
    parser.add_argument("--config")
    args = parser.parse_args()
    config = ExperimentConfig.load(args.config) if args.config else ExperimentConfig()
    metrics = run(config, args.output_dir)
    for condition, values in metrics.items():
        print(f"{condition}: balanced_accuracy={values['balanced_accuracy']:.3f}, "
              f"f1={values['f1']:.3f}, fpr={values['false_positive_rate']:.3f}")


if __name__ == "__main__":
    main()
