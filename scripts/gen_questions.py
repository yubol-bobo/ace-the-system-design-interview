#!/usr/bin/env python3
"""Generate all question detail pages from structured data."""
import os
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "pages" / "arena" / "questions"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{qid}. {title_en} — SD-Guide</title>
  <link rel="stylesheet" href="../../../assets/css/main.css">
</head>
<body>

  <nav class="nav">
    <div class="nav-inner">
      <a class="nav-brand" href="../../../index.html"><span class="nav-brand-logo">SD</span><span>SD-Guide</span></a>
      <ul class="nav-links">
        <li><a href="../../../index.html"><span data-lang="en">Home</span><span data-lang="zh">首页</span></a></li>
        <li><a href="../index.html" class="active"><span data-lang="en">真题 Arena</span><span data-lang="zh">真题竞技场</span></a></li>
        <li><a href="../../guide/index.html"><span data-lang="en">Study Guide</span><span data-lang="zh">学习手册</span></a></li>
        <li><a href="../../resources/index.html"><span data-lang="en">Resources</span><span data-lang="zh">资源</span></a></li>
        <li><a href="../../about/index.html"><span data-lang="en">About</span><span data-lang="zh">关于</span></a></li>
      </ul>
      <div class="nav-tools">
        <button class="icon-btn" id="lang-toggle">中文</button>
        <button class="icon-btn" id="theme-toggle">☀</button>
      </div>
    </div>
  </nav>

  <main class="page-body">
    <div class="container">
      <div class="breadcrumb">
        <a href="../../../index.html"><span data-lang="en">Home</span><span data-lang="zh">首页</span></a>
        <span class="sep">›</span>
        <a href="../index.html"><span data-lang="en">Arena</span><span data-lang="zh">竞技场</span></a>
        <span class="sep">›</span>
        <span>{qid}</span>
      </div>

      <article class="prose wide">
        <div class="question-meta" style="margin-bottom:1rem;">
          <span class="tag company-{company}">{company_label}</span>
          <span class="tag freq-{freq}">{stars} Frequent</span>
          <span class="tag difficulty-{diff}">{diff_label}</span>
          {extra_tags}
        </div>

        <h1>
          <span data-lang="en">{qid} · {title_en}</span>
          <span data-lang="zh">{qid} · {title_zh}</span>
        </h1>

        <div class="callout {company}">
          <h4><span data-lang="en">Verified source</span><span data-lang="zh">经核实出处</span></h4>
          <p>{source_html}</p>
        </div>

        {body}

        <h2><span data-lang="en">Related study-guide topics</span><span data-lang="zh">相关学习手册专题</span></h2>
        <ul>{related}</ul>
      </article>
    </div>
  </main>

  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script src="../../../assets/js/app.js"></script>
