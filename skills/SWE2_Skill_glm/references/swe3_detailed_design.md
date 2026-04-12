# SWE.3 软件详细设计与单元构建 - 详细工作流指南

## 过程目的

SWE.3 的目的是为软件组件开发详细设计，并将软件单元定义为可实现的要素。详细设计应提供足够的细节，使开发人员能够实现软件单元，并支持单元验证活动。

## 输入要求

| 输入项 | 来源 | 说明 |
|--------|------|------|
| 软件架构设计 | SWE.2 | 组件定义和接口规范 |
| 软件需求规格 | SWE.1 | 功能和非功能需求 |
| 编码规范 | 项目定义 | 代码风格、命名规范等 |

## 执行步骤

### Step 1: 组件分解

1. **将组件分解为软件单元**
   ```
   单元命名规范：
   - 文件名：snake_case.c / snake_case.h
   - 函数名：ComponentName_FunctionName
   - 单元ID：SU-XXX
   
   示例：
   - SWC-SENSOR_HANDLER 分解为：
     - SU-001: SensorHandler_Init()
     - SU-002: SensorHandler_ReadValue()
     - SU-003: SensorHandler_ConvertToPhysical()
   ```

2. **单元粒度原则**
   | 原则 | 说明 |
   |------|------|
   | 原子性 | 一个单元只做一件事 |
   | 可测试性 | 单元可独立测试 |
   | 内聚性 | 单元内部高度相关 |
   | 低耦合 | 单元之间依赖最小化 |

### Step 2: 详细设计规范

1. **单元设计模板**
   ```markdown
   ## 软件单元: SU-XXX
   
   ### 基本信息
   | 属性 | 值 |
   |------|-----|
   | 单元ID | SU-001 |
   | 单元名称 | SensorHandler_ReadValue |
   | 所属组件 | SWC-SENSOR_HANDLER |
   | 文件位置 | src/sensor_handler.c |
   | 语言 | C (C99) |
   
   ### 功能描述
   [详细描述单元的功能]
   
   ### 接口定义
   #### 函数原型
   ```c
   Std_ReturnType SensorHandler_ReadValue(
       Sensor_ChannelType channel,
       float* value
   );
   ```
   
   #### 参数说明
   | 参数 | 方向 | 类型 | 范围 | 单位 | 描述 |
   |------|------|------|------|------|------|
   | channel | IN | Sensor_ChannelType | 0-15 | - | 传感器通道号 |
   | value | OUT | float* | 0.0-5.0 | V | 传感器电压值 |
   
   #### 返回值
   | 值 | 含义 |
   |-----|------|
   | E_OK | 读取成功 |
   | E_NOT_OK | 读取失败 |
   
   ### 算法描述
   [使用伪代码或流程图描述]
   
   ### 数据流
   [描述输入到输出的转换过程]
   
   ### 错误处理
   | 错误条件 | 处理方式 |
   |----------|----------|
   | 通道号无效 | 返回 E_NOT_OK |
   | 指针为空 | 返回 E_NOT_OK |
   
   ### 资源需求
   | 资源 | 需求 |
   |------|------|
   | 栈空间 | 32 bytes |
   | 执行时间 | < 100 μs |
   ```

2. **数据结构设计**
   ```markdown
   ## 数据结构: SensorConfigType
   
   ```c
   typedef struct {
       uint8_t channel;       /* 通道号: 0-15 */
       uint8_t resolution;    /* 分辨率: 10/12 bit */
       float referenceVoltage;/* 参考电压: V */
       float offset;          /* 偏移校准值: V */
   } SensorConfigType;
   ```
   
   | 字段 | 类型 | 范围 | 单位 | 描述 |
   |------|------|------|------|------|
   | channel | uint8_t | 0-15 | - | ADC通道号 |
   | resolution | uint8_t | 10,12 | bit | ADC分辨率 |
   | referenceVoltage | float | 0.0-5.5 | V | 参考电压 |
   | offset | float | -1.0-1.0 | V | 校准偏移值 |
   ```

### Step 3: 算法设计

1. **算法描述方式**
   - 伪代码描述
   - 流程图/状态图
   - 数学公式
   - 表格/决策表

2. **算法设计示例**
   ```markdown
   ## 算法: 传感器值到物理值转换
   
   ### 数学模型
   物理值 = (电压值 - 偏移量) × 增益
   
   其中:
   - 电压值: ADC读取值转换后的电压
   - 偏移量: 传感器零点偏移
   - 增益: 单位转换系数
   
   ### 伪代码
   ```
   function ConvertToPhysical(voltage, offset, gain):
       if voltage < MIN_VOLTAGE or voltage > MAX_VOLTAGE:
           return ERROR_OUT_OF_RANGE
       end if
       
       physical = (voltage - offset) * gain
       
       if physical < MIN_PHYSICAL:
           physical = MIN_PHYSICAL
       else if physical > MAX_PHYSICAL:
           physical = MAX_PHYSICAL
       end if
       
       return physical
   end function
   ```
   
   ### 边界条件
   | 条件 | 输入 | 预期输出 |
   |------|------|----------|
   | 最小电压 | 0.0V | MIN_PHYSICAL |
   | 最大电压 | 5.0V | MAX_PHYSICAL |
   | 超量程 | 5.5V | ERROR |
   ```

