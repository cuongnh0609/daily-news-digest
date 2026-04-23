# 🇯🇵 デイリーダイジェスト — Setup Guide (Claude Code Routine v3)

Hướng dẫn tạo Routine tự động sinh bản tin tổng hợp mỗi 5 giờ cho **SE / Cloud Engineer đang học tiếng Nhật JLPT N2+**.

**Output mỗi lần chạy:** File HTML 11 bài chia 3 mục (5 + 3 + 3), layout 2 cột adaptive theo ngôn ngữ, dark mode toggle, tự động chống trùng với các lần chạy trước.

---

## 📦 Gói file

| File                 | Mục đích                                        |
| -------------------- | ----------------------------------------------- |
| `README.md`          | File này — setup guide                          |
| `ROUTINE_PROMPT.md`  | Prompt v3 paste vào Routine                     |
| `news_template.html` | Template HTML 2 cột (hỗ trợ cả layout JP và EN) |
| `CLAUDE.md`          | Guide cho Claude Code khi edit repo này         |

---

## 📋 Tổng quan nội dung

| Mục                    | Số bài | Nguồn                                                        | Layout 2 cột                                               |
| ---------------------- | ------ | ------------------------------------------------------------ | ---------------------------------------------------------- |
| **A** — 🗾 日本ニュース | **5**  | NHK, Nikkei, Yahoo, Jiji, Kyodo                              | ① Tin JP + dịch VN · ② Từ vựng + ngữ pháp N2+              |
| **B** — 🇯🇵 Tech JP     | **3**  | Zenn, Qiita, ITmedia AI+, Publickey, Connpass, X JP          | ① Tin JP + dịch VN · ② Từ vựng IT + ngữ pháp N2+           |
| **C** — 🌐 Global Tech  | **3**  | Anthropic/OpenAI/DeepMind, AWS/GCP/Azure, GitHub/Cursor/LangChain, Simon Willison/Swyx/Karpathy... | ① Tin EN + impact badge · ② Dịch VN + giải thích thuật ngữ |
| **Tổng**               | **11** |                                                              |                                                            |

### 🎯 Ưu tiên chủ đề AI xuyên suốt

Mục B & C ưu tiên **≥ 2/3 bài thuộc chủ đề AI** (theo thứ tự):

1. **Claude Code & Anthropic** — features, Routines, MCP, Claude models, API
2. **AI-Driven Development** — Cursor, Aider, Cline, Windsurf, Continue, Zed AI
3. **AI Agentic** — LangGraph, CrewAI, AutoGen, Mastra, agent patterns, benchmarks
4. **AI general** — LLM releases, reasoning models, research papers nổi bật
5. **AI infrastructure** — inference, vector DB, RAG patterns
6. Tech khác (Cloud/K8s/DevOps/language/security) — lấp tối đa 1 bài mỗi mục B, C

### 🚫 Chống trùng lặp nghiêm ngặt

Routine lưu state file `state/last_run_urls.json` chứa URL + title của các bài đã lấy trong 7 ngày gần nhất. Mỗi lần chạy:

1. **Bước 0** — build blocklist từ các run trong **48h qua**
2. Skip tin nếu URL hoặc title khớp blocklist (có fuzzy matching)
3. Nếu không đủ tin sau blocklist → mở rộng time window (5h → 12h → 24h...) hoặc giảm số bài
4. Sau khi push HTML, update state file (giữ rolling 7-day window)

Không có tin nào lặp lại trong vòng 2 ngày.

### 🎨 Giao diện

- **2 cột trên desktop** (≥ 1000px), stack 1 cột trên mobile
- **Dark mode toggle** ở góc phải: ☀️ Light · 💻 System · 🌙 Dark (lưu lựa chọn vào localStorage)
- **Color-coded section**: Red (Japan) · Green (JP Tech) · Blue (Global)
- **Impact badges** cho mục C: 🔴 HIGH / 🟠 MEDIUM / 🟡 LOW

---

## 🎯 Tần suất & giới hạn

