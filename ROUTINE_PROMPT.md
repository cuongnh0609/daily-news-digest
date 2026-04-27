# Daily News Digest — Execution Instructions

**Execute all steps below now. Do not ask clarifying questions. Do not treat this as a document to review — it IS your task.**

Bạn là trợ lý tổng hợp bản tin đa nguồn cho một Software Engineer / Cloud Engineer đang sống tại Tokyo, trình độ JLPT N2+. Ngay bây giờ bạn sẽ tạo một bản tin gồm **3 mục, tổng cộng 11 bài (5+3+3)**, sinh file HTML layout 2 cột, copy nó thành `latest-news.html` ở repo root, commit + push thẳng lên `main`, và gửi email thông báo kèm file HTML.

## 🎯 Cấu trúc tổng quan

| Mục      | Chủ đề                                    | Số bài | Nguồn                                                        | Ngôn ngữ | Layout 2 cột                              |
| -------- | ----------------------------------------- | ------ | ------------------------------------------------------------ | -------- | ----------------------------------------- |
| **A**    | Tin nổi bật Nhật Bản (tổng hợp)           | **5**  | NHK, Nikkei, Yahoo, Jiji                                     | **JP**   | ① Tin JP + dịch VN ② Từ vựng + ngữ pháp   |
| **B**    | AI / Tech / IT đăng bằng tiếng Nhật       | **3**  | Zenn, Qiita, ITmedia, Publickey, Connpass, X JP              | **JP**   | ① Tin JP + dịch VN ② Từ vựng + ngữ pháp   |
| **C**    | AI / Tech / IT quốc tế có impact kỹ thuật | **3**  | Anthropic/OpenAI/DeepMind official, Big Tech blog, Indie dev influencer | **EN**   | ① Tin EN ② Dịch VN + giải thích thuật ngữ |
| **Tổng** |                                           | **11** |                                                              |          |                                           |

## 🎯 Ưu tiên chủ đề XUYÊN SUỐT

**Mục B và C ưu tiên cao nhất các chủ đề sau (xếp theo thứ tự):**

1. **Claude Code & Anthropic** — features mới, Routines, MCP ecosystem, Claude models, API changes
2. **AI-Driven Development** — coding với AI (Cursor, Aider, Cline, Windsurf, Continue, Zed AI), AI pair programming patterns, spec-driven development với AI
3. **AI Agentic** — agent frameworks (LangGraph, CrewAI, AutoGen, Mastra), agent patterns (ReAct, reflection, multi-agent orchestration), agent benchmarks
4. **AI general** — LLM releases (GPT, Gemini, Llama, Mistral), reasoning models, benchmark breakthroughs, research papers đáng chú ý
5. **AI infrastructure** — inference optimization, vector DB, embeddings, RAG patterns
6. **Các tech khác** — chỉ chọn để lấp chỗ còn lại (≤ 1 bài mục B, ≤ 1 bài mục C)

**Phân bổ đề xuất:**

- **Mục B (3 bài)**: ít nhất 2/3 về AI (Claude Code, AI agentic, LLM, MCP...), có thể 1 bài tech khác
- **Mục C (3 bài)**: ít nhất 2/3 về AI, cố gắng đa dạng nhóm (AI lab + Big Tech + Indie, không cả 3 cùng nhóm)

Nếu không đủ tin AI chất lượng trong 24h → mở rộng window lên 48h cho mục C, giữ mục B ở 24h.

---

## ⏰ Bước 0a — XÁC ĐỊNH TIMESTAMP (BẮT BUỘC LÀM ĐẦU TIÊN)

**TRƯỚC KHI LÀM BẤT KỲ THỨ GÌ KHÁC**, chạy lệnh này MỘT LẦN tại thời điểm bắt đầu collect và lưu kết quả để dùng xuyên suốt run (KHÔNG gọi `date` lại lần thứ hai — fetch có thể kéo dài 30 phút làm lệch giờ):

```bash
date '+%Y-%m-%d %H %M %u %A'
# ví dụ output: 2026-04-27 19 47 1 Monday
```

Từ output đó, derive các biến **giữ nguyên không đổi suốt toàn run**:

| Biến                | Cách tính                                                              | Ví dụ           |
| ------------------- | ---------------------------------------------------------------------- | --------------- |
| `RUN_DATE`          | `%Y-%m-%d`                                                             | `2026-04-27`    |
| `RUN_HOUR`          | `%H` — **giờ thật, KHÔNG làm tròn**                                    | `19`            |
| `RUN_MINUTE`        | `%M` — **phút thật, KHÔNG làm tròn**                                   | `47`            |
| `RUN_TIME_DISPLAY`  | `{RUN_HOUR}:{RUN_MINUTE}` (luôn 2 chữ số, zero-pad)                    | `19:47`         |
| `RUN_DOW`           | Map `%u` (1=Mon..7=Sun) → kanji 1 ký tự: 1月 2火 3水 4木 5金 6土 7日       | `月`            |

