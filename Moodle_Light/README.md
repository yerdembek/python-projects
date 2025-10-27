# 🎓 Moodle Light

Moodle Light is a Python + Flask educational project that represents a simplified version of the distance learning platform.

It implements basic Moodle features: courses, assignments, comments, user roles, and a rating system.

---

## 🚀 Features

### 👤 Authorization and Roles
- User login and logout via a JSON database (users.json)
- Two roles:
- Teacher — can create, edit, and delete courses and assignments, as well as grade students
- Student — can view courses, submit assignments, and receive grades

---

### 📚 Courses
- List of all courses
- Add, edit, and delete courses (teacher only)
- Discussion (comments) under each course

---

### 📝 Assignments
- Assignment creation by the teacher
- Student upload of solutions (files)
- View all submitted solutions by the teacher
- Assigning grades and providing feedback
- Storing all data in tasks.json and submissions.json

---

### ⭐ User Profile
- Student: Sees their submitted assignments, grades, and GPA
- Teacher: sees their courses, the number of assignments, and students' unprocessed solutions

---

### 🛠️ Commands for correct operation and general information about the data
1. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
.venv\Scripts\activate # (Windows)
source .venv/bin/activate # (Linux/Mac)

pip install -r requirements.txt
```
2. Start the server:
```bash
puthon app.py
```
3. Open in browser:
```bash
http://127/0/0/1:5000
```
4. Test users:
```bash
teacher 1234
student 1234
```
---
### 📄 License

This project is for educational purposes.
Feel free to use, improve, and modify it to suit your needs.

---

💡 Author: Beknur Erdembek \
📅 Version: 1.0 \
🛠️ Technologies: Python 3, Flask, HTML, CSS, JSON