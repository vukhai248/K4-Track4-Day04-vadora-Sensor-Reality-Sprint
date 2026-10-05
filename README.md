# T1 — Camera degradation health score

> Nhóm: vadora. Repository: https://github.com/vukhai248/K4-Track4-Day04-vadora-Sensor-Reality-Sprint

## Phạm vi dự kiến
- Nền tảng: xe ADAS.
- Sensor: camera quan sát đường.
- Failure case: ảnh bị nhòe (blur).
- Claim ban đầu: tăng mức nhòe trên cùng ảnh làm blur score giảm.
- Benchmark hoàn chỉnh: 50 ảnh gốc (baseline), mỗi ảnh có thêm average blur 3×3, 5×5, 7×7, 9×9, 11×11; tổng 300 điều kiện ảnh.
- Metric: blur score, saturation ratio, entropy; định nghĩa cách tính trước khi chạy.

## Cấu trúc
- TEAMMATES.md: họ tên và MSSV của 2 thành viên theo xác nhận người dùng; xem lưu ý quy mô nhóm trong checklist.
- src/: mã nguồn benchmark.
- configs/: tham số baseline, mức lỗi và cấu hình đo.
- data/: ảnh mẫu được phép chia sẻ hoặc hướng dẫn lấy dữ liệu.
- results/: bảng số đo, log, ảnh trước/sau và plot.
- reports/: báo cáo nhóm, 2 bản riêng và kịch bản pitch.

## Nguồn và cách chạy
- Paper/repository đã đọc: BREMOLA 2025; xem [ghi chép đọc paper](docs/BREMOLA_READING.md).
- Nguồn thuật toán: code BREMOLA commit `7ba26999c265692bb8e44c5a3f2d91c06746830f`; script nhóm áp dụng các phép tính trong code công khai, không tái hiện nguyên bản mọi thí nghiệm của paper.
- Nguồn dữ liệu, số mẫu: 50 ảnh BDD100K clear/daytime từ mirror dgural/bdd100k; revision, nhãn và SHA-256 trong [data](data/README.md).
- Mã chạy: `src/benchmark_camera.py`; dependencies được ghi trong `requirements.txt`.

## Chạy trên Windows PowerShell

Mở terminal tại thư mục repository. Lần đầu, tạo môi trường và cài thư viện:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Chạy 5 ảnh đã tải:

```powershell
.\.venv\Scripts\python.exe src\benchmark_camera.py --limit 5
```

Khi muốn chạy cả 50 ảnh:

```powershell
.\.venv\Scripts\python.exe src\benchmark_camera.py --limit 50
```

Phân tích và tạo lại báo cáo từ kết quả (thay đường dẫn bằng thư mục kết quả vừa chạy):

```powershell
.\.venv\Scripts\python.exe src\analyze_results.py results\average-blur-20261005-173207-032247
.\.venv\Scripts\python.exe src\build_report.py results\average-blur-20261005-173207-032247
```

`build_report.py` tạo lại báo cáo nhóm và hai bản cá nhân; sẽ ghi đè nội dung các file đó, nên lưu riêng chỉnh sửa cá nhân trước khi chạy lại.

Mỗi lần chạy tạo một thư mục mới `results/average-blur-<timestamp>/` chứa:
- `metrics.csv`: số đo từng ảnh ở từng mức blur.
- `summary.csv`: mean/std và số mẫu hợp lệ theo mức blur.
- `metrics_by_blur.png`: sáu biểu đồ, mỗi đường là một ảnh.
- `<image_id>_comparison.png`: ảnh gốc và năm mức blur cạnh nhau.
- `images/`: ảnh PNG của từng điều kiện.
- `config.json`, `run.log`: định nghĩa metric, tham số, phiên bản, hash đầu vào và log.

Baseline condition là ảnh gốc sau resize cố định 1920×1080 nhưng chưa thêm blur. Method baseline là `fourier_area` chưa bù complexity; BREMOLA được lưu cả `bremola_raw=A/sqrt(B)` và score có scaling/clipping theo code công khai. Variance of Laplacian là metric bổ sung, không phải B trong BREMOLA.

Các score có thang đo khác nhau; không so trực tiếp độ cao số hoặc raw standard deviation giữa chúng để kết luận phương pháp nào tốt hơn. Score 0–100 không phải xác suất camera khỏe. Không dùng riêng phép thử này để kết luận recall/mAP hay camera hỏng thật. Đây là benchmark riêng trên BDD100K; kernel/padding bám code công khai, blur và resize được khai báo rõ.

## Trạng thái
Đã tải dữ liệu, đọc paper và chạy 50 ảnh × 6 điều kiện = 300 hàng số đo. Kết quả chính: [full benchmark](results/average-blur-20261005-173207-032247/analysis.md). Không chạy detector.

Kết quả tự đo: BREMOLA raw trung bình 277,34 → 159,94; 21/50 ảnh có ít nhất một bước score tăng khi kernel blur tăng. Điều này không chứng minh BREMOLA tốt hơn mọi metric, cũng không chứng minh camera hỏng vật lý.

- [Báo cáo nhóm](reports/group-report.md)
- [Vũ Gia Khải](reports/thanh-vien-1.md)
- [Phạm Văn Kiên](reports/thanh-vien-2.md)
- [Kịch bản pitch](reports/pitch.md)
- [Checklist nộp bài](SUBMISSION_CHECKLIST.md)
- [Vị trí camera quality monitor trong pipeline ADAS](docs/ADAS_PIPELINE.md)

## Nộp bài
Mỗi thành viên nộp bản báo cáo riêng và cùng URL repository nhóm trên VLearn. Đã có phân công; người học cần kiểm tra đóng góp thực tế và ngoại lệ nhóm 2 người so với yêu cầu 5 người trong bản đề đã cung cấp.

