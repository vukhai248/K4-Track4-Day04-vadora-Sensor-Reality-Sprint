# BDD100K subset — dữ liệu chuẩn bị cho T1

Đã tải 50 ảnh; chưa tạo blur, chưa tính metric, chưa chạy detector.

- Mirror: https://huggingface.co/datasets/dgural/bdd100k
- Revision: c2e7f266756bcd07b87f1a45a35937c8eac20241
- Ngày tải: 05/10/2026.
- Metadata của mirror: 10.000 mẫu; 1.756 mẫu thỏa tiêu chí.
- Tiêu chí: weather=clear, timeofday=daytime, có ít nhất một car/pedestrian/bicycle.
- Sắp xếp theo filepath và lấy 50 mẫu đầu tiên, không phải lấy mẫu đại diện/ngẫu nhiên.
- Tổng dung lượng 50 ảnh: 3.572.812 bytes (khoảng 3,57 MB).
- Ảnh gốc: raw/; ảnh đã được kiểm tra đọc được và đúng kích thước metadata.
- manifest.json: danh sách ảnh, URL theo revision, kích thước và SHA-256.
- annotations/subset-samples.json: toàn bộ nhãn và metadata của 50 ảnh đã chọn.
- annotations/bdd100k-mirror-samples.json: metadata đầy đủ tải về, chỉ lưu local.
- Nhãn bbox của mirror: [x, y, width, height] chuẩn hóa theo kích thước ảnh, không phải YOLO [center_x, center_y, width, height].
- Tên nhãn người trong dữ liệu là pedestrian; cần mapping sang person nếu sau này dùng COCO detector.

## Tải lại

Script cần Python, requests và Pillow:

```powershell
python src/download_data.py
```

Script mặc định dùng revision cố định `c2e7f266756bcd07b87f1a45a35937c8eac20241`, trùng benchmark đã báo cáo. Các source_url và SHA-256 được lưu trong manifest.json. `--revision` cho phép chọn phiên bản khác cho thí nghiệm mới.

## Nguồn và quyền sử dụng

Ghi chú nguồn và điều khoản được công bố trong [dataset card](https://huggingface.co/datasets/dgural/bdd100k/blob/c2e7f266756bcd07b87f1a45a35937c8eac20241/README.md); đối chiếu nguồn này khi chia sẻ dữ liệu. Bản tải về trong docs/sources/bdd100k-mirror-README.md chỉ có ở máy đã chuẩn bị lab, không nằm trên GitHub.
Git bỏ qua ảnh raw và metadata đầy đủ để repo không mang theo các tệp tải lớn. Manifest, nhãn subset và script tải vẫn có thể lưu trong repo.
