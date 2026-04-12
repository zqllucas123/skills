#!/usr/bin/env python3
"""
ASPICE SWE 工作空间初始化工具

功能：
- 创建符合ASPICE规范的工作空间目录结构
- 生成初始文档模板
- 初始化追溯性矩阵

使用方法：
    python workspace_initializer.py init <workspace> [--project-name <name>]
    python workspace_initializer.py status <workspace>
"""

import argparse
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional


class WorkspaceInitializer:
    """工作空间初始化器"""
    
    # ASPICE 标准目录结构
    DIRECTORY_STRUCTURE = {
        "docs": "文档目录",
        "src": "源代码目录",
        "src/include": "头文件目录",
        "tests": "测试目录",
        "tests/unit": "单元测试目录",
        "tests/integration": "集成测试目录",
        "tests/validation": "验证测试目录",
        "reports": "报告目录",
        "config": "配置目录"
    }
    
    # ASPICE 标准工作产品
    WORK_PRODUCTS = {
        "17-00_Software_Requirements_Specification.md": "软件需求规格说明书",
        "04-04_Software_Architecture.md": "软件架构设计文档",
        "04-05_Software_Detailed_Design.md": "软件详细设计文档",
        "08-60_Unit_Verification_Measures.md": "单元验证措施",
        "08-60_Integration_Verification_Measures.md": "集成验证措施",
        "08-60_Software_Verification_Measures.md": "软件验证措施",
        "15-52_Unit_Verification_Results.md": "单元验证结果",
        "15-52_Integration_Verification_Results.md": "集成验证结果",
        "15-52_Software_Verification_Results.md": "软件验证结果",
        "13-51_Traceability_Matrix.csv": "追溯性矩阵"
    }
    
    def __init__(self, workspace: str, project_name: str = "ASPICE_SW_Project"):
        self.workspace = workspace
        self.project_name = project_name
    
    def init_workspace(self) -> None:
        """初始化工作空间"""
        print(f"正在初始化工作空间: {self.workspace}")
        print(f"项目名称: {self.project_name}")
        print("-" * 50)
        
        # 创建目录结构
        self._create_directories()
        
        # 创建工作产品模板
        self._create_work_product_templates()
        
        # 创建追溯性矩阵
        self._create_traceability_matrix()
        
        # 创建项目配置文件
        self._create_project_config()
        
        print("-" * 50)
        print("工作空间初始化完成！")
    
    def _create_directories(self) -> None:
        """创建目录结构"""
        print("\n创建目录结构...")
        
        for dir_path, description in self.DIRECTORY_STRUCTURE.items():
            full_path = os.path.join(self.workspace, dir_path)
            os.makedirs(full_path, exist_ok=True)
            print(f"  创建: {dir_path}/ ({description})")
    
    def _create_work_product_templates(self) -> None:
        """创建工作产品模板"""
        print("\n创建工作产品模板...")
        
        templates = self._get_templates()
        
        for filename, description in self.WORK_PRODUCTS.items():
            filepath = os.path.join(self.workspace, filename)
            
            if os.path.exists(filepath):
                print(f"  跳过: {filename} (已存在)")
                continue
            
            template = templates.get(filename, self._get_default_template(filename, description))
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template)
            
            print(f"  创建: {filename} ({description})")
    
    def _get_templates(self) -> Dict[str, str]:
        """获取文档模板"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        return {
            "17-00_Software_Requirements_Specification.md": f"""# 软件需求规格说明书

## 文档信息
| 项目 | 内容 |
|------|------|
| 文档编号 | 17-00 |
| 项目名称 | {self.project_name} |
| 版本 | 1.0 |
| 创建日期 | {current_date} |
| 状态 | 草稿 |

## 1. 引言
### 1.1 目的
[描述本文档的目的]

### 1.2 范围
[描述本文档的范围]

### 1.3 定义与缩略语
| 术语 | 定义 |
|------|------|
| ... | ... |

## 2. 总体描述
### 2.1 产品视角
[描述产品在系统中的位置]

### 2.2 用户特征
[描述目标用户群体]

### 2.3 约束条件
[描述设计约束]

