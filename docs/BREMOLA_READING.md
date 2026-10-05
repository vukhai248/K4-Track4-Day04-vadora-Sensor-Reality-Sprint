# Ghi chép đọc BREMOLA và làm rõ baseline

Trạng thái: đã đọc paper đầy đủ và code tác giả; đã chạy kiểm tra benchmark riêng trên 5 ảnh sau khi người dùng yêu cầu tạo code để chạy. Chưa chạy detector.

## Nguồn

- Nam, Youn, Ha (2025), Vehicles 7(1), 8. DOI: https://doi.org/10.3390/vehicles7010008
- Paper: https://www.mdpi.com/2624-8921/7/1/8
- PDF local: sources/bremola-2025.pdf (bản từ kho TU Darmstadt, có một trang bìa bổ sung).
- Kho PDF: https://tustorage.ulb.tu-darmstadt.de/server/api/core/bitstreams/9a5ffe21-e88f-40af-9ec4-1def8e544487/content
- Code: https://github.com/woongchan789/BREMOLA/blob/master/bremola.py

## Problem — mục 1 và 3.3

Camera có thể còn xuất ảnh nhưng ảnh bị blur. Khi cảnh thay đổi, score ảnh cũng thay đổi do số lượng biên/texture, khiến cảnh đơn giản bị nhầm với ảnh suy giảm. Bài đề xuất một metric no-reference để giảm ảnh hưởng đó; không cần ảnh tham chiếu khi tính từng score.

## Method — mục 4.1, 4.2; Equation (8), Figure 12

1. Chuyển ảnh sang grayscale; FFT và dịch phổ.
2. Tính phổ log với hệ số 14; A là số phần tử phổ vượt ngưỡng 100.
3. Tính B từ tổng giá trị ảnh biên Laplacian, đại diện độ phức tạp cảnh.
4. Score chính trong paper: A/sqrt(B). Code công khai chia thêm 5 và clip về 0–100.

B không phải Variance of Laplacian. Paper chọn Laplacian qua so sánh tương quan hạng giữa các bộ lọc và A (Table 2), không phải qua mAP detector. Khi triển khai phải ghi rõ dùng công thức paper hay code công khai, tránh trộn hai cách.

## Thí nghiệm và giới hạn

Paper dùng 45 frame từ ba video và 20 kích thước bộ lọc blur, tổng 900 mẫu. Figure 17 so sánh score phổ trước/sau bù complexity; Figure 18 so với các IQA khác. Figure 19 minh họa theo dõi chuỗi video với blur tăng theo thời gian.

Đây là bằng chứng của tác giả trên bộ thử của họ, chưa phải kết quả nhóm. Nghiên cứu giới hạn ở blur, cần kiểm chứng trên nhiều cảnh/thời tiết và hệ quyết định phía sau (mục 6).

Các điểm cần chú ý khi tái hiện:
- Mục 5.1 có cách gọi median/mean không nhất quán, còn mô tả bộ lọc và nhiều hình nói average/mean filter. Phải khai báo rõ phép blur nhóm thực sự dùng.
- Mục 3.4 đặt ranh giới normal <=3x3 và faulty >=4x4, nhưng Figure 19 gọi mốc 3x3 là failure onset. Không lấy mốc này làm ngưỡng camera hỏng phổ quát.
- Paper chưa định lượng recall/mAP hoặc chứng minh cảnh báo xảy ra trước lỗi detector.
- Code resize 1920x1080, Laplacian CV_8U ksize=3; cần kiểm tra sự khác biệt kernel/padding so với mô tả paper trước khi gọi là tái hiện nguyên bản.
- B=0 có thể khiến score không hợp lệ; cần quy tắc xử lý khi triển khai.

## Ba nghĩa của baseline

| Thuật ngữ | Nghĩa trong kế hoạch nhóm |
|---|---|
| Baseline condition của đề lab | Ảnh gốc chưa chủ động thêm lỗi; cùng dữ liệu/pipeline so với 3–5 mức blur. |
| Method baseline bám paper | Score phổ A chưa bù complexity, so với A/sqrt(B); thang đo phải được ghi rõ. |
| Method baseline bổ sung | Variance of Laplacian là lựa chọn đơn giản do nhóm thêm, không phải đối chứng chính của Figure 17. |

Có ảnh gốc để tạo đối chứng không làm BREMOLA thành full-reference: score của mỗi ảnh vẫn được tính từ chính ảnh đó, không lấy ảnh gốc để tính sai khác pixel.

## Đề lab có bắt buộc áp dụng paper không?

Đối chiếu văn bản đề người dùng cung cấp (Bước 2, 4, 6): yêu cầu tìm paper hoặc repository liên quan, giải thích phương pháp và chạy demo/benchmark nhỏ có metric/bằng chứng. Cho phép demo gốc, script nhỏ hoặc benchmark mô phỏng; nếu mô phỏng phải nêu lý do và giới hạn proxy. Không yêu cầu tái hiện đầy đủ một paper cụ thể.

Đề xuất sau khi người dùng chốt: chạy một phần BREMOLA trên subset đã tải, đối chứng với A chưa bù complexity; thêm Variance of Laplacian và các metric T1 nếu phù hợp. Nếu dùng defocus disk thay vì average filter và BDD100K thay dữ liệu gốc, báo cáo là áp dụng phương pháp trên benchmark riêng, không tái hiện nguyên bản paper.

Cấu hình chạy thử hiện tại: 5 ảnh, average blur với kernel 1 (original), 3, 5, 7, 9, 11; resize 1920x1080 trước blur. Đây là bước kiểm tra pipeline, chưa phải kết luận tổng quát về phương pháp.
