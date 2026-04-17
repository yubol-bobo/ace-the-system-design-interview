# Book TOCs and Study-Note Grounding

Seven books extracted for OpenAI / Anthropic system-design interview prep.
Each entry: metadata, top-level chapter list with 1-sentence annotation,
highest-leverage chapters, and topics the book is DEFINITIVE on.

---

## 1. Acing the System Design Interview — Zhiyong Tan (Manning, 472 pp)

### Chapters
- **Part 1 — Foundations**
  - Ch 1. A walkthrough of system design concepts — end-to-end scaling tour (GeoDNS, CDN, horizontal scale, FaaS).
  - Ch 2. A typical system design interview flow — how to structure an interview (requirements, API, data model, observability).
  - Ch 3. Non-functional requirements — scalability, availability, fault tolerance, consistency, security, privacy, cost.
  - Ch 4. Scaling databases — replication, sharding, partitioning, large-key-space handling, NoSQL vs SQL.
  - Ch 5. Distributed transactions — 2PC, sagas, event sourcing, CDC, idempotency.
  - Ch 6. Common services for functional partitioning — shared services (metadata, auth, config, object storage, lock).
- **Part 2 — Small-to-medium designs**
  - Ch 7. Design Craigslist.
  - Ch 8. Design a rate-limiting service.
  - Ch 9. Design a notification/alerting service.
  - Ch 10. Design a database batch auditing service — data-quality auditing at scale.
  - Ch 11. Autocomplete / typeahead.
- **Part 3 — Large designs**
  - Ch 12. Design Flickr (photo-sharing/storage).
  - Ch 13. Design a Content Distribution Network (CDN).
  - Ch 14. Design a text messaging app.
  - Ch 15. Design Airbnb (inventory + booking).
  - Ch 16. Design a news feed.
  - Ch 17. Design a dashboard of top 10 products on Amazon by sales (real-time top-K analytics).

### Highest-leverage chapters (interview prep)
Ch 1, 2, 3 (framework + NFRs), Ch 4 (DB scaling), Ch 8 (rate limiter), Ch 13 (CDN), Ch 16 (news feed), Ch 17 (streaming top-K).

### Definitive on
Interview *process* (reflection, self-assessment, requirement discussion) and **functional-partitioning patterns** for shared services (Ch 6). Also uniquely strong on batch-auditing/data-quality services.

---

## 2. Agentic Design Patterns — Antonio Gulli (Springer, 482 pp)

### Chapters
- Front matter: Introduction, "What makes an AI system an agent?"
- **Part One — Core orchestration**
  - Ch 1. Prompt Chaining — sequencing prompts to decompose tasks.
  - Ch 2. Routing — classifier / LLM router dispatches to specialist sub-agents.
  - Ch 3. Parallelization — fan-out / fan-in concurrent tool and agent calls.
  - Ch 4. Reflection — self-critique + revise loops.
  - Ch 5. Tool Use — function / tool calling patterns.
  - Ch 6. Planning — plan-and-execute, decomposition strategies.
  - Ch 7. Multi-Agent — collaborating specialist agents and roles.
- **Part Two — State & context**
  - Ch 8. Memory Management — short/long term, summarization, vector memory.
  - Ch 9. Learning and Adaptation — online tuning, feedback loops.
  - Ch 10. Model Context Protocol (MCP) — standardized tool/data interfaces.
  - Ch 11. Goal Setting and Monitoring — tracking goals against execution.
- **Part Three — Robustness**
  - Ch 12. Exception Handling and Recovery.
  - Ch 13. Human-in-the-Loop.
  - Ch 14. Knowledge Retrieval (RAG).
- **Part Four — Advanced**
  - Ch 15. Inter-Agent Communication (A2A).
  - Ch 16. Resource-Aware Optimization — cost/latency budgeting.
  - Ch 17. Reasoning Techniques — CoT, ToT, self-consistency.
  - Ch 18. Guardrails / Safety Patterns.
  - Ch 19. Evaluation and Monitoring.
  - Ch 20. Prioritization.
  - Ch 21. Exploration and Discovery.
- **Appendices A–G**: advanced prompting, GUI to real-world, agentic frameworks, AgentSpace, CLI agents, reasoning engines, coding agents.

### Highest-leverage chapters
Ch 5 (Tool Use), Ch 7 (Multi-Agent), Ch 8 (Memory), Ch 10 (MCP), Ch 14 (RAG), Ch 18 (Guardrails), Ch 19 (Evaluation), Appendix A (Prompting).

