"""Summarize measured benchmark results and select a score-ordering failure."""
import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

NAMES = ['fourier_area', 'bremola_raw', 'bremola_0_100',
         'laplacian_variance', 'saturation_ratio', 'entropy_bits']


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('results', type=Path)
    args = ap.parse_args()
    root = args.results
    with (root / 'metrics.csv').open(encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    ids = list(dict.fromkeys(r['image_id'] for r in rows))
    groups = {i: sorted([r for r in rows if r['image_id'] == i], key=lambda r: int(r['kernel_px'])) for i in ids}
    kernels = [int(r['kernel_px']) for r in groups[ids[0]]]
    stats, summary = {}, []
    for name in NAMES:
        values = np.array([[float(r[name]) if r[name] else np.nan for r in groups[i]] for i in ids])
        valid = np.all(np.isfinite(values), axis=1)
        increases = [(i, k) for i in range(len(ids)) if valid[i]
                     for k in range(1, len(kernels)) if values[i, k] > values[i, k-1] + 1e-9]
        stats[name] = {'valid_images': int(valid.sum()),
                       'mean': np.nanmean(values, axis=0).tolist(),
                       'std': np.nanstd(values, axis=0).tolist(),
                       'cv': (np.nanstd(values, axis=0) / np.nanmean(values, axis=0)).tolist(),
                       'nonincreasing_images': sum(bool(np.all(np.diff(v) <= 1e-9)) for v in values[valid]),
                       'increasing_transitions': len(increases)}
        stat = stats[name]
        summary.append({'metric': name, 'original_mean': stat['mean'][0], 'k11_mean': stat['mean'][-1],
                        'drop_percent': 100*(1-stat['mean'][-1]/stat['mean'][0]),
                        'nonincreasing_images': stat['nonincreasing_images'],
                        'valid_images': stat['valid_images'],
                        'original_cv': stat['cv'][0], 'k11_cv': stat['cv'][-1]})
    candidates = []
    for i, group in groups.items():
        for before, after in zip(group, group[1:]):
            if before['bremola_raw'] and after['bremola_raw']:
                increase = float(after['bremola_raw']) / float(before['bremola_raw']) - 1
                if increase > 1e-9:
                    candidates.append((increase, i, before, after))
    failure = None
    if candidates:
        increase, image_id, before, after = max(candidates, key=lambda x: x[0])
        failure = {'image_id': image_id, 'relative_increase_percent': increase*100,
                   'before': before, 'after': after,
                   'interpretation': 'Blur kernel increased while BREMOLA increased; score-ordering limitation, not a measured detector failure.'}
        canvas = Image.new('RGB', (1280, 425), 'white')
        for col, row in enumerate([before, after]):
            k = int(row['kernel_px'])
            path = root / 'images' / f'{image_id}_k{k:02d}.png'
            with Image.open(path) as image:
                canvas.paste(image.resize((640,360)), (col*640,65))
            label = f"k={k} | BREMOLA={float(row['bremola_raw']):.2f} | A={row['fourier_area']}"
            ImageDraw.Draw(canvas).text((col*640+10,10), label, fill='black')
            ImageDraw.Draw(canvas).text((col*640+10,35), f"B={row['laplacian_complexity']} | LapVar={float(row['laplacian_variance']):.2f}", fill='black')
        canvas.save(root / 'failure-case.png')
    result = {'image_count':len(ids), 'rows':len(rows), 'kernels':kernels,
              'metrics':stats, 'failure':failure, 'summary':summary}
    (root/'analysis.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    fig, axes = plt.subplots(2,3,figsize=(15,8))
    for ax, name in zip(axes.ravel(),NAMES):
        stat=stats[name]
        ax.errorbar(kernels,stat['mean'],yerr=stat['std'],marker='o',capsize=4)
        ax.set(title=name,xlabel='Average blur kernel width (pixels)',ylabel=name)
        ax.set_xticks(kernels)
        ax.grid(alpha=.25)
    fig.suptitle(f'N={len(ids)}; mean +/- population SD across images (not confidence intervals)')
    fig.tight_layout()
    fig.savefig(root/'aggregate-metrics.png',dpi=150)
    plt.close(fig)
    lines=['# Measured benchmark analysis','',f'N={len(ids)} images; {len(rows)} measurements.','',
           '| Metric | Original mean | k11 mean | Drop (%) | Nonincreasing images |',
           '|---|---:|---:|---:|---:|']
    for s in summary:
        lines.append(f"| {s['metric']} | {s['original_mean']:.6f} | {s['k11_mean']:.6f} | {s['drop_percent']:.2f} | {s['nonincreasing_images']}/{s['valid_images']} |")
    lines+=['','BREMOLA raw and 0-100 are the same underlying metric. Monotonicity does not establish general sensor fault detection or downstream accuracy.']
    if failure:
        lines+=['',f"Score-ordering failure: {failure['image_id']}, k={failure['before']['kernel_px']} -> {failure['after']['kernel_px']}; BREMOLA increased {failure['relative_increase_percent']:.2f}%.",'','![Measured failure case](failure-case.png)']
    (root/'analysis.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'summary':summary,'failure':failure},ensure_ascii=True,indent=2))


if __name__=='__main__':
    main()
