from flask import Flask, render_template, request, jsonify, redirect, url_for, session, abort, flash
import os
from functools import wraps
from service import load_json, save_json
from datetime import datetime, timezone

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")  # замените в проде

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TASKS = os.path.join(BASE_DIR, "tasks.json")
UPLOADS = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOADS, exist_ok=True)

USERS       = os.path.join(BASE_DIR, "users.json")
COURSES     = os.path.join(BASE_DIR, "courses.json")
COMMENTS    = os.path.join(BASE_DIR, "comments.json")
SUBMISSIONS = os.path.join(BASE_DIR, "submissions.json")

# ----------------- auth helpers -----------------
def _load_users():
    return load_json(USERS, {"users": []})

def get_user_by_id(uid: int):
    data = _load_users()
    for u in data["users"]:
        if u["id"] == uid:
            return u
    return None

def get_user_by_username(username: str):
    data = _load_users()
    for u in data["users"]:
        if u["username"] == username:
            return u
    return None

def current_user():
    uid = session.get("uid")
    return get_user_by_id(uid) if uid else None

def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if not current_user():
            flash("Нужно войти.")
            return redirect(url_for("login", next=request.path))
        return fn(*a, **kw)
    return wrapper

def teacher_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        user = current_user()
        if not user:
            flash("Нужно войти.")
            return redirect(url_for("login", next=request.path))
        if user.get("role") != "teacher":
            abort(403)
        return fn(*a, **kw)
    return wrapper

# ----------------- courses helpers -----------------
def _load_courses():
    return load_json(COURSES, {"courses": []})

def _save_courses(data):
    save_json(COURSES, data)

def _find_course(cid, data=None):
    data = data or _load_courses()
    for c in data["courses"]:
        if c["id"] == cid:
            return c
    return None

# ----------------- task helpers -----------------
def _load_tasks():
    return load_json(TASKS, {"tasks": []})

def _save_tasks(data):
    save_json(TASKS, data)

def _find_task(tid, data=None):
    data = data or _load_tasks()
    for t in data["tasks"]:
        if t["id"] == tid:
            return t
    return None

# ----------------- routes -----------------
@app.route("/")
def index():
    data = _load_courses()
    return render_template("index.html", courses=data["courses"], user=current_user())

# API
@app.post("/api/courses")
@teacher_required
def api_add_course():
    payload = request.get_json(force=True, silent=True) or {}
    title = (payload.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title required"}), 400
    data = _load_courses()
    next_id = max((c["id"] for c in data["courses"]), default=0) + 1
    course = {"id": next_id, "title": title, "description": ""}
    data["courses"].append(course)
    _save_courses(data)
    return jsonify(course), 201

@app.get("/api/courses")
def api_get_courses():
    data = _load_courses()
    return jsonify(data["courses"])

@app.post("/add_course")
@teacher_required
def add_course_form():
    title = (request.form.get("title") or "").strip()
    if not title:
        return redirect(url_for("index"))
    data = _load_courses()
    next_id = max((c["id"] for c in data["courses"]), default=0) + 1
    data["courses"].append({"id": next_id, "title": title, "description": ""})
    _save_courses(data)
    return redirect(url_for("index"))

@app.get("/course/<int:cid>")
def course_view(cid):
    data = _load_courses()
    course = _find_course(cid, data)
    if not course:
        abort(404)
    comments_data = load_json(COMMENTS, {"comments": []})
    comments = [cm for cm in comments_data["comments"] if cm["course_id"] == cid]
    return render_template("course.html", course=course, comments=comments, user=current_user())

@app.post("/course/<int:cid>/comment")
@login_required
def course_comment_create(cid):
    text = (request.form.get("text") or "").strip()
    if not text:
        return redirect(url_for("course_view", cid=cid))
    if not _find_course(cid):
        abort(404)
    data = load_json(COMMENTS, {"comments": []})
    next_id = max((cm["id"] for cm in data["comments"]), default=0) + 1
    data["comments"].append({
        "id": next_id,
        "course_id": cid,
        "user_id": current_user()["id"],
        "text": text
    })
    save_json(COMMENTS, data)
    return redirect(url_for("course_view", cid=cid))

@app.post("/course/<int:cid>/comment/<int:cmid>/delete")
@teacher_required
def course_comment_delete(cid, cmid):
    data = load_json(COMMENTS, {"comments": []})
    before = len(data["comments"])
    data["comments"] = [cm for cm in data["comments"] if not (cm["id"] == cmid and cm["course_id"] == cid)]
    if len(data["comments"]) != before:
        save_json(COMMENTS, data)
    return redirect(url_for("course_view", cid=cid))

@app.get("/course/<int:cid>/edit")
@teacher_required
def course_edit(cid):
    data = _load_courses()
    course = _find_course(cid, data)
    if not course:
        abort(404)
    return render_template("course_edit.html", course=course, user=current_user())

@app.post("/course/<int:cid>/edit")
@teacher_required
def course_edit_save(cid):
    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()
    data = _load_courses()
    course = _find_course(cid, data)
    if not course:
        abort(404)
    if title:
        course["title"] = title
    course["description"] = description
    _save_courses(data)
    return redirect(url_for("course_view", cid=cid))

@app.post("/course/<int:cid>/delete")
@teacher_required
def course_delete(cid):
    data = _load_courses()
    before = len(data["courses"])
    data["courses"] = [c for c in data["courses"] if c["id"] != cid]
    if len(data["courses"]) != before:
        _save_courses(data)
        comments = load_json(COMMENTS, {"comments": []})
        comments["comments"] = [cm for cm in comments["comments"] if cm["course_id"] != cid]
        save_json(COMMENTS, comments)
    return redirect(url_for("index"))

# ----------------- login/logout -----------------
@app.get("/login")
def login():
    return render_template("login.html", user=current_user(), next=request.args.get("next") or "/")

@app.post("/login")
def login_post():
    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "").strip()
    next_url = request.form.get("next") or url_for("index")
    user = get_user_by_username(username)
    if not user or user.get("password") != password:
        flash("Неверные учетные данные")
        return redirect(url_for("login", next=next_url))
    session["uid"] = user["id"]
    flash(f"Вход выполнен: {user['username']}")
    return redirect(next_url)

