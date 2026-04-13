#!/usr/bin/env python3
"""
ASPICE SWE 合规验证工具

功能：
- 验证工作产品是否符合ASPICE规范
- 检查追溯性完整性
- 生成合规报告

使用方法：
    python aspice_validator.py validate <workspace>
    python aspice_validator.py checklist <workspace>
    python aspice_validator.py report <workspace>
"""

import argparse
import csv
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ComplianceLevel(Enum):
    """合规等级"""
    FULL = "Full"          # 完全合规
    PARTIAL = "Partial"    # 部分合规
    NON_COMPLIANT = "Non-Compliant"  # 不合规
    NOT_APPLICABLE = "N/A"  # 不适用


class ASPICEProcess(Enum):
    """ASPICE 过程"""
    SWE_1 = "SWE.1"
    SWE_2 = "SWE.2"
    SWE_3 = "SWE.3"
    SWE_4 = "SWE.4"
    SWE_5 = "SWE.5"
    SWE_6 = "SWE.6"


@dataclass
class ValidationResult:
    """验证结果"""
    check_id: str
    check_name: str
    process: str
    level: ComplianceLevel
    details: str
    evidence: str = ""
    recommendations: List[str] = field(default_factory=list)


@dataclass
class WorkProductStatus:
    """工作产品状态"""
    filename: str
    exists: bool
    has_content: bool
    required_sections: List[str]
    missing_sections: List[str]
    completeness: float


