# SWE.4 软件单元验证 - 详细工作流指南

## 过程目的

SWE.4 的目的是验证软件单元是否符合详细设计，并提供证据证明软件单元满足其规范要求。单元验证包括静态分析和单元测试。

## 输入要求

| 输入项 | 来源 | 说明 |
|--------|------|------|
| 详细设计文档 | SWE.3 | 单元接口规范和算法描述 |
| 源代码 | SWE.3 | 软件单元实现 |
| 验证策略 | 项目定义 | 验证方法、覆盖率要求等 |

## 执行步骤

### Step 1: 制定验证策略

1. **验证方法选择**
   | 方法 | 适用场景 | 产出 |
   |------|----------|------|
   | 静态分析 | 所有代码 | 代码质量报告 |
   | 代码评审 | 关键代码 | 评审记录 |
   | 单元测试 | 功能逻辑 | 测试用例和结果 |
   | 形式化验证 | 安全关键 | 验证报告 |

2. **覆盖率目标**
   | 覆盖类型 | 描述 | ASPICE要求 |
   |----------|------|------------|
   | 语句覆盖 | 每条语句至少执行一次 | 100% |
   | 分支覆盖 | 每个分支至少执行一次 | 100% |
   | MC/DC覆盖 | 条件独立影响结果 | 安全相关100% |

### Step 2: 静态分析

1. **静态分析工具配置**
   ```json
   {
     "tool": "Cppcheck",
     "version": "2.7",
     "standards": ["MISRA-C:2012"],
     "checks": {
       "style": true,
       "performance": true,
       "portability": true,
       "unusedFunctions": true,
       "missingInclude": true
     }
   }
   ```

2. **分析执行命令**
   ```bash
   # Cppcheck 静态分析
   cppcheck --enable=all --std=c99 \
            --force --inline-suppr \
            --addon=misra.json \
            src/ --output-file=static_analysis_report.txt
   ```

3. **分析结果分类**
   | 级别 | 描述 | 处理要求 |
   |------|------|----------|
   | error | 确定的错误 | 必须修复 |
   | warning | 可能的问题 | 需要分析 |
   | style | 代码风格问题 | 建议修复 |
   | information | 信息提示 | 可选处理 |
   | portability | 移植性问题 | 建议修复 |

### Step 3: 单元测试设计

1. **测试用例设计方法**
   | 方法 | 描述 | 适用场景 |
   |------|------|----------|
   | 等价类划分 | 将输入域分为等价类 | 输入范围验证 |
   | 边界值分析 | 测试边界条件 | 数值边界 |
   | 决策表 | 组合条件测试 | 复杂逻辑 |
   | 状态转换 | 状态机测试 | 有状态单元 |
   | 错误推测 | 基于经验推测 | 经验补充 |

2. **测试用例模板**
   ```markdown
   ## 测试用例: UT-SU001-001
   
   ### 基本信息
   | 属性 | 值 |
   |------|-----|
   | 测试ID | UT-SU001-001 |
   | 被测单元 | SU-001: SensorHandler_ReadValue |
   | 测试类型 | 功能测试 |
   | 设计方法 | 边界值分析 |
   
   ### 测试描述
   验证在有效通道号输入时，能正确读取传感器值
   
   ### 前置条件
   - 传感器模块已初始化
   - ADC通道0已配置
   
   ### 测试步骤
   | 步骤 | 操作 | 预期结果 |
   |------|------|----------|
   | 1 | 调用 SensorHandler_ReadValue(0, &value) | 返回 E_OK |
   | 2 | 检查 value 值 | 0.0 <= value <= 5.0 |
   
   ### 测试数据
   | 输入 | 值 |
   |------|-----|
   | channel | 0 |
   
   | 预期输出 | 值 |
   |----------|-----|
   | 返回值 | E_OK |
   | value | 有效的传感器值 |
   
   ### 覆盖目标
   - 语句覆盖: 行 10, 11, 12
   - 分支覆盖: 分支 B1 (TRUE)
   ```

