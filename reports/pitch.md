# Kịch bản pitch 3–5 phút — nhóm vadora

## 0:00–0:35 — Problem

Camera ADAS có thể vẫn có ảnh nhưng ảnh mờ. Nhóm muốn biết có thể dùng score từ chính ảnh để theo dõi chất lượng hay không. Bài thử tập trung average blur, không train model và chưa chạy detector.

Block của nhóm là camera quality monitor: sau thu nhận ảnh/ISP và chạy song song camera perception. Score được đề xuất gửi tới sensor supervisor, phục vụ cảnh báo và policy tin cậy của fusion; không phải thuật toán xử lý radar/LiDAR. Xem sơ đồ trong docs/ADAS_PIPELINE.md. Chỉ block tính score offline đã được chạy trong lab.

## 0:35–1:20 — Method

BREMOLA của Nam và cộng sự, 2025, nhận một ảnh và trả score không cần reference. Fourier A phản ánh phổ ảnh; Laplacian B phản ánh độ phức tạp; kết hợp A/sqrt(B) để bù ảnh hưởng cảnh. Nhóm so với A chưa bù và đo thêm Laplacian variance, saturation ratio, entropy. BREMOLA raw và score 0–100 là cùng một thông tin với thang đo khác nhau.

## 1:20–2:20 — Benchmark

Mở aggregate-metrics.png trong kết quả full benchmark. Nhóm tải 50 ảnh BDD100K clear/daytime, resize cố định rồi tạo 5 mức average blur. Ảnh gốc là baseline, mỗi ảnh có 6 điều kiện, tổng 300 hàng số đo. Fourier trung bình giảm khoảng 72%, BREMOLA giảm khoảng 42%, Laplacian variance giảm khoảng 97%. Entropy gần như không đổi, nên không dùng làm metric blur chính. Các tỷ lệ giảm có thang đo khác nhau, không phải bảng xếp hạng phương pháp.

## 2:20–3:10 — Failure case

Mở failure-case.png. Với ảnh b1ff4656-94ee8536, tăng blur 5×5 lên 7×7 nhưng BREMOLA tăng 167,14 lên 170,63. A giảm và B cũng giảm, khiến tỷ số tăng. Có 21/50 ảnh có ít nhất một bước BREMOLA tăng. Đây là giới hạn xếp thứ tự mức blur; chưa có số đo chứng minh detector bỏ sót vật thể.

## 3:10–4:00 — Engineering decision

Theo dõi BREMOLA cùng các metric và ảnh/log hỗ trợ, chưa dùng một threshold chung để tuyên bố camera hỏng. Bước tiếp theo là hiệu chuẩn trên tập riêng, đo false alarm trên video có đổi cảnh và đánh giá detector với nhãn. Cảnh báo bền vững qua nhiều frame giảm dao động nhưng có thể làm trễ cảnh báo. Dữ liệu hiện tại ít, chỉ ban ngày, blur tổng hợp không đại diện đầy đủ lỗi optics.

## Khi được hỏi đã chạy gì

Mở metrics.csv, config.json và run.log trong results/average-blur-20261005-173207-032247/. Có thể chạy lại lệnh README trên cùng manifest ảnh. Chỉ trích số tự đo từ CSV; kết quả paper là nguồn riêng.

## Phân công trình bày

Nếu được hỏi về multi-camera: tính score cho từng camera sau ISP rồi đưa vào supervisor theo timestamp và vùng nhìn. Không lấy trung bình làm kết luận duy nhất vì camera quan trọng bị mờ có thể bị các camera khác che lấp. Đây là extension trong docs/MULTI_CAMERA_EXTENSION.md, chưa phải kết quả đã chạy.

- Vũ Gia Khải: problem, vị trí block trong pipeline, method và benchmark.
- Phạm Văn Kiên: failure case, limitation, engineering decision và trade-off.
