"""Download a reproducible BDD100K subset; does not run any benchmark."""
import hashlib
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATASET = "dgural/bdd100k"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', default='c2e7f266756bcd07b87f1a45a35937c8eac20241',
                        help='Pinned dataset revision; use a different revision only for a new experiment')
    args = parser.parse_args()
    revision = args.revision
    base = f"https://huggingface.co/datasets/{DATASET}/resolve/{revision}"
    metadata = ROOT / "data/annotations/bdd100k-mirror-samples.json"
    metadata.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(f"{base}/samples.json", timeout=120)
    response.raise_for_status()
    metadata.write_bytes(response.content)
    samples = json.loads(response.content)["samples"]
    eligible = [s for s in samples
                if s.get("weather", {}).get("label") == "clear"
                and s.get("timeofday", {}).get("label") == "daytime"
                and any(d["label"] in {"car", "pedestrian", "bicycle"}
                        for d in s.get("detections", {}).get("detections", []))]
    eligible.sort(key=lambda s: s["filepath"])
    chosen = eligible[:50]
    if len(chosen) != 50:
        raise RuntimeError("Not enough eligible samples")
    raw = ROOT / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)

    def download(sample):
        relative = sample["filepath"]
        response = requests.get(f"{base}/{relative}", timeout=90)
        response.raise_for_status()
        path = raw / Path(relative).name
        path.write_bytes(response.content)
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            width, height = im.size
        expected = sample["metadata"]
        if (width, height) != (expected["width"], expected["height"]):
            raise RuntimeError(f"Dimension mismatch: {path.name}")
        return {"image_id": path.stem, "local_path": path.relative_to(ROOT).as_posix(),
                "source_url": f"{base}/{relative}", "width": width, "height": height,
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(response.content).hexdigest()}

    with ThreadPoolExecutor(max_workers=4) as pool:
        images = list(pool.map(download, chosen))
    manifest = {"dataset": DATASET, "revision": revision,
                "source_samples_count": len(samples), "eligible_samples_count": len(eligible),
                "selection": "weather=clear, timeofday=daytime, >=1 car/pedestrian/bicycle; sort filepath; first 50",
                "count": len(images), "download_date": "2026-10-05",
                "samples_json_sha256": hashlib.sha256(metadata.read_bytes()).hexdigest(),
                "images": images}
    (ROOT / "data/manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (ROOT / "data/annotations/subset-samples.json").write_text(
        json.dumps({"dataset": DATASET, "revision": revision, "samples": chosen}, indent=2), encoding="utf-8")
    print(json.dumps({"downloaded": len(images), "image_bytes": sum(x["bytes"] for x in images),
                      "revision": revision, "eligible": len(eligible)}))


if __name__ == "__main__":
    main()
