"""Distributed systems topics: replication, partitioning, consensus, transactions, stream/batch, storage engines."""

TOPICS = [
    # ------------------------------------------------------------------
    # 1. Replication & Consistency
    # ------------------------------------------------------------------
    {
        "category": "distributed",
        "slug": "replication-consistency",
        "title_en": "Replication & Consistency",
        "title_zh": "复制与一致性",
        "lead_en": "Single-leader, multi-leader, leaderless. CAP vs PACELC. Linearizability, read-your-writes, monotonic reads — how to pick the weakest model that still works.",
        "lead_zh": "单主、多主、无主；CAP 与 PACELC；线性一致、读你所写、单调读——如何挑选仍然够用的最弱一致性模型。",
        "tags": ["DDIA Ch.5", "DDIA Ch.9", "CAP vs PACELC"],
        "refs": ["DDIA Ch.5", "DDIA Ch.9", "Acing SDI Ch.4"],
        "toc_en": [
            "Why replicate at all",
            "Single-leader replication",
            "Multi-leader and leaderless",
            "CAP, PACELC, and what they actually say",
            "Consistency models ladder",
            "Failure modes and real outages",
            "Interview decision tree",
        ],
        "toc_zh": [
            "为什么要复制",
            "单主复制",
            "多主与无主",
            "CAP、PACELC 及其真正含义",
            "一致性模型阶梯",
            "故障模式与真实事故",
            "面试决策树",
        ],
        "body_en": r"""
<h2 id="s1">Why replicate at all</h2>
<p>Three orthogonal reasons, in DDIA Ch.5's framing: <strong>latency</strong> (serve reads from a replica close to the user), <strong>availability</strong> (survive node failure), and <strong>throughput</strong> (scale reads horizontally). Durability is a bonus. If you need none of these, do not replicate — a single Postgres with good backups beats a mis-tuned 5-node cluster every time.</p>
<p>The hard part is not copying bytes; it is deciding <em>what the reader sees</em> when writes and reads race. That is why Kleppmann spends Ch.5 on mechanics and Ch.9 on what the resulting guarantees are called.</p>
<div class="callout tip"><h4>Source cross-reference</h4><p>DDIA Ch.5 covers leader/follower, multi-leader, leaderless with Dynamo-style quorums. DDIA Ch.9 defines linearizability, causal consistency, and consensus. Acing SDI Ch.4 gives the SQL-vs-NoSQL framing most interviewers expect.</p></div>

<h2 id="s2">Single-leader replication</h2>
<p>One node accepts writes; followers replay the log. Synchronous followers block the writer until ack (zero RPO, slow tail); asynchronous followers lag (fast, may lose recent writes on failover). Most real systems run <strong>one sync + many async</strong> — the "chain" that Postgres, MySQL Group Replication, and AWS Aurora all converge on.</p>
<div class="mermaid-container"><pre class="mermaid">
flowchart LR
    C[Client] --&gt;|write| L[Leader]
    L --&gt;|sync WAL| F1[Follower 1 sync]
    L --&gt;|async| F2[Follower 2]
    L --&gt;|async| F3[Follower 3]
    R[Read client] --&gt; F2
</pre></div>
<ul>
  <li><strong>Replication lag</strong>: typical 10–100 ms intra-region, seconds cross-region. Must-know for read-your-writes discussion.</li>
  <li><strong>Failover</strong>: who promotes the new leader? A consensus service (etcd, ZooKeeper) holds the lease; see <a href="../../guide/distributed/consensus.html">consensus</a>.</li>
  <li><strong>Throughput ceiling</strong>: single-leader Postgres caps at ~50 k writes/sec on a fat NVMe box. Beyond that, partition (see <a href="../../guide/distributed/partitioning.html">partitioning</a>) or move to leaderless.</li>
</ul>
<div class="callout warn"><h4>Anti-pattern</h4><p>Running "multi-master" Postgres via logical replication as a write-scaling strategy. Conflicts are not automatic; you own every last-writer-wins bug. Don't do it unless you have a conflict resolver (CRDT, per-row ownership).</p></div>

<h2 id="s3">Multi-leader and leaderless</h2>
<p><strong>Multi-leader</strong> (e.g., Postgres BDR, CouchDB, calendar apps with offline clients): each region accepts writes, replicates async to others. Concurrent writes to the same key create conflicts resolved by vector clocks, LWW timestamps, or CRDT merge. Best fit: geographically distributed with mostly-disjoint write sets (per-user data).</p>
<p><strong>Leaderless / Dynamo-style</strong> (Cassandra, Riak, ScyllaDB): clients write to N replicas, consider it successful when W ack; reads query R replicas. If W+R &gt; N you get quorum overlap. Anti-entropy via Merkle trees + read-repair + hinted handoff patches divergence.</p>
<table>
  <thead><tr><th>Style</th><th>Writes scale</th><th>Conflict risk</th><th>Example</th></tr></thead>
  <tbody>
    <tr><td>Single-leader</td><td>1 node</td><td>None (serialized)</td><td>Postgres, MySQL</td></tr>
    <tr><td>Multi-leader</td><td>N regions</td><td>High</td><td>CouchDB, BDR</td></tr>
    <tr><td>Leaderless</td><td>N nodes</td><td>Medium (quorum)</td><td>Cassandra, Dynamo</td></tr>
  </tbody>
</table>

<h2 id="s4">CAP, PACELC, and what they actually say</h2>
<p>CAP (Brewer, 2000) says during a network <em>P</em>artition you must choose <em>C</em>onsistency or <em>A</em>vailability. It does <strong>not</strong> say "pick 2 of 3"; partitions are not optional. Useful but oversimplified.</p>
<p>PACELC (Abadi, 2010) repairs the gap: <em>If P, choose A or C; Else choose Latency or Consistency.</em> This is the version staff engineers actually use. Spanner is a PC/EC system (consistent even when healthy, at a latency cost); Dynamo is PA/EL (available and fast, eventually consistent). State the letters explicitly in your answer.</p>
<div class="callout openai"><h4>OpenAI-specific</h4><p>For conversation-history stores, OpenAI-style answers often choose PA/EC: available during partitions but strongly consistent when healthy (same-session read-your-writes must hold). Achieve this with a single-leader region + causal token the client returns on each request.</p></div>

<h2 id="s5">Consistency models ladder</h2>
<p>From strongest to weakest (DDIA Ch.9):</p>
<ol>
  <li><strong>Linearizable (atomic)</strong>: every operation appears to take effect at a single point in real time. Required for leader election, distributed locks, uniqueness constraints. Cost: at least one RTT to a consensus quorum.</li>
  <li><strong>Sequential</strong>: all clients see the same order, but the order can lag real time.</li>
  <li><strong>Causal</strong>: causally related operations are seen in order; concurrent ones may differ. Achievable with vector clocks without consensus.</li>
  <li><strong>Read-your-writes</strong> (session guarantee): after you write, <em>you</em> see it. Cheap to implement with sticky sessions or client-tracked last-LSN.</li>
  <li><strong>Monotonic reads</strong>: once you see a value, you never see an earlier one. Stick a user to one replica.</li>
  <li><strong>Eventual</strong>: converges "eventually" (undefined duration). Most leaderless defaults. Fine for social-media like counts.</li>
</ol>
<p>Interview heuristic: name the weakest model the product can tolerate, then the mechanism that delivers it. "User profiles need read-your-writes after save; monotonic-read across refreshes is enough elsewhere; analytics dashboards can run on 10-minute stale replicas."</p>

<h2 id="s6">Failure modes and real outages</h2>
<ul>
  <li><strong>Split-brain</strong>: network partition isolates the old leader; a new leader is elected; both accept writes. Mitigation: fencing tokens, STONITH, quorum-based leases. See <a href="../../guide/distributed/consensus.html">consensus</a>.</li>
  <li><strong>Replication lag spikes</strong>: a slow follower falls minutes behind; reads served from it look stale. Monitor <code>seconds_behind_master</code> and evict from read pool beyond 1 s.</li>
  <li><strong>2015 AWS DynamoDB metadata storm</strong>: a 4-hour us-east-1 outage where retry storms against a metadata service amplified under replica lag. Lesson: backpressure + jittered exponential backoff, not unbounded retries.</li>
  <li><strong>2017 GitLab postgres deletion</strong>: followers were lagged by 4 GB of WAL when the primary was accidentally wiped; async followers had data the sync one didn't. Runbook the RPO you actually have, not the one on the slide.</li>
</ul>
<div class="callout anthropic"><h4>Anthropic-specific</h4><p>Anthropic interviewers push on <em>auditability</em>: after a failover, can you reconstruct which requests were served by which leader? Answer: write-ahead log with monotonic LSN + leader-epoch baked into every response header, plus a separate append-only audit store.</p></div>

<h2 id="s7">Interview decision tree</h2>
<ol>
  <li>Do you need strong consistency on <em>writes</em>? → single-leader (Postgres/Spanner) or consensus-backed (etcd/CockroachDB).</li>
  <li>Need globally-distributed writes with disjoint keys? → multi-leader with per-user home region.</li>
  <li>Need extreme write throughput + tolerate LWW? → leaderless (Cassandra/Dynamo), R=W=quorum.</li>
  <li>Only reads scale? → single-leader + async read replicas, with a causal token for read-your-writes.</li>
</ol>
<p>State the chosen model, then its PACELC letters, then the one anti-pattern you are explicitly avoiding. That three-sentence answer is what Kleppmann would write on a whiteboard.</p>
""",
        "body_zh": r"""
<h2 id="s1">为什么要复制</h2>
<p>按 DDIA 第 5 章的分法，三个相互独立的理由：<strong>延迟</strong>（就近副本提供读）、<strong>可用性</strong>（节点故障仍可用）、<strong>吞吐</strong>（读横向扩展）。持久性是附带收益。若三者都不需要，就别复制——一台带好备份的 Postgres 永远强过一个没调好的 5 节点集群。</p>
<p>难点不是搬数据，而是在读写竞争时决定<em>读者能看见什么</em>。所以 Kleppmann 第 5 章讲机制、第 9 章讲这些机制带来的保证叫什么名字。</p>
<div class="callout tip"><h4>来源交叉引用</h4><p>DDIA 第 5 章：主从、多主、Dynamo 风格无主与 quorum；第 9 章：线性一致、因果一致、共识。Acing SDI 第 4 章补 SQL/NoSQL 视角。</p></div>

<h2 id="s2">单主复制</h2>
<p>一个节点接受写，follower 重放日志。同步 follower 让写阻塞到 ack（RPO=0，尾延迟高）；异步 follower 有延迟（快，但故障切换可能丢最近写）。真实系统大多跑<strong>1 同步 + 多异步</strong>——Postgres、MySQL Group Replication、AWS Aurora 都如此。</p>
<div class="mermaid-container"><pre class="mermaid">
flowchart LR
    C[客户端] --&gt;|写| L[主]
    L --&gt;|同步 WAL| F1[同步副本]
    L --&gt;|异步| F2[副本 2]
    L --&gt;|异步| F3[副本 3]
    R[读客户端] --&gt; F2
</pre></div>
<ul>
  <li><strong>复制延迟</strong>：同区域 10–100 ms，跨区域秒级。读你所写讨论必考。</li>
  <li><strong>故障切换</strong>：谁提拔新主？共识服务（etcd、ZooKeeper）持有 lease，见 <a href="../../guide/distributed/consensus.html">共识</a>。</li>
  <li><strong>吞吐上限</strong>：单主 Postgres 胖 NVMe 机器上限约 5 万写/秒。再高要分区（见 <a href="../../guide/distributed/partitioning.html">分区</a>）或换无主。</li>
</ul>
<div class="callout warn"><h4>反模式</h4><p>用 Postgres 逻辑复制搞「多主」做写扩展。冲突不会自动解决，你要自己写每一条 LWW bug。没有冲突解决器（CRDT、行级所有权）就别做。</p></div>

<h2 id="s3">多主与无主</h2>
<p><strong>多主</strong>（Postgres BDR、CouchDB、有离线客户端的日历）：每个区域接受写，异步复制到其他。并发写同 key 会冲突，由向量时钟、LWW 时间戳或 CRDT 合并解决。最适合地理分布且写集合基本互不相交（按用户分区）的数据。</p>
<p><strong>无主 / Dynamo 风格</strong>（Cassandra、Riak、ScyllaDB）：客户端向 N 个副本写，W 个 ack 即成功；读查 R 个。W+R&gt;N 时 quorum 有交集。Merkle 树 anti-entropy + read-repair + hinted handoff 修复分歧。</p>
<table>
  <thead><tr><th>类型</th><th>写扩展</th><th>冲突风险</th><th>例子</th></tr></thead>
  <tbody>
    <tr><td>单主</td><td>1 节点</td><td>无（已串行）</td><td>Postgres、MySQL</td></tr>
    <tr><td>多主</td><td>N 区域</td><td>高</td><td>CouchDB、BDR</td></tr>
    <tr><td>无主</td><td>N 节点</td><td>中（quorum）</td><td>Cassandra、Dynamo</td></tr>
  </tbody>
</table>

<h2 id="s4">CAP、PACELC 及其真正含义</h2>
<p>CAP（Brewer 2000）：发生网络<em>分区</em>时必须在一致性和可用性中选一个。它<strong>不是</strong>「三选二」——分区不是可选项。有用但简化过头。</p>
<p>PACELC（Abadi 2010）补齐：<em>分区时选 A 或 C；否则选 L 或 C。</em>staff engineer 实际用这个版本。Spanner 是 PC/EC（健康时也强一致，代价是延迟）；Dynamo 是 PA/EL（可用且快，最终一致）。答题时显式报字母。</p>
<div class="callout openai"><h4>OpenAI 专属</h4><p>对话历史存储，OpenAI 风格答案多选 PA/EC：分区时可用，健康时强一致（同会话必须读你所写）。实现：单主区域 + 客户端每次回传因果 token。</p></div>

<h2 id="s5">一致性模型阶梯</h2>
<p>DDIA 第 9 章从强到弱：</p>
<ol>
  <li><strong>线性一致</strong>：每个操作在真实时间某个点原子生效。选主、分布式锁、唯一性约束必需。代价：至少一次到 quorum 的 RTT。</li>
  <li><strong>顺序一致</strong>：所有客户端看到同一顺序，但顺序可以滞后真实时间。</li>
  <li><strong>因果一致</strong>：因果相关的操作按序可见，并发的顺序可不同。向量时钟实现，无需共识。</li>
  <li><strong>读你所写</strong>（会话保证）：自己写完自己一定读得到。sticky session 或客户端记录 last-LSN 即可。</li>
  <li><strong>单调读</strong>：看过某值后不会再看到更早的。让用户粘在一个副本。</li>
  <li><strong>最终一致</strong>：「最终」会收敛（时长未定义）。大多无主默认。社交 like 计数够用。</li>
</ol>
<p>面试启发：先说产品能容忍的最弱模型，再说实现机制。「用户资料保存后需读你所写；刷新间单调读足矣；分析看板跑在 10 分钟陈旧副本上。」</p>

<h2 id="s6">故障模式与真实事故</h2>
<ul>
  <li><strong>脑裂</strong>：分区把旧主隔离，新主被选出，两者都接写。缓解：fencing token、STONITH、基于 quorum 的 lease，见 <a href="../../guide/distributed/consensus.html">共识</a>。</li>
  <li><strong>复制延迟暴增</strong>：慢 follower 落后几分钟，从它读看到陈旧数据。监控 <code>seconds_behind_master</code>，超 1 秒从读池剔除。</li>
  <li><strong>2015 AWS DynamoDB metadata 风暴</strong>：us-east-1 4 小时故障，元数据服务重试风暴在副本滞后下放大。教训：反压 + 抖动指数退避，禁无界重试。</li>
  <li><strong>2017 GitLab Postgres 误删</strong>：误删主库时 follower 落后 4 GB WAL；异步 follower 有同步副本没有的数据。RPO 要按实际配置 runbook，不是 PPT 上的。</li>
</ul>
<div class="callout anthropic"><h4>Anthropic 专属</h4><p>Anthropic 面试官会追问<em>可审计性</em>：故障切换后能否重建每个请求由哪个主服务的？答：带单调 LSN 的 WAL + 响应头写入 leader-epoch + 独立 append-only 审计存储。</p></div>

<h2 id="s7">面试决策树</h2>
<ol>
  <li>写也要强一致？→ 单主（Postgres/Spanner）或共识支持（etcd/CockroachDB）。</li>
  <li>跨地域写、key 不相交？→ 每用户 home 区的多主。</li>
  <li>极致写吞吐、能容忍 LWW？→ 无主（Cassandra/Dynamo），R=W=quorum。</li>
  <li>只扩展读？→ 单主 + 异步读副本 + 因果 token 保读你所写。</li>
</ol>
<p>答：选定模型 → PACELC 字母 → 明确避开的一个反模式。这三句话就是 Kleppmann 在白板上会写的东西。</p>
""",
        "links": [
            ("Next topic", "下一主题", "../../guide/distributed/partitioning.html",
             "Partitioning & sharding", "分区与分片"),
            ("Deep dive", "深入", "../../guide/distributed/consensus.html",
             "Consensus (Paxos/Raft)", "共识 (Paxos/Raft)"),
            ("Arena", "真题", "../../arena/questions/a24-key-value-store.html",
             "Design a key-value store", "设计键值存储"),
            ("Arena", "真题", "../../arena/questions/o9-in-memory-database.html",
             "In-memory database", "内存数据库"),
        ],
    },

    # ------------------------------------------------------------------
    # 2. Partitioning
    # ------------------------------------------------------------------
    {
        "category": "distributed",
        "slug": "partitioning",
        "title_en": "Partitioning & Sharding",
        "title_zh": "分区与分片",
        "lead_en": "Range vs hash, consistent hashing with virtual nodes, hot partitions, secondary indexes, and the rebalancing problem.",
        "lead_zh": "范围 vs 哈希、带虚节点的一致性哈希、热点分区、二级索引、再平衡问题。",
        "tags": ["DDIA Ch.6", "Alex Xu V1 Ch.5", "consistent hashing"],
        "refs": ["DDIA Ch.6", "Alex Xu V1 Ch.5", "Acing SDI Ch.4"],
        "toc_en": [
            "Why partition",
            "Range vs hash partitioning",
            "Consistent hashing & virtual nodes",
            "Hot partitions",
            "Secondary indexes: local vs global",
            "Rebalancing strategies",
            "Request routing",
        ],
        "toc_zh": [
            "为什么分区",
            "范围分区 vs 哈希分区",
            "一致性哈希与虚节点",
            "热点分区",
            "二级索引：本地 vs 全局",
            "再平衡策略",
            "请求路由",
        ],
        "body_en": r"""
<h2 id="s1">Why partition</h2>
<p>Replication solves reads and availability; <strong>partitioning</strong> solves writes and storage. Once your data exceeds a single node's disk (~30 TB NVMe today) or your write rate exceeds a single leader (~50 k writes/sec for Postgres on a fat box), you must split. DDIA Ch.6 defines a partition as a subset of rows assigned to a node; in Cassandra it's a "ring segment", in DynamoDB it's a "partition", in MongoDB it's a "chunk". Same concept, different branding.</p>
<div class="callout tip"><h4>Source cross-reference</h4><p>DDIA Ch.6 is the gold standard. Alex Xu V1 Ch.5 on consistent hashing is the interview-template version (virtual nodes, add/remove math). Acing SDI Ch.4 frames sharding as a scaling lever.</p></div>

<h2 id="s2">Range vs hash partitioning</h2>
<p><strong>Range</strong>: partition by key order, e.g. usernames A–E, F–J, .... Pro: range scans are cheap (<code>SELECT ... WHERE user BETWEEN 'a' AND 'd'</code>). Con: skew — sequential keys like timestamps hammer one partition. Used by HBase, BigTable, Spanner.</p>
<p><strong>Hash</strong>: <code>partition = hash(key) % N</code>. Pro: uniform distribution. Con: range scans require scatter-gather. Used by Cassandra, DynamoDB, Redis Cluster.</p>
<p>Most real systems are <strong>hash-of-prefix, range-within</strong>: the partition key is hashed (to spread load), but the sort key within a partition is ordered (for efficient scans). DynamoDB's (PK, SK) design, Cassandra's (partition key, clustering key) — same idea.</p>
<pre><code>DynamoDB item: PK = user#42, SK = ts#2026-04-16T10:00:00Z
  → partition chosen by hash(user#42)
  → within partition, items sorted by ts</code></pre>

<h2 id="s3">Consistent hashing &amp; virtual nodes</h2>
<p>Naïve <code>hash(key) % N</code> breaks when N changes — all keys remap. Karger et al. 1997 consistent hashing places nodes on a hash ring; each key is assigned to the next node clockwise. Adding a node only takes 1/N of the keys from its neighbor.</p>
<div class="mermaid-container"><pre class="mermaid">
flowchart LR
    subgraph Ring
      N1((Node A)) --&gt; N2((Node B))
      N2 --&gt; N3((Node C))
      N3 --&gt; N4((Node D))
      N4 --&gt; N1
    end
    K1[Key k1] -.-&gt; N2
    K2[Key k2] -.-&gt; N3
</pre></div>
<p>Problem: with N=5 nodes, variance in key distribution is ±O(1/√N) which is ~45% — ugly. Solution: <strong>virtual nodes</strong> (vnodes). Each physical node claims 100–256 positions on the ring; variance drops to ±5%. Cassandra defaults to 256 vnodes/node; DynamoDB hides it entirely.</p>
<p>Add-node math: with 256 vnodes × 10 nodes = 2560 tokens on the ring. Adding an 11th node steals 256 tokens (~10%) evenly from the other 10. Network traffic during rebalance: 10% of total dataset moved. For a 100 TB cluster that is 10 TB → at 1 GB/s sustained, ~3 hours. <strong>Throttle the rebalance</strong> or you will stomp foreground traffic.</p>
<div class="callout warn"><h4>Anti-pattern</h4><p>Using <code>hash(key) % N</code> with N baked into client code. Scaling out requires rewriting every client. The 2010 reddit incident: migrating from mod-hashing to consistent hashing took months. Start with consistent hashing on day one.</p></div>

<h2 id="s4">Hot partitions</h2>
<p>A celebrity Twitter user with 100 M followers, a viral URL in a short-link service, Black Friday top-SKU in e-commerce — any skewed workload concentrates on one partition. Symptoms: one node at 95% CPU, the rest idle; p99 latency explodes while p50 stays fine.</p>
<p>Mitigations, in order of cost:</p>
<ul>
  <li><strong>Cache the hot keys</strong>: Redis in front of the partition, TTL 1–60 s. Cheapest.</li>
  <li><strong>Write sharding</strong>: append a 2-digit random suffix to the partition key (<code>celeb#42-07</code>). Aggregate at read time. DynamoDB's recommended hot-partition pattern.</li>
  <li><strong>Split the partition</strong>: double-hash or adaptive splitting (DynamoDB auto-splits partitions past 3000 RCU/1000 WCU since 2018).</li>
  <li><strong>Dedicated shard</strong>: Twitter's "celebrity cluster" moves top-N accounts to a special pool with fan-out optimized for them.</li>
</ul>
<div class="callout openai"><h4>OpenAI-specific</h4><p>For prompt-caching or chat-history by user, the "power-user" tail is long: 1% of users drive 30% of tokens. Don't partition by <code>user_id</code> alone; prepend a <code>bucket</code> dimension (<code>(user_id, day_bucket)</code>) to spread the heaviest users across partitions.</p></div>

<h2 id="s5">Secondary indexes: local vs global</h2>
<p>Primary partitioning is chosen by access pattern; secondary access (by a different column) needs an index. Two strategies (DDIA Ch.6):</p>
<ul>
  <li><strong>Local (document-partitioned)</strong>: every partition has its own index on its rows. Writes are cheap (local). Reads by secondary key must <em>scatter-gather</em> every partition. Used by Elasticsearch shards, MongoDB local indexes.</li>
  <li><strong>Global (term-partitioned)</strong>: one index keyed by the secondary column, partitioned by that column's hash. Reads are single-partition. Writes to the base table now also hit a different partition (2PC or async). DynamoDB GSI is eventually consistent precisely because sync'ing is expensive.</li>
</ul>
<p>Trade-off slogan: <em>"Local indexes make writes cheap and reads expensive; global indexes do the opposite."</em></p>

<h2 id="s6">Rebalancing strategies</h2>
<ul>
  <li><strong>Fixed partitions</strong>: create 1000 partitions on day one across 10 nodes (100 each). Adding node 11 → move 1/11 of partitions to it. Elasticsearch, Riak. Must guess the high-water mark upfront.</li>
  <li><strong>Dynamic partitioning</strong>: start with 1 partition; split when it exceeds threshold (default 10 GB in HBase). Shrinks when undersize. Works well for unbounded growth.</li>
  <li><strong>Proportional to nodes</strong>: Cassandra's token-per-node (256 vnodes). Adding a node reshuffles 1/N of tokens.</li>
</ul>
<p><strong>Automatic vs manual</strong> rebalancing: automatic is tempting but can stampede during a network blip. Production-grade systems require <em>operator confirmation</em> for moves above a threshold. CockroachDB and Spanner both gate large rebalances.</p>

<h2 id="s7">Request routing</h2>
<p>Who knows which partition holds <code>user#42</code>?</p>
<ol>
  <li><strong>Smart client</strong>: client library embeds the partition map. Fast, but requires pushing updates to all clients. Cassandra drivers do this.</li>
  <li><strong>Coordinator / routing tier</strong>: a stateless proxy reads the map from ZK/etcd, forwards requests. Extra hop (+0.5 ms), easier ops. Used by Kafka, Vitess.</li>
  <li><strong>Partition-aware DNS / anycast</strong>: rare; only for coarse-grained routing.</li>
</ol>
<p>Either way, there is a metadata store (ZK/etcd) that holds the authoritative partition map. This is exactly why the <strong>2015 DynamoDB metadata storm</strong> was catastrophic — losing the map means losing the ability to route <em>anything</em>. Cache the map on every node with a 5–30 s TTL and graceful staleness.</p>
<div class="callout anthropic"><h4>Anthropic-specific</h4><p>For tenant-isolated inference (Claude for Enterprise), partition by <code>tenant_id</code> at the top level so data never shares a physical node across tenants. This simplifies audit and SOC2: one partition = one tenant = one bucket of logs.</p></div>
""",
        "body_zh": r"""
<h2 id="s1">为什么分区</h2>
<p>复制解决读与可用性；<strong>分区</strong>解决写与存储。数据超过单机磁盘（今天 NVMe 约 30 TB）或写超过单主（胖机器 Postgres 约 5 万写/秒）就必须切。DDIA 第 6 章把分区定义为分配给某节点的一组行：Cassandra 叫「ring segment」，DynamoDB 叫「partition」，MongoDB 叫「chunk」，同概念不同名字。</p>
<div class="callout tip"><h4>来源交叉引用</h4><p>DDIA 第 6 章是金标；Alex Xu V1 第 5 章一致性哈希是面试模板版；Acing SDI 第 4 章把分片当扩展杠杆。</p></div>

<h2 id="s2">范围分区 vs 哈希分区</h2>
<p><strong>范围</strong>：按 key 有序切，比如用户名 A–E、F–J。优点：范围扫描便宜。缺点：倾斜——时间戳这种顺序 key 砸同一分区。HBase、BigTable、Spanner 用这种。</p>
<p><strong>哈希</strong>：<code>partition = hash(key) % N</code>。优点：均匀。缺点：范围查询要 scatter-gather。Cassandra、DynamoDB、Redis Cluster 用这种。</p>
<p>真实系统多是<strong>前缀哈希 + 分区内有序</strong>：分区 key 哈希散开，分区内 sort key 排序。DynamoDB (PK, SK)、Cassandra (partition key, clustering key)，同思想。</p>
<pre><code>DynamoDB 条目：PK = user#42, SK = ts#2026-04-16T10:00:00Z
  → 由 hash(user#42) 决定分区
  → 分区内按 ts 排序</code></pre>

<h2 id="s3">一致性哈希与虚节点</h2>
<p>朴素 <code>hash(key) % N</code> 在 N 变时所有 key 重映射。Karger 等 1997 的一致性哈希把节点放在哈希环上，每个 key 顺时针归属下个节点。加一节点只从邻居拿 1/N。</p>
<div class="mermaid-container"><pre class="mermaid">
flowchart LR
    subgraph Ring
      N1((节点 A)) --&gt; N2((节点 B))
      N2 --&gt; N3((节点 C))
      N3 --&gt; N4((节点 D))
      N4 --&gt; N1
    end
    K1[key k1] -.-&gt; N2
    K2[key k2] -.-&gt; N3
</pre></div>
<p>问题：5 节点时分布方差 ±O(1/√N) ≈ 45%，丑。方案：<strong>虚节点</strong>（vnode）。每个物理节点占 100–256 个位置，方差降到 ±5%。Cassandra 默认 256/节点，DynamoDB 完全隐藏。</p>
<p>加节点算术：256 × 10 = 2560 tokens；加第 11 节点偷 256 个（~10%）平均分自其他 10 节点。重平衡网络流量 = 总数据的 10%。100 TB 集群 = 10 TB，1 GB/s 约 3 小时。<strong>限速重平衡</strong>，否则会把前台流量踩死。</p>
<div class="callout warn"><h4>反模式</h4><p>客户端代码写死 <code>hash(key) % N</code>。扩容要改每个客户端。2010 年 reddit 案例：从 mod 哈希迁到一致性哈希用了几个月。第一天就上一致性哈希。</p></div>

<h2 id="s4">热点分区</h2>
<p>1 亿粉丝的大 V、爆款短链、黑五头部 SKU——任何倾斜负载都会集中到一个分区。表现：一节点 CPU 95%，其余空闲；p99 爆炸但 p50 正常。</p>
<p>按成本从低到高：</p>
<ul>
  <li><strong>缓存热 key</strong>：Redis 挡在分区前，TTL 1–60 秒。最便宜。</li>
  <li><strong>写分片</strong>：分区 key 后缀 2 位随机（<code>celeb#42-07</code>），读时聚合。DynamoDB 官方热点模式。</li>
  <li><strong>拆分区</strong>：双哈希或自适应拆（DynamoDB 自 2018 起超 3000 RCU/1000 WCU 自动拆）。</li>
  <li><strong>专用分片</strong>：Twitter 的「名人集群」，把头部账号挪到专池，扇出专门优化。</li>
</ul>
<div class="callout openai"><h4>OpenAI 专属</h4><p>按用户缓存 prompt 或聊天历史时尾部很长：1% 用户贡献 30% token。不要只按 <code>user_id</code> 分区，加一个 <code>bucket</code> 维度（<code>(user_id, day_bucket)</code>）把重度用户散开。</p></div>

<h2 id="s5">二级索引：本地 vs 全局</h2>
<p>主分区按访问模式挑，但按其他列查需要索引。DDIA 第 6 章两种策略：</p>
<ul>
  <li><strong>本地（按文档分区）</strong>：每分区自带索引。写便宜（本地）。按二级 key 读要<em>scatter-gather</em>全部分区。Elasticsearch shard、MongoDB 本地索引。</li>
  <li><strong>全局（按 term 分区）</strong>：以二级列做 key，其哈希决定分区。读单分区。写主表同时要写到不同分区（2PC 或异步）。DynamoDB GSI 就是因为同步太贵所以默认最终一致。</li>
</ul>
<p>口诀：<em>本地索引写便宜读贵，全局索引反之。</em></p>

<h2 id="s6">再平衡策略</h2>
<ul>
  <li><strong>固定分区数</strong>：第一天建 1000 分区跨 10 节点（每节点 100）。加第 11 节点 → 挪 1/11 分区。Elasticsearch、Riak。要预估高水位。</li>
  <li><strong>动态分区</strong>：从 1 分区开始，超阈值（HBase 默认 10 GB）就拆，太小合并。无界增长适用。</li>
  <li><strong>按节点比例</strong>：Cassandra 每节点 token（256 vnodes）。加节点洗 1/N。</li>
</ul>
<p><strong>自动 vs 手动</strong>重平衡：自动诱人但网络抖动时容易踩踏。生产级系统对超阈值移动要求<em>运维确认</em>。CockroachDB、Spanner 都有此门控。</p>

<h2 id="s7">请求路由</h2>
<p>谁知道 <code>user#42</code> 在哪个分区？</p>
<ol>
  <li><strong>智能客户端</strong>：客户端库内嵌分区图。快，但要推送更新。Cassandra 驱动这样做。</li>
  <li><strong>协调器 / 路由层</strong>：无状态代理从 ZK/etcd 读图再转发。多一跳（+0.5 ms），运维容易。Kafka、Vitess 这样。</li>
  <li><strong>分区感知 DNS / anycast</strong>：少见，只做粗粒度。</li>
</ol>
<p>不管哪种都要一个元数据存储（ZK/etcd）保存权威分区图。<strong>2015 DynamoDB metadata 风暴</strong>之所以灾难：丢了图就路不了<em>任何</em>请求。每节点缓存图，TTL 5–30 秒，允许优雅陈旧。</p>
<div class="callout anthropic"><h4>Anthropic 专属</h4><p>租户隔离推理（Claude for Enterprise）时，顶层按 <code>tenant_id</code> 分区，跨租户不共享物理节点。审计和 SOC2 更简单：一分区 = 一租户 = 一桶日志。</p></div>
""",
        "links": [
            ("Previous", "上一", "../../guide/distributed/replication-consistency.html",
             "Replication & consistency", "复制与一致性"),
            ("Next topic", "下一主题", "../../guide/distributed/consensus.html",
             "Consensus (Paxos/Raft)", "共识 (Paxos/Raft)"),
            ("Arena", "真题", "../../arena/questions/a24-key-value-store.html",
             "Key-value store", "键值存储"),
            ("Arena", "真题", "../../arena/questions/a28-distributed-search-1b.html",
             "Distributed search (1B docs)", "分布式搜索 1B 文档"),
        ],
    },

    # ------------------------------------------------------------------
    # 3. Consensus
    # ------------------------------------------------------------------
    {
        "category": "distributed",
        "slug": "consensus",
        "title_en": "Consensus (Paxos, Raft)",
        "title_zh": "共识 (Paxos, Raft)",
        "lead_en": "Leader election, fencing tokens, etcd/ZooKeeper patterns, split-brain avoidance — and why you rarely implement consensus yourself.",
        "lead_zh": "选主、fencing token、etcd/ZooKeeper 模式、脑裂防范——以及为什么很少自己实现共识。",
        "tags": ["DDIA Ch.9", "Raft", "split-brain"],
        "refs": ["DDIA Ch.8", "DDIA Ch.9"],
        "toc_en": [
            "What consensus actually is",
            "Paxos intuition",
            "Raft: consensus you can understand",
            "Leader election & fencing tokens",
            "etcd, ZooKeeper, and the right layer",
            "Split-brain, FLP, and time",
            "Interview-ready patterns",
        ],
        "toc_zh": [
            "共识到底是什么",
            "Paxos 直觉",
            "Raft：能理解的共识",
            "选主与 fencing token",
            "etcd、ZooKeeper 与正确的抽象层",
            "脑裂、FLP 与时间",
            "面试级模式",
        ],
        "body_en": r"""
<h2 id="s1">What consensus actually is</h2>
<p>Consensus = making N nodes agree on a single value even though some crash, some are slow, and the network drops or reorders messages. DDIA Ch.9 formalizes it as four properties: <strong>uniform agreement</strong> (no two nodes decide differently), <strong>integrity</strong> (no node decides twice), <strong>validity</strong> (the decided value was proposed by some node), <strong>termination</strong> (every non-crashed node eventually decides).</p>
<p>Every important use case reduces to consensus: leader election, atomic commit across shards (2PC on top of consensus = "transactions" in Spanner), linearizable register, uniqueness constraint. If you need linearizability across nodes, you need consensus or something equivalent.</p>
<div class="callout tip"><h4>Source cross-reference</h4><p>DDIA Ch.8 ("Trouble with Distributed Systems") motivates why consensus is hard (no global clock, unreliable networks, partial failure). Ch.9 delivers the solutions. The two chapters belong together.</p></div>

<h2 id="s2">Paxos intuition</h2>
<p>Lamport's 1998 Paxos (single-decree) has two phases: <strong>Prepare</strong> (proposer picks ballot number n, asks majority "promise not to accept anything numbered &lt; n; tell me the highest-numbered value you've accepted"), and <strong>Accept</strong> (proposer sends value back to majority; if accepted, it is decided). A ballot succeeds only if a majority quorum participates, so two concurrent ballots cannot both succeed — the proof is by overlap at any single node.</p>
<p>Multi-Paxos amortizes the Prepare phase by electing a stable leader who can run only Accept for a sequence of slots. In practice, multi-Paxos and Raft converge on nearly the same algorithm; the paper by Ongaro &amp; Ousterhout (2014) explicitly rewrote it for teachability.</p>

<h2 id="s3">Raft: consensus you can understand</h2>
<p>Raft has exactly three roles (follower, candidate, leader), one log per node, and a single RPC family (<code>AppendEntries</code>, <code>RequestVote</code>). Leader is elected for a <strong>term</strong> (monotonically increasing integer). All writes go through the leader; leader replicates to followers; entry is <em>committed</em> once a majority has stored it.</p>
<div class="mermaid-container"><pre class="mermaid">
sequenceDiagram
    participant C as Client
    participant L as Leader (term 5)
    participant F1 as Follower 1
    participant F2 as Follower 2
    C-&gt;&gt;L: write(x=42)
    L-&gt;&gt;L: append to log[idx=10]
    par Replicate
      L-&gt;&gt;F1: AppendEntries(term=5, idx=10, x=42)
      L-&gt;&gt;F2: AppendEntries(term=5, idx=10, x=42)
    end
    F1--&gt;&gt;L: ok
    F2--&gt;&gt;L: ok
    L-&gt;&gt;L: majority reached, commit idx=10
    L--&gt;&gt;C: committed
    L-&gt;&gt;F1: AppendEntries(commitIdx=10)
    L-&gt;&gt;F2: AppendEntries(commitIdx=10)
</pre></div>
<p>Concrete latency on a 3-node Raft cluster in one DC: median write ~2 ms (one intra-DC RTT × 1 round-trip). Across two DCs in same region: ~5 ms. Across continents: 80–150 ms, which is why Spanner co-locates most writes within a region and uses Paxos groups per partition rather than one global group.</p>
<div class="callout warn"><h4>Anti-pattern</h4><p>Writing Raft from scratch for an interview. Interviewers want to hear "I'd use etcd/ZooKeeper for leader election and lock management." They do <strong>not</strong> want a bug-for-bug reimplementation; production Raft took the CockroachDB team 5 engineer-years to stabilize.</p></div>

<h2 id="s4">Leader election &amp; fencing tokens</h2>
<p>Raft/Paxos gives you a leader for a term. Two dangers remain:</p>
<ol>
  <li><strong>Stale leader</strong>: the old leader hasn't noticed it was deposed (paused VM, long GC). It may send a stale <code>write</code> to storage.</li>
  <li><strong>Zombie writes</strong>: write issued before lease expired but arriving at storage after a new leader's write.</li>
</ol>
<p>Solution: <strong>fencing tokens</strong>. Every lease carries a monotonically increasing token. The storage layer rejects writes carrying a token older than the highest it has seen. Martin Kleppmann's blog post on "How to do distributed locking" (2016) popularized the pattern after Redis's Redlock was found to allow a similar failure.</p>
<pre><code># Pseudocode
lease = etcd.acquire_lease("db-leader")  # returns (ok, fence_token=47)
storage.write(key, value, fence=47)  # storage rejects if fence &lt; previously_seen</code></pre>

<h2 id="s5">etcd, ZooKeeper, and the right layer</h2>
<table>
  <thead><tr><th>System</th><th>Algorithm</th><th>Sweet spot</th></tr></thead>
  <tbody>
    <tr><td>ZooKeeper</td><td>ZAB (Paxos-like)</td><td>Config mgmt, leader election, service discovery. Hadoop/Kafka heritage.</td></tr>
    <tr><td>etcd</td><td>Raft</td><td>Kubernetes' source of truth, service registry, small KV. Read-mostly workloads.</td></tr>
    <tr><td>Consul</td><td>Raft</td><td>Service mesh + KV + multi-DC.</td></tr>
    <tr><td>FoundationDB</td><td>Paxos + MVCC</td><td>Strongly consistent ordered KV, ACID. Snowflake/Apple use.</td></tr>
  </tbody>
</table>
<p>Rule of thumb: consensus systems handle <em>10 k–50 k writes/sec cluster-wide</em>. They are <strong>not</strong> your primary data store for user data; they are the <em>coordination layer</em> that tells the primary store who the leader is, which shards exist, and what the config is. When a team puts 1 M ops/sec through ZooKeeper, they page at 3 a.m.</p>

<h2 id="s6">Split-brain, FLP, and time</h2>
<p><strong>FLP impossibility</strong> (Fischer, Lynch, Paterson 1985): in a fully asynchronous model with even one faulty node, no deterministic consensus algorithm can guarantee termination. Real systems escape by assuming partial synchrony — the network is "eventually" timely — and using timeouts. This is why Raft's election timeout (150–300 ms) matters: too short causes spurious elections, too long stretches outage windows.</p>
<p><strong>Split-brain</strong> happens when two nodes both believe they are leader. Prevention: majority quorums (you cannot have two disjoint majorities in one cluster). A 4-node cluster is strictly worse than 3 (same fault tolerance, double the write cost). Always use <strong>odd-sized</strong> clusters: 3, 5, or 7.</p>
<ul>
  <li><strong>3 nodes</strong>: tolerate 1 failure; cheapest production choice.</li>
  <li><strong>5 nodes</strong>: tolerate 2; standard for planetary services (etcd in GKE).</li>
  <li><strong>7 nodes</strong>: tolerate 3; only if you have really loud pagers.</li>
</ul>
<div class="callout openai"><h4>OpenAI-specific</h4><p>Model-weight registry and experiment tracking are classic consensus-layer workloads: small data, linearizable reads, rare writes. Answer "how do you pick which model version serves traffic?" with "etcd cluster holding the current pointer + fencing token on the routing layer."</p></div>

<h2 id="s7">Interview-ready patterns</h2>
<ol>
  <li><strong>Distributed lock with lease + fencing</strong>: acquire lease in etcd, get fence token, pass it to the resource on every call. The resource is the source of truth on fence ordering.</li>
  <li><strong>Config distribution</strong>: store config blob in etcd; services watch and reload on change. Push via watches; pull periodically as backup.</li>
  <li><strong>Leader of a worker pool</strong>: one worker holds an etcd lease, runs the singleton job (e.g., cron, compaction scheduler). Others wait. On lease expiry, they race; fencing protects the shared resource.</li>
  <li><strong>2PC on top of consensus</strong>: Spanner pattern. Each partition's Paxos group is a participant; the coordinator writes the commit record to its own Paxos group. See <a href="../../guide/distributed/transactions.html">transactions</a>.</li>
</ol>
<div class="callout anthropic"><h4>Anthropic-specific</h4><p>Anthropic's interviewers probe "what happens during a rolling deploy?" Answer: Raft's joint-consensus membership change (or etcd's <code>learner</code> mode) lets you add/remove nodes one at a time without ever losing quorum. Describe the <code>Cold-new</code> configuration transition explicitly.</p></div>
""",
        "body_zh": r"""
<h2 id="s1">共识到底是什么</h2>
<p>共识 = 在部分节点崩溃、部分慢、网络丢/乱序的条件下，让 N 个节点就一个值达成一致。DDIA 第 9 章形式化为四条：<strong>统一一致</strong>（任意两节点决定相同）、<strong>完整性</strong>（任一节点只决一次）、<strong>有效性</strong>（决定的值是某节点提出的）、<strong>终止性</strong>（非崩溃节点最终都能决）。</p>
<p>所有重要用例都归约到共识：选主、跨分片原子提交（共识上的 2PC = Spanner 的「事务」）、线性一致寄存器、唯一性约束。跨节点的线性一致必然要共识或等价物。</p>
<div class="callout tip"><h4>来源交叉引用</h4><p>DDIA 第 8 章讲为什么共识难（无全局时钟、不可靠网络、部分失败），第 9 章给答案。两章一起读。</p></div>

<h2 id="s2">Paxos 直觉</h2>
<p>Lamport 1998 的单决 Paxos 两阶段：<strong>Prepare</strong>（提案者选 ballot n，问多数派「不接受 &lt; n 的，并告诉我你已接受的最高编号值」），<strong>Accept</strong>（提案者把值发给多数派，被接受即决定）。ballot 要多数 quorum 才能成功，任意两节点必在某点重叠——这就是不能同时决两次的证明。</p>
<p>Multi-Paxos 摊薄 Prepare：选出稳定 leader，连续 slot 只跑 Accept。实际上 multi-Paxos 和 Raft 几乎同一算法；Ongaro &amp; Ousterhout (2014) 把它为可教学性重写一遍。</p>

<h2 id="s3">Raft：能理解的共识</h2>
<p>Raft 只有三种角色（follower、candidate、leader）、一个日志、一个 RPC 家族（<code>AppendEntries</code>、<code>RequestVote</code>）。leader 按<strong>term</strong>（单调自增）选出。所有写经 leader，leader 复制到 follower，多数存储后<em>提交</em>。</p>
<div class="mermaid-container"><pre class="mermaid">
sequenceDiagram
    participant C as 客户端
    participant L as Leader (term 5)
    participant F1 as Follower 1
    participant F2 as Follower 2
    C-&gt;&gt;L: write(x=42)
    L-&gt;&gt;L: 追加日志 idx=10
    par 复制
      L-&gt;&gt;F1: AppendEntries(term=5, idx=10, x=42)
      L-&gt;&gt;F2: AppendEntries(term=5, idx=10, x=42)
    end
    F1--&gt;&gt;L: ok
    F2--&gt;&gt;L: ok
    L-&gt;&gt;L: 多数达成，提交 idx=10
    L--&gt;&gt;C: committed
    L-&gt;&gt;F1: AppendEntries(commitIdx=10)
    L-&gt;&gt;F2: AppendEntries(commitIdx=10)
</pre></div>
<p>同机房 3 节点 Raft 写中位数 ~2 ms（1 次 RTT）。同区域两机房 ~5 ms。跨大陆 80–150 ms，这也是 Spanner 把多数写锁在区域内、每分区一个 Paxos 组（而非一个全局组）的原因。</p>
<div class="callout warn"><h4>反模式</h4><p>面试时从零写 Raft。面试官想听「我会用 etcd/ZooKeeper 做选主和锁」。他们<strong>不</strong>想要 bug-for-bug 复刻；CockroachDB 团队 5 工程年才把生产 Raft 稳定下来。</p></div>

<h2 id="s4">选主与 fencing token</h2>
<p>Raft/Paxos 给 term 级 leader。还有两个坑：</p>
<ol>
  <li><strong>陈旧 leader</strong>：老 leader 还没意识到被废（VM 挂起、GC 长），继续向存储发写。</li>
  <li><strong>僵尸写</strong>：lease 过期前发出、在新 leader 之后才到达存储。</li>
</ol>
<p>解：<strong>fencing token</strong>。每个 lease 带单调 token；存储层拒绝 token 低于已见最高的写。Kleppmann 2016 博文「How to do distributed locking」推广此模式（Redis Redlock 就有类似失败）。</p>
<pre><code>lease = etcd.acquire_lease("db-leader")  # 返回 (ok, fence=47)
storage.write(key, value, fence=47)  # 若 fence &lt; 已见最高则拒</code></pre>

<h2 id="s5">etcd、ZooKeeper 与正确的抽象层</h2>
<table>
  <thead><tr><th>系统</th><th>算法</th><th>最佳用途</th></tr></thead>
  <tbody>
    <tr><td>ZooKeeper</td><td>ZAB（类 Paxos）</td><td>配置管理、选主、服务发现。Hadoop/Kafka 血统。</td></tr>
    <tr><td>etcd</td><td>Raft</td><td>K8s 的真源、注册表、小 KV。读多写少。</td></tr>
    <tr><td>Consul</td><td>Raft</td><td>服务网格 + KV + 多 DC。</td></tr>
    <tr><td>FoundationDB</td><td>Paxos + MVCC</td><td>强一致有序 KV、ACID。Snowflake/Apple 用。</td></tr>
  </tbody>
</table>
<p>拇指规则：共识系统集群级<em>1–5 万写/秒</em>。它<strong>不是</strong>存用户数据的主库；是<em>协调层</em>，告诉主库谁是 leader、有哪些 shard、配置是什么。若你把 100 万 ops/秒压进 ZooKeeper，半夜 3 点报警。</p>

<h2 id="s6">脑裂、FLP 与时间</h2>
<p><strong>FLP 不可能</strong>（Fischer, Lynch, Paterson 1985）：完全异步模型下只要一个故障节点，没有确定性共识算法能保证终止。真实系统假定部分同步——网络「最终」及时——用超时绕过。Raft 选举超时 150–300 ms：太短导致多余选举，太长拉长故障窗口。</p>
<p><strong>脑裂</strong>：两节点都认为自己是 leader。预防：多数派 quorum（同集群不可能有两个不相交多数）。4 节点严格劣于 3（同容错，双倍写成本）。永远用<strong>奇数</strong>：3、5、7。</p>
<ul>
  <li><strong>3 节点</strong>：容 1 故障，最便宜。</li>
  <li><strong>5 节点</strong>：容 2，行星级服务标配（GKE 的 etcd）。</li>
  <li><strong>7 节点</strong>：容 3，只在报警器特别响时用。</li>
</ul>
<div class="callout openai"><h4>OpenAI 专属</h4><p>模型权重注册表、实验跟踪是经典共识层负载：小数据、线性一致读、偶尔写。「如何选哪个模型版本对外服务？」答：etcd 集群存当前指针 + 路由层带 fencing token。</p></div>

<h2 id="s7">面试级模式</h2>
<ol>
  <li><strong>lease + fencing 的分布式锁</strong>：etcd 拿 lease 取 fence token，每次调资源时带上。资源是 fence 序的真源。</li>
  <li><strong>配置分发</strong>：etcd 存 blob，服务 watch 热加载；推送 + 兜底轮询。</li>
  <li><strong>worker 池 leader</strong>：一个 worker 持 etcd lease，跑 singleton job（cron、压缩调度）；其余等待；过期后抢，fencing 保护共享资源。</li>
  <li><strong>共识之上的 2PC</strong>：Spanner 模式。每分区 Paxos 组是 participant，coordinator 把 commit record 写到自己的 Paxos 组。见 <a href="../../guide/distributed/transactions.html">事务</a>。</li>
</ol>
<div class="callout anthropic"><h4>Anthropic 专属</h4><p>Anthropic 会问「滚动发布期间怎样？」答：Raft 联合共识成员变更（或 etcd 的 <code>learner</code> 模式）允许逐个加减节点、全程保 quorum。明确描述 <code>Cold-new</code> 配置过渡。</p></div>
""",
        "links": [
            ("Previous", "上一", "../../guide/distributed/partitioning.html",
             "Partitioning & sharding", "分区与分片"),
            ("Next topic", "下一主题", "../../guide/distributed/transactions.html",
             "Transactions & isolation", "事务与隔离"),
            ("Arena", "真题", "../../arena/questions/a24-key-value-store.html",
             "Key-value store (Dynamo)", "键值存储 (Dynamo)"),
            ("Arena", "真题", "../../arena/questions/o4-design-slack.html",
             "Design Slack", "设计 Slack"),
        ],
    },

    # ------------------------------------------------------------------
    # 4. Transactions
    # ------------------------------------------------------------------
    {
        "category": "distributed",
        "slug": "transactions",
        "title_en": "Transactions & Isolation",
        "title_zh": "事务与隔离",
        "lead_en": "ACID, the anomaly zoo (dirty read, lost update, phantom), snapshot isolation vs SSI, 2PC, sagas, and idempotency.",
        "lead_zh": "ACID、异常动物园（脏读、丢失更新、幻读）、快照隔离 vs SSI、2PC、saga、幂等性。",
        "tags": ["DDIA Ch.7", "Acing SDI Ch.5", "isolation zoo"],
        "refs": ["DDIA Ch.7", "Acing SDI Ch.5"],
        "toc_en": [
            "ACID — what each letter really means",
            "The anomaly zoo",
            "Isolation levels in practice",
            "Snapshot isolation vs SSI",
            "Two-phase commit",
            "Sagas and compensations",
            "Idempotency as a primitive",
        ],
        "toc_zh": [
            "ACID —— 每个字母的真实含义",
            "异常动物园",
            "实务中的隔离级别",
            "快照隔离 vs SSI",
            "两阶段提交",
            "Saga 与补偿",
            "幂等作为原语",
        ],
        "body_en": r"""
<h2 id="s1">ACID — what each letter really means</h2>
<p>Jim Gray coined ACID in 1981, and Andreas Reuter added the 'I' for Isolation in 1983. DDIA Ch.7 takes pains to point out that <strong>vendors mean different things by each letter</strong>; "ACID-compliant" on a brochure is marketing, not a spec.</p>
<ul>
  <li><strong>Atomicity</strong>: all-or-nothing on <em>crash</em>. Not about concurrency. Usually implemented via WAL + undo/redo.</li>
  <li><strong>Consistency</strong>: invariants preserved. The <em>application's</em> job; the DB can only enforce declared constraints (FK, CHECK). Largely aspirational.</li>
  <li><strong>Isolation</strong>: concurrent transactions do not interfere. The interesting letter. Serializability is the gold standard; nobody ships it by default because it is slow.</li>
  <li><strong>Durability</strong>: once committed, survives a crash. <code>fsync</code> on the WAL to local SSD gives single-machine durability; replication to another zone gives datacenter-loss durability.</li>
</ul>
<div class="callout tip"><h4>Source cross-reference</h4><p>DDIA Ch.7 is the canonical reference; Acing SDI Ch.5 adds 2PC/saga case studies with idempotency patterns from e-commerce and payment systems.</p></div>

<h2 id="s2">The anomaly zoo</h2>
<p>What goes wrong without isolation?</p>
<table>
  <thead><tr><th>Anomaly</th><th>Scenario</th><th>Prevented by</th></tr></thead>
  <tbody>
    <tr><td>Dirty read</td><td>T2 reads T1's uncommitted writes; T1 aborts.</td><td>Read Committed</td></tr>
    <tr><td>Dirty write</td><td>T2 overwrites T1's uncommitted write.</td><td>Read Committed (row lock)</td></tr>
    <tr><td>Non-repeatable read</td><td>T1 reads x twice, sees different values because T2 committed between.</td><td>Repeatable Read / Snapshot</td></tr>
    <tr><td>Lost update</td><td>Two T1/T2 do read-modify-write on x; one write is lost.</td><td>Explicit lock, <code>CAS</code>, or SI + write-conflict detection</td></tr>
    <tr><td>Write skew</td><td>Two transactions each read a set, write based on it, together violate an invariant (e.g., both on-call doctors resign).</td><td>Serializable / SSI / materializing conflicts</td></tr>
    <tr><td>Phantom</td><td>Range query repeated after another commit sees new rows.</td><td>Predicate lock / range lock / Serializable</td></tr>
  </tbody>
</table>
<p>Write skew is the one that bites senior engineers. A "doctor on-call" invariant (at least one doctor must remain on-call) is violated when two resign concurrently — each reads 2 doctors, each decides it's fine to leave. Snapshot isolation does <em>not</em> prevent this.</p>

<h2 id="s3">Isolation levels in practice</h2>
<p>SQL standard levels are historical fiction; vendors implement what they can. Actual mapping (2024):</p>
<ul>
  <li><strong>Postgres default</strong>: Read Committed. Upgradable to Repeatable Read (= Snapshot Isolation) and Serializable (= SSI).</li>
  <li><strong>MySQL InnoDB default</strong>: Repeatable Read (with weird phantom behavior — gap locks).</li>
  <li><strong>Oracle</strong>: Read Committed and Serializable (their "Serializable" is actually Snapshot Isolation).</li>
  <li><strong>Spanner</strong>: Strict Serializable (serializable + linearizable) by default.</li>
  <li><strong>DynamoDB</strong>: Read Committed per-item; <code>TransactWriteItems</code> offers serializable across items in a single request.</li>
</ul>
<div class="callout warn"><h4>Anti-pattern</h4><p>Assuming "Repeatable Read" means repeatable read. MySQL's RR allows phantoms in some edge cases; Oracle's "Serializable" allows write skew. Always reference the actual isolation level <em>as implemented</em>, not the SQL-standard name.</p></div>

<h2 id="s4">Snapshot isolation vs SSI</h2>
<p><strong>Snapshot Isolation (SI)</strong>: each transaction reads from a consistent snapshot taken at its start. Writes are buffered; at commit, check if any key you wrote was also written by a committed concurrent txn — if so, abort (first-committer-wins). Implemented with MVCC (Postgres, Oracle). Fast, no read locks, prevents dirty/non-repeatable reads but <em>not write skew</em>.</p>
<p><strong>Serializable Snapshot Isolation (SSI)</strong>: Cahill et al. 2008 (used by Postgres <code>SERIALIZABLE</code>, CockroachDB). Tracks read–write dependencies at runtime; aborts a transaction whose dependency graph forms a dangerous cycle. Gives true serializability at 10–30% throughput cost over SI. <strong>This is the default you want when write skew matters</strong> (finance, booking).</p>
<p>Performance data: Postgres 15 on pgbench serializable vs read-committed shows about 20% throughput drop at low contention, 50%+ at high contention. Worth it when correctness matters; measure before shipping.</p>

<h2 id="s5">Two-phase commit</h2>
<p>2PC coordinates an atomic commit across N participants. Phase 1 (<em>Prepare</em>): coordinator asks all to prepare; each durably writes "ready" or "abort". Phase 2 (<em>Commit</em>): if all ready, coordinator writes "commit" and tells all; otherwise "abort".</p>
<div class="mermaid-container"><pre class="mermaid">
sequenceDiagram
    participant C as Coordinator
    participant P1 as Participant 1
    participant P2 as Participant 2
    C-&gt;&gt;P1: Prepare
    C-&gt;&gt;P2: Prepare
    P1--&gt;&gt;C: ready (durable)
    P2--&gt;&gt;C: ready (durable)
    C-&gt;&gt;C: write commit record
    C-&gt;&gt;P1: Commit
    C-&gt;&gt;P2: Commit
    P1--&gt;&gt;C: ack
    P2--&gt;&gt;C: ack
</pre></div>
<p>Fatal flaw: if the coordinator crashes after some participants voted ready but before the commit decision is replicated, those participants are <strong>stuck holding locks</strong> indefinitely (until a human runs recovery). This is why "XA transactions" have a bad reputation and why Spanner uses Paxos-backed coordinators so the decision itself is fault-tolerant.</p>
<p><strong>Throughput cost</strong>: 2PC doubles the write latency (two rounds) and quadruples the WAL traffic. Budget ~20–50 ms per cross-shard commit in-region, hundreds of ms across regions.</p>

<h2 id="s6">Sagas and compensations</h2>
<p>When 2PC is too expensive (microservices across teams, different databases, long-running workflows), use a <strong>saga</strong>: a sequence of local transactions where each has a compensating action for rollback. Originally: Garcia-Molina &amp; Salem 1987 on long-lived transactions.</p>
<p>Example — book a trip:</p>
<ol>
  <li>T1: reserve flight. Compensation: cancel flight.</li>
  <li>T2: reserve hotel. Compensation: cancel hotel.</li>
  <li>T3: charge card. Compensation: refund.</li>
</ol>
<p>If T3 fails, run T2-comp then T1-comp. <strong>Sagas are not ACID</strong>; you lose isolation — another transaction can see half-applied state. You must design idempotent compensations, handle compensation failures (retry queue, human escalation), and add <em>semantic locks</em> (mark "pending" rows) to prevent double booking. Acing SDI Ch.5 gives the pattern with failure-handling state machines.</p>

<h2 id="s7">Idempotency as a primitive</h2>
<p>At any layer above a single-node DB, retries are inevitable — client, load balancer, queue. Every mutation must therefore be <em>idempotent</em>: f(f(x)) = f(x).</p>
<ul>
  <li><strong>Idempotency key</strong>: client generates a UUID per logical operation, server stores "(key, result)" with TTL. Retries return the stored result, do not re-execute. Stripe popularized this for payments.</li>
  <li><strong>Conditional writes</strong>: <code>UPDATE ... WHERE version = N</code>, DynamoDB <code>ConditionExpression</code>. Provides optimistic concurrency control.</li>
  <li><strong>Upserts</strong>: <code>INSERT ... ON CONFLICT DO UPDATE</code>. Safe to retry.</li>
</ul>
<div class="callout openai"><h4>OpenAI-specific</h4><p>The <code>POST /v1/chat/completions</code> endpoint accepts a client-supplied <code>idempotency-key</code> (or uses request fingerprinting) so that a retried request does not double-charge tokens or duplicate tool calls. Mention this explicitly for any billing/agent question.</p></div>
<div class="callout anthropic"><h4>Anthropic-specific</h4><p>For tool-calling agents that make external HTTP requests, sagas with explicit compensation beat 2PC every time. Anthropic interviewers look for: idempotency keys on tool calls, compensation action per tool, max-retry with exponential backoff, and a manual-review queue when compensation fails.</p></div>
""",
        "body_zh": r"""
<h2 id="s1">ACID —— 每个字母的真实含义</h2>
<p>Jim Gray 1981 年造了 ACID，Andreas Reuter 1983 年加了 I（隔离）。DDIA 第 7 章特别强调<strong>各厂商对每个字母的含义都不一样</strong>；宣传页上的「ACID 兼容」是营销语不是规范。</p>
<ul>
  <li><strong>Atomicity（原子性）</strong>：崩溃时全有或全无。不是并发。WAL + undo/redo 实现。</li>
  <li><strong>Consistency（一致性）</strong>：保不变式。是<em>应用</em>的职责；DB 只能强制声明的约束（FK、CHECK）。多半是愿景。</li>
  <li><strong>Isolation（隔离性）</strong>：并发事务互不干扰。最有趣的字母。可串行化是金标，默认没人跑，因为慢。</li>
  <li><strong>Durability（持久性）</strong>：提交后崩溃不丢。WAL <code>fsync</code> 到本地 SSD 保单机，跨 zone 复制保机房丢失。</li>
</ul>
<div class="callout tip"><h4>来源交叉引用</h4><p>DDIA 第 7 章是权威；Acing SDI 第 5 章补 2PC/saga 案例与电商/支付的幂等模式。</p></div>

<h2 id="s2">异常动物园</h2>
<p>没有隔离会出什么事？</p>
<table>
  <thead><tr><th>异常</th><th>场景</th><th>防御</th></tr></thead>
  <tbody>
    <tr><td>脏读</td><td>T2 读了 T1 未提交；T1 回滚。</td><td>Read Committed</td></tr>
    <tr><td>脏写</td><td>T2 覆盖了 T1 未提交写。</td><td>Read Committed（行锁）</td></tr>
    <tr><td>不可重复读</td><td>T1 两次读 x 不同，中间 T2 提交。</td><td>Repeatable Read / 快照</td></tr>
    <tr><td>丢失更新</td><td>两个读-改-写，一次写被吞。</td><td>显式锁 / <code>CAS</code> / SI + 写冲突</td></tr>
    <tr><td>写偏斜</td><td>两个事务各读一组、基于此写，合起来破坏不变式（两个值班医生同时辞职）。</td><td>Serializable / SSI / 物化冲突</td></tr>
    <tr><td>幻读</td><td>同一范围查询再看到新行。</td><td>谓词锁 / 范围锁 / Serializable</td></tr>
  </tbody>
</table>
<p>写偏斜专咬 senior。「至少一位值班医生」不变式下两人同时辞职——各看到还有 2 位、各以为可以走。快照隔离<em>防不住</em>这个。</p>

<h2 id="s3">实务中的隔离级别</h2>
<p>SQL 标准隔离级别是历史小说，厂商各自实现。2024 实际映射：</p>
<ul>
  <li><strong>Postgres 默认</strong>：Read Committed。可升至 Repeatable Read（= 快照隔离）与 Serializable（= SSI）。</li>
  <li><strong>MySQL InnoDB 默认</strong>：Repeatable Read（带怪异幻读——gap lock）。</li>
  <li><strong>Oracle</strong>：Read Committed 与 Serializable（其「Serializable」实为快照隔离）。</li>
  <li><strong>Spanner</strong>：默认严格可串行化（可串行 + 线性一致）。</li>
  <li><strong>DynamoDB</strong>：单条目 Read Committed；<code>TransactWriteItems</code> 单请求内多条目可串行。</li>
</ul>
<div class="callout warn"><h4>反模式</h4><p>假定「Repeatable Read」就是可重复读。MySQL RR 在边界允许幻读；Oracle「Serializable」允许写偏斜。永远引用<em>实际实现</em>的级别，不是标准名。</p></div>

<h2 id="s4">快照隔离 vs SSI</h2>
<p><strong>快照隔离（SI）</strong>：每个事务从启动时一致快照读。写先缓存；提交时检查写 key 是否被并发已提交事务写过，有则 abort（first-committer-wins）。MVCC 实现（Postgres、Oracle）。快，无读锁，防脏读/不可重复读，但<em>防不住写偏斜</em>。</p>
<p><strong>可串行化快照隔离（SSI）</strong>：Cahill 等 2008（Postgres <code>SERIALIZABLE</code>、CockroachDB 用）。运行时追踪读写依赖，把危险环的事务 abort。真可串行化，比 SI 吞吐低 10–30%。<strong>写偏斜要命时（金融、订座）用这个。</strong></p>
<p>性能数据：Postgres 15 pgbench 中 serializable vs read-committed 低竞争下吞吐降 ~20%，高竞争 50%+。正确性重要就值得，上线前测。</p>

<h2 id="s5">两阶段提交</h2>
<p>2PC 跨 N 个 participant 协调原子提交。阶段 1（<em>Prepare</em>）：coordinator 问全员，各自持久写「ready」或「abort」。阶段 2（<em>Commit</em>）：全 ready 则 coordinator 写 commit 记录并通知，否则 abort。</p>
<div class="mermaid-container"><pre class="mermaid">
sequenceDiagram
    participant C as Coordinator
    participant P1 as Participant 1
    participant P2 as Participant 2
    C-&gt;&gt;P1: Prepare
    C-&gt;&gt;P2: Prepare
    P1--&gt;&gt;C: ready（持久）
    P2--&gt;&gt;C: ready（持久）
    C-&gt;&gt;C: 写 commit 记录
    C-&gt;&gt;P1: Commit
    C-&gt;&gt;P2: Commit
    P1--&gt;&gt;C: ack
    P2--&gt;&gt;C: ack
</pre></div>
<p>致命缺陷：coordinator 在部分 participant 已 ready 但 commit 决定未复制出去时崩溃，这些 participant 将<strong>无限期持锁</strong>（待人工恢复）。这就是「XA 事务」名声差的原因，也是 Spanner 用 Paxos 支持 coordinator 的原因——决定本身容错。</p>
<p><strong>吞吐代价</strong>：2PC 写延迟翻倍（两轮）、WAL 流量四倍。同区域跨分片提交 ~20–50 ms，跨区域几百 ms。</p>

<h2 id="s6">Saga 与补偿</h2>
<p>2PC 太贵时（跨团队微服务、不同 DB、长流程）用 <strong>saga</strong>：一系列本地事务，每个有回滚补偿。原典：Garcia-Molina &amp; Salem 1987 长事务论文。</p>
<p>订行程例：</p>
<ol>
  <li>T1：订机票。补偿：退票。</li>
  <li>T2：订酒店。补偿：退订。</li>
  <li>T3：扣款。补偿：退款。</li>
</ol>
<p>T3 失败则跑 T2-comp 再 T1-comp。<strong>Saga 不是 ACID</strong>——你失去隔离，别的事务能看到半状态。补偿必须幂等、处理补偿失败（重试队列、人工升级）、加<em>语义锁</em>（pending 标记）防重复订。Acing SDI 第 5 章给出带失败态的状态机模式。</p>

<h2 id="s7">幂等作为原语</h2>
<p>单机 DB 以上的任何层级都会重试——客户端、LB、队列。每个写操作必须<em>幂等</em>：f(f(x)) = f(x)。</p>
<ul>
  <li><strong>幂等 key</strong>：客户端为每个逻辑操作生 UUID，服务端存「(key, result)」带 TTL。重试返存的结果，不再执行。Stripe 把此模式推广到支付。</li>
  <li><strong>条件写</strong>：<code>UPDATE ... WHERE version = N</code>、DynamoDB <code>ConditionExpression</code>。乐观并发控制。</li>
  <li><strong>upsert</strong>：<code>INSERT ... ON CONFLICT DO UPDATE</code>。安全重试。</li>
</ul>
<div class="callout openai"><h4>OpenAI 专属</h4><p><code>POST /v1/chat/completions</code> 接受客户端 <code>idempotency-key</code>（或用请求指纹），使重试请求不重复扣 token、不重复调用工具。任何计费/agent 题都要提这一点。</p></div>
<div class="callout anthropic"><h4>Anthropic 专属</h4><p>调外部 HTTP 的工具型 agent，saga + 显式补偿永远优于 2PC。Anthropic 面试看：工具调用带幂等 key、每工具一个补偿动作、指数退避重试上限、补偿失败入人工审核队列。</p></div>
""",
        "links": [
            ("Previous", "上一", "../../guide/distributed/consensus.html",
             "Consensus (Paxos/Raft)", "共识"),
            ("Next topic", "下一主题", "../../guide/distributed/stream-batch.html",
             "Stream & batch processing", "流与批处理"),
            ("Arena", "真题", "../../arena/questions/o1-webhook-delivery-platform.html",
             "Webhook delivery platform", "Webhook 投递平台"),
            ("Arena", "真题", "../../arena/questions/a25-agentic-system.html",
             "Agentic system", "Agent 系统"),
        ],
    },

    # ------------------------------------------------------------------
    # 5. Stream & Batch
    # ------------------------------------------------------------------
    {
        "category": "distributed",
        "slug": "stream-batch",
        "title_en": "Stream & Batch Processing",
        "title_zh": "流与批处理",
        "lead_en": "Kafka's log abstraction, MapReduce, Lambda vs Kappa, exactly-once via idempotent writes, event vs processing time, and watermarks.",
        "lead_zh": "Kafka 日志抽象、MapReduce、Lambda vs Kappa、通过幂等写实现 exactly-once、事件时间 vs 处理时间、水位。",
        "tags": ["DDIA Ch.10", "DDIA Ch.11", "Kafka"],
        "refs": ["DDIA Ch.10", "DDIA Ch.11"],
        "toc_en": [
            "The log as universal primitive",
            "Batch processing and MapReduce",
            "Stream processing primitives",
            "Event time vs processing time, watermarks",
            "Exactly-once (and why it is a lie)",
            "Lambda vs Kappa architectures",
            "When to pick what",
        ],
        "toc_zh": [
            "日志作为通用原语",
            "批处理与 MapReduce",
            "流处理原语",
            "事件时间 vs 处理时间、水位",
            "Exactly-once（以及它为何是个谎言）",
            "Lambda vs Kappa 架构",
            "何时选哪个",
        ],
        "body_en": r"""
<h2 id="s1">The log as universal primitive</h2>
<p>Kafka's central insight (Narkhede 2011, popularized by Kleppmann's Ch.11): an append-only <em>log</em> is a general-purpose primitive that unifies messaging, storage, and state replication. Producers append; consumers read at their own offsets; the log retains records for a configured window.</p>
<ul>
  <li><strong>Partitioned</strong>: one topic = N partitions; each partition is an ordered log with a single leader (backed by replication).</li>
  <li><strong>Immutable</strong>: once written, never rewritten. Enables replay, time-travel debugging, and multiple consumers.</li>
  <li><strong>Bounded retention</strong>: 7 days typical; tiered storage (Confluent, Redpanda) extends to months in object storage at 10× lower $/GB.</li>
</ul>
<div class="callout tip"><h4>Source cross-reference</h4><p>DDIA Ch.10 covers batch (MapReduce, Dataflow), Ch.11 covers streams (logs, exactly-once, event time). Both must be read together.</p></div>
<div class="mermaid-container"><pre class="mermaid">
flowchart LR
    P1[Producer A] --&gt; T[[Topic: clicks<br/>partition 0]]
    P2[Producer B] --&gt; T2[[Topic: clicks<br/>partition 1]]
    T --&gt; C1[Consumer group X<br/>offset=1234]
    T --&gt; C2[Consumer group Y<br/>offset=98]
    T2 --&gt; C1
    T2 --&gt; C2
    C1 --&gt; S1[(Sink: warehouse)]
    C2 --&gt; S2[(Real-time dashboard)]
</pre></div>
<p>Concrete throughput: a single Kafka broker on an r6i.4xlarge with NVMe sustains 1 GB/s in + 1 GB/s out across all its partitions. A LinkedIn-scale cluster (the original) handles 7 trillion messages/day.</p>

<h2 id="s2">Batch processing and MapReduce</h2>
<p>MapReduce (Dean &amp; Ghemawat 2004) is the grandparent of modern dataflow: <em>map</em> user-provided function over input partitions, <em>shuffle</em> by key, <em>reduce</em> per-key. Reads bounded input, writes bounded output, assumes you can retry any task.</p>
<p>Key properties:</p>
<ul>
  <li><strong>Deterministic</strong>: same input → same output. Enables retry on task failure without polluting results.</li>
  <li><strong>Materialize intermediate state to disk/HDFS</strong>. Slow but robust.</li>
  <li><strong>Latency: minutes to hours</strong>. Never a user-facing service.</li>
</ul>
<p>Modern successors — Spark, Flink batch mode, BigQuery — trade disk materialization for in-memory shuffle, cutting latency ~5×. For LLM training data curation or daily user analytics, you want Spark/BigQuery, not raw MapReduce.</p>

<h2 id="s3">Stream processing primitives</h2>
<p>Three operator families:</p>
<ol>
  <li><strong>Stateless transforms</strong>: filter, map. Trivial.</li>
  <li><strong>Windowed aggregations</strong>: count per 1-minute tumbling window, per 5-minute sliding window, per session. State = window → running aggregate.</li>
  <li><strong>Stream-stream joins</strong>: join two event streams within a time bound. State = buffered side × join-key. Most memory-hungry.</li>
</ol>
<p>State must be <strong>durable</strong> (survive operator crash) and <strong>recoverable</strong> from the log. Flink stores state in RocksDB + periodic checkpoint to S3. Kafka Streams uses a local RocksDB + changelog topic in Kafka itself.</p>

<h2 id="s4">Event time vs processing time, watermarks</h2>
<p>Event time = when it happened in the real world; processing time = when your system sees it. A mobile client goes offline on a plane, sends events 6 hours later — event time is from 6 hours ago, processing time is now.</p>
<p>Correct streaming must aggregate by event time. But event time arrivals are <em>out of order</em>: how long do you wait? Enter <strong>watermarks</strong> (Akidau et al. 2015 Dataflow paper): a watermark W means "no more events with timestamp &lt; W are expected." Windows close when the watermark passes their end.</p>
<ul>
  <li>Watermark too aggressive → late events are dropped, results are wrong.</li>
  <li>Watermark too conservative → windows close slow, latency shoots up.</li>
  <li>In practice: heuristic watermark (percentile of observed lag) + <em>allowed lateness</em> (emit an update when late events arrive) + <em>dead letter</em> for the truly stale.</li>
</ul>

<h2 id="s5">Exactly-once (and why it is a lie)</h2>
<p>End-to-end "exactly-once" is achievable only if every side effect is <em>idempotent or transactional with the offset commit</em>. DDIA's framing: exactly-once = at-least-once delivery + idempotent processing.</p>
<p>Mechanisms:</p>
<ul>
  <li><strong>Transactional offsets</strong>: Kafka 0.11+ supports transactions that atomically commit output records and consumer offsets. Works for Kafka-to-Kafka.</li>
  <li><strong>Sink idempotency</strong>: writes include a unique record ID; the sink dedupes. S3 conditional writes, DynamoDB <code>ConditionExpression</code>, Postgres <code>ON CONFLICT DO NOTHING</code>.</li>
  <li><strong>Two-phase commit to an external sink</strong>: Flink's TwoPhaseCommitSinkFunction — expensive, but works for JDBC and custom sinks.</li>
</ul>
<div class="callout warn"><h4>Anti-pattern</h4><p>Claiming "exactly-once" when your sink is a REST endpoint with no idempotency key. You have at-most-once (if you commit offsets before the HTTP call) or at-least-once (if after); you do not have exactly-once. Be honest with the interviewer.</p></div>

<h2 id="s6">Lambda vs Kappa architectures</h2>
<p><strong>Lambda</strong> (Marz 2011): run a batch job and a streaming job in parallel over the same data; the batch layer is authoritative, the stream gives low-latency approximate results; a serving layer merges. Pro: each layer tuned independently. Con: two codebases, two bug surfaces, two on-call rotations.</p>
<p><strong>Kappa</strong> (Kreps 2014): only a streaming layer; to recompute history, replay the log from the beginning. Pro: one codebase. Con: replay time for a year of events can be long; state-heavy jobs eat RAM.</p>
<table>
  <thead><tr><th>Aspect</th><th>Lambda</th><th>Kappa</th></tr></thead>
  <tbody>
    <tr><td>Codebases</td><td>2 (batch + stream)</td><td>1</td></tr>
    <tr><td>Backfill</td><td>Re-run batch job</td><td>Replay from log</td></tr>
    <tr><td>State size</td><td>Lower per-job</td><td>Higher (all state in stream)</td></tr>
    <tr><td>Typical use</td><td>Legacy analytics</td><td>Modern Flink/Kafka stacks</td></tr>
  </tbody>
</table>

<h2 id="s7">When to pick what</h2>
<ol>
  <li><strong>Daily business reports</strong>, ML feature tables over last 30 days: pure batch (Spark on S3 or BigQuery). Simplest, cheapest, correct.</li>
  <li><strong>Real-time dashboards, alerting, sub-minute personalization</strong>: streaming (Flink / Kafka Streams) with event-time windows.</li>
  <li><strong>Correct long-tail + fresh short-tail</strong> (fraud detection, abuse moderation): Kappa with generous late-event reprocessing, idempotent sink.</li>
  <li><strong>Training-data pipelines for LLMs</strong>: batch is typical; use streaming only for continuous evals or live safety signals.</li>
</ol>
<div class="callout openai"><h4>OpenAI-specific</h4><p>Usage metering and token billing are a classic Kappa use case: Kafka topic of every inference event, Flink job aggregates tokens per (org, model, minute), results land in a ledger DB keyed by idempotent <code>(request_id, event_kind)</code>. Replay the topic to rebuild ledgers after a bug.</p></div>
<div class="callout anthropic"><h4>Anthropic-specific</h4><p>Safety signal pipelines (refusal rates, jailbreak attempts, policy hits) need both low latency and exact historical replay. Anthropic answers: stream processing for alerting + batch re-aggregation nightly for the safety team's gold dashboards. Mention event-time alignment across the two paths.</p></div>
""",
        "body_zh": r"""
<h2 id="s1">日志作为通用原语</h2>
<p>Kafka 的核心洞察（Narkhede 2011，Kleppmann 第 11 章推广）：仅追加<em>日志</em>是统一消息、存储、状态复制的通用原语。Producer 追加，consumer 按自己的 offset 读，日志按配置保留。</p>
<ul>
  <li><strong>分区</strong>：一 topic = N 个 partition，每个是带 leader 的有序日志。</li>
  <li><strong>不可变</strong>：写入后不改。支持回放、时光调试、多消费者。</li>
  <li><strong>有限保留</strong>：通常 7 天；分层存储（Confluent、Redpanda）把冷数据放对象存储，成本降 10×。</li>
</ul>
<div class="callout tip"><h4>来源交叉引用</h4><p>DDIA 第 10 章讲批（MapReduce、Dataflow），第 11 章讲流（日志、exactly-once、事件时间）。必须一起读。</p></div>
<div class="mermaid-container"><pre class="mermaid">
flowchart LR
    P1[Producer A] --&gt; T[[Topic: clicks<br/>partition 0]]
    P2[Producer B] --&gt; T2[[Topic: clicks<br/>partition 1]]
    T --&gt; C1[消费组 X<br/>offset=1234]
    T --&gt; C2[消费组 Y<br/>offset=98]
    T2 --&gt; C1
    T2 --&gt; C2
    C1 --&gt; S1[(数仓)]
    C2 --&gt; S2[(实时看板)]
</pre></div>
<p>具体吞吐：r6i.4xlarge + NVMe 的单 broker 可持续 1 GB/s 入 + 1 GB/s 出。LinkedIn 级集群（原始）处理 7 万亿消息/天。</p>

<h2 id="s2">批处理与 MapReduce</h2>
<p>MapReduce（Dean &amp; Ghemawat 2004）是现代 dataflow 的祖父：<em>map</em> 用户函数到输入分片、按 key <em>shuffle</em>、按 key <em>reduce</em>。有界输入、有界输出，假定可重试。</p>
<ul>
  <li><strong>确定性</strong>：同输入 → 同输出。重试不污染。</li>
  <li><strong>中间态物化到磁盘/HDFS</strong>：慢但稳。</li>
  <li><strong>延迟：分钟到小时</strong>，绝不面向用户实时。</li>
</ul>
<p>现代后继——Spark、Flink batch、BigQuery——用内存 shuffle 替代磁盘，延迟降 ~5×。LLM 训练数据清洗、每日用户分析：Spark/BigQuery，不是裸 MapReduce。</p>

<h2 id="s3">流处理原语</h2>
<p>三类算子：</p>
<ol>
  <li><strong>无状态变换</strong>：filter、map。</li>
  <li><strong>窗口聚合</strong>：每 1 分钟翻滚、每 5 分钟滑动、按会话。状态 = 窗口 → 累计值。</li>
  <li><strong>流-流 join</strong>：两流按时间边界 join。状态 = 缓冲一侧 × join key。最吃内存。</li>
</ol>
<p>状态必须<strong>持久</strong>（崩溃后保留）且<strong>可从日志恢复</strong>。Flink 用 RocksDB + 定期 S3 checkpoint；Kafka Streams 用本地 RocksDB + Kafka changelog topic。</p>

<h2 id="s4">事件时间 vs 处理时间、水位</h2>
<p>事件时间 = 真实世界发生时间；处理时间 = 系统看到时间。飞机上移动端掉线，6 小时后上报——事件时间 6 小时前、处理时间当下。</p>
<p>正确流处理按事件时间聚合。但事件<em>乱序</em>到达：等多久？<strong>水位</strong>（Akidau 等 2015 Dataflow 论文）：水位 W 意为「不再期待 timestamp &lt; W 的事件」。窗口末超过水位则关闭。</p>
<ul>
  <li>水位过激进 → 迟到事件被丢，结果错。</li>
  <li>水位过保守 → 窗口关得慢，延迟飙升。</li>
  <li>实践：启发式水位（观测 lag 百分位）+ <em>允许迟到</em>（迟到事件触发更新）+ 真正陈旧的进<em>死信</em>。</li>
</ul>

<h2 id="s5">Exactly-once（以及它为何是个谎言）</h2>
<p>端到端「精确一次」只有在每个副作用<em>幂等或与 offset 提交一起事务化</em>时才可达。DDIA 的说法：exactly-once = at-least-once + 幂等处理。</p>
<ul>
  <li><strong>事务性 offset</strong>：Kafka 0.11+ 原子提交输出与消费 offset。Kafka-to-Kafka 有效。</li>
  <li><strong>sink 幂等</strong>：写入带唯一 record ID，sink 去重。S3 条件写、DynamoDB <code>ConditionExpression</code>、Postgres <code>ON CONFLICT DO NOTHING</code>。</li>
  <li><strong>外部 sink 2PC</strong>：Flink TwoPhaseCommitSinkFunction——贵但 JDBC 和自定义 sink 可用。</li>
</ul>
<div class="callout warn"><h4>反模式</h4><p>sink 是无幂等 key 的 REST 端点却声称「exactly-once」。你只能至多一次（HTTP 前提交 offset）或至少一次（HTTP 后），不可能 exactly-once。对面试官诚实。</p></div>

<h2 id="s6">Lambda vs Kappa 架构</h2>
<p><strong>Lambda</strong>（Marz 2011）：同数据上并行跑批和流；批层权威、流层低延迟近似；服务层合并。优点：各层独立调。缺点：两套代码、两套 bug、两套 on-call。</p>
<p><strong>Kappa</strong>（Kreps 2014）：只留流层；回补历史就回放日志。优点：一套代码。缺点：一年事件回放耗时；状态重的作业吃内存。</p>
<table>
  <thead><tr><th>维度</th><th>Lambda</th><th>Kappa</th></tr></thead>
  <tbody>
    <tr><td>代码库</td><td>2（批+流）</td><td>1</td></tr>
    <tr><td>回填</td><td>重跑批</td><td>回放日志</td></tr>
    <tr><td>单作业状态</td><td>小</td><td>大</td></tr>
    <tr><td>典型场景</td><td>老式分析</td><td>现代 Flink/Kafka 栈</td></tr>
  </tbody>
</table>

<h2 id="s7">何时选哪个</h2>
<ol>
  <li><strong>每日业务报表</strong>、过去 30 天 ML 特征表：纯批（Spark on S3 或 BigQuery）。最简、最便宜、正确。</li>
  <li><strong>实时看板、告警、分钟级个性化</strong>：流（Flink / Kafka Streams）按事件时间开窗。</li>
  <li><strong>长尾正确 + 短尾新鲜</strong>（反欺诈、滥用审核）：Kappa，宽松迟到重处理，sink 幂等。</li>
  <li><strong>LLM 训练数据流水线</strong>：批主导；仅连续 eval 或实时安全信号用流。</li>
</ol>
<div class="callout openai"><h4>OpenAI 专属</h4><p>用量计量与 token 计费是经典 Kappa 场景：每条推理事件进 Kafka topic，Flink 按 (org, model, 分钟) 聚合 token，落账本 DB，key = 幂等 <code>(request_id, event_kind)</code>。bug 后回放 topic 重建账本。</p></div>
<div class="callout anthropic"><h4>Anthropic 专属</h4><p>安全信号（拒答率、越狱尝试、策略命中）既要低延迟又要精确历史回放。Anthropic 答法：流做告警 + 每晚批重聚为安全团队的金指标看板。两路的事件时间要对齐。</p></div>
""",
        "links": [
            ("Previous", "上一", "../../guide/distributed/transactions.html",
             "Transactions & isolation", "事务与隔离"),
            ("Next topic", "下一主题", "../../guide/distributed/storage-engines.html",
             "Storage engines", "存储引擎"),
            ("Arena", "真题", "../../arena/questions/o1-webhook-delivery-platform.html",
             "Webhook delivery platform", "Webhook 投递平台"),
            ("Arena", "真题", "../../arena/questions/a14-batch-inference-api.html",
             "Batch inference API", "批推理 API"),
            ("Arena", "真题", "../../arena/questions/a26-web-crawler.html",
             "Web crawler", "网络爬虫"),
        ],
    },

    # ------------------------------------------------------------------
    # 6. Storage Engines
    # ------------------------------------------------------------------
    {
        "category": "distributed",
        "slug": "storage-engines",
        "title_en": "Storage Engines",
        "title_zh": "存储引擎",
        "lead_en": "B-trees vs LSM-trees, write/read amplification, compaction (leveled vs tiered), column stores, and bloom filters.",
        "lead_zh": "B 树 vs LSM 树、写/读放大、压缩（leveled vs tiered）、列存、布隆过滤器。",
        "tags": ["DDIA Ch.3", "LSM-tree", "compaction"],
        "refs": ["DDIA Ch.3"],
        "toc_en": [
            "Why storage engines matter",
            "B-tree mechanics",
            "LSM-tree mechanics",
            "Amplification: write, read, space",
            "Compaction strategies",
            "Bloom filters and read-path tricks",
            "Column stores and OLAP",
        ],
        "toc_zh": [
            "为什么存储引擎重要",
            "B 树机制",
            "LSM 树机制",
            "放大：写、读、空间",
            "压缩策略",
            "布隆过滤器与读路径小技巧",
            "列存与 OLAP",
        ],
        "body_en": r"""
<h2 id="s1">Why storage engines matter</h2>
<p>Picking "Postgres" or "Cassandra" is picking a storage engine architecture. DDIA Ch.3 argues — correctly — that understanding the B-tree vs LSM-tree distinction is what lets you predict the performance envelope of any new database you meet. Two rules:</p>
<ul>
  <li><strong>B-trees</strong> are tuned for <em>read-heavy, mutation-heavy</em> workloads with low latency. MySQL/InnoDB, Postgres, SQL Server, Oracle.</li>
  <li><strong>LSM-trees</strong> are tuned for <em>write-heavy</em> workloads with time-series or append-like access. RocksDB, Cassandra, HBase, DynamoDB, ScyllaDB.</li>
</ul>
<div class="callout tip"><h4>Source cross-reference</h4><p>DDIA Ch.3 is the single best explanation of both engines. Pair with the original LSM paper (O'Neil et al. 1996) and Google's Bigtable paper (2006) for depth.</p></div>

<h2 id="s2">B-tree mechanics</h2>
<p>A balanced n-ary tree where each page (4–16 KB) holds a sorted array of keys and child pointers. A 4-level B-tree with 256-key fan-out indexes 4 billion rows; a read costs log_256(N) disk seeks = 4 for a huge table. With buffer-pool caching of inner pages, only the leaf read hits disk — ~100 µs on NVMe.</p>
<p>Writes are <strong>in-place</strong>: find leaf, modify, optionally split. To survive crashes mid-split, every write first goes to a <em>write-ahead log (WAL)</em>. Recovery replays WAL into the tree.</p>
<ul>
  <li>Update latency: ~1 WAL append (fsync: 50–200 µs) + occasional leaf fsync.</li>
  <li>Write amplification: ~1–3× (WAL + page write).</li>
  <li>Space amplification: low; each logical byte is ~1.3 physical bytes after indexes.</li>
</ul>
<div class="callout warn"><h4>Anti-pattern</h4><p>Claiming B-trees have "no write amp." They write both WAL and page. A random-write workload against a 10 TB B-tree with 16 KB pages produces 16 KB I/O per 100-byte logical write = 160× amplification in the worst case.</p></div>

<h2 id="s3">LSM-tree mechanics</h2>
<p>Writes go to an in-memory <em>memtable</em> (sorted by key; typically a skip list). When memtable hits threshold (~64 MB), it is flushed as an immutable <em>SSTable</em> to disk. Background <em>compaction</em> merges SSTables into larger sorted runs.</p>
<div class="mermaid-container"><pre class="mermaid">
flowchart TB
    W[Write] --&gt; M[Memtable<br/>RAM, sorted]
    M -- flush 64 MB --&gt; L0[(L0 SSTables)]
    L0 -- compact --&gt; L1[(L1 SSTables)]
    L1 -- compact --&gt; L2[(L2 SSTables)]
    L2 -- compact --&gt; L3[(L3 SSTables)]
    R[Read] --&gt; M
    R --&gt; L0
    R --&gt; L1
    R --&gt; L2
    R --&gt; L3
</pre></div>
<p>Reads must check memtable + all SSTable levels; bloom filters (see below) short-circuit most negative lookups. Writes are always <strong>sequential appends</strong>, which SSDs prefer.</p>
<ul>
  <li>Write throughput: 10–100 MB/s sustained per disk for LSM vs 1–10 MB/s for B-tree on random-write workloads.</li>
  <li>Read latency: higher tail (may visit many SSTables).</li>
  <li>Write amplification: 10–30× (leveled compaction); 2–10× (tiered). See next section.</li>
</ul>

<h2 id="s4">Amplification: write, read, space</h2>
<table>
  <thead><tr><th>Amplification</th><th>Definition</th><th>B-tree</th><th>LSM (leveled)</th><th>LSM (tiered)</th></tr></thead>
  <tbody>
    <tr><td>Write</td><td>physical bytes / logical bytes</td><td>1–3×</td><td>10–30×</td><td>2–10×</td></tr>
    <tr><td>Read</td><td>physical reads / logical read</td><td>1 (leaf)</td><td>1–3</td><td>5–10</td></tr>
    <tr><td>Space</td><td>physical bytes / logical bytes</td><td>1.3×</td><td>1.1×</td><td>1.5–2×</td></tr>
  </tbody>
</table>
<p>Quote to memorize: "Leveled compaction gives write amp 10–30× at the cost of space amp 1.1×; tiered gives 2–10× at the cost of read amp 5–10×." State it with numbers; interviewers love the specific ratios.</p>

<h2 id="s5">Compaction strategies</h2>
<p><strong>Leveled compaction</strong> (LevelDB, RocksDB default, CockroachDB): L_i is ~10× L_{i-1}; each level is a single sorted run (except L0). On compaction, one SSTable from L_i merges with overlapping SSTables in L_{i+1}. Minimizes space amp and read amp, pays in write amp.</p>
<p><strong>Tiered compaction</strong> (Cassandra Size-Tiered STCS, many time-series DBs): L_i holds K similar-sized SSTables; when full, merge all K into one at L_{i+1}. Minimizes write amp, pays in read amp (many overlapping runs) and space amp (pre-compaction duplicates).</p>
<p><strong>Time-window compaction</strong> (Cassandra TWCS): partition data by write-time window (1 hour, 1 day); compact only within window. Ideal for time-series with TTL — drop whole SSTables on expiry with zero compaction cost.</p>
<p>Real numbers: a Cassandra node with STCS and 500 GB data produces ~8 TB of compaction I/O/day; switching to LCS drops that to ~15 TB over the life of the data but amortized — read latency p99 drops ~40%. Instagram's 2019 migration from STCS to LCS paper is the canonical reference.</p>

<h2 id="s6">Bloom filters and read-path tricks</h2>
<p>A Bloom filter is a compact probabilistic set: "might contain, or definitely does not." 10 bits per key gives ~1% false-positive rate. For every SSTable, keep an in-memory bloom; on a point lookup, skip SSTables whose bloom says "definitely not here." Dramatically reduces LSM read I/O on missing keys.</p>
<p>Other read-path tricks:</p>
<ul>
  <li><strong>Block cache</strong>: LRU of recently-read data blocks. 4–32 GB per node typical.</li>
  <li><strong>Index block cache</strong>: index blocks of SSTables kept hot.</li>
  <li><strong>Prefix bloom</strong>: bloom for key prefixes, enabling range prefix skip.</li>
  <li><strong>Ribbon filter</strong> (Facebook 2022): ~30% smaller than bloom for same FP rate; used in newer RocksDB.</li>
</ul>
<div class="callout openai"><h4>OpenAI-specific</h4><p>Vector DB backends (Turbopuffer, LanceDB) are essentially LSM engines with bloom-filter equivalents on IVF partitions. For "design a vector DB" mention LSM + WAL replication + bloom on partition IDs. See <a href="../../arena/questions/o18-vector-database.html">vector DB arena</a>.</p></div>

<h2 id="s7">Column stores and OLAP</h2>
<p>Columnar storage (Parquet, Apache Arrow, C-Store/Vertica, ClickHouse, Snowflake, DuckDB) stores each column contiguously instead of each row. Benefits:</p>
<ul>
  <li><strong>Compression</strong>: same-type values compress 5–20× with dictionary encoding + RLE + delta.</li>
  <li><strong>Vectorized execution</strong>: SIMD over tight column arrays; 10–100× faster scans than row stores.</li>
  <li><strong>Column pruning</strong>: <code>SELECT a, b</code> from a 200-column table reads only 1% of bytes.</li>
</ul>
<p>Cost: individual row lookups and updates are expensive; column stores are OLAP (analytics), not OLTP (transactions). Typical split: OLTP row store (Postgres) → CDC → columnar warehouse (Snowflake/BigQuery) for reporting and ML features.</p>
<div class="callout anthropic"><h4>Anthropic-specific</h4><p>For model evaluation data (millions of (prompt, completion, eval_score) rows) you want a columnar store, not Postgres. Mention Parquet on S3 + DuckDB or ClickHouse for interactive eval dashboards. This is a routine Anthropic interview hook — showing familiarity with evaluation infrastructure signals fit.</p></div>
<div class="callout warn"><h4>Closing anti-pattern</h4><p>Defaulting to "use Postgres" for a 100 TB analytical workload. Postgres is a row store; scan times are hours. The right answer is "ETL to Parquet on S3, query with ClickHouse or Snowflake" — one sentence that shows you know the OLTP/OLAP divide.</p></div>
""",
        "body_zh": r"""
<h2 id="s1">为什么存储引擎重要</h2>
<p>选「Postgres」或「Cassandra」就是在选存储引擎架构。DDIA 第 3 章强调——正确地——理解 B 树 vs LSM 树之分，让你能预测任何新数据库的性能包络。两条：</p>
<ul>
  <li><strong>B 树</strong>适合<em>读多、改多</em>、要求低延迟的负载。MySQL/InnoDB、Postgres、SQL Server、Oracle。</li>
  <li><strong>LSM 树</strong>适合<em>写多</em>、时序或追加型访问。RocksDB、Cassandra、HBase、DynamoDB、ScyllaDB。</li>
</ul>
<div class="callout tip"><h4>来源交叉引用</h4><p>DDIA 第 3 章是两种引擎最好的解释。配 LSM 原论文（O'Neil 等 1996）与 Google Bigtable 论文（2006）加深度。</p></div>

<h2 id="s2">B 树机制</h2>
<p>平衡 n 叉树，每页（4–16 KB）存有序 key 数组和子指针。256 fan-out 的 4 层 B 树索引 40 亿行；读取 log_256(N) 次磁盘 = 大表 4 次。内部页缓冲池命中后，只有叶读盘——NVMe ~100 µs。</p>
<p>写入<strong>原地</strong>：找叶、改、必要时分裂。为防崩溃，每写先入<em>预写日志 WAL</em>。恢复时重放 WAL。</p>
<ul>
  <li>更新延迟：~1 次 WAL 追加（fsync 50–200 µs）+ 偶发叶 fsync。</li>
  <li>写放大：~1–3×（WAL + 页写）。</li>
  <li>空间放大：低；含索引后每逻辑字节约 1.3 物理字节。</li>
</ul>
<div class="callout warn"><h4>反模式</h4><p>声称 B 树「无写放大」。它既写 WAL 也写页。16 KB 页、10 TB B 树的随机写负载最坏情况：100 字节逻辑写对应 16 KB IO = 160× 放大。</p></div>

<h2 id="s3">LSM 树机制</h2>
<p>写入进 RAM 中的<em>memtable</em>（按 key 排序，通常跳表）。满 ~64 MB 后作为不可变 <em>SSTable</em> 刷盘。后台<em>压缩</em>把 SSTable 合并成更大的有序段。</p>
<div class="mermaid-container"><pre class="mermaid">
flowchart TB
    W[写] --&gt; M[Memtable<br/>RAM, 有序]
    M -- 刷 64 MB --&gt; L0[(L0 SSTables)]
    L0 -- 压缩 --&gt; L1[(L1 SSTables)]
    L1 -- 压缩 --&gt; L2[(L2 SSTables)]
    L2 -- 压缩 --&gt; L3[(L3 SSTables)]
    R[读] --&gt; M
    R --&gt; L0
    R --&gt; L1
    R --&gt; L2
    R --&gt; L3
</pre></div>
<p>读要查 memtable + 所有层 SSTable；布隆过滤器（见下）短路大部分 miss。写永远<strong>顺序追加</strong>，SSD 喜欢。</p>
<ul>
  <li>写吞吐：随机写负载 LSM 持续 10–100 MB/s/盘，B 树 1–10 MB/s。</li>
  <li>读延迟：尾更高（可能访问多个 SSTable）。</li>
  <li>写放大：leveled 10–30×；tiered 2–10×。下节。</li>
</ul>

<h2 id="s4">放大：写、读、空间</h2>
<table>
  <thead><tr><th>放大</th><th>定义</th><th>B 树</th><th>LSM (leveled)</th><th>LSM (tiered)</th></tr></thead>
  <tbody>
    <tr><td>写</td><td>物理字节 / 逻辑字节</td><td>1–3×</td><td>10–30×</td><td>2–10×</td></tr>
    <tr><td>读</td><td>物理读 / 逻辑读</td><td>1（叶）</td><td>1–3</td><td>5–10</td></tr>
    <tr><td>空间</td><td>物理字节 / 逻辑字节</td><td>1.3×</td><td>1.1×</td><td>1.5–2×</td></tr>
  </tbody>
</table>
<p>要背的口诀：「leveled 压缩写放大 10–30×，空间放大 1.1×；tiered 写 2–10×，代价是读放大 5–10×。」说出具体数字，面试官最吃这套。</p>

<h2 id="s5">压缩策略</h2>
<p><strong>Leveled compaction</strong>（LevelDB、RocksDB 默认、CockroachDB）：L_i ≈ 10× L_{i-1}；每层为单一有序段（L0 除外）。压缩时 L_i 一个 SSTable 与 L_{i+1} 重叠者合并。空间/读放大最小，写放大为代价。</p>
<p><strong>Tiered compaction</strong>（Cassandra STCS、许多时序 DB）：L_i 存 K 个近似大小的 SSTable，满了合并成 L_{i+1} 的一个。写放大最小，读放大（多重叠段）与空间放大（压缩前重复）为代价。</p>
<p><strong>时间窗口压缩</strong>（Cassandra TWCS）：按写时间窗口（1 小时、1 天）分区，只窗口内压缩。TTL 时序数据理想：到期整段 SSTable 删除，零压缩成本。</p>
<p>真实数字：STCS 的 Cassandra 节点 500 GB 数据 ~8 TB/天压缩 IO；切 LCS 后全生命周期 ~15 TB 但摊薄，p99 读延迟降 ~40%。Instagram 2019 STCS→LCS 迁移是经典参考。</p>

<h2 id="s6">布隆过滤器与读路径小技巧</h2>
<p>布隆过滤器是紧凑概率集：「可能有或一定没有」。每 key 10 bit 的假阳率 ~1%。每个 SSTable 一个内存布隆；点查「一定没有」直接跳过。极大降 LSM 在缺 key 的读 IO。</p>
<p>其他读路径技巧：</p>
<ul>
  <li><strong>块缓存</strong>：最近读数据块 LRU。典型每节点 4–32 GB。</li>
  <li><strong>索引块缓存</strong>：SSTable 索引块常驻。</li>
  <li><strong>前缀布隆</strong>：按 key 前缀，支持范围前缀跳跃。</li>
  <li><strong>Ribbon filter</strong>（Facebook 2022）：同假阳率比布隆小 ~30%，新 RocksDB 用。</li>
</ul>
<div class="callout openai"><h4>OpenAI 专属</h4><p>向量 DB 后端（Turbopuffer、LanceDB）本质是 LSM + IVF 分区上的布隆等价物。「设计向量 DB」答题时提 LSM + WAL 复制 + 分区 ID 布隆，见 <a href="../../arena/questions/o18-vector-database.html">向量 DB 真题</a>。</p></div>

<h2 id="s7">列存与 OLAP</h2>
<p>列存（Parquet、Apache Arrow、C-Store/Vertica、ClickHouse、Snowflake、DuckDB）按列连续存而非按行。好处：</p>
<ul>
  <li><strong>压缩</strong>：同类型字典编码 + RLE + delta 压缩 5–20×。</li>
  <li><strong>向量化执行</strong>：紧凑列数组上 SIMD，扫描比行存快 10–100×。</li>
  <li><strong>列裁剪</strong>：200 列表 <code>SELECT a, b</code> 只读 1% 字节。</li>
</ul>
<p>代价：单行查改贵，列存是 OLAP（分析）不是 OLTP。典型分层：OLTP 行存（Postgres）→ CDC → 列存数仓（Snowflake/BigQuery）做报表和 ML 特征。</p>
<div class="callout anthropic"><h4>Anthropic 专属</h4><p>模型评估数据（数百万 (prompt, completion, eval_score) 行）要列存不是 Postgres。提 S3 上 Parquet + DuckDB 或 ClickHouse 做交互式 eval 看板。这是 Anthropic 面试常见钩子——表现出对评测基础设施的熟悉度就是契合信号。</p></div>
<div class="callout warn"><h4>收尾反模式</h4><p>100 TB 分析负载默认「用 Postgres」。Postgres 是行存，全扫要小时。正解是「ETL 成 S3 Parquet，ClickHouse 或 Snowflake 查」——一句话展示你懂 OLTP/OLAP 分界。</p></div>
""",
        "links": [
            ("Previous", "上一", "../../guide/distributed/stream-batch.html",
             "Stream & batch processing", "流与批处理"),
            ("Next track", "下一主线", "../../guide/foundations/interview-framework.html",
             "Interview framework (revisit)", "面试框架（回顾）"),
            ("Arena", "真题", "../../arena/questions/o9-in-memory-database.html",
             "In-memory database", "内存数据库"),
            ("Arena", "真题", "../../arena/questions/a24-key-value-store.html",
             "Key-value store", "键值存储"),
            ("Arena", "真题", "../../arena/questions/o18-vector-database.html",
             "Vector database", "向量数据库"),
        ],
    },
]
