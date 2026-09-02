# AI Skills

个人 AI Agent Skill 仓库，沉淀可复用的方法论、任务流程、脚本与参考资料，适用于支持 `SKILL.md` 约定的 Agent 环境（如 Codex、Claude Code、WorkBuddy 等）。

每个 Skill 聚焦一类明确任务：由 `SKILL.md` 定义触发条件、工作方法和交付标准；需要自动化或领域细节时，再按需读取同目录的 `scripts/` 与 `references/`。

## 技能索引

| Skill | 解决的问题 | 主要交付/能力 | 配套资源 |
| --- | --- | --- | --- |
| [crm-module-analysis](./crm-module-analysis/) | 将客户、线索、商机、报价、合同、订单、服务等 CRM 业务域做成可交付的咨询分析 | 模块定位、状态机、规则、数据模型、RACI、SLA、KPI、问题库与咨询手册 | 方法论库、章节模板、`md2html.py` HTML 转换器 |
| [travel-guide-from-xhs](./travel-guide-from-xhs/) | 基于小红书等内容与实时信息制作旅行攻略 | 出行方案、逐日行程、预算、避坑清单、行动时间线 | 小红书笔记抓取与评论脚本、笔记提取说明 |
| [travel-plan-with-xhs](./travel-plan-with-xhs/) | 将旅行偏好、内容经验与可核验的交通/住宿信息整合为可执行计划 | 可预订、可跟随的旅行计划；区分经验建议与实时事实 | 旅行调研与核验方法 |

## 快速使用

1. 克隆或下载本仓库。
2. 将需要的**单个 Skill 目录**复制到所用 Agent 的 skills 目录。
3. 在对话中直接描述任务，或按 Agent 的语法显式调用对应 Skill。

```text
ai-skills/
├── crm-module-analysis/
│   ├── SKILL.md
│   └── references/
├── travel-guide-from-xhs/
│   ├── SKILL.md
│   ├── scripts/
│   └── references/
└── travel-plan-with-xhs/
    └── SKILL.md
```

示例：

```text
使用 crm-module-analysis，帮我系统剖析 CRM 的商机管理模块。

使用 travel-plan-with-xhs，为 7 月的北海道之行制定可执行行程。
```

> 不同 Agent 的安装目录与调用语法不同；请以对应产品的 Skill 文档为准。复制目录时请保留 `SKILL.md`、`scripts/` 与 `references/` 的相对路径。

## 仓库约定

每个 Skill 使用以下最小结构：

```text
skill-name/
├── SKILL.md            # 必需：名称、触发条件、工作流与交付标准
├── scripts/            # 可选：可重复执行的自动化脚本
└── references/         # 可选：按需读取的方法、模板或领域资料
```

- `SKILL.md` 保持聚焦：写清何时使用、关键判断和不可遗漏的交付约束。
- 重复执行或容易出错的操作放在 `scripts/`，并在 `SKILL.md` 中说明使用时机。
- 仅在任务需要时读取 `references/`，避免把所有背景材料塞进主说明文件。
- 新增或更新 Skill 后，同步更新本 README 的技能索引和配套资源描述。

## 添加新 Skill

1. 在仓库根目录创建小写连字符命名的目录，例如 `customer-health-analysis/`。
2. 创建包含 YAML frontmatter 的 `SKILL.md`，明确 Skill 名称、用途、触发范围与边界。
3. 仅在确有复用价值时增加 `scripts/` 或 `references/`。
4. 用一个真实任务验证触发、流程与交付是否符合预期。
5. 在上方“技能索引”新增一行，说明它解决的问题、主要能力和配套资源。

## 维护原则

- 方法论优先于功能清单：Skill 应帮助 Agent 作出更好的任务判断，而非堆叠泛化说明。
- 事实、假设与建议分开表达；涉及实时数据、价格、政策或预订信息时先核验。
- 对外部系统、账户和文件的写入，应在获得用户授权后进行。

---

维护者：[alllenyan](https://github.com/alllenyan)
