"""Generate 8-week workout schedule starting from 2026-10-04."""
import json
from datetime import date, timedelta
from pathlib import Path

BASE = Path(r"D:\program\myPro\goodbody")
START = date(2026, 10, 4)
TOTAL_DAYS = 56
CYCLE = ["shoulder", "abs", "chest", "back", "legs", "rest"]
CYCLE_CN = {
    "shoulder": "肩部训练",
    "abs": "腹部训练",
    "chest": "胸部训练",
    "back": "背部训练",
    "legs": "腿部训练",
    "rest": "休息日",
}
WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
EXECUTIONS = {
    "shoulder": "跪姿冲肩俯卧撑 / 标准冲肩俯卧撑 / 折刀俯卧撑",
    "abs": "平板支撑 / 西西里卷腹 / 俯身开合跳",
    "chest": "跪姿俯卧撑 / 标准俯卧撑 / 下斜俯卧撑",
    "back": "门框划船 / 毛巾划船 / 反向划船或引体向上",
    "legs": "徒手深蹲 / 保加利亚分腿蹲 / 辅助单腿深蹲或跳跃深蹲 + 提踵",
    "rest": "可选休息；不安排训练动作",
}

# Build day list
days = []
for i in range(TOTAL_DAYS):
    d = START + timedelta(days=i)
    wtype = CYCLE[i % len(CYCLE)]
    days.append((d, wtype))

# Generate markdown
lines = []
lines.append("# 无器械五分化薄肌训练日程规划（v3.1）")
lines.append("")
lines.append("> 依据文档：《新手健身指导-文字版.md》《新手健身指导-图文详解版.md》《无器械五分化薄肌训练指导_v3.0.md》")
lines.append(f"> 计划周期：{START.isoformat()}（周日）至 {(START + timedelta(days=55)).isoformat()}（周六），共8周56天")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 执行规则")
lines.append("")
lines.append("**训练体系：** 无器械五分化薄肌训练  ")
lines.append("**循环周期：** 肩 → 腹 → 胸 → 背 → 腿 → 休息 → 重复  ")
lines.append("**组间休息：** 2分钟  ")
lines.append("**阶段规则：** 每个动作仅训练当前阶段，不要三个阶段一起做  ")
lines.append("**进阶规则：** 连续两次训练轻松完成目标、最后一组仍有1~2次余力、无关节疼痛即可升级阶段")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 每日固定流程")
lines.append("")
lines.append("| 顺序 | 内容 |")
lines.append("|---|---|")
lines.append("| 1 | 训练前热身5~8分钟 |")
lines.append("| 2 | 当天对应部位训练 |")
lines.append("| 3 | 训练后拉伸5~8分钟 |")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 动作安排")
lines.append("")
lines.append("### 肩部训练日")
lines.append("")
lines.append("| 当前阶段 | 训练动作 | 每组次数 | 组数 | 组间休息 |")
lines.append("|---|---|---:|---:|---:|")
lines.append("| 第一阶段 | 跪姿冲肩俯卧撑 | 8~10次 | 6组 | 2分钟 |")
lines.append("| 第二阶段 | 标准冲肩俯卧撑 | 8~10次 | 6组 | 2分钟 |")
lines.append("| 第三阶段 | 折刀俯卧撑 | 8~10次 | 6组 | 2分钟 |")
lines.append("")
lines.append("### 腹部训练日")
lines.append("")
lines.append("| 当前阶段 | 训练动作 | 每组次数/时长 | 组数 | 组间休息 |")
lines.append("|---|---|---:|---:|---:|")
lines.append("| 第一阶段 | 平板支撑 | 60秒 | 8组 | 2分钟 |")
lines.append("| 第二阶段 | 西西里卷腹 | 15次 | 5组 | 2分钟 |")
lines.append("| 第三阶段 | 俯身开合跳 | 12次 | 5组 | 2分钟 |")
lines.append("")
lines.append("### 胸部训练日")
lines.append("")
lines.append("| 当前阶段 | 训练动作 | 每组次数 | 组数 | 组间休息 |")
lines.append("|---|---|---:|---:|---:|")
lines.append("| 第一阶段 | 跪姿俯卧撑 | 12次 | 8组 | 2分钟 |")
lines.append("| 第二阶段 | 标准俯卧撑 | 12次 | 8组 | 2分钟 |")
lines.append("| 第三阶段 | 下斜俯卧撑 | 10~12次 | 8组 | 2分钟 |")
lines.append("")
lines.append("### 背部训练日")
lines.append("")
lines.append("| 当前阶段 | 训练动作 | 每组次数 | 组数 | 组间休息 |")
lines.append("|---|---|---:|---:|---:|")
lines.append("| 第一阶段 | 门框划船 | 8~10次 | 6组 | 2分钟 |")
lines.append("| 第二阶段 | 毛巾划船 | 8~12次 | 6组 | 2分钟 |")
lines.append("| 第三阶段 | 反向划船/引体向上 | 接近力竭 | 6组 | 2分钟 |")
lines.append("")
lines.append("### 腿部训练日")
lines.append("")
lines.append("| 当前阶段 | 训练动作 | 每组次数 | 组数 | 组间休息 |")
lines.append("|---|---|---:|---:|---:|")
lines.append("| 第一阶段 | 徒手深蹲 | 15次 | 6组 | 2分钟 |")
lines.append("| 第二阶段 | 保加利亚分腿蹲 | 每侧10次 | 6组 | 2分钟 |")
lines.append("| 第三阶段 | 辅助单腿深蹲/跳跃深蹲 | 每侧8~10次 | 6组 | 2分钟 |")
lines.append("| 固定补充 | 提踵 | 20次 | 5组 | 2分钟 |")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 8周跟练日程表")
lines.append("")

