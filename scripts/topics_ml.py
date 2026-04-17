"""ML System topics for the SD-Guide study module.

Each TOPIC entry is rendered by gen_guide.py into
/pages/guide/ml/<slug>.html.  Section anchors are s1..sN matching
toc_en / toc_zh order.
"""

TOPICS = [

# =====================================================================
# 1. ML Lifecycle & Platform
# =====================================================================
{
  "category": "ml",
  "slug": "ml-lifecycle",
  "title_en": "ML Lifecycle & Platform",
  "title_zh": "ML 生命周期与平台",
  "lead_en": "From a raw feature table to a production model serving 10k QPS: feature store, training pipeline, model registry, CI/CD for ML, and the three deploy shapes (batch, online, streaming) — plus the shadow / canary / A-B hierarchy that keeps regressions out of production.",
  "lead_zh": "从原始特征表到承载 10k QPS 的生产模型：特征平台、训练流水线、模型注册表、ML 的 CI/CD、三种部署形态（批、在线、流），以及把回归挡在门外的 shadow / canary / A-B 层级。",
  "tags": ["Feature store", "Model registry", "Shadow/canary", "MLOps"],
  "refs": ["Chip Huyen Ch.7", "Chip Huyen Ch.10", "Khang Pham Ch.2"],
  "toc_en": [
    "Why an ML platform exists",
    "Feature store: offline vs online split",
    "Training pipeline & model registry",
    "CI/CD for ML (tests that matter)",
    "Serving: batch vs online vs streaming",
    "Shadow, canary, A/B and interleaving",
    "OpenAI vs Anthropic framing",
  ],
  "toc_zh": [
    "为什么需要 ML 平台",
    "特征平台：离线/在线双库",
    "训练流水线与模型注册表",
    "ML 的 CI/CD（哪些测试最重要）",
    "服务化：批 vs 在线 vs 流",
    "Shadow、灰度、A/B 与 interleaving",
    "OpenAI 与 Anthropic 的视角差异",
  ],
  "body_en": """
        <div class="callout openai">
          <h4>Source cross-reference</h4>
          <p>This page synthesises <strong>Chip Huyen Ch.7 (Deployment)</strong>, <strong>Ch.10 (Infra &amp; MLOps)</strong> and <strong>Khang Pham Ch.2</strong> (core ML primer). Read Chip Huyen Ch.7 on "Batch prediction vs online prediction" and Ch.10 on "ML platforms" as the companions to this note.</p>
        </div>

        <h2 id="s1">Why an ML platform exists</h2>
        <p>A team with one model and one engineer needs no platform. A team with <strong>20 models, 40 features per model, 5 training frameworks and weekly deploys</strong> cannot survive without one. Chip Huyen Ch.10 frames the problem as removing the <em>N&times;M explosion</em>: N modelling teams &times; M plumbing concerns (feature freshness, online lookup, rollback, monitoring). A platform collapses the M concerns into one paved road.</p>
        <p>In interviews, when the question says "design a recommender for 100M DAU", do not jump to models. First sketch the lifecycle: <em>data &rarr; features &rarr; training &rarr; registry &rarr; serving &rarr; monitoring &rarr; retraining</em>, and only then drill into the piece the interviewer cares about. Scoring rubrics at both OpenAI and Anthropic reward candidates who explicitly trace a feature from source log to a served prediction.</p>

        <h2 id="s2">Feature store: offline vs online split</h2>
        <p>A feature store has <strong>two physical stores with one logical API</strong>: an offline store (Hive, S3+Parquet, BigQuery) sized in terabytes for training, and an online store (Redis, DynamoDB, RocksDB, ScyllaDB) sized in gigabytes for serving with p99 &lt; 5 ms lookups. The two must stay consistent; any skew becomes an invisible prediction bug. Feast, Tecton and Databricks Feature Store are the common concretisations; roll-your-own is a valid answer if you justify it.</p>
        <div class="mermaid-container"><pre class="mermaid">
flowchart LR
  logs[Event logs / CDC] --> stream[Stream job: Flink/Spark Streaming]
  logs --> batch[Batch job: Spark/dbt]
  batch --> off[(Offline store<br/>Parquet/Iceberg)]
  stream --> on[(Online store<br/>Redis/Scylla)]
  stream -.replicate.-> off
  off --> train[Training job]
  on --> serve[Inference service]
  train --> reg[Model registry]
  reg --> serve
        </pre></div>
        <p>Key design rules:</p>
        <ul>
          <li><strong>Point-in-time joins</strong> on the offline side to prevent label leakage; you must reconstruct what the online store would have returned at event time.</li>
          <li><strong>Feature versioning</strong>: adding a feature never mutates an existing ID; it creates <code>feature_v2</code> to preserve reproducibility.</li>
          <li><strong>TTL and freshness budget per feature</strong>: a user-activity counter might have a 10 s freshness SLO, country-of-residence 24 h.</li>
          <li>Typical scale: Uber's Michelangelo reports ~10,000 features, ~2,000 online features touched per request, p99 ~2 ms from a sharded Cassandra.</li>
        </ul>

        <h2 id="s3">Training pipeline &amp; model registry</h2>
        <p>Training is not a notebook; it is a DAG executed by Airflow, Kubeflow, Metaflow, or Flyte. The DAG must be <strong>idempotent, parameterised, and reproducible</strong>: same inputs + same code + same seeds &rArr; bit-equivalent model, within fp tolerance. Outputs go to a registry (MLflow, Weights &amp; Biases, SageMaker Model Registry, Vertex AI Model Registry) keyed by <code>(model_name, version)</code> and carrying <strong>lineage metadata</strong>: training dataset hash, feature schema version, code commit SHA, hyperparameters, offline metrics, and human sign-off.</p>
        <p>Registry state machine: <code>trained &rarr; staging &rarr; production &rarr; archived</code>. Promotion from staging to production is gated by the CI/CD tests below, never by a human pressing a green button alone.</p>

        <h2 id="s4">CI/CD for ML (tests that matter)</h2>
        <p>Traditional CI tests code. ML CI tests <em>code + data + model</em>. The five tests that catch 90% of regressions:</p>
        <ol>
          <li><strong>Schema test</strong>: new feature batch matches the declared schema (types, ranges, nullability).</li>
          <li><strong>Data drift test</strong>: PSI &lt; 0.2 vs training distribution on every top-20 feature.</li>
          <li><strong>Offline metric test</strong>: new model's AUC / NDCG / calibration is no worse than previous by more than a configured epsilon (e.g. 0.3%).</li>
          <li><strong>Slice test</strong>: no protected subgroup (geo, language, new-user cohort) regresses by &gt;1%.</li>
          <li><strong>Behavioural test</strong>: a curated set of ~200 "golden" inputs produce expected outputs; equivalent to unit tests but on model outputs.</li>
        </ol>
        <div class="callout tip">
          <h4>Concrete numbers</h4>
          <p>A healthy ML platform at a mid-sized company ships 5&ndash;20 model versions per week to staging, 1&ndash;3 to production. Median time from commit to canary = <strong>2 hours</strong>; full rollout with 48 h observation window = <strong>2&ndash;3 days</strong>.</p>
        </div>

        <h2 id="s5">Serving: batch vs online vs streaming</h2>
        <p>Chip Huyen Ch.7 makes three shapes explicit; know when to pick each:</p>
        <ul>
          <li><strong>Batch prediction</strong>: compute daily/hourly, store into a KV; serve by lookup. Used when inputs change slowly (user LTV, lead score). p99 read = &lt;10 ms. Drawback: stale predictions for new users.</li>
          <li><strong>Online (request-time)</strong>: compute on the hot path. Used when inputs change fast (search ranking, ad CTR, LLM routing). p99 = 20&ndash;200 ms. Drawback: tail latency and cost risk.</li>
          <li><strong>Streaming</strong>: pre-compute on events as they arrive (Flink, Spark Streaming); store into online store. Used when you need "online-like" freshness but the model itself is too heavy for request-time (e.g. user embedding update every session).</li>
        </ul>
        <p>Hybrid is the norm: candidate generation batch-precomputed, ranking online, feature updates streaming.</p>

        <h2 id="s6">Shadow, canary, A/B and interleaving</h2>
        <p>Chip Huyen Ch.9 catalogues the four <em>online evaluation</em> strategies; they are a hierarchy of risk/information trade-offs:</p>
        <div class="mermaid-container"><pre class="mermaid">
flowchart LR
  new[New model v2] --> shadow[1. Shadow<br/>0% user impact<br/>log only]
  shadow --> canary[2. Canary<br/>1-5% traffic<br/>abort on KPI regression]
  canary --> ab[3. A/B test<br/>50/50 · 1-2 weeks<br/>powered for MDE]
  ab --> rollout[4. Full rollout<br/>100%]
  ab -.-> interleave[Interleaving<br/>same-user pairs<br/>10x sample efficiency]
        </pre></div>
        <ol>
          <li><strong>Shadow</strong>: send the same request to v1 and v2, serve v1, log both. Catches crashes, latency regressions and gross output drift before any user sees v2.</li>
          <li><strong>Canary</strong>: route 1&ndash;5% of traffic to v2 with automatic abort on pre-declared KPI guardrails (error rate, latency p99, business metric).</li>
          <li><strong>A/B</strong>: 50/50 (or power-calculated) split for 1&ndash;2 weeks. Requires an MDE (minimum detectable effect) calculation; a common anti-pattern is reading the test early and declaring victory on noise.</li>
          <li><strong>Interleaving</strong> (for ranked lists): serve a list that interleaves v1 and v2 results to the <em>same user</em>; about 10&times; more sample-efficient than user-split A/B for ranking problems (Chapelle &amp; Li).</li>
        </ol>
        <div class="callout warn">
          <h4>Anti-pattern: "we deployed straight to 100%"</h4>
          <p>Skipping shadow + canary and going directly to A/B is the most common outage generator. A new embedding version with a silent OOV bug can null-out 0.5% of recommendations and cost days of debugging. Always spend the 48 h in shadow, regardless of urgency.</p>
        </div>

        <h2 id="s7">OpenAI vs Anthropic framing</h2>
        <div class="callout openai">
          <h4>OpenAI emphasis</h4>
          <p>OpenAI interviews treat the ML platform as the <em>foundation for fast iteration</em>: expect probing on feature-store freshness SLOs, online feature serving latency, and the CI/CD tests that keep a model-versions-per-week cadence safe. Bias toward <strong>online serving</strong> examples (search, ranking, ad).</p>
        </div>
        <div class="callout anthropic">
          <h4>Anthropic emphasis</h4>
          <p>Anthropic asks the same questions but from a <em>safety-first</em> angle: shadow mode is non-negotiable, rollback must be one click, every promotion must carry a human sign-off field in the registry, and offline eval suites must include harm-slice tests alongside accuracy. The registry is a compliance artefact, not just a version list.</p>
        </div>
        <p>Either way, the winning interview narrative is: define the lifecycle, pick the deploy shape justified by input velocity, bound the risk with shadow&rarr;canary&rarr;A/B, and wire monitoring to the registry so you can roll back in &lt;5 min.</p>
""",
  "body_zh": """
        <div class="callout openai">
          <h4>来源对照</h4>
          <p>本页综合 <strong>Chip Huyen 第 7 章（部署）</strong>、<strong>第 10 章（基础设施与 MLOps）</strong>与 <strong>Khang Pham 第 2 章</strong>（ML 核心入门）。建议配合 Chip Huyen Ch.7「批预测 vs 在线预测」与 Ch.10「ML 平台」一起阅读。</p>
        </div>

        <h2 id="s1">为什么需要 ML 平台</h2>
        <p>一个团队、一个模型、一个工程师，完全不需要平台。但当团队有 <strong>20 个模型、每个 40 个特征、5 种训练框架、每周都要上线</strong>时，没有平台是活不下去的。Chip Huyen 第 10 章把问题抽象为消除 <em>N&times;M 爆炸</em>：N 个建模团队 &times; M 个基础设施问题（特征时效、在线查询、回滚、监控）。平台把这 M 件事汇聚成一条「铺好的路」。</p>
        <p>面试里，当题目说「为 1 亿 DAU 设计推荐系统」，不要直接冲进模型。先画出生命周期：<em>数据 &rarr; 特征 &rarr; 训练 &rarr; 注册表 &rarr; 服务 &rarr; 监控 &rarr; 再训练</em>，再根据面试官的兴趣点深挖。OpenAI 与 Anthropic 的评分标准都奖励能把某个特征从源日志追踪到被服务端预测使用的候选人。</p>

        <h2 id="s2">特征平台：离线/在线双库</h2>
        <p>特征平台有<strong>两个物理库、一个逻辑 API</strong>：离线库（Hive、S3+Parquet、BigQuery），TB 量级，供训练；在线库（Redis、DynamoDB、RocksDB、ScyllaDB），GB 量级，服务时 p99 &lt; 5 ms。两者必须保持一致——任何偏差都会变成看不见的预测 bug。常见实现有 Feast、Tecton、Databricks Feature Store；自研也是合理答案，但要说明理由。</p>
        <div class="mermaid-container"><pre class="mermaid">
flowchart LR
  logs[事件日志 / CDC] --> stream[流任务 Flink/Spark]
  logs --> batch[批任务 Spark/dbt]
  batch --> off[(离线库<br/>Parquet/Iceberg)]
  stream --> on[(在线库<br/>Redis/Scylla)]
  stream -.回写.-> off
  off --> train[训练任务]
  on --> serve[推理服务]
  train --> reg[模型注册表]
  reg --> serve
        </pre></div>
        <p>关键设计点：</p>
        <ul>
          <li><strong>时间点连接（point-in-time join）</strong>——离线必须重现事件发生那一刻在线库会返回的数据，防止 label 泄漏。</li>
          <li><strong>特征版本化</strong>——新增特征永远新建 <code>feature_v2</code>，不动旧 ID，确保可复现。</li>
          <li><strong>每个特征独立的 TTL 与时效预算</strong>：比如「用户活跃计数」10 秒，「居住国」24 小时。</li>
          <li>规模参考：Uber Michelangelo 约 1 万个特征，每次请求用到 2,000 个在线特征，分片 Cassandra 上 p99 约 2 ms。</li>
        </ul>

        <h2 id="s3">训练流水线与模型注册表</h2>
        <p>训练不是 Notebook，而是一个由 Airflow / Kubeflow / Metaflow / Flyte 执行的 DAG。DAG 必须<strong>幂等、参数化、可复现</strong>：同输入+同代码+同种子 &rArr; 浮点误差内的比特等模型。产物写入注册表（MLflow、W&amp;B、SageMaker、Vertex AI），以 <code>(model_name, version)</code> 为主键，并附带<strong>血缘元数据</strong>：训练数据哈希、特征 schema 版本、代码 commit SHA、超参数、离线指标、人工签字。</p>
        <p>注册表状态机：<code>trained &rarr; staging &rarr; production &rarr; archived</code>。staging 到 production 的晋升应由 CI/CD 测试把关，而不是仅靠人点绿色按钮。</p>

        <h2 id="s4">ML 的 CI/CD（哪些测试最重要）</h2>
        <p>传统 CI 测代码；ML CI 要测<em>代码+数据+模型</em>。能拦住 90% 回归的五类测试：</p>
        <ol>
          <li><strong>Schema 测试</strong>——新一批特征的类型、范围、是否可空要与声明一致。</li>
          <li><strong>数据漂移测试</strong>——每个 Top-20 特征相对训练分布的 PSI &lt; 0.2。</li>
          <li><strong>离线指标测试</strong>——新模型 AUC / NDCG / 校准度相对旧模型不能劣化超过 epsilon（例如 0.3%）。</li>
          <li><strong>分片测试</strong>——任何受保护子群（地域、语言、新用户）不得劣化 &gt;1%。</li>
          <li><strong>行为测试</strong>——约 200 个「金样本」输入产出固定输出，相当于模型输出的单元测试。</li>
        </ol>
        <div class="callout tip">
          <h4>具体数字</h4>
          <p>健康的 ML 平台每周推 5&ndash;20 个模型版本到 staging，1&ndash;3 个到生产。commit 到 canary 中位数 <strong>2 小时</strong>，含 48 小时观察期的全量发布 <strong>2&ndash;3 天</strong>。</p>
        </div>

        <h2 id="s5">服务化：批 vs 在线 vs 流</h2>
        <p>Chip Huyen Ch.7 把三种形态讲得很清楚：</p>
        <ul>
          <li><strong>批预测</strong>——每日/小时跑一次，结果进 KV，查即返。适用于输入变化慢的场景（用户 LTV、线索评分）。p99 读 &lt;10 ms。缺点：新用户预测会滞后。</li>
          <li><strong>在线（请求时）</strong>——直接在热路径上算。适用于输入变化快的场景（搜索排序、广告 CTR、LLM 路由）。p99 = 20&ndash;200 ms。缺点：长尾延迟和成本。</li>
          <li><strong>流式</strong>——事件到达时提前算（Flink、Spark Streaming），写入在线库。用于需要「近实时」新鲜度、但模型本身太重无法请求时跑的情况（例如会话级用户 embedding 更新）。</li>
        </ul>
        <p>实战里几乎都是混合：召回批预计算，排序在线算，特征流式更新。</p>

        <h2 id="s6">Shadow、灰度、A/B 与 interleaving</h2>
        <p>Chip Huyen Ch.9 把四种<em>在线评估</em>策略按风险/信息量排成层级：</p>
        <div class="mermaid-container"><pre class="mermaid">
flowchart LR
  new[新模型 v2] --> shadow[1. Shadow<br/>0% 用户影响<br/>仅记录]
  shadow --> canary[2. Canary<br/>1-5% 流量<br/>KPI 异常自动中止]
  canary --> ab[3. A/B 测试<br/>50/50 · 1-2 周<br/>按 MDE 配置样本]
  ab --> rollout[4. 全量]
  ab -.-> interleave[Interleaving<br/>同用户对比<br/>样本效率 10x]
        </pre></div>
        <ol>
          <li><strong>Shadow</strong>：请求同时发给 v1 与 v2，只返 v1，双边记录。可在用户看不到 v2 之前就发现崩溃、延迟退化、严重输出漂移。</li>
          <li><strong>Canary</strong>：1&ndash;5% 流量打到 v2，按预设 KPI 护栏（错误率、p99、业务指标）自动中止。</li>
          <li><strong>A/B</strong>：50/50（或按 power 计算）拆分 1&ndash;2 周。必须先算 MDE（最小可检测效应）；常见反模式是提前读数、把噪音当胜利。</li>
          <li><strong>Interleaving</strong>（排序列表专属）：把 v1 与 v2 的结果交织给<em>同一个用户</em>，比用户拆分 A/B 高 10&times; 样本效率（Chapelle &amp; Li）。</li>
        </ol>
        <div class="callout warn">
          <h4>反模式：「我们直接上了 100%」</h4>
          <p>跳过 shadow + canary 直接 A/B 是事故最大来源。一个有 OOV bug 的 embedding 新版本可能静默把 0.5% 推荐置空，排查耗掉几天。无论多紧急，都要走完 48 小时 shadow。</p>
        </div>

        <h2 id="s7">OpenAI 与 Anthropic 的视角差异</h2>
        <div class="callout openai">
          <h4>OpenAI 侧重</h4>
          <p>OpenAI 面试把 ML 平台当作<em>快速迭代的地基</em>：会追问特征新鲜度 SLO、在线特征查询延迟、支撑每周多次发版的 CI/CD 测试。偏爱<strong>在线服务</strong>类案例（搜索、排序、广告）。</p>
        </div>
        <div class="callout anthropic">
          <h4>Anthropic 侧重</h4>
          <p>Anthropic 会从<em>安全优先</em>角度问同样的问题：shadow 模式不可省；回滚必须一键；注册表的每次晋升都要带人工签字字段；离线评估套件必须包含「伤害分片测试」，不能只看准确率。注册表在这里是合规制品，不仅是版本号列表。</p>
        </div>
        <p>无论对谁，获胜的叙事是：先定义生命周期；再依据输入变化速率选择部署形态；用 shadow&rarr;canary&rarr;A/B 约束风险；把监控与注册表连通，确保 5 分钟内可回滚。</p>
""",
  "links": [
    ("Next", "下一篇", "./drift-monitoring.html",
     "Drift Detection & Monitoring", "漂移检测与监控"),
    ("Arena", "真题", "../../arena/questions/a16-low-latency-inference-api.html",
     "A16 · Low-latency ML inference API", "A16 · 低延迟 ML 推理 API"),
    ("Arena", "真题", "../../arena/questions/o8-search-recommendation-llm.html",
     "O8 · Search / recommendation + LLM", "O8 · 搜索/推荐 + LLM"),
    ("Related", "相关", "../llm/llm-serving.html",
     "LLM Serving & Inference", "LLM 推理服务"),
  ],
},

# =====================================================================
# 2. Drift Detection & Monitoring
# =====================================================================
{
  "category": "ml",
  "slug": "drift-monitoring",
  "title_en": "Drift Detection & Monitoring",
  "title_zh": "漂移检测与监控",
  "lead_en": "A deployed model is a decaying asset. This note covers the three kinds of drift (data, label, concept), the statistical tests that detect them (PSI, KS, KL), the monitoring stack (Arize, WhyLabs, Evidently), retraining triggers, and the LLM-specific drifts (prompt drift, output drift) that neither book fully predicted.",
  "lead_zh": "上线模型是会衰减的资产。本文覆盖三种漂移（数据、标签、概念）、检测它们的统计检验（PSI、KS、KL）、监控栈（Arize、WhyLabs、Evidently）、再训练触发条件，以及两本书都未完全覆盖的 LLM 专属漂移（prompt drift、output drift）。",
  "tags": ["PSI", "KS test", "KL divergence", "Retraining", "LLM drift"],
  "refs": ["Chip Huyen Ch.8", "Chip Huyen Ch.9"],
  "toc_en": [
    "The three drifts",
    "Statistical tests (PSI, KS, KL)",
    "Monitoring stack & SLOs",
    "Retraining triggers",
    "LLM-specific drift",
    "What trips up candidates",
  ],
  "toc_zh": [
    "三种漂移",
    "统计检验（PSI、KS、KL）",
    "监控栈与 SLO",
    "再训练触发条件",
    "LLM 专属漂移",
    "候选人常见翻车点",
  ],
  "body_en": """
        <div class="callout openai">
          <h4>Source cross-reference</h4>
          <p>Chip Huyen <strong>Ch.8 "Data Distribution Shifts and Monitoring"</strong> and <strong>Ch.9 "Continual Learning and Test in Production"</strong>. The terminology (covariate / label / concept drift) is from the Chapelle 2009 tutorial; Chip Huyen is the practitioner synthesis you should cite in interviews.</p>
        </div>

        <h2 id="s1">The three drifts</h2>
        <p>A model learns a joint distribution <code>P(X, Y)</code>. Production can violate the training assumption in three distinct ways, and the response for each differs:</p>
        <ul>
          <li><strong>Data (covariate) drift</strong>: <code>P(X)</code> changes while <code>P(Y|X)</code> stays stable. Example: traffic mix shifts to mobile after an app launch; features like screen-size distribution move. Fix: re-weight training data or retrain with fresh features.</li>
          <li><strong>Label drift</strong>: <code>P(Y)</code> changes. Example: fraud rate triples during a holiday. Often co-occurs with data drift. Fix: recalibrate, adjust thresholds, or retrain.</li>
          <li><strong>Concept drift</strong>: <code>P(Y|X)</code> changes &mdash; the underlying relationship shifts. Example: a spam classifier trained pre-LLM stops catching LLM-generated phishing; the same features now mean something different. Fix: retrain is mandatory; re-weighting cannot recover concept drift.</li>
        </ul>
        <div class="mermaid-container"><pre class="mermaid">
flowchart TB
  drift{Which part of<br/>P(X,Y) changed?}
  drift -- "P(X) only" --> d1[Covariate drift<br/>-&gt; reweight / retrain]
  drift -- "P(Y) only" --> d2[Label drift<br/>-&gt; recalibrate / retrain]
  drift -- "P(Y|X)" --> d3[Concept drift<br/>-&gt; retrain mandatory]
        </pre></div>

        <h2 id="s2">Statistical tests (PSI, KS, KL)</h2>
        <p>Knowing the three drifts matters only if you can measure them. Four workhorse tests:</p>
        <ol>
          <li><strong>PSI (Population Stability Index)</strong> for binned univariate distributions: <code>PSI = &Sigma; (p_i &minus; q_i) &middot; ln(p_i / q_i)</code>. Rules of thumb: &lt;0.1 stable, 0.1&ndash;0.25 moderate shift, &gt;0.25 significant shift. PSI is the standard in banking; it is cheap, interpretable, and catches the common case.</li>
          <li><strong>Kolmogorov-Smirnov (KS) test</strong>: non-parametric test on continuous distributions, uses max CDF gap. Good for small samples and heavy-tailed features. Report p-value with a Bonferroni correction if you are testing many features.</li>
          <li><strong>KL divergence</strong>: <code>KL(p||q) = &Sigma; p log(p/q)</code>. Asymmetric; use Jensen-Shannon if you want symmetric. Strong sensitivity to tail differences; most useful when you already trust your binning.</li>
          <li><strong>Chi-squared</strong> for categorical features.</li>
        </ol>
        <div class="callout tip">
          <h4>Concrete numbers</h4>
          <p>Monitor at two cadences: (a) <strong>hourly</strong> PSI on top-20 features with a 7-day rolling reference; (b) <strong>daily</strong> KS on each continuous feature with training distribution as reference. Alert SLO: 3 consecutive intervals over threshold. Typical false-positive rate target &lt; 2 alerts/week per model.</p>
        </div>

        <h2 id="s3">Monitoring stack &amp; SLOs</h2>
        <p>A full monitoring stack has four layers:</p>
        <ol>
          <li><strong>Feature monitoring</strong>: PSI/KS/chi-squared on every input feature, plus missingness rate and unique-value drift.</li>
          <li><strong>Prediction monitoring</strong>: output distribution drift, score calibration (Brier, ECE), and "prediction entropy" (does the model collapse to one class?).</li>
          <li><strong>Outcome monitoring</strong>: online business metric (CTR, conversion, revenue) with confidence intervals and per-slice breakdowns.</li>
          <li><strong>System monitoring</strong>: latency p50/p95/p99, error rate, GPU utilisation, feature-store lookup failures. Shared with non-ML services.</li>
        </ol>
        <p>Off-the-shelf tools: <strong>Arize AI</strong> and <strong>WhyLabs</strong> are SaaS with built-in drift dashboards and embeddings monitoring; <strong>Evidently</strong> is the dominant open-source library &mdash; it plugs into Airflow or a notebook and emits HTML/JSON drift reports. For custom stacks, Prometheus + Grafana for numerics plus Great Expectations for schema is a minimum viable combo. SageMaker Model Monitor and Vertex AI Model Monitoring are the default on their respective clouds.</p>

        <h2 id="s4">Retraining triggers</h2>
        <p>Chip Huyen Ch.9 lists four trigger policies; interviews love when you enumerate trade-offs:</p>
        <ul>
          <li><strong>Scheduled</strong>: every N days. Simple, predictable, wastes compute when data is stable, too slow for fast-moving domains.</li>
          <li><strong>Data-based</strong>: retrain when drift metric crosses threshold for K consecutive windows. Sensitive to metric choice.</li>
          <li><strong>Performance-based</strong>: retrain when online metric drops by &Delta;X vs rolling baseline. Requires labels &mdash; expensive or delayed in many domains.</li>
          <li><strong>Continual</strong>: micro-batches every few minutes, online learning. Only justified where domain shifts within hours (news feed, fraud).</li>
        </ul>
        <p>A pragmatic default: <em>weekly scheduled + drift-triggered early retrain + performance-triggered emergency retrain</em>. Always pair with the shadow/canary discipline from the lifecycle page &mdash; a retrain is a new model and must go through the full rollout ladder.</p>

        <h2 id="s5">LLM-specific drift</h2>
        <p>Neither Chip Huyen book fully covers what OpenAI and Anthropic interviewers now ask. Three LLM-specific drifts:</p>
        <ul>
          <li><strong>Prompt drift</strong>: your prompt template includes a phrase a provider fine-tune begins handling differently (e.g. behaviour on "system: you are a helpful assistant" changes between GPT-4 minor versions). Detect by running a golden-prompt eval suite nightly and alerting on response distribution shift.</li>
          <li><strong>Output drift</strong>: same input, different outputs, due to upstream model updates or temperature creep. Measure via output embedding similarity (sentence-transformers) against a reference fixture set, alert if cosine drops below 0.85 on &gt;5% of fixtures.</li>
          <li><strong>User-population drift</strong>: the kinds of questions users ask shift. Detect by clustering embeddings of live prompts weekly and tracking cluster mass. Rising new clusters = new use case = new evaluation needs.</li>
        </ul>
        <div class="mermaid-container"><pre class="mermaid">
flowchart LR
  prod[Live LLM traffic] --> emb[Embed prompts]
  emb --> cluster[Weekly cluster<br/>HDBSCAN]
  cluster --> compare{Compare vs<br/>last week}
  compare -- new cluster --> alert[Alert: new use case]
  compare -- cluster mass shift --> eval[Trigger re-eval + maybe retrain]
  prod --> golden[Run golden<br/>prompt suite]
  golden --> sim[Output similarity<br/>vs fixtures]
  sim --> alert
        </pre></div>

        <h2 id="s6">What trips up candidates</h2>
        <div class="callout warn">
          <h4>Anti-patterns</h4>
          <ul>
            <li><strong>"We monitor accuracy"</strong> &mdash; in most domains labels arrive days or weeks late (delayed feedback). You cannot rely on accuracy as the primary alert signal; you need feature and prediction monitoring that fires before labels land.</li>
            <li><strong>"PSI on everything"</strong> &mdash; with 10,000 features, you will get thousands of alerts daily. Rank features by training-time importance and monitor only the top 20 aggressively.</li>
            <li><strong>"Retrain on every drift alert"</strong> &mdash; creates a feedback loop that amplifies noise. Gate retrains on sustained drift + offline improvement test.</li>
          </ul>
        </div>
        <div class="callout openai">
          <h4>OpenAI framing</h4>
          <p>Expect questions like "how would you know your routing model degraded?" &mdash; probe around prediction entropy and per-tenant slice metrics, since one customer's workload can mask aggregate drift.</p>
        </div>
        <div class="callout anthropic">
          <h4>Anthropic framing</h4>
          <p>Drift monitoring becomes a <em>safety signal</em>: a shift in refusal rate or jailbreak-attempt-per-1k-prompts is as important as accuracy. Expect the discussion to include "what would you escalate to the on-call safety reviewer?" &mdash; answer with clear thresholds and a human-in-the-loop path.</p>
        </div>
""",
  "body_zh": """
        <div class="callout openai">
          <h4>来源对照</h4>
          <p>Chip Huyen <strong>第 8 章「数据分布偏移与监控」</strong>与 <strong>第 9 章「持续学习与线上测试」</strong>。术语（协变量/标签/概念漂移）来自 Chapelle 2009 tutorial；Chip Huyen 是面试里最值得引用的实践综合源。</p>
        </div>

        <h2 id="s1">三种漂移</h2>
        <p>模型学的是联合分布 <code>P(X, Y)</code>。生产环境有三种打破训练假设的方式，每一种的应对不同：</p>
        <ul>
          <li><strong>数据（协变量）漂移</strong>：<code>P(X)</code> 变了，<code>P(Y|X)</code> 没变。例：App 发版后移动端流量上升，屏幕尺寸分布改变。对策：重加权训练数据或用新特征重训。</li>
          <li><strong>标签漂移</strong>：<code>P(Y)</code> 变了。例：假日期间欺诈率翻三倍。常与数据漂移并发。对策：重校准、调阈值或重训。</li>
          <li><strong>概念漂移</strong>：<code>P(Y|X)</code> 变了——底层关系变了。例：LLM 时代前训练的垃圾分类器抓不到 LLM 生成的钓鱼，同样特征含义已变。对策：必须重训，重加权救不了概念漂移。</li>
        </ul>
        <div class="mermaid-container"><pre class="mermaid">
flowchart TB
  drift{P(X,Y) 的哪部分<br/>变了？}
  drift -- "仅 P(X)" --> d1[协变量漂移<br/>-&gt; 重加权/重训]
  drift -- "仅 P(Y)" --> d2[标签漂移<br/>-&gt; 重校准/重训]
  drift -- "P(Y|X)" --> d3[概念漂移<br/>-&gt; 必须重训]
        </pre></div>

        <h2 id="s2">统计检验（PSI、KS、KL）</h2>
        <p>三种漂移必须能被测出来才有意义。四个常用检验：</p>
        <ol>
          <li><strong>PSI（群体稳定性指数）</strong>，对分箱单变量：<code>PSI = &Sigma; (p_i &minus; q_i) &middot; ln(p_i / q_i)</code>。经验阈值：&lt;0.1 稳定，0.1&ndash;0.25 中度偏移，&gt;0.25 显著偏移。银行业标配，便宜、可解释、能抓常见情况。</li>
          <li><strong>KS 检验</strong>：连续分布的非参检验，用 CDF 最大差。适合小样本和重尾特征。多特征同时测时要做 Bonferroni 校正。</li>
          <li><strong>KL 散度</strong>：<code>KL(p||q) = &Sigma; p log(p/q)</code>，不对称——想对称请用 JS 散度。对尾部差异敏感，适合已信任分箱的场景。</li>
          <li><strong>卡方</strong>：处理类别型特征。</li>
        </ol>
        <div class="callout tip">
          <h4>具体数字</h4>
          <p>两种监控节奏：(a) <strong>每小时</strong>对 Top-20 特征算 PSI，参考窗口 7 天滚动；(b) <strong>每日</strong>对连续特征做 KS，参考训练分布。告警 SLO：连续 3 个窗口越阈值。单模型假阳性目标 &lt; 2 次/周。</p>
        </div>

        <h2 id="s3">监控栈与 SLO</h2>
        <p>完整监控栈有四层：</p>
        <ol>
          <li><strong>特征监控</strong>：每个输入的 PSI/KS/卡方，加上缺失率与唯一值漂移。</li>
          <li><strong>预测监控</strong>：输出分布漂移、校准度（Brier、ECE）、「预测熵」（是否塌缩到某一类）。</li>
          <li><strong>结果监控</strong>：线上业务指标（CTR、转化、收入），含置信区间与分片分解。</li>
          <li><strong>系统监控</strong>：延迟 p50/p95/p99、错误率、GPU 利用率、特征查询失败。与非 ML 服务共用。</li>
        </ol>
        <p>现成工具：<strong>Arize AI</strong>、<strong>WhyLabs</strong> 是 SaaS，自带漂移与 embedding 监控面板；<strong>Evidently</strong> 是主流开源库，可接入 Airflow 或 Notebook 输出 HTML/JSON 漂移报告。自研最小组合：Prometheus + Grafana 看数值 + Great Expectations 看 schema。SageMaker Model Monitor、Vertex AI Model Monitoring 分别是 AWS / GCP 的默认选择。</p>

        <h2 id="s4">再训练触发条件</h2>
        <p>Chip Huyen Ch.9 列出四种触发策略，面试官喜欢看你把权衡讲清楚：</p>
        <ul>
          <li><strong>定时</strong>：每 N 天一次。简单、可预期；数据稳定时浪费算力，高速变化场景跟不上。</li>
          <li><strong>数据触发</strong>：漂移指标连续 K 个窗口越阈值。对指标选择敏感。</li>
          <li><strong>性能触发</strong>：线上指标相对滚动基线下降 &Delta;X 时触发。需要标签——很多场景标签贵或迟到。</li>
          <li><strong>持续学习</strong>：分钟级微批在线学习。只有在领域几小时内就变化（新闻流、欺诈）时才值得。</li>
        </ul>
        <p>务实默认：<em>周定时 + 漂移触发提前重训 + 性能触发紧急重训</em>。必须配合生命周期页讲过的 shadow/canary 流程——重训出来的就是新模型，必须走完灰度梯子。</p>

        <h2 id="s5">LLM 专属漂移</h2>
        <p>两本 Chip Huyen 都未完全覆盖 OpenAI / Anthropic 现在会问的 LLM 场景。三种 LLM 专属漂移：</p>
        <ul>
          <li><strong>Prompt drift</strong>：prompt 模板里的一句话在模型提供方小版本更新后行为变化（例如 GPT-4 两个小版本对「system: you are a helpful assistant」的处理不同）。对策：夜间跑「金 prompt 套件」，告警响应分布偏移。</li>
          <li><strong>Output drift</strong>：同输入输出变了，来源可能是上游模型更新或温度漂移。用 sentence-transformers 把输出 embed，对固定 fixture 集做相似度，&gt;5% 的 fixture 余弦 &lt; 0.85 时告警。</li>
          <li><strong>用户群漂移</strong>：用户提问的种类变化。每周对线上 prompt embedding 做聚类，追踪簇质量。新簇涌现 = 新用例 = 需要新评估。</li>
        </ul>
        <div class="mermaid-container"><pre class="mermaid">
flowchart LR
  prod[线上 LLM 流量] --> emb[Prompt embedding]
  emb --> cluster[每周 HDBSCAN<br/>聚类]
  cluster --> compare{对比上周}
  compare -- 新簇 --> alert[告警：新用例]
  compare -- 簇质量偏移 --> eval[触发再评估 / 重训]
  prod --> golden[跑金 prompt<br/>套件]
  golden --> sim[输出相似度<br/>对比 fixture]
  sim --> alert
        </pre></div>

        <h2 id="s6">候选人常见翻车点</h2>
        <div class="callout warn">
          <h4>反模式</h4>
          <ul>
            <li><strong>「我们监控准确率」</strong>——多数业务的标签延迟几天到几周。把准确率当主告警信号会慢到看不见事故；必须靠特征和预测监控提前发现。</li>
            <li><strong>「给所有特征都上 PSI」</strong>——10,000 个特征每天会出几千条告警。按训练期重要性取前 20 重点监控即可。</li>
            <li><strong>「漂移一响就重训」</strong>——会形成放大噪声的反馈循环。重训要用「持续漂移 + 离线改进测试」把关。</li>
          </ul>
        </div>
        <div class="callout openai">
          <h4>OpenAI 侧重</h4>
          <p>常考「你怎么知道路由模型退化了？」——重点讲预测熵与按租户分片的指标，因为某个客户的流量会掩盖整体漂移。</p>
        </div>
        <div class="callout anthropic">
          <h4>Anthropic 侧重</h4>
          <p>漂移监控本身就是<em>安全信号</em>：拒答率变化或每千次提问中的越狱尝试数跟准确率一样重要。常被问「你会把什么上报给值班的安全审核员？」——答出清晰阈值与人工介入流程。</p>
        </div>
""",
  "links": [
    ("Next", "下一篇", "./recommenders.html",
     "Recommenders & Ranking", "推荐与排序"),
    ("Prev", "上一篇", "./ml-lifecycle.html",
     "ML Lifecycle & Platform", "ML 生命周期与平台"),
    ("Arena", "真题", "../../arena/questions/o13-nsfw-detection.html",
     "O13 · NSFW detection at scale", "O13 · 大规模 NSFW 检测"),
    ("Related", "相关", "../llm/llm-evaluation.html",
     "LLM Evaluation", "LLM 评估"),
  ],
},

# =====================================================================
# 3. Recommenders & Ranking
# =====================================================================
{
  "category": "ml",
  "slug": "recommenders",
  "title_en": "Recommenders & Ranking",
  "title_zh": "推荐与排序",
  "lead_en": "The canonical three-stage funnel (candidate generation then ranking then re-ranking) walked through with the YouTube two-tower, Facebook/LinkedIn feed, Airbnb search, and wide-and-deep / DLRM ranking architectures. Plus how LLM-assisted ranking is reshaping the stack.",
  "lead_zh": "经典三段漏斗——候选生成 &rarr; 排序 &rarr; 重排——配合 YouTube 双塔、Facebook/LinkedIn feed、Airbnb 搜索与 wide&amp;deep / DLRM 排序架构讲清楚；外加 LLM 辅助排序如何改造这套栈。",
  "tags": ["Two-tower", "Wide & deep", "DLRM", "Embeddings", "LLM ranking"],
  "refs": ["Khang Pham Ch.2-4", "Khang Pham Ch.7", "Khang Pham Ch.8"],
  "toc_en": [
    "The three-stage funnel",
    "Candidate generation (retrieval)",
    "Ranking models",
    "Re-ranking & business rules",
    "Case patterns: YouTube, feed, Airbnb",
    "LLM-assisted ranking",
    "Numbers to remember",
  ],
  "toc_zh": [
    "三段漏斗",
    "候选生成（召回）",
    "排序模型",
    "重排与业务规则",
    "案例：YouTube、Feed、Airbnb",
    "LLM 辅助排序",
    "要背下来的数字",
  ],
  "body_en": """
        <div class="callout openai">
          <h4>Source cross-reference</h4>
          <p>Primary: Khang Pham <strong>Ch.2 (core ML / embeddings)</strong>, <strong>Ch.3 (YouTube video recs)</strong>, <strong>Ch.4 (feed ranking)</strong>, <strong>Ch.7 (Airbnb similar listings)</strong>, <strong>Ch.8 (LinkedIn personalized search)</strong>. Cross-reference with Chip Huyen Ch.6 for offline eval metrics (NDCG, MAP).</p>
        </div>

        <h2 id="s1">The three-stage funnel</h2>
        <p>Every large-scale recommender at Google, Meta, LinkedIn, Pinterest, and Airbnb uses the same shape: <strong>billions of items -&gt; thousands -&gt; hundreds -&gt; tens</strong> across three stages. The funnel exists because no single model can be both cheap enough to score a billion items and smart enough to rank ten of them.</p>
        <div class="mermaid-container"><pre class="mermaid">
flowchart LR
  corpus[(Corpus<br/>10^9 items)] --> cg[Candidate Generation<br/>many sources in parallel<br/>two-tower, collab filtering, popularity]
  cg --> merge[Merge &amp; dedup<br/>~1,000 items]
  merge --> rank[Ranking<br/>heavy model<br/>wide&amp;deep / DLRM / transformer]
  rank --> rerank[Re-rank<br/>diversity, business rules<br/>LLM-assisted]
  rerank --> ui[UI · top 10-50]
        </pre></div>
        <p>Per-stage latency budget for a 200 ms end-to-end feed: <strong>retrieval &le; 40 ms, ranking &le; 80 ms, re-rank &le; 20 ms, network+render &le; 60 ms</strong>. Every successful design you have seen in an interview fits this pattern.</p>

        <h2 id="s2">Candidate generation (retrieval)</h2>
        <p>Goal: from 10^9 items, return O(10^3) that are worth ranking. Three families:</p>
        <ol>
          <li><strong>Two-tower / dual encoder</strong>: one tower encodes the user (history, demographics), one encodes the item; train with sampled-softmax / in-batch negatives so that <code>&lt;user, item&gt; &asymp; score</code>. Serve by ANN search (ScaNN, HNSW, FAISS) on the item side. This is the YouTube recs backbone (Ch.3).</li>
          <li><strong>Collaborative filtering / matrix factorisation</strong>: older but still strong for cold-start-free domains. Ch.2 covers the primer.</li>
          <li><strong>Rule-based / heuristic</strong>: popular-in-your-country, recency, "friends' recent posts". Cheap safety net; LinkedIn's feed (Ch.4) ensembles 10+ such generators.</li>
        </ol>
        <p>Key design choices:</p>
        <ul>
          <li><strong>Negative sampling</strong>: random negatives are too easy; hard negatives (same session, almost clicked) dominate modern two-tower. In-batch negatives are free.</li>
          <li><strong>Embedding dim</strong>: 64-256 is typical. Larger embeddings buy accuracy and latency/storage pain.</li>
          <li><strong>ANN index</strong>: HNSW beats flat at 10^6+ items; quantised ScaNN beats HNSW at 10^8+ with 4x memory cut.</li>
        </ul>

        <h2 id="s3">Ranking models</h2>
        <p>Ranking scores each of the ~1,000 candidates with a heavy model that can consume hundreds of features.</p>
        <ul>
          <li><strong>Wide &amp; Deep</strong> (Cheng 2016, Google Play): wide linear arm memorises sparse crosses, deep MLP generalises. Still the simplest respectable baseline. Ch.5 shows the ad-CTR version.</li>
          <li><strong>DLRM</strong> (Meta, 2019): embedding tables for categoricals -&gt; feature-interaction layer (dot products) -&gt; MLP. Workhorse of Meta ranking; the open-source code is a great reference. Memory is dominated by embedding tables (often &gt;100 GB).</li>
          <li><strong>DeepFM / DCN-V2</strong>: explicit cross-feature networks; replace the wide arm.</li>
          <li><strong>Transformer rankers (SASRec, BST)</strong>: sequence-aware, handle long user history natively; Alibaba and Pinterest have public results.</li>
          <li><strong>Multi-task heads</strong>: one tower predicts click, watch-time, share, report; combine with a learned or hand-tuned scalarisation. Ch.3's YouTube design uses this explicitly.</li>
        </ul>
        <div class="callout tip">
          <h4>Loss functions in one line</h4>
          <p><strong>Pointwise</strong> (log-loss) for CTR; <strong>pairwise</strong> (BPR / LambdaRank) when you have implicit comparisons; <strong>listwise</strong> (softmax-CE / LambdaMART) when NDCG is the target. Airbnb's Aerosolve (Ch.7) uses pairwise hinge loss.</p>
        </div>

        <h2 id="s4">Re-ranking &amp; business rules</h2>
        <p>The last stage applies constraints the ranker cannot see inside its objective:</p>
        <ul>
          <li><strong>Diversity</strong>: MMR (maximal marginal relevance), DPP (determinantal point process), per-category caps (e.g. "no more than 3 videos from the same creator in top 10"). Facebook's feed explicitly enforces creator diversity.</li>
          <li><strong>Freshness</strong>: time-decay boosts for new items; counteracts popularity bias.</li>
          <li><strong>Business rules</strong>: policy filters (e.g. must be available in user's country), ad-slot blending, creator ecosystem rules.</li>
          <li><strong>Calibration</strong>: rescale scores so they reflect probability, important when scores blend across systems (ads + organic).</li>
        </ul>

        <h2 id="s5">Case patterns: YouTube, feed, Airbnb</h2>
        <p>Three canonical shapes you should be able to draw in 2 minutes:</p>
        <ul>
          <li><strong>YouTube (Ch.3)</strong>: two-tower retrieval from billions of videos with user watch-history + context; ranking is a multi-task model optimising click + watch-time + satisfaction survey; hard negatives are sampled from the same session. 20+ retrieval sources merged.</li>
          <li><strong>Feed ranking &mdash; Facebook/LinkedIn (Ch.4, Ch.8)</strong>: candidates from "friends' posts", "pages you follow", "groups", "sponsored" streams; ranker is a DLRM-style multi-task model predicting click, dwell, like, share, hide. LinkedIn layers a second-pass ranking after re-rank to optimise recruiter value.</li>
          <li><strong>Airbnb search (Ch.7)</strong>: user-location + query geohash + listing features; two-tower produces listing embeddings trained with "user viewed A then booked B" pairs; ranker is gradient-boosted trees until recently, now wide-and-deep. Seasonality and host-cancellation risk are explicit features.</li>
        </ul>

        <h2 id="s6">LLM-assisted ranking</h2>
        <p>Interview-relevant since 2024:</p>
        <ul>
          <li><strong>LLM as a feature</strong>: precompute item descriptions via an LLM, embed with a sentence encoder; feed as extra features to the ranker. No inference-path LLM call -&gt; cheap and safe.</li>
          <li><strong>LLM as a re-ranker</strong>: give a top-20 shortlist plus user context to an LLM, have it output a permutation or score. 200-500 ms extra latency; only justified for high-value surfaces (e.g. flagship recommendations home).</li>
          <li><strong>LLM-generated candidates</strong>: "user is planning a trip to Kyoto, suggest experiences" -&gt; LLM proposes 10 concepts -&gt; resolved to real items via retrieval. Used by Airbnb and Spotify in 2024 launches.</li>
        </ul>
        <div class="callout warn">
          <h4>Anti-pattern: put an LLM on every query</h4>
          <p>An LLM call at 400 ms p50 / 2 s p99 on a 100 ms feed budget is infeasible at scale. Use LLMs only (a) offline to enrich items, (b) for very top slots, (c) behind a caching layer with aggressive TTL. Always have a non-LLM fallback path.</p>
        </div>

        <h2 id="s7">Numbers to remember</h2>
        <div class="callout tip">
          <h4>Cheat-sheet</h4>
          <ul>
            <li>Retrieval output: 500-2,000 candidates.</li>
            <li>Ranking input: up to 1,000, output: top ~50.</li>
            <li>Typical two-tower embedding: 64-256 dims; item index 10^8 items -&gt; ANN ~10 ms p99 with HNSW (M=32, efSearch=128).</li>
            <li>Feed end-to-end latency budget: 100-200 ms; ranking model &le; 80 ms on CPU with INT8 quantisation, or ~20 ms on a T4.</li>
            <li>Offline metrics: <strong>NDCG@10 &ge; 0.4</strong> is acceptable baseline on public datasets; production wins are often measured in 0.5-2% relative CTR lift per quarter.</li>
            <li>A/B sample size: 1-2 weeks, &ge;1M users per arm, for a 0.5% MDE on CTR at alpha=0.05, power=0.8.</li>
          </ul>
        </div>
        <div class="callout openai">
          <h4>OpenAI lens</h4>
          <p>OpenAI-style questions emphasise <em>latency budgets</em> and <em>cost per 1k requests</em>. Be ready to compute: "your ranker adds 30 ms and costs $0.01 per 1k requests &mdash; is that worth a 0.3% CTR lift?" Most candidates cannot answer without thinking; pre-bake a framework.</p>
        </div>
        <div class="callout anthropic">
          <h4>Anthropic lens</h4>
          <p>Anthropic wants recommenders that do not recommend harm. Expect probing on <em>negative</em> objectives (avoid showing self-harm, misinformation, PII leakage from retrieved docs), on slice-wise fairness audits, and on clear escape hatches for users to contest rankings. Treat safety as a first-class ranker objective, not an afterthought re-ranker filter.</p>
        </div>
""",
  "body_zh": """
        <div class="callout openai">
          <h4>来源对照</h4>
          <p>主源：Khang Pham <strong>Ch.2（ML 与 embedding 入门）</strong>、<strong>Ch.3（YouTube 视频推荐）</strong>、<strong>Ch.4（feed 排序）</strong>、<strong>Ch.7（Airbnb 相似房源）</strong>、<strong>Ch.8（LinkedIn 个性化搜索）</strong>。离线评估指标（NDCG、MAP）见 Chip Huyen 第 6 章。</p>
        </div>

        <h2 id="s1">三段漏斗</h2>
        <p>Google、Meta、LinkedIn、Pinterest、Airbnb 的大规模推荐系统全是同一个形状：<strong>十亿级 &rarr; 千级 &rarr; 百级 &rarr; 十级</strong>，三段漏斗。为什么要分段？因为没有一个模型既便宜到能给十亿个物品打分，又聪明到能把十个物品排好。</p>
        <div class="mermaid-container"><pre class="mermaid">
flowchart LR
  corpus[(语料<br/>10^9 item)] --> cg[候选生成<br/>多路并行<br/>双塔 · 协同过滤 · 热门]
  cg --> merge[合并去重<br/>~1000]
  merge --> rank[排序<br/>重模型<br/>wide&amp;deep / DLRM / transformer]
  rank --> rerank[重排<br/>多样性 · 业务规则<br/>LLM 辅助]
  rerank --> ui[UI · Top 10-50]
        </pre></div>
        <p>200 ms 端到端预算下的各段延迟：<strong>召回 &le; 40 ms，排序 &le; 80 ms，重排 &le; 20 ms，网络+渲染 &le; 60 ms</strong>。你在面试里见过的所有成功设计都是这个形状。</p>

        <h2 id="s2">候选生成（召回）</h2>
        <p>目标：从 10^9 个物品里取 O(10^3) 值得排序的。三种套路：</p>
        <ol>
          <li><strong>双塔 / dual encoder</strong>：一个塔编码用户（历史、画像），一个塔编码物品；用 sampled-softmax / in-batch negatives 训练，使得 <code>&lt;user, item&gt; &asymp; score</code>；上线时在物品侧做 ANN（ScaNN、HNSW、FAISS）。这是 YouTube 推荐的骨干（Ch.3）。</li>
          <li><strong>协同过滤 / 矩阵分解</strong>：传统但在非冷启场景仍强。Ch.2 入门足够。</li>
          <li><strong>规则 / 启发式</strong>：所在国热门、最近、「朋友近期动态」。便宜的安全网；LinkedIn feed（Ch.4）同时集成 10+ 路。</li>
        </ol>
        <p>关键决策：</p>
        <ul>
          <li><strong>负样本采样</strong>：随机负太简单；hard negatives（同 session、差点就点）是现代双塔的主力。in-batch negatives 白嫖。</li>
          <li><strong>embedding 维度</strong>：64-256 常见。维度越高越准，但延迟和存储也越贵。</li>
          <li><strong>ANN 索引</strong>：10^6+ 时 HNSW 优于 flat；10^8+ 时量化 ScaNN 比 HNSW 再省 4x 内存。</li>
        </ul>

        <h2 id="s3">排序模型</h2>
        <p>排序把 ~1000 个候选逐个用重模型打分，可吃数百个特征。</p>
        <ul>
          <li><strong>Wide &amp; Deep</strong>（Cheng 2016，Google Play）：宽线性臂记忆稀疏交叉，深 MLP 泛化。最简单靠谱的基线。Ch.5 讲广告 CTR 版本。</li>
          <li><strong>DLRM</strong>（Meta，2019）：类别型走 embedding 表 &rarr; 特征交互层（点积）&rarr; MLP。Meta 排序主力，开源代码值得看。内存主要被 embedding 表占（常 &gt;100 GB）。</li>
          <li><strong>DeepFM / DCN-V2</strong>：显式交叉网络，替代宽臂。</li>
          <li><strong>Transformer 排序（SASRec、BST）</strong>：对长用户历史天然；阿里、Pinterest 已公开效果。</li>
          <li><strong>多任务头</strong>：一座塔同时预测 click、watch-time、share、report，用学到或人工配的标量化融合。Ch.3 YouTube 明确这么做。</li>
        </ul>
        <div class="callout tip">
          <h4>损失函数一句话</h4>
          <p><strong>pointwise</strong>（log-loss）用于 CTR；<strong>pairwise</strong>（BPR / LambdaRank）有隐式比较；<strong>listwise</strong>（softmax-CE / LambdaMART）目标是 NDCG。Airbnb 的 Aerosolve（Ch.7）用 pairwise hinge。</p>
        </div>

        <h2 id="s4">重排与业务规则</h2>
        <p>最后一段加上排序目标里不好表达的约束：</p>
        <ul>
          <li><strong>多样性</strong>：MMR、DPP、分类帽子（「Top 10 里同创作者最多 3 条」）。Facebook feed 明确强制创作者多样性。</li>
          <li><strong>新鲜度</strong>：新物品时间衰减加权，抵消流行度偏差。</li>
          <li><strong>业务规则</strong>：合规过滤（必须在用户所在国可用）、广告位混排、创作者生态规则。</li>
          <li><strong>校准</strong>：让打分反映概率，跨系统混排时（广告 + 有机）尤其关键。</li>
        </ul>

        <h2 id="s5">案例：YouTube、Feed、Airbnb</h2>
        <p>三个你应该能 2 分钟画出来的经典形状：</p>
        <ul>
          <li><strong>YouTube（Ch.3）</strong>：双塔从十亿视频召回，塔输入是用户历史 + 上下文；排序是多任务模型（click + watch-time + 满意度问卷）；hard negatives 同会话采样。20+ 路召回合并。</li>
          <li><strong>Feed——Facebook/LinkedIn（Ch.4, Ch.8）</strong>：候选来自「朋友动态」「关注页面」「群组」「赞助」多流；排序是 DLRM 风格多任务（click、dwell、like、share、hide）。LinkedIn 在重排之后再加一层二次排序优化招聘价值。</li>
          <li><strong>Airbnb 搜索（Ch.7）</strong>：用户位置 + 查询 geohash + 房源特征；双塔用「看过 A 然后订了 B」对训练房源 embedding；排序长期是 GBDT，近几年迁到 wide&amp;deep。季节性、房东取消风险是显式特征。</li>
        </ul>

        <h2 id="s6">LLM 辅助排序</h2>
        <p>2024 年后面试必考：</p>
        <ul>
          <li><strong>LLM 当特征</strong>：离线用 LLM 给物品写描述，再用句向量 encode，作为额外特征给排序模型。推理链路没有 LLM 调用——便宜且稳。</li>
          <li><strong>LLM 当重排</strong>：把 Top-20 + 用户上下文给 LLM，让它输出一个排列或分数。额外 200-500 ms 延迟；只适合高价值位置（例如首页旗舰推荐）。</li>
          <li><strong>LLM 生成候选</strong>：「用户在计划京都旅行，建议体验项目」&rarr; LLM 提议 10 个概念 &rarr; 用检索解析到真实物品。Airbnb、Spotify 2024 都上过。</li>
        </ul>
        <div class="callout warn">
          <h4>反模式：每条请求都套 LLM</h4>
          <p>LLM 调用 p50 400 ms / p99 2 s，对 100 ms 预算的 feed 完全不可行。只在（a）离线给物品打标签，（b）最顶部位置，（c）带 TTL 缓存时使用；始终保留非 LLM 回退路径。</p>
        </div>

        <h2 id="s7">要背下来的数字</h2>
        <div class="callout tip">
          <h4>速查表</h4>
          <ul>
            <li>召回输出：500-2,000 个候选。</li>
            <li>排序输入：至多 1,000，输出 Top ~50。</li>
            <li>常见双塔 embedding：64-256 维；10^8 item 规模下 HNSW（M=32, efSearch=128）p99 &asymp; 10 ms。</li>
            <li>Feed 端到端预算 100-200 ms；排序模型 CPU+INT8 &le; 80 ms，T4 &asymp; 20 ms。</li>
            <li>离线指标：公开数据集 <strong>NDCG@10 &ge; 0.4</strong> 算合格基线；生产胜率常以每季度 0.5-2% 相对 CTR 提升衡量。</li>
            <li>A/B 样本：每臂 &ge;100 万用户、1-2 周，可在 alpha=0.05、power=0.8 下检出 0.5% 的 MDE。</li>
          </ul>
        </div>
        <div class="callout openai">
          <h4>OpenAI 视角</h4>
          <p>OpenAI 风格的题目看重<em>延迟预算</em>和<em>每千请求成本</em>。要能当场算：「这个 ranker 多加 30 ms、每千请求贵 0.01 美元——换 0.3% CTR 提升值不值？」多数候选人临场卡住；提前把框架练熟。</p>
        </div>
        <div class="callout anthropic">
          <h4>Anthropic 视角</h4>
          <p>Anthropic 要的是不推荐伤害的推荐器。会深挖<em>负向</em>目标（避免自伤、虚假信息、从检索文档里泄漏 PII）、分片公平性审计、以及让用户能申诉的透明通道。把安全当一等目标塞进 ranker，而不是在重排层打补丁。</p>
        </div>
""",
  "links": [
    ("Prev", "上一篇", "./drift-monitoring.html",
     "Drift Detection & Monitoring", "漂移检测与监控"),
    ("Arena", "真题", "../../arena/questions/o8-search-recommendation-llm.html",
     "O8 · Search / recommendation + LLM", "O8 · 搜索/推荐 + LLM"),
    ("Arena", "真题", "../../arena/questions/a16-low-latency-inference-api.html",
     "A16 · Low-latency ML inference API", "A16 · 低延迟 ML 推理 API"),
    ("Related", "相关", "../llm/rag.html",
     "RAG Architecture", "RAG 架构"),
    ("Related", "相关", "../safety/safety-engineering.html",
     "Safety Engineering", "安全工程"),
  ],
},
]
