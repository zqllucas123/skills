#!/usr/bin/env python3
"""
ASPICE SWE 追溯性矩阵管理工具

功能：
- 创建、更新、验证追溯性矩阵
- 支持双向追溯性检查
- 生成追溯性报告

使用方法：
    python traceability_manager.py init <workspace>
    python traceability_manager.py add <workspace> --source <id> --target <id> --type <type>
    python traceability_manager.py validate <workspace>
    python traceability_manager.py report <workspace>
"""

import argparse
import csv
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class TraceabilityType(Enum):
    """追溯关系类型"""
    SATISFIES = "satisfies"
    DERIVES = "derives"
    REFINES = "refines"
    IMPLEMENTS = "implements"
    VERIFIES = "verifies"


class TraceabilityLevel(Enum):
    """追溯层级"""
    USER_REQ = "User_Req_ID"
    SW_REQ = "SW_Req_ID"
    ARCH_COMPONENT = "Arch_Component_ID"
    DETAILED_DESIGN = "Detailed_Design_ID"
    UNIT = "Unit_ID"
    VERIFICATION_MEASURE = "Verification_Measure_ID"
    VERIFICATION_RESULT = "Verification_Result_ID"


@dataclass
class TraceabilityLink:
    """追溯链接"""
    source_id: str
    target_id: str
    relationship: str
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TraceabilityMatrix:
    """追溯性矩阵"""
    links: List[TraceabilityLink] = field(default_factory=list)
    
    def add_link(self, link: TraceabilityLink) -> None:
        """添加追溯链接"""
        # 检查是否已存在
        for existing in self.links:
            if (existing.source_id == link.source_id and 
                existing.target_id == link.target_id and
                existing.relationship == link.relationship):
                return  # 已存在，不重复添加
        self.links.append(link)
    
    def find_by_source(self, source_id: str) -> List[TraceabilityLink]:
        """根据源ID查找链接"""
        return [link for link in self.links if link.source_id == source_id]
    
    def find_by_target(self, target_id: str) -> List[TraceabilityLink]:
        """根据目标ID查找链接"""
        return [link for link in self.links if link.target_id == target_id]
    
    def get_all_ids(self, level: str) -> Set[str]:
        """获取指定层级的所有ID"""
        ids = set()
        for link in self.links:
            if level.lower() in link.source_id.lower():
                ids.add(link.source_id)
            if level.lower() in link.target_id.lower():
                ids.add(link.target_id)
        return ids