# Generate weekly tables
for week in range(8):
    week_start = week * 7
    week_end = week_start + 7
    lines.append(f"### 第{week+1}周")
    lines.append("")
    lines.append("| 日期 | 星期 | 训练内容 | 执行项目 |")
    lines.append("|---|---|---|---|")
    for i in range(week_start, min(week_end, TOTAL_DAYS)):
        d, wtype = days[i]
        wd = WEEKDAY_CN[d.weekday()]
        lines.append(f"| {d.isoformat()} | {wd} | {CYCLE_CN[wtype]} | {EXECUTIONS[wtype]} |")
    lines.append("")

lines.append("---")
lines.append("")
lines.append("## 打卡记录总览")
lines.append("")
lines.append("| 周次 | 周一 | 周二 | 周三 | 周四 | 周五 | 周六 | 周日 |")
lines.append("|---|---|---|---|---|---|---|---|")
for week in range(8):
    row = [f"第{week+1}周"]
    for weekday in range(7):
        day_index = week * 7 + weekday
        if day_index < TOTAL_DAYS:
            _, wtype = days[day_index]
            short = {"shoulder": "肩", "abs": "腹", "chest": "胸", "back": "背", "legs": "腿", "rest": "休"}[wtype]
            row.append(short)
        else:
            row.append("—")
    lines.append("| " + " | ".join(row) + " |")

lines.append("")
lines.append("---")
lines.append("")
lines.append("## 手臂说明")
lines.append("")
lines.append("无需单独手臂日：")
lines.append("- 二头：划船、引体已充分刺激")
lines.append("- 三头：各类俯卧撑已充分刺激")
lines.append("- 如3个月后仍偏弱，可增加椅子臂屈伸12~15次×4组")
lines.append("")
lines.append("## 饮食与恢复建议")
lines.append("")
lines.append("- 蛋白质：1.6~2.0g/kg体重")
lines.append("- 睡眠：7~9小时")
lines.append("- 饮水：2~3L/天")
lines.append("- 增肌：轻微热量盈余")
lines.append("- 减脂：轻微热量缺口")
lines.append("")
lines.append("> 坚持训练比频繁更换计划更重要。")

# Write markdown
md_path = BASE / "健身日程规划-第三阶段.md"
md_path.write_text("\n".join(lines), encoding="utf-8")
print(f"Markdown written: {md_path}")

# Update workout_plan.json
plan_path = BASE / "data" / "workout_plan.json"
plan = json.loads(plan_path.read_text(encoding="utf-8"))
plan["start_date"] = START.isoformat()
plan["total_days"] = TOTAL_DAYS
plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"JSON updated: {plan_path}")
print(f"Start: {START.isoformat()}, End: {(START + timedelta(days=55)).isoformat()}")
