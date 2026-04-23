# 🇯🇵 デイリーダイジェスト — Setup Guide (Claude Code Routine v3)

Hướng dẫn tạo Routine tự động sinh bản tin tổng hợp mỗi 5 giờ cho **SE / Cloud Engineer đang học tiếng Nhật JLPT N2+**.

**Output mỗi lần chạy:** File HTML 11 bài chia 3 mục (5 + 3 + 3), layout 2 cột adaptive theo ngôn ngữ, dark mode toggle, tự động chống trùng với các lần chạy trước.

---

## 📦 Gói file

| File                                        | Mục đích                                             |
| ------------------------------------------- | ---------------------------------------------------- |
| `README.md`                                 | File này — setup guide                               |
| `ROUTINE_PROMPT.md`                         | Prompt v3 — truyền vào `claude --print` qua wrapper  |
| `news_template.html`                        | Template HTML 2 cột (hỗ trợ cả layout JP và EN)      |
| `scripts/run_digest.sh`                     | Wrapper cron chạy `claude` headless + git pull/push  |
| `scripts/notify_email.sh`                   | Gửi email qua macOS Mail.app (osascript)             |
| `scripts/com.cuongnh.daily-news-digest.plist` | launchd plist — copy vào `~/Library/LaunchAgents/` |
| `CLAUDE.md`                                 | Guide cho Claude Code khi edit repo này              |

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

| Mục                    | Chi tiết                                                     |
| ---------------------- | ------------------------------------------------------------ |
| **Tần suất**           | Mỗi 5 giờ từ 00:00 JST (00, 05, 10, 15, 20)                  |
| **Số runs/ngày**       | 5 lần                                                        |
| **Execution model**    | **Local cron (launchd)** — gọi `claude` CLI headless trên máy bạn |
| **Plan đang dùng**     | Claude **Max** — token usage vẫn tính vào quota hàng tháng   |
| **Token estimate**     | ~15-25K output tokens/run × 5 runs = ~75-125K tokens/ngày    |
| **Miss khi máy ngủ**   | ⚠️ launchd **không đánh thức** MacBook — run bị skip nếu máy sleep đúng giờ cron |

---

## ⚠️ Lưu ý quan trọng trước khi bắt đầu

### Execution model

Không dùng Claude Code Routines (server-side). Thay vào đó:

- **launchd plist** trên máy bạn gọi `scripts/run_digest.sh` mỗi 5 tiếng
- Wrapper pull git → gọi `claude --permission-mode bypassPermissions --print "$(cat ROUTINE_PROMPT.md)"`
- Claude CLI crawl → sinh HTML → commit + push branch `claude/news-*` → gửi email qua Mail.app
- State dedup (`state/last_run_urls.json`) vẫn dùng như cũ

### Timezone

launchd đọc **timezone hệ thống của máy** (System Settings → General → Date & Time → Time Zone). Máy đặt `Asia/Tokyo (UTC+9)` → cron chạy đúng giờ JST.

### MacBook sleep

launchd không có cơ chế đánh thức máy. Run tại 00:00/05:00 rất khả năng bị miss nếu máy đang sleep. Chấp nhận miss, hoặc sau này thêm `pmset schedule wake` để đánh thức Mac trước mỗi run.

---

## 🛠️ Bước 1 — Cài đặt phụ thuộc (một lần)

Các công cụ sau phải có trên máy:

```bash
# claude CLI
claude --version         # cần Claude Max login sẵn (~/.claude/ credentials)

# gh CLI (cho git push)
gh auth status            # cần login với account có write access vào repo

# git
git --version
```

Đã check trên máy hiện tại: ✅ `claude` tại `/Users/cuongnh0609/.local/bin/claude` (v2.1.118), ✅ `gh` login `cuongnh0609`.

---

## 🛠️ Bước 2 — Cài launchd plist

```bash
# Copy plist vào LaunchAgents
cp scripts/com.cuongnh.daily-news-digest.plist ~/Library/LaunchAgents/

# Load vào launchd
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.cuongnh.daily-news-digest.plist

# Xác nhận đã load
launchctl list | grep daily-news-digest
```

Output `launchctl list` nên thấy: `-    0    com.cuongnh.daily-news-digest` (cột giữa 0 = chưa chạy, cột trái `-` = không đang chạy).

### Thay đổi lịch

Edit `scripts/com.cuongnh.daily-news-digest.plist` → đổi các `<integer>Hour</integer>` → reload:

```bash
launchctl bootout gui/$UID ~/Library/LaunchAgents/com.cuongnh.daily-news-digest.plist
cp scripts/com.cuongnh.daily-news-digest.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.cuongnh.daily-news-digest.plist
```