3. **测试用例清单**
   ```markdown
   ## 单元测试用例清单
   
   | 测试ID | 被测单元 | 测试类型 | 描述 | 状态 |
   |--------|----------|----------|------|------|
   | UT-SU001-001 | SensorHandler_ReadValue | 正常功能 | 有效通道读取 | PASS |
   | UT-SU001-002 | SensorHandler_ReadValue | 异常处理 | 无效通道号 | PASS |
   | UT-SU001-003 | SensorHandler_ReadValue | 异常处理 | 空指针参数 | PASS |
   | UT-SU001-004 | SensorHandler_ReadValue | 边界值 | 最小通道号 | PASS |
   | UT-SU001-005 | SensorHandler_ReadValue | 边界值 | 最大通道号 | PASS |
   ```

### Step 4: 测试代码实现

1. **测试框架选择**
   | 框架 | 语言 | 特点 |
   |------|------|------|
   | Unity | C | 轻量级，适合嵌入式 |
   | CppUTest | C/C++ | 功能丰富，支持Mock |
   | Google Test | C++ | 功能强大，广泛使用 |

2. **测试代码示例**
   ```c
   /* test_unit_sensor_handler.c */
   
   #include "unity.h"
   #include "sensor_handler.h"
   
   /* 测试夹具 */
   void setUp(void) {
       /* 每个测试前的初始化 */
       SensorHandler_Init();
   }
   
   void tearDown(void) {
       /* 每个测试后的清理 */
   }
   
   /* 测试用例实现 */
   void test_ReadValue_ValidChannel_ReturnsOk(void) {
       /* Given */
       float value;
       uint8_t channel = 0;
       
       /* When */
       Std_ReturnType result = SensorHandler_ReadValue(channel, &value);
       
       /* Then */
       TEST_ASSERT_EQUAL(E_OK, result);
       TEST_ASSERT_FLOAT_WITHIN(5.0f, 0.0f, value);
   }
   
   void test_ReadValue_InvalidChannel_ReturnsNotOk(void) {
       /* Given */
       float value;
       uint8_t channel = 255; /* 无效通道 */
       
       /* When */
       Std_ReturnType result = SensorHandler_ReadValue(channel, &value);
       
       /* Then */
       TEST_ASSERT_EQUAL(E_NOT_OK, result);
   }
   
   void test_ReadValue_NullPointer_ReturnsNotOk(void) {
       /* Given */
       uint8_t channel = 0;
       
       /* When */
       Std_ReturnType result = SensorHandler_ReadValue(channel, NULL);
       
       /* Then */
       TEST_ASSERT_EQUAL(E_NOT_OK, result);
   }
   
   /* 测试运行器 */
   int main(void) {
       UNITY_BEGIN();
       RUN_TEST(test_ReadValue_ValidChannel_ReturnsOk);
       RUN_TEST(test_ReadValue_InvalidChannel_ReturnsNotOk);
       RUN_TEST(test_ReadValue_NullPointer_ReturnsNotOk);
       return UNITY_END();
   }
   ```

### Step 5: 测试执行与结果记录

1. **测试执行命令**
   ```bash
   # 编译测试代码
   gcc -I src/include -I tests/unity \
       tests/unit/test_sensor_handler.c \
       src/sensor_handler.c \
       tests/unity/unity.c \
       -o test_sensor_handler
   
   # 执行测试
   ./test_sensor_handler
   ```

2. **测试结果记录**
   ```markdown
   ## 单元测试结果: SensorHandler_ReadValue
   
   ### 执行摘要
   | 项目 | 值 |
   |------|-----|
   | 执行时间 | 2024-01-15 10:30:00 |
   | 总用例数 | 5 |
   | 通过数 | 5 |
   | 失败数 | 0 |
   | 通过率 | 100% |
   
   ### 详细结果
   | 测试ID | 结果 | 执行时间 | 备注 |
   |--------|------|----------|------|
   | UT-SU001-001 | PASS | 0.001s | - |
   | UT-SU001-002 | PASS | 0.001s | - |
   | UT-SU001-003 | PASS | 0.001s | - |
   | UT-SU001-004 | PASS | 0.001s | - |
   | UT-SU001-005 | PASS | 0.001s | - |
   
   ### 覆盖率报告
   | 覆盖类型 | 目标 | 实际 | 状态 |
   |----------|------|------|------|
   | 语句覆盖 | 100% | 100% | PASS |
   | 分支覆盖 | 100% | 100% | PASS |
   ```

