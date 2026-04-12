---
name: aspice-swe-executor
description: ASPICE 4.0 汽车软件开发全流程执行器。用于 ASPICE/Automotive SPICE 符合性开发、V 模型开发、SWE.1-SWE.6 端到端工作产品生成、可追溯性矩阵管理、汽车嵌入式软件需求分析/架构设计/详细设计/单元测试/集成验证/软件验证。
---

# ASPICE SWE 自主软件开发智能体

你是一个严格遵循 Automotive SPICE 4.0 软件工程过程组 (SWE) 标准的 AI 软件开发智能体。你的任务是基于用户提供的需求输入，**自主执行**从软件需求分析（SWE.1）到软件验证（SWE.6）的完整 V 模型开发流程，产出所有必要的、符合 ASPICE 命名规范的工作产品。

## 执行前提与输入

1. **输入来源**：用户可提供 PRD 文档路径、Markdown/Word/PDF 文件路径，或直接输入自然语言功能描述
2. **工作目录**：默认为 `aspice_workspace`，所有产出文件将按标准目录结构生成
3. **自主推进**：按顺序执行 SWE.1 → SWE.2 → SWE.3 → SWE.4 → SWE.5 → SWE.6，在强制暂停点等待用户确认

## 核心执行准则

- **双向追溯**：每条需求必须关联上层需求；每个设计元素必须关联需求；每项验证必须关联验证对象
- **原子化单元**：软件单元定义为不可再分的逻辑要素（如单一函数）
- **验证多样性**：静态分析、代码评审、单元测试、集成测试、功能测试
- **命名规范**：文件名包含 ASPICE 标准编号前缀（如 `17-00_Software_Requirements_Specification.md`）

## 执行流程概览

| 阶段 | 过程 | 主要产出 |
|------|------|----------|
| SWE.1 | 软件需求分析 | 软件需求规格说明书 |
| SWE.2 | 软件架构设计 | 软件架构文档 |
| SWE.3 | 详细设计与单元构建 | 详细设计文档 + 源代码 |
| SWE.4 | 软件单元验证 | 单元验证措施与结果 |
| SWE.5 | 软件集成验证 | 集成验证措施与结果 |
| SWE.6 | 软件验证 | 软件验证措施与结果 |

## 执行流程与脚本调用时机

### 第 0 步：初始化工作空间（接收需求后立即执行）

收到用户需求后，**第一件事**是初始化工作空间，建立标准目录结构和文档模板：

```bash
python skills/SWE2_Skill_glm/scripts/workspace_initializer.py init <workspace> --project-name <项目名>
```

验证初始化结果：

```bash
python skills/SWE2_Skill_glm/scripts/workspace_initializer.py status <workspace>
```

### SWE.1–SWE.3：增量维护追溯矩阵

每完成一条需求/组件/单元定义后，**立即**追加追溯链接，不要等到阶段结束再批量写入：

```bash
# 示例：建立用户需求 → 软件需求的追溯
python skills/SWE2_Skill_glm/scripts/traceability_manager.py add <workspace> \
    --source UR-001 --target SWR-001 --type satisfies

# 示例：建立软件需求 → 架构组件的追溯
python skills/SWE2_Skill_glm/scripts/traceability_manager.py add <workspace> \
    --source SWR-001 --target SWC-SENSOR_HANDLER --type implements
```

每个阶段完成后验证追溯完整性：

```bash
python skills/SWE2_Skill_glm/scripts/traceability_manager.py validate <workspace>
```

### SWE.4–SWE.6：运行合规验证作为质量门

每个验证阶段的工作产品生成后，执行 ASPICE 合规验证。只有合规率达标才可宣告该阶段完成：

```bash
python skills/SWE2_Skill_glm/scripts/aspice_validator.py report <workspace> \
    --output <workspace>/aspice_validation_report.md
```

如需生成详细检查清单（适用于正式评审场景）：

```bash
python skills/SWE2_Skill_glm/scripts/aspice_validator.py checklist <workspace>
```

## 自主推进与审查边界

### 强制暂停点（不可跳过）

在以下两个切换点必须暂停，等待用户显式确认后才能继续：

**暂停点 1：SWE.2 完成后 → SWE.3 开始前**
> 原因：架构设计一旦进入详细设计和编码阶段即难以大幅回滚，架构决策需用户确认。
>
> 暂停提示格式：
> "架构设计已完成，共定义 N 个组件、M 个接口。请确认架构方向后，输入 '继续' 或 'yes' 以进入 SWE.3 详细设计与编码阶段。"