### Definitive on
**Agentic design patterns taxonomy** — the canonical catalog of reusable LLM-agent patterns (routing, reflection, planning, MCP, A2A, guardrails, eval). The go-to source for Anthropic/OpenAI-style agent-system design questions.

---

## 3. ByteByteGo Big Archive: System Design 2023 (344 pp)

Format: compilation of ~150 short illustrated articles (not chapters). Treat as a **reference cheat-sheet**, not a linear textbook.

### Dominant clusters
- **API & protocols**: REST vs gRPC vs GraphQL vs SOAP, OAuth 2.0 flows, JWT/SSO, API gateway, webhooks, HTTP status codes, API security.
- **Databases**: sharding, SQL vs NoSQL, Redis persistence, PostgreSQL deep-dives, data warehouse vs lake, serverless DBs, 8 data structures powering DBs.
- **Caching & CDN**: top-5 caching strategies, cache placement, CDN primer.
- **Messaging**: Kafka/RabbitMQ/Pulsar evolution, event sourcing, stream vs batch.
- **Scalability**: load-balancing algorithms, "zero-to-millions" scaling, unique-ID generators, distributed-system patterns, latency numbers.
- **Cloud & DevOps**: Docker, Kubernetes service types, CI/CD, cloud-native anti-patterns, IaaS/PaaS, AWS 3-tier architecture.
- **Case studies**: Netflix, Uber, Stack Overflow, Twitter, Discord, Amazon Prime Video, ChatGPT, Slack, YouTube.
- **Observability**: logs/traces/metrics pillars, debugging high CPU.

### Highest-leverage articles
Latency numbers every engineer should know; Top-6 load balancing algorithms; DB sharding; Top-5 caching strategies; Kafka deep dive; Message-queue evolution; API architecture styles; 10 NFRs cheatsheet; Netflix/Uber tech stacks.

### Definitive on
**Breadth visuals / cheat-sheet material** and *case-study tech stacks* of real companies (Netflix, Uber, Discord, Slack). Best used for quick recall and diagram inspiration, not deep mechanics.

---

## 4. Designing Data-Intensive Applications — Martin Kleppmann (O'Reilly, 613 pp)

### Chapters
- **Part I — Foundations**
  - Ch 1. Reliable, Scalable, and Maintainable Applications.
  - Ch 2. Data Models and Query Languages — relational, document, graph.
  - Ch 3. Storage and Retrieval — B-trees, LSM-trees, OLTP vs OLAP, column stores.
  - Ch 4. Encoding and Evolution — schemas, Avro/Protobuf/Thrift, backward/forward compat.
- **Part II — Distributed Data**
  - Ch 5. Replication — leader/follower, multi-leader, leaderless, quorums.
  - Ch 6. Partitioning — range vs hash, rebalancing, secondary indexes.
  - Ch 7. Transactions — ACID, isolation levels, snapshot isolation, serializability.
  - Ch 8. The Trouble with Distributed Systems — clocks, partial failure, unreliable networks.
  - Ch 9. Consistency and Consensus — linearizability, ordering, Paxos/Raft, 2PC.
- **Part III — Derived Data**
  - Ch 10. Batch Processing — MapReduce, dataflow engines.
  - Ch 11. Stream Processing — logs, event sourcing, stream joins, exactly-once.
  - Ch 12. The Future of Data Systems — lambda/kappa, end-to-end correctness, ethics.

### Highest-leverage chapters
Ch 1, 3, 5, 6, 7, 8, 9, 11 — essentially most of the book. If picking 6: 5, 6, 7, 8, 9, 11.

### Definitive on
**Replication, partitioning, consensus, isolation levels, stream/batch processing, consistency models.** This is *the* authoritative source for the distributed-systems internals underpinning any system-design interview. No other book in this list comes close on these mechanics.

---

## 5. Designing Machine Learning Systems — Chip Huyen (O'Reilly, 389 pp)

### Chapters
- Ch 1. Overview of Machine Learning Systems — when/why ML, ML-in-production vs research.
- Ch 2. Introduction to Machine Learning Systems Design — framing, objectives, requirements for ML products.
- Ch 3. Data Engineering Fundamentals — sources, formats, OLTP/OLAP, ETL/ELT, modes of dataflow.
- Ch 4. Training Data — sampling, labeling, class imbalance, data augmentation.
- Ch 5. Feature Engineering — missing values, scaling, encoding, feature leakage, feature importance.
- Ch 6. Model Development and Offline Evaluation — model selection, ensembles, experiment tracking, offline metrics, slice-based eval.
- Ch 7. Model Deployment and Prediction Service — batch vs online, model compression, edge vs cloud.
- Ch 8. Data Distribution Shifts and Monitoring — covariate/label/concept drift, detection, retraining triggers.
- Ch 9. Continual Learning and Test in Production — online learning, shadow/canary/A-B/interleaved/bandits.
- Ch 10. Infrastructure and Tooling for MLOps — dev env, resource mgmt, ML platforms, build vs buy.
- Ch 11. The Human Side of Machine Learning — stakeholders, fairness, responsible AI.