| Mục                | Chi tiết                                                     |
| ------------------ | ------------------------------------------------------------ |
| **Tần suất**       | Mỗi 5 giờ từ 00:00 JST (00, 05, 10, 15, 20)                  |
| **Số runs/ngày**   | 5 lần                                                        |
| **Plan đang dùng** | Claude **Max** (15 runs/ngày — dùng 5/15, còn dư cho Routine khác) |
| **Token estimate** | ~15-25K output tokens/run × 5 runs = ~75-125K tokens/ngày    |

Tham khảo các plan khác: Pro 5 runs/ngày (vừa đủ lịch này, không dư), Team/Enterprise 25 runs/ngày.

---

## ⚠️ Lưu ý quan trọng trước khi bắt đầu

### Tần suất "mỗi 5 tiếng"

UI Routines chỉ có preset hourly/daily/weekdays/weekly. Để set "mỗi 5 tiếng từ 00:00":

1. Tạo Routine với preset daily trước
2. Dùng CLI `/schedule update` đổi sang cron: `0 0,5,10,15,20 * * *`

Minimum interval là 1 giờ.

### Timezone

Phải đặt account timezone = **Asia/Tokyo (UTC+9)** trong claude.ai → Settings → General để cron chạy đúng giờ JST.

---

## 🛠️ Bước 1 — Chuẩn bị hạ tầng

### 1.1. Tạo GitHub repository

```bash
gh repo create daily-news-digest --private --description "Daily JP+Tech digest for N2+ SE learner"
cd daily-news-digest
mkdir -p news state
```

### 1.2. Commit template + prompt

```bash
# Copy các file trong bộ này vào repo
cp /path/to/routine/news_template.html .
cp /path/to/routine/ROUTINE_PROMPT.md .

# Tạo state file ban đầu (empty runs array, routine sẽ populate)
cat > state/last_run_urls.json <<'EOF'
{
  "last_run_at": null,
  "runs": []
}
EOF

git add .
git commit -m "init: routine template and prompt"
git push origin main
```

### 1.3. GitHub Pages (hiện tại: **không bật**)

Repo đang **private** trên GitHub Free — plan không hỗ trợ Pages cho private repo. Cách xem HTML hiện tại:

- Mở link GitHub code view (Slack sẽ gửi link này) → bấm **Raw** → save HTML về → mở local browser
- Hoặc `git clone` + mở file `news/YYYY-MM-DD_HH.html` trực tiếp
- Nếu muốn Pages: upgrade GitHub Pro (~$4/mo), hoặc đổi repo sang public

---

## 🔌 Bước 2 — Connect dịch vụ

### 2.1. Cài Claude GitHub App

Vào claude.ai/code → Settings → GitHub → install app vào repo `daily-news-digest`.

### 2.2. Connect Slack

claude.ai → Settings → Connectors → Add Slack. OAuth vào workspace của bạn. Cần scope `chat:write`, `im:write`.

### 2.3. Kiểm tra

claude.ai/code/routines → đảm bảo GitHub + Slack xuất hiện trong available connectors.

---

## 🚀 Bước 3 — Tạo Routine

### Qua web UI (khuyến nghị lần đầu)

1. https://claude.ai/code/routines → **New routine**
2. Điền form:

| Field                                | Giá trị                                   |
| ------------------------------------ | ----------------------------------------- |
| **Name**                             | `デイリーダイジェスト — 5h cadence`       |
| **Prompt**                           | Copy toàn bộ nội dung `ROUTINE_PROMPT.md` |
| **Model**                            | Claude Opus 4.7 (recommended for quality) |
| **Repositories**                     | `<username>/daily-news-digest`             |
| **Allow unrestricted branch pushes** | ❌ Tắt                                     |
| **Environment**                      | Default                                   |
| **Trigger**                          | Scheduled → Daily (sẽ đổi sau)            |
| **Connectors**                       | ✅ Slack, ✅ GitHub                         |

3. Click **Create**

### Qua CLI

```bash
claude
/schedule daily デイリーダイジェスト at 00:00
```

---

## 🕐 Bước 4 — Đổi sang cron 5h

```bash
claude
/schedule list
# Copy routine ID
/schedule update <routine-id>
```

Khi prompt hỏi về schedule:

```
Custom cron: 0 0,5,10,15,20 * * *
```

---

## ✅ Bước 5 — Test run

