# -*- coding: utf-8 -*-
"""健身日志 App - 数据层（SQLite）"""
import sqlite3
import os
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fitlog.db")


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c


def init_db():
    c = conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS workouts (
        d TEXT PRIMARY KEY,
        aerobic TEXT,
        state INTEGER,
        fatigue INTEGER
    );

    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_date TEXT NOT NULL,
        ex_name TEXT NOT NULL,
        position INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS sets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id INTEGER NOT NULL,
        ex_name TEXT NOT NULL,
        position INTEGER DEFAULT 0,
        weight REAL,
        reps INTEGER,
        rpe REAL,
        done INTEGER DEFAULT 0,
        FOREIGN KEY (workout_id) REFERENCES exercises(id)
    );

    CREATE TABLE IF NOT EXISTS foods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        d TEXT NOT NULL,
        meal TEXT,
        name TEXT,
        kcal REAL,
        carb REAL,
        protein REAL,
        fat REAL,
        weight REAL
    );

    CREATE TABLE IF NOT EXISTS body (
        d TEXT PRIMARY KEY,
        weight REAL,
        bodyfat REAL
    );

    CREATE TABLE IF NOT EXISTS cycles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        start_date TEXT,
        end_date TEXT,
        note TEXT
    );
    """)
    c.commit()
    c.close()


def today_str():
    return date.today().isoformat()


def ensure_workout(d=None):
    if d is None:
        d = today_str()
    c = conn()
    c.execute("INSERT OR IGNORE INTO workouts (d, aerobic, state, fatigue) VALUES (?,?,?,?)",
              (d, "", 0, 0))
    c.commit()
    c.close()


def get_workout(d=None):
    if d is None:
        d = today_str()
    c = conn()
    row = c.execute("SELECT * FROM workouts WHERE d=?", (d,)).fetchone()
    c.close()
    return dict(row) if row else None


def save_workout(d, aerobic, state, fatigue):
    c = conn()
    c.execute("INSERT OR IGNORE INTO workouts (d, aerobic, state, fatigue) VALUES (?,?,?,?)",
              (d, "", 0, 0))
    c.execute("UPDATE workouts SET aerobic=?, state=?, fatigue=? WHERE d=?",
              (aerobic, state, fatigue, d))
    c.commit()
    c.close()


def add_exercise(d, ex_name, position=0):
    c = conn()
    c.execute("INSERT INTO exercises (workout_date, ex_name, position) VALUES (?,?,?)",
              (d, ex_name, position))
    c.commit()
    eid = c.execute("SELECT id FROM exercises WHERE workout_date=? AND ex_name=? ORDER BY id DESC LIMIT 1",
                    (d, ex_name)).fetchone()["id"]
    c.close()
    return eid


def get_exercises(d):
    c = conn()
    rows = c.execute("SELECT * FROM exercises WHERE workout_date=? ORDER BY position, id", (d,)).fetchall()
    c.close()
    return [dict(r) for r in rows]


def add_set(workout_id, ex_name, weight, reps, rpe=0, position=0):
    c = conn()
    c.execute("INSERT INTO sets (workout_id, ex_name, position, weight, reps, rpe, done) VALUES (?,?,?,?,?,?,?)",
              (workout_id, ex_name, position, weight, reps, rpe, 0))
    c.commit()
    c.close()


def get_sets(workout_id):
    c = conn()
    rows = c.execute("SELECT * FROM sets WHERE workout_id=? ORDER BY position, id", (workout_id,)).fetchall()
    c.close()
    return [dict(r) for r in rows]


def recent_sets_for_exercise(ex_name, n=3, before_date=None):
    c = conn()
    if before_date:
        rows = c.execute(
            "SELECT s.* FROM sets s JOIN exercises e ON s.workout_id=e.id "
            "WHERE s.ex_name=? AND e.workout_date<? ORDER BY e.workout_date DESC, s.id DESC LIMIT ?",
            (ex_name, before_date, n)).fetchall()
    else:
        rows = c.execute(
            "SELECT s.* FROM sets s JOIN exercises e ON s.workout_id=e.id "
            "WHERE s.ex_name=? ORDER BY e.workout_date DESC, s.id DESC LIMIT ?",
            (ex_name, n)).fetchall()
    c.close()
    return [dict(r) for r in rows]


def add_food(d, meal, name, kcal, carb, protein, fat, weight):
    c = conn()
    c.execute("INSERT INTO foods (d, meal, name, kcal, carb, protein, fat, weight) VALUES (?,?,?,?,?,?,?,?)",
              (d, meal, name, kcal, carb, protein, fat, weight))
    c.commit()
    c.close()


def get_foods(d):
    c = conn()
    rows = c.execute("SELECT * FROM foods WHERE d=? ORDER BY id", (d,)).fetchall()
    c.close()
    return [dict(r) for r in rows]


def delete_food(fid):
    c = conn()
    c.execute("DELETE FROM foods WHERE id=?", (fid,))
    c.commit()
    c.close()


def get_body(d=None):
    if d is None:
        d = today_str()
    c = conn()
    row = c.execute("SELECT * FROM body WHERE d=?", (d,)).fetchone()
    c.close()
    return dict(row) if row else None


def save_body(d, weight, bodyfat):
    c = conn()
    c.execute("INSERT OR REPLACE INTO body (d, weight, bodyfat) VALUES (?,?,?)", (d, weight, bodyfat))
    c.commit()
    c.close()


def get_body_history(days=30):
    c = conn()
    start = (date.today() - timedelta(days=days)).isoformat()
    rows = c.execute("SELECT * FROM body WHERE d>=? ORDER BY d", (start,)).fetchall()
    c.close()
    return [dict(r) for r in rows]


def get_date_range_stats(start_date, end_date):
    c = conn()
    rows = c.execute(
        "SELECT d, SUM(kcal) as total_kcal, SUM(carb) as total_carb, "
        "SUM(protein) as total_protein, SUM(fat) as total_fat "
        "FROM foods WHERE d>=? AND d<=? GROUP BY d ORDER BY d",
        (start_date, end_date)).fetchall()
    c.close()
    return [dict(r) for r in rows]


def add_cycle(name, start_date, end_date, note=""):
    c = conn()
    c.execute("INSERT INTO cycles (name, start_date, end_date, note) VALUES (?,?,?,?)",
              (name, start_date, end_date, note))
    c.commit()
    c.close()


def get_cycles():
    c = conn()
    rows = c.execute("SELECT * FROM cycles ORDER BY id DESC").fetchall()
    c.close()
    return [dict(r) for r in rows]


def delete_cycle(cid):
    c = conn()
    c.execute("DELETE FROM cycles WHERE id=?", (cid,))
    c.commit()
    c.close()


def calc_tdee(weight, bodyfat_pct, activity_factor, goal):
    if weight and bodyfat_pct and bodyfat_pct > 0:
        lbm = weight * (1 - bodyfat_pct / 100)
        fm = weight - lbm
        bmr = 370 + 21.6 * lbm
    elif weight:
        bmr = 22 * weight
    else:
        bmr = 1500
    tdee = bmr * activity_factor
    if goal == "cut":
        target = tdee - 500
    elif goal == "bulk":
        target = tdee + 300
    else:
        target = tdee
    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "target": round(target),
        "protein_g": round(weight * 2.0) if weight else 0,
        "carb_g": round(target * 0.4 / 4) if target else 0,
        "fat_g": round(target * 0.25 / 9) if target else 0,
    }


init_db()
