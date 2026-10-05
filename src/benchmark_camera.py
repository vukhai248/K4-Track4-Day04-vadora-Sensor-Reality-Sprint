"""Small T1 benchmark: original vs average blur; Fourier vs BREMOLA.

Uses the operations in the public BREMOLA script, with explicit preprocessing,
invalid-score handling, and additional lab metrics. No detector is run.
"""
import argparse
import csv
import hashlib
import json
import platform
import sys
from datetime import datetime
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
KERNELS = [1, 3, 5, 7, 9, 11]
SOURCE = "https://github.com/woongchan789/BREMOLA/blob/7ba26999c265692bb8e44c5a3f2d91c06746830f/bremola.py"


def metrics(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    spectrum = 14 * np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(gray))))
    area = int(np.count_nonzero(spectrum > 100))
    complexity = int(cv2.Laplacian(gray, cv2.CV_8U, ksize=3,
                                 borderType=cv2.BORDER_DEFAULT).sum())
    raw = area / np.sqrt(complexity) if complexity > 0 else None
    counts = np.bincount(gray.ravel(), minlength=256)
    probabilities = counts[counts > 0] / gray.size
    dark = float(np.mean(gray <= 5))
    bright = float(np.mean(gray >= 250))
    return {
        "fourier_area": area,
        "laplacian_complexity": complexity,
        "bremola_raw": float(raw) if raw is not None else None,
        "bremola_0_100": float(np.clip(raw / 5, 0, 100)) if raw is not None else None,
        "score_status": "ok" if complexity > 0 else "invalid_zero_complexity",
        "laplacian_variance": float(cv2.Laplacian(gray, cv2.CV_64F,
                                                ksize=3).var()),
        "dark_ratio": dark,
        "bright_ratio": bright,
        "saturation_ratio": dark + bright,
        "entropy_bits": float(-np.sum(probabilities * np.log2(probabilities))),
    }


def write_csv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def save_image(path, image):
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise RuntimeError(f"Could not encode {path}")
    path.write_bytes(encoded.tobytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/raw")
    parser.add_argument("--limit", type=int, default=5, help="First N images sorted by filename")
    parser.add_argument("--output", type=Path, help="New output directory; existing directory is rejected")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be >= 1")
    files = sorted(p for p in args.input.iterdir()
                   if p.suffix.lower() in {".jpg", ".jpeg", ".png"})[:args.limit]
    if not files:
        parser.error(f"No input images in {args.input}")
    # Reject duplicate output identities across different image formats.
    if len({p.stem for p in files}) != len(files):
        parser.error("Input filenames must have unique stems")
    out = args.output or ROOT / "results" / datetime.now().strftime("average-blur-%Y%m%d-%H%M%S-%f")
    out.mkdir(parents=True, exist_ok=False)
    (out / "images").mkdir()
    rows, source_images, log = [], [], []
    for path in files:
        image = cv2.imdecode(np.frombuffer(path.read_bytes(), dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise RuntimeError(f"Could not read {path}")
        source_images.append({"file": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                              "original_width": image.shape[1], "original_height": image.shape[0]})
        # Fixed preprocessing BEFORE corruption, so kernel sizes are comparable.
        image = cv2.resize(image, (1920, 1080), interpolation=cv2.INTER_LINEAR)
        strip = Image.new("RGB", (640 * 3, (360 + 35) * 2), "white")
        for level, kernel in enumerate(KERNELS):
            degraded = image.copy() if kernel == 1 else cv2.blur(image, (kernel, kernel),
                                                               borderType=cv2.BORDER_DEFAULT)
            row = {"image_id": path.stem, "level": level, "kernel_px": kernel, **metrics(degraded)}
            rows.append(row)
            save_image(out / "images" / f"{path.stem}_k{kernel:02d}.png", degraded)
            thumbnail = Image.fromarray(cv2.cvtColor(degraded, cv2.COLOR_BGR2RGB)).resize((640, 360))
            x, y = (level % 3) * 640, (level // 3) * 395
            strip.paste(thumbnail, (x, y + 35))
            label = "Original (baseline)" if kernel == 1 else f"Average blur {kernel}x{kernel}"
            ImageDraw.Draw(strip).text((x + 10, y + 10), label, fill="black")
            log.append(f"{path.name}: k={kernel}, A={row['fourier_area']}, B={row['laplacian_complexity']}, status={row['score_status']}")
        strip.save(out / f"{path.stem}_comparison.png")
        print(f"Processed {path.name}", flush=True)
    write_csv(out / "metrics.csv", rows)
    metric_names = ["fourier_area", "bremola_raw", "bremola_0_100", "laplacian_variance",
                    "saturation_ratio", "entropy_bits"]
    summary = []
    for kernel in KERNELS:
        group = [r for r in rows if r["kernel_px"] == kernel]
        entry = {"kernel_px": kernel, "image_count": len(group)}
        for name in metric_names:
            values = [r[name] for r in group if r[name] is not None and np.isfinite(r[name])]
            entry[f"{name}_valid_count"] = len(values)
            entry[f"{name}_mean"] = float(np.mean(values)) if values else None
            entry[f"{name}_std"] = float(np.std(values)) if values else None
        summary.append(entry)
    write_csv(out / "summary.csv", summary)
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, name in zip(axes.ravel(), metric_names):
        for path in files:
            group = [r for r in rows if r["image_id"] == path.stem]
            ax.plot(KERNELS, [r[name] if r[name] is not None else np.nan for r in group], marker="o", alpha=.65)
        ax.set(title=name, xlabel="Average blur kernel width (pixels)", ylabel=name)
        ax.set_xticks(KERNELS)
        ax.grid(alpha=.25)
    fig.suptitle(f"Original (k=1) vs average blur; N={len(files)}; each line is one image")
    fig.tight_layout()
    fig.savefig(out / "metrics_by_blur.png", dpi=150)
    plt.close(fig)
    config = {
        "command": [sys.executable, *sys.argv], "source_method": SOURCE,
        "method_note": "Operations adapted from public code; not an exact reproduction of all paper experiments.",
        "selection": "first N files sorted by filename", "image_count": len(files),
        "rows": len(rows), "kernels": KERNELS, "resize_before_blur": [1920, 1080],
        "resize_interpolation": "INTER_LINEAR", "border": "OpenCV BORDER_DEFAULT (REFLECT_101)",
        "fourier": "A=count(14*log(1+abs(fftshift(fft2(gray))))>100)",
        "complexity": "B=sum(Laplacian(gray,CV_8U,ksize=3))",
        "bremola_raw": "A/sqrt(B); blank/invalid if B=0",
        "bremola_0_100": "clip(bremola_raw/5,0,100); not a probability of camera health",
        "laplacian_variance": "var(Laplacian(gray,CV_64F,ksize=3)); intensity-squared units",
        "saturation_ratio": "fraction of grayscale pixels <=5 or >=250; dark/bright ratios also saved",
        "entropy_bits": "Shannon entropy of 256-bin grayscale histogram, log base 2",
        "summary_std": "population standard deviation (ddof=0); within each kernel across images",
        "versions": {"python": platform.python_version(), "opencv": cv2.__version__,
                     "numpy": np.__version__, "matplotlib": matplotlib.__version__, "pillow": Image.__version__},
        "inputs": source_images, "detector_run": False,
    }
    (out / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (out / "run.log").write_text("\n".join(log) + "\n", encoding="utf-8")
    print(f"Done: {len(rows)} rows. Results: {out.resolve()}")


if __name__ == "__main__":
    main()