## 3. 功能需求
| ID | 标题 | 描述 | 优先级 | 验收标准 |
|----|------|------|--------|----------|
| SWR-001 | [需求名称] | [需求描述] | 高 | [验收条件] |

## 4. 非功能需求
### 4.1 性能需求
[性能要求描述]

### 4.2 安全需求
[安全要求描述]

### 4.3 可靠性需求
[可靠性要求描述]

## 5. 接口需求
### 5.1 用户接口
[用户界面要求]

### 5.2 硬件接口
[硬件接口要求]

### 5.3 软件接口
[软件接口要求]

## 6. 可追溯性
[引用 13-51_Traceability_Matrix.csv]
""",
            
            "04-04_Software_Architecture.md": f"""# 软件架构设计文档

## 文档信息
| 项目 | 内容 |
|------|------|
| 文档编号 | 04-04 |
| 项目名称 | {self.project_name} |
| 版本 | 1.0 |
| 创建日期 | {current_date} |
| 状态 | 草稿 |

## 1. 引言
### 1.1 目的与范围
[描述本文档的目的和范围]

### 1.2 参考文档
- 17-00_Software_Requirements_Specification.md

## 2. 架构概述
### 2.1 架构目标
[描述架构的主要目标]

### 2.2 架构决策
| 决策ID | 决策内容 | 原因 | 替代方案 |
|--------|----------|------|----------|
| AD-001 | ... | ... | ... |

### 2.3 设计约束
[描述设计约束条件]

## 3. 架构视图
### 3.1 静态视图
[组件图描述]

### 3.2 动态视图
[时序图描述]

### 3.3 部署视图
[部署图描述]

## 4. 组件定义
### 4.1 组件清单
| 组件ID | 组件名称 | 职责描述 | 关联需求 |
|--------|----------|----------|----------|
| SWC-001 | ... | ... | SWR-XXX |

### 4.2 组件详细描述
[各组件的详细描述]

## 5. 接口定义
### 5.1 接口清单
| 接口ID | 接口名称 | 类型 | 提供者 | 消费者 |
|--------|----------|------|--------|--------|
| IF-001 | ... | ... | SWC-XXX | SWC-YYY |

### 5.2 接口详细规范
[各接口的详细规范]

## 6. 资源分析
### 6.1 内存分配
[内存使用估算]

### 6.2 CPU 负载预估
[CPU负载估算]

## 7. 可追溯性
[引用 13-51_Traceability_Matrix.csv]
""",
            
            "04-05_Software_Detailed_Design.md": f"""# 软件详细设计文档

## 文档信息
| 项目 | 内容 |
|------|------|
| 文档编号 | 04-05 |
| 项目名称 | {self.project_name} |
| 版本 | 1.0 |
| 创建日期 | {current_date} |
| 状态 | 草稿 |

## 1. 引言
### 1.1 目的与范围
[描述本文档的目的和范围]

### 1.2 参考文档
- 04-04_Software_Architecture.md

## 2. 设计概述
### 2.1 设计原则
[描述设计原则]

### 2.2 编码规范
[描述编码规范要求]

## 3. 组件详细设计
### 3.1 [SWC-XXX]
#### 3.1.1 单元清单
| 单元ID | 单元名称 | 文件位置 | 功能描述 |
|--------|----------|----------|----------|
| SU-001 | ... | src/xxx.c | ... |

#### 3.1.2 单元详细设计
[各单元的详细设计]

## 4. 数据结构设计
### 4.1 全局数据结构
[全局数据结构定义]

### 4.2 类型定义
[自定义类型定义]

## 5. 文件结构
### 5.1 头文件组织
```
src/include/
├── module_a.h
├── module_b.h
└── ...
```

### 5.2 源文件组织
```
src/
├── module_a.c
├── module_b.c
└── ...
```

## 6. 可追溯性
[引用 13-51_Traceability_Matrix.csv]
""",
            
            "08-60_Unit_Verification_Measures.md": f"""# 单元验证措施

## 文档信息
| 项目 | 内容 |
|------|------|
| 文档编号 | 08-60 |
| 项目名称 | {self.project_name} |
| 版本 | 1.0 |
| 创建日期 | {current_date} |
| 状态 | 草稿 |