@app.post("/logout")
def logout():
    session.pop("uid", None)
    flash("Вы вышли из системы")
    return redirect(url_for("index"))

# ========== TASKS ==========
@app.get("/course/<int:cid>/tasks")
@login_required
def task_list(cid):
    course = _find_course(cid)
    if not course:
        abort(404)
    tasks_data = _load_tasks()
    course_tasks = [t for t in tasks_data["tasks"] if t["course_id"] == cid]
    return render_template("tasks.html", course=course, tasks=course_tasks, user=current_user())

@app.get("/course/<int:cid>/task/add")
@teacher_required
def task_add_form(cid):
    course = _find_course(cid)
    if not course:
        abort(404)
    return render_template("task_add.html", course=course, user=current_user())

@app.post("/course/<int:cid>/task/add")
@teacher_required
def task_add(cid):
    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip()
    deadline = (request.form.get("deadline") or "").strip()
    data = _load_tasks()
    next_id = max((t["id"] for t in data["tasks"]), default=0) + 1
    task = {
        "id": next_id,
        "course_id": cid,
        "title": title,
        "description": description,
        "deadline": deadline
    }
    data["tasks"].append(task)
    _save_tasks(data)
    flash("Задание добавлено")
    return redirect(url_for("task_list", cid=cid))

@app.get("/course/<int:cid>/task/<int:tid>")
@login_required
def task_view(cid, tid):
    course = _find_course(cid)
    task = _find_task(tid)
    if not course or not task:
        abort(404)
    subs = load_json(SUBMISSIONS, {"submissions": []})
    answers = [s for s in subs["submissions"] if s["task_id"] == tid]
    user = current_user()
    user_sub = next((s for s in answers if s["user_id"] == user["id"]), None)
    return render_template("task_view.html", course=course, task=task, answers=answers, user=user, user_sub=user_sub)

@app.post("/course/<int:cid>/task/<int:tid>/submit")
@login_required
def task_submit(cid, tid):
    course = _find_course(cid)
    task = _find_task(tid)
    if not course or not task:
        abort(404)
    if "file" not in request.files:
        flash("Файл не выбран")
        return redirect(url_for("task_view", cid=cid, tid=tid))
    file = request.files["file"]
    if file.filename == "":
        flash("Файл не выбран")
        return redirect(url_for("task_view", cid=cid, tid=tid))
    filename = f"{current_user()['id']}_{tid}_{file.filename}"
    path = os.path.join(UPLOADS, filename)
    file.save(path)

    data = load_json(SUBMISSIONS, {"submissions": []})
    data["submissions"] = [s for s in data["submissions"] if not (s["user_id"] == current_user()["id"] and s["task_id"] == tid)]
    data["submissions"].append({
        "user_id": current_user()["id"],
        "task_id": tid,
        "filename": filename
    })
    save_json(SUBMISSIONS, data)
    flash("Ответ отправлен!")
    return redirect(url_for("task_view", cid=cid, tid=tid))