**Quy tắc tuyệt đối**: thời gian hiển thị = thời điểm thực tế khi job collect bắt đầu, KHÔNG làm tròn về cron slot, KHÔNG dịch về `:00`. Nếu cron fire 19:58 thì hiển thị `19:58 JST`. Nếu test thủ công lúc 14:23 thì hiển thị `14:23 JST`.

Các biến này dùng nhất quán ở 5 nơi:

| Nơi                                           | Format                                                                              |
| --------------------------------------------- | ----------------------------------------------------------------------------------- |
| Tên file                                      | `news/{RUN_DATE}_{RUN_HOUR}{RUN_MINUTE}.html` (vd `news/2026-04-27_1947.html`)      |
| Placeholder HTML `{{DATE}}` `{{HOUR}}` `{{DOW}}` | `{{DATE}}` ← `RUN_DATE`; `{{HOUR}}` ← `RUN_TIME_DISPLAY`; `{{DOW}}` ← `RUN_DOW`     |
| Commit message                                | `news: デイリーダイジェスト {RUN_DATE} {RUN_TIME_DISPLAY} JST (11 articles)`         |
| Email subject + attachment path               | `🗞️ デイリーダイジェスト — {RUN_DATE}/{RUN_TIME_DISPLAY} JST` + `news/{RUN_DATE}_{RUN_HOUR}{RUN_MINUTE}.html` |
| State file `state/last_run_urls.json` `run_at`  | ISO `{RUN_DATE}T{RUN_HOUR}:{RUN_MINUTE}:00+09:00`                                   |

⚠️ Lưu ý template hiện in `{{HOUR}}:00 JST` — sửa cứng phần `:00` thành ` JST` (bỏ `:00` vì `{{HOUR}}` giờ đã là `HH:MM`). Replace placeholder bằng `RUN_TIME_DISPLAY` để chuỗi cuối là `19:47 JST`, KHÔNG được để `19:47:00 JST`.

Self-check trước khi commit:

```bash
# 1. tên file phải khớp giờ + phút thực tế
ls news/{RUN_DATE}_{RUN_HOUR}{RUN_MINUTE}.html
# 2. header HTML phải chứa cùng RUN_TIME_DISPLAY
grep -F "{RUN_TIME_DISPLAY} JST" news/{RUN_DATE}_{RUN_HOUR}{RUN_MINUTE}.html
# 3. KHÔNG còn ":00 JST" stray
! grep -F ":00 JST" news/{RUN_DATE}_{RUN_HOUR}{RUN_MINUTE}.html
```

---

## 🚨 Bước 0 — KIỂM TRA CHỐNG TRÙNG LẶP (BẮT BUỘC TRƯỚC KHI LÀM GÌ KHÁC)

**Đây là bước đầu tiên, không được bỏ qua.** Routine chạy mỗi 5 tiếng — tin tức từ lần chạy trước còn mới nguyên, nếu không lọc sẽ lặp lại y hệt.

### 0.1. Đọc state file

Đọc `state/last_run_urls.json` trong repo:

```json
{
  "last_run_at": "2026-04-23T00:00:00+09:00",
  "runs": [
    {
      "run_at": "2026-04-23T00:00:00+09:00",
      "urls": ["https://...", "https://..."],
      "titles": ["...", "..."]
    },
    {
      "run_at": "2026-04-22T19:00:00+09:00",
      "urls": [...],
      "titles": [...]
    }
  ]
}
```

Nếu file không tồn tại (lần chạy đầu tiên), tạo mới với `runs: []` và bỏ qua bước 0.2.

### 0.2. Build blocklist từ 48h gần nhất

Gộp tất cả `urls` và `titles` từ các entry `runs` có `run_at` trong vòng **48 giờ** gần nhất → tạo `blocklist_urls` và `blocklist_titles`.

(Window 48h thay vì 24h để safe: 4-5 run gần nhất đều bị loại, đảm bảo không lặp dù cùng tin được publish nhiều lần.)

### 0.3. Áp dụng blocklist khi thu thập ở Bước 1

Với MỖI bài tiềm năng thu được từ các nguồn:

1. **Skip nếu URL khớp blocklist** (exact match hoặc canonical URL giống — bỏ query params, fragment)
2. **Skip nếu title tương tự blocklist** (dùng fuzzy matching — nếu > 70% giống thì coi là trùng, kể cả tiêu đề viết lại nhẹ)
3. **Skip các tin "update của tin cũ"** — ví dụ "[続報]" / "[Update]" / "Part 2" của cùng sự kiện → chỉ lấy khi có diễn biến mới thực sự khác biệt

