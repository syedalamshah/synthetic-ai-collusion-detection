"""Small dependency-free SVG figures for experiment comparison and errors."""
from pathlib import Path


def _svg(path, width, height, body):
    Path(path).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">{body}</svg>\n', encoding="utf-8")


def write_figures(output_dir, dataset, predictions, metrics):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    conditions = list(metrics)
    colors = {"M": "#4e79a7", "A": "#f28e2b", "MA": "#59a14f", "S": "#e15759"}
    body = '<rect width="100%" height="100%" fill="white"/><text x="20" y="25" font-size="16">Balanced accuracy</text>'
    for i, condition in enumerate(conditions):
        x = 45 + i * 115
        value = metrics[condition]["balanced_accuracy"]
        height = round(value * 180)
        body += (f'<rect x="{x}" y="{220-height}" width="65" height="{height}" '
                 f'fill="{colors[condition]}"/><text x="{x+20}" y="240" font-size="13">{condition}</text>'
                 f'<text x="{x+12}" y="{210-height}" font-size="11">{value:.3f}</text>')
    _svg(output / "metrics_comparison.svg", 520, 270, body)

    labels = {row["case_id"]: row["sealed_label"]["label"] for row in dataset}
    body = '<rect width="100%" height="100%" fill="white"/><text x="20" y="25" font-size="16">Errors by detector</text>'
    for i, condition in enumerate(conditions):
        pred = predictions[condition]
        fp = sum(labels[k] == 0 and v == 1 for k, v in pred.items())
        fn = sum(labels[k] == 1 and v == 0 for k, v in pred.items())
        x = 55 + i * 115
        fp_h, fn_h = fp * 7, fn * 7
        body += (f'<rect x="{x}" y="{210-fp_h}" width="28" height="{fp_h}" fill="#f28e2b"/>'
                 f'<rect x="{x+32}" y="{210-fn_h}" width="28" height="{fn_h}" fill="#e15759"/>'
                 f'<text x="{x+15}" y="230" font-size="13">{condition}</text>'
                 f'<text x="{x}" y="{200-fp_h}" font-size="10">FP {fp}</text>'
                 f'<text x="{x+32}" y="{200-fn_h}" font-size="10">FN {fn}</text>')
    body += '<text x="400" y="255" font-size="11">orange=FP, red=FN</text>'
    _svg(output / "error_analysis.svg", 520, 270, body)
