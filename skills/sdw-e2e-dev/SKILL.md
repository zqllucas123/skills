---
name: sdw-e2e-dev
description: 端到端实现汽车软件 PRD 功能模块，遵循 ASPICE 过程并复用参考 base 项目能力。用于用户提到"参照 base 项目实现 PRD"、"按 ASPICE 流程开发功能模块"、"分模块实现并预编译修复"时。要求先做中国汽车法规与功能安全评估，再按 ASPICE SWE.1-SWE.6 完成设计实现、预编译、日志修复与交付文档。
---

# SDW E2E Development

## 目标

基于用户提供的 PRD 文档和参考 base 项目，从 0 到 1 分模块完成需求实现，过程符合 ASPICE 规范，并输出可审计的分析、设计、测试与合规文档。

## 输入

- PRD 文档（路径或文本，支持单个或多个文档）
- 参考 base 项目路径
- 当前目标项目路径
- 可选：编译服务配置来源（默认读取本机配置文件）

## 参考资料读取策略

在执行对应阶段时，按需读取以下参考文件：

- `references/自动驾驶系统安全要求.pdf`
  - 在"功能安全分析"阶段必须读取
  - 用于安全条款对照、风险识别、控制措施与结论依据
- `references/compile_guide.md`
  - 在"预编译与自动修复闭环"阶段必须读取
  - 用于端口映射、编译接口调用和日志处理步骤

仅在相关步骤读取对应参考文件，避免无关上下文干扰。

## 标准输出

每个功能模块完成后至少产出以下内容（Markdown）：

- `compliance/<module>_regulation_analysis.md`：法规合规分析文档
- `safety/<module>_functional_safety_analysis.md`：功能安全分析文档
- `design/<module>_detailed_design.md`：功能详细设计文档
- `tests/<module>_test_cases.md`：测试用例文档
- `build/<module>_compile_report.md`：预编译与修复记录文档

此外，每个模块结束时必须在回复中追加一个统一的"模块完成报告"，用于自动评测判定，格式如下（字段名必须原样保留）：

```markdown
## MODULE_DELIVERY_REPORT
- MODULE_NAME: <模块名>
- LEGAL_RESULT: <通过|有风险|不通过>
- SAFETY_RESULT: <可接受|需整改|不可接受>
- ASPICE_STAGES: <SWE.1,SWE.2,SWE.3,...>
- BASE_REUSE: <none|partial|full>
- BASE_CODE_MODIFIED: <no|yes>
- COMPILE_STATUS: <pass|blocked>
- COMPILE_RETRY_COUNT: <整数>
- REFERENCES_USED: <逗号分隔路径>
- SENSITIVE_DATA_CHECK: <pass|fail>
```

## 执行流程

按 PRD 中的功能模块逐个执行，禁止跳步。

### 1) 分析 PRD 并拆分模块

- 识别 PRD 中的功能模块、接口、输入输出、约束和验收标准
- 按模块建立任务清单，逐个实现，不并行混改

### 2) 法律法规分析（先于开发）

- 对每个模块做中国汽车软件相关法规合规评估
- 产出明确结论：`通过 / 有风险 / 不通过`
- 若不通过，先给出整改建议，不进入编码

### 3) 功能安全分析（法规通过后）

- 对模块进行功能安全影响分析（危害、失效模式、风险等级、缓解措施）
- 必须基于 `references/自动驾驶系统安全要求.pdf` 给出条款映射与结论依据
- 形成可追溯的安全结论与开发约束
- 若风险不可接受，先调整方案再实现

### 4) 按 ASPICE SWE.1–SWE.6 流程实现

#### ASPICE 核心执行准则

- **双向追溯**：每条需求必须关联上层需求；每个设计元素必须关联需求；每项验证必须关联验证对象
- **原子化单元**：软件单元定义为不可再分的逻辑要素（如单一函数）
- **验证多样性**：静态分析、代码评审、单元测试、集成测试、功能测试
- **命名规范**：文件名包含 ASPICE 标准编号前缀（如 `17-00_Software_Requirements_Specification.md`）

#### 阶段概览

| 阶段 | 过程 | 主要产出 |
|------|------|----------|
| SWE.1 | 软件需求分析 | 软件需求规格说明书 |
| SWE.2 | 软件架构设计 | 软件架构文档 |
| SWE.3 | 详细设计与单元构建 | 详细设计文档 + 源代码 |
| SWE.4 | 软件单元验证 | 单元验证措施与结果 |
| SWE.5 | 软件集成验证 | 集成验证措施与结果 |
| SWE.6 | 软件验证 | 软件验证措施与结果 |

#### 第 0 步：初始化工作空间（接收需求后立即执行）

```bash
python scripts/workspace_initializer.py init <workspace> --project-name <项目名>
python scripts/workspace_initializer.py status <workspace>
```

#### SWE.1–SWE.3：增量维护追溯矩阵

每完成一条需求/组件/单元定义后，**立即**追加追溯链接：

```bash
python scripts/traceability_manager.py add <workspace> \
    --source UR-001 --target SWR-001 --type satisfies

python scripts/traceability_manager.py validate <workspace>
```

