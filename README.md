# 🎬 Hướng dẫn sử dụng NexgenAgent Auto

**Tạo video quảng cáo bằng AI — không cần biết lập trình.**

NexgenAgent Auto giúp team tạo video quảng cáo bằng **Claude + Negen + CapCut**.

Bạn chỉ cần chọn sản phẩm, duyệt ý tưởng và kiểm tra video cuối cùng. Claude sẽ hỗ trợ các bước còn lại.

## 1. Chuẩn bị

Trước khi bắt đầu, bạn cần:

- Máy Windows (Mac cũng dùng được).
- [Claude Desktop](https://claude.ai/download) — sử dụng mục **Code**.
- [Tài khoản Negen](https://marketing-tool.nexgenbros.com).
- CapCut bản máy tính (phiên bản 9.x), đã mở ít nhất một lần và đã tạo thử một project.
- Quyền truy cập repo NexgenAgent Auto.

Máy Windows cần thêm Git, Python và ffmpeg. Nếu thiếu, Claude sẽ báo và hướng dẫn cài trong lúc setup.

## 2. Cài đặt lần đầu

**Bước 1:** Mở Claude Desktop → chọn **Code**.

**Bước 2:** Copy và gửi tin nhắn sau cho Claude:

```text
Hãy cài đặt công cụ này giúp mình:

https://github.com/NexGen26-tool/NexgenAgent-Auto

Lưu vào ~/NexgenAgent-Auto và chạy setup.

Mình không có kiến thức kỹ thuật, hãy hướng dẫn
từng bước bằng tiếng Việt nếu cần mình thao tác.
```

**Bước 3:** Làm theo hướng dẫn của Claude.

Nếu được yêu cầu tải font hoặc hiệu ứng, hãy mở CapCut và sử dụng từng mục sau một lần:

- Font: Montserrat, PT Sans, HV-Analogue-Bold-Italic.
- Hiệu ứng chữ: Zoom 1 (In), Smoke (Out).

Sau đó nhắn Claude: **"Chạy lại setup và kiểm tra giúp mình."**

Khi xuất hiện **Setup OK** là hoàn tất. Bạn chỉ cần cài đặt một lần.

Nếu setup báo **"CapCut can take built projects: NO"**, công cụ vẫn dùng được. Khi đó Claude không tạo được project
CapCut, mà sẽ gửi video sạch kèm một bảng chữ (text sheet) ghi từng dòng chữ và thời gian để bạn gõ vào CapCut.

## 3. Tạo video quảng cáo

**Bước 1:** Mở Claude Desktop → Code → chọn thư mục `NexgenAgent-Auto`.

**Bước 2:** Đăng nhập Negen trong trình duyệt Claude sử dụng.

**Bước 3:** Nhập lệnh:

`/fastlane`

Claude sẽ hướng dẫn bạn chọn sản phẩm, tạo storyboard, chuẩn bị brief, duyệt Hook và chạy tạo video.

Bạn chỉ cần làm theo hướng dẫn và xác nhận khi Claude yêu cầu. Những thao tác tốn credits hoặc tiền sẽ cần được bạn đồng ý trước.

**Bước 4:** Khi Claude chuẩn bị project CapCut, hãy thoát hẳn CapCut nếu được yêu cầu:

- Windows: đóng CapCut, rồi bấm chuột phải vào biểu tượng CapCut ở khay hệ thống (góc phải dưới) → Thoát.
- Mac: bấm **Cmd + Q**.

**Bước 5:** Mở project CapCut do Claude chuẩn bị và kiểm tra:

- Đúng sản phẩm và thương hiệu.
- Hình ảnh, chữ và logo hiển thị chính xác.
- Voice-over khớp với video.
- Hiệu ứng kết thúc hoạt động bình thường.

Chỉnh sửa nếu cần, sau đó xuất video.

## 4. Các lệnh cần nhớ

| Lệnh | Công dụng |
|---|---|
| `/fastlane` | Bắt đầu tạo video |
| `/fastlane-status` | Kiểm tra tiến độ |
| `/fastlane-capcut` | Tạo lại project CapCut |

## 5. Khi gặp lỗi

| Vấn đề | Cách xử lý |
|---|---|
| Hết Grok credits | Liên hệ admin |
| ChatGPT bị đăng xuất | Liên hệ admin |
| CapCut đang mở | Thoát hẳn CapCut (Windows: thoát cả ở khay hệ thống; Mac: Cmd + Q) rồi chạy lại |
| Setup báo CapCut không nhận project | Vẫn dùng được: Claude gửi video kèm bảng chữ để bạn gõ vào CapCut |
| Font hiển thị sai | Tải font trong CapCut, nhờ Claude kiểm tra setup rồi tạo lại project |
| Không hiểu lỗi | Copy thông báo lỗi và gửi Claude nhờ hướng dẫn |

Bạn có thể nhắn Claude bằng tiếng Việt:

> Mình gặp lỗi này. Hãy giải thích đơn giản và hướng dẫn mình từng bước để xử lý.

---

**Nhớ 4 bước chính:**

**Mở Claude Code → `/fastlane` → Duyệt nội dung → Hoàn thiện trong CapCut.**

Không cần học GitHub hay lập trình để sử dụng công cụ.