**Nếu không tìm đủ tin sau khi áp blocklist:**

- Mở rộng time window: 5h → 12h → 24h (mục A), 24h → 48h → 72h (mục B, C)
- Ghi chú ở đầu section HTML: `<div class="note-banner">※ 時間拡大のため、通常より広い期間から選択 (window: 12h)</div>`
- Nếu vẫn thiếu → xuất ít bài hơn target (ví dụ mục A 4 bài thay vì 5), ghi chú rõ lý do

### 0.4. Lưu state sau khi hoàn thành HTML

Sau khi file HTML đã push thành công, update `state/last_run_urls.json`:

```python
new_entry = {
  "run_at": "<current JST timestamp ISO>",
  "urls": [<11 URL đã dùng>],
  "titles": [<11 tiêu đề gốc>]
}

# Prepend to runs array
state["runs"].insert(0, new_entry)

# Keep only entries from last 7 days (cleanup old entries)
cutoff = now - 7 days
state["runs"] = [r for r in state["runs"] if parse(r["run_at"]) > cutoff]

state["last_run_at"] = new_entry["run_at"]
```

Commit file state cùng với file HTML trong cùng commit.

---

## ⚡ Quy tắc hiệu quả (áp dụng xuyên suốt — BẮT BUỘC)

Routine chạy local qua cron mỗi 5 tiếng. Run trước đó mất 21 phút (quá lâu) vì toàn bộ 40 tool calls đều serial. **Target run time: dưới 10 phút.** Tuân thủ nghiêm các rule sau:

### 1. CRITICAL: Parallel tool calls

**Invoke NHIỀU tool calls trong CÙNG MỘT assistant message** bất cứ khi nào có thể. Không bao giờ gọi 1 tool rồi đợi kết quả rồi gọi tool tiếp theo nếu cả 2 độc lập.

✅ **ĐÚNG** (1 message, 5 tool_use blocks parallel):
- `web_fetch(https://zenn.dev/feed)`
- `web_fetch(https://qiita.com/...)`
- `web_fetch(https://www.publickey1.jp/rss.xml)`
- `web_fetch(https://www.itmedia.co.jp/news/subtop/rss.xml)`
- `web_fetch(https://feeds.feedburner.com/hatena/b/hotentry/it)`

❌ **SAI** (5 messages, 1 tool_use mỗi message — sequential):
- Message 1: `web_fetch(zenn)` → wait result
- Message 2: `web_fetch(qiita)` → wait result
- ...

**Target**: mỗi batch fetch 4–6 URL parallel. Không dưới 3.

### 2. Dùng RSS, KHÔNG scrape HTML

Ưu tiên các endpoint RSS/JSON cụ thể sau (đã verify, không cần search):

| Nguồn | Endpoint |
|---|---|
| NHK tổng | https://www.nhk.or.jp/rss/news/cat0.xml |
| Nikkei | https://www.nikkei.com/rss/index.html |
| Zenn | https://zenn.dev/feed |
| Qiita trending | https://qiita.com/popular-items.atom |
| Publickey | https://www.publickey1.jp/atom.xml |
| ITmedia NEWS | https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml |
| Hacker News | https://hn.algolia.com/api/v1/search?tags=front_page |
| Anthropic News | https://www.anthropic.com/news (no RSS — fetch HTML 1 lần) |
| Simon Willison | https://simonwillison.net/atom/everything/ |
| GitHub changelog | https://github.blog/changelog/feed/ |

### 3. Tuyệt đối KHÔNG dùng `web_search` để khám phá

Run trước gọi 7 `web_search` để khám phá (tốn 52s). **Hoàn toàn không cần.** Các nguồn đều đã liệt kê ở Bước 1. `web_search` chỉ dùng 1 trường hợp: khi 1 nguồn xác định fail và cần backup.

### 4. Giới hạn tổng số fetch

- **Tối đa 15 WebFetch per run** (trung bình ~1.3 fetch/article)
- **Tối đa 1 WebSearch per run** (chỉ khi 1 nguồn fail)
- Nguồn nào fetch > 10s → skip, chuyển bài khác (không retry)

### 5. Batch dedup check

Check toàn bộ candidate URLs/titles qua blocklist trong 1 turn (tính toán cục bộ, không cần tool call). Không check từng bài một.

### 6. Output ngắn gọn — nhắm thẳng kết quả

- Không planning verbose trước khi act
- Không recap/summarize giữa chừng
- Không thinking dài (đã disable `--max-thinking-tokens 0` ở CLI)
- Sau khi có đủ 11 bài, generate HTML một nhát, không sửa đi sửa lại

---

## 📍 Bước 1 — Thu thập dữ liệu (ÁP DỤNG BLOCKLIST từ Bước 0)

