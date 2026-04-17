"""Foundations topics: interview framework + back-of-envelope estimation."""

TOPICS = [
    {
        "category": "foundations",
        "slug": "interview-framework",
        "title_en": "The Interview Framework",
        "title_zh": "系统设计面试通用框架",
        "lead_en": "A 45-minute blueprint: Requirements → Scale → API → Data Model → Architecture → Deep Dive, tuned for OpenAI and Anthropic interview panels.",
        "lead_zh": "45 分钟蓝图：需求 → 规模 → API → 数据模型 → 架构 → 深挖，针对 OpenAI 与 Anthropic 面试场景定制。",
        "tags": ["45-min blueprint", "Acing SDI Ch.2", "OpenAI/Anthropic tweaks"],
        "refs": ["Alex Xu V1 Ch.3", "Acing SDI Ch.2", "Chip Huyen DMLS Ch.2"],
        "toc_en": [
            "Why a framework at all",
            "Phase 1 — Requirements & scoping (5 min)",
            "Phase 2 — Back-of-envelope scale (5 min)",
            "Phase 3 — API surface (5 min)",
            "Phase 4 — Data model & storage (5 min)",
            "Phase 5 — High-level architecture (10 min)",
            "Phase 6 — Deep dive + wrap (15 min)",
            "OpenAI vs Anthropic-specific tweaks",
        ],
        "toc_zh": [
            "为什么需要框架",
            "阶段一 — 需求澄清（5 分钟）",
            "阶段二 — 规模估算（5 分钟）",
            "阶段三 — API 设计（5 分钟）",
            "阶段四 — 数据模型与存储（5 分钟）",
            "阶段五 — 高层架构（10 分钟）",
            "阶段六 — 深挖与收尾（15 分钟）",
            "OpenAI 与 Anthropic 特定调整",
        ],
        "body_en": r"""
<h2 id="s1">Why a framework at all</h2>
<p>A system design interview is not an oral exam on distributed systems trivia; it is a structured conversation under time pressure where the interviewer scores your <em>engineering judgment</em>. Alex Xu's 4-step template (<code>scope → high-level → deep-dive → wrap</code>) and Zhiyong Tan's longer checklist in <em>Acing the System Design Interview</em> Chapter 2 both converge on the same idea: spend the first 10 minutes nailing the problem, the next 15 sketching a reasonable baseline, and the last 20 demonstrating depth on one or two components the interviewer cares about.</p>
<p>The framework below is the tightest version that still survives a 45-minute slot. It prevents the two most common failure modes: <strong>premature architecture</strong> (drawing boxes before you know the QPS) and <strong>shallow breadth</strong> (describing seven services at the same level of detail, none of them deeply).</p>
<div class="callout tip"><h4>Source cross-reference</h4><p>Alex Xu V1 Ch.3 gives the 4-step skeleton; Acing SDI Ch.2 adds the requirement-discussion taxonomy (functional, non-functional, constraints); Chip Huyen DMLS Ch.2 supplies the ML-specific framing (objective → data → model → deployment) you'll need for any LLM/ML question.</p></div>

<h2 id="s2">Phase 1 — Requirements &amp; scoping (5 min)</h2>
<p>Before touching the whiteboard, extract three lists:</p>
<ul>
  <li><strong>Functional requirements</strong>: the two or three core user journeys. "Upload video, watch video, search video" is enough for YouTube; do <em>not</em> list 15 features.</li>
  <li><strong>Non-functional requirements</strong> (NFRs): availability target (three-nines = ~8.76 h downtime/year, four-nines = ~52 min), p99 latency budget, durability, consistency model, regulatory (GDPR, HIPAA, SOC2).</li>
  <li><strong>Explicit out-of-scope</strong>: "We will not design the mobile client, the billing system, or the CDN provider." This buys you back 5 minutes later when the interviewer asks.</li>
</ul>
<p>Write NFRs as numbers, never adjectives. "Low latency" is a junior answer. "p99 read &lt; 100 ms in-region, p99 write &lt; 300 ms, 99.95% availability, RPO &lt; 1 min, RTO &lt; 5 min" is a staff answer.</p>
<div class="callout warn"><h4>Anti-pattern</h4><p>Do not start listing databases (<em>"I'll use Postgres and Redis and Kafka..."</em>) before requirements are nailed. Interviewers silently flag this as pattern-matching without thought. Stay on requirements until you can state the problem back in one sentence.</p></div>

<h2 id="s3">Phase 2 — Back-of-envelope scale (5 min)</h2>
<p>Convert product assumptions into numeric targets. For a chat app: 500 M DAU × 40 messages/day = 20 B messages/day ≈ 230 k writes/sec average, ~5× for peak = 1.15 M writes/sec. Storage at 200 bytes/message × 20 B/day = 4 TB/day ≈ 1.5 PB/year.</p>
<p>You will refer back to these numbers in every later phase. A 1 M QPS system needs horizontal sharding from day one; a 5 k QPS system can live on a single Postgres primary with read replicas. Getting the order of magnitude right is 80% of the value; precision past one significant figure is wasted breath.</p>
<p>See the companion page on <a href="../../guide/foundations/estimation.html">estimation</a> for the constants (Jeff Dean numbers, latency cheat-sheet, LLM-token economics).</p>

<h2 id="s4">Phase 3 — API surface (5 min)</h2>
<p>Define 3–6 endpoints, typed. Example for a URL shortener:</p>
<pre><code>POST /v1/links          { long_url, custom_alias? } -&gt; { short_url, expires_at }
GET  /v1/{alias}        302 -&gt; long_url
GET  /v1/links/{alias}  -&gt; { clicks, created_at, owner }
DELETE /v1/links/{alias}</code></pre>
<p>State explicitly: auth model (JWT, mTLS, API key), idempotency keys on <code>POST</code>, pagination style (cursor vs offset), and rate-limit bucket. For LLM-flavored questions, always mention <strong>streaming</strong> responses (<code>text/event-stream</code> or gRPC server-streaming) and <strong>tool-call schemas</strong>.</p>
<div class="callout openai"><h4>OpenAI-specific</h4><p>OpenAI interviews love <code>/v1/chat/completions</code>-shaped APIs. Be ready to discuss SSE framing, <code>stream_options</code>, function-calling JSON schemas, and how you would backpressure a slow client without dropping the generation.</p></div>

<h2 id="s5">Phase 4 — Data model &amp; storage (5 min)</h2>
<p>Pick a primary store and state the schema in 3–5 lines. Justify the choice with one sentence referencing access pattern, not brand loyalty.</p>
<ul>
  <li><strong>OLTP key-value with predictable partition</strong> (user-scoped inbox, session store): DynamoDB, Cassandra, FoundationDB.</li>
  <li><strong>Relational with joins &amp; strong consistency</strong>: Postgres (single-region up to ~50 k writes/sec), Spanner / CockroachDB for global.</li>
  <li><strong>Append-only event log</strong>: Kafka + tiered storage, or a purpose-built log like Pulsar.</li>
  <li><strong>Blob</strong>: S3 / GCS, 11 nines durability, ~5 ms first-byte from same region.</li>
  <li><strong>Vector</strong>: pgvector (&lt;10 M), Milvus / Pinecone / Turbopuffer (100 M+). See the <a href="../../arena/questions/o18-vector-database.html">vector DB arena question</a>.</li>
</ul>

<h2 id="s6">Phase 5 — High-level architecture (10 min)</h2>
<p>Draw 5–8 boxes. Client → load balancer → stateless service tier → cache + primary store + async queue + downstream workers. Label every arrow with the protocol (HTTP/2, gRPC, Kafka topic) and the direction of data flow.</p>
<div class="mermaid-container"><pre class="mermaid">
flowchart LR
    C[Client] --&gt;|HTTPS| LB[Global LB / Anycast]
    LB --&gt; API[Stateless API tier]
    API --&gt;|read-through| CACHE[(Redis cluster)]
    API --&gt;|writes| DB[(Primary store)]
    API --&gt;|events| Q[[Kafka]]
    Q --&gt; W[Workers]
    W --&gt; DB
    W --&gt;|cold| OBJ[(S3)]
</pre></div>
<p>Call out at least one <strong>concrete number</strong> per box: "Redis cluster sized for 100 k ops/sec/node, 6 shards, 3 replicas = 1.8 M ops/sec cluster throughput." Numbers separate candidates who have run systems from those who have only read about them.</p>

<h2 id="s7">Phase 6 — Deep dive + wrap (15 min)</h2>
<p>The interviewer will nominate one or two components for deep-dive. Common targets:</p>
<ul>
  <li><em>How do you keep the cache consistent with the primary?</em> → write-through vs cache-aside, invalidation lag, the 2013 Facebook memcached paper's "leases" trick.</li>
  <li><em>What if the leader DB fails?</em> → failover playbook: consensus on new leader (etcd/Raft), fencing tokens (<a href="../../guide/distributed/consensus.html">see consensus</a>), RPO window, split-brain avoidance.</li>
  <li><em>How do you rate-limit?</em> → token bucket at the edge, sliding-window log at user scope (see <a href="../../arena/questions/o17-rate-limiter.html">rate-limiter arena</a>).</li>
</ul>
<p>Reserve 2 minutes at the end for an explicit <strong>trade-off summary</strong>: "If we needed global strong consistency I would swap Postgres for Spanner and accept 2× write latency; if read volume doubled, add regional read replicas with bounded staleness." This is the single highest-signal minute of the interview.</p>

<h2 id="s8">OpenAI vs Anthropic-specific tweaks</h2>
<p>The framework is the same; the emphasis shifts.</p>
<table>
  <thead><tr><th>Dimension</th><th>OpenAI style</th><th>Anthropic style</th></tr></thead>
  <tbody>
    <tr><td>Opening question</td><td>Product-flavored ("Design ChatGPT memory")</td><td>Safety/eval-flavored ("Design a red-team harness")</td></tr>
    <tr><td>Depth target</td><td>GPU scheduling, KV-cache sharing, streaming protocol</td><td>Policy pipeline, audit logs, rollback, sandboxing</td></tr>
    <tr><td>Preferred stack cues</td><td>Python + Rust services, Triton, vLLM, Kubernetes</td><td>Python + Rust, custom inference stack, strong typing, extensive evals</td></tr>
    <tr><td>Must-mention</td><td>Throughput/$ and p50 vs p99 under batching</td><td>Constitutional AI feedback loop, refusal metrics, provenance</td></tr>
  </tbody>
</table>
<div class="callout anthropic"><h4>Anthropic-specific</h4><p>Anthropic interviewers routinely pivot to safety: "What happens if a prompt tries to exfiltrate another user's context?" Have a canned answer involving tenant isolation at the process level, scrubbed logs, and a circuit breaker that kills generations on policy hits. Reference Constitutional AI and the <a href="../../guide/safety/safety-engineering.html">threat modeling page</a> if they push.</p></div>
<div class="callout warn"><h4>Final anti-pattern</h4><p>Running out of time on Phase 5 and never reaching deep-dive is the single most common reason strong candidates fail. Set a mental timer: if you are still drawing boxes at minute 25, stop, pick one component, and go deep.</p></div>
""",
        "body_zh": r"""
<h2 id="s1">为什么需要框架</h2>
<p>系统设计面试不是分布式系统知识的口试，而是在时间压力下的结构化对话，面试官评估的是你的<em>工程判断力</em>。Alex Xu 的 4 步模板（<code>范围 → 高层 → 深挖 → 收尾</code>）与 Zhiyong Tan 在《Acing the System Design Interview》第 2 章的更长清单，核心思想一致：前 10 分钟锁定问题，中间 15 分钟画出合理基线，最后 20 分钟在一到两个组件上展示深度。</p>
<p>下面这套框架是仍能在 45 分钟内走完的最紧凑版本。它避免了两种常见失败：<strong>过早架构</strong>（还没算 QPS 就开始画框）和<strong>浅层广度</strong>（七个服务全部停在同一个粒度，没有任何一个讲透）。</p>
<div class="callout tip"><h4>来源交叉引用</h4><p>Alex Xu V1 第 3 章给出 4 步骨架；Acing SDI 第 2 章补充需求讨论分类（功能性、非功能性、约束）；Chip Huyen DMLS 第 2 章提供 ML 特有的问题框架（目标 → 数据 → 模型 → 部署），回答 LLM/ML 题必备。</p></div>

<h2 id="s2">阶段一 — 需求澄清（5 分钟）</h2>
<p>在动笔之前，先提炼三份清单：</p>
<ul>
  <li><strong>功能需求</strong>：两到三条核心用户旅程。YouTube 题目说「上传视频、观看视频、搜索视频」就够了，不要列 15 个功能。</li>
  <li><strong>非功能需求</strong>（NFR）：可用性目标（三个九 ≈ 每年 8.76 小时停机，四个九 ≈ 52 分钟）、p99 延迟预算、持久性、一致性模型、合规要求（GDPR、HIPAA、SOC2）。</li>
  <li><strong>明确的范围外</strong>：「我们不设计移动端、计费系统、CDN 提供商。」这在后面能帮你省回 5 分钟。</li>
</ul>
<p>NFR 要写成数字，不要写形容词。「低延迟」是初级答案；「同区域 p99 读 &lt; 100 ms，p99 写 &lt; 300 ms，可用性 99.95%，RPO &lt; 1 分钟，RTO &lt; 5 分钟」是 staff 答案。</p>
<div class="callout warn"><h4>反模式</h4><p>需求还没锁定就开始罗列数据库（「我用 Postgres 加 Redis 加 Kafka……」）。面试官会默默扣分：这是无思考的模式匹配。坚持到你能用一句话把问题复述出来。</p></div>

<h2 id="s3">阶段二 — 规模估算（5 分钟）</h2>
<p>把产品假设换成数字。聊天应用：5 亿日活 × 每天 40 条消息 = 200 亿条/天 ≈ 23 万写入/秒的平均值，峰值按 5× 算 = 115 万写入/秒。存储按 200 字节/条 × 200 亿/天 = 4 TB/天 ≈ 1.5 PB/年。</p>
<p>后续每个阶段都会引用这些数字。100 万 QPS 的系统从第一天就要水平分片；5000 QPS 的系统单主 Postgres 加读副本完全能扛。数量级正确是 80% 的价值，精度到一位有效数字之外都是浪费时间。</p>
<p>常数见配套页面 <a href="../../guide/foundations/estimation.html">估算</a>（Jeff Dean 数字、延迟速查表、LLM token 经济学）。</p>

<h2 id="s4">阶段三 — API 设计（5 分钟）</h2>
<p>定义 3–6 个带类型的端点。短链接服务示例：</p>
<pre><code>POST /v1/links          { long_url, custom_alias? } -&gt; { short_url, expires_at }
GET  /v1/{alias}        302 -&gt; long_url
GET  /v1/links/{alias}  -&gt; { clicks, created_at, owner }
DELETE /v1/links/{alias}</code></pre>
<p>明确说明：鉴权方式（JWT、mTLS、API key）、<code>POST</code> 的幂等 key、分页方式（cursor vs offset）、限流桶。LLM 类题目一定要提<strong>流式响应</strong>（<code>text/event-stream</code> 或 gRPC 服务端流）与<strong>工具调用 schema</strong>。</p>
<div class="callout openai"><h4>OpenAI 专属</h4><p>OpenAI 面试偏爱 <code>/v1/chat/completions</code> 形状的 API。准备好 SSE 帧格式、<code>stream_options</code>、function calling 的 JSON schema，以及如何在不中断生成的前提下对慢客户端施加反压。</p></div>

<h2 id="s5">阶段四 — 数据模型与存储（5 分钟）</h2>
<p>选一个主存储，写 3–5 行 schema。用一句话根据访问模式（不是品牌偏好）证明选择合理。</p>
<ul>
  <li><strong>OLTP 键值，分区可预测</strong>（用户收件箱、会话）：DynamoDB、Cassandra、FoundationDB。</li>
  <li><strong>关系型，需 join 与强一致</strong>：Postgres（单区域到 ~5 万写/秒）；全球场景用 Spanner / CockroachDB。</li>
  <li><strong>仅追加事件日志</strong>：Kafka + 分层存储，或 Pulsar。</li>
  <li><strong>对象存储</strong>：S3 / GCS，11 个九的持久性，同区域首字节 ~5 ms。</li>
  <li><strong>向量库</strong>：pgvector（&lt;1000 万）、Milvus / Pinecone / Turbopuffer（1 亿+）。见 <a href="../../arena/questions/o18-vector-database.html">向量数据库真题</a>。</li>
</ul>

<h2 id="s6">阶段五 — 高层架构（10 分钟）</h2>
<p>画 5–8 个框：客户端 → 负载均衡 → 无状态服务层 → 缓存 + 主存储 + 异步队列 + 下游 worker。每条箭头标明协议（HTTP/2、gRPC、Kafka topic）和数据流方向。</p>
<div class="mermaid-container"><pre class="mermaid">
flowchart LR
    C[客户端] --&gt;|HTTPS| LB[全局 LB / Anycast]
    LB --&gt; API[无状态 API 层]
    API --&gt;|read-through| CACHE[(Redis 集群)]
    API --&gt;|writes| DB[(主存储)]
    API --&gt;|events| Q[[Kafka]]
    Q --&gt; W[Workers]
    W --&gt; DB
    W --&gt;|冷数据| OBJ[(S3)]
</pre></div>
<p>每个框至少报出一个<strong>具体数字</strong>：「Redis 集群按单节点 10 万 ops/秒规划，6 分片 × 3 副本 = 集群 180 万 ops/秒。」数字能区分真正跑过系统的人和只读过书的人。</p>

<h2 id="s7">阶段六 — 深挖与收尾（15 分钟）</h2>
<p>面试官会点一到两个组件深挖。常见目标：</p>
<ul>
  <li><em>缓存如何与主存储保持一致？</em> → write-through vs cache-aside，失效延迟，2013 年 Facebook memcached 论文里的「lease」技巧。</li>
  <li><em>主库挂了怎么办？</em> → 故障切换：用 etcd/Raft 选主、fencing token（见 <a href="../../guide/distributed/consensus.html">共识页面</a>）、RPO 窗口、脑裂防范。</li>
  <li><em>如何限流？</em> → 边缘 token bucket + 用户维度滑动窗口日志（见 <a href="../../arena/questions/o17-rate-limiter.html">限流真题</a>）。</li>
</ul>
<p>最后 2 分钟留给明确的<strong>权衡总结</strong>：「如果需要全球强一致，我会把 Postgres 换成 Spanner 并接受 2× 写延迟；如果读量翻倍，增加有界陈旧的区域读副本。」这是整场面试信号最强的一分钟。</p>

<h2 id="s8">OpenAI 与 Anthropic 特定调整</h2>
<p>框架一样，重心不同。</p>
<table>
  <thead><tr><th>维度</th><th>OpenAI 风格</th><th>Anthropic 风格</th></tr></thead>
  <tbody>
    <tr><td>开场题</td><td>产品风（「设计 ChatGPT 记忆」）</td><td>安全/评测风（「设计红队 harness」）</td></tr>
    <tr><td>深挖方向</td><td>GPU 调度、KV-cache 共享、流式协议</td><td>策略流水线、审计日志、回滚、沙箱</td></tr>
    <tr><td>偏好栈</td><td>Python + Rust、Triton、vLLM、K8s</td><td>Python + Rust、自研推理栈、强类型、大量 eval</td></tr>
    <tr><td>必须提</td><td>吞吐/$ 与 batching 下的 p50/p99</td><td>Constitutional AI 反馈闭环、拒答率指标、溯源</td></tr>
  </tbody>
</table>
<div class="callout anthropic"><h4>Anthropic 专属</h4><p>Anthropic 面试官经常转向安全：「如果一个 prompt 试图窃取另一用户的上下文怎么办？」请准备好答案：进程级租户隔离、日志脱敏、策略命中时熔断生成。若被追问，引用 Constitutional AI 和 <a href="../../guide/safety/safety-engineering.html">威胁建模页面</a>。</p></div>
<div class="callout warn"><h4>最终反模式</h4><p>在阶段五卡住、从未进入深挖，是强候选人失败的头号原因。心里设个闹钟：第 25 分钟还在画框，立刻停、挑一个组件、深入下去。</p></div>
""",
        "links": [
            ("Next topic", "下一主题", "../../guide/foundations/estimation.html",
             "Back-of-envelope estimation", "规模估算"),
            ("Deep dive", "深入", "../../guide/distributed/replication-consistency.html",
             "Replication & consistency", "复制与一致性"),
            ("Arena", "真题", "../../arena/questions/a25-agentic-system.html",
             "Design an agentic system", "设计一个 Agent 系统"),
            ("Arena", "真题", "../../arena/questions/o17-rate-limiter.html",
             "Rate-limiter walkthrough", "限流器演练"),
            ("Related", "相关", "../../guide/llm/llm-serving.html",
             "LLM serving stack", "LLM 服务栈"),
        ],
    },

    {
        "category": "foundations",
        "slug": "estimation",
        "title_en": "Back-of-Envelope Estimation",
        "title_zh": "规模估算速算",
        "lead_en": "Latency constants, storage/bandwidth arithmetic, Jeff Dean numbers, and LLM-token economics — the math every senior candidate does in their head.",
        "lead_zh": "延迟常数、存储/带宽算术、Jeff Dean 数字、LLM token 经济学——senior 候选人心算的全部内容。",
        "tags": ["Jeff Dean numbers", "Alex Xu V1 Ch.2", "token economics"],
        "refs": ["Alex Xu V1 Ch.2", "ByteByteGo latency cheat-sheet"],
        "toc_en": [
            "The constants table",
            "Units and powers of two",
            "QPS and storage worked examples",
            "Bandwidth and egress costs",
            "LLM-token economics",
            "Common mistakes and sanity checks",
        ],
        "toc_zh": [
            "常数表",
            "单位与 2 的幂",
            "QPS 与存储实例",
            "带宽与出口成本",
            "LLM token 经济学",
            "常见错误与合理性检查",
        ],
        "body_en": r"""
<h2 id="s1">The constants table</h2>
<p>Memorize the following. In an interview you will not have time to derive them; Alex Xu V1 Ch.2 and the ByteByteGo latency cheat-sheet both publish near-identical versions because they all descend from Jeff Dean's "Numbers Everyone Should Know" (2009, updated by Colin Scott for 2020 hardware).</p>
<table>
  <thead><tr><th>Operation</th><th>Latency</th><th>Mental anchor</th></tr></thead>
  <tbody>
    <tr><td>L1 cache hit</td><td>0.5 ns</td><td>free</td></tr>
    <tr><td>Branch mispredict</td><td>5 ns</td><td>free</td></tr>
    <tr><td>L2 cache hit</td><td>7 ns</td><td>free</td></tr>
    <tr><td>Mutex lock/unlock</td><td>25 ns</td><td>free</td></tr>
    <tr><td>Main memory reference</td><td>100 ns</td><td>100× L1</td></tr>
    <tr><td>Compress 1 KB w/ Zstd</td><td>2 µs</td><td>20× memory ref</td></tr>
    <tr><td>Send 2 KB over 1 Gbps</td><td>20 µs</td><td>network floor</td></tr>
    <tr><td>SSD random read (4 KB)</td><td>100 µs</td><td>1000× memory ref</td></tr>
    <tr><td>Read 1 MB sequentially from SSD</td><td>250 µs</td><td>~4 GB/s SSD BW</td></tr>
    <tr><td>Round-trip within same DC</td><td>500 µs</td><td>half a millisecond</td></tr>
    <tr><td>Read 1 MB from network</td><td>1 ms</td><td>~1 GB/s DC link</td></tr>
    <tr><td>Disk seek (HDD)</td><td>10 ms</td><td>legacy only</td></tr>
    <tr><td>TLS handshake (new)</td><td>50–100 ms</td><td>RTT × 2</td></tr>
    <tr><td>California → Netherlands RTT</td><td>150 ms</td><td>speed-of-light floor</td></tr>
    <tr><td>GPU H100 FLOP/s (BF16)</td><td>989 TFLOP/s</td><td>~1 PFLOP/s nominal</td></tr>
    <tr><td>H100 HBM3 bandwidth</td><td>3.35 TB/s</td><td>memory-bound regime</td></tr>
  </tbody>
</table>
<div class="callout tip"><h4>Source cross-reference</h4><p>Rows 1–13 follow Alex Xu V1 Ch.2 almost verbatim; the GPU rows come from NVIDIA H100 datasheets and are essential for any LLM-serving question. For the visual version consult the ByteByteGo "Latency Numbers Every Programmer Should Know" sheet.</p></div>

<h2 id="s2">Units and powers of two</h2>
<p>Mix-ups here lose interviews. Commit these to muscle memory:</p>
<ul>
  <li>2<sup>10</sup> ≈ 10<sup>3</sup> = 1 K (kilo)</li>
  <li>2<sup>20</sup> ≈ 10<sup>6</sup> = 1 M (mega)</li>
  <li>2<sup>30</sup> ≈ 10<sup>9</sup> = 1 G (giga)</li>
  <li>2<sup>40</sup> ≈ 10<sup>12</sup> = 1 T (tera)</li>
  <li>2<sup>50</sup> ≈ 10<sup>15</sup> = 1 P (peta)</li>
  <li>86 400 s/day ≈ 10<sup>5</sup>. 2.6 × 10<sup>6</sup> s/month. 3.15 × 10<sup>7</sup> s/year.</li>
  <li>1 year ≈ π × 10<sup>7</sup> seconds (a useful physicist trick).</li>
</ul>
<p>Corollary: if something happens "once per second per user" and you have 10 M users, that is 10 M/s average. Peak is usually 2–5× average for consumer apps; for B2B with business-hour traffic, peak-to-avg ratio is often 8–10×.</p>

<h2 id="s3">QPS and storage worked examples</h2>
<h3>Example 1 — Chat app (Alex Xu Ch.12 style)</h3>
<p>500 M DAU, 40 messages/day each. Daily writes = 2 × 10<sup>10</sup>. Average write QPS = 2 × 10<sup>10</sup> / 10<sup>5</sup> = 2 × 10<sup>5</sup> = 200 k/s. Peak (3×) ≈ 600 k/s. Reads are fan-out: average 3 recipients per message → 600 k/s writes amplify to 1.8 M/s reads. Storage: 200 bytes/message × 2 × 10<sup>10</sup> = 4 TB/day = 1.46 PB/year. With 3× replication and 30% overhead → ~6 PB/year actually provisioned.</p>

<h3>Example 2 — URL shortener (Alex Xu Ch.8)</h3>
<p>100 M new URLs/month → 100M / (2.6 × 10<sup>6</sup> s) ≈ 40 writes/sec average. 10:1 read-to-write → 400 reads/sec. This is a <em>single Postgres</em> problem, not a shard-from-day-one problem. 10 years × 100 M = 1.2 B rows × 500 bytes = 600 GB. Fits on one NVMe.</p>

<h3>Example 3 — Photo upload (Flickr / Acing Ch.12)</h3>
<p>10 M uploads/day, 3 MB original + 5 thumbnail sizes (200 KB combined). Write bandwidth: 10<sup>7</sup> × 3.2 MB / 86 400 s ≈ 370 MB/s ingress. Storage: 32 TB/day → 11.7 PB/year (before replication). Glacier/cold tier at $0.004/GB/mo → $45 k/month for 11.7 PB in cold.</p>

<h2 id="s4">Bandwidth and egress costs</h2>
<p>In 2025 on AWS us-east-1, egress is ~$0.09/GB for the first 10 TB/month, dropping to $0.05/GB past 150 TB/month. Serving 1 PB of video out of S3 raw = ~$50 k/month in egress alone, which is why YouTube/Netflix-scale systems use <em>peered CDN egress</em> at $0.002–0.01/GB (50–100× cheaper). This is a concrete number the interviewer will mine for: always mention CDN offload for any read-heavy blob workload.</p>
<ul>
  <li>1 Gbps = 125 MB/s = 10.8 TB/day.</li>
  <li>10 Gbps = ~1.1 PB/day (a fat server NIC).</li>
  <li>100 Gbps (modern DC spine) = ~10.8 PB/day per link.</li>
</ul>
<div class="callout warn"><h4>Anti-pattern</h4><p>Forgetting egress math in video/audio/LLM-streaming designs. A candidate who designs "YouTube" without acknowledging that raw S3 egress would cost more than the entire revenue of a small YouTube clone has failed the cost-awareness check.</p></div>

<h2 id="s5">LLM-token economics</h2>
<p>This is the OpenAI/Anthropic-specific layer that the classic books do not cover. Memorize:</p>
<ul>
  <li>1 English token ≈ 0.75 words ≈ 4 characters.</li>
  <li>A 2000-word document ≈ 2700 tokens.</li>
  <li>GPT-4-class dense model at 70 B parameters, BF16: ~140 GB weights → fits on 2× H100 (80 GB each) with KV cache.</li>
  <li><strong>Prefill</strong> is compute-bound (FLOPs ≈ 2 × params × prompt_tokens); <strong>decode</strong> is memory-bandwidth-bound (bytes moved ≈ params_bytes per output token).</li>
  <li>On H100 BF16: decode throughput ≈ HBM_BW / params_bytes = 3.35 TB/s ÷ 140 GB ≈ 24 tokens/sec per replica, single-stream. With continuous batching (vLLM-style), aggregate throughput rises 10–50×.</li>
</ul>

<h3>Worked example — 100 k RPS LLM service</h3>
<p>See the <a href="../../arena/questions/a23-100k-rps-llm.html">100k RPS LLM arena question</a>. Assume 2 k input + 500 output tokens per request, 8 B model. Prefill FLOPs per request ≈ 2 × 8e9 × 2000 = 3.2 × 10<sup>13</sup>. At H100 300 TFLOP/s effective = ~100 ms/request prefill. Decode at 500 tokens × 40 ms/token (batched) = 20 s/request. To serve 100 k RPS, you need ~2 M concurrent decodes → with continuous batching at 256 concurrency/GPU → ~8000 H100s. At $2/hr on-demand that is $16 k/hour = $140 M/year just in GPUs. This is why <em>quantization + speculative decoding + MoE routing</em> are not optional at OpenAI/Anthropic scale.</p>
<div class="callout openai"><h4>OpenAI-specific</h4><p>OpenAI interviewers will drill on batching vs latency trade: explain the Pareto frontier between per-user tokens/sec and cluster tokens/sec/$, and why they ship different SKUs (Turbo vs Standard) along that curve.</p></div>
<div class="callout anthropic"><h4>Anthropic-specific</h4><p>Anthropic cares about the <em>context-length tail</em>: a 200 k-token Claude request has prefill FLOPs 100× a 2 k prompt; KV cache alone is ~40 GB at BF16 for a 70 B model. Mention chunked prefill, paged attention, and prefix-caching for shared system prompts.</p></div>

<h2 id="s6">Common mistakes and sanity checks</h2>
<ul>
  <li><strong>Off-by-1000 on bytes vs bits</strong>. 1 Gbps is 125 MB/s, not 1 GB/s.</li>
  <li><strong>Ignoring replication overhead</strong>. Usable storage ≈ raw / 3 for standard RF=3.</li>
  <li><strong>Confusing DAU with QPS</strong>. 100 M DAU at 10 actions/day is 11 k/s average, not 100 k/s.</li>
  <li><strong>Forgetting peak multiplier</strong>. Peak/avg = 2–5× consumer, 8–10× B2B.</li>
  <li><strong>Treating RTT as one-way</strong>. A query + response is 2 RTTs minimum if TLS handshake is involved.</li>
  <li><strong>Quoting HDD seek times</strong> (10 ms) for a modern NVMe design. 2008 called.</li>
</ul>
<p>Sanity check: if your storage-per-year number is bigger than Google's total disclosed capacity, you miscounted a factor of 10. If your QPS is larger than global internet packet rates (~10 B/s), same.</p>
<blockquote>"I'd rather be approximately right than precisely wrong." — John Maynard Keynes, quoted by every staff engineer doing whiteboard math.</blockquote>
""",
        "body_zh": r"""
<h2 id="s1">常数表</h2>
<p>必须背下来。面试时没时间推导；Alex Xu V1 第 2 章与 ByteByteGo 延迟速查表的版本几乎相同，因为它们都来自 Jeff Dean 的「每个工程师都该知道的数字」（2009，Colin Scott 在 2020 年按新硬件更新）。</p>
<table>
  <thead><tr><th>操作</th><th>延迟</th><th>记忆锚点</th></tr></thead>
  <tbody>
    <tr><td>L1 缓存命中</td><td>0.5 ns</td><td>免费</td></tr>
    <tr><td>分支预测失败</td><td>5 ns</td><td>免费</td></tr>
    <tr><td>L2 缓存命中</td><td>7 ns</td><td>免费</td></tr>
    <tr><td>互斥锁加解锁</td><td>25 ns</td><td>免费</td></tr>
    <tr><td>主内存引用</td><td>100 ns</td><td>L1 的 100×</td></tr>
    <tr><td>Zstd 压缩 1 KB</td><td>2 µs</td><td>内存引用的 20×</td></tr>
    <tr><td>1 Gbps 发 2 KB</td><td>20 µs</td><td>网络底线</td></tr>
    <tr><td>SSD 随机读 4 KB</td><td>100 µs</td><td>内存的 1000×</td></tr>
    <tr><td>SSD 顺序读 1 MB</td><td>250 µs</td><td>~4 GB/s</td></tr>
    <tr><td>同机房 RTT</td><td>500 µs</td><td>半毫秒</td></tr>
    <tr><td>网络读 1 MB</td><td>1 ms</td><td>~1 GB/s</td></tr>
    <tr><td>HDD 寻道</td><td>10 ms</td><td>历史遗留</td></tr>
    <tr><td>新 TLS 握手</td><td>50–100 ms</td><td>2 × RTT</td></tr>
    <tr><td>加州 → 荷兰 RTT</td><td>150 ms</td><td>光速底线</td></tr>
    <tr><td>H100 BF16 FLOP/s</td><td>989 TFLOP/s</td><td>~1 PFLOP/s 名义</td></tr>
    <tr><td>H100 HBM3 带宽</td><td>3.35 TB/s</td><td>memory-bound 区</td></tr>
  </tbody>
</table>
<div class="callout tip"><h4>来源交叉引用</h4><p>前 13 行几乎照搬 Alex Xu V1 第 2 章；GPU 两行来自 NVIDIA H100 数据表，是 LLM 服务题的刚需。可视化版本参考 ByteByteGo「Latency Numbers Every Programmer Should Know」。</p></div>

<h2 id="s2">单位与 2 的幂</h2>
<p>在这里搞错就挂面试。肌肉记忆：</p>
<ul>
  <li>2<sup>10</sup> ≈ 10<sup>3</sup> = 1 K</li>
  <li>2<sup>20</sup> ≈ 10<sup>6</sup> = 1 M</li>
  <li>2<sup>30</sup> ≈ 10<sup>9</sup> = 1 G</li>
  <li>2<sup>40</sup> ≈ 10<sup>12</sup> = 1 T</li>
  <li>2<sup>50</sup> ≈ 10<sup>15</sup> = 1 P</li>
  <li>86 400 秒/天 ≈ 10<sup>5</sup>；2.6 × 10<sup>6</sup> 秒/月；3.15 × 10<sup>7</sup> 秒/年。</li>
  <li>1 年 ≈ π × 10<sup>7</sup> 秒（物理学家的小技巧）。</li>
</ul>
<p>推论：「每人每秒一次」× 1000 万用户 = 1000 万/秒平均。消费类应用峰值 2–5× 平均值，B2B 白天集中型 8–10×。</p>

<h2 id="s3">QPS 与存储实例</h2>
<h3>例 1 — 聊天应用（Alex Xu 第 12 章风格）</h3>
<p>5 亿 DAU × 每人 40 条/天 = 2 × 10<sup>10</sup>/天。平均写 QPS = 2 × 10<sup>10</sup> / 10<sup>5</sup> = 20 万/秒。峰值（3×）≈ 60 万/秒。读是扇出：平均每条 3 个接收者 → 60 万/秒写放大为 180 万/秒读。存储：每条 200 字节 × 2 × 10<sup>10</sup> = 4 TB/天 = 1.46 PB/年。3 副本 + 30% 开销 → 实际配额 ~6 PB/年。</p>

<h3>例 2 — 短链接（Alex Xu 第 8 章）</h3>
<p>每月 1 亿新 URL → 1e8 / (2.6 × 10<sup>6</sup> s) ≈ 40 写/秒。10:1 读写比 → 400 读/秒。这是<em>单 Postgres</em>问题，不是第一天就分片的问题。10 年 × 1 亿 = 12 亿行 × 500 字节 = 600 GB，一块 NVMe 就装下。</p>

<h3>例 3 — 照片上传（Flickr / Acing 第 12 章）</h3>
<p>1000 万上传/天，原图 3 MB + 5 种缩略图（合计 200 KB）。写入带宽：10<sup>7</sup> × 3.2 MB / 86 400 s ≈ 370 MB/s。存储：32 TB/天 → 11.7 PB/年（未复制）。Glacier 冷层 $0.004/GB/月 → 11.7 PB 冷存约 4.5 万美元/月。</p>

<h2 id="s4">带宽与出口成本</h2>
<p>2025 年 AWS us-east-1 出口费前 10 TB/月 ~$0.09/GB，超过 150 TB/月降至 $0.05/GB。从 S3 裸出 1 PB 视频 ≈ 5 万美元/月出口费，所以 YouTube/Netflix 级系统都走<em>peered CDN</em>出口（$0.002–0.01/GB，便宜 50–100×）。面试官会追问：读重型 blob 工作负载一定提 CDN 分流。</p>
<ul>
  <li>1 Gbps = 125 MB/s = 10.8 TB/天。</li>
  <li>10 Gbps ≈ 1.1 PB/天（胖服务器网卡）。</li>
  <li>100 Gbps（现代 DC spine）≈ 每链路 10.8 PB/天。</li>
</ul>
<div class="callout warn"><h4>反模式</h4><p>视频/音频/LLM 流设计里忘了出口费。候选人若设计「YouTube」时没意识到 S3 裸出口费超过整个小型 YouTube 的收入，就算没通过成本意识检查。</p></div>

<h2 id="s5">LLM token 经济学</h2>
<p>这是经典书不覆盖的 OpenAI/Anthropic 特有一层。背熟：</p>
<ul>
  <li>1 个英文 token ≈ 0.75 词 ≈ 4 字符。</li>
  <li>2000 词文档 ≈ 2700 token。</li>
  <li>GPT-4 级 70 B 参数 BF16：权重 ~140 GB → 2× H100（每块 80 GB）+ KV cache。</li>
  <li><strong>Prefill</strong> 受算力限（FLOPs ≈ 2 × 参数数 × prompt_tokens）；<strong>decode</strong> 受显存带宽限（每个输出 token 需搬运 params_bytes）。</li>
  <li>H100 BF16 单流 decode 吞吐 ≈ HBM_BW / params_bytes = 3.35 TB/s ÷ 140 GB ≈ 24 token/秒。continuous batching（vLLM 风格）后总吞吐提升 10–50×。</li>
</ul>

<h3>实例：10 万 RPS LLM 服务</h3>
<p>见 <a href="../../arena/questions/a23-100k-rps-llm.html">100k RPS LLM 真题</a>。假设每请求 2 k 输入 + 500 输出 token，8 B 模型。单次 prefill FLOPs ≈ 2 × 8e9 × 2000 = 3.2 × 10<sup>13</sup>。H100 有效 300 TFLOP/s → 约 100 ms 预填。decode 500 token × 40 ms/token（batched）= 20 秒。支撑 10 万 RPS 需 ~200 万并发 decode → continuous batching 256 并发/GPU → ~8000 块 H100。on-demand $2/小时 = 1.6 万美元/小时 = 1.4 亿美元/年，纯 GPU。所以在 OpenAI/Anthropic 规模上<em>量化 + 投机解码 + MoE 路由</em>不是可选项。</p>
<div class="callout openai"><h4>OpenAI 专属</h4><p>OpenAI 会追问 batching 与延迟的权衡：讲清每用户 token/秒与集群 token/秒/$ 的 Pareto 前沿，以及为什么产品上出不同 SKU（Turbo vs Standard）沿这条曲线分布。</p></div>
<div class="callout anthropic"><h4>Anthropic 专属</h4><p>Anthropic 在意<em>长上下文尾部</em>：20 万 token 的 Claude 请求 prefill FLOPs 是 2 k prompt 的 100×；70 B 模型 BF16 时 KV cache 就有 ~40 GB。提 chunked prefill、paged attention、共享 system prompt 的 prefix caching。</p></div>

<h2 id="s6">常见错误与合理性检查</h2>
<ul>
  <li><strong>字节 vs 比特差 1000×</strong>。1 Gbps 是 125 MB/s，不是 1 GB/s。</li>
  <li><strong>忽略复制开销</strong>。可用容量 ≈ 裸容量 / 3（RF=3）。</li>
  <li><strong>混淆 DAU 与 QPS</strong>。1 亿 DAU × 10 动作/天 = 1.1 万/秒，不是 10 万/秒。</li>
  <li><strong>忘记峰值倍数</strong>。消费型 2–5×，B2B 8–10×。</li>
  <li><strong>把 RTT 当单程</strong>。查询+响应至少 2 个 RTT，带 TLS 握手更多。</li>
  <li><strong>引用 HDD 寻道时间</strong>（10 ms）做现代 NVMe 设计。2008 打来电话了。</li>
</ul>
<p>合理性检查：如果你的年度存储大于 Google 公开的总容量，少算/多算了 10 倍；如果 QPS 大于全球互联网包率（~100 亿/秒），同理。</p>
<blockquote>「宁可大约正确，也不要精确错误。」——凯恩斯，白板算数的每位 staff engineer 都引用过。</blockquote>
""",
        "links": [
            ("Previous topic", "上一主题", "../../guide/foundations/interview-framework.html",
             "Interview framework", "面试框架"),
            ("Next track", "下一主线", "../../guide/distributed/replication-consistency.html",
             "Replication & consistency", "复制与一致性"),
            ("Arena", "真题", "../../arena/questions/a23-100k-rps-llm.html",
             "100k RPS LLM service", "10 万 RPS LLM 服务"),
            ("Arena", "真题", "../../arena/questions/o9-in-memory-database.html",
             "In-memory database", "内存数据库"),
            ("Related", "相关", "../../guide/llm/llm-serving.html",
             "LLM serving stack", "LLM 服务栈"),
        ],
    },
]
