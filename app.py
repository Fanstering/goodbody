from __future__ import annotations

import json
import threading
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RECORD_FILE = DATA_DIR / "checkin_record.json"

app = Flask(__name__)


def load_json(name: str) -> dict:
    with (DATA_DIR / name).open("r", encoding="utf-8") as f:
        return json.load(f)


def load_records() -> dict:
    if not RECORD_FILE.exists():
        return {"records": {}}
    with RECORD_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_records(records: dict) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    with RECORD_FILE.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def iter_program_days(plan: dict):
    start = date.fromisoformat(plan["start_date"])
    cycle = plan["cycle"]
    for offset in range(plan["total_days"]):
        current = start + timedelta(days=offset)
        yield current.isoformat(), cycle[offset % len(cycle)]


def build_schedule() -> dict:
    plan = load_json("workout_plan.json")
    exercise_options = load_json("exercise_options.json")
    schedule = {}
    for day_key, workout_type in iter_program_days(plan):
        options = []
        workout = plan["workouts"][workout_type]
        for option_id in workout["options"]:
            option = exercise_options[option_id]
            options.append(
                {
                    "id": option_id,
                    "title": option["title"],
                    "stage": option["stage"],
                    "summary": option["summary"],
                }
            )
        schedule[day_key] = {
            "workout_type": workout_type,
            "title": workout["title"],
            "options": options,
        }
    return schedule


def day_completed(record: dict) -> bool:
    return bool(record.get("completed_options"))


@app.get("/")
def index():
    plan = load_json("workout_plan.json")
    return render_template("index.html", program_name=plan["program_name"])


@app.get("/api/config")
def config():
    plan = load_json("workout_plan.json")
    return jsonify(
        {
            "program_name": plan["program_name"],
            "start_date": plan["start_date"],
            "total_days": plan["total_days"],
        }
    )


@app.get("/api/schedule")
def month_schedule():
    year = int(request.args.get("year", date.today().year))
    month = int(request.args.get("month", date.today().month))
    schedule = build_schedule()
    records = load_records()["records"]
    month_days = {}
    for day_key, day_plan in schedule.items():
        current = date.fromisoformat(day_key)
        if current.year == year and current.month == month:
            record = records.get(day_key, {})
            month_days[day_key] = {
                "has_workout": bool(day_plan["options"]),
                "completed": day_completed(record),
                "workout_title": day_plan["title"],
            }
    return jsonify({"month_days": month_days})


@app.get("/api/day")
def day_detail():
    day_key = request.args.get("date", date.today().isoformat())
    schedule = build_schedule()
    if day_key not in schedule:
        return jsonify(
            {
                "date": day_key,
                "day_type": "rest",
                "title": "无训练安排",
                "pending": [],
                "completed": [],
            }
        )

    records = load_records()["records"]
    completed_ids = set(records.get(day_key, {}).get("completed_options", []))
    options = schedule[day_key]["options"]
    if not options:
        return jsonify(
            {
                "date": day_key,
                "day_type": "rest",
                "title": schedule[day_key]["title"],
                "pending": [],
                "completed": [],
            }
        )
    pending = [item for item in options if item["id"] not in completed_ids]
    completed = [item for item in options if item["id"] in completed_ids]
    return jsonify(
        {
            "date": day_key,
            "day_type": "training",
            "title": schedule[day_key]["title"],
            "pending": pending,
            "completed": completed,
        }
    )


@app.post("/api/checkin")
def checkin():
    payload = request.get_json(force=True)
    day_key = payload["date"]
    option_id = payload["option_id"]
    records = load_records()
    day_record = records["records"].setdefault(day_key, {"completed_options": []})
    if option_id not in day_record["completed_options"]:
        day_record["completed_options"].append(option_id)
    day_record["checkin_time"] = datetime.now().isoformat(timespec="seconds")
    save_records(records)
    return jsonify({"success": True, "completed": True})


@app.post("/api/uncheck")
def uncheck():
    payload = request.get_json(force=True)
    day_key = payload["date"]
    option_id = payload["option_id"]
    records = load_records()
    day_record = records["records"].setdefault(day_key, {"completed_options": []})
    day_record["completed_options"] = [
        item for item in day_record.get("completed_options", []) if item != option_id
    ]
    save_records(records)
    return jsonify({"success": True, "completed": day_completed(day_record)})


@app.get("/api/exercise")
def exercise_detail():
    option_id = request.args["id"]
    exercise_options = load_json("exercise_options.json")
    option = exercise_options.get(option_id)
    if not option:
        return jsonify({"error": "not found"}), 404
    return jsonify(option | {"id": option_id})


@app.get("/api/stats")
def stats():
    schedule = build_schedule()
    records = load_records()["records"]
    today = date.today()
    total_checkin_days = sum(1 for record in records.values() if day_completed(record))
    week_start = today - timedelta(days=today.weekday())
    week_days = [(week_start + timedelta(days=i)).isoformat() for i in range(7)]
    week_total = sum(
        1 for day_key in week_days if day_key in schedule and schedule[day_key]["options"]
    )
    week_completed = sum(
        1 for day_key in week_days if day_completed(records.get(day_key, {}))
    )

    streak = 0
    cursor = today
    while True:
        day_key = cursor.isoformat()
        if day_key not in schedule or not day_completed(records.get(day_key, {})):
            break
        streak += 1
        cursor -= timedelta(days=1)

    return jsonify(
        {
            "total_checkin_days": total_checkin_days,
            "week_completed": week_completed,
            "week_total": week_total,
            "current_streak": streak,
        }
    )


if __name__ == "__main__":
    # 延迟2秒后自动用默认浏览器打开页面
    def _open_browser():
        webbrowser.open("http://127.0.0.1:5000")
    threading.Timer(2.0, _open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