class ASPICEValidator:
    """ASPICE 合规验证器"""
    
    # 工作产品与过程的映射
    WORK_PRODUCT_PROCESS_MAP = {
        "17-00_Software_Requirements_Specification.md": ASPICEProcess.SWE_1,
        "04-04_Software_Architecture.md": ASPICEProcess.SWE_2,
        "04-05_Software_Detailed_Design.md": ASPICEProcess.SWE_3,
        "08-60_Unit_Verification_Measures.md": ASPICEProcess.SWE_4,
        "08-60_Integration_Verification_Measures.md": ASPICEProcess.SWE_5,
        "08-60_Software_Verification_Measures.md": ASPICEProcess.SWE_6,
        "15-52_Unit_Verification_Results.md": ASPICEProcess.SWE_4,
        "15-52_Integration_Verification_Results.md": ASPICEProcess.SWE_5,
        "15-52_Software_Verification_Results.md": ASPICEProcess.SWE_6,
        "13-51_Traceability_Matrix.csv": None  # 所有过程
    }
    
    # 各过程必需的工作产品
    REQUIRED_WORK_PRODUCTS = {
        ASPICEProcess.SWE_1: ["17-00_Software_Requirements_Specification.md"],
        ASPICEProcess.SWE_2: ["04-04_Software_Architecture.md"],
        ASPICEProcess.SWE_3: ["04-05_Software_Detailed_Design.md"],
        ASPICEProcess.SWE_4: ["08-60_Unit_Verification_Measures.md", "15-52_Unit_Verification_Results.md"],
        ASPICEProcess.SWE_5: ["08-60_Integration_Verification_Measures.md", "15-52_Integration_Verification_Results.md"],
        ASPICEProcess.SWE_6: ["08-60_Software_Verification_Measures.md", "15-52_Software_Verification_Results.md"]
    }
    
    # 文档必需章节
    REQUIRED_SECTIONS = {
        "17-00_Software_Requirements_Specification.md": [
            "引言", "功能需求", "非功能需求", "接口需求"
        ],
        "04-04_Software_Architecture.md": [
            "架构概述", "架构视图", "组件定义", "接口定义"
        ],
        "04-05_Software_Detailed_Design.md": [
            "设计概述", "组件详细设计", "数据结构设计"
        ],
        "08-60_Unit_Verification_Measures.md": [
            "验证策略", "静态分析措施", "单元测试措施"
        ],
        "15-52_Unit_Verification_Results.md": [
            "静态分析结果", "单元测试结果", "验证结论"
        ]
    }
    
    # ASPICE 基本实践检查项
    BASE_PRACTICES = {
        ASPICEProcess.SWE_1: [
            ("BP1", "分析系统需求", "分析系统需求以确定软件需求"),
            ("BP2", "定义软件需求", "定义软件功能和非功能需求"),
            ("BP3", "分析软件需求", "分析并构建软件需求"),
            ("BP4", "建立需求追溯", "建立软件需求与系统需求的追溯"),
            ("BP5", "开发验证准则", "开发软件需求的验证准则"),
            ("BP6", "记录需求结果", "记录软件需求分析结果"),
        ],
        ASPICEProcess.SWE_2: [
            ("BP1", "定义架构设计", "定义软件架构的高级设计"),
            ("BP2", "分配需求", "将软件需求分配到架构组件"),
            ("BP3", "定义接口", "定义软件组件间的接口"),
            ("BP4", "描述动态行为", "描述软件的动态行为"),
            ("BP5", "定义资源消耗", "定义软件的资源消耗目标"),
            ("BP6", "评估架构设计", "评估备选架构设计"),
        ],
        ASPICEProcess.SWE_3: [
            ("BP1", "开发详细设计", "为软件组件开发详细设计"),
            ("BP2", "定义软件单元", "将组件分解为软件单元"),
            ("BP3", "描述单元算法", "描述每个软件单元的算法"),
            ("BP4", "定义接口", "定义软件单元的接口"),
            ("BP5", "描述动态行为", "描述软件单元的动态行为"),
            ("BP6", "记录设计结果", "记录详细设计结果"),
        ],
        ASPICEProcess.SWE_4: [
            ("BP1", "制定验证策略", "制定软件单元验证策略"),
            ("BP2", "开发验证措施", "开发单元验证措施"),
            ("BP3", "执行静态分析", "执行静态分析"),
            ("BP4", "执行单元测试", "执行单元测试"),
            ("BP5", "记录结果", "记录单元验证结果"),
            ("BP6", "确保一致性", "确保验证结果的一致性"),
        ],
        ASPICEProcess.SWE_5: [
            ("BP1", "制定集成策略", "制定软件集成策略"),
            ("BP2", "开发集成措施", "开发集成验证措施"),
            ("BP3", "集成软件单元", "集成软件单元和组件"),
            ("BP4", "执行集成测试", "执行集成验证"),
            ("BP5", "记录结果", "记录集成验证结果"),
            ("BP6", "确保一致性", "确保集成结果一致性"),
        ],
        ASPICEProcess.SWE_6: [
            ("BP1", "制定验证策略", "制定软件验证策略"),
            ("BP2", "开发验证措施", "开发软件验证措施"),
            ("BP3", "执行验证", "执行软件验证"),
            ("BP4", "记录结果", "记录验证结果"),
            ("BP5", "确保一致性", "确保验证结果一致性"),
        ]
    }
    
    def __init__(self, workspace: str):
        self.workspace = workspace
        self.results: List[ValidationResult] = []
        self.work_product_status: Dict[str, WorkProductStatus] = {}
    
    def validate_all(self) -> Dict:
        """执行全部验证"""
        print(f"正在验证工作空间: {self.workspace}")
        print("=" * 60)
        
        # 检查工作产品
        self._check_work_products()
        
        # 检查追溯性
        self._check_traceability()
        
        # 检查基本实践
        self._check_base_practices()
        
        # 生成汇总报告
        summary = self._generate_summary()
        
        return summary
    
    def _check_work_products(self) -> None:
        """检查工作产品"""
        print("\n[1] 检查工作产品...")
        
        for filename in self.WORK_PRODUCT_PROCESS_MAP.keys():
            filepath = os.path.join(self.workspace, filename)
            
            if filename.endswith('.md'):
                status = self._check_markdown_document(filepath, filename)
            elif filename.endswith('.csv'):
                status = self._check_csv_document(filepath, filename)
            else:
                continue
            
            self.work_product_status[filename] = status
            
            # 记录验证结果
            level = ComplianceLevel.FULL if status.completeness >= 100 else (
                ComplianceLevel.PARTIAL if status.completeness > 0 
                else ComplianceLevel.NON_COMPLIANT
            )
            
            result = ValidationResult(
                check_id=f"WP-{filename.split('_')[0]}",
                check_name=f"工作产品检查: {filename}",
                process=self.WORK_PRODUCT_PROCESS_MAP.get(filename, "ALL").value if self.WORK_PRODUCT_PROCESS_MAP.get(filename) else "ALL",
                level=level,
                details=f"完整度: {status.completeness:.1f}%",
                evidence=filepath,
                recommendations=self._get_recommendations(status)
            )
            self.results.append(result)
            
            icon = "✓" if status.exists and status.has_content else "✗"
            print(f"  [{icon}] {filename}: {status.completeness:.1f}%")
            if status.missing_sections:
                print(f"      缺失章节: {', '.join(status.missing_sections)}")
    
    def _check_markdown_document(self, filepath: str, filename: str) -> WorkProductStatus:
        """检查Markdown文档"""
        required_sections = self.REQUIRED_SECTIONS.get(filename, [])
        missing_sections = []
        
        exists = os.path.exists(filepath)
        has_content = False
        content = ""
        
        if exists:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            has_content = len(content.strip()) > 100  # 至少100字符
            
            # 检查必需章节
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
        
        completeness = 0.0
        if exists:
            if has_content:
                if required_sections:
                    completeness = (len(required_sections) - len(missing_sections)) / len(required_sections) * 100
                else:
                    completeness = 100.0
            else:
                completeness = 10.0  # 文件存在但内容不足
        
        return WorkProductStatus(
            filename=filename,
            exists=exists,
            has_content=has_content,
            required_sections=required_sections,
            missing_sections=missing_sections,
            completeness=completeness
        )
    
    def _check_csv_document(self, filepath: str, filename: str) -> WorkProductStatus:
        """检查CSV文档"""
        exists = os.path.exists(filepath)
        has_content = False
        row_count = 0
        
        if exists:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    row_count = len(rows)
                    has_content = row_count > 1  # 至少有表头+1行数据
            except Exception:
                pass
        
        completeness = 0.0
        if exists:
            if has_content:
                completeness = min(100.0, row_count * 10)  # 每行10%，最大100%
            else:
                completeness = 20.0  # 文件存在
        
        return WorkProductStatus(
            filename=filename,
            exists=exists,
            has_content=has_content,
            required_sections=["数据行"],
            missing_sections=[] if has_content else ["数据行"],
            completeness=completeness
        )
    
    def _check_traceability(self) -> None:
        """检查追溯性"""
        print("\n[2] 检查追溯性...")
        
        traceability_file = os.path.join(self.workspace, "13-51_Traceability_Matrix.csv")
        
        if not os.path.exists(traceability_file):
            result = ValidationResult(
                check_id="TR-001",
                check_name="追溯性矩阵存在性",
                process="ALL",
                level=ComplianceLevel.NON_COMPLIANT,
                details="追溯性矩阵文件不存在",
                recommendations=["创建 13-51_Traceability_Matrix.csv 文件"]
            )
            self.results.append(result)
            print("  [✗] 追溯性矩阵不存在")
            return
        
        # 读取追溯性矩阵
        links = []
        try:
            with open(traceability_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    links.append(row)
        except Exception as e:
            result = ValidationResult(
                check_id="TR-002",
                check_name="追溯性矩阵格式",
                process="ALL",
                level=ComplianceLevel.NON_COMPLIANT,
                details=f"无法读取追溯性矩阵: {str(e)}",
                recommendations=["检查CSV文件格式"]
            )
            self.results.append(result)
            print(f"  [✗] 无法读取追溯性矩阵: {e}")
            return
        
        # 检查追溯性完整性
        levels = ["User_Req_ID", "SW_Req_ID", "Arch_Component_ID", 
                  "Detailed_Design_ID", "Unit_ID", "Verification_Measure_ID"]
        
        for i, level in enumerate(levels[:-1]):
            next_level = levels[i + 1]
            
            # 统计该层级的链接数
            links_count = 0
            for link in links:
                if link.get(level) and link.get(next_level):
                    links_count += 1
            
            result = ValidationResult(
                check_id=f"TR-{i+3:03d}",
                check_name=f"追溯性: {level} → {next_level}",
                process="ALL",
                level=ComplianceLevel.FULL if links_count > 0 else ComplianceLevel.NON_COMPLIANT,
                details=f"发现 {links_count} 条追溯链接",
                recommendations=[] if links_count > 0 else [f"添加 {level} 到 {next_level} 的追溯链接"]
            )
            self.results.append(result)
            
            icon = "✓" if links_count > 0 else "✗"
            print(f"  [{icon}] {level} → {next_level}: {links_count} 条链接")
    
    def _check_base_practices(self) -> None:
        """检查基本实践"""
        print("\n[3] 检查基本实践...")
        
        for process, practices in self.BASE_PRACTICES.items():
            print(f"\n  {process.value}:")
            
            process_results = []
            
            for bp_id, bp_name, bp_desc in practices:
                # 根据工作产品状态评估实践执行情况
                level = self._evaluate_practice(process, bp_id)
                
                result = ValidationResult(
                    check_id=f"{process.value}-{bp_id}",
                    check_name=bp_name,
                    process=process.value,
                    level=level,
                    details=bp_desc,
                    recommendations=self._get_bp_recommendations(process, bp_id, level)
                )
                self.results.append(result)
                process_results.append(result)
                
                icon = {"Full": "✓", "Partial": "◐", "Non-Compliant": "✗"}.get(level.value, "?")
                print(f"    [{icon}] {bp_id}: {bp_name}")
    
    def _evaluate_practice(self, process: ASPICEProcess, bp_id: str) -> ComplianceLevel:
        """评估实践执行情况"""
        # 获取该过程的工作产品
        required_wps = self.REQUIRED_WORK_PRODUCTS.get(process, [])
        
        if not required_wps:
            return ComplianceLevel.NOT_APPLICABLE
        
        # 检查工作产品状态
        total_completeness = 0
        for wp in required_wps:
            status = self.work_product_status.get(wp)
            if status:
                total_completeness += status.completeness
        
        avg_completeness = total_completeness / len(required_wps) if required_wps else 0
        
        if avg_completeness >= 80:
            return ComplianceLevel.FULL
        elif avg_completeness >= 40:
            return ComplianceLevel.PARTIAL
        else:
            return ComplianceLevel.NON_COMPLIANT
    
    def _get_recommendations(self, status: WorkProductStatus) -> List[str]:
        """获取改进建议"""
        recommendations = []
        
        if not status.exists:
            recommendations.append(f"创建文件: {status.filename}")
        elif not status.has_content:
            recommendations.append("添加文档内容")
        
        for section in status.missing_sections:
            recommendations.append(f"添加章节: {section}")
        
        return recommendations
    
    def _get_bp_recommendations(self, process: ASPICEProcess, bp_id: str, 
                                level: ComplianceLevel) -> List[str]:
        """获取基本实践改进建议"""
        if level == ComplianceLevel.FULL:
            return []
        
        # 根据实践ID提供具体建议
        recommendations_map = {
            (ASPICEProcess.SWE_1, "BP1"): ["完成系统需求分析文档"],
            (ASPICEProcess.SWE_1, "BP2"): ["在需求文档中定义功能和非功能需求"],
            (ASPICEProcess.SWE_1, "BP4"): ["更新追溯性矩阵，建立需求追溯"],
            (ASPICEProcess.SWE_2, "BP1"): ["完善架构设计文档"],
            (ASPICEProcess.SWE_2, "BP3"): ["定义组件间的接口规范"],
            (ASPICEProcess.SWE_4, "BP3"): ["执行静态分析并记录结果"],
            (ASPICEProcess.SWE_4, "BP4"): ["执行单元测试并记录结果"],
        }
        
        return recommendations_map.get((process, bp_id), ["完善相关工作产品"])
    
    def _generate_summary(self) -> Dict:
        """生成验证汇总"""
        total_checks = len(self.results)
        full_count = sum(1 for r in self.results if r.level == ComplianceLevel.FULL)
        partial_count = sum(1 for r in self.results if r.level == ComplianceLevel.PARTIAL)
        non_compliant_count = sum(1 for r in self.results if r.level == ComplianceLevel.NON_COMPLIANT)
        
        # 计算各过程合规率
        process_compliance = {}
        for process in ASPICEProcess:
            process_results = [r for r in self.results if r.process == process.value]
            if process_results:
                full = sum(1 for r in process_results if r.level == ComplianceLevel.FULL)
                process_compliance[process.value] = full / len(process_results) * 100
            else:
                process_compliance[process.value] = 0
        
        summary = {
            "workspace": self.workspace,
            "validation_date": datetime.now().isoformat(),
            "total_checks": total_checks,
            "full_compliance": full_count,
            "partial_compliance": partial_count,
            "non_compliant": non_compliant_count,
            "overall_compliance_rate": full_count / total_checks * 100 if total_checks > 0 else 0,
            "process_compliance": process_compliance,
            "results": self.results,
            "recommendations": self._collect_recommendations()
        }
        
        return summary
    
    def _collect_recommendations(self) -> List[str]:
        """收集所有改进建议"""
        all_recommendations = []
        for result in self.results:
            all_recommendations.extend(result.recommendations)
        
        # 去重
        return list(dict.fromkeys(all_recommendations))
    
    def generate_checklist(self) -> str:
        """生成检查清单"""
        checklist = []
        checklist.append("# ASPICE SWE 过程检查清单\n")
        checklist.append(f"生成时间: {datetime.now().isoformat()}")
        checklist.append(f"工作空间: {self.workspace}\n")
        
        for process in ASPICEProcess:
            checklist.append(f"\n## {process.value}\n")
            
            practices = self.BASE_PRACTICES.get(process, [])
            for bp_id, bp_name, bp_desc in practices:
                checklist.append(f"- [ ] **{bp_id}**: {bp_name}")
                checklist.append(f"  - {bp_desc}\n")
        
        return "\n".join(checklist)
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """生成验证报告"""
        summary = self.validate_all()
        
        report = []
        report.append("# ASPICE SWE 合规验证报告\n")
        report.append(f"生成时间: {summary['validation_date']}")
        report.append(f"工作空间: {summary['workspace']}\n")
        
        report.append("## 验证摘要\n")
        report.append(f"| 项目 | 数量 |")
        report.append(f"|------|------|")
        report.append(f"| 总检查项 | {summary['total_checks']} |")
        report.append(f"| 完全合规 | {summary['full_compliance']} |")
        report.append(f"| 部分合规 | {summary['partial_compliance']} |")
        report.append(f"| 不合规 | {summary['non_compliant']} |")
        report.append(f"| 总体合规率 | {summary['overall_compliance_rate']:.1f}% |\n")
        
        report.append("## 各过程合规率\n")
        report.append("| 过程 | 合规率 |")
        report.append("|------|--------|")
        for process, rate in summary['process_compliance'].items():
            report.append(f"| {process} | {rate:.1f}% |")
        
        report.append("\n## 详细检查结果\n")
        for result in summary['results']:
            icon = {"Full": "✓", "Partial": "◐", "Non-Compliant": "✗", "N/A": "-"}.get(result.level.value, "?")
            report.append(f"### [{icon}] {result.check_name}\n")
            report.append(f"- **检查ID**: {result.check_id}")
            report.append(f"- **过程**: {result.process}")
            report.append(f"- **状态**: {result.level.value}")
            report.append(f"- **详情**: {result.details}")
            if result.recommendations:
                report.append(f"- **建议**:")
                for rec in result.recommendations:
                    report.append(f"  - {rec}")
            report.append("")
        
        if summary['recommendations']:
            report.append("## 改进建议汇总\n")
            for i, rec in enumerate(summary['recommendations'], 1):
                report.append(f"{i}. {rec}")
        
        report_text = "\n".join(report)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"\n报告已保存到: {output_path}")
        
        return report_text


