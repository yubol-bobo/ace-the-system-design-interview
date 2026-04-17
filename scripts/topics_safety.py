"""Safety & Alignment Engineering topics for the SD-Guide study module.

Rendered by gen_guide.py into /pages/guide/safety/<slug>.html.
Anthropic's per-round safety gate makes this section table-stakes.
"""

TOPICS = [

# =====================================================================
# 1. Safety Engineering
# =====================================================================
{
  "category": "safety",
  "slug": "safety-engineering",
  "title_en": "Safety Engineering",
  "title_zh": "安全工程",
  "lead_en": "Anthropic's per-round safety gate and OpenAI's Trust & Safety layer share one architecture: layered defences (input filter, constitutional / policy check, policy router, output filter), a red-team platform, and a human-review workflow. This note gives you the reference blueprint, the harm taxonomy every candidate should know, and the RLHF vs DPO vs CAI comparison interviewers probe for.",
  "lead_zh": "Anthropic 每轮面试都有安全关，OpenAI 的 Trust &amp; Safety 层共享同一架构：分层防御（输入过滤 &rarr; 宪法/策略检查 &rarr; 策略路由 &rarr; 输出过滤）、红队平台、人工审核流程。本文给出参考蓝图、每位候选人都该熟悉的伤害分类，以及面试常深挖的 RLHF / DPO / CAI 对比。",
  "tags": ["Layered defence", "Red-team", "CAI", "RLHF", "Prompt injection", "Incident response"],
  "refs": ["Agentic Design Patterns Ch.18", "Bai et al. 2022 (Constitutional AI)", "Chip Huyen Ch.11"],
  "toc_en": [
    "Why safety is an architecture, not a filter",
    "Harm taxonomies every candidate should know",
    "Layered defences blueprint",
    "Red-team platform & eval infra",
    "RLHF vs DPO vs CAI",
    "Human review & incident response",
    "Anthropic-specific interview expectations",
  ],
  "toc_zh": [
    "安全是一套架构，不是一个过滤器",
    "每位候选人都要懂的伤害分类",
    "分层防御参考蓝图",
    "红队平台与评估基建",
    "RLHF vs DPO vs CAI",
    "人工审核与事故响应",
    "Anthropic 面试特定预期",
  ],
  "body_en": """
        <div class="callout anthropic">
          <h4>Source cross-reference</h4>
          <p>Primary sources: <strong>Gulli, Agentic Design Patterns Ch.18 "Guardrails / Safety Patterns" and Ch.19 "Evaluation and Monitoring"</strong>; <strong>Bai et al. 2022 "Constitutional AI" (arXiv:2212.08073)</strong>; <strong>Chip Huyen Ch.11 "The Human Side of ML"</strong>. This page is the single highest-leverage topic for Anthropic interviews &mdash; every round touches it.</p>
        </div>

        <h2 id="s1">Why safety is an architecture, not a filter</h2>
        <p>Beginners picture safety as "a classifier that blocks bad content". This fails immediately under real traffic. A jailbreak like "ignore previous instructions and..." will bypass a single classifier; a prompt-injection via a retrieved webpage will bypass it from a completely different direction; a data-exfil attack will slip through by phrasing the request benignly. The only defensible posture is <strong>defence in depth</strong>: many cheap layers, each targeting a different failure mode, with monitoring that detects when any layer fires.</p>
        <p>Anthropic treats this as a first-class <em>architecture problem</em>. Expect interviewers to push past the "add a classifier" answer and ask: what exact layers, in what order, with what failure behaviour, at what latency cost, with what observability, and with what human backstop when the automated layers are wrong. OpenAI's Trust &amp; Safety team asks the same questions with different emphasis.</p>

        <h2 id="s2">Harm taxonomies every candidate should know</h2>
        <p>You cannot design safety without a categorisation of what you are preventing. The canonical set covers seven harm families:</p>
        <ol>
          <li><strong>CSAM</strong> (child sexual abuse material): legal obligation, zero-tolerance, specialised hash-matching (PhotoDNA) and specialised classifiers. Never handled by general-purpose filters alone.</li>
          <li><strong>PII leakage</strong>: credit cards, SSNs, health records, addresses. Both input (users pasting PII) and output (model memorising training data) directions.</li>
          <li><strong>CBRN</strong> (chemical, biological, radiological, nuclear): uplift for mass-casualty weapons. Covered explicitly by Anthropic's RSP (Responsible Scaling Policy) and OpenAI's Preparedness framework.</li>
          <li><strong>Self-harm &amp; suicide</strong>: dedicated escalation paths to safety messaging plus human review.</li>
          <li><strong>Violent extremism / targeted harassment</strong>: content, but also users organising to attack individuals.</li>
          <li><strong>Jailbreaks</strong>: adversarial prompts aimed at bypassing the model's policy (DAN, "roleplay as an evil AI", many-shot jailbreaking).</li>
          <li><strong>Prompt injection</strong> (a 2023-era addition): hostile instructions smuggled through tool outputs, retrieved documents, or images. Distinct from jailbreak because the attacker is not the user.</li>
        </ol>
        <p>A good answer lists all seven in the first 90 seconds, then deep-dives wherever the interviewer pushes.</p>

        <h2 id="s3">Layered defences blueprint</h2>
        <div class="mermaid-container"><pre class="mermaid">
flowchart LR
  u[User prompt] --> in1[L1 · Input filter<br/>regex · PII redact · CSAM hash]
  in1 --> in2[L2 · Intent classifier<br/>harm-family routing]
  in2 --> pol[L3 · Policy router<br/>small · medium · human]
  pol -->|safe| llm[LLM generation]
  pol -->|risky| cai[L4 · Constitutional check<br/>self-critique prompt]
  cai --> llm
  llm --> out1[L5 · Output classifier<br/>harm categories]
  out1 --> out2[L6 · PII / code / URL scrub]
  out2 --> log[L7 · Audit log<br/>sampled -&gt; human review]
  log --> u2[User response]
  in1 -.block.-> refusal[Structured refusal<br/>with safer-alternative]
  out1 -.block.-> refusal
        </pre></div>
        <p>Budget-conscious design rules:</p>
        <ul>
          <li><strong>Cheap layers first</strong>: regex / hash / small classifier run in 1-3 ms per check; heavy LLM self-critique only fires on the ~5% flagged subset.</li>
          <li><strong>Fail closed for high-harm categories</strong> (CSAM, CBRN), fail open with logging for borderline cases &mdash; over-refusal is itself a safety metric (hurts helpfulness, drives users to less-safe alternatives).</li>
          <li><strong>Always return a structured refusal</strong>, never a silent block. Refusal carries a category code for analytics and a safer-alternative suggestion for the user.</li>
          <li><strong>Sample every interaction into an audit stream</strong> (1-5%) for human review. Without this you cannot close the loop.</li>
        </ul>
        <div class="callout tip">
          <h4>Concrete numbers</h4>
          <p>Typical production targets: input+output filter p99 &lt; 50 ms combined; overall false-positive (over-refusal) rate &lt; 2% on a benign prompt eval; false-negative rate &lt; 0.1% on a red-team eval set of 10k adversarial prompts. Human review queue SLA: high-severity &lt; 15 min, medium &lt; 4 h.</p>
        </div>

        <h2 id="s4">Red-team platform &amp; eval infra</h2>
        <p>A red-team platform is an internal product, not a one-off exercise. Four subsystems:</p>
        <ol>
          <li><strong>Attack library</strong>: versioned corpus of known adversarial prompts, tagged by harm category, attack technique (DAN, prompt injection, many-shot, encoded/cipher), severity, discovery date. 10k-100k at mature orgs.</li>
          <li><strong>Automated red-teaming</strong>: an LLM attacker that generates adversarial variants, scored by a judge model or a classifier. Produces fresh attacks at scale; essential because human red-teamers saturate.</li>
          <li><strong>Evaluation harness</strong>: run a candidate model against the attack library nightly, produce per-category refusal rates and regression alerts. Integrated into the model registry so that no promotion to production can happen without passing the harness.</li>
          <li><strong>Human red team</strong>: paid experts, domain specialists (bio, cyber, legal), external contractors, bug-bounty participants. Automated attackers cannot replace the creativity of a good human adversary.</li>
        </ol>
        <p>Latency note: the attack-evaluation loop should run in minutes, not days. A safety regression caught at canary is an incident; a safety regression caught in human review after GA is a crisis.</p>

        <h2 id="s5">RLHF vs DPO vs CAI</h2>
        <p>Three fine-tuning techniques for aligning a base model to a policy; be able to whiteboard all three.</p>
        <ul>
          <li><strong>RLHF</strong> (Christiano 2017, Ouyang 2022): (1) collect human preference pairs, (2) train a reward model, (3) PPO the policy against the reward model with a KL penalty. Expensive, unstable, but strong results. OpenAI's dominant technique through 2023.</li>
          <li><strong>DPO</strong> (Rafailov 2023): skip the reward model and RL loop by optimising a closed-form loss directly on preference pairs. Simpler, more stable, comparable quality on many benchmarks. Now the default in many open-source efforts.</li>
          <li><strong>CAI</strong> (Bai 2022, Anthropic): replace most of the human preference labelling with a <em>constitution</em> &mdash; a written set of principles the model uses to self-critique and self-revise its outputs. "Is this response harmful under principle 3? Rewrite if so." Dramatically reduces the human labelling required; makes the alignment target inspectable and contestable. Anthropic's signature contribution.</li>
        </ul>
        <div class="mermaid-container"><pre class="mermaid">
flowchart LR
  base[Base LLM] --> rlhf[RLHF<br/>pref pairs + RM + PPO]
  base --> dpo[DPO<br/>closed-form on pref pairs]
  base --> cai[CAI<br/>self-critique by written constitution<br/>+ RLAIF final pass]
  rlhf --> aligned[Aligned model]
  dpo --> aligned
  cai --> aligned
        </pre></div>
        <p>In interviews, the expected move is: "I would use CAI for the broad harm categories where the principles are inspectable, keep a thin human-preference layer for subjective quality, and use DPO rather than PPO for stability and cost."</p>

        <h2 id="s6">Human review &amp; incident response</h2>
        <p>Automated filters are necessary but insufficient; a production safety system always has humans in the loop:</p>
        <ul>
          <li><strong>Reviewer tooling</strong>: triage UI with conversation context, suggested label, keyboard-friendly label actions, wellbeing protections (rotation, hour caps, mandatory counseling for exposure to distressing content).</li>
          <li><strong>Labels feed back into</strong>: classifier training data, prompt-template fixes, policy documentation, attack-library additions.</li>
          <li><strong>Incident response</strong>: pager rotation, severity taxonomy (SEV1 = live harm, SEV2 = pattern, SEV3 = near-miss), kill-switches at the policy router and the model-serving layer, public transparency for SEV1 (post-mortem within a week).</li>
        </ul>
        <div class="callout warn">
          <h4>Anti-pattern: "we will add safety later"</h4>
          <p>Retrofitting safety onto a shipped product costs 5-10x more than building it in, and always leaves permanent gaps. The classifier training data depends on early interaction logs; the human-review workflow depends on early product decisions; rollback requires a kill-switch that has to be designed in. "Safety later" is how high-profile failures happen.</p>
        </div>
        <div class="callout warn">
          <h4>Anti-pattern: over-block as a KPI</h4>
          <p>If your only metric is "blocks per 1k requests", you will over-refuse legitimate queries. Anthropic's own guidance treats unnecessary refusal as a safety failure &mdash; it erodes trust and pushes users to jailbreaks. Always pair block-rate with a benign-prompt false-positive rate.</p>
        </div>

        <h2 id="s7">Anthropic-specific interview expectations</h2>
        <div class="callout anthropic">
          <h4>What Anthropic specifically probes</h4>
          <ul>
            <li><strong>Constitutional thinking</strong>: given a policy question, can you express the trade-off as competing principles rather than a single rule? ("helpfulness vs honesty vs harm avoidance").</li>
            <li><strong>RSP ladder</strong>: show that you know about ASL-2 / ASL-3 capability thresholds and that deployment decisions are gated by <em>measured</em> capability, not vibes.</li>
            <li><strong>Prompt injection</strong>: almost every agent-design interview at Anthropic includes "how do you defend against a malicious tool response?" Show the confused-deputy framing and concrete mitigations (per-tool allowlists, output schemas, cross-tool info-flow policy).</li>
            <li><strong>Transparency</strong>: you log enough to write an honest post-mortem, and you proactively publish safety results.</li>
          </ul>
        </div>
        <div class="callout openai">
          <h4>OpenAI framing differences</h4>
          <p>OpenAI treats safety with equal weight but bias toward <em>product-integrated</em> answers: moderation API, spec-driven policy updates, scalable human review, fine-tuning partnerships with large customers. Expect more emphasis on enterprise boundary cases (data residency, customer-specific policies) and less on the alignment technique itself.</p>
        </div>
        <p>The winning interview narrative for either company: name the seven harms, draw the layered blueprint, place a red-team platform as an explicit subsystem, explain CAI/RLHF/DPO trade-offs, and close with the human review + incident response loop. Show that safety is an <em>engineering discipline</em> with SLOs, regressions, and post-mortems &mdash; not a vibe.</p>
""",
  "body_zh": """
        <div class="callout anthropic">
          <h4>来源对照</h4>
          <p>主要来源：<strong>Gulli《Agentic Design Patterns》Ch.18 安全模式 &amp; Ch.19 评估与监控</strong>；<strong>Bai 等 2022「Constitutional AI」(arXiv:2212.08073)</strong>；<strong>Chip Huyen Ch.11「ML 的人本一面」</strong>。本页是 Anthropic 面试最高杠杆的一章——每一轮都会问到。</p>
        </div>

        <h2 id="s1">安全是一套架构，不是一个过滤器</h2>
        <p>初学者把安全想成「一个分类器挡住坏内容」。真实流量下立刻失效：像「ignore previous instructions and...」这种越狱直接绕单一分类器；通过检索网页注入的 prompt injection 从完全不同方向绕过；数据外泄攻击用中性措辞就能蒙混。唯一站得住的姿态是<strong>深度防御</strong>：许多廉价的层，各针对一种失败模式，并有监控告知哪一层起作用。</p>
        <p>Anthropic 把这当作一流的<em>架构问题</em>。面试官会越过「加分类器」的答案继续追问：具体哪些层、什么顺序、失败时怎么处理、延迟代价多少、可观测性如何、自动层出错时的人工兜底在哪。OpenAI 的 Trust &amp; Safety 也问同样的问题，只是侧重不同。</p>

        <h2 id="s2">每位候选人都要懂的伤害分类</h2>
        <p>不能在没有分类的前提下设计安全。经典七类：</p>
        <ol>
          <li><strong>CSAM</strong>（儿童性剥削素材）：法律义务、零容忍，用 PhotoDNA 等特化哈希匹配与专用分类器，绝不交给通用过滤器。</li>
          <li><strong>PII 泄漏</strong>：信用卡、身份号、健康记录、地址。输入（用户粘贴 PII）和输出（模型记住训练数据）两方向都要防。</li>
          <li><strong>CBRN</strong>（化生放核）：大规模杀伤武器能力抬升。Anthropic 的 RSP、OpenAI 的 Preparedness 框架都显式覆盖。</li>
          <li><strong>自伤与自杀</strong>：专门的升级路径到安全提示语 + 人工审核。</li>
          <li><strong>暴力极端/定向骚扰</strong>：内容本身之外，还要防用户串联攻击个体。</li>
          <li><strong>越狱</strong>：绕过模型策略的对抗 prompt（DAN、「扮演邪恶 AI」、many-shot 越狱）。</li>
          <li><strong>Prompt injection</strong>（2023 新增）：通过工具输出、检索文档、图像夹带的恶意指令。与越狱不同——攻击者不是用户。</li>
        </ol>
        <p>好答案会在头 90 秒内把七类列全，然后按面试官指向深挖。</p>

        <h2 id="s3">分层防御参考蓝图</h2>
        <div class="mermaid-container"><pre class="mermaid">
flowchart LR
  u[用户 prompt] --> in1[L1 · 输入过滤<br/>正则 · PII 脱敏 · CSAM 哈希]
  in1 --> in2[L2 · 意图分类<br/>按伤害族路由]
  in2 --> pol[L3 · 策略路由<br/>小模型 · 中模型 · 人工]
  pol -->|安全| llm[LLM 生成]
  pol -->|风险| cai[L4 · Constitutional 检查<br/>自我批判 prompt]
  cai --> llm
  llm --> out1[L5 · 输出分类器<br/>伤害类别]
  out1 --> out2[L6 · PII / 代码 / URL 清洗]
  out2 --> log[L7 · 审计日志<br/>采样 -&gt; 人工复核]
  log --> u2[返回用户]
  in1 -.拦截.-> refusal[结构化拒答<br/>含更安全替代]
  out1 -.拦截.-> refusal
        </pre></div>
        <p>预算友好的设计原则：</p>
        <ul>
          <li><strong>便宜层在前</strong>：正则 / 哈希 / 小分类器每次 1-3 ms；重的 LLM 自我批判只对约 5% 被标记子集跑。</li>
          <li><strong>高危类别 fail-closed</strong>（CSAM、CBRN），边缘情形 fail-open 并记录——过度拒答本身就是安全指标，会伤害帮助性，把用户赶去更不安全的替代品。</li>
          <li><strong>永远返回结构化拒答</strong>，别静默拦截。拒答带类别码供分析，带更安全的替代建议给用户。</li>
          <li><strong>每次交互都按比例（1-5%）采样进审计流</strong>供人工复核。缺这一环就闭不上反馈回路。</li>
        </ul>
        <div class="callout tip">
          <h4>具体数字</h4>
          <p>生产目标：输入+输出过滤 p99 &lt; 50 ms；对良性 prompt 评估集的整体假阳性（过度拒答）率 &lt; 2%；对 1 万条红队对抗集的假阴性率 &lt; 0.1%。人工审核队列 SLA：高严重 &lt; 15 分钟，中等 &lt; 4 小时。</p>
        </div>

        <h2 id="s4">红队平台与评估基建</h2>
        <p>红队平台是内部产品，不是一次性活动。四个子系统：</p>
        <ol>
          <li><strong>攻击库</strong>：版本化的对抗 prompt 语料，按伤害类别、攻击手法（DAN、prompt injection、many-shot、编码/密文）、严重度、发现日期打标。成熟团队 1 万到 10 万条。</li>
          <li><strong>自动红队</strong>：用一个 LLM 攻击者生成对抗变体，由判定模型或分类器打分。规模化产出新鲜攻击；必不可少，因为人类红队会饱和。</li>
          <li><strong>评估流水线</strong>：每晚把候选模型跑过攻击库，出按类别的拒答率和回归告警。接入模型注册表，未通过此流水线不得晋升到生产。</li>
          <li><strong>人类红队</strong>：付费专家、领域专家（生物、网络、法律）、外包、bug bounty。自动攻击无法替代优秀人类对手的创造力。</li>
        </ol>
        <p>延迟说明：攻击评估回路应在分钟级运行，不是天级。canary 抓到的安全回归是事件；GA 后人工审核才抓到的是危机。</p>

        <h2 id="s5">RLHF vs DPO vs CAI</h2>
        <p>三种把基座模型对齐到策略的微调技术，都要能当白板讲清楚。</p>
        <ul>
          <li><strong>RLHF</strong>（Christiano 2017, Ouyang 2022）：(1) 收集人类偏好对，(2) 训练奖励模型，(3) 用带 KL 惩罚的 PPO 优化策略。贵、不稳，但效果强。2023 年前 OpenAI 的主技术。</li>
          <li><strong>DPO</strong>（Rafailov 2023）：跳过奖励模型与 RL 循环，直接在偏好对上优化闭式损失。更简单、更稳、许多基准上质量相当。如今多数开源工作默认 DPO。</li>
          <li><strong>CAI</strong>（Bai 2022，Anthropic）：用一份<em>宪法</em>（书面原则集）代替多数人类偏好标注，让模型自我批判并自我修订：「此回应是否违反原则 3？若是请改写。」显著减少所需人工标注；让对齐目标可审视、可争辩。Anthropic 的标志性贡献。</li>
        </ul>
        <div class="mermaid-container"><pre class="mermaid">
flowchart LR
  base[基座 LLM] --> rlhf[RLHF<br/>偏好对 + RM + PPO]
  base --> dpo[DPO<br/>偏好对闭式损失]
  base --> cai[CAI<br/>按书面宪法自我批判<br/>+ RLAIF 终轮]
  rlhf --> aligned[对齐后模型]
  dpo --> aligned
  cai --> aligned
        </pre></div>
        <p>面试标准操作：「我会在原则可审视的大类伤害上用 CAI；在主观质量上保留薄人工偏好层；以 DPO 代替 PPO 以求稳定与降本。」</p>

        <h2 id="s6">人工审核与事故响应</h2>
        <p>自动过滤必要但不够；生产安全永远有人在回路中：</p>
        <ul>
          <li><strong>审核工具</strong>：含会话上下文的 triage UI、建议标签、键盘友好的操作、审核员 wellbeing 保护（轮岗、工时上限、强制心理咨询）。</li>
          <li><strong>标签反哺</strong>：分类器训练数据、prompt 模板修复、策略文档、攻击库新增。</li>
          <li><strong>事故响应</strong>：值班轮转、严重度分级（SEV1=真实伤害，SEV2=模式，SEV3=险情），策略路由与服务层双 kill-switch，SEV1 一周内对外透明的 post-mortem。</li>
        </ul>
        <div class="callout warn">
          <h4>反模式：「安全以后再加」</h4>
          <p>对已上线产品补安全，成本是内建的 5-10 倍，且永远留下空洞。分类器训练数据依赖早期交互日志；审核流程依赖早期产品决策；回滚需要预留 kill-switch。「以后再加」就是高曝光事故的源头。</p>
        </div>
        <div class="callout warn">
          <h4>反模式：把过度拦截当 KPI</h4>
          <p>如果指标只有「每千请求拦截次数」，你会过度拒答合法问题。Anthropic 把无谓拒答视为安全失败——侵蚀信任、驱使用户寻找越狱路径。拦截率必须与良性 prompt 假阳性率成对评估。</p>
        </div>

        <h2 id="s7">Anthropic 面试特定预期</h2>
        <div class="callout anthropic">
          <h4>Anthropic 深挖什么</h4>
          <ul>
            <li><strong>宪法式思考</strong>：给你一个策略问题，你能把权衡表达成多个原则的取舍（帮助性 vs 诚实 vs 避伤），而不是单一规则。</li>
            <li><strong>RSP 阶梯</strong>：熟悉 ASL-2 / ASL-3 能力阈值，说明部署决策是由<em>测得的</em>能力门控，不是靠感觉。</li>
            <li><strong>Prompt injection</strong>：Anthropic 的 agent 设计题几乎都会问「如何防御恶意工具响应？」要能用「confused deputy」框架讲出具体缓解（逐工具白名单、输出 schema、跨工具信息流策略）。</li>
            <li><strong>透明度</strong>：日志足以写诚实的 post-mortem，并主动公开安全结果。</li>
          </ul>
        </div>
        <div class="callout openai">
          <h4>OpenAI 视角差异</h4>
          <p>OpenAI 同样重视安全，但偏<em>产品一体化</em>答案：Moderation API、基于 spec 的策略更新、规模化人工审核、与大客户的微调合作。更强调企业边界（数据驻留、客户专属策略），对齐技术本身的细节着墨较少。</p>
        </div>
        <p>对两家公司都适用的获胜叙事：先列出七类伤害；画出分层蓝图；把红队平台作为一等子系统；解释 CAI / RLHF / DPO 的取舍；最后收束到人工审核 + 事故响应回路。展示安全是一门带 SLO、带回归、带 post-mortem 的<em>工程学科</em>——不是氛围。</p>
""",
  "links": [
    ("Arena", "真题", "../../arena/questions/o13-nsfw-detection.html",
     "O13 · NSFW detection at scale", "O13 · 大规模 NSFW 检测"),
    ("Arena", "真题", "../../arena/questions/a25-agentic-system.html",
     "A25 · Agentic system design", "A25 · Agent 系统设计"),
    ("Arena", "真题", "../../arena/questions/a19-prompt-playground.html",
     "A19 · Prompt playground", "A19 · Prompt Playground"),
    ("Related", "相关", "../llm/agentic-patterns.html",
     "Agentic Design Patterns", "Agent 设计模式"),
    ("Related", "相关", "../llm/llm-evaluation.html",
     "LLM Evaluation", "LLM 评估"),
  ],
},

]