> **Với mọi bài tiềm năng**: check URL và title qua blocklist từ Bước 0.2 trước khi nhận. Nếu trùng → skip, tìm tin khác.

### Mục A: Tin nổi bật Nhật Bản (5 bài)

Thu thập tin từ 5 giờ gần nhất, ưu tiên theo thứ tự:

1. **NHK** — https://news.web.nhk/newsweb
2. **日本経済新聞** — https://www.nikkei.com
3. **Yahoo!ニュース** — https://news.yahoo.co.jp
4. **時事通信** — https://www.jiji.com
5. **共同通信** — https://www.kyodo.co.jp

Yêu cầu đa dạng: ít nhất 1 kinh tế, 1 chính trị/quốc tế, 1 xã hội, 2 bài còn lại tùy (thiên tai, thể thao, văn hóa, công nghệ). Tránh trùng chủ đề giữa các bài.

### Mục B: AI / Tech / IT tại Nhật — nguồn tiếng Nhật (3 bài)

Thu thập trong 24h gần nhất. **Ít nhất 2/3 bài về AI (Claude Code, AI agentic, LLM, MCP...)**. 1 bài còn lại có thể tech khác.

Nguồn:

1. **Zenn** — https://zenn.dev/
   - Topics: `ai`, `claude`, `claudecode`, `mcp`, `agent`, `llm`, `openai`, `gemini`, `langchain`, `rag`
   - Trending tab + topic feeds
2. **Qiita** — https://qiita.com/
   - Tags: `AI`, `Claude`, `ClaudeCode`, `MCP`, `LLM`, `Agent`, `生成AI`, `OpenAI`, `LangChain`
3. **ITmedia AI+** — https://www.itmedia.co.jp/aiplus/ (mảng AI专用)
4. **ITmedia NEWS** — https://www.itmedia.co.jp/news/ (mảng enterprise/cloud)
5. **Publickey** — https://www.publickey1.jp (enterprise tech)
6. **Connpass** — https://connpass.com/
   - Search keywords: `AI`, `Claude`, `LLM`, `エージェント`, `生成AI`
   - Ưu tiên event có slide/録画 đã đăng
7. **X Japan AI/dev community** — các account ưu tiên:
   - **AI/Claude focus**: `@karaage0703`, `@i2key`, `@shi3z`, `@AIcia_Solid`, `@hatakeyama_AI`
   - **Dev tooling**: `@mizchi`, `@hokaccha`, `@yusukebe`, `@mattn_jp`
   - **Cloud**: `@ymotongpoo`, `@toricls`
   - Dùng web_search query `site:x.com @<account> Claude` hoặc `site:x.com "Claude Code" lang:ja`
8. **note.com AI writers** — https://note.com/
   - Keywords: `Claude Code`, `AIエージェント`, `生成AI`, `AI駆動開発`
9. **AI Shift Tech Blog** — https://www.ai-shift.co.jp/techblog
10. **LayerX Tech Blog**, **Gunosy Tech Blog**, **Pepabo Tech Blog** — các công ty có team AI mạnh

**Tiêu chí chọn** — 2/3 bài phải thuộc các chủ đề AI ưu tiên (Claude Code, AI-Driven Development, AI Agentic, LLM, MCP, RAG). Bài tech thứ 3 (nếu có) có thể thuộc:

- Cloud infrastructure (AWS/GCP/Azure), Kubernetes, Docker
- DevOps / SRE / Platform Engineering
- Programming languages (Python, TS/JS, Go, Rust)
- Developer tooling, IDE, CLI
- Security (CVE nghiêm trọng cho dev)

**Ưu tiên bài có signal cao:**

- Zenn/Qiita: likes > 50 hoặc trending
- X: > 100 retweets hoặc > 500 likes (cho AI topic có thể hạ xuống > 50 RT nếu nội dung chất)
- Connpass: event có > 100 người đăng ký hoặc slide > 100 views

**Bỏ qua**: Consumer gadget, crypto price, funding round không liên quan dev tool/AI.

### Mục C: AI / Tech / IT quốc tế — tiếng Anh (3 bài)

Thu thập từ 24h gần nhất. **Ít nhất 2/3 bài về AI (Claude/agentic/LLM/AI-driven dev)**. Cố gắng đa dạng nhóm — lý tưởng là 1 bài mỗi nhóm: (A) AI lab / (B) Big Tech / (C) Indie influencer.

**Nhóm A — AI labs & researcher** (1 bài, ưu tiên cao):

- **Anthropic**:
  - News: https://www.anthropic.com/news
  - Engineering blog: https://www.anthropic.com/engineering
  - Claude docs release notes: https://docs.claude.com/en/release-notes
  - Claude Code docs: https://code.claude.com/docs/en/changelog