def main():
    parser = argparse.ArgumentParser(
        description="ASPICE SWE 合规验证工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 执行完整验证
  python aspice_validator.py validate ./aspice_workspace
  
  # 生成检查清单
  python aspice_validator.py checklist ./aspice_workspace
  
  # 生成验证报告
  python aspice_validator.py report ./aspice_workspace --output validation_report.md
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # validate 命令
    validate_parser = subparsers.add_parser("validate", help="执行完整验证")
    validate_parser.add_argument("workspace", help="工作目录路径")
    
    # checklist 命令
    checklist_parser = subparsers.add_parser("checklist", help="生成检查清单")
    checklist_parser.add_argument("workspace", help="工作目录路径")
    checklist_parser.add_argument("--output", help="输出文件路径")
    
    # report 命令
    report_parser = subparsers.add_parser("report", help="生成验证报告")
    report_parser.add_argument("workspace", help="工作目录路径")
    report_parser.add_argument("--output", help="报告输出路径")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    validator = ASPICEValidator(args.workspace)
    
    if args.command == "validate":
        validator.validate_all()
    
    elif args.command == "checklist":
        checklist = validator.generate_checklist()
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(checklist)
            print(f"检查清单已保存到: {args.output}")
        else:
            print(checklist)
    
    elif args.command == "report":
        output_path = args.output or os.path.join(args.workspace, "aspice_validation_report.md")
        validator.generate_report(output_path)


if __name__ == "__main__":
    main()
