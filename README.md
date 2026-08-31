# ai-skills

我的 AI Agent 技能仓库（WorkBuddy / Claude 等支持 agent skills 的助手通用）。

每个技能按目录组织：`skill-name/` 内含 `SKILL.md` 及其脚本与参考文档。
克隆到本机后，将单个技能目录复制到对应 skills 目录（如 `~/.workbuddy/skills/`）即可启用。

## 技能清单

| 技能 | 说明 | 触发词 |
| ---- | ---- | ------ |
| [travel-guide-from-xhs](./travel-guide-from-xhs/) | 基于小红书博主经验制作旅行攻略与旅行计划表（出行方案、逐日行程、费用预算、避坑清单、行动时间线），含免登录 SSR 抓取与逐图识别 | 旅行攻略、行程规划、X天X晚、小红书笔记读取 |
| [crm-module-analysis](./crm-module-analysis/) | 剖析 CRM 业务模块的通用方法技能：四问框架 → 流程=状态机 → 逐节点规则设计 → 双维度正交检查 → 支撑体系（SLA/数据模型/RACI/KPI）→ 问题库 → 文档化输出，沉淀自线索模块实战（手册 15 节） | 剖析XX模块、XX模块怎么做咨询、一天一个模块、线索/商机/报价/合同/订单模块咨询 |
## 添加新技能

新增技能时在仓库根目录新建文件夹（`skill-name/SKILL.md` + `scripts/` + `references/`），并在上方表格追加一行。