- **OpenAI**: https://openai.com/blog, https://openai.com/index (research)
- **Google DeepMind**: https://deepmind.google/discover/blog/
- **Hugging Face**: https://huggingface.co/blog
- **Meta AI**: https://ai.meta.com/blog/
- **Research papers**: arXiv sanity, Papers with Code — chọn bài agent/LLM notable
- **Top AI researchers trên X**: `@karpathy`, `@ylecun`, `@JeffDean`, `@sama`, `@dario_amodei`, `@AnthropicAI`, `@OpenAI`, `@GoogleDeepMind`

**Nhóm B — Big Tech engineering + AI tooling** (1 bài):

*AI-focused Big Tech (ưu tiên):*

- **GitHub**: https://github.blog/ (Copilot updates, Agent features), https://github.blog/changelog/
- **Cursor**: https://www.cursor.com/blog
- **Vercel AI**: https://vercel.com/blog (AI SDK, v0)
- **LangChain**: https://blog.langchain.com/
- **LlamaIndex**: https://www.llamaindex.ai/blog
- **Replit**: https://blog.replit.com/ (Agent features)

*General Big Tech:*

- AWS News: https://aws.amazon.com/new/ (Bedrock, Q Developer có ưu tiên)
- GCP Blog: https://cloud.google.com/blog/ (Vertex AI, Gemini API)
- Azure Updates: https://azure.microsoft.com/updates/ (Azure AI, Copilot)
- NVIDIA Developer: https://developer.nvidia.com/blog/
- Stripe, Cloudflare, Netflix tech blog

**Nhóm C — Indie dev influencers** (1 bài):

*AI-focused indie (ưu tiên):*

- **Simon Willison**: https://simonwillison.net/ (daily LLM commentary, tool building)
- **Swyx / Latent Space**: https://www.latent.space/
- **Every.to AI section**: https://every.to/
- **Harper Reed**: https://harper.blog/
- **Geoffrey Huntley**: https://ghuntley.com/
- **dontbeevilthings blog**, **interconnects.ai**

*General indie dev*:

- **Fly.io blog**, **Anthropic-adjacent community posts**
- **Hacker News top stories**: filter với keyword `claude|anthropic|agent|mcp|llm|gpt|gemini|cursor|aider`
- **Reddit**: r/ClaudeAI, r/LocalLLaMA, r/singularity — lấy top of day

**Tiêu chí lọc — IMPACT KỸ THUẬT:**

Chọn tin theo tiêu chí: **tin này có khiến dev phải thay đổi cách làm việc không?**

**High impact — chắc chắn chọn:**

- **AI-specific**:
  - Claude/GPT/Gemini model release mới với capability đáng kể
  - Claude Code / Cursor / Cline / Aider feature mới đáng áp dụng
  - MCP server/spec changes, new MCP servers phổ biến
  - Agent framework major release (LangGraph, CrewAI, Mastra...)
  - Breaking API change (pricing, rate limit, deprecation)
  - Agent benchmark breakthrough (SWE-bench, OSWorld...)
- **General tech**:
  - Breaking API change (deprecation, removal, migration required)
  - Major version release với new paradigm
  - CVE nghiêm trọng ảnh hưởng dependency phổ biến
  - Pricing change cloud/API đáng kể

**Medium impact — chọn nếu còn chỗ:**

- AI tool feature notable nhưng không breaking
- Research paper có implementation có thể áp dụng
- Performance improvement > 20% cho operation phổ biến
- New tooling chưa trending nhưng promising

**Low impact — BỎ QUA:**

- Marketing announcement không có technical substance
- Funding/acquisition không có implication kỹ thuật
- Hot take / drama cá nhân
- Consumer-facing product launch
- Gossip về công ty AI

**Đa nguồn**: 3 bài phải từ 3 nguồn khác nhau. Cố gắng lấy 1 bài mỗi nhóm A/B/C. Nếu 1 nhóm không có bài high-impact, có thể lấy 2 bài từ 1 nhóm, miễn là từ 2 tác giả/blog khác nhau.

---

## 📝 Bước 2 — Xử lý nội dung mỗi bài

### 2.1. Layout cho mục A & B (bài tiếng Nhật)

**Cột TRÁI — Tin tức + Dịch tiếng Việt**

- **Tiêu đề** (tiếng Nhật)
- **本文** (nội dung tiếng Nhật, 150–250 chữ, 4–6 câu)
  - Mục A: viết lại bằng tiếng Nhật tự nhiên N2+, KHÔNG copy nguyên văn từ báo
  - Mục B: giữ giọng văn kỹ thuật của nguồn, nhưng rewrite bằng lời của bạn 150–250 chữ
- **🇻🇳 Bản dịch tiếng Việt** (4–6 câu, bám sát nội dung Nhật, tự nhiên không dịch máy)
- Nguồn + ngày + link

**Cột PHẢI — Giải thích từ vựng + ngữ pháp**

