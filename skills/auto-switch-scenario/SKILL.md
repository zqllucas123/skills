---
name: auto-switch-scenario
description: 切换 DreamCarSim 仿真场景。用于用户说"切换场景"、"换个场景"、"触发场景"、"帮我切换到 xxx 场景"、"选择仿真场景"时。会自动读取 ~/.sdw/senarios/ 下的可用场景，检查 DreamCarSim.exe 是否运行并按需启动，再触发对应的 AHK 脚本完成场景切换。
---

# Auto Switch Scenario

## 目标

根据用户的场景选择，自动完成：检查 DreamCarSim 软件是否运行 → 按需启动 → 触发目标场景的 AHK 脚本。

## 工具脚本

所有逻辑均封装在 `scripts/trigger_scene.py`，执行时需在 Windows 环境下运行（依赖 `tasklist` 和 AHK）。

```bash
# 列出可用场景
python skills/auto-switch-scenario/scripts/trigger_scene.py --list

# 触发指定场景（传入中文场景名，不含 .ahk 后缀）
python skills/auto-switch-scenario/scripts/trigger_scene.py --run <场景名>
```

## 执行流程

### 第 1 步：列出并展示可用场景

运行以下命令获取场景列表（读取 `~/.sdw/senarios/` 下所有 `.ahk` 文件，自动排除 `run_app.ahk`）：

```bash
python skills/auto-switch-scenario/scripts/trigger_scene.py --list
```

将输出的场景名以编号列表的方式告知用户，例如：

```
可用场景：
  1. 光庭停车场
  2. 山姆超市混合停车位
  3. 重庆雨天
```

询问用户选择哪个场景。

### 第 2 步：触发所选场景

用户选定后，执行：

```bash
python skills/auto-switch-scenario/scripts/trigger_scene.py --run "<用户选择的场景名>"
```

脚本会自动：
1. 检测 `DreamCarSim.exe` 是否运行
2. 若未运行，调用 `run_app.ahk` 启动软件并等待 30 秒
3. 调用对应场景的 `.ahk` 脚本完成场景切换

### 第 3 步：反馈结果

- 若脚本输出 `[OK]`，告知用户场景已触发成功
- 若输出 `[ERROR]`，将错误信息转述给用户并说明可用场景

## 约束

- `run_app.ahk` 仅用于启动软件，不作为场景选项展示给用户
- 不得修改 `~/.sdw/senarios/` 下的任何 `.ahk` 文件
- 仅在 Windows 环境下有效（脚本依赖 `tasklist` 和 AutoHotkey）

## 示例

**用户输入：** 帮我切换到山姆超市混合停车位场景

**执行过程：**
1. 运行 `--list` 确认场景存在
2. 运行 `--run "山姆超市混合停车位"`
3. 脚本检测到 DreamCarSim 已运行，直接触发场景 AHK
4. 回复用户：「场景『山姆超市混合停车位』已触发。」