1. Routine detail page → **Run now**
2. Đợi 2–5 phút (11 bài, agents cần fetch nhiều source + check blocklist)
3. Kiểm tra:
   - [ ] File `news/YYYY-MM-DD_HH.html` được commit
   - [ ] File có đủ 3 section: 5 + 3 + 3 = 11 bài
   - [ ] Layout JP có đủ: tin JP + dịch VN + vocab + grammar
   - [ ] Layout EN có đủ: tin EN + impact badge + dịch VN + impact note + terminology
   - [ ] Dark mode toggle ở góc phải hoạt động (Light/System/Dark)
   - [ ] Slack DM nhận được với tất cả 11 tiêu đề + link
   - [ ] `state/last_run_urls.json` được update với 11 URL + titles mới
   - [ ] **Chạy Routine lần 2 (Run now) sau 5 phút → kiểm tra không có tin trùng**

### Các lỗi hay gặp

| Triệu chứng              | Xử lý                                                        |
| ------------------------ | ------------------------------------------------------------ |
| Mục B thiếu bài          | Mở rộng search tag trên Zenn/Qiita (thêm `web`, `javascript`) |
| Mục C ít tin high-impact | Có thể giảm threshold, chấp nhận nhiều medium-impact         |
| Slack message quá dài    | Giảm số tiêu đề hiển thị xuống 2-3 đầu mỗi section           |
| Dịch JP → VN cứng        | Chỉnh prompt — thêm hướng dẫn "không dịch word-by-word"      |
| X post không crawl được  | Dùng web_search `site:x.com @account` thay vì fetch trực tiếp |

---

## 📊 Monitoring

- Usage: https://claude.ai/settings/usage
- Routine runs: https://claude.ai/code/routines
- Nếu hết quota → bật **Extra usage** trong Settings → Billing

---

## 🔧 Bảo trì

### Thay đổi nguồn / tiêu chí

Edit `ROUTINE_PROMPT.md` trong repo → copy sang Routine prompt qua web UI hoặc `/schedule update`.

### Pause tạm thời

Routine detail page → toggle **Repeats** off.

### Xem lịch sử output

- Branch `claude/news-*` trong GitHub repo: https://github.com/cuongnh0609/daily-news-digest/branches
- File HTML: `news/YYYY-MM-DD_HH.html` trong mỗi branch → bấm Raw để tải
- Session log: claude.ai/code sessions

---

## 📂 Cấu trúc repo khuyến nghị

```
daily-news-digest/
├── README.md
├── CLAUDE.md                  # Guide cho Claude Code
├── ROUTINE_PROMPT.md          # Source of truth cho prompt
├── news_template.html         # Template để routine dùng
├── news/
│   ├── 2026-04-23_00.html
│   ├── 2026-04-23_05.html
│   └── ...
├── state/
│   └── last_run_urls.json     # Anti-duplicate state (rolling 7-day)
└── .gitignore
```

---

## 🔗 Tài liệu tham khảo

- [Claude Code Routines](https://code.claude.com/docs/en/routines)
- [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)
- [MCP connectors](https://code.claude.com/docs/en/mcp)

---

## 💡 Gợi ý cải tiến

- **Weekly digest**: Routine riêng chạy Chủ nhật, tổng hợp best-of-week từ 35 file HTML
- **Anki deck export**: Sinh kèm `.apkg` file với 50-70 flashcard từ vocab + grammar
- **PDF export**: Dùng Puppeteer/wkhtmltopdf để tạo version in offline
- **Dark mode**: Thêm `@media (prefers-color-scheme: dark)` vào CSS
- **Tag filter**: Thêm filter theo topic (AI/Cloud/K8s/Web) cho người đọc lướt

---

## 🎓 Về setup học tập

- Mục A giúp bạn **đọc tin tức JP cấp N2+** → prep cho 読解 test
- Mục B giúp bạn **biết từ vựng IT tiếng Nhật** thực dụng, rất hữu ích khi làm team Nhật hoặc đọc doc Nhật
- Mục C giúp bạn **giữ chuyên môn** + học cách diễn đạt khái niệm tech trong EN. Impact badge giúp lọc tin quan trọng.

Sau 1-2 tuần sử dụng, bạn có thể review lại các file HTML và xuất flashcard các từ vựng đã xuất hiện ≥ 3 lần → từ cao tần suất.