### Step 4: 源代码实现

1. **目录结构**
   ```
   src/
   ├── include/
   │   ├── sensor_handler.h
   │   ├── control_loop.h
   │   └── comm_manager.h
   ├── sensor_handler.c
   ├── control_loop.c
   └── comm_manager.c
   ```

2. **代码规范示例**
   ```c
   /**
    * @file    sensor_handler.c
    * @brief   传感器处理模块实现
    * @details 实现传感器数据采集、转换和滤波功能
    * 
    * @version 1.0
    * @date    YYYY-MM-DD
    * @author  [Author]
    */
   
   /* 标准头文件 */
   #include <stdint.h>
   #include <stdbool.h>
   
   /* 模块头文件 */
   #include "sensor_handler.h"
   
   /* 私有宏定义 */
   #define SENSOR_MIN_VOLTAGE   (0.0f)
   #define SENSOR_MAX_VOLTAGE   (5.0f)
   
   /* 私有类型定义 */
   
   /* 私有变量 */
   
   /* 私有函数声明 */
   
   /* 公有函数实现 */
   
   /**
    * @brief   初始化传感器处理模块
    * @return  E_OK: 成功, E_NOT_OK: 失败
    */
   Std_ReturnType SensorHandler_Init(void)
   {
       /* 实现代码 */
   }
   
   /* 私有函数实现 */
   ```

### Step 5: 生成工作产品

**产出文件**: `04-05_Software_Detailed_Design.md`

**文件结构**:
```markdown
# 软件详细设计文档

## 文档信息
| 项目 | 内容 |
|------|------|
| 文档编号 | 04-05 |
| 版本 | 1.0 |
| 创建日期 | YYYY-MM-DD |

## 1. 引言
### 1.1 目的与范围
### 1.2 参考文档

## 2. 设计概述
### 2.1 设计原则
### 2.2 编码规范

## 3. 组件详细设计
### 3.1 [SWC-SENSOR_HANDLER]
#### 3.1.1 单元清单
#### 3.1.2 单元详细设计
### 3.2 [SWC-CONTROL_LOOP]
...

## 4. 数据结构设计
### 4.1 全局数据结构
### 4.2 类型定义

## 5. 文件结构
### 5.1 头文件组织
### 5.2 源文件组织

## 6. 可追溯性
[引用 13-51_Traceability_Matrix.csv]
```

### Step 6: 更新追溯性矩阵

**更新内容**:
```csv
Arch_Component_ID,Detailed_Design_ID,Unit_ID,Unit_File,Notes
SWC-SENSOR_HANDLER,DD-001,SU-001,sensor_handler.c:SensorHandler_Init,初始化单元
SWC-SENSOR_HANDLER,DD-002,SU-002,sensor_handler.c:SensorHandler_ReadValue,读取单元
```

### Step 7: 自检验证

**检查清单**:
- [ ] 所有架构组件是否都已分解为单元？
- [ ] 每个单元是否有详细的接口规范？
- [ ] 输入/输出范围和单位是否明确？
- [ ] 算法是否清晰可理解？
- [ ] 源代码是否遵循编码规范？
- [ ] 可追溯性是否完整？

## 过程输出

| 输出项 | 文件名/目录 | 说明 |
|--------|-------------|------|
| 详细设计文档 | 04-05_Software_Detailed_Design.md | 详细设计规范 |
| 源代码文件 | src/*.c, src/include/*.h | 实现代码 |
| 可追溯性矩阵 | 13-51_Traceability_Matrix.csv | 更新单元追溯 |

## 编码规范要点

### MISRA-C 关键规则示例

| 规则类别 | 规则示例 | 说明 |
|----------|----------|------|
| 必要规则 | Rule 17.7 | 函数返回值必须使用 |
| 必要规则 | Rule 21.1 | 不得使用标准库保留标识符 |
| 必要规则 | Rule 10.1 | 隐式整型转换需谨慎 |
| 建议规则 | Rule 8.13 | 指针参数应尽可能使用 const |

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件 | snake_case | sensor_handler.c |
| 函数 | Component_Function | SensorHandler_Init |
| 变量 | camelCase | sensorValue |
| 常量 | UPPER_CASE | MAX_SENSOR_COUNT |
| 类型 | PascalType | SensorConfigType |

## 进入下一阶段的条件

- [ ] 详细设计文档已完成
- [ ] 源代码已实现
- [ ] 代码静态检查通过
- [ ] 可追溯性矩阵已更新
- [ ] 自检通过或用户确认