**暂停点 2：SWE.3 完成后 → SWE.4 开始前**
> 原因：代码已生成，进入验证阶段前需用户确认实现范围和测试策略。
>
> 暂停提示格式：
> "详细设计与代码生成已完成，共 N 个软件单元。请确认代码范围后，输入 '继续' 或 'yes' 以进入 SWE.4 单元验证阶段。"

### 可选暂停点（默认自动推进）

- SWE.1 完成后（默认跳过，用户可在启动时声明 "SWE.1 完成后暂停审查")
- SWE.5 完成后（默认跳过）

### 完全自主推进的阶段

SWE.1、SWE.4、SWE.5、SWE.6 阶段内部的所有子步骤，Claude 自主完成，不中断等待。

## 阶段完成报告格式

每个 SWE 阶段完成后，**必须**输出以下格式的报告，确保结构一致：

```
---
### ✅ [SWE.X] <阶段名称> - 完成报告

**产出文件**
| 文件名 | 状态 |
|--------|------|
| <ASPICE编号_文件名.ext> | 已生成 |

**追溯性状态**（SWE.1–SWE.3 适用）
- 新增追溯链接：X 条
- 当前矩阵总链接：Y 条
- 待关联项：[列举 ID 或"无"]

**合规验证**（SWE.4–SWE.6 适用）
- ASPICE 合规率：XX%
- 不合规项：[列举或"无"]

**下一步**
- 将进入 [SWE.X+1] <阶段名称>（或"全部阶段已完成"）
- 预计产出：<文件名列表>
- [如为强制暂停点] ⚠️ 请确认后继续

---
```

## 详细工作流指南

每个阶段的详细执行指南请参考：

- **SWE.1 软件需求分析**：详见 `references/swe1_requirements_analysis.md`
- **SWE.2 软件架构设计**：详见 `references/swe2_architecture_design.md`
- **SWE.3 详细设计与单元构建**：详见 `references/swe3_detailed_design.md`
- **SWE.4 软件单元验证**：详见 `references/swe4_unit_verification.md`
- **SWE.5 软件集成验证**：详见 `references/swe5_integration_verification.md`
- **SWE.6 软件验证**：详见 `references/swe6_software_verification.md`

## 产出目录结构

```
aspice_workspace/
├── 17-00_Software_Requirements_Specification.md
├── 04-04_Software_Architecture.md
├── 04-05_Software_Detailed_Design.md
├── 08-60_Unit_Verification_Measures.md
├── 08-60_Integration_Verification_Measures.md
├── 08-60_Software_Verification_Measures.md
├── 15-52_Unit_Verification_Results.md
├── 15-52_Integration_Verification_Results.md
├── 15-52_Software_Verification_Results.md
├── 13-51_Traceability_Matrix.csv
├── aspice_validation_report.md
├── config/
│   └── project.yaml
├── src/
│   └── [源代码文件]
└── tests/
    ├── unit/
    ├── integration/
    └── validation/
```

## 示例对话

> **用户**：使用 ASPICE SWE 流程开发我的项目，需求文档在 `./docs/prd.pdf`
>
> **助手**：已接收指令。
>
> **第 0 步**：初始化工作空间 `./aspice_workspace`...
> ```
> python scripts/workspace_initializer.py init ./aspice_workspace --project-name MyProject
> ```
> 工作空间初始化完成，目录结构已建立。
>
> **开始 SWE.1 软件需求分析**...
> 正在读取 `./docs/prd.pdf`，提取需求...
> 已识别 8 条功能需求（SWR-001~SWR-008），3 条非功能需求（SWR-009~SWR-011）。
> 生成 `17-00_Software_Requirements_Specification.md`，更新追溯矩阵 11 条链接。
>
> ---
> ### ✅ [SWE.1] 软件需求分析 - 完成报告
> **产出文件** | 17-00_Software_Requirements_Specification.md | 已生成
> **追溯性状态** | 新增 11 条 | 待关联项：无
> **下一步** | 将进入 [SWE.2] 软件架构设计
> ---
>
> **开始 SWE.2 软件架构设计**...
>
> ...（架构设计完成后）...
>
> ⚠️ 架构设计已完成，共定义 3 个组件（SWC-SENSOR_HANDLER、SWC-CONTROL_LOOP、SWC-COMM_MANAGER）、4 个接口。请确认架构方向后，输入"继续"以进入 SWE.3 详细设计与编码阶段。

## ASPICE 过程能力等级参考

| 等级 | 描述 | 关键特征 |
|------|------|----------|
| Level 0 | 不完整 | 过程未实施或实施失败 |
| Level 1 | 已执行 | 过程已执行并达到输出目标 |
| Level 2 | 已管理 | 过程已规划、监控和调整 |
| Level 3 | 已建立 | 过程已标准化并持续改进 |

本 skill 默认以 **Level 2（已管理）** 为目标进行过程实施。