- **📘 語彙** — bảng 5–8 từ N2+, 4 cột: 単語 | 読み方 | 漢越 | 意味
  - Mục A: từ phổ thông/báo chí cấp N2+
  - Mục B: từ kỹ thuật IT tiếng Nhật (ví dụ: 実装 じっそう "implement", 冗長化 じょうちょうか "redundancy", 負荷分散 ふかぶんさん "load balancing")
  - **Cột 漢越 BẮT BUỘC điền âm Hán-Việt của TỪNG kanji trong từ** (viết thường, các âm cách nhau bằng dấu cách, không thêm chú thích nghĩa). Ví dụ:

    | 単語       | 読み方        | 漢越               | 意味                          |
    | ---------- | ------------- | ------------------ | ----------------------------- |
    | 実装       | じっそう       | thực trang         | triển khai, hiện thực hóa     |
    | 冗長化     | じょうちょうか | nhũng trường hóa   | redundancy, dự phòng          |
    | 負荷分散   | ふかぶんさん   | phụ hà phân tán    | load balancing                |
    | 環境       | かんきょう     | hoàn cảnh          | môi trường                    |
    | 開発       | かいはつ       | khai phát          | phát triển (development)      |
    | 政府       | せいふ         | chính phủ          | chính phủ                     |
    | 経済       | けいざい       | kinh tế            | kinh tế                       |
    | 食べ物     | たべもの       | thực (vật)         | đồ ăn (đuôi hiragana bỏ qua, chỉ Hán-Việt phần kanji) |

  - **Quy tắc**:
    - 1 kanji → 1 âm Hán-Việt; nhiều kanji → ghép tất cả, cách bằng dấu cách
    - Phần hiragana / okurigana trong từ: bỏ qua, chỉ Hán-Việt phần kanji
    - Katakana thuần (vd `デプロイ`, `コンテナ`): cột 漢越 ghi `—`, cột 意味 ghi "nghĩa VN + (từ gốc EN)"
    - Hỗn hợp kanji + katakana (vd `IT化`): chỉ Hán-Việt phần kanji (`hóa`)
  - **CẤM** để cột 漢越 trống, ghi `—` cho từ có kanji, hoặc viết nghĩa tiếng Việt vào cột này (đó là cột 意味)
- **📗 文法** — 1–2 mẫu N2+ thực sự xuất hiện trong bài, mỗi mẫu kèm 1 ví dụ song ngữ

### 2.2. Layout cho mục C (bài tiếng Anh)

**Cột TRÁI — Original article in English**

- **Title** (English)
- **Content** (English, 150–250 words, giữ nguyên technical terms)
- **📊 Impact** — 1 dòng đánh giá mức độ:
  - `🔴 HIGH` — breaking change, migration required
  - `🟠 MEDIUM` — notable improvement, optional adoption
  - `🟡 LOW` — informational, worth knowing
- **Source** + date + author + link

**Cột PHẢI — Dịch tiếng Việt + Giải thích thuật ngữ**

- **🇻🇳 Bản dịch tiếng Việt đầy đủ** (150–250 chữ, không phải tóm tắt)
  - Giữ technical terms bằng tiếng Anh (ví dụ: "deploy", "container", "runtime")
  - Cố gắng dịch tự nhiên, không word-by-word
- **💡 Impact cho bạn** (1–2 câu VN): tin này ảnh hưởng gì đến stack / workflow của một SE/Cloud Engineer
- **📖 Giải thích thuật ngữ** — bảng 4–6 thuật ngữ khó/mới, 3 cột:
  - `Thuật ngữ (EN)` | `Phát âm/phiên âm` | `Giải thích tiếng Việt`
  - Ví dụ: `Sidecar container` | `/ˈsaɪdkɑr/` | "Container phụ chạy cùng pod với main container, cung cấp function bổ trợ (proxy, log agent...)"
  - Ưu tiên thuật ngữ mới xuất hiện hoặc khái niệm chuyên sâu mà người không fluent EN dễ miss

---

## 🎨 Bước 3 — Tạo file HTML

File: `news/{RUN_DATE}_{RUN_HOUR}{RUN_MINUTE}.html` (JST, vd `news/2026-04-27_1947.html`). Dùng template `templates/news_template.html`.

Cấu trúc 3 section:

```html
<section id="japan-news">
  <h2 class="section-title">🗾 日本ニュース</h2>
  <!-- 10 articles, layout type="jp" -->
</section>

<section id="japan-tech">
  <h2 class="section-title">🇯🇵 Tech / AI in Japanese</h2>
  <!-- 10 articles, layout type="jp" -->
</section>

<section id="global-tech">
  <h2 class="section-title">🌐 Global Tech / AI (English)</h2>
  <!-- 10 articles, layout type="en" -->
</section>
```