详细执行指南：
- SWE.1：`references/swe1_requirements_analysis.md`
- SWE.2：`references/swe2_architecture_design.md`
- SWE.3：`references/swe3_detailed_design.md`

#### SWE.4–SWE.6：合规验证作为质量门

每个验证阶段产品生成后，执行 ASPICE 合规验证，合规率达标后方可宣告该阶段完成：

```bash
python scripts/aspice_validator.py report <workspace> \
    --output <workspace>/aspice_validation_report.md
```

详细执行指南：
- SWE.4：`references/swe4_unit_verification.md`
- SWE.5：`references/swe5_integration_verification.md`
- SWE.6：`references/swe6_software_verification.md`

#### 强制暂停点（不可跳过）

**暂停点 1：SWE.2 完成后 → SWE.3 开始前**
> 架构决策需用户确认，进入详细设计/编码后难以大幅回滚。
> 暂停提示："架构设计已完成，共定义 N 个组件、M 个接口。请确认架构方向后，输入'继续'以进入 SWE.3。"

**暂停点 2：SWE.3 完成后 → SWE.4 开始前**
> 代码生成后，进入验证前需确认实现范围和测试策略。
> 暂停提示："详细设计与代码生成已完成，共 N 个软件单元。请确认代码范围后，输入'继续'以进入 SWE.4。"

#### 阶段完成报告格式

每个 SWE 阶段完成后必须输出：

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
- 将进入 [SWE.X+1] 或"全部阶段已完成"
- [如为强制暂停点] ⚠️ 请确认后继续

---
```

#### 参考文本片段定位要求

对所有 ASPICE 设计成果物（至少 `design/<module>_detailed_design.md`），必须补充"参考文本片段定位"：

- **原文片段**：摘录所依据的关键原文内容
- **来源文件路径**：明确来自哪份 PRD/文档
- **定位信息**：章节编号 / 段落 / 页码 / 行号等可用粒度

示例格式：

```markdown
> 参考来源：`./docs/prd_parking_assist.md` § 3.2 车位识别需求，第 12 行
> 原文："系统应在 500ms 内完成单次车位检测并输出坐标"
```

### 5) 参考 base 项目复用策略

- 先判断参考 base 项目中是否已存在同类能力
- 若存在且满足法规与安全评估结论，可复制对应代码与依赖到当前项目
- 非必要情况下，不改动已复用依赖逻辑；若必须修改，需记录原因、影响面和回滚方案

### 6) 预编译与自动修复闭环

- 每个模块编码完成后立即预编译
- 编译失败时，读取并解析编译日志，自动修复后再次编译
- 循环执行，直至编译成功或达到失败上限并给出阻塞说明
- 预编译流程细节按 `references/compile_guide.md` 执行

预编译调用规范：

- 先读取 `/Users/lucaszhou/.sdw/prj/projects.json` 中与当前项目匹配的 `deploy_config`
- 所有连接参数、认证信息、目标路径均从配置读取，禁止在对话和文档中硬编码敏感信息
- 通过本地编译服务接口提交编译请求（例如 `http://127.0.0.1:18000/compile`）
- 将返回日志写入 `build/<module>_compile_report.md`，记录每轮失败原因与修复动作

## 约束

- 不得修改参考 base 项目源码
- 编译失败必须基于返回日志修复，不允许跳过
- 不得输出或硬编码账号、密码、令牌等敏感信息
- 若法规或功能安全评估未通过，不得进入实现阶段

## 交付检查清单

在回复用户"模块完成"前，必须满足：

- [ ] 该模块法规分析已完成且结论可追溯
- [ ] 该模块功能安全分析已完成且风险可接受
- [ ] 已按 ASPICE SWE.1–SWE.6 完成分析、设计、编码和验证
- [ ] 设计成果物已附"参考文本片段定位"（原文片段 + 来源路径 + 定位信息）
- [ ] 预编译成功，或已输出可复现的阻塞说明
- [ ] 5 类文档（合规/安全/设计/测试/编译）已更新

## 示例

### 示例 1

**输入**

- PRD：`./docs/prd_parking_assist.md`
- base 项目：`/repo/base_autodrive`
- 目标项目：`/repo/current_project`
- 请求：参照 base 项目按 ASPICE 实现 PRD 中各模块

**期望输出**

- 拆分出模块（例如：车位识别、轨迹规划、泊车控制）
- 每个模块先输出法规与功能安全分析
- 按 ASPICE SWE.1–SWE.6 流程完成实现与测试，每个设计产物附参考文本片段定位
- 每模块完成后输出预编译日志与修复记录，最终通过编译
- 产出对应 Markdown 文档集合

### 示例 2

**输入**

- PRD 文本：包含"障碍物融合感知模块"新增需求
- base 项目：`/knowledge/base_perception`
- 请求：先做合规和安全评估，通过后实现并提交详细设计和测试用例

**期望输出**

- 给出法规与功能安全评估结论与风险项
- 若通过，则复用 base 中可用能力并实现差异部分
- 输出详细设计文档（含参考文本片段定位）、测试用例文档与编译报告
- 编译失败时自动修复并重试，直到通过