## 1. 验证策略
### 1.1 验证方法
| 方法 | 适用范围 | 工具 |
|------|----------|------|
| 静态分析 | 所有代码 | Cppcheck |
| 单元测试 | 所有单元 | Unity |

### 1.2 覆盖率要求
| 覆盖类型 | 目标值 |
|----------|--------|
| 语句覆盖 | 100% |
| 分支覆盖 | 100% |

## 2. 静态分析措施
### 2.1 分析工具配置
[工具配置信息]

### 2.2 分析规则集
[使用的规则集]

## 3. 单元测试措施
### 3.1 测试框架
[测试框架说明]

### 3.2 测试用例设计
| 测试ID | 被测单元 | 测试类型 | 描述 |
|--------|----------|----------|------|
| UT-SU001-001 | SU-001 | 功能测试 | ... |

## 4. 验证措施清单
| 措施ID | 类型 | 描述 | 关联单元 |
|--------|------|------|----------|
| VM-001 | 静态分析 | MISRA-C检查 | SU-001 |
""",
            
            "15-52_Unit_Verification_Results.md": f"""# 单元验证结果

## 文档信息
| 项目 | 内容 |
|------|------|
| 文档编号 | 15-52 |
| 项目名称 | {self.project_name} |
| 版本 | 1.0 |
| 创建日期 | {current_date} |
| 状态 | 草稿 |

## 1. 静态分析结果
### 1.1 分析工具信息
| 工具 | 版本 | 配置文件 |
|------|------|----------|
| Cppcheck | 2.7 | misra.json |

### 1.2 分析结果摘要
| 级别 | 数量 | 状态 |
|------|------|------|
| error | 0 | - |
| warning | 0 | - |

### 1.3 问题清单与处理
| 问题ID | 描述 | 级别 | 状态 |
|--------|------|------|------|
| - | - | - | - |

## 2. 单元测试结果
### 2.1 执行摘要
| 项目 | 值 |
|------|-----|
| 总用例数 | 0 |
| 通过数 | 0 |
| 失败数 | 0 |
| 通过率 | - |

### 2.2 详细结果
| 测试ID | 结果 | 执行时间 | 备注 |
|--------|------|----------|------|
| - | - | - | - |

### 2.3 覆盖率报告
| 覆盖类型 | 目标 | 实际 | 状态 |
|----------|------|------|------|
| 语句覆盖 | 100% | - | - |
| 分支覆盖 | 100% | - | - |

## 3. 验证结论
### 3.1 总体评价
[验证结果总结]

### 3.2 遗留问题
[待解决问题列表]
""",
            
            "13-51_Traceability_Matrix.csv": """User_Req_ID,SW_Req_ID,Arch_Component_ID,Detailed_Design_ID,Unit_ID,Verification_Measure_ID,Verification_Result_ID,Relationship,Notes
"""
        }
    
    def _get_default_template(self, filename: str, description: str) -> str:
        """获取默认模板"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        return f"""# {description}

## 文档信息
| 项目 | 内容 |
|------|------|
| 文档编号 | {filename.split('_')[0]} |
| 项目名称 | {self.project_name} |
| 版本 | 1.0 |
| 创建日期 | {current_date} |
| 状态 | 草稿 |

## 1. 引言
[待填写]

## 2. 正文
[待填写]
"""
    
    def _create_traceability_matrix(self) -> None:
        """创建追溯性矩阵"""
        print("\n创建追溯性矩阵...")
        filepath = os.path.join(self.workspace, "13-51_Traceability_Matrix.csv")
        
        if os.path.exists(filepath):
            print("  追溯性矩阵已存在，跳过")
            return
        
        header = "User_Req_ID,SW_Req_ID,Arch_Component_ID,Detailed_Design_ID,Unit_ID,Verification_Measure_ID,Verification_Result_ID,Relationship,Notes\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header)
        
        print("  创建: 13-51_Traceability_Matrix.csv")
    
    def _create_project_config(self) -> None:
        """创建项目配置文件"""
        print("\n创建项目配置...")
        
        config = f"""# ASPICE SWE 项目配置
project:
  name: {self.project_name}
  version: 1.0.0
  created: {datetime.now().isoformat()}

aspice:
  level: 2
  standard: Automotive SPICE 4.0
  