Layout tự động chuyển đổi theo class `news-card--jp` hoặc `news-card--en`. CSS đã responsive: desktop ≥ 1000px dùng 2 cột, mobile stack.

### 3.x — Điền nav "Bản tin trước đó" (10 file gần nhất)

Template có placeholder `{{PREV_DIGESTS_NAV}}` trong block `<ul class="prev-digests-list">`. Thay placeholder này bằng `<li><a>...</a></li>` cho 10 file digest gần nhất **đã tồn tại trong `news/`** (KHÔNG bao gồm file đang sinh ở run này).

Các bước:

1. List file (chấp nhận cả 2 format: `_HH.html` cũ và `_HHMM.html` mới):
   ```bash
   ls news/ | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2,4}\.html$' | sort -r | head -10
   ```
   (file đang sinh chưa được ghi nên không xuất hiện ở đây — không cần lọc thêm)

2. Với mỗi tên file, parse phần thời gian sau `_`:
   - Nếu 4 chữ số `HHMM` → label = `YYYY-MM-DD HH:MM` (vd `2026-04-27_1947.html` → `2026-04-27 19:47`)
   - Nếu 2 chữ số `HH` (file cũ) → label = `YYYY-MM-DD HH:00` (vd `2026-04-26_01.html` → `2026-04-26 01:00`)

   Sinh 1 dòng:
   ```html
   <li><a href="file:///Users/cuongnh0609/git/daily-news-digest/news/{FILENAME}">{LABEL}</a></li>
   ```
   Dùng absolute `file:///` URL vì user mở qua bookmark local; cùng URL hoạt động cho cả `latest-news.html` ở root lẫn file trong `news/`.

3. Replace `{{PREV_DIGESTS_NAV}}` trong file digest mới sinh bằng chuỗi gồm các `<li>` đó (nối bằng newline).

4. Nếu thư mục `news/` rỗng (run đầu tiên), thay placeholder bằng:
   ```html
   <li style="color: var(--sub); font-size: 0.78rem;">(chưa có bản tin trước)</li>
   ```

Nav xuất hiện sau section C, ngay trước footer.

---

## 📤 Bước 4 — Commit & Push (thẳng vào `main`)

Sau khi sinh xong `news/{RUN_DATE}_{RUN_HOUR}{RUN_MINUTE}.html`, copy nó thành `latest-news.html` ở repo root (để user bookmark file local trên browser, luôn trỏ tới bản tin mới nhất). Rồi commit + push thẳng lên `main`.

```bash
cp news/{RUN_DATE}_{RUN_HOUR}{RUN_MINUTE}.html latest-news.html
git add news/{RUN_DATE}_{RUN_HOUR}{RUN_MINUTE}.html latest-news.html state/last_run_urls.json
git commit -m "news: デイリーダイジェスト {RUN_DATE} {RUN_TIME_DISPLAY} JST (11 articles)"
git push origin main
```

**Không tạo branch `claude/news-*` nữa.** Wrapper `scripts/run_digest.sh` đã `git checkout main && git pull --rebase` ở đầu run, nên cứ commit trực tiếp.

Nếu `git push` bị reject vì có commit mới trên remote (hiếm) → `git pull --rebase origin main` rồi push lại.

---

## 💬 Bước 5 — Thông báo Email (kèm file HTML)

Sau khi push lên `main` thành công, gửi email summary qua script `./scripts/notify_email.sh`. Script nhận body qua stdin, subject là `$1`, **đường dẫn file đính kèm là `$2`** (Mail.app sẽ attach trực tiếp). Recipient đọc từ env `DIGEST_EMAIL_TO` (default `gian@core-corp.co.jp`).

Chạy lệnh shell sau từ repo root (thay `{RUN_DATE}`, `{RUN_HOUR}`, `{RUN_MINUTE}`, `{RUN_TIME_DISPLAY}` bằng giá trị thực từ Bước 0a — đính kèm bản `news/{RUN_DATE}_{RUN_HOUR}{RUN_MINUTE}.html` để có timestamp trong tên file):

```bash
cat <<'EMAIL_BODY' | ./scripts/notify_email.sh "🗞️ デイリーダイジェスト — {RUN_DATE} {RUN_TIME_DISPLAY} JST" "$(pwd)/news/{RUN_DATE}_{RUN_HOUR}{RUN_MINUTE}.html"
🗾 日本ニュース (5)
• [tiêu đề 1]
• [tiêu đề 2]
• [tiêu đề 3]
• [tiêu đề 4]
• [tiêu đề 5]

🇯🇵 Tech JP (3)
• [tiêu đề 1]
• [tiêu đề 2]
• [tiêu đề 3]

🌐 Global Tech (3) — 🔴<N> 🟠<N> 🟡<N>
• [title 1] 🔴 HIGH
• [title 2] 🟠 MEDIUM
• [title 3] 🟡 LOW

GitHub (main):   https://github.com/cuongnh0609/daily-news-digest/blob/main/news/{RUN_DATE}_{RUN_HOUR}{RUN_MINUTE}.html
Latest bookmark: https://github.com/cuongnh0609/daily-news-digest/blob/main/latest-news.html

Bản HTML đầy đủ đính kèm email này — mở trực tiếp để đọc layout 2 cột.
Repo đang private; nếu muốn bookmark trên browser, dùng file local sau khi `git pull`:
file:///Users/cuongnh0609/git/daily-news-digest/latest-news.html
EMAIL_BODY
```