### Highest-leverage chapters
Ch 2 (framing), Ch 6 (eval), Ch 7 (deployment), Ch 8 (drift/monitoring), Ch 9 (continual learning + online testing), Ch 10 (MLOps infra), plus Ch 4 or 5.

### Definitive on
**ML-system design lifecycle end-to-end**: the framing framework, drift detection, online-eval strategies (shadow / canary / interleaved / bandits), and MLOps infrastructure decisions. The canonical reference for ML system-design interviews.

---

## 6. Machine Learning Design Interview — Khang Pham (2022, 236 pp)

### Chapters (inferred from front-matter + body)
- Ch 1. Introduction & interview framework for ML system design.
- Ch 2. Core ML / recommender primer — embeddings (word2vec, two-tower), retrieval / ranking / re-ranking, loss functions, pointwise/pairwise, cross features, feature store.
- Ch 3. Video Recommendation (YouTube-style) — retrieval via two-tower, ranking with multitask / multi-head.
- Ch 4. Feed Ranking (Facebook/LinkedIn) — label generation, ranking architecture, scale-out.
- Ch 5. Ads Click Prediction — CTR modeling, delayed feedback, wide-and-deep, calibration.
- Ch 6. Estimate Delivery Time (DoorDash/Uber Eats) — regression + personalization.
- Ch 7. Similar Listings / Airbnb Search Ranking — Hinge loss, Aerosolve, embeddings.
- Ch 8. Personalized Search / LinkedIn Recruiter — layered ranking architecture.
- Ch 9. Practice problems (open-ended design exercises: feed from non-friends, job suggestions, smart notifications, contraband detection, hashtag filtering, demand prediction, etc.).

### Highest-leverage chapters
Ch 2 (core concepts), Ch 3 (YouTube recs), Ch 4 (feed ranking), Ch 5 (ad CTR), Ch 7 (similar-listing embeddings), Ch 8 (search ranking), Ch 9 (mock drills).

### Definitive on
**Applied ML-system-design case studies at FAANG scale** — concrete retrieval/ranking architectures actually used at YouTube, Facebook, LinkedIn, Pinterest, Airbnb, DoorDash. Complements Chip Huyen by going case-by-case, with architectures and metrics.

---

## 7. System Design Interview Vol. 1 — Alex Xu (2nd ed., 269 pp)

### Chapters
- Ch 1. Scale from Zero to Millions of Users — single-server, replication, cache, CDN, sharding.
- Ch 2. Back-of-the-Envelope Estimation — QPS, storage, bandwidth, latency numbers.
- Ch 3. A Framework for System Design Interviews — 4-step process (scope, high-level, deep-dive, wrap-up).
- Ch 4. Design a Rate Limiter — token bucket, leaky bucket, sliding window.
- Ch 5. Design Consistent Hashing — virtual nodes, rebalancing.
- Ch 6. Design a Key-Value Store — Dynamo-style: quorum, vector clocks, Merkle trees, gossip.
- Ch 7. Design a Unique ID Generator in Distributed Systems — Snowflake, UUIDs.
- Ch 8. Design a URL Shortener — hashing + base62, 301 vs 302.
- Ch 9. Design a Web Crawler — politeness, dedup, priority.
- Ch 10. Design a Notification System — fan-out to push/SMS/email providers.
- Ch 11. Design a News Feed System — fan-out on write vs read.
- Ch 12. Design a Chat System — long polling/WebSockets, presence, delivery semantics.
- Ch 13. Design a Search Autocomplete System — trie + ranking + caching.
- Ch 14. Design YouTube — transcoding pipeline, CDN, metadata.
- Ch 15. Design Google Drive — block storage, sync, metadata DB.
- Ch 16. The Learning Continues — broader resources.

### Highest-leverage chapters
Ch 1, 3 (framework), Ch 4 (rate limiter), Ch 6 (KV store - Dynamo), Ch 11 (news feed), Ch 12 (chat), Ch 13 (autocomplete), Ch 14 (YouTube).