</body>
</html>
"""


def render_page(q):
    stars = "★" * q.get("freq", 2)
    diff_label = q.get("diff_label", "Hard")
    extra_tags = "".join(f'<span class="tag">{t}</span>' for t in q.get("extra_tags", []))
    related = "".join(f'<li><a href="../../guide/{r[0]}">{r[1]}</a></li>' for r in q.get("related", []))
    html = HTML_TEMPLATE.format(
        qid=q["qid"],
        title_en=q["title_en"],
        title_zh=q["title_zh"],
        company=q["company"],
        company_label="OpenAI" if q["company"] == "openai" else "Anthropic",
        freq=q.get("freq", 2),
        stars=stars,
        diff=q.get("diff", "hard"),
        diff_label=diff_label,
        extra_tags=extra_tags,
        source_html=q["source_html"],
        body=q["body"],
        related=related,
    )
    out_path = OUTPUT_DIR / q["filename"]
    out_path.write_text(html)
    print(f"✓ {q['filename']}")


# Common body fragments (bilingual)
def section(title_en, title_zh, content_html):
    return f'<h2><span data-lang="en">{title_en}</span><span data-lang="zh">{title_zh}</span></h2>\n{content_html}'


def bi(en, zh):
    """Bilingual inline span."""
    return f'<span data-lang="en">{en}</span><span data-lang="zh">{zh}</span>'


def mermaid(src):
    return f'<div class="mermaid-container"><pre class="mermaid">\n{src}\n</pre></div>'


def callout(kind, title_en, title_zh, body_en, body_zh):
    return (f'<div class="callout {kind}">'
            f'<h4>{bi(title_en, title_zh)}</h4>'
            f'<p>{bi(body_en, body_zh)}</p>'
            f'</div>')


QUESTIONS = []

# ====================================================================
# O2. Webhook Service REST API
# ====================================================================
QUESTIONS.append({
    "qid": "O2", "filename": "o2-webhook-service.html",
    "title_en": "Design a Webhook Service (REST API)",
    "title_zh": "设计 Webhook 服务（REST API）",
    "company": "openai", "freq": 3, "diff": "hard",
    "extra_tags": ["REST", "Caching", "Queue"],
    "source_html": (
        'Original prompt: "System design Webhook service…caching, db design, focus on failure and retry mechanism in message queue. '
        'Implement the REST service with JSON body and query for GET and POST." — '
        '<a href="https://www.teamblind.com" target="_blank" rel="noopener">TeamBlind</a>, 2024-04-10, screening round. Credibility <strong>C</strong>.'
    ),
    "body": (
        section("Requirements clarification", "需求澄清",
                '<p>' + bi(
                    "Unlike O1 (internal platform), this framing wants a <strong>product API</strong>. Make GET/POST resource semantics explicit: resource paths, filtering, pagination. Confirm whether delivery is at-least-once (almost always yes) and the max retry window.",
                    "与 O1 不同，这题把 webhook 当作<strong>产品 API</strong>。要讲清 GET/POST 的资源语义：路径、过滤、分页。确认投递是否 at-least-once（基本都是）与最大重试窗口。") + '</p>') +

        section("High-level architecture", "高层架构",
                '<p>' + bi("Split read path (config lookups, dashboard) from write path (delivery). Cache the read-heavy config layer, but avoid caching delivery results unless a clear hot-read pattern exists.",
                           "读路径（配置查询、仪表盘）与写路径（投递）分离。对读多的 config 层做缓存；除非有明显的热读，否则不要缓存投递结果。") + '</p>' +
                mermaid("""flowchart LR
  U[API Caller] --> G[REST API]
  G --> C[Config Cache]
  C -->|miss| D[(Config DB)]
  G --> Q[Delivery Queue]
  Q --> W[Workers]
  W --> T[Target URL]
  W --> L[(Delivery Log)]""")) +

        section("MVP resource model", "MVP 资源模型",
                '<pre><code>WebhookSubscription(subscription_id, tenant_id, event_type, endpoint_id)\n'
                'WebhookDelivery(delivery_id, subscription_id, event_id, status, last_attempt)\n'
                'WebhookAttempt(attempt_id, delivery_id, status_code, latency_ms, timestamp)</code></pre>') +

        section("API", "API 设计",
                '<pre><code>POST /subscriptions  { event_type, endpoint_id }\n'
                'POST /deliveries     { subscription_id, payload, idempotency_key } → { delivery_id }\n'
                'GET  /deliveries?subscription_id=&status=&cursor=\n'
                'GET  /deliveries/{delivery_id}/attempts</code></pre>') +

        section("How to talk about cache like an engineer", "缓存该怎么讲才像真做过",
                '<ul>'
                f'<li>{bi("<strong>Cache endpoint/subscription config</strong>: read-heavy, cache-aside, write-DB-then-invalidate. Alternative write-through adds latency and is rarely worth it.", "<strong>缓存 endpoint/subscription 配置</strong>：读多，cache-aside，写 DB 后失效缓存。Write-through 方案会增加延迟，不划算。")}</li>'
                f'<li>{bi("<strong>Don&apos;t cache delivery results</strong> except for well-known hot debug pages, and then only with short TTL + singleflight.", "<strong>不要缓存投递结果</strong>，除非明显热读（调试页），且必须加短 TTL + singleflight。")}</li>'
                f'<li>{bi("<strong>Cache stampede mitigation</strong>: random TTL, singleflight, per-key rate limit. Mention these or you&apos;ll be asked.", "<strong>缓存雪崩/击穿</strong>：随机 TTL、singleflight、按 key 限流。主动提及，否则必被追问。")}</li>'
                '</ul>') +

        section("Consistency", "一致性",
                '<ul>'
                f'<li>{bi("Config updates are eventually consistent (cache may be briefly stale). But <em>disable_endpoint</em> must take effect fast — push to workers with a version number.", "配置更新最终一致（缓存可能短暂旧值）。但「禁用 endpoint」必须快速生效——给 worker 推送带版本号的禁用信号。")}</li>'
                f'<li>{bi("Delivery state uses append-only attempt log + materialized view to avoid write amplification.", "delivery 状态用追加式 attempt 日志 + 物化视图，避免写放大。")}</li>'
                '</ul>') +

        section("Common follow-ups", "高频追问",
                '<ol>'
                f'<li>{bi("<strong>Cache invalidation race with concurrent writes?</strong> Version key (<code>etag</code>/<code>updated_at</code>), invalidate after DB write, read-through correction.", "<strong>缓存失效与写竞态？</strong>版本号（<code>etag</code>/<code>updated_at</code>），写后失效，必要时读修正。")}</li>'
                f'<li>{bi("<strong>How do you implement delay queues?</strong> Either a delayed topic or a <code>scheduled_at</code> column with a worker that pulls due items.", "<strong>延迟队列如何实现？</strong>延迟 topic 或 <code>scheduled_at</code> 字段 + worker 拉取到期项。")}</li>'
                f'<li>{bi("<strong>How to paginate the attempts list?</strong> Cursor-based (<code>cursor=last_attempt_id</code>); offset pagination breaks under high write-rate.", "<strong>attempt 分页如何做？</strong>游标分页（<code>cursor=last_attempt_id</code>）；offset 在高写入速率下会错位。")}</li>'
                '</ol>')
    ),
    "related": [
        ("classical/rate-limiter.html", bi("Rate limiter", "限流器")),
        ("distributed/stream-batch.html", bi("Stream processing", "流处理")),
    ],
})

# ====================================================================
# O3. Webhook with External URL + 24h Retry
# ====================================================================
QUESTIONS.append({
    "qid": "O3", "filename": "o3-webhook-platform-24h.html",
    "title_en": "Webhook Platform with External URL Lookup (24h Retry)",
    "title_zh": "依赖外部服务的 Webhook 平台（24h 重试）",
    "company": "openai", "freq": 2, "diff": "hard",
    "extra_tags": ["State Machine", "Circuit Breaker"],
    "source_html": (
        'Original prompt: "implement a webhook platform…create a webhook request. (cxid, json blob). url is queried from serviceB. retry for 24 hours." — '
        '<a href="https://leetcode.com/discuss" target="_blank" rel="noopener">LeetCode</a>, 2024-10-30, screening system design. Credibility <strong>C</strong>.'
    ),
    "body": (
        section("What makes this different from O1/O2", "与 O1/O2 的不同点",
                '<p>' + bi("The URL is <strong>not yours</strong> — it lives in ServiceB. Two risks: (1) which URL version you bind to an event, (2) ServiceB unavailability cascading into your ingest path.",
                           "URL 不在你手上——它在 ServiceB。两大风险：(1) 事件绑定哪一版 URL，(2) ServiceB 不可用向 ingest 路径级联。") + '</p>') +

        section("Key design decisions", "关键设计决策",
                '<ul>'
                f'<li>{bi("<strong>Resolve URL at delivery time, not ingest time.</strong> Tracks ServiceB changes; cost is one extra dependency on the delivery path.", "<strong>在投递时查 URL，而不是 ingest 时固化。</strong>能跟随 ServiceB 变化；代价是投递路径多一次依赖。")}</li>'
                f'<li>{bi("<strong>Short-TTL config cache (1-5 min)</strong> to reduce ServiceB load and absorb jitter. Store <em>resolved_url</em> + <em>serviceb_version</em> in each attempt for traceability.", "<strong>短 TTL 配置缓存（1-5 分钟）</strong>降低 ServiceB 压力、吸收抖动。每次 attempt 记录 <em>resolved_url</em> 与 <em>serviceb_version</em> 以便追溯。")}</li>'
                f'<li>{bi("<strong>Circuit breaker on ServiceB</strong> — if degraded, delay retries, mark events <code>blocked_on_dependency</code>, alert.", "<strong>对 ServiceB 熔断</strong>——降级时延迟重试、将事件标记为 <code>blocked_on_dependency</code>、告警。")}</li>'
                '</ul>') +

        section("Architecture", "架构",
                mermaid("""flowchart LR
  A[Create Webhook Request] --> B[Ingest API]
  B --> Q[Queue]
  Q --> W[Worker]
  W --> S[ServiceB: Get URL]
  W --> T[Deliver HTTP]
  W --> R[Retry until 24h]
  W --> DLQ[(DLQ)]""")) +

        section("Data model (cxid-keyed)", "数据模型（以 cxid 为键）",
                '<pre><code>WebhookRequest(\n'
                '  cxid, request_id PK, payload_ref,\n'
                '  created_at, deadline_at=created_at+24h,\n'
                '  status, resolved_url, serviceb_version\n'
                ')\n'
                'Attempt(attempt_id, request_id, resolved_url, serviceb_version, http_status, ...)</code></pre>'
                '<p>' + bi("<code>deadline_at</code> is a strong constraint: every retry scheduler check must honor it so backlog doesn't cause infinite retries.",
                            "<code>deadline_at</code> 是强约束：所有重试调度必须检查它，避免积压导致无限重试。") + '</p>') +

        section("24-hour retry policy", "24 小时重试策略",
                '<ul>'
                f'<li>{bi("Exponential backoff + jitter; within 24h, you must cover enough attempts: e.g. 1s, 2s, 4s... capped at 10–30 min.", "指数退避 + 抖动；24h 内必须覆盖足够次数：1s, 2s, 4s... 到 10–30 分钟封顶。")}</li>'
                f'<li>{bi("Error classification: DNS/timeout/5xx retry; 4xx (except 429) don&apos;t retry; 429 obey <code>Retry-After</code>.", "错误分类：DNS/超时/5xx 可重试；4xx（除 429）不重试；429 遵守 <code>Retry-After</code>。")}</li>'
                f'<li>{bi("After deadline: DLQ + tenant notification + manual replay button.", "超过 deadline：DLQ + 通知租户 + 手动回放。")}</li>'
                '</ul>') +

        section("Follow-ups", "高频追问",
                '<ol>'
                f'<li>{bi("<strong>What if ServiceB is down?</strong> Worker uses cache + circuit breaker; re-queue with backoff; events marked blocked_on_dependency for capacity protection.", "<strong>ServiceB 挂了怎么办？</strong>Worker 使用缓存 + 熔断；带退避重入队；事件标记为 blocked_on_dependency 以保护容量。")}</li>'
                f'<li>{bi("<strong>Idempotency across cxid?</strong> Unique key is <code>(cxid, request_id)</code>; attempts are append-only.", "<strong>cxid 幂等如何做？</strong>唯一键 <code>(cxid, request_id)</code>；attempts 追加写。")}</li>'
                '</ol>')
    ),
    "related": [
        ("distributed/replication.html", bi("Failure modes", "故障模式")),
        ("classical/rate-limiter.html", bi("Rate limiter", "限流器")),
    ],
})

# ====================================================================
# O4. Design Slack
# ====================================================================
QUESTIONS.append({
    "qid": "O4", "filename": "o4-design-slack.html",
    "title_en": "Design Slack", "title_zh": "设计 Slack",
    "company": "openai", "freq": 3, "diff": "hard",
    "extra_tags": ["WebSocket", "Fan-out", "Chat"],
    "source_html": (
        'Original prompt: "design slack…deliver a MVP in 2 weeks…message delivery scalability/reliability" — '
        '<a href="https://leetcode.com/discuss" target="_blank" rel="noopener">LeetCode</a>, 2024-10-30. '
        'Also reported on Exponent and Glassdoor. Credibility <strong>C</strong>.'
    ),
    "body": (
        section("Framing the MVP correctly", "MVP 砍对范围",
                '<p>' + bi("Two-week MVP means <strong>ruthless scoping</strong>. In-scope: 1:1 &amp; small-group chat, send/receive, fetch history, online push via WebSocket, basic auth. <strong>Out of scope</strong>: search, files, complex permissions, cross-device state sync, read receipts.",
                           "两周 MVP 意味着<strong>果断砍需求</strong>。范围内：1:1 与小群聊、发送/接收、拉历史、WebSocket 在线推送、基础鉴权。<strong>范围外</strong>：搜索、文件、复杂权限、跨设备状态同步、已读回执。") + '</p>') +

        section("Minimum architecture", "最小架构",
                mermaid("""flowchart LR
  C[Client] --> G[Gateway]
  G --> A[Auth]
  G --> M[Message Service]
  M --> D[(Message DB)]
  M --> Q[Fanout Queue]
  Q --> N[Notification/Push]
  N --> C""")) +

        section("Semantics you MUST nail", "必须讲清的语义",
                '<ul>'
                f'<li>{bi("<strong>Delivery guarantee</strong>: at-least-once is standard; client dedups on message_id.", "<strong>投递保证</strong>：at-least-once 是标准；客户端按 message_id 去重。")}</li>'
                f'<li>{bi("<strong>Ordering</strong>: per-channel monotonic <code>seq</code>; no cross-channel ordering.", "<strong>顺序</strong>：每 channel 单调递增 <code>seq</code>；跨 channel 无序。")}</li>'
                f'<li>{bi("<strong>Offline</strong>: persist all messages; on reconnect, pull history since last <code>seq</code> + subscribe to stream.", "<strong>离线</strong>：所有消息持久化；重连时按最后 <code>seq</code> 拉历史 + 订阅流。")}</li>'
                f'<li>{bi("<strong>Multi-device</strong>: one user multiple sessions; server tracks <code>last_read_seq</code> per session.", "<strong>多端</strong>：单用户多 session；服务端记录每 session 的 <code>last_read_seq</code>。")}</li>'
                '</ul>') +

        section("API (MVP)", "API（MVP）",
                '<pre><code>POST /channels/{id}/messages  { client_msg_id, text }\n'
                'GET  /channels/{id}/messages?before=&limit=\n'
                'GET  /ws  (or /events/stream)  — streaming new messages\n'
                '                                heartbeat every 30s, cursor resume on reconnect</code></pre>') +

        section("Data model", "数据模型",
                '<pre><code>Message(channel_id, message_id, sender_id, created_at, payload, seq)\n'
                '-- Index: (channel_id, seq DESC) for pagination\n'
                'Channel(channel_id, type, members, next_seq)</code></pre>') +

        section("Scale &amp; consistency", "扩展与一致性",
                '<ul>'
                f'<li>{bi("<strong>Strict per-channel ordering via single-partition writes</strong> caps throughput. Mitigation: shard by channel_id; use claim-check for attachments.", "<strong>严格每 channel 顺序 = 单分区写</strong>限制吞吐。缓解：按 channel_id 分片；附件用 claim-check 模式。")}</li>'
                f'<li>{bi("<strong>Fanout-on-write</strong> (push to each user inbox) vs <strong>fanout-on-read</strong> (aggregate on read). MVP uses fanout-on-read for small groups; production mixes them for big channels.", "<strong>Fanout-on-write</strong>（推送到每用户 inbox） vs <strong>fanout-on-read</strong>（读时聚合）。MVP 用 fanout-on-read；生产混合策略应对大群。")}</li>'
                '</ul>') +

        callout("warn", "Hot channel / big group", "热频道 / 大群",
                "A 10,000-member channel can cause a fanout storm. Solution: push to online users in real time, offline users pull on reconnect; big channels use a layered topic.",
                "1 万人频道会触发 fanout 风暴。方案：在线用户实时推送，离线用户重连时拉取；大频道用分层 topic。") +

        section("Follow-ups", "追问",
                '<ol>'
                f'<li>{bi("<strong>Exactly-once?</strong> Not in messaging — use client_msg_id dedup.", "<strong>Exactly-once？</strong>IM 不做；用 client_msg_id 去重。")}</li>'
                f'<li>{bi("<strong>Edit/delete?</strong> New event (edit_event) with same message_id; client replays.", "<strong>编辑/撤回？</strong>新事件（edit_event）复用 message_id；客户端重放。")}</li>'
                f'<li>{bi("<strong>Presence?</strong> Heartbeat → short TTL cache; online/offline is eventually consistent.", "<strong>在线状态？</strong>心跳 → 短 TTL 缓存；在线/离线最终一致。")}</li>'
                '</ol>')
    ),
    "related": [
        ("classical/news-feed.html", bi("News feed &amp; fanout", "新闻流与 fanout")),
        ("distributed/partitioning.html", bi("Partitioning", "分区")),
    ],
})

# ====================================================================
# O5. CI/CD like GitHub Actions
# ====================================================================
QUESTIONS.append({
    "qid": "O5", "filename": "o5-cicd-github-actions.html",
    "title_en": "Design a CI/CD System (like GitHub Actions)",
    "title_zh": "设计 CI/CD 系统（类 GitHub Actions）",
    "company": "openai", "freq": 3, "diff": "hard",
    "extra_tags": ["Workflow Engine", "Lease", "Multi-tenant"],
    "source_html": (
        'Original prompt: "design a CI/CD system, pretty similar to Github Actions…focus on high reliability first" — '
        '<a href="https://leetcode.com/discuss" target="_blank" rel="noopener">LeetCode</a>, 2026-02-12 and <a href="https://www.jointaro.com" target="_blank" rel="noopener">Jointaro</a>, 2025-07-31. Credibility <strong>C</strong>.'
    ),
    "body": (
        section("Requirements clarification", "需求澄清",
                '<ul>'
                f'<li>{bi("Triggers: push / PR / cron / manual?", "触发方式：push / PR / cron / manual？")}</li>'
                f'<li>{bi("Job model: workflow → jobs → steps; DAG or linear? (Often expands from linear to DAG.)", "作业模型：workflow → jobs → steps；DAG 还是线性？（常常从线性扩到 DAG）")}</li>'
                f'<li>{bi("Runners: self-hosted or managed? Isolation (container/VM)?", "Runner：自托管还是托管？隔离要求（容器/VM）？")}</li>'
                f'<li>{bi("If control plane dies, do in-flight jobs continue?", "控制面挂了，运行中的 job 是否继续？")}</li>'
                f'<li>{bi("Outputs: logs, artifacts, status webhooks.", "输出：日志、artifact、状态回调 webhook。")}</li>'
                '</ul>') +

        section("Reliability-first design: persistent state machine", "可靠性优先：持久化状态机",
                '<p>' + bi("The core is a <strong>persistent, auditable state machine</strong> for every job/step — so any failure can be replayed and recovered.",
                           "核心是每个 job/step 的<strong>持久化、可审计的状态机</strong>——任何故障都能重放/恢复。") + '</p>' +
                mermaid("""flowchart LR
  U[User/Repo] --> API[CI API]
  API --> DB[(State DB)]
  API --> Q[Job Queue]
  Q --> S[Scheduler]
  S --> R[Runner Fleet]
  R --> L[Log Store]
  R --> A[Artifact Store]
  R --> DB""")) +

        section("API (give just four)", "API（只给 4 个）",
                '<pre><code>POST /repos/{repo}/workflows/{wf}/dispatch\n'
                'GET  /runs/{run_id}                  -- aggregate status\n'
                'GET  /runs/{run_id}/logs             -- paginated / streamed\n'
                'POST /runners/{runner_id}/heartbeat  -- runner capability + lease + health</code></pre>') +

        section("Data model", "数据模型",
                '<pre><code>WorkflowRun(run_id, repo_id, trigger, status, created_at)\n'
                'Job(job_id, run_id, status, requirements, assigned_runner, attempt, lease_id)\n'
                'Step(step_id, job_id, status, started_at, ended_at, exit_code)</code></pre>') +

        section("Scale &amp; isolation", "扩展与隔离",
                '<ul>'
                f'<li>{bi("<strong>Multi-tenant</strong>: org/repo quota; queue partition; separate runner pools.", "<strong>多租户</strong>：org/repo 配额；队列分区；Runner pool 分组。")}</li>'
                f'<li>{bi("<strong>Runner security</strong>: minimum-privilege token, short-lived creds, container/VM sandbox.", "<strong>Runner 安全</strong>：最小权限 token、短期凭证、容器/VM 沙箱。")}</li>'
                f'<li>{bi("<strong>Scheduling</strong>: priority queue (paid/urgent) + fair-share quota.", "<strong>调度</strong>：优先级队列（付费/紧急）+ 配额公平。")}</li>'
                '</ul>') +

        callout("warn", "Common follow-up", "典型追问",
                "“What if the scheduler dies?” — State is in DB; jobs use lease + idempotent claim; after failure, another scheduler reclaims. Two runners claiming the same job is prevented by compare-and-swap on lease_id.",
                "「调度器挂了怎么办？」——状态在 DB；jobs 用 lease + 幂等 claim；故障后重新 claim。两个 runner 争同一 job 用 lease_id 的 CAS 防止。") +

        section("Cost &amp; perf", "成本与性能",
                '<ul>'
                f'<li>{bi("Runner compute dominates cost. Optimize with idle reclamation, warm pool, spot-instance mix with checkpoint tolerance.", "Runner 资源占主成本。优化：空闲回收、预热池、spot 混用 + checkpoint 容忍。")}</li>'
                f'<li>{bi("Log explosion: segmented upload, compression, tiered cold storage after 30 days.", "日志爆炸：分段上传、压缩、30 天后冷存储分层。")}</li>'
                '</ul>')
    ),
    "related": [
        ("distributed/consensus.html", bi("Leases &amp; consensus", "Lease 与共识")),
        ("distributed/partitioning.html", bi("Partitioning", "分区")),
    ],
})

# ====================================================================
# O6. GitHub Actions from Scratch (product angle)
# ====================================================================
QUESTIONS.append({
    "qid": "O6", "filename": "o6-github-actions-scratch.html",
    "title_en": "Design GitHub Actions from Scratch",
    "title_zh": "从零设计 GitHub Actions",
    "company": "openai", "freq": 2, "diff": "hard",
    "extra_tags": ["YAML", "Secrets", "RBAC"],
    "source_html": (
        'Prompt: "System Design: Design GitHub Actions from scratch." — '
        '<a href="https://www.jointaro.com" target="_blank" rel="noopener">Jointaro</a>, 2025-07-31 community report. Credibility <strong>C</strong>.'
    ),
    "body": (
        '<p>' + bi("Use <strong>O5 as the skeleton</strong> and add two productization concerns that signal you understand the real shape of GitHub Actions.",
                   "以 <strong>O5 作为骨架</strong>，增加两块产品化能力，体现你理解真实形态。") + '</p>' +

        section("Extra block 1 — Config parsing &amp; versioning", "加分块 1 — 配置解析与版本化",
                '<ul>'
                f'<li>{bi("Parse <code>.github/workflows/*.yml</code>; schema-validate on commit.", "解析 <code>.github/workflows/*.yml</code>；commit 时 schema 校验。")}</li>'
                f'<li>{bi("Pin to commit SHA for reproducibility; support version rollback.", "按 commit SHA 绑定以可复现；支持版本回滚。")}</li>'
                f'<li>{bi("Reject invalid config before producing a run, so UI shows an actionable error.", "产生 run 之前拒绝非法配置，UI 提示可操作的错误。")}</li>'
                '</ul>') +

        section("Extra block 2 — Event integration &amp; permissions", "加分块 2 — 事件集成与权限",
                '<ul>'
                f'<li>{bi("Ingest repo webhooks (push, PR); idempotent (dedup by delivery_id).", "采集 repo webhook（push/PR）；幂等（按 delivery_id 去重）。")}</li>'
                f'<li>{bi("Per-run permission token: minimum-scope, time-bounded, audience = runner.", "每 run 的权限 token：最小 scope、时限制、受众 = runner。")}</li>'
                f'<li>{bi("<strong>Secret masking</strong> is compulsory — scan runner stdout and log store for any regex match of stored secrets.", "<strong>Secret 脱敏</strong>是强制的——扫描 runner stdout 与日志，匹配已存 secret 的 regex。")}</li>'
                '</ul>') +

        section("Architecture sketch", "架构",
                mermaid("""flowchart LR
  E[Repo Events] --> WH[Webhook Ingest]
  WH --> P[Policy/Permissions]
  P --> API[CI Control Plane]
  API --> Q[Queue] --> R[Runner]
  R --> L[Logs + Secret Masker]""")) +

        callout("warn", "Follow-up they always ask", "必问追问",
                "How do you ensure a secret never leaks into logs? Answer: secret masking layer, minimum-privilege tokens, short-lived creds, audit trail of access.",
                "如何确保 secret 不泄漏到日志？答：脱敏层 + 最小权限 token + 短期凭证 + 访问审计链路。")
    ),
    "related": [
        ("classical/rate-limiter.html", bi("Rate limiting", "限流")),
        ("safety/safety-engineering.html", bi("Safety engineering", "安全工程")),
    ],
})

# ====================================================================
# O7. CI/CD Linear
# ====================================================================
QUESTIONS.append({
    "qid": "O7", "filename": "o7-cicd-linear.html",
    "title_en": "CI/CD with Linear Multi-Step Pipeline",
    "title_zh": "线性多步 CI/CD 流水线",
    "company": "openai", "freq": 2, "diff": "medium",
    "diff_label": "Medium-Hard",
    "extra_tags": ["CDC", "State Machine"],
    "source_html": (
        'Prompt: "System Design — CI/CD…simple linear multi-step flow (not a DAG)…store each step as a DB entry…enqueue next step when previous completes" — '
        '<a href="https://leetcode.com/discuss" target="_blank" rel="noopener">LeetCode</a>, 2025-11-08. Credibility <strong>C</strong>.'
    ),
    "body": (
        '<p>' + bi("This is \"the minimum viable subset of a distributed workflow engine.\" Avoid presenting it as \"just a cron job.\"",
                   "这是「分布式工作流引擎的最小子集」。务必避免「写个 cron 就行」的回答。") + '</p>' +
        section("Architecture — state-driven scheduling", "状态驱动调度",
                mermaid("""flowchart LR
  API[Pipeline API] --> DB[(Step Table)]
  DB --> EVT[Change Stream / CDC]
  EVT --> SCH[Stateless Scheduler]
  SCH --> Q[Task Queue] --> W[Workers]
  W --> DB""")) +
        section("Why CDC is the elegant answer", "为什么 CDC 是优雅答案",
                '<p>' + bi("Workers write step status → CDC emits → scheduler discovers next step → enqueue. Avoids polling overhead while giving low latency, and remains stateless.",
                           "Worker 写 step 状态 → CDC 事件流 → 调度器发现下一步 → 入队。无需轮询，延迟低，且保持无状态。") + '</p>') +
        section("Trade-offs", "权衡",
                '<ul>'
                f'<li>{bi("Polling: simple but expensive &amp; latency-unstable.", "轮询：简单但成本高、延迟不稳。")}</li>'
                f'<li>{bi("Event-driven: better but must handle duplicate events → idempotent consumers.", "事件驱动：更优但必须处理重复事件 → 消费者幂等。")}</li>'
                f'<li>{bi("Serial guarantee: one active step per pipeline (DB row lock or <code>lease_id</code>).", "串行保证：同一 pipeline 任一时刻仅一个 active step（DB 行锁 或 <code>lease_id</code>）。")}</li>'
                '</ul>')
    ),
    "related": [
        ("distributed/stream-batch.html", bi("CDC &amp; stream processing", "CDC 与流处理")),
    ],
})

# ====================================================================
# O8. Search/Recommendation with LLMs
# ====================================================================
QUESTIONS.append({
    "qid": "O8", "filename": "o8-search-recommendation-llm.html",
    "title_en": "Search/Recommendation System with LLMs",
    "title_zh": "融合 LLM 的搜索/推荐系统",
    "company": "openai", "freq": 2, "diff": "hard",
    "extra_tags": ["RAG", "Hybrid Retrieval", "Rerank"],
    "source_html": (
        'Recruiter prompt: "We\'ll explore your experience with search, ranking, retrieval, and how to adapt LLMs to interact with such systems." — '
        '<a href="https://www.teamblind.com" target="_blank" rel="noopener">TeamBlind</a>, 2025-10-22. Credibility <strong>C</strong>.'
    ),
    "body": (
        section("Split into two chains", "拆成两条主链路",
                '<ol>'
                f'<li>{bi("<strong>Online retrieval + ranking</strong>: Query → recall (keyword + vector) → rerank → result page.", "<strong>在线检索与排序</strong>：Query → 召回（keyword + 向量）→ rerank → 结果页。")}</li>'
                f'<li>{bi("<strong>LLM insertion points</strong>: query understanding/rewrite, result summary/conversational explanation, tool-use to trigger secondary retrieval.", "<strong>LLM 插入点</strong>：Query 理解/改写、结果摘要/对话式解释、工具调用触发二次检索。")}</li>'
                '</ol>') +

        section("Reference architecture", "参考架构",
                mermaid("""flowchart LR
  U[User] --> QP[Query Parser]
  QP --> KR[Keyword Search (BM25)]
  QP --> VR[Vector Search (ANN)]
  KR --> M[Merge]
  VR --> M
  M --> RR[Reranker (Cross-Encoder)]
  RR --> LLM[LLM Layer]
  LLM --> U""")) +

        section("Key trade-offs", "核心权衡",
                '<ul>'
                f'<li>{bi("<strong>LLM in recall (query rewrite)</strong>: cheaper downstream; risk of recall bias.", "<strong>LLM 参与召回（Query 改写）</strong>：后续成本低；但有召回偏差风险。")}</li>'
                f'<li>{bi("<strong>LLM in rerank / summarize</strong>: safer but more expensive per-query.", "<strong>LLM 参与 rerank / 摘要</strong>：更稳但每次成本更高。")}</li>'
                f'<li>{bi("<strong>Index update</strong>: real-time writes sacrifice throughput; batch sacrifices freshness.", "<strong>索引更新</strong>：实时写牺牲吞吐；批处理牺牲新鲜度。")}</li>'
                '</ul>') +

        section("Evaluation (dual)", "评估（双轨）",
                '<ul>'
                f'<li>{bi("IR metrics: Recall@K, NDCG@10, MRR.", "IR 指标：Recall@K、NDCG@10、MRR。")}</li>'
                f'<li>{bi("Generation quality: faithfulness, helpfulness, LLM-as-judge + human pairwise.", "生成质量：faithfulness、helpfulness、LLM-as-judge + 人类 pairwise。")}</li>'
                f'<li>{bi("Online: A/B with click, dwell time, satisfaction proxy.", "在线：A/B 测试点击、停留时间、满意度代理指标。")}</li>'
                '</ul>') +

        callout("openai", "Safety lens", "Safety 视角",
                "If safety comes up, reference Anthropic's Constitutional AI as a structured way to layer policy into the LLM step. A moderation pipeline on both the query and the answer is standard.",
                "若被问到安全，可引用 Anthropic 的 Constitutional AI 作为「把策略注入 LLM 步骤」的结构化方法。对 Query 与 Answer 都做 moderation 是标配。")
    ),
    "related": [
        ("llm/rag.html", "RAG deep dive"),
        ("llm/llm-evaluation.html", bi("LLM evaluation", "LLM 评估")),
    ],
})

# ====================================================================
# O9. In-memory database
# ====================================================================
QUESTIONS.append({
    "qid": "O9", "filename": "o9-in-memory-database.html",
    "title_en": "Design an In-Memory Database",
    "title_zh": "设计内存数据库",
    "company": "openai", "freq": 3, "diff": "hard",
    "extra_tags": ["KV", "WAL", "Snapshot"],
    "source_html": (
        'Prompt: "Design an in-memory database." — '
        '<a href="https://igotanoffer.com/" target="_blank" rel="noopener">IGotAnOffer</a> (also Glassdoor, StaffEngPrep, PracHub). Credibility <strong>B / D</strong> (curated + interview-coach).'
    ),
    "body": (
        section("Scope control (critical)", "范围控制（关键）",
                '<p>' + bi("Start with <strong>SET / GET / DEL + TTL + prefix scan</strong>. Evolve to persistence (AOF / snapshot), sharding, replication. Follow-ups may add GROUP BY, ORDER BY.",
                           "从 <strong>SET/GET/DEL + TTL + 前缀扫描</strong>开始。演进：持久化（AOF/snapshot）、分片、复制。追问可加 GROUP BY、ORDER BY。") + '</p>') +

        section("Core architecture", "核心架构",
                mermaid("""flowchart LR
  C[Client] --> API[KV API]
  API --> MEM[(Memtable)]
  API --> WAL[(Write-Ahead Log)]
  MEM --> SNAP[Snapshot]""")) +

        section("API", "API 设计",
                '<pre><code>PUT    /kv/{key}     body { value, ttl_seconds? }\n'
                'GET    /kv/{key}\n'
                'DELETE /kv/{key}\n'
                'GET    /scan?prefix=&amp;limit=&amp;cursor=</code></pre>') +

        section("Internals", "内部实现",
                '<ul>'
                f'<li>{bi("<strong>Sharding</strong>: consistent hash or modulo per shard; RWLock within a shard.", "<strong>分片</strong>：一致性哈希或取模；shard 内 RWLock。")}</li>'
                f'<li>{bi("<strong>TTL</strong>: min-heap or timing wheel; background reaper + lazy delete.", "<strong>TTL</strong>：小根堆或 timing wheel；后台清理 + 懒删。")}</li>'
                f'<li>{bi("<strong>Persistence</strong>: append-only WAL + periodic snapshot; recover = load snapshot + replay WAL.", "<strong>持久化</strong>：追加 WAL + 周期 snapshot；恢复 = 加载 snapshot + 重放 WAL。")}</li>'
                '</ul>') +

        section("Trade-offs", "权衡",
                '<ul>'
                f'<li>{bi("Single leader = simple consistency. Multi-replica needs replication protocol (Raft / quorum), with obvious write-latency cost.", "单主：一致性简单。多副本需要复制协议（Raft / quorum），写延迟代价明显。")}</li>'
                f'<li>{bi("Read-from-replica possible but requires explicit stale-read policy.", "副本读可行但需明确的陈旧读策略。")}</li>'
                '</ul>') +

        callout("tip", "How to level up the answer", "如何把答案做出高度",
                "Mention Redis's actual design choices (single-threaded per shard, AOF+RDB combined, PSYNC for replication) to anchor it in production reality — interviewers love this signal.",
                "提 Redis 的真实选型（每 shard 单线程、AOF+RDB 组合、PSYNC 复制）——这是面试官喜欢的工程现实信号。")
    ),
    "related": [
        ("distributed/storage-engines.html", bi("Storage engines", "存储引擎")),
        ("distributed/replication.html", bi("Replication", "复制")),
    ],
})

# ====================================================================
# O10. Polite Web Crawler
# ====================================================================
QUESTIONS.append({
    "qid": "O10", "filename": "o10-polite-web-crawler.html",
    "title_en": "Fault-Tolerant Polite Web Crawler @ 10M RPS",
    "title_zh": "容错礼貌型网页爬虫（10M RPS）",
    "company": "openai", "freq": 2, "diff": "hard",
    "extra_tags": ["Frontier", "Politeness", "Bloom Filter"],
    "source_html": (
        'Prompt: "Design a fault-tolerant, polite web crawling service that can scale to 10M requests per second." — '
        '<a href="https://igotanoffer.com/" target="_blank" rel="noopener">IGotAnOffer</a>, 2026-04-13. Credibility <strong>D</strong>.'
    ),
    "body": (
        section("Core architecture", "核心架构",
                mermaid("""flowchart LR
  S[Seed URLs] --> F[URL Frontier]
  F --> P[Politeness Scheduler]
  P --> Q[Fetch Queue]
  Q --> W[Crawler Workers]
  W --> D[Parser + Dedup]
  D --> F
  W --> ST[(Content Store)]""")) +

        section("Politeness mechanics", "礼貌机制",
                '<ul>'
                f'<li>{bi("Per-host/per-domain token-bucket rate limit.", "per-host/per-domain 令牌桶限流。")}</li>'
                f'<li>{bi("robots.txt parse &amp; cache (24h TTL).", "robots.txt 解析并缓存（24h TTL）。")}</li>'
                f'<li>{bi("Cap concurrent connections per host (≤ N).", "每 host 并发连接上限（≤ N）。")}</li>'
                '</ul>') +

        section("Dedup at 10M RPS (the hard part)", "10M RPS 下去重（最难点）",
                '<ul>'
                f'<li>{bi("URL canonicalization: normalize scheme/host, sort query params, strip tracking.", "URL 规范化：归一化 scheme/host、排序 query、去追踪参数。")}</li>'
                f'<li>{bi("Bloom filter (approximate) + exact set for hot domains.", "Bloom filter（近似）+ 热域精确集。")}</li>'
                f'<li>{bi("Content dedup via simhash/minhash for near-duplicates (bonus).", "内容去重用 simhash/minhash 检测近似重复（加分）。")}</li>'
                '</ul>') +

        section("Fault tolerance", "容错",
                '<ul>'
                f'<li>{bi("Stateless workers; the queue + scheduler own retry/backoff.", "Worker 无状态；重试/退避由队列与调度器管。")}</li>'
                f'<li>{bi("Idempotent writes keyed on content_hash or canonical_url.", "按 content_hash 或 canonical_url 的幂等写入。")}</li>'
                '</ul>')
    ),
    "related": [
        ("classical/rate-limiter.html", bi("Rate limiter", "限流器")),
        ("distributed/partitioning.html", bi("Partitioning", "分区")),
    ],
})

# ====================================================================
# O11. OpenAI Playground
# ====================================================================
QUESTIONS.append({
    "qid": "O11", "filename": "o11-openai-playground.html",
    "title_en": "Design the OpenAI Playground",
    "title_zh": "设计 OpenAI Playground",
    "company": "openai", "freq": 3, "diff": "hard",
    "extra_tags": ["Product Design", "Streaming", "Versioning"],
    "source_html": (
        'Prompt: "Design the OpenAI Playground." — '
        '<a href="https://www.tryexponent.com/" target="_blank" rel="noopener">Exponent</a> (candidate-verified, 2024–2025). Credibility <strong>B</strong>.'
    ),
    "body": (
        section("Scope clarification", "范围澄清",
                '<ul>'
                f'<li>{bi("Target audience: developers debugging prompts, or end users? (Developers.)", "目标用户：调试 prompt 的开发者，还是终端用户？（开发者）")}</li>'
                f'<li>{bi("Which surfaces: web only, or web + API + SDK?", "覆盖面：仅 Web，还是 Web + API + SDK？")}</li>'
                f'<li>{bi("Multi-turn threads persisted? Sharable? Versioned?", "多轮线程是否持久化？可分享？版本化？")}</li>'
                f'<li>{bi("Cost visibility: token counter per-run?", "成本可见性：每次运行的 token 计数？")}</li>'
                '</ul>') +

        section("Architecture", "架构",
                mermaid("""flowchart LR
  UI[Web UI / SDK] --> GW[API Gateway]
  GW --> AUTH[Auth + Rate Limit]
  GW --> TH[Thread Service]
  GW --> MS[Model Service]
  TH --> DB[(Threads DB)]
  MS --> LLM[LLM Inference]
  MS --> METER[Usage Metering]
  MS --> STREAM[SSE / WebSocket]""")) +

        section("Thread / Message data model", "线程/消息数据模型",
                '<pre><code>Thread(thread_id, user_id, title, model, system_prompt, created_at, updated_at)\n'
                'Message(message_id, thread_id, role, content, parent_id, token_count, model_version)\n'
                'Run(run_id, thread_id, message_id, model, params, status, latency_ms, cost_usd)</code></pre>') +

        section("API", "API",
                '<pre><code>POST /threads                         -&gt; { thread_id }\n'
                'POST /threads/{id}/messages  -&gt; SSE stream of tokens\n'
                'GET  /threads/{id}/messages?cursor=\n'
                'POST /threads/{id}/fork               (for A/B compare)</code></pre>') +

        section("Key engineering topics", "关键工程点",
                '<ul>'
                f'<li>{bi("<strong>Streaming</strong>: SSE per request; reconnect via message_id + token cursor.", "<strong>流式</strong>：SSE per request；按 message_id + token cursor 重连。")}</li>'
                f'<li>{bi("<strong>Versioning</strong>: model version &amp; system prompt pinned per Run for reproducibility.", "<strong>版本化</strong>：模型版本与 system prompt 固化到 Run，保障可复现。")}</li>'
                f'<li>{bi("<strong>Metering</strong>: count tokens twice (local estimate + server truth) to show pre-send budget.", "<strong>计量</strong>：本地估算 + 服务端真实，用于发送前预算显示。")}</li>'
                f'<li>{bi("<strong>Multi-model selector</strong>: unified API, model-specific context-window enforcement.", "<strong>多模型选择器</strong>：统一 API，按模型各自上下文长度校验。")}</li>'
                '</ul>')
    ),
    "related": [
        ("llm/llm-serving.html", bi("LLM serving", "LLM 推理服务")),
        ("llm/agentic-patterns.html", bi("Agent patterns", "Agent 模式")),
    ],
})

# ====================================================================
# O12. ChatGPT @ 100M
# ====================================================================
QUESTIONS.append({
    "qid": "O12", "filename": "o12-chatgpt-100m.html",
    "title_en": "Design ChatGPT for 100M Users",
    "title_zh": "设计承载 1 亿用户的 ChatGPT",
    "company": "openai", "freq": 2, "diff": "hard",
    "extra_tags": ["Scale", "GPU Fleet", "Regional"],
    "source_html": (
        'Prompt: "Design ChatGPT to handle 100M users." — Medium / 1Point3Acres reports (2024–2025). Credibility <strong>C</strong>.'
    ),
    "body": (
        section("Capacity envelope", "容量估算",
                '<ul>'
                f'<li>{bi("100M MAU → ~10M DAU → ~5 msg/user/day = 50M msg/day = ~600 msg/sec avg, ~3–5K/sec peak.", "100M MAU → ~10M DAU → ~5 msg/人/天 = 50M msg/天 = 平均 ~600 msg/秒，峰值 ~3–5K/秒。")}</li>'
                f'<li>{bi("Each msg ≈ 500 tokens in, 500 out → ~600 × 1K × 3600s/h = GPU-hours math needed.", "每条消息 ≈ 500 in + 500 out tokens → ~600 × 1K × 3600s/h = GPU 时级换算。")}</li>'
                '</ul>') +

        section("Architecture", "架构",
                mermaid("""flowchart LR
  U[Users] --> CDN[Edge / CDN]
  CDN --> ALB[Regional LB]
  ALB --> GW[API Gateway]
  GW --> SESS[Session Service]
  SESS --> CONV[(Conversation Store)]
  GW --> ROUTE[Model Router]
  ROUTE --> INF[Inference Cluster]
  INF --> BATCH[Batcher] --> GPU[GPU Fleet]
  GW --> METER[Usage Metering]
  GW --> SAFE[Safety Pipeline]""")) +

        section("Key decisions", "关键决策",
                '<ul>'
                f'<li>{bi("<strong>Regional routing</strong> by user home region (latency + data residency).", "<strong>区域路由</strong>按用户 home region（延迟 + 数据合规）。")}</li>'
                f'<li>{bi("<strong>Session stickiness</strong> to one region; with async replication of conversation metadata.", "<strong>会话黏附</strong>到单区域；对话元数据异步跨区复制。")}</li>'
                f'<li>{bi("<strong>Capacity planning</strong> per GPU family: A100/H100 pools; autoscale on tokens/sec, not CPU.", "<strong>容量规划</strong>分 GPU 家族：A100/H100 池；基于 tokens/sec 而非 CPU 自动扩容。")}</li>'
                f'<li>{bi("<strong>Degraded modes</strong>: when saturated, serve smaller/cheaper model or cached prompt prefixes.", "<strong>降级</strong>：过载时转小/便宜模型或缓存 prefix。")}</li>'
                '</ul>') +

        callout("warn", "Where cost hides", "成本陷阱",
                "$/token dominates, not compute-hours. Answer: batching + KV cache + prompt caching reduce $/token; free/paid tier split by rate limits and model availability.",
                "成本主体是 $/token，而非机器小时。答：batching + KV cache + prompt caching 降 $/token；按限流与模型可用性划分免费/付费等级。")
    ),
    "related": [
        ("llm/llm-serving.html", bi("LLM serving deep dive", "LLM 推理服务")),
        ("classical/rate-limiter.html", bi("Rate limiter", "限流器")),
    ],
})

# ====================================================================
# O13. NSFW / Safety Detection
# ====================================================================
QUESTIONS.append({
    "qid": "O13", "filename": "o13-nsfw-detection.html",
    "title_en": "NSFW / Safety Detection for ChatGPT Outputs",
    "title_zh": "ChatGPT 输出的 NSFW/安全检测",
    "company": "openai", "freq": 2, "diff": "hard",
    "extra_tags": ["Moderation", "Classifier"],
    "source_html": (
        'Prompt: "Design a System to Detect NSFW Content in ChatGPT Outputs." — Jobright, Glassdoor. Credibility <strong>C/D</strong>.'
    ),
    "body": (
        section("What you need to cover", "必须覆盖的要点",
                '<ol>'
                f'<li>{bi("Data collection: sample outputs, red-team prompts, public benchmarks, user reports.", "数据采集：模型输出采样、red-team 提示、公共基准、用户举报。")}</li>'
                f'<li>{bi("Model choice: rule filters (regex/keyword) → ML classifier (fast) → LLM-judge (high quality, expensive).", "模型选择：规则（正则/关键词）→ ML 分类器（快）→ LLM-judge（质量高但成本高）。")}</li>'
                f'<li>{bi("Latency budget: block inline <em>or</em> async-moderate. Inline adds to TTFT.", "延迟预算：同步拦截 <em>or</em> 异步审核。同步会增加 TTFT。")}</li>'
                f'<li>{bi("Feedback loop: label disagreement → retrain; policy updates → new classifier version.", "反馈循环：标签不一致 → 再训练；策略更新 → 分类器新版本。")}</li>'
                '</ol>') +

        section("Architecture", "架构",
                mermaid("""flowchart LR
  LLM[LLM Output] --> RULES[Rule Filter]
  RULES -->|pass| CLS[ML Classifier]
  RULES -->|flag| ACTION
  CLS -->|pass| RET[Return to user]
  CLS -->|uncertain| LJ[LLM Judge]
  LJ --> ACTION[Action: block / rewrite / warn]
  ACTION --> AUDIT[(Audit Log)]
  RET --> SAMPLE[Async Sampler]
  SAMPLE --> TRAIN[Retraining Data]""")) +

        section("Design trade-offs", "设计权衡",
                '<ul>'
                f'<li>{bi("Inline vs async: inline catches before egress (safer) but blocks streaming; async requires downstream correction (edit/delete).", "同步 vs 异步：同步在出口前拦截（更安全）但阻塞流式；异步需要下游修正（编辑/删除）。")}</li>'
                f'<li>{bi("Token-by-token moderation for streaming: chunk-level classifier every K tokens with rollback.", "流式的逐 token 审核：每 K tokens 做 chunk 级分类 + 回滚。")}</li>'
                '</ul>')
    ),
    "related": [
        ("safety/safety-engineering.html", bi("Safety engineering", "安全工程")),
        ("llm/llm-evaluation.html", bi("LLM evaluation", "LLM 评估")),
    ],
})

# ====================================================================
# O14. GPU Credit
# ====================================================================
QUESTIONS.append({
    "qid": "O14", "filename": "o14-gpu-credit-scheduling.html",
    "title_en": "GPU Credit / Quota Scheduling System",
    "title_zh": "GPU 信用/配额调度系统",
    "company": "openai", "freq": 2, "diff": "hard",
    "extra_tags": ["Accounting", "Fairness"],
    "source_html": 'Prompt: "Design a GPU Scheduling System (Credits)." — Glassdoor. Credibility <strong>C</strong>.',
    "body": (
        section("Clarifications", "需求澄清",
                '<ul>'
                f'<li>{bi("Granularity: credits per GPU-second, per token, per request?", "粒度：每 GPU-秒、每 token、每请求？")}</li>'
                f'<li>{bi("Consumption order: oldest first (FIFO by grant date)?", "消费顺序：最旧额度优先（按授予日期 FIFO）？")}</li>'
                f'<li>{bi("Expiration: per grant or per account?", "过期：按批次还是按账户？")}</li>'
                f'<li>{bi("Overdraft allowed?", "允许透支？")}</li>'
                '</ul>') +

        section("Data model", "数据模型",
                '<pre><code>Account(account_id, tenant_id, status)\n'
                'CreditGrant(grant_id, account_id, amount, granted_at, expires_at, source)\n'
                'CreditLedger(entry_id, account_id, grant_id, delta, reason, job_id, created_at)\n'
                '-- Running balance = SUM(delta) grouped by account\n'
                '-- FIFO consumption: consume from oldest non-expired grant first</code></pre>') +

        section("Key algorithms", "关键算法",
                '<ul>'
                f'<li>{bi("<strong>Reserve → commit → release</strong>: reserve credits before job starts (2-phase). Avoids race and overspend.", "<strong>Reserve → commit → release</strong>：作业开始前先预留（两阶段）。避免竞态与超支。")}</li>'
                f'<li>{bi("<strong>FIFO consumption</strong>: maintain a sorted view by (expires_at ASC). Greedy-consume oldest grants first.", "<strong>FIFO 消费</strong>：维护按 (expires_at ASC) 排序的视图。贪心从最旧 grant 消费。")}</li>'
                f'<li>{bi("<strong>Idempotent commits</strong> keyed on job_id — retries must not double-charge.", "<strong>幂等 commit</strong> 按 job_id 加键——重试不得双扣。")}</li>'
                '</ul>') +

        section("Fairness layer", "公平层",
                '<p>' + bi("Credits answer \"can you run?\"; a separate WFQ scheduler answers \"who runs next?\". Don&apos;t conflate them.",
                           "Credit 回答「能不能跑」；独立的 WFQ 调度器回答「谁先跑」。两者不要混淆。") + '</p>')
    ),
    "related": [
        ("llm/llm-serving.html", bi("LLM serving", "LLM 推理服务")),
    ],
})

# ====================================================================
# O15. Streaming Token Response
# ====================================================================
QUESTIONS.append({
    "qid": "O15", "filename": "o15-streaming-token-response.html",
    "title_en": "Streaming Token Response System",
    "title_zh": "Token 流式响应系统",
    "company": "openai", "freq": 2, "diff": "hard",
    "extra_tags": ["SSE", "TTFT", "Backpressure"],
    "source_html": 'Prompt: "Design a Streaming Token Response System." — SystemDesignHandbook. Credibility <strong>D</strong>.',
    "body": (
        section("Two protocol options", "两种协议选型",
                '<ul>'
                f'<li>{bi("<strong>SSE</strong>: one-way server→client; simple; reconnect via <code>Last-Event-ID</code>.", "<strong>SSE</strong>：单向 server→client；简单；用 <code>Last-Event-ID</code> 重连。")}</li>'
                f'<li>{bi("<strong>WebSocket</strong>: bi-directional; required for tool-use / cancel mid-stream.", "<strong>WebSocket</strong>：双向；支持工具调用 / 流中取消。")}</li>'
                '</ul>') +

        section("Architecture", "架构",
                mermaid("""flowchart LR
  C[Client] --> GW[HTTP Gateway]
  GW --> STREAM[Stream Handler]
  STREAM --> INF[Inference Worker (GPU)]
  INF --> MOD[Inline Moderation]
  MOD --> STREAM
  STREAM --> C
  STREAM --> STATE[(Stream State Store)]""")) +

        section("Must-cover engineering points", "必答工程点",
                '<ul>'
                f'<li>{bi("TTFT (time-to-first-token) SLO: dominated by prefill + queue wait.", "TTFT（首 token 延迟）SLO：主要受 prefill + 队列等待影响。")}</li>'
                f'<li>{bi("Backpressure: if client is slow, buffer bounded; on overflow close stream with error.", "背压：客户端慢时缓冲有上限；溢出时关闭流并报错。")}</li>'
                f'<li>{bi("Reconnect: stream_id + last_token_index → resume from index; require server to keep N seconds of token history.", "重连：stream_id + last_token_index → 从索引恢复；要求服务端保留 N 秒 token 历史。")}</li>'
                f'<li>{bi("Inline moderation: chunked classifier every 10-20 tokens; can retract emitted tokens via <code>[retract]</code> event.", "流式 moderation：每 10-20 token 做 chunk 级分类；可通过 <code>[retract]</code> 事件撤回已发 token。")}</li>'
                '</ul>')
    ),
    "related": [
        ("llm/llm-serving.html", bi("LLM serving", "LLM 推理服务")),
    ],
})

# ====================================================================
# O16. RAG / Enterprise Search
# ====================================================================
QUESTIONS.append({
    "qid": "O16", "filename": "o16-llm-enterprise-search.html",
    "title_en": "LLM-powered Enterprise Search (RAG)",
    "title_zh": "面向企业的 LLM 语义搜索（RAG）",
    "company": "openai", "freq": 2, "diff": "hard",
    "extra_tags": ["RAG", "Vector DB"],
    "source_html": 'Prompt: "Design an LLM-powered Enterprise Search System." — Glassdoor. Credibility <strong>C</strong>.',
    "body": (
        section("Two pipelines", "两条管道",
                '<ol>'
                f'<li>{bi("<strong>Indexing pipeline</strong>: data ingest → clean/chunk → embed → vector store (+ keyword index).", "<strong>索引管道</strong>：采集 → 清洗/分块 → embed → 向量库（+ 关键词索引）。")}</li>'
                f'<li>{bi("<strong>Query pipeline</strong>: query → rewrite (optional) → hybrid retrieval → rerank → context assemble → LLM generate with citations.", "<strong>查询管道</strong>：query → 改写（可选）→ 混合检索 → 重排 → 上下文组装 → LLM 生成（带引用）。")}</li>'
                '</ol>') +

        section("Architecture", "架构",
                mermaid("""flowchart LR
  subgraph Indexing
    A[Docs / Connectors] --> B[Cleaner]
    B --> C[Chunker]
    C --> D[Embedder]
    D --> E[(Vector DB)]
    C --> F[(Keyword Index)]
  end
  subgraph Query
    Q[User Query] --> R[Query Rewrite]
    R --> HV[Vector Search] --> M[Merge]
    R --> HK[Keyword Search] --> M
    M --> RR[Reranker] --> LLM
    LLM --> ANS[Answer + Citations]
  end
  E --> HV
  F --> HK""")) +

        section("Key design decisions", "关键决策",
                '<ul>'
                f'<li>{bi("<strong>Chunk size</strong> is the single most important trade-off — too small loses context, too large injects noise. 200-500 tokens typical with 10-20% overlap.", "<strong>Chunk 大小</strong>是最关键的权衡——太小丢上下文，太大引入噪声。典型 200-500 tokens，10-20% 重叠。")}</li>'
                f'<li>{bi("<strong>Hybrid retrieval</strong>: BM25 (sparse) + dense embedding; merge via reciprocal rank fusion.", "<strong>混合检索</strong>：BM25（稀疏）+ 稠密 embedding；通过 RRF 合并。")}</li>'
                f'<li>{bi("<strong>Cross-encoder rerank</strong> of top-K (say K=50 → 10). Cost increases but answer quality jumps.", "<strong>Cross-encoder 重排</strong>对 top-K（K=50 → 10）。成本上升但答案质量显著提升。")}</li>'
                f'<li>{bi("<strong>HyDE</strong> (hypothetical document embeddings) for recall boost on rare queries.", "<strong>HyDE</strong>（假设文档 embedding）提升稀缺 query 召回。")}</li>'
                '</ul>') +

        section("Evaluation", "评估",
                '<ul>'
                f'<li>{bi("Retrieval: Recall@K, MRR, NDCG.", "检索：Recall@K、MRR、NDCG。")}</li>'
                f'<li>{bi("Generation: Faithfulness (grounded in context), answer relevancy, citation accuracy.", "生成：Faithfulness（是否基于上下文）、answer relevancy、引用准确性。")}</li>'
                '</ul>') +

        section("Follow-ups", "追问",
                '<ul>'
                f'<li>{bi("<strong>Knowledge-base updates</strong>: incremental embed + delete; use soft-delete with tombstones.", "<strong>知识库更新</strong>：增量 embed + 删除；软删除用 tombstone。")}</li>'
                f'<li>{bi("<strong>Hallucination mitigation</strong>: constrain to &quot;cite or say you don&apos;t know&quot;; evaluate with faithfulness metric.", "<strong>幻觉缓解</strong>：约束「引用或承认不知道」；用 faithfulness 评估。")}</li>'
                f'<li>{bi("<strong>Multi-modal docs</strong>: PDFs with tables/images → layout-aware parsers + separate embedding for tables.", "<strong>多模态文档</strong>：含表格/图片的 PDF → layout-aware 解析器 + 表格独立 embedding。")}</li>'
                '</ul>')
    ),
    "related": [
        ("llm/rag.html", bi("RAG deep dive", "RAG 深度剖析")),
        ("llm/agentic-patterns.html", bi("Agent patterns", "Agent 模式")),
    ],
})

# ====================================================================
# O17. Rate Limiter
# ====================================================================
QUESTIONS.append({
    "qid": "O17", "filename": "o17-rate-limiter.html",
    "title_en": "Design a Rate Limiter",
    "title_zh": "设计限流器",
    "company": "openai", "freq": 2, "diff": "medium",
    "diff_label": "Medium",
    "extra_tags": ["Token Bucket", "Distributed"],
    "source_html": 'Prompt: "Design a Rate Limiter." — Jobright, IGotAnOffer. Classic with AI twist (per-token billing). Credibility <strong>C/D</strong>.',
    "body": (
        section("Algorithms compared", "算法对比",
                '<table><thead><tr><th>Algorithm</th><th>Properties</th><th>Use-case</th></tr></thead><tbody>'
                f'<tr><td><strong>Token bucket</strong></td><td>{bi("Burst allowed up to bucket size, steady refill.", "允许突发到桶大小，稳定续 token。")}</td><td>{bi("Most APIs — OpenAI-style.", "多数 API，OpenAI 风格。")}</td></tr>'
                f'<tr><td><strong>Leaky bucket</strong></td><td>{bi("Strict smoothing; queue with fixed drain.", "严格平滑；定速流出队列。")}</td><td>{bi("Traffic shaping; streaming.", "流量整形；流式场景。")}</td></tr>'
                f'<tr><td><strong>Fixed window</strong></td><td>{bi("Simple; burst at window boundary.", "简单；窗口边界有突发。")}</td><td>{bi("Coarse quotas, daily limits.", "粗粒度配额、日限。")}</td></tr>'
                f'<tr><td><strong>Sliding window log</strong></td><td>{bi("Exact but memory-heavy.", "精确但内存开销大。")}</td><td>{bi("Small scale, accuracy-critical.", "小规模，精度关键。")}</td></tr>'
                f'<tr><td><strong>Sliding window counter</strong></td><td>{bi("Approximate; O(1) memory.", "近似；O(1) 内存。")}</td><td>{bi("Most APIs.", "多数 API。")}</td></tr>'
                '</tbody></table>') +

        section("Distributed coordination", "分布式协调",
                '<ul>'
                f'<li>{bi("<strong>Redis + Lua</strong> for atomic token-bucket operations (check-and-decrement).", "<strong>Redis + Lua</strong>原子化令牌桶（先查后扣一步完成）。")}</li>'
                f'<li>{bi("<strong>Sticky hashing</strong> of key (user/API key) to specific shard → locality + consistency.", "<strong>按 key 黏附哈希</strong>（用户/API key）到特定 shard → 局部性 + 一致性。")}</li>'
                f'<li>{bi("<strong>Client-side check with server reconciliation</strong>: gateway pre-filters, Redis authoritatively decides.", "<strong>客户端预检 + 服务端权威</strong>：网关预过滤，Redis 最终拍板。")}</li>'
                '</ul>') +

        section("AI-specific twist", "AI 专属扩展",
                '<p>' + bi("For LLM APIs, limit on <strong>tokens</strong> (input+output) not just requests. Requires predicting output tokens or reserving max then refunding unused.",
                           "LLM API 的限流应基于 <strong>token</strong>（输入+输出）而非请求数。需预估输出 token 或先 reserve 最大再返还未用部分。") + '</p>')
    ),
    "related": [
        ("classical/rate-limiter.html", bi("Rate limiter deep dive", "限流器深度")),
        ("llm/llm-serving.html", bi("LLM serving", "LLM 推理服务")),
    ],
})

# ====================================================================
# O18. Vector Database
# ====================================================================
QUESTIONS.append({
    "qid": "O18", "filename": "o18-vector-database.html",
    "title_en": "Design a Vector Database",
    "title_zh": "设计向量数据库",
    "company": "openai", "freq": 2, "diff": "hard",
    "extra_tags": ["ANN", "HNSW", "Sharding"],
    "source_html": 'Prompt: "Design a Vector Database." — Jobright. Credibility <strong>C</strong>.',
    "body": (
        section("Problem size", "规模",
                '<p>' + bi("Billions of 768-1536 dim vectors, sub-100ms query latency, filtered by metadata (tenant, date, source).",
                           "数十亿 768-1536 维向量，查询延迟 &lt; 100ms，支持 metadata 过滤（租户、日期、来源）。") + '</p>') +

        section("ANN index families", "ANN 索引家族",
                '<ul>'
                f'<li>{bi("<strong>HNSW</strong>: graph-based, best recall/speed trade-off, higher memory.", "<strong>HNSW</strong>：基于图，召回/速度权衡最佳，内存更高。")}</li>'
                f'<li>{bi("<strong>IVF-PQ</strong>: inverted file + product quantization, lower memory, worse recall at high K.", "<strong>IVF-PQ</strong>：倒排 + 乘积量化，内存低，高 K 召回偏弱。")}</li>'
                f'<li>{bi("<strong>ScaNN</strong> (Google) and <strong>DiskANN</strong> (Microsoft) for disk-resident indices.", "<strong>ScaNN</strong>（Google）与 <strong>DiskANN</strong>（微软）用于磁盘索引。")}</li>'
                '</ul>') +

        section("Architecture", "架构",
                mermaid("""flowchart LR
  W[Writer] --> SHARD[Sharder]
  SHARD --> S1[Shard 1: HNSW]
  SHARD --> S2[Shard 2: HNSW]
  SHARD --> S3[Shard 3: HNSW]
  Q[Query] --> ROUTE[Router]
  ROUTE --> S1 & S2 & S3
  S1 & S2 & S3 --> MERGE[Top-K Merger]
  MERGE --> RET[Return]""")) +

        section("Key decisions", "关键决策",
                '<ul>'
                f'<li>{bi("<strong>Sharding</strong>: random or by tenant. Random = balance but query fans to all shards. By tenant = locality but hot-tenant risk.", "<strong>分片</strong>：随机或按租户。随机 = 均衡但 query 扇出；按租户 = 局部性但有热租户风险。")}</li>'
                f'<li>{bi("<strong>Metadata filter</strong>: pre-filter can crash recall; post-filter wastes compute. Hybrid &quot;filter-then-index&quot; per-shard is often best.", "<strong>Metadata 过滤</strong>：预过滤会破坏召回；后过滤浪费算力。每分片 hybrid「filter-then-index」通常最优。")}</li>'
                f'<li>{bi("<strong>Ingestion pipeline</strong>: batched writes; async index rebuild; immutable segments like LSM-tree.", "<strong>采集管道</strong>：批量写；异步重建索引；不可变段（类 LSM）。")}</li>'
                f'<li>{bi("<strong>Freshness</strong>: if real-time writes required, maintain a live search layer + periodic merge into cold HNSW index.", "<strong>新鲜度</strong>：若需实时写入，维护实时搜索层 + 周期合并到冷 HNSW 索引。")}</li>'
                '</ul>')
    ),
    "related": [
        ("llm/rag.html", bi("RAG", "RAG")),
        ("distributed/partitioning.html", bi("Partitioning", "分区")),
    ],
})

# ====================================================================
# O19. Distributed ML Training
# ====================================================================
QUESTIONS.append({
    "qid": "O19", "filename": "o19-distributed-training.html",
    "title_en": "Distributed ML Training Platform",
    "title_zh": "分布式 ML 训练平台",
    "company": "openai", "freq": 2, "diff": "hard",
    "diff_label": "Staff-level",
    "extra_tags": ["3D Parallelism", "ZeRO", "Checkpoint"],
    "source_html": 'Prompt: "Design a Distributed ML Training Platform." — Hello Interview (Staff-level). Credibility <strong>D</strong>.',
    "body": (
        section("Clarify scope", "范围澄清",
                '<ul>'
                f'<li>{bi("Target model sizes? 1B vs 100B parameters pull wildly different architectures.", "目标模型规模？1B vs 100B 参数对应架构差异巨大。")}</li>'
                f'<li>{bi("Users: internal researchers or external customers?", "用户：内部研究者还是外部客户？")}</li>'
                f'<li>{bi("Hardware: homogeneous GPU cluster or multi-region multi-type?", "硬件：同构 GPU 集群还是跨区多型号？")}</li>'
                '</ul>') +

        section("Three orthogonal parallelism strategies", "三种正交并行策略",
                '<ul>'
                f'<li>{bi("<strong>Data Parallel (DP)</strong>: replicate model, shard data, AllReduce gradients. ZeRO-1/2/3 progressively shards optimizer states, gradients, parameters.", "<strong>数据并行 (DP)</strong>：复制模型、切分数据、AllReduce 梯度。ZeRO-1/2/3 渐进分片优化器状态、梯度、参数。")}</li>'
                f'<li>{bi("<strong>Tensor Parallel (TP)</strong>: split weight matrices within a layer. High bandwidth needed (NVLink-only).", "<strong>张量并行 (TP)</strong>：层内切分权重矩阵。对带宽要求高（仅限 NVLink）。")}</li>'
                f'<li>{bi("<strong>Pipeline Parallel (PP)</strong>: split layers across stages, feed micro-batches to fill the pipe. Bubble ratio &lt; 25% needs micro-batches &gt; 4× stages.", "<strong>流水线并行 (PP)</strong>：跨阶段切分层，用微批次填充流水线。Bubble 率 &lt; 25% 需要微批次 &gt; 4× 阶段数。")}</li>'
                '</ul>') +

        section("Production recipe (3D parallelism)", "生产配方（3D 并行）",
                '<p>' + bi("<strong>Intra-node TP</strong> (NVLink) + <strong>PP</strong> across nodes + <strong>DP</strong> across replicas. Meta Llama 3 uses topology-aware comm patterns.",
                           "<strong>节点内 TP</strong>（NVLink）+ <strong>跨节点 PP</strong> + <strong>副本间 DP</strong>。Meta Llama 3 采用拓扑感知通信模式。") + '</p>') +

        section("Platform services", "平台服务",
                mermaid("""flowchart LR
  UI[CLI / UI] --> SCH[Job Scheduler]
  SCH --> RES[Resource Manager]
  RES --> GPU[GPU Fleet]
  SCH --> CKPT[Checkpoint Service]
  CKPT --> S3[(Object Store)]
  GPU --> METRICS[Metrics / Profiler]
  GPU --> ELA[Elastic Reshard]""")) +

        section("Fault tolerance is mandatory", "容错是必选项",
                '<ul>'
                f'<li>{bi("Periodic checkpoints every N steps (memory-map + async upload).", "每 N 步周期 checkpoint（memory-map + 异步上传）。")}</li>'
                f'<li>{bi("Elastic training: detect GPU failure, reschedule job with same checkpoint, resume.", "弹性训练：检测 GPU 故障 → 用同 checkpoint 重调度 → 恢复。")}</li>'
                f'<li>{bi("Loss-spike detection: auto-rollback to prior checkpoint; gradient clip.", "Loss-spike 检测：自动回滚至前一 checkpoint；梯度裁剪。")}</li>'
                '</ul>') +

        callout("openai", "Anthropic's take", "Anthropic 视角",
                "RE interviews explicitly ask: \"Pre-training a 100B model — loss spike appears. Data issue? LR? Hardware?\" Candidates are expected to walk through diagnosis and checkpoint-revert strategy.",
                "RE 面试明确问：「预训练 100B 模型出现 loss spike——是数据、LR、还是硬件问题？」候选人需能讲清诊断路径与 checkpoint 回滚策略。")
    ),
    "related": [
        ("llm/distributed-training.html", bi("Distributed training deep dive", "分布式训练深度")),
        ("ml/ml-lifecycle.html", bi("ML lifecycle", "ML 生命周期")),
    ],
})

# Now the Anthropic questions
# ====================================================================
# A11. High-concurrency LLM inference service
# ====================================================================
QUESTIONS.append({
    "qid": "A11", "filename": "a11-llm-inference-service.html",
    "title_en": "High-Concurrency LLM Inference Service",
    "title_zh": "高并发 LLM 推理服务",
    "company": "anthropic", "freq": 4, "diff": "hard",
    "extra_tags": ["LLM Serving", "KV Cache", "PagedAttention"],
    "source_html": (
        'Prompt: "Design a high-concurrency LLM inference platform…support streaming token output…must discuss prefill vs decode, KV cache, batching strategy, tail latency…" — '
        '<a href="https://prachub.com" target="_blank" rel="noopener">PracHub</a>, 2026-02, Onsite. Credibility <strong>B</strong>.'
    ),
    "body": (
        section("Open with the prefill / decode split (first minute)", "第一分钟：分相 prefill / decode",
                '<ul>'
                f'<li>{bi("<strong>Prefill</strong>: one big compute pass over the prompt. Throughput-bound. Loves batching.", "<strong>Prefill</strong>：对 prompt 的一次大计算。吞吐导向。喜欢 batching。")}</li>'
                f'<li>{bi("<strong>Decode</strong>: autoregressive per-token. Latency-bound. Vulnerable to tail latency from long-running requests.", "<strong>Decode</strong>：按 token 自回归。延迟导向。易被长请求拖累尾延迟。")}</li>'
                '</ul>') +

        section("Reference architecture", "参考架构",
                mermaid("""flowchart LR
  C[Client] --> GW[API Gateway]
  GW --> RL[Rate Limit & Auth]
  RL --> SCH[Scheduler / Continuous Batcher]
  SCH --> W[GPU Workers]
  W --> TOK[Token Stream]
  TOK --> C
  SCH --> MET[Metrics / Tracing]
  W --> KV[(PagedAttention KV Cache Mgr)]""")) +

        section("KV cache — speak it like you&apos;ve operated it", "KV cache——讲得像真做过",
                '<ul>'
                f'<li>{bi("KV cache avoids recomputing attention keys/values on every decode step. Time-space trade-off.", "KV cache 避免每次 decode 重算 attention 的 K/V，是时间-空间权衡。")}</li>'
                f'<li>{bi("Under high concurrency it dominates GPU memory and fragments it.", "高并发下它会占用并碎片化 GPU 显存。")}</li>'
                f'<li>{bi("<strong>vLLM&apos;s PagedAttention</strong>: OS-style virtual-memory paging for KV → fragmentation drops from 60-80% to &lt;4%, enabling ~23× throughput.", "<strong>vLLM 的 PagedAttention</strong>：借 OS 虚存分页管 KV → 碎片率从 60-80% 降到 &lt;4%，吞吐提升 ~23×。")}</li>'
                '</ul>') +

        section("Batching &amp; scheduling (give an executable strategy)", "Batching 与调度（给可执行策略）",
                '<ul>'
                f'<li>{bi("<strong>Continuous batching</strong>: iteration-level scheduling — after each token, check for completions and substitute new requests. Eliminates static batching stragglers.", "<strong>Continuous batching</strong>：迭代级调度——每生成一个 token 后检查完成并替换新请求。消除静态 batching 的掉队者。")}</li>'
                f'<li>{bi("Multi-bin by predicted remaining tokens to reduce intra-batch length variance.", "按预测剩余 token 分桶，减少批内长度方差。")}</li>'
                f'<li>{bi("Objective: <code>w1·TTFT + w2·per-token latency + w3·GPU_util + w4·drop_rate</code>; A/B the weights.", "目标函数：<code>w1·TTFT + w2·per-token 延迟 + w3·GPU 利用率 + w4·丢弃率</code>；权重 A/B。")}</li>'
                '</ul>') +

        section("Further optimizations (papers to namedrop)", "进阶优化（可引用论文）",
                '<ul>'
                f'<li>{bi("<strong>FlashAttention</strong>: IO-aware attention; big win for long contexts.", "<strong>FlashAttention</strong>：IO 感知 attention；长上下文收益显著。")}</li>'
                f'<li>{bi("<strong>Speculative decoding</strong>: small draft model generates, big model verifies — 1.5-2× speedup when accept rate is high.", "<strong>Speculative decoding</strong>：小 draft 模型生成，大模型验证——接受率高时 1.5-2× 加速。")}</li>'
                f'<li>{bi("<strong>Chunked prefill</strong>: split long prefills to keep decode alive.", "<strong>Chunked prefill</strong>：切分长 prefill 保持 decode 活跃。")}</li>'
                f'<li>{bi("<strong>Prefix caching</strong>: cache KV for repeated system-prompt prefixes.", "<strong>前缀缓存</strong>：缓存重复 system-prompt 前缀的 KV。")}</li>'
                '</ul>') +

        section("Cost model", "成本模型",
                '<pre><code>$ / token ≈ GPU_hourly_cost / tokens_per_hour_per_gpu\n'
                '          — reduce numerator via spot/larger batch; boost denominator via optimizations</code></pre>'
                '<p>' + bi("Rough anchor: AWS p4d.24xlarge (8× A100) ≈ $22/hr; H100 roughly 2× that. Quote a framework, not a final number.",
                           "参考：AWS p4d.24xlarge（8× A100）≈ $22/小时；H100 约 2 倍。用公式，不拍死数字。") + '</p>') +

        callout("anthropic", "Anthropic-style follow-ups", "Anthropic 风格追问",
                "(1) How do you avoid head-of-line blocking? → bucketing, chunked prefill, priority queue. (2) Autoscale signal? → token-queue depth > GPU util. (3) Release process? → warmup, canary, rollback thresholds, shadow traffic. (4) Where does safety go? → input/output filters, policy routing; cite Constitutional AI as framing.",
                "(1) 避免队头阻塞？→ 分桶、chunked prefill、优先级队列。(2) 扩容信号？→ token 队列深度优于 GPU 利用率。(3) 发布流程？→ warmup、canary、回滚阈值、影子流量。(4) Safety 怎么插？→ 输入/输出过滤、策略路由；引用 Constitutional AI。")
    ),
    "related": [
        ("llm/llm-serving.html", bi("LLM serving deep dive", "LLM 推理服务深度")),
        ("llm/distributed-training.html", bi("Training infra", "训练基础设施")),
    ],
})

# ====================================================================
# A12. GPU Batching
# ====================================================================
QUESTIONS.append({
    "qid": "A12", "filename": "a12-gpu-batching.html",
    "title_en": "GPU Inference Request Batching",
    "title_zh": "GPU 推理请求动态 batching",
    "company": "anthropic", "freq": 3, "diff": "hard",
    "extra_tags": ["Dynamic Batching", "SLO"],
    "source_html": 'Prompt: "Design a system that serves online model-inference requests on GPUs…batching…balance throughput against latency SLOs…overload, failures, observability." — PracHub, 2026-03, Onsite. Credibility <strong>B</strong>.',
    "body": (
        section("Make batching a controllable decision", "把 batching 变成可控决策",
                '<pre><code>if batch_size == B_MAX: flush\n'
                'elif oldest_wait_ms > W_MAX: flush\n'
                'elif predicted_exec_time_spread > T_SPREAD_MAX: flush\n'
                'else: wait a tiny delta (1-5ms) and re-evaluate</code></pre>') +

        section("Architecture", "架构",
                mermaid("""flowchart LR
  C[Client RPC] --> API[Inference API]
  API --> B[Batcher]
  B --> GPU[GPU Worker]
  GPU --> API""")) +

        section("Bottlenecks &amp; mitigations", "瓶颈与缓解",
                '<ul>'
                f'<li>{bi("<strong>Long tail</strong>: bucket by length / model spec; prioritize TTFT for small models.", "<strong>长尾</strong>：按长度 / 模型规格分桶；小模型优先保 TTFT。")}</li>'
                f'<li>{bi("<strong>Overload</strong>: admission control (token bucket + concurrency cap) + queue-timeout + degrade (CPU / 429).", "<strong>过载</strong>：准入控制（令牌桶 + 并发上限）+ 排队超时 + 降级（转 CPU / 返回 429）。")}</li>'
                f'<li>{bi("<strong>Observability</strong>: TTFT, per-token latency, batch-size distribution, drop/timeout rate, GPU memory pressure.", "<strong>可观测性</strong>：TTFT、per-token 延迟、batch size 分布、丢弃/超时率、GPU 内存压力。")}</li>'
                '</ul>')
    ),
    "related": [("llm/llm-serving.html", bi("LLM serving", "LLM 推理服务"))],
})

# ====================================================================
# A13. Routing & Scheduling Layer
# ====================================================================
QUESTIONS.append({
    "qid": "A13", "filename": "a13-inference-routing.html",
    "title_en": "Inference Routing &amp; Scheduling Layer",
    "title_zh": "推理路由与调度层",
    "company": "anthropic", "freq": 3, "diff": "hard",
    "extra_tags": ["WFQ", "Result Cache"],
    "source_html": 'Prompt: "routing layer…prioritization…dynamic batching…query result cache…credit-based fairness" — PracHub, Onsite. Credibility <strong>B</strong>.',
    "body": (
        section("Three things to nail", "讲清这三件事就赢一半",
                '<ol>'
                f'<li>{bi("Multi-tenant priority: different tenants / request classes have different SLOs &amp; quotas.", "多租户优先级：不同租户 / 请求类有不同 SLO 与配额。")}</li>'
                f'<li>{bi("Heterogeneous routing: GPU / CPU / different model versions / hardware pools.", "异构路由：GPU / CPU / 不同模型版本 / 硬件池。")}</li>'
                f'<li>{bi("Determinism &amp; caching: at temperature=0, cache results (only for reproducible inputs).", "确定性与缓存：temperature=0 时可缓存结果（仅限可复现输入）。")}</li>'
                '</ol>') +

        section("Architecture", "架构",
                mermaid("""flowchart LR
  API[Front API] --> RT[Router]
  RT --> PQ[Priority Queues]
  PQ --> BT[Batcher]
  BT --> GPU[GPU Pool]
  RT --> CPU[CPU Pool]
  RT --> Cache[(Result Cache)]""")) +

        section("Credit-based fairness (standard answer)", "基于 credit 的公平调度",
                '<ul>'
                f'<li>{bi("Weighted Fair Queueing / Deficit Round Robin: prevent a large tenant from monopolizing GPUs.", "WFQ / DRR：防止大客户独占 GPU。")}</li>'
                f'<li>{bi("Credits burn by token-cost estimate, not request count (LLM cost scales with tokens).", "Credit 消耗按预估 token 成本，而非请求数（LLM 成本与 token 强相关）。")}</li>'
                '</ul>') +

        section("Cache admission &amp; eviction", "缓存准入与淘汰",
                '<ul>'
                f'<li>{bi("Cache only reproducible requests: temperature=0, fixed model version, fixed system prompt.", "只缓存可复现请求：temperature=0 + 固定模型版本 + 固定 system prompt。")}</li>'
                f'<li>{bi("Key: <code>hash(model_version, prompt_prefix, user_input, tool_state)</code>.", "Key：<code>hash(model_version, prompt_prefix, user_input, tool_state)</code>。")}</li>'
                f'<li>{bi("Eviction: LRU/LFU + cost-aware (a giant response may not be worth caching).", "淘汰：LRU/LFU + 成本感知（超长响应不一定划算缓存）。")}</li>'
                '</ul>')
    ),
    "related": [("llm/llm-serving.html", bi("LLM serving", "LLM 推理服务"))],
})

# ====================================================================
# A14. Batch Inference API
# ====================================================================
QUESTIONS.append({
    "qid": "A14", "filename": "a14-batch-inference-api.html",
    "title_en": "Batch Inference API",
    "title_zh": "批量推理 API",
    "company": "anthropic", "freq": 3, "diff": "hard",
    "extra_tags": ["Async Job", "Idempotency"],
    "source_html": 'Prompt: "Design an inference service API where clients POST a job and later poll for results…queued/running/succeeded/failed…idempotency…partial failures within a batch." — PracHub, Onsite. Credibility <strong>B</strong>.',
    "body": (
        section("API", "API 设计",
                '<pre><code>POST /v1/jobs                        {model, inputs[...], idempotency_key} → {job_id}\n'
                'GET  /v1/jobs/{job_id}               → {status, progress, counts}\n'
                'GET  /v1/jobs/{job_id}/results?cursor=   # paginated, supports partial\n'
                'POST /v1/jobs/{job_id}:cancel</code></pre>') +

        section("Architecture", "架构",
                mermaid("""flowchart LR
  C[Client] --> S[Submit Job]
  S --> J[(Job DB)]
  S --> Q[Job Queue]
  Q --> W[Workers]
  W --> R[(Result Store)]
  C --> P[Poll Status / Results]
  P --> J
  P --> R""")) +

        section("Data model (two layers)", "数据模型（两层）",
                '<pre><code>Job(job_id, tenant_id, model, status, created_at, idempotency_key, input_ref)\n'
                'JobItem(job_id, item_id, status, output_ref, error)</code></pre>'
                '<p>' + bi("Two-level model handles partial batch failures and supports incremental result pulling.",
                           "两级模型处理批内部分失败，并支持增量拉取结果。") + '</p>') +

        section("Cost &amp; scaling", "成本与扩展",
                '<ul>'
                f'<li>{bi("Batch is naturally off-peak — use for valley-filling.", "批处理天然适合「填谷」——用于低峰期。")}</li>'
                f'<li>{bi("Can batch-size more aggressively than online (higher W_MAX, bigger B_MAX).", "比在线服务更激进地 batch（W_MAX/B_MAX 更大）。")}</li>'
                f'<li>{bi("Typical savings 40-50% vs online (Anthropic&apos;s public pricing confirms this).", "相比在线通常节省 40-50%（Anthropic 官方定价已证实）。")}</li>'
                '</ul>')
    ),
    "related": [("llm/llm-serving.html", bi("LLM serving", "LLM 推理服务"))],
})

# ====================================================================
# A15. Multi-Model GPU API
# ====================================================================
QUESTIONS.append({
    "qid": "A15", "filename": "a15-multi-model-inference-api.html",
    "title_en": "Multi-Model GPU Inference API",
    "title_zh": "多模型 GPU 推理 API",
    "company": "anthropic", "freq": 3, "diff": "hard",
    "extra_tags": ["Control Plane", "Canary"],
    "source_html": 'Prompt: "Design a GPU-backed inference API…multi-model…dynamic batching…A/B routing…autoscaling…KV/cache" — PracHub, Onsite. Credibility <strong>B</strong>.',
    "body": (
        section("Two-layer design", "两层架构",
                '<ul>'
                f'<li>{bi("<strong>Data plane</strong>: request ingress → batcher → GPU worker → token stream.", "<strong>数据面</strong>：请求入口 → batcher → GPU worker → token 流。")}</li>'
                f'<li>{bi("<strong>Control plane</strong>: model registry, version rollouts, routing policy, autoscaling, cost policy.", "<strong>控制面</strong>：模型注册表、版本发布、路由策略、自动扩缩容、成本策略。")}</li>'
                '</ul>') +

        section("Architecture", "架构",
                mermaid("""flowchart LR
  C[Client] --> GW[Gateway]
  GW --> SCH[Scheduler / Batcher]
  SCH --> GPU[GPU Workers]
  CTRL[Control Plane] --> SCH
  CTRL --> REG[(Model Registry)]
  GPU --> OBS[Observability]""")) +

        section("A/B routing", "A/B 路由",
                '<ul>'
                f'<li>{bi("Routing key: <code>tenant_id + experiment_id + user_id</code> for stickiness.", "路由键：<code>tenant_id + experiment_id + user_id</code> 保证粘性。")}</li>'
                f'<li>{bi("Rollback triggers: error-budget burn, p95 TTFT over threshold, rising OOM ratio.", "回滚触发：error-budget 烧光、p95 TTFT 超阈、OOM 比例上升。")}</li>'
                '</ul>') +

        section("Cold start is the hidden cost", "冷启动是隐藏成本",
                '<ul>'
                f'<li>{bi("Model load + warmup can take minutes. Solution: <strong>always-warm pool for top-N models</strong> + tiered SKU pools.", "模型加载 + warmup 耗时分钟级。方案：<strong>top-N 模型常驻热池</strong> + 分层 SKU 池。")}</li>'
                f'<li>{bi("KV-cache / weights reuse across tenants → citing vLLM PagedAttention credits you here.", "跨租户复用 KV-cache / weights → 引用 vLLM PagedAttention 加分。")}</li>'
                '</ul>')
    ),
    "related": [("llm/llm-serving.html", bi("LLM serving", "LLM 推理服务"))],
})

# ====================================================================
# A16. Low-latency ML Inference API
# ====================================================================
QUESTIONS.append({
    "qid": "A16", "filename": "a16-low-latency-inference-api.html",
    "title_en": "Low-Latency ML Inference API",
    "title_zh": "低延迟 ML 推理 API",
    "company": "anthropic", "freq": 3, "diff": "hard",
    "extra_tags": ["Feature Store", "Drift"],
    "source_html": 'Prompt: "Design a low-latency ML inference API…SLOs…feature retrieval…canary/rollbacks…drift detection" — PracHub, Onsite. Credibility <strong>B</strong>.',
    "body": (
        section("Three numbers you must have", "必须给出的三个数字",
                '<ul>'
                f'<li>{bi("p95 latency (e.g. 50–150ms depending on business).", "p95 延迟（如 50–150ms，按业务）。")}</li>'
                f'<li>{bi("Availability SLO (99.9 / 99.99).", "可用性 SLO（99.9 / 99.99）。")}</li>'
                f'<li>{bi("QPS / throughput for capacity math.", "QPS/吞吐用于容量规划。")}</li>'
                '</ul>') +

        section("Architecture", "架构",
                mermaid("""flowchart LR
  U[Product Service] --> API[Inference API]
  API --> FS[Feature Store]
  API --> MS[Model Server]
  MS --> API
  API --> MON[Metrics + Drift]""")) +

        section("Feature store realism", "Feature store 的现实",
                '<ul>'
                f'<li>{bi("Online store must be low-latency. Training-serving skew is the #1 bug.", "在线 store 必须低延迟。Training-serving skew 是头号 bug。")}</li>'
                f'<li>{bi("Cache hot features with TTL + version.", "热特征缓存 + TTL + 版本。")}</li>'
                '</ul>') +

        section("Fallback (don&apos;t crash on partial failure)", "降级（部分故障时不崩）",
                '<ul>'
                f'<li>{bi("Feature store slow → return default features / smaller model.", "Feature store 慢 → 返回默认特征 / 小模型。")}</li>'
                f'<li>{bi("GPU pool starved → switch to CPU / smaller model.", "GPU 池不足 → 切 CPU / 小模型。")}</li>'
                f'<li>{bi("Model anomaly → rollback to previous (always keep prior warm).", "模型异常 → 回滚上一个（上一版始终保持预热）。")}</li>'
                '</ul>')
    ),
    "related": [
        ("ml/drift-monitoring.html", bi("Drift &amp; monitoring", "漂移与监控")),
        ("ml/ml-lifecycle.html", bi("ML lifecycle", "ML 生命周期")),
    ],
})

# ====================================================================
# A17. Design Review
# ====================================================================
QUESTIONS.append({
    "qid": "A17", "filename": "a17-design-review.html",
    "title_en": "Review an Inference API Design for Scale",
    "title_zh": "评审他人的推理 API 设计",
    "company": "anthropic", "freq": 2, "diff": "hard",
    "extra_tags": ["Design Review", "SRE"],
    "source_html": 'Prompt: "You are reviewing another engineer\'s design doc…critique…SLOs…autoscaling…circuit breakers…canary…audit logs…cost controls." — PracHub, Onsite. Credibility <strong>B</strong>.',
    "body": (
        section("Standard answer structure (use as a checklist)", "标准答题结构（当清单用）",
                '<ol>'
                f'<li>{bi("Fill missing SLOs / capacity assumptions first.", "先补齐缺失的 SLO / 容量假设。")}</li>'
                f'<li>{bi("Find single points &amp; failure modes (GPU OOM, hot-swap failure, queue backlog, cross-AZ partition).", "找单点与故障模式（GPU OOM、热更失败、队列积压、跨 AZ 断链）。")}</li>'
                f'<li>{bi("Prioritize changes: safety-first (rate limit / circuit breaker / rollback) → efficiency (batch / cache) → cost (SKU pool / valley-fill).", "改动优先级：保命（限流/熔断/回滚）→ 提效（batch/缓存）→ 降本（SKU 池/填谷）。")}</li>'
                '</ol>') +

        section("Failure-mode catalog", "故障模式清单",
                '<ul>'
                f'<li>{bi("<strong>Overload</strong>: admission control + token-level backpressure.", "<strong>过载</strong>：准入控制 + token 级背压。")}</li>'
                f'<li>{bi("<strong>Bad release</strong>: canary + automated rollback on error-budget burn.", "<strong>坏发布</strong>：canary + 错误预算告警触发自动回滚。")}</li>'
                f'<li>{bi("<strong>Noisy neighbor</strong>: per-tenant isolation, quota, priority queues.", "<strong>嘈杂邻居</strong>：按租户隔离、配额、优先级队列。")}</li>'
                f'<li>{bi("<strong>Data corruption</strong>: immutable inputs, output signing, audit log.", "<strong>数据污染</strong>：不可变输入、输出签名、审计日志。")}</li>'
                '</ul>') +

        callout("anthropic", "Tip", "技巧",
                "Anchor each recommendation to an SLO change (e.g., \"this canary policy cuts blast radius from 100% → 1% for bad releases\"). Raw advice without SLO framing loses points.",
                "每条建议都锚定到 SLO 变化（如「这套 canary 把坏发布的 blast radius 从 100% 降到 1%」）。不绑 SLO 的建议扣分。")
    ),
    "related": [("llm/llm-serving.html", bi("LLM serving", "LLM 推理服务"))],
})

# ====================================================================
# A18. Model Downloader
# ====================================================================
QUESTIONS.append({
    "qid": "A18", "filename": "a18-model-downloader.html",
    "title_en": "Model Downloader / Artifact Distribution",
    "title_zh": "模型分发器 / 制品分发系统",
    "company": "anthropic", "freq": 2, "diff": "medium",
    "diff_label": "Medium-Hard",
    "extra_tags": ["Artifact", "Rollout"],
    "source_html": 'Prompt: "Design a system that distributes model artifacts…integrity validation…rollout to thousands of hosts…rollback…auditability" — PracHub, Onsite 2026-02. Credibility <strong>B</strong>.',
    "body": (
        section("Architecture (control plane + host agent)", "架构（控制面 + 主机 agent）",
                mermaid("""flowchart LR
  REG[(Model Registry)] --> CDN[Artifact Storage / CDN]
  REG --> CTRL[Rollout Controller]
  CTRL --> AG[Host Agent]
  AG --> CDN
  AG --> RUN[Inference Runtime]
  AG --> OBS[Report Status]
  OBS --> CTRL""")) +

        section("Correctness invariants", "正确性不变量",
                '<ul>'
                f'<li>{bi("<strong>Manifest</strong> = {version, deps, checksum, signature}. Verified before activation.", "<strong>Manifest</strong> = {版本、依赖、checksum、签名}。激活前验证。")}</li>'
                f'<li>{bi("<strong>Atomic switch</strong>: download to staging dir; validate; flip symlink; old kept for rollback.", "<strong>原子切换</strong>：下载到暂存目录；校验；切 symlink；旧版本保留用于回滚。")}</li>'
                f'<li>{bi("<strong>Rollback</strong>: keep last N versions; auto-rollback on agent-reported health failure.", "<strong>回滚</strong>：保留最近 N 版本；agent 上报失败时自动回滚。")}</li>'
                f'<li>{bi("<strong>Rate control</strong>: stage by AZ / batch; prevent thundering-herd download.", "<strong>限速</strong>：按 AZ / 批次分发；防止惊群下载。")}</li>'
                '</ul>') +

        section("Observability", "可观测性",
                '<ul>'
                f'<li>{bi("Per-host status + version lag histogram.", "按主机状态 + 版本滞后直方图。")}</li>'
                f'<li>{bi("SLI: rollout duration p95, failed-host rate, rollback rate.", "SLI：rollout 时长 p95、失败主机率、回滚率。")}</li>'
                '</ul>')
    ),
    "related": [
        ("llm/llm-serving.html", bi("LLM serving", "LLM 推理服务")),
        ("distributed/replication.html", bi("Replication", "复制")),
    ],
})

# ====================================================================
# A19. Prompt Playground
# ====================================================================
QUESTIONS.append({
    "qid": "A19", "filename": "a19-prompt-playground.html",
    "title_en": "Prompt Playground / Experiment Platform",
    "title_zh": "Prompt 实验平台",
    "company": "anthropic", "freq": 2, "diff": "medium",
    "diff_label": "Medium",
    "extra_tags": ["Experimentation", "Prompt Cache"],
    "source_html": 'Prompt: "Design a prompt playground…compare outputs…collaborate…prompt versioning…experiment management…evaluation…context too large" — PracHub, Onsite 2026-02. Credibility <strong>B</strong>.',
    "body": (
        section("Treat it as an experiment platform (not a UI wrapper)", "当作实验平台（而非 UI 包装）",
                mermaid("""flowchart LR
  UI[Web UI] --> API[Playground API]
  API --> V[(Prompt Versions)]
  API --> RUN[Run Orchestrator]
  RUN --> LLM[Model API]
  RUN --> E[(Eval Results)]
  API --> COL[Collaboration / ACL]""")) +

        section("Four product-workflow questions you must answer", "必须回答的 4 个产品工作流问题",
                '<ol>'
                f'<li>{bi("<strong>Reproducibility per experiment</strong>: pin model version, params, context, tool versions, dataset version.", "<strong>每次实验可复现</strong>：固定模型版本、参数、上下文、工具版本、数据集版本。")}</li>'
                f'<li>{bi("<strong>Comparison</strong>: side-by-side view + automated metrics (accuracy, preference, toxicity).", "<strong>对比</strong>：并排视图 + 自动指标（准确率、偏好、毒性）。")}</li>'
                f'<li>{bi("<strong>Permissions</strong>: workspace, share links, audit log.", "<strong>权限</strong>：workspace、分享链接、审计日志。")}</li>'
                f'<li>{bi("<strong>Oversize context</strong>: reference external docs (RAG), chunk prompt, or use prompt caching for repeated prefixes.", "<strong>超大上下文</strong>：引用外部文档（RAG）、分块 prompt、重复前缀用 prompt cache。")}</li>'
                '</ol>') +

        section("Prompt caching gotcha", "Prompt caching 陷阱",
                '<ul>'
                f'<li>{bi("Anthropic&apos;s prompt caching has 5-min default TTL (extensible to 1 hour at cost).", "Anthropic 的 prompt cache 默认 5 分钟 TTL（付费可扩展到 1 小时）。")}</li>'
                f'<li>{bi("In a playground, cache the <em>system prompt + background material</em> prefix to cut cost; cache key MUST include workspace / tenant to prevent cross-tenant leaks.", "playground 中缓存 <em>system prompt + 背景材料</em>前缀以降本；cache key <strong>必须</strong>包含 workspace/tenant 防止跨租户泄漏。")}</li>'
                '</ul>')
    ),
    "related": [
        ("llm/llm-evaluation.html", bi("LLM eval", "LLM 评估")),
        ("llm/rag.html", bi("RAG", "RAG")),
    ],
})

# ====================================================================
# A20. Performance Take-Home
# ====================================================================
QUESTIONS.append({
    "qid": "A20", "filename": "a20-performance-takehome.html",
    "title_en": "Performance Take-Home (Cycle Optimization)",
    "title_zh": "性能 Take-Home（底层优化）",
    "company": "anthropic", "freq": 2, "diff": "hard",
    "extra_tags": ["Perf Engineering", "Profiling"],
    "source_html": 'Anthropic\'s Original Performance Take-Home (open-sourced on GitHub). Warning in README: LLMs can "cheat" by modifying tests. Credibility <strong>A</strong> (open-source official).',
    "body": (
        '<p>' + bi("Not a classical system-design question, but very much in Anthropic&apos;s value system: infra-level optimization + <em>correctness integrity</em>. The README explicitly warns that LLM agents may &quot;cheat&quot; by modifying tests.",
                   "这不是传统系统设计，但符合 Anthropic 的价值观：基础设施级优化 + <em>正确性诚信</em>。README 明确警告 LLM Agent 可能「改测试作弊」。") + '</p>' +

        section("How to approach it (and adjacent questions)", "解题思路（及类似题目）",
                '<ul>'
                f'<li>{bi("Establish baseline profile: hotspots, instruction counts, memory access.", "建立 baseline profile：热点、指令数、内存访问。")}</li>'
                f'<li>{bi("Change one class of optimization per iteration; preserve explainability (loop unrolling, branch reduction, cache locality, SIMD).", "每次迭代只改一类手段，保持可解释（loop 展开、减分支、缓存局部性、SIMD）。")}</li>'
                f'<li>{bi("<strong>Correctness guardrails</strong>: fixed test set, diff-tests directory, record cycle-count vs correctness per commit.", "<strong>正确性护栏</strong>：固定测试集、diff-tests 目录、每次 commit 记录 cycle-count 与正确性。")}</li>'
                f'<li>{bi("Never modify tests. The repo detects this.", "绝不修改测试。仓库会检测。")}</li>'
                '</ul>') +

        callout("anthropic", "Why this matters in interviews", "为何面试重视",
                "Anthropic cares about agents that don\'t cheat their own evals. Demonstrating rigorous methodology and zero test tampering signals \"can be trusted to run autonomously.\"",
                "Anthropic 关心不作弊的 Agent。展现严谨方法论与零测试改动等于说「可被信任自主运行」。")
    ),
    "related": [
        ("safety/safety-engineering.html", bi("Safety engineering", "安全工程")),
    ],
})

# ====================================================================
# A21-A29 — rest of Anthropic questions (briefer detail pages)
# ====================================================================
QUESTIONS.append({
    "qid": "A21", "filename": "a21-claude-chat-service.html",
    "title_en": "Design Claude Chat Service",
    "title_zh": "设计 Claude Chat 服务",
    "company": "anthropic", "freq": 2, "diff": "hard",
    "extra_tags": ["Session", "Streaming"],
    "source_html": 'Prompt: "Design Claude Chat Service." — interviewing.io. Credibility <strong>C/D</strong>.',
    "body": (
        section("Core concerns", "核心考察",
                '<ul>'
                f'<li>{bi("Session management (long-lived conversations with token limits).", "会话管理（带 token 限制的长对话）。")}</li>'
                f'<li>{bi("Streaming output over SSE / WebSocket.", "SSE / WebSocket 流式输出。")}</li>'
                f'<li>{bi("Token-level billing (metered at worker after tokenization).", "Token 级计费（tokenization 后按 worker 计）。")}</li>'
                f'<li>{bi("Log aggregation (conversation + safety annotations for audit).", "日志聚合（对话 + safety 注释用于审计）。")}</li>'
                f'<li>{bi("Safety pipeline integration (input filter, output filter, content policy).", "Safety 管道集成（输入过滤、输出过滤、内容策略）。")}</li>'
                '</ul>') +
        section("Architecture", "架构",
                mermaid("""flowchart LR
  C[Client] --> GW[Gateway]
  GW --> SESS[Session Service]
  SESS --> CONV[(Conv Store)]
  GW --> SAFE[Safety Input Filter]
  SAFE --> INF[Inference]
  INF --> SAFE2[Safety Output Filter]
  SAFE2 --> GW
  GW --> METER[Usage Metering]""")) +
        '<p>' + bi("See A11 for inference depth and A19 for prompt versioning.",
                   "推理深度参考 A11，Prompt 版本化参考 A19。") + '</p>'
    ),
    "related": [
        ("llm/llm-serving.html", bi("LLM serving", "LLM 推理服务")),
        ("safety/safety-engineering.html", bi("Safety", "安全")),
    ],
})

QUESTIONS.append({
    "qid": "A22", "filename": "a22-p2p-file-distribution.html",
    "title_en": "P2P File Distribution (BitTorrent-style)",
    "title_zh": "P2P 大文件分发（类 BitTorrent）",
    "company": "anthropic", "freq": 2, "diff": "hard",
    "extra_tags": ["P2P", "Bandwidth"],
    "source_html": 'Prompt: "Design a Peer-to-Peer File Distribution System" (bandwidth-constrained, thousands of machines). — Exponent. Credibility <strong>B/C</strong>.',
    "body": (
        section("Why P2P here", "为什么用 P2P",
                '<p>' + bi("Distributing TB-scale model weights to thousands of hosts from a single origin saturates the origin\'s uplink. P2P shares upload bandwidth across peers.",
                           "从单源向数千主机分发 TB 级模型权重会打满上行。P2P 把上传带宽分摊到 peers。") + '</p>') +
        section("Core mechanics (BitTorrent-style)", "核心机制（BitTorrent 风格）",
                '<ul>'
                f'<li>{bi("Chunk the file into fixed-size pieces, each with a SHA-256.", "将文件切成固定大小的片段，每片带 SHA-256。")}</li>'
                f'<li>{bi("Tracker discovery: simple centralized tracker returns peer list per-chunk.", "Tracker 发现：中心化 tracker 按 chunk 返回 peer 列表。")}</li>'
                f'<li>{bi("Chunk selection: <strong>rarest-first</strong> to avoid last-chunk starvation.", "Chunk 选择：<strong>最稀缺优先</strong>，避免最后一片饥饿。")}</li>'
                f'<li>{bi("Peer selection: <strong>tit-for-tat</strong> unchoking — prefer peers that upload back to you.", "Peer 选择：<strong>tit-for-tat</strong>——优先给会回上传给你的 peer。")}</li>'
                f'<li>{bi("Super-seeding mode for initial seeder: feeds each peer a different chunk first.", "初始 seeder 的 super-seeding：先给每个 peer 不同 chunk。")}</li>'
                '</ul>') +
        section("Production tweaks for model weights", "模型权重场景的生产调优",
                '<ul>'
                f'<li>{bi("Signed manifests to prevent poisoning.", "签名 manifest 防止投毒。")}</li>'
                f'<li>{bi("Rack-aware peer selection (prefer same-AZ peers).", "机架感知 peer 选择（优先同 AZ）。")}</li>'
                f'<li>{bi("Staged rollout: 1% → 10% → 100% by AZ + validation.", "分级 rollout：1% → 10% → 100% 按 AZ 推 + 验证。")}</li>'
                '</ul>')
    ),
    "related": [
        ("distributed/partitioning.html", bi("Partitioning", "分区")),
    ],
})

QUESTIONS.append({
    "qid": "A23", "filename": "a23-100k-rps-llm.html",
    "title_en": "Handle 100K RPS for LLM Token Generation",
    "title_zh": "承载 100K RPS 的 LLM Token 生成",
    "company": "anthropic", "freq": 2, "diff": "hard",
    "extra_tags": ["Throughput", "Scale"],
    "source_html": 'Prompt: "Handle 100K RPS for LLM Token-Generation." — Exponent. Credibility <strong>B/C</strong>.',
    "body": (
        section("Back-of-envelope", "估算",
                '<ul>'
                f'<li>{bi("100K RPS × avg ~1K output tokens ≈ 100M tokens/sec (peak).", "100K RPS × 平均 ~1K 输出 tokens ≈ 100M tokens/sec（峰值）。")}</li>'
                f'<li>{bi("Single H100 can do ~5-10K tokens/sec for a 70B model → need ~10–20K H100s. Clearly multi-datacenter.", "单 H100 对 70B 模型可做 ~5-10K tokens/sec → 需要 ~1-2 万张 H100。显然是多 DC 规模。")}</li>'
                '</ul>') +
        section("How to scale", "如何扩展",
                '<ul>'
                f'<li>{bi("<strong>Horizontal replica</strong> of the inference cluster with sticky session by conversation_id.", "<strong>水平副本</strong>，按 conversation_id 粘性路由。")}</li>'
                f'<li>{bi("<strong>Regional serving</strong>: route to nearest DC; only cross-region when capacity forces it.", "<strong>区域服务</strong>：路由到最近 DC；容量不足时才跨区。")}</li>'
                f'<li>{bi("<strong>Autoscale signal</strong>: token-queue depth per model (not CPU or GPU util).", "<strong>扩容信号</strong>：每模型的 token 队列深度（而非 CPU / GPU 利用率）。")}</li>'
                f'<li>{bi("<strong>Graceful degradation</strong>: under saturation, return 429 for free tier, slower model for paid tier, full model for Enterprise.", "<strong>优雅降级</strong>：饱和时免费返 429，付费转小模型，企业保原模型。")}</li>'
                '</ul>') +
        '<p>' + bi("For the micro-architecture of each inference cluster, see A11. This question is really about fleet-level orchestration.",
                   "单个推理集群的微架构见 A11。本题本质是集群级编排。") + '</p>'
    ),
    "related": [("llm/llm-serving.html", bi("LLM serving", "LLM 推理服务"))],
})

QUESTIONS.append({
    "qid": "A24", "filename": "a24-key-value-store.html",
    "title_en": "Design a Key-Value Store (Dynamo-style)",
    "title_zh": "设计键值存储（Dynamo 风格）",
    "company": "anthropic", "freq": 2, "diff": "hard",
    "extra_tags": ["Dynamo", "Quorum"],
    "source_html": 'Prompt: "Design a Key-Value Store." — Exponent. Classic question. Credibility <strong>B/C</strong>.',
    "body": (
        section("Canonical Dynamo answer", "经典 Dynamo 解法",
                '<ul>'
                f'<li>{bi("<strong>Consistent hashing</strong> with virtual nodes for load balance.", "<strong>一致性哈希</strong> + 虚拟节点做负载均衡。")}</li>'
                f'<li>{bi("<strong>Replication factor N</strong>; quorum R/W with <code>R + W &gt; N</code> for strong consistency.", "<strong>复制因子 N</strong>；读写 quorum <code>R + W &gt; N</code> 实现强一致。")}</li>'
                f'<li>{bi("<strong>Vector clocks</strong> for conflict detection; client-side resolution or last-write-wins.", "<strong>向量时钟</strong>检测冲突；客户端解决或后写胜出。")}</li>'
                f'<li>{bi("<strong>Merkle trees</strong> for anti-entropy (detect divergent replicas).", "<strong>Merkle 树</strong>做反熵（检测分歧副本）。")}</li>'
                f'<li>{bi("<strong>Gossip</strong> for membership &amp; failure detection.", "<strong>Gossip</strong> 做成员管理与故障探测。")}</li>'
                f'<li>{bi("<strong>Hinted handoff</strong> for write availability during node failures.", "<strong>Hinted handoff</strong>确保节点故障时写入仍可用。")}</li>'
                '</ul>') +
        section("Storage engine: LSM vs B-tree", "存储引擎：LSM vs B-tree",
                '<p>' + bi("LSM-tree (like RocksDB): write-optimized, compaction background. Best default for KV. B-tree: better point-read latency but worse write amplification.",
                           "LSM 树（如 RocksDB）：写优化，后台 compaction。KV 首选。B-tree：点读延迟好但写放大差。") + '</p>') +
        section("See also", "参阅",
                '<p>' + bi("This answer is largely drawn from <em>DDIA Ch. 5/6/9</em> and <em>Alex Xu Vol. 1 Ch. 6</em>. See the study guide pages for deeper treatment.",
                           "本答案主要基于 <em>DDIA 第 5/6/9 章</em>与 <em>Alex Xu Vol. 1 第 6 章</em>。深度内容见学习手册。") + '</p>')
    ),
    "related": [
        ("distributed/replication.html", bi("Replication", "复制")),
        ("distributed/consensus.html", bi("Consensus", "共识")),
    ],
})

QUESTIONS.append({
    "qid": "A25", "filename": "a25-agentic-system.html",
    "title_en": "Design an Agentic AI System",
    "title_zh": "设计自主 Agent 系统",
    "company": "anthropic", "freq": 2, "diff": "hard",
    "extra_tags": ["Agent", "MCP", "Guardrails"],
    "source_html": 'Prompt: "Design an Agentic AI System." — Exponent (MLE role). Credibility <strong>B/C</strong>.',
    "body": (
        section("The four core components", "四大核心组件",
                '<ul>'
                f'<li>{bi("<strong>LLM reasoning engine</strong>: CoT / ToT / ReAct; produces plans and tool calls.", "<strong>LLM 推理引擎</strong>：CoT/ToT/ReAct；产出 plan 与工具调用。")}</li>'
                f'<li>{bi("<strong>Planning module</strong>: task decomposition, self-reflection, goal monitoring.", "<strong>规划模块</strong>：任务分解、自我反思、目标监控。")}</li>'
                f'<li>{bi("<strong>Memory</strong>: short-term (scratchpad) + long-term (vector store + episodic summaries).", "<strong>记忆</strong>：短期（scratchpad）+ 长期（向量库 + 情景摘要）。")}</li>'
                f'<li>{bi("<strong>Tool use</strong>: typed tool API (function calling) + MCP for standardized external integrations.", "<strong>工具使用</strong>：类型化工具 API（function calling）+ MCP 标准化外部集成。")}</li>'
                '</ul>') +

        section("Anthropic&apos;s MCP is a must-name", "必须提到 Anthropic 的 MCP",
                '<p>' + bi("Model Context Protocol reduces the N×M tool-integration problem to N+M by standardizing the agent↔tool contract. Mention it and you signal current awareness.",
                           "MCP 把 N×M 的工具集成问题降到 N+M——标准化了 Agent↔Tool 合约。提到它 = 现代认知的信号。") + '</p>') +

        section("Multi-agent patterns (Gulli Ch 7)", "多 Agent 架构（Gulli 第 7 章）",
                '<ul>'
                f'<li>{bi("<strong>Orchestrator</strong> pattern: one agent delegates to specialist agents.", "<strong>编排者</strong>模式：一个 agent 分派给专家 agent。")}</li>'
                f'<li>{bi("<strong>Blackboard</strong>: shared memory with multiple agents reading/writing.", "<strong>黑板架构</strong>：多 agent 读写共享记忆。")}</li>'
                f'<li>{bi("<strong>Conversational</strong>: agents as peers debating (actor-critic).", "<strong>对话式</strong>：agents 作为同辈辩论（演员-评论家）。")}</li>'
                f'<li>{bi("<strong>Role-based</strong>: domain-specialist agents (planner, coder, reviewer).", "<strong>角色式</strong>：领域专家 agent（规划器、编码器、评审）。")}</li>'
                '</ul>') +

        section("Safety &amp; loop-prevention", "安全与循环防护",
                '<ul>'
                f'<li>{bi("Max-step limit per plan; detect repeated same-action-same-state loops.", "每 plan 最大步数；检测相同 state+action 的循环。")}</li>'
                f'<li>{bi("Tool-call approval gate for destructive actions (delete, payment).", "破坏性操作（删除、支付）的工具调用审批门。")}</li>'
                f'<li>{bi("Sandboxed execution environment for code/shell tools.", "代码/shell 工具的沙箱执行环境。")}</li>'
                f'<li>{bi("Audit log of every tool call with inputs/outputs.", "记录每次工具调用的输入/输出到审计日志。")}</li>'
                '</ul>')
    ),
    "related": [
        ("llm/agentic-patterns.html", bi("Agentic patterns", "Agent 模式")),
        ("safety/safety-engineering.html", bi("Safety", "安全")),
    ],
})

QUESTIONS.append({
    "qid": "A26", "filename": "a26-web-crawler.html",
    "title_en": "Design a Web Crawler",
    "title_zh": "设计网页爬虫",
    "company": "anthropic", "freq": 2, "diff": "hard",
    "extra_tags": ["Crawler", "Dedup"],
    "source_html": 'Prompt: "Design a Web Crawler." — Exponent, programhelp.net. Credibility <strong>B/C</strong>.',
    "body": (
        '<p>' + bi("Core mechanics identical to O10 (OpenAI version). Anthropic&apos;s version often emphasizes multi-threaded / async workers and rate control. See O10 for the full architecture.",
                   "核心机制与 O10（OpenAI 版本）一致。Anthropic 版本常强调多线程/异步 worker 与速率控制。完整架构见 O10。") + '</p>' +
        section("Anthropic-specific follow-ups", "Anthropic 风格追问",
                '<ul>'
                f'<li>{bi("How would you safely filter out sensitive / restricted content during crawling?", "爬取过程中如何安全过滤敏感/受限内容？")}</li>'
                f'<li>{bi("How do you handle dynamic JS-rendered pages? (Headless browser subset — expensive.)", "如何处理 JS 动态渲染页面？（Headless 浏览器子集——成本高。）")}</li>'
                f'<li>{bi("How do you avoid creating legal / ethical issues (robots.txt compliance, copyright)?", "如何避免法律/伦理问题（robots.txt 合规、版权）？")}</li>'
                '</ul>')
    ),
    "related": [
        ("classical/rate-limiter.html", bi("Rate limiter", "限流器")),
    ],
})

QUESTIONS.append({
    "qid": "A27", "filename": "a27-banking-app.html",
    "title_en": "Design a Banking App",
    "title_zh": "设计银行应用",
    "company": "anthropic", "freq": 2, "diff": "medium",
    "diff_label": "Medium-Hard",
    "extra_tags": ["ACID", "Ledger", "Audit"],
    "source_html": 'Prompt: "Design a Banking App." — interviewing.io. Credibility <strong>C/D</strong>.',
    "body": (
        section("Core concerns (traditional SD)", "核心考察（传统系统设计）",
                '<ul>'
                f'<li>{bi("<strong>Double-entry ledger</strong>: every transfer = two entries (debit + credit). Enforce <code>SUM(balance) = 0</code> invariant.", "<strong>双重记账</strong>：每次转账 = 两条记录（借 + 贷）。强制 <code>SUM(balance) = 0</code> 不变量。")}</li>'
                f'<li>{bi("<strong>Idempotent transfers</strong>: idempotency_key; safe retries.", "<strong>幂等转账</strong>：idempotency_key；重试安全。")}</li>'
                f'<li>{bi("<strong>Two-phase commit</strong> or <strong>saga</strong> for cross-account / cross-system transfers.", "<strong>两阶段提交</strong>或<strong>Saga</strong>用于跨账户/跨系统转账。")}</li>'
                f'<li>{bi("<strong>Audit log</strong>: append-only, cryptographically chained entries.", "<strong>审计日志</strong>：追加式、密码学链接条目。")}</li>'
                f'<li>{bi("<strong>Fraud detection</strong>: rules + ML model; decision latency &lt; 100ms.", "<strong>反欺诈</strong>：规则 + ML；决策延迟 &lt; 100ms。")}</li>'
                '</ul>') +
        section("Data model", "数据模型",
                '<pre><code>Account(account_id, owner_id, currency, status)\n'
                'LedgerEntry(entry_id, account_id, amount, currency, ref_tx_id, created_at)\n'
                '-- Invariant: for each tx, SUM(entries.amount) = 0\n'
                'Transaction(tx_id, idempotency_key, status, initiated_at)</code></pre>')
    ),
    "related": [
        ("distributed/transactions.html", bi("Transactions &amp; isolation", "事务与隔离")),
    ],
})

QUESTIONS.append({
    "qid": "A28", "filename": "a28-distributed-search-1b.html",
    "title_en": "Distributed Search for 1B Documents @ 1M QPS",
    "title_zh": "1B 文档 @ 1M QPS 的分布式搜索",
    "company": "anthropic", "freq": 3, "diff": "hard",
    "extra_tags": ["Scale", "Sharding"],
    "source_html": 'Prompt: "Design a Distributed Search System for 1B documents, 1M QPS." — Medium Anqi Silvia 2025; linkjob.ai. Credibility <strong>C</strong>.',
    "body": (
        section("Scale math first", "先讲规模",
                '<ul>'
                f'<li>{bi("1B docs × avg 10 KB = 10 TB index → ~100 shards at 100 GB each.", "1B 文档 × 平均 10 KB = 10 TB 索引 → 约 100 分片 × 100 GB。")}</li>'
                f'<li>{bi("1M QPS → with 100 shards, each shard serves ~10K QPS. Need multiple replicas per shard.", "1M QPS → 100 分片下每分片 ~10K QPS。每分片需多副本。")}</li>'
                f'<li>{bi("If LLM re-rank / generate involved, GPU cost dominates — rate-limit or skip for bulk queries.", "若涉及 LLM 重排/生成，GPU 成本主导——大批量 query 应限流或跳过。")}</li>'
                '</ul>') +
        section("Architecture", "架构",
                mermaid("""flowchart LR
  Q[Query] --> GW[Gateway + Rate Limit]
  GW --> CACHE[(L1 Cache / Edge)]
  CACHE --> L2[(Semantic Cache)]
  L2 --> FAN[Scatter-Gather]
  FAN --> S1[Shard 1] & S2[Shard 2] & S3[Shard N]
  S1 & S2 & S3 --> MER[Top-K Merge]
  MER --> RE[Reranker / LLM (optional)]
  RE --> Q""")) +
        section("Hot-spot mitigation", "热点规避",
                '<ul>'
                f'<li>{bi("Cache top-5% queries in edge cache (cuts 40%+ load at large scale).", "边缘缓存热门 top-5% query（大规模下可削 40%+ 负载）。")}</li>'
                f'<li>{bi("Re-shard on hot keys; consistent hashing with virtual nodes.", "按热 key 重分片；一致性哈希 + 虚拟节点。")}</li>'
                f'<li>{bi("Semantic cache (embedding-proximity) catches near-duplicate queries.", "语义缓存（embedding 近似）捕捉近似 query。")}</li>'
                '</ul>') +
        section("GPU memory optimization", "GPU 显存优化",
                '<ul>'
                f'<li>{bi("PagedAttention for LLM rerank layer.", "LLM 重排层用 PagedAttention。")}</li>'
                f'<li>{bi("Prefix caching for a shared system prompt.", "共享 system prompt 的 prefix caching。")}</li>'
                f'<li>{bi("Quantization (FP8/INT8) for reranker.", "重排器量化（FP8/INT8）。")}</li>'
                '</ul>')
    ),
    "related": [
        ("llm/llm-serving.html", bi("LLM serving", "LLM 推理服务")),
        ("llm/rag.html", "RAG"),
    ],
})

QUESTIONS.append({
    "qid": "A29", "filename": "a29-model-serving-platform.html",
    "title_en": "Model Serving Platform for LLMs",
    "title_zh": "LLM 模型服务平台",
    "company": "anthropic", "freq": 3, "diff": "hard",
    "extra_tags": ["Open-ended", "Platform"],
    "source_html": 'Prompt: "Design a Model Serving Platform for LLMs." — linkjob.ai. Open-ended; you must drive scope. Credibility <strong>C</strong>.',
    "body": (
        section("Open-ended — drive the conversation", "开放式——主导对话",
                '<p>' + bi("Anthropic explicitly evaluates \"driving the conversation.\" Your first move is <strong>to state what in-scope and out-of-scope</strong> means. Example: \"I&apos;ll focus on multi-tenant inference serving for an internal fleet of models. I&apos;m out of scope on training and fine-tuning. Does that work?\"",
                           "Anthropic 明确评估「主导对话」。你第一步要<strong>声明在 / 不在范围内</strong>。例：「我关注多租户内部模型的推理服务；不覆盖训练与微调。这样可以吗？」") + '</p>') +
        section("Skeleton to follow", "推荐骨架",
                '<ol>'
                f'<li>{bi("Clarify requirements: which models, QPS, SLOs, tenants.", "澄清需求：哪些模型、QPS、SLO、租户。")}</li>'
                f'<li>{bi("High-level architecture: control plane / data plane, refer to A15.", "高层架构：控制面 / 数据面，参考 A15。")}</li>'
                f'<li>{bi("Safety / latency / reliability trade-offs explicitly.", "显式讨论 safety / 延迟 / 可靠性权衡。")}</li>'
                f'<li>{bi("Pick one component (batcher) and go deep (see A11, A12).", "挑一个组件（batcher）深入（见 A11、A12）。")}</li>'
                f'<li>{bi("Close with capacity / cost math.", "以容量 / 成本估算收尾。")}</li>'
                '</ol>') +
        callout("anthropic", "Signal vs noise", "信号 vs 噪声",
                "Asking \"what should I focus on?\" is a disqualifier. State a plan, then ask \"does this match what you want to explore?\" — that reads as senior.",
                "问「我该关注什么？」是一票否决。先给方案，再问「这是否符合你想探讨的方向？」——听起来就是高级工程师。")
    ),
    "related": [
        ("llm/llm-serving.html", bi("LLM serving", "LLM 推理服务")),
    ],
})


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for q in QUESTIONS:
        render_page(q)
    print(f"\nGenerated {len(QUESTIONS)} question detail pages.")