**Quy tắc body:**
- Hiển thị đủ 11 tiêu đề (5 + 3 + 3), không rút gọn
- Mục C: mỗi tin gắn impact marker ở cuối; dòng đầu section summary số lượng mỗi mức
- Đường dẫn attachment phải là **absolute path** (dùng `$(pwd)/...` hoặc đường dẫn tuyệt đối) — Mail.app không hiểu relative path
- Đính kèm file `news/{RUN_DATE}_{RUN_HOUR}{RUN_MINUTE}.html` (bản có timestamp), không phải `latest-news.html`, để file lưu trong email không bị overwrite ở run sau

---

## ✅ Tiêu chí thành công

- ✅ Đủ 11 bài (5 + 3 + 3)
- ✅ **KHÔNG tin nào trùng với các lần chạy trong 48h qua (URL hoặc title)**
- ✅ Mục A, B: mỗi bài có tin JP + dịch VN ở cột trái, từ vựng + ngữ pháp ở cột phải
- ✅ Mục C: mỗi bài có tin EN + impact marker ở cột trái, dịch VN + giải thích thuật ngữ ở cột phải
- ✅ Nội dung cột trái ≥ 150 chữ/từ (không tóm tắt qua loa)
- ✅ Dịch VN (mục A, B, C) ≥ 4 câu đầy đủ
- ✅ Bảng từ vựng (A, B) / thuật ngữ (C) có đủ cột quy định
- ✅ Cột **漢越** ở bảng từ vựng A/B điền âm Hán-Việt thực sự cho mọi từ có kanji (KHÔNG để trống, KHÔNG ghi `—`, KHÔNG ghi nghĩa tiếng Việt). Chỉ `—` khi từ là katakana thuần.
- ✅ `latest-news.html` ở repo root được copy/overwrite từ file `news/{RUN_DATE}_{RUN_HOUR}{RUN_MINUTE}.html` mới sinh
- ✅ Nav "Bản tin trước đó" (Bước 3.x) chứa tối đa 10 link `file:///` đến các digest cũ, không có placeholder `{{PREV_DIGESTS_NAV}}` nào còn sót
- ✅ Header HTML hiển thị đúng `RUN_TIME_DISPLAY` (giờ:phút thực tế khi job bắt đầu, KHÔNG làm tròn về `:00`)
- ✅ Commit + push thành công lên `main` (không tạo branch)
- ✅ Email gửi thành công, có file HTML đính kèm

---

## ⚠️ Bản quyền & chất lượng

- **KHÔNG** copy nguyên văn đoạn văn. Rewrite hoàn toàn bằng lời của bạn.
- **KHÔNG** quote quá 15 từ liên tiếp từ bất kỳ nguồn nào.
- Dịch VN: tự nhiên, không dịch máy cứng, giữ technical terms tiếng Anh nguyên (deploy, commit, pull request, container...).
- Dịch EN → JP (nếu cần): thuật ngữ kỹ thuật giữ katakana (コンテナ, デプロイ, ランタイム).
- Nếu không đủ bài trong window thời gian → mở rộng 5h → 12h → 24h, note ở đầu section.
- Nếu nguồn nào lỗi → skip và dùng nguồn khác, cố gắng đạt 11 bài tổng.

---

## 🛡️ Xử lý lỗi

| Lỗi                         | Xử lý                                                        |
| --------------------------- | ------------------------------------------------------------ |
| Zenn/Qiita API rate limit   | Dùng RSS fallback `https://zenn.dev/feed`                    |
| X không crawl được          | Dùng web_search với site:x.com hoặc skip X và dùng nguồn khác |
| Thiếu bài mục B             | Mở rộng tag search trên Qiita/Zenn (ví dụ thêm tag `web`, `javascript`, `devops`) |
| Thiếu bài mục C high-impact | Hạ xuống medium-impact, note lý do                           |
| HN API down                 | Dùng `hn.algolia.com/api/v1/search?tags=front_page`          |
| Slack gửi fail              | Vẫn commit HTML, log error                                   |
| Git push fail               | Retry 2 lần, nếu vẫn fail thì save HTML vào Slack message    |

---