class TraceabilityManager:
    """追溯性管理器"""
    
    TRACEABILITY_FILE = "13-51_Traceability_Matrix.csv"
    
    # 追溯层级顺序
    LEVEL_ORDER = [
        "User_Req_ID",
        "SW_Req_ID", 
        "Arch_Component_ID",
        "Detailed_Design_ID",
        "Unit_ID",
        "Verification_Measure_ID",
        "Verification_Result_ID"
    ]
    
    def __init__(self, workspace: str):
        self.workspace = workspace
        self.traceability_path = os.path.join(workspace, self.TRACEABILITY_FILE)
        self.matrix = TraceabilityMatrix()
    
    def init_matrix(self) -> None:
        """初始化追溯性矩阵文件"""
        os.makedirs(self.workspace, exist_ok=True)
        
        if os.path.exists(self.traceability_path):
            print(f"追溯性矩阵文件已存在: {self.traceability_path}")
            return
        
        # 创建初始CSV文件
        with open(self.traceability_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.LEVEL_ORDER + ["Relationship", "Notes"])
        
        print(f"已创建追溯性矩阵文件: {self.traceability_path}")
    
    def load_matrix(self) -> None:
        """加载追溯性矩阵"""
        if not os.path.exists(self.traceability_path):
            raise FileNotFoundError(f"追溯性矩阵文件不存在: {self.traceability_path}")
        
        with open(self.traceability_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 从行数据中提取链接信息
                source_id = None
                target_id = None
                
                # 找到非空的ID列
                non_empty_ids = []
                for level in self.LEVEL_ORDER:
                    if row.get(level) and row[level].strip():
                        non_empty_ids.append(row[level])
                
                if len(non_empty_ids) >= 2:
                    # 创建相邻层级间的链接
                    for i in range(len(non_empty_ids) - 1):
                        link = TraceabilityLink(
                            source_id=non_empty_ids[i],
                            target_id=non_empty_ids[i + 1],
                            relationship=row.get("Relationship", "satisfies"),
                            notes=row.get("Notes", "")
                        )
                        self.matrix.add_link(link)
    
    def add_link(self, source_id: str, target_id: str, 
                 relationship: str = "satisfies", notes: str = "") -> None:
        """添加追溯链接"""
        link = TraceabilityLink(
            source_id=source_id,
            target_id=target_id,
            relationship=relationship,
            notes=notes
        )
        self.matrix.add_link(link)
        self._save_link(link)
        print(f"已添加追溯链接: {source_id} -> {target_id} ({relationship})")
    
    def _save_link(self, link: TraceabilityLink) -> None:
        """保存链接到CSV文件"""
        # 追加一行到CSV文件
        with open(self.traceability_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 确定每个层级的值
            row = [""] * len(self.LEVEL_ORDER)
            
            # 根据ID前缀确定层级
            source_level = self._get_level_from_id(link.source_id)
            target_level = self._get_level_from_id(link.target_id)
            
            if source_level:
                row[self.LEVEL_ORDER.index(source_level)] = link.source_id
            if target_level:
                row[self.LEVEL_ORDER.index(target_level)] = link.target_id
            
            row.extend([link.relationship, link.notes])
            writer.writerow(row)
    
    def _get_level_from_id(self, id_str: str) -> Optional[str]:
        """根据ID格式确定层级"""
        id_upper = id_str.upper()
        
        if id_upper.startswith("UR-"):
            return "User_Req_ID"
        elif id_upper.startswith("SWR-"):
            return "SW_Req_ID"
        elif id_upper.startswith("SWC-"):
            return "Arch_Component_ID"
        elif id_upper.startswith("DD-"):
            return "Detailed_Design_ID"
        elif id_upper.startswith("SU-"):
            return "Unit_ID"
        elif id_upper.startswith("VM-"):
            return "Verification_Measure_ID"
        elif id_upper.startswith("VR-"):
            return "Verification_Result_ID"
        
        return None
    
    def validate_traceability(self) -> Dict:
        """验证追溯性完整性"""
        self.load_matrix()
        
        results = {
            "is_valid": True,
            "coverage": {},
            "missing_links": [],
            "orphan_items": [],
            "warnings": []
        }
        
        # 检查每个层级的覆盖情况
        for i, level in enumerate(self.LEVEL_ORDER[:-1]):
            next_level = self.LEVEL_ORDER[i + 1]
            
            # 获取当前层级和下一层级的所有ID
            current_ids = self.matrix.get_all_ids(level)
            next_ids = self.matrix.get_all_ids(next_level)
            
            # 检查是否有链接
            links_from_current = sum(1 for link in self.matrix.links 
                                    if self._get_level_from_id(link.source_id) == level)
            links_to_next = sum(1 for link in self.matrix.links 
                               if self._get_level_from_id(link.target_id) == next_level)
            
            coverage = {
                "from_level": level,
                "to_level": next_level,
                "source_count": len(current_ids),
                "target_count": len(next_ids),
                "link_count": min(links_from_current, links_to_next),
                "coverage_rate": 0.0
            }
            
            if len(current_ids) > 0:
                coverage["coverage_rate"] = min(links_from_current, links_to_next) / len(current_ids) * 100
            
            results["coverage"][f"{level}_to_{next_level}"] = coverage
            
            if coverage["coverage_rate"] < 100:
                results["warnings"].append(
                    f"{level} -> {next_level} 覆盖率: {coverage['coverage_rate']:.1f}%"
                )
        
        # 检查孤立项（没有链接的项）
        all_source_ids = set(link.source_id for link in self.matrix.links)
        all_target_ids = set(link.target_id for link in self.matrix.links)
        all_linked_ids = all_source_ids | all_target_ids
        
        # 检查双向追溯
        for link in self.matrix.links:
            # 检查是否有反向追溯
            reverse_links = self.matrix.find_by_source(link.target_id)
            if not reverse_links and self._get_level_from_id(link.target_id) != self.LEVEL_ORDER[-1]:
                results["warnings"].append(
                    f"缺少反向追溯: {link.target_id} 没有向下的追溯链接"
                )
        
        results["is_valid"] = len(results["missing_links"]) == 0 and len(results["orphan_items"]) == 0
        
        return results
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """生成追溯性报告"""
        self.load_matrix()
        validation = self.validate_traceability()
        
        report = []
        report.append("# 追溯性矩阵报告")
        report.append(f"\n生成时间: {datetime.now().isoformat()}")
        report.append(f"工作目录: {self.workspace}")
        report.append(f"总链接数: {len(self.matrix.links)}")
        
        report.append("\n## 追溯覆盖率\n")
        report.append("| 源层级 | 目标层级 | 源项数 | 目标项数 | 链接数 | 覆盖率 |")
        report.append("|--------|----------|--------|----------|--------|--------|")
        
        for key, coverage in validation["coverage"].items():
            report.append(
                f"| {coverage['from_level']} | {coverage['to_level']} | "
                f"{coverage['source_count']} | {coverage['target_count']} | "
                f"{coverage['link_count']} | {coverage['coverage_rate']:.1f}% |"
            )
        
        if validation["warnings"]:
            report.append("\n## 警告\n")
            for warning in validation["warnings"]:
                report.append(f"- {warning}")
        
        report.append("\n## 追溯链接详情\n")
        report.append("| 源ID | 目标ID | 关系 | 备注 |")
        report.append("|------|--------|------|------|")
        
        for link in self.matrix.links:
            report.append(f"| {link.source_id} | {link.target_id} | {link.relationship} | {link.notes} |")
        
        report_text = "\n".join(report)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"报告已保存到: {output_path}")
        
        return report_text
    
    def export_matrix(self, output_format: str = "csv") -> str:
        """导出追溯性矩阵"""
        if output_format == "csv":
            return self.traceability_path
        elif output_format == "json":
            import json
            json_path = self.traceability_path.replace('.csv', '.json')
            
            data = {
                "links": [
                    {
                        "source_id": link.source_id,
                        "target_id": link.target_id,
                        "relationship": link.relationship,
                        "notes": link.notes,
                        "created_at": link.created_at
                    }
                    for link in self.matrix.links
                ]
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return json_path
        else:
            raise ValueError(f"不支持的导出格式: {output_format}")


def main():
    parser = argparse.ArgumentParser(
        description="ASPICE SWE 追溯性矩阵管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 初始化工作空间
  python traceability_manager.py init ./aspice_workspace
  
  # 添加追溯链接
  python traceability_manager.py add ./aspice_workspace --source UR-001 --target SWR-001 --type satisfies
  
  # 验证追溯性
  python traceability_manager.py validate ./aspice_workspace
  
  # 生成报告
  python traceability_manager.py report ./aspice_workspace
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化追溯性矩阵")
    init_parser.add_argument("workspace", help="工作目录路径")
    
    # add 命令
    add_parser = subparsers.add_parser("add", help="添加追溯链接")
    add_parser.add_argument("workspace", help="工作目录路径")
    add_parser.add_argument("--source", required=True, help="源ID")
    add_parser.add_argument("--target", required=True, help="目标ID")
    add_parser.add_argument("--type", default="satisfies", 
                           choices=["satisfies", "derives", "refines", "implements", "verifies"],
                           help="关系类型")
    add_parser.add_argument("--notes", default="", help="备注")
    
    # validate 命令
    validate_parser = subparsers.add_parser("validate", help="验证追溯性完整性")
    validate_parser.add_argument("workspace", help="工作目录路径")
    
    # report 命令
    report_parser = subparsers.add_parser("report", help="生成追溯性报告")
    report_parser.add_argument("workspace", help="工作目录路径")
    report_parser.add_argument("--output", help="报告输出路径")
    
    # export 命令
    export_parser = subparsers.add_parser("export", help="导出追溯性矩阵")
    export_parser.add_argument("workspace", help="工作目录路径")
    export_parser.add_argument("--format", default="csv", choices=["csv", "json"],
                              help="导出格式")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = TraceabilityManager(args.workspace)
    
    if args.command == "init":
        manager.init_matrix()
    
    elif args.command == "add":
        manager.load_matrix()
        manager.add_link(args.source, args.target, args.type, args.notes)
    
    elif args.command == "validate":
        results = manager.validate_traceability()
        print("\n=== 追溯性验证结果 ===")
        print(f"状态: {'通过' if results['is_valid'] else '未通过'}")
        
        if results["warnings"]:
            print("\n警告:")
            for warning in results["warnings"]:
                print(f"  - {warning}")
    
    elif args.command == "report":
        output_path = args.output or os.path.join(args.workspace, "traceability_report.md")
        report = manager.generate_report(output_path)
        print(report)
    
    elif args.command == "export":
        manager.load_matrix()
        output_path = manager.export_matrix(args.format)
        print(f"已导出到: {output_path}")


if __name__ == "__main__":
    main()
