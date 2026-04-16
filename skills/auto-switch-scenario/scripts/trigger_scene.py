"""
触发场景 AHK 脚本的调度工具。
用法：
  python trigger_scene.py --list               列出所有可用场景
  python trigger_scene.py --run <场景名>       检查软件并触发指定场景
"""

import subprocess
import os
import sys
import time
import argparse

# AHK 可执行文件路径（与 trigger.py 保持一致）
AHK_PATH = r"D:\software\auto_key\v1.1.37.02\AutoHotkeyU64.exe"

# 场景脚本目录：~/.sdw/senarios/
AUTO_TRIGGER_DIR = os.path.expanduser(r"~/.sdw/senarios")


def list_scenes() -> list[str]:
    """返回 auto_trigger/ 下所有场景名（去掉 run_app.ahk 和 .ahk 后缀）。"""
    names = []
    for f in sorted(os.listdir(AUTO_TRIGGER_DIR)):
        if f.endswith(".ahk") and f != "run_app.ahk":
            names.append(os.path.splitext(f)[0])
    return names


def is_dreamcarsim_running() -> bool:
    """检查 DreamCarSim.exe 进程是否存在。"""
    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq DreamCarSim.exe"],
        capture_output=True,
        text=True,
    )
    return "DreamCarSim.exe" in result.stdout


def run_ahk(script_path: str) -> None:
    """用 AHK 运行指定脚本，工作目录设为脚本所在目录。"""
    subprocess.Popen(
        [AHK_PATH, script_path],
        cwd=os.path.dirname(script_path),
    )


def ensure_app_running(wait_seconds: int = 30) -> None:
    """若 DreamCarSim 未运行则先启动，并等待软件就绪。"""
    if is_dreamcarsim_running():
        print("[INFO] DreamCarSim.exe 已在运行。")
        return

    print("[INFO] DreamCarSim.exe 未运行，正在通过 run_app.ahk 启动...")
    run_app_script = os.path.join(AUTO_TRIGGER_DIR, "run_app.ahk")
    run_ahk(run_app_script)
    print(f"[INFO] 等待软件启动（{wait_seconds} 秒）...")
    time.sleep(wait_seconds)

    if not is_dreamcarsim_running():
        print("[WARN] 软件可能尚未完全就绪，继续尝试触发场景。")


def trigger_scene(scene_name: str) -> None:
    """检查软件状态后触发指定场景脚本。"""
    scene_script = os.path.join(AUTO_TRIGGER_DIR, scene_name + ".ahk")
    if not os.path.exists(scene_script):
        available = list_scenes()
        print(f"[ERROR] 找不到场景脚本：{scene_script}")
        print(f"[INFO]  可用场景：{', '.join(available)}")
        sys.exit(1)

    ensure_app_running()
    print(f"[INFO] 正在触发场景：{scene_name}")
    run_ahk(scene_script)
    print(f"[OK]   场景「{scene_name}」已触发。")


def main() -> None:
    parser = argparse.ArgumentParser(description="DreamCarSim 场景切换工具")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="列出所有可用场景")
    group.add_argument("--run", metavar="SCENE", help="触发指定场景（中文名）")
    args = parser.parse_args()

    if args.list:
        scenes = list_scenes()
        if not scenes:
            print("[WARN] auto_trigger/ 中未找到任何场景脚本。")
        else:
            print("可用场景：")
            for i, s in enumerate(scenes, 1):
                print(f"  {i}. {s}")
    else:
        trigger_scene(args.run)


if __name__ == "__main__":
    main()
