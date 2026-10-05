# Measured benchmark analysis

N=50 images; 300 measurements.

| Metric | Original mean | k11 mean | Drop (%) | Nonincreasing images |
|---|---:|---:|---:|---:|
| fourier_area | 991267.820000 | 278349.560000 | 71.92 | 50/50 |
| bremola_raw | 277.337916 | 159.941411 | 42.33 | 29/50 |
| bremola_0_100 | 55.467583 | 31.988282 | 42.33 | 29/50 |
| laplacian_variance | 809.910174 | 21.230633 | 97.38 | 50/50 |
| saturation_ratio | 0.012794 | 0.010792 | 15.65 | 49/50 |
| entropy_bits | 7.485861 | 7.468517 | 0.23 | 30/50 |

BREMOLA raw and 0-100 are the same underlying metric. Monotonicity does not establish general sensor fault detection or downstream accuracy.

Score-ordering failure: b1ff4656-94ee8536, k=5 -> 7; BREMOLA increased 2.09%.

![Measured failure case](failure-case.png)