### Step 6: 生成工作产品

**产出文件**: `08-60_Unit_Verification_Measures.md`

```markdown
# 软件单元验证措施

## 文档信息
| 项目 | 内容 |
|------|------|
| 文档编号 | 08-60 |
| 版本 | 1.0 |
| 创建日期 | YYYY-MM-DD |

## 1. 验证策略
### 1.1 验证方法
### 1.2 覆盖率要求
### 1.3 工具选择

## 2. 静态分析措施
### 2.1 分析工具配置
### 2.2 分析规则集
### 2.3 结果评价标准

## 3. 单元测试措施
### 3.1 测试框架
### 3.2 测试用例设计
### 3.3 Mock/Stub策略

## 4. 验证措施清单
| 措施ID | 类型 | 描述 | 关联单元 |
|--------|------|------|----------|
| VM-001 | 静态分析 | MISRA-C检查 | SU-001 |
| VM-002 | 单元测试 | 功能验证 | SU-001 |
```

**产出文件**: `15-52_Unit_Verification_Results.md`

```markdown
# 软件单元验证结果

## 文档信息
| 项目 | 内容 |
|------|------|
| 文档编号 | 15-52 |
| 版本 | 1.0 |
| 创建日期 | YYYY-MM-DD |

## 1. 静态分析结果
### 1.1 分析工具信息
### 1.2 分析结果摘要
### 1.3 问题清单与处理

## 2. 单元测试结果
### 2.1 执行摘要
### 2.2 详细结果
### 2.3 覆盖率报告

## 3. 验证结论
### 3.1 总体评价
### 3.2 遗留问题
### 3.3 后续行动
```

### Step 7: 更新追溯性矩阵

**更新内容**:
```csv
Unit_ID,Verification_Measure_ID,Verification_Result_ID,Result,Notes
SU-001,VM-001,VR-001,PASS,静态分析通过
SU-001,VM-002,VR-002,PASS,单元测试通过
SU-002,VM-003,VR-003,PASS,静态分析通过
SU-002,VM-004,VR-004,PASS,单元测试通过
```

### Step 8: 自检验证

**检查清单**:
- [ ] 每个软件单元是否都有验证措施？
- [ ] 静态分析是否完成？
- [ ] 单元测试覆盖率是否达标？
- [ ] 所有测试用例是否通过？
- [ ] 验证结果是否记录完整？
- [ ] 可追溯性是否完整？

## 过程输出

| 输出项 | 文件名/目录 | 说明 |
|--------|-------------|------|
| 验证措施文档 | 08-60_Unit_Verification_Measures.md | 验证策略和措施 |
| 验证结果文档 | 15-52_Unit_Verification_Results.md | 验证结果记录 |
| 测试代码 | tests/unit/*.c | 单元测试代码 |
| 可追溯性矩阵 | 13-51_Traceability_Matrix.csv | 更新验证追溯 |

## 缺陷管理

### 缺陷分类

| 级别 | 描述 | 处理时限 |
|------|------|----------|
| Critical | 导致系统崩溃或安全风险 | 立即修复 |
| Major | 功能缺陷或性能问题 | 当前迭代修复 |
| Minor | 小问题或改进建议 | 后续版本修复 |

### 缺陷记录模板

| 字段 | 说明 |
|------|------|
| 缺陷ID | DEF-XXX |
| 发现阶段 | SWE.4 单元验证 |
| 关联单元 | SU-XXX |
| 严重程度 | Critical/Major/Minor |
| 描述 | 问题详细描述 |
| 复现步骤 | 如何复现该问题 |
| 状态 | Open/Fixed/Verified/Closed |
| 修复日期 | YYYY-MM-DD |
| 验证日期 | YYYY-MM-DD |

## 进入下一阶段的条件

- [ ] 静态分析完成且无严重问题
- [ ] 所有单元测试通过
- [ ] 覆盖率达标
- [ ] 验证文档完成
- [ ] 可追溯性矩阵更新
- [ ] 自检通过或用户确认