paths:
  docs: docs/
  src: src/
  tests: tests/
  reports: reports/

coverage:
  statement: 100%
  branch: 100%
  mcdc: 100%
"""
        
        config_path = os.path.join(self.workspace, "config", "project.yaml")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config)
        
        print(f"  创建: config/project.yaml")
    
    def get_status(self) -> Dict:
        """获取工作空间状态"""
        status = {
            "workspace": self.workspace,
            "exists": os.path.exists(self.workspace),
            "directories": {},
            "work_products": {},
            "ready_for_stage": {}
        }
        
        if not status["exists"]:
            return status
        
        # 检查目录
        for dir_path in self.DIRECTORY_STRUCTURE.keys():
            full_path = os.path.join(self.workspace, dir_path)
            status["directories"][dir_path] = os.path.exists(full_path)
        
        # 检查工作产品
        for filename in self.WORK_PRODUCTS.keys():
            filepath = os.path.join(self.workspace, filename)
            if os.path.exists(filepath):
                stat = os.stat(filepath)
                status["work_products"][filename] = {
                    "exists": True,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            else:
                status["work_products"][filename] = {"exists": False}
        
        # 确定可执行阶段
        status["ready_for_stage"] = self._determine_ready_stages(status["work_products"])
        
        return status
    
    def _determine_ready_stages(self, work_products: Dict) -> Dict:
        """确定可执行的阶段"""
        stages = {
            "SWE.1": work_products.get("17-00_Software_Requirements_Specification.md", {}).get("exists", False),
            "SWE.2": work_products.get("04-04_Software_Architecture.md", {}).get("exists", False),
            "SWE.3": work_products.get("04-05_Software_Detailed_Design.md", {}).get("exists", False),
            "SWE.4": work_products.get("15-52_Unit_Verification_Results.md", {}).get("exists", False),
            "SWE.5": work_products.get("15-52_Integration_Verification_Results.md", {}).get("exists", False),
            "SWE.6": work_products.get("15-52_Software_Verification_Results.md", {}).get("exists", False)
        }
        
        return stages
    
    def print_status(self) -> None:
        """打印工作空间状态"""
        status = self.get_status()
        
        print(f"\n工作空间状态: {status['workspace']}")
        print(f"存在: {'是' if status['exists'] else '否'}")
        
        if not status["exists"]:
            return
        
        print("\n目录结构:")
        for dir_path, exists in status["directories"].items():
            icon = "✓" if exists else "✗"
            print(f"  [{icon}] {dir_path}/")
        
        print("\n工作产品:")
        for filename, info in status["work_products"].items():
            if info.get("exists"):
                size = info.get("size", 0)
                print(f"  [✓] {filename} ({size} bytes)")
            else:
                print(f"  [✗] {filename}")
        
        print("\n阶段完成状态:")
        stage_names = {
            "SWE.1": "软件需求分析",
            "SWE.2": "软件架构设计",
            "SWE.3": "详细设计与单元构建",
            "SWE.4": "软件单元验证",
            "SWE.5": "软件集成验证",
            "SWE.6": "软件验证"
        }
        
        for stage, completed in status["ready_for_stage"].items():
            icon = "✓" if completed else "○"
            print(f"  [{icon}] {stage}: {stage_names[stage]}")


def main():
    parser = argparse.ArgumentParser(
        description="ASPICE SWE 工作空间初始化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 初始化工作空间
  python workspace_initializer.py init ./aspice_workspace --project-name MyProject
  
  # 查看工作空间状态
  python workspace_initializer.py status ./aspice_workspace
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化工作空间")
    init_parser.add_argument("workspace", help="工作目录路径")
    init_parser.add_argument("--project-name", default="ASPICE_SW_Project", help="项目名称")
    
    # status 命令
    status_parser = subparsers.add_parser("status", help="查看工作空间状态")
    status_parser.add_argument("workspace", help="工作目录路径")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    initializer = WorkspaceInitializer(args.workspace, 
                                        getattr(args, 'project_name', 'ASPICE_SW_Project'))
    
    if args.command == "init":
        initializer.init_workspace()
    
    elif args.command == "status":
        initializer.print_status()


if __name__ == "__main__":
    main()