### Thay đổi email recipient

Edit key `DIGEST_EMAIL_TO` trong plist → reload như trên.

---

## ✅ Bước 3 — Test run thủ công

Trigger chạy ngay không đợi cron:

```bash
# Cách 1: gọi script trực tiếp (không qua launchd)
./scripts/run_digest.sh
tail -f logs/run_*.log

# Cách 2: trigger qua launchd
launchctl kickstart -k gui/$UID/com.cuongnh.daily-news-digest
tail -f logs/launchd.stderr.log logs/launchd.stdout.log logs/run_*.log
```

Checklist sau khi run xong:

- [ ] File `news/YYYY-MM-DD_HH.html` được commit
- [ ] Branch mới `claude/news-*` được push lên GitHub
- [ ] File có đủ 3 section: 5 + 3 + 3 = 11 bài
- [ ] Layout JP: tin JP + dịch VN + vocab + grammar
- [ ] Layout EN: tin EN + impact badge + dịch VN + impact note + terminology
- [ ] Dark mode toggle hoạt động
- [ ] Email nhận được ở `gian@core-corp.co.jp` (Mail.app sent từ account default)
- [ ] `state/last_run_urls.json` được update
- [ ] **Chạy lần 2 sau 5 phút → kiểm tra không có tin trùng**

### Các lỗi hay gặp

| Triệu chứng                    | Xử lý                                                        |
| ------------------------------ | ------------------------------------------------------------ |
| `claude: command not found` trong log | Edit `scripts/run_digest.sh` → thêm path tới `claude` vào `PATH` |
| `gh` push fail (auth)          | `gh auth login` lại, check `~/.config/gh/hosts.yml`          |
| Email không gửi                | Mail.app chưa configured → mở Mail.app setup account, hoặc đổi `notify_email.sh` sang curl-SMTP |
| Mục B thiếu bài                | Mở rộng search tag trên Zenn/Qiita (thêm `web`, `javascript`) |
| Mục C ít tin high-impact       | Có thể giảm threshold, chấp nhận nhiều medium-impact         |
| Dịch JP → VN cứng              | Chỉnh prompt — thêm hướng dẫn "không dịch word-by-word"      |
| X post không crawl được        | Dùng web_search `site:x.com @account` thay vì fetch trực tiếp |
| launchd không chạy             | `log show --predicate 'subsystem == "com.apple.xpc.launchd"' --last 1h --style compact \| grep daily-news-digest` |

---

## 📊 Monitoring

- **Run logs**: `logs/run_YYYY-MM-DD_HHMMSS.log` (mỗi run 1 file) + `logs/launchd.stdout.log`, `logs/launchd.stderr.log`
- **Token usage**: `claude` session kết thúc sẽ in summary; tổng quota dùng `claude --print "show my usage"` hoặc claude.ai/settings/usage
- **Kiểm tra launchd status**: `launchctl print gui/$UID/com.cuongnh.daily-news-digest`

---

## 🔧 Bảo trì

### Thay đổi nguồn / tiêu chí

Edit `ROUTINE_PROMPT.md` → commit + push. Lần chạy cron tiếp theo sẽ dùng prompt mới (wrapper `git pull` trước khi gọi claude).

### Pause tạm thời

```bash
launchctl bootout gui/$UID ~/Library/LaunchAgents/com.cuongnh.daily-news-digest.plist
```

Resume: `launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.cuongnh.daily-news-digest.plist`

### Xem lịch sử output

- Branch `claude/news-*` trong GitHub repo: https://github.com/cuongnh0609/daily-news-digest/branches
- File HTML: `news/YYYY-MM-DD_HH.html` trong mỗi branch → bấm Raw để tải về, hoặc `git checkout claude/news-...` local
- Run logs: `ls -lt logs/run_*.log | head`

---

## 📂 Cấu trúc repo khuyến nghị

```
daily-news-digest/
├── README.md
├── CLAUDE.md                              # Guide cho Claude Code
├── ROUTINE_PROMPT.md                      # Source of truth cho prompt
├── news_template.html                     # Template HTML
├── scripts/
│   ├── run_digest.sh                      # cron wrapper
│   ├── notify_email.sh                    # email qua Mail.app
│   └── com.cuongnh.daily-news-digest.plist # launchd plist
├── news/
│   ├── 2026-04-23_00.html
│   └── ...
├── state/
│   └── last_run_urls.json                 # Anti-duplicate state (7-day rolling)
├── logs/                                  # .gitignore'd — launchd + run logs
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