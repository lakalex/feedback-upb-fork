import sqlite3
import json
import os
import glob

DB_NAME = "moodle_analytics.db"
JSON_DIR = "."

MAPPING = {
    "prof_know": ("Cadrul didactic stăpânește bine domeniul", True),
    "prof_behave": ("Comportamentul cadrului didactic față de studenți", True),
    "assist_know": ("Cadrul didactic stăpânește bine domeniul", True),
    "assist_behave": ("Comportamentul cadrului didactic față de studenți", True),
    "part_percent": ("Numarul aproximativ de activitati", False),
    "prof_teach": ("Metoda de expunere", True),
    "prof_interact": ("Cursul a stimulat discutiile", True),
    "assist_teach": ("sprijinit activitatea individuala", True),
    "assist_interact": ("Aplicatiile au stimulat discutiile", True),
    "eval_overall": ("Evaluarea dumneavoastră generală", True),
    "expected_grade": ("Care este nota la care va asteptati", False),
    "load": ("Incarcarea generala", True),
    "equipment": ("Dotarea (locatie", True),
    "lecture_doc": (
        "Materialele didactice puse la dispozitie sunt suficiente pentru intelegerea cursului",
        True,
    ),
    "lab_doc": ("suficiente pentru intelegerea aplicatiilor", True),
    "assign_time": ("Estimati numarul mediu de ore", False),
    "assign_diff": ("dificultatea temelor", True),
    "assign_useful": ("ajutat la intelegerea materiei", True),
    "positive_text": ("aspectele pozitive", False),
    "negative_text": ("trebuie imbunatatit", False),
    "difficulty_text": ("dificultatea principala", False),
    "other_text": ("Alte comentarii", False),
}


def get_db():
    return sqlite3.connect(DB_NAME)


def load_json(filename):
    path = os.path.join(JSON_DIR, filename)
    print(filename)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return None


def parse_val(raw, invert=False):
    try:
        val = int(raw)
    except (ValueError, TypeError):
        return None

    if invert:
        if 1 <= val <= 5:
            return 6 - val
    return val


def migrate_cat(conn):
    data = load_json("categories.json")
    if not data:
        return

    c = conn.cursor()
    count = 0
    for cat in data:
        try:
            parent_id = cat["parent"]
            if parent_id == 0:
                parent_id = None

            c.execute(
                """INSERT OR REPLACE INTO categories
                        (category_id, name, parent_id, path, depth, sortorder)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    cat["id"],
                    cat["name"],
                    parent_id,
                    cat["path"],
                    cat["depth"],
                    cat.get("sortorder"),
                ),
            )
            count += 1
        except Exception as e:
            print(f"Eroare: {e}.")

    conn.commit()
    print(f" Am salvat {count} categorii")


def migrate_cours(conn):
    courses_data = load_json("courses.json")

    c = conn.cursor()
    count = 0

    for course in courses_data:
        course_id = course["id"]
        cat_id = course.get("categoryid")

        try:
            c.execute(
                """INSERT OR REPLACE INTO courses
                         (course_id, shortname, fullname, startdate, enddate, category_id)
                         VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    course_id,
                    course["shortname"],
                    course["fullname"],
                    course["startdate"],
                    course["enddate"],
                    cat_id,
                ),
            )
            count += 1
        except Exception as e:
            print(f"Eroare curs {course_id}, {cat_id}, {e}")

    conn.commit()
    print(f"Am salvat {count} cursuri")


def migrate_feedbacks(conn):
    all_files = glob.glob(os.path.join(JSON_DIR, "*.json"))
    exclude = [
        "categories.json",
        "courses.json",
        "courses4categories.json",
        "feedbacks.json",
    ]
    feedback_files = [f for f in all_files if os.path.basename(f) not in exclude]

    c = conn.cursor()

    for filepath in feedback_files:
        filename = os.path.basename(filepath)

        try:
            instance_id = int(filename.split(".")[0])
        except ValueError:
            continue

        data = load_json(filename)
        attempts = data["anonattempts"]

        for att in attempts:
            row_data = {
                "attempt_id": att["id"],
                "instance_id": instance_id,
                "prof_name": None,
                "assist_name": None,
                "eval_overall": None,
                "expected_grade": None,
                "load": None,
                "equipment": None,
                "part_percent": None,
                "prof_know": None,
                "prof_teach": None,
                "prof_behave": None,
                "lecture_doc": None,
                "assist_know": None,
                "assist_teach": None,
                "assist_interact": None,
                "assist_behave": None,
                "lab_doc": None,
                "assign_time": None,
                "assign_diff": None,
                "assign_useful": None,
                "positive_text": None,
                "negative_text": None,
                "difficulty_text": None,
                "other_text": None,
            }
            know_count = 0
            behave_count = 0

            for r in att["responses"]:
                q_text = r["name"]
                raw = r["rawval"]
                print_val = r["printval"]

                if "Teacher" in q_text:
                    row_data["prof_name"] = print_val
                elif "Laboratory" in q_text:
                    row_data["assist_name"] = print_val

                for db_col, (keyword, do_invert) in MAPPING.items():
                    if keyword in q_text:
                        if db_col not in [
                            "prof_know",
                            "assist_know",
                            "prof_behave",
                            "assist_behave",
                        ]:
                            row_data[db_col] = parse_val(raw, do_invert)

                if "Cadrul didactic stăpânește bine" in q_text:
                    val = parse_val(raw, True)
                    if know_count == 0:
                        row_data["prof_know"] = val
                    else:
                        row_data["assist_know"] = val
                    know_count += 1

                if "Comportamentul cadrului didactic" in q_text:
                    val = parse_val(raw, True)
                    if behave_count == 0:
                        row_data["prof_behave"] = val
                    else:
                        row_data["assist_behave"] = val
                    behave_count += 1

            cols = ", ".join(row_data.keys())
            placehld = ", ".join(["?"] * len(row_data))
            values = list(row_data.values())

            c.execute(
                f"INSERT OR REPLACE INTO feedback_responses ({cols}) VALUES ({placehld})",
                values,
            )

        conn.commit()
        print("GATA")


def migrate_instances(conn):
    data = load_json("feedbacks.json")

    c = conn.cursor()
    count = 0

    for item in data:
        inst_id = item["id"]
        course_id = item["course"]
        name = item.get("name", "Feedback fara ")
        anon = item.get("anonymous")

        c.execute(
            """INSERT OR REPLACE INTO feedback_instances
                     (instance_id, course_id, name, anonymous)
                	 VALUES (?, ?, ?, ?)""",
            (inst_id, course_id, name, anon),
        )

    conn.commit()


if __name__ == "__main__":
    conn = get_db()
    migrate_cat(conn)
    migrate_cours(conn)
    migrate_instances(conn)
    migrate_feedbacks(conn)
    conn.close()