### Definitive on
**Interview-ready templates for classic system-design questions** — the best single source of *practice answers* with diagrams. Especially definitive on rate limiter, consistent hashing, Snowflake-style ID gen, and news-feed fan-out tradeoffs.

---

## Cross-cutting topic map (for 15-18 note pages)

| Topic | Primary source | Complements |
|---|---|---|
| Framework & NFRs for SD interviews | Alex Xu Ch 1-3; Acing Ch 1-3 | ByteByteGo (NFRs cheatsheet) |
| Back-of-envelope estimation | Alex Xu Ch 2 | ByteByteGo (latency numbers) |
| Replication / consistency | DDIA Ch 5, 9 | Acing Ch 4 |
| Partitioning / sharding | DDIA Ch 6 | Acing Ch 4; ByteByteGo |
| Consensus (Paxos/Raft) | DDIA Ch 8, 9 | - |
| Transactions & isolation | DDIA Ch 7 | Acing Ch 5 |
| Storage engines (LSM / B-tree) | DDIA Ch 3 | ByteByteGo (DB data structures) |
| Stream / batch processing | DDIA Ch 10, 11 | Acing Ch 17 |
| Rate limiter | Alex Xu Ch 4 | Acing Ch 8 |
| Consistent hashing / ID gen | Alex Xu Ch 5, 7 | ByteByteGo |
| Key-value store (Dynamo) | Alex Xu Ch 6 | DDIA Ch 5, 6 |
| News feed | Alex Xu Ch 11; Acing Ch 16 | - |
| Chat system | Alex Xu Ch 12 | Acing Ch 14 |
| CDN | Acing Ch 13 | Alex Xu Ch 1; ByteByteGo |
| YouTube / video | Alex Xu Ch 14 | Khang Pham Ch 3 |
| Autocomplete | Alex Xu Ch 13; Acing Ch 11 | - |
| ML system design lifecycle | Chip Huyen (whole book) | Khang Pham Ch 1-2 |
| Feature engineering / feature stores | Chip Huyen Ch 5 | Khang Pham Ch 2 |
| Drift / online monitoring | Chip Huyen Ch 8, 9 | - |
| MLOps infra | Chip Huyen Ch 10 | - |
| Recommender (retrieval + ranking) | Khang Pham Ch 2-4 | Chip Huyen Ch 2 |
| CTR / ads ranking | Khang Pham Ch 5 | - |
| Search / personalized ranking | Khang Pham Ch 7, 8 | - |
| Agentic patterns (routing, reflection, planning, multi-agent) | Gulli Ch 1-7 | - |
| Tool use / MCP / A2A | Gulli Ch 5, 10, 15 | - |
| RAG | Gulli Ch 14 | Chip Huyen (monitoring) |
| LLM guardrails / eval | Gulli Ch 18, 19 | Chip Huyen Ch 6 |
| Agent memory | Gulli Ch 8 | - |

### Where multiple books agree (safe to cite widely)
- **Scalability fundamentals** (cache, CDN, LB, shard): Alex Xu Ch 1, ByteByteGo, Acing Ch 1.
- **Rate limiter token/leaky bucket**: Alex Xu Ch 4, Acing Ch 8, ByteByteGo.
- **News feed fan-out tradeoffs**: Alex Xu Ch 11, Acing Ch 16.
- **Replication/sharding tradeoffs**: DDIA Ch 5-6, Acing Ch 4, ByteByteGo.
- **Retrieval + ranking recommender pattern**: Chip Huyen, Khang Pham Ch 2-3.
- **Online eval (shadow/canary/A-B)**: Chip Huyen Ch 9 (and implicit in Khang Pham cases).

### Unique coverage (only-found-here)
- **DDIA**: consensus mechanics, isolation levels, storage internals.
- **Chip Huyen**: ML lifecycle framing + drift + MLOps infra.
- **Khang Pham**: concrete FAANG recommender/ranking case studies.
- **Gulli**: agentic patterns taxonomy, MCP, A2A, agent memory, guardrails.
- **Alex Xu**: ready-to-recite templates for classic questions.
- **Acing**: interview *process/reflection*, functional-partitioning shared services, batch auditing.
- **ByteByteGo**: cheat-sheet diagrams + real-company tech stacks.

> Vol 2 (EPUB) not extracted per instructions; if needed later it adds: Proximity service, Nearby friends, Google Maps, Distributed message queue, Metrics monitoring, Ad click aggregation, Hotel reservation, Distributed email, S3-like object storage, real-time gaming leaderboard, payment system, digital wallet, stock exchange.
