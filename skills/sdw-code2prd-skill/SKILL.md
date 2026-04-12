---
name: sdw-code2prd-skill
description: 参照 base 项目的业务代码进行逆向需求分析，拆解功能模块并汇总生成一份 PRD 文档。用于用户提到“参照 xxx base 项目生成 PRD”“分析项目功能模块并输出 PRD”“从代码逆向整理需求文档”时。
---

# SDW Code To PRD Skill

## 目标

基于用户提供的参考 base 项目代码（或模块路径），识别并拆解业务功能模块，逆向生成结构化 PRD 需求文档（Markdown 单文件）。

## 触发短语

- 帮我参照 xxx base 项目，分析其中的各个功能模块，并生成 PRD 文档
- 帮我分析并生成 xxx 项目的 PRD 文档
- 根据项目代码逆向整理产品需求文档

## 输入格式

- 文本描述（项目背景、目标、业务范围）
- 文件/目录路径（base 项目根目录或子模块路径）
- 可选：已有文档路径（README、接口文档、设计文档）

## 输出格式

- `MD 文档`：单份 PRD 需求文档
- 默认文件名：`PRD_from_codebase.md`
- 结构要求：必须严格符合 `assets/templates/template_prd_automotive_software.md`

## 执行工作流

### 1) 分析并拆解功能模块

- 读取 base 项目业务代码与可用文档，识别核心业务边界
- 按“用户价值 + 业务流程 + 系统职责”拆分功能模块
- 为每个模块提取：
  - 模块目标
  - 用户角色与使用场景
  - 输入/输出
  - 业务规则与约束
  - 关键流程（主流程/异常流程）
  - 依赖关系（上下游模块、外部系统）

### 2) 将模块结论汇总到单份 PRD

- 将所有模块统一汇总到一份 PRD，确保术语一致、边界清晰
- 对重复或交叉能力进行归并，避免模块描述冲突
- 为每个模块补充验收标准（可测试、可验证）
- 按 `assets/templates/template_prd_automotive_software.md` 逐章节填充
- 输出最终 Markdown 文档

## PRD 模板使用规则

- 开始生成 PRD 前，必须先读取：`assets/templates/template_prd_automotive_software.md`
- 输出文档章节必须与模板保持一致，不可缺少主章节
- 若某章节暂缺证据，写明“待确认”并列出问题，不得删除该章节

## 约束

- 不得修改参考 base 项目中的任何代码或配置
- 仅做读取、分析、总结，不执行破坏性命令
- 所有功能模块需求分析必须汇总到同一份 PRD 文档
- 当代码证据不足时，明确标注“推断/待确认”，不得伪造已确认需求
- 生成的 PRD 文档必须符合 `assets/templates/template_prd_automotive_software.md`

## 质量检查清单

在交付前确认：

- [ ] 功能模块拆分完整，覆盖核心业务流程
- [ ] 每个模块均包含目标、流程、规则、验收标准
- [ ] 模块之间依赖关系清晰，无冲突描述
- [ ] 全部需求已汇总到单份 PRD（Markdown）
- [ ] 未修改 base 项目代码
- [ ] PRD 章节结构与模板一致，未缺失主章节

## 示例

### 示例输入

帮我分析并生成 xxx 项目的 PRD 文档，base 项目路径是 `/repo/xxx-base`。

### 期望输出

- 一份 `PRD_from_codebase.md`，并严格符合 `assets/templates/template_prd_automotive_software.md` 的章节要求。