@app.get("/course/<int:cid>/task/<int:tid>/grade/<int:uid>")
@teacher_required
def grade_form(cid, tid, uid):
    course = _find_course(cid)
    task = _find_task(tid)
    if not course or not task:
        abort(404)
    subs = load_json(SUBMISSIONS, {"submissions": []})
    sub = next((s for s in subs["submissions"] if s["task_id"] == tid and s["user_id"] == uid), None)
    if not sub:
        abort(404)
    return render_template("task_grade.html", course=course, task=task, sub=sub, user=current_user())

@app.post("/course/<int:cid>/task/<int:tid>/grade/<int:uid>")
@teacher_required
def grade_save(cid, tid, uid):
    course = _find_course(cid)
    task = _find_task(tid)
    if not course or not task:
        abort(404)

    grade_raw = (request.form.get("grade") or "").strip()
    feedback = (request.form.get("feedback") or "").strip()

    grade = None
    if grade_raw != "":
        try:
            grade = int(grade_raw)
        except ValueError:
            flash("Оценка должна быть целым числом")
            return redirect(url_for("grade_form", cid=cid, tid=tid, uid=uid))
        if grade < 0 or grade > 100:
            flash("Оценка должна быть в диапазоне 0–100")
            return redirect(url_for("grade_form", cid=cid, tid=tid, uid=uid))

    subs = load_json(SUBMISSIONS, {"submissions": []})
    found = False
    for s in subs["submissions"]:
        if s["task_id"] == tid and s["user_id"] == uid:
            s["grade"] = grade
            s["feedback"] = feedback
            s["graded_by"] = current_user()["id"]
            s["graded_at"] = datetime.now(timezone.utc).isoformat()
            found = True
            break

    if not found:
        abort(404)

    save_json(SUBMISSIONS, subs)
    flash("Оценка сохранена")
    return redirect(url_for("task_view", cid=cid, tid=tid))

# ---------- Профиль ----------
@app.get("/profile")
@login_required
def profile():
    user = current_user()

    courses_data = _load_courses()
    tasks_data = _load_tasks()
    subs_data = load_json(SUBMISSIONS, {"submissions": []})

    course_by_id = {c["id"]: c for c in courses_data["courses"]}
    tasks_by_course = {}
    for t in tasks_data["tasks"]:
        tasks_by_course.setdefault(t["course_id"], []).append(t)

    student_rows = []
    if user["role"] == "student":
        for s in subs_data["submissions"]:
            if s["user_id"] != user["id"]:
                continue

            task = next((t for t in tasks_data["tasks"] if t["id"] == s["task_id"]), None)
            if not task:
                continue
            course = course_by_id.get(task["course_id"])
            student_rows.append({
                "course": course["title"] if course else f"course#{task['course_id']}",
                "task": task["title"],
                "filename": s.get("filename"),
                "grade": s.get("grade"),
                "feedback": s.get("feedback"),
                "task_id": task["id"],
                "course_id": task["course_id"],
            })

        graded = [r["grade"] for r in student_rows if isinstance(r.get("grade"), int)]
        avg_grade = round(sum(graded) / len(graded), 2) if graded else None
    else:
        avg_grade = None

    teacher_courses = []
    if user["role"] == "teacher":
        for c in courses_data["courses"]:
            course_tasks = tasks_by_course.get(c["id"], [])

            course_task_ids = {t["id"] for t in course_tasks}
            course_subs = [s for s in subs_data["submissions"] if s["task_id"] in course_task_ids]
            pending = [s for s in course_subs if s.get("grade") is None]
            teacher_courses.append({
                "course": c,
                "tasks_count": len(course_tasks),
                "subs_count": len(course_subs),
                "pending_count": len(pending),
                "pending": pending[:10],
            })

    return render_template(
        "profile.html",
        user=user,
        student_rows=student_rows,
        avg_grade=avg_grade,
        teacher_courses=teacher_courses,
        username=lambda uid: get_user_by_id(uid)["username"] if get_user_by_id(uid) else f"user#{uid}",
    )

@app.context_processor
def utility_processor():
    return dict(load_json=load_json)

@app.context_processor
def inject_utils():
    def username(uid):
        u = get_user_by_id(uid)
        return u["username"] if u else f"user#{uid}"
    return {"username": username}

if __name__ == "__main__":
    app.run(debug=True)