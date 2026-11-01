"""
StudySpark – Smart Task & Study Planner
=======================================
A modern, colorful student productivity web application built with Python & Flask.
Designed for college academic evaluation with clean, beginner-friendly code
and real Data Structures & Algorithms (DSA) implementations.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import json
import os

# Import DSA functions from dsa_operations.py
from dsa_operations import (
    linear_search_task,
    bubble_sort_tasks,
    build_task_hash_map,
    get_smart_recommendation,
    undo_stack,
    get_task_counts,
    filter_tasks_by_category
)

app = Flask(__name__)
app.secret_key = "studyspark-student-secret-key-2026"

# File paths for local JSON storage
USERS_FILE = os.path.join("data", "users.json")
TASKS_FILE = os.path.join("data", "tasks.json")


# =====================================================================
# HELPER FUNCTIONS (JSON Storage & Login Check)
# =====================================================================
def load_json(filepath):
    """Safely loads data from a JSON file. Returns empty list if missing or corrupted."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_json(filepath, data):
    """Saves data to a JSON file with clean indentation."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_current_user():
    """Returns the currently logged-in user dictionary from session, or None."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    users = load_json(USERS_FILE)
    for u in users:
        if u.get("id") == user_id:
            return u
    return None


def get_user_tasks(user_id):
    """Fetches all tasks belonging exclusively to the specified user ID."""
    all_tasks = load_json(TASKS_FILE)
    # DSA Concept: List comprehension / filtering
    return [t for t in all_tasks if t.get("user_id") == user_id]


# Context processor to make current user available in all templates
@app.context_processor
def inject_user():
    return {
        "current_user": get_current_user(),
        "today_date": date.today().strftime("%A, %b %d, %Y"),
        "today_str": date.today().strftime("%Y-%m-%d"),
        "can_undo": not undo_stack.is_empty()
    }


# =====================================================================
# AUTHENTICATION ROUTES (Signup, Login, Logout)
# =====================================================================
@app.route("/")
def index():
    """Landing homepage for StudySpark. If logged in, users can jump to dashboard."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Registers a new student account."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Input validations
        if not (name and email and username and password):
            flash("Please fill in all required fields.", "error")
            return render_template("signup.html")

        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "error")
            return render_template("signup.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("signup.html")

        users = load_json(USERS_FILE)

        # Check if username or email is already taken
        for u in users:
            if u.get("username") == username:
                flash("Username is already taken. Please choose another.", "error")
                return render_template("signup.html")
            if u.get("email") == email:
                flash("An account with this email already exists.", "error")
                return render_template("signup.html")

        # Create new user with secure password hash
        new_id = max([u.get("id", 0) for u in users], default=0) + 1
        new_user = {
            "id": new_id,
            "name": name,
            "username": username,
            "email": email,
            "password": generate_password_hash(password),
            "created_at": date.today().strftime("%Y-%m-%d")
        }

        users.append(new_user)
        save_json(USERS_FILE, users)

        # Automatically log in the student
        session["user_id"] = new_user["id"]
        session["username"] = new_user["username"]
        session["name"] = new_user["name"]

        flash(f"Welcome to StudySpark, {name}! Your account has been created.", "success")
        return redirect(url_for("dashboard"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Logs in an existing student."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        login_input = request.form.get("login_input", "").strip().lower()
        password = request.form.get("password", "")

        if not login_input or not password:
            flash("Please enter both username/email and password.", "error")
            return render_template("login.html")

        users = load_json(USERS_FILE)
        matched_user = None

        # Search for matching user by username or email
        for u in users:
            if u.get("username") == login_input or u.get("email") == login_input:
                matched_user = u
                break

        if matched_user and check_password_hash(matched_user.get("password", ""), password):
            session["user_id"] = matched_user["id"]
            session["username"] = matched_user["username"]
            session["name"] = matched_user["name"]
            flash(f"Welcome back, {matched_user['name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials. Please check your username and password.", "error")
            return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Logs out the user and clears the session."""
    session.clear()
    flash("You have been successfully logged out.", "success")
    return redirect(url_for("login"))


# =====================================================================
# DASHBOARD ROUTE
# =====================================================================
@app.route("/dashboard")
def dashboard():
    """Student productivity dashboard featuring stats, DSA recommendations, and today's overview."""
    if "user_id" not in session:
        flash("Please log in to access your dashboard.", "error")
        return redirect(url_for("login"))

    user_tasks = get_user_tasks(session["user_id"])

    # 1. DSA Concept: Single pass traversal for statistics
    stats = get_task_counts(user_tasks)

    # 2. DSA Concept: Priority Queue (Heap) for smart recommendation
    recommendation = get_smart_recommendation(user_tasks)

    # 3. Filtered subsets for Today's Overview
    today_tasks = filter_tasks_by_category(user_tasks, "today")
    overdue_tasks = filter_tasks_by_category(user_tasks, "overdue")
    upcoming_tasks = filter_tasks_by_category(user_tasks, "upcoming")
    
    # Recently completed (last 4 completed tasks)
    completed_tasks = [t for t in user_tasks if t.get("done", False)]
    recent_completed = sorted(completed_tasks, key=lambda x: x.get("id", 0), reverse=True)[:4]

    # Greeting based on time of day
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good Morning"
    elif hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    return render_template(
        "dashboard.html",
        stats=stats,
        recommendation=recommendation,
        today_tasks=today_tasks,
        overdue_tasks=overdue_tasks,
        upcoming_tasks=upcoming_tasks,
        recent_completed=recent_completed,
        greeting=greeting
    )


# =====================================================================
# TASK MANAGEMENT ROUTES (CRUD + DSA Sorting & Filtering)
# =====================================================================
@app.route("/tasks")
def tasks_view():
    """Complete Task Management page with search, filters, and sorting."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_tasks = get_user_tasks(session["user_id"])

    filter_type = request.args.get("filter", "all")
    sort_by = request.args.get("sort", "priority")

    # 1. DSA Concept: Filtering using conditions
    filtered_tasks = filter_tasks_by_category(user_tasks, filter_type)

    # 2. DSA Concept: Bubble Sort algorithm implementation
    sorted_tasks = bubble_sort_tasks(filtered_tasks, sort_by=sort_by)

    stats = get_task_counts(user_tasks)

    return render_template(
        "tasks.html",
        tasks=sorted_tasks,
        current_filter=filter_type,
        current_sort=sort_by,
        stats=stats
    )


@app.route("/tasks/add", methods=["POST"])
def add_task():
    """Adds a new study task for the logged-in student."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()
    description = request.form.get("description", "").strip()
    due_date = request.form.get("due_date", "")
    priority = request.form.get("priority", "2")
    estimated_hours = request.form.get("estimated_hours", "1")

    if not title:
        flash("Task title cannot be empty.", "error")
        return redirect(request.referrer or url_for("tasks_view"))

    all_tasks = load_json(TASKS_FILE)
    new_id = max([t.get("id", 0) for t in all_tasks], default=0) + 1

    new_task = {
        "id": new_id,
        "user_id": session["user_id"],
        "title": title,
        "subject": subject if subject else "General",
        "description": description,
        "due_date": due_date if due_date else date.today().strftime("%Y-%m-%d"),
        "priority": priority,
        "estimated_hours": float(estimated_hours) if estimated_hours else 1.0,
        "done": False,
        "is_highlighted": False,
        "created_at": date.today().strftime("%Y-%m-%d")
    }

    all_tasks.append(new_task)
    save_json(TASKS_FILE, all_tasks)

    flash(f"Task '{title}' added successfully!", "success")
    return redirect(request.referrer or url_for("tasks_view"))


@app.route("/tasks/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    """Edits an existing task."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    all_tasks = load_json(TASKS_FILE)

    # DSA Concept: Linear Search to locate the task
    task, index = linear_search_task(all_tasks, task_id)

    # Security check: ensure task exists and belongs to current user
    if task and task.get("user_id") == session["user_id"]:
        task["title"] = request.form.get("title", task["title"]).strip()
        task["subject"] = request.form.get("subject", task["subject"]).strip()
        task["description"] = request.form.get("description", task["description"]).strip()
        task["due_date"] = request.form.get("due_date", task["due_date"])
        task["priority"] = request.form.get("priority", task["priority"])
        
        est = request.form.get("estimated_hours")
        if est:
            try:
                task["estimated_hours"] = float(est)
            except ValueError:
                pass

        all_tasks[index] = task
        save_json(TASKS_FILE, all_tasks)
        flash("Task updated successfully!", "success")
    else:
        flash("Task not found or access denied.", "error")

    return redirect(request.referrer or url_for("tasks_view"))


@app.route("/tasks/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    """Toggles task completion status and records action in Stack for Undo."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    all_tasks = load_json(TASKS_FILE)
    task, index = linear_search_task(all_tasks, task_id)

    if task and task.get("user_id") == session["user_id"]:
        # Record action in Undo Stack (DSA Concept: LIFO Stack)
        undo_stack.push({
            "type": "toggle",
            "task_id": task_id,
            "previous_state": task.get("done", False)
        })

        task["done"] = not task.get("done", False)
        all_tasks[index] = task
        save_json(TASKS_FILE, all_tasks)

        status_msg = "completed! Great job! 🎉" if task["done"] else "marked as pending."
        flash(f"Task '{task['title']}' {status_msg}", "success")
    else:
        flash("Task not found.", "error")

    return redirect(request.referrer or url_for("tasks_view"))


@app.route("/tasks/star/<int:task_id>", methods=["POST"])
def star_task(task_id):
    """Toggles the highlighted/starred status of a task."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    all_tasks = load_json(TASKS_FILE)
    task, index = linear_search_task(all_tasks, task_id)

    if task and task.get("user_id") == session["user_id"]:
        task["is_highlighted"] = not task.get("is_highlighted", False)
        all_tasks[index] = task
        save_json(TASKS_FILE, all_tasks)
        
        action_text = "highlighted" if task["is_highlighted"] else "unhighlighted"
        flash(f"Task {action_text}!", "success")
    else:
        flash("Task not found.", "error")

    return redirect(request.referrer or url_for("tasks_view"))


@app.route("/tasks/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    """Deletes a task and pushes it onto the Undo Stack."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    all_tasks = load_json(TASKS_FILE)
    task, index = linear_search_task(all_tasks, task_id)

    if task and task.get("user_id") == session["user_id"]:
        # Push deleted task to Undo Stack (DSA Concept: LIFO Stack)
        undo_stack.push({
            "type": "delete",
            "task": task
        })

        all_tasks.pop(index)
        save_json(TASKS_FILE, all_tasks)
        flash(f"Task '{task['title']}' deleted. You can click Undo if this was a mistake.", "info")
    else:
        flash("Task not found or access denied.", "error")

    return redirect(request.referrer or url_for("tasks_view"))


@app.route("/tasks/undo", methods=["POST"])
def undo_action():
    """Pops the most recent action from the ActionStack and reverts it."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    # DSA Concept: Stack Pop operation
    last_action = undo_stack.pop()
    if not last_action:
        flash("Nothing to undo.", "info")
        return redirect(request.referrer or url_for("tasks_view"))

    all_tasks = load_json(TASKS_FILE)

    if last_action["type"] == "toggle":
        task_id = last_action["task_id"]
        task, index = linear_search_task(all_tasks, task_id)
        if task:
            task["done"] = last_action["previous_state"]
            all_tasks[index] = task
            save_json(TASKS_FILE, all_tasks)
            flash(f"Reverted completion status for '{task['title']}'.", "success")

    elif last_action["type"] == "delete":
        restored_task = last_action["task"]
        all_tasks.append(restored_task)
        save_json(TASKS_FILE, all_tasks)
        flash(f"Restored deleted task '{restored_task['title']}'!", "success")

    return redirect(request.referrer or url_for("tasks_view"))


# =====================================================================
# TASK HIGHLIGHTS ROUTE
# =====================================================================
@app.route("/highlights")
def highlights():
    """Dedicated Task Highlights section organizing tasks that need urgent student attention."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_tasks = get_user_tasks(session["user_id"])

    # Categorized tasks using DSA filtering
    starred = filter_tasks_by_category(user_tasks, "starred")
    today_tasks = filter_tasks_by_category(user_tasks, "today")
    overdue_tasks = filter_tasks_by_category(user_tasks, "overdue")
    high_priority = [t for t in user_tasks if not t.get("done", False) and str(t.get("priority")) == "3"]
    upcoming_tasks = filter_tasks_by_category(user_tasks, "upcoming")
    
    completed_tasks = [t for t in user_tasks if t.get("done", False)]
    recent_completed = sorted(completed_tasks, key=lambda x: x.get("id", 0), reverse=True)[:6]

    return render_template(
        "highlights.html",
        starred=starred,
        today_tasks=today_tasks,
        overdue_tasks=overdue_tasks,
        high_priority=high_priority,
        upcoming_tasks=upcoming_tasks,
        recent_completed=recent_completed
    )


# =====================================================================
# SETTINGS ROUTE
# =====================================================================
@app.route("/settings", methods=["GET", "POST"])
def settings():
    """User profile management and preferences."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = get_current_user()

    if request.method == "POST":
        action = request.form.get("action")
        users = load_json(USERS_FILE)

        for u in users:
            if u["id"] == session["user_id"]:
                if action == "update_profile":
                    new_name = request.form.get("name", "").strip()
                    if new_name:
                        u["name"] = new_name
                        session["name"] = new_name
                        flash("Profile updated successfully!", "success")

                elif action == "change_password":
                    current_pw = request.form.get("current_password", "")
                    new_pw = request.form.get("new_password", "")
                    confirm_pw = request.form.get("confirm_password", "")

                    if not check_password_hash(u.get("password", ""), current_pw):
                        flash("Current password is incorrect.", "error")
                    elif new_pw != confirm_pw:
                        flash("New passwords do not match.", "error")
                    elif len(new_pw) < 6:
                        flash("New password must be at least 6 characters.", "error")
                    else:
                        u["password"] = generate_password_hash(new_pw)
                        flash("Password changed successfully!", "success")

                elif action == "clear_completed":
                    all_tasks = load_json(TASKS_FILE)
                    # Keep all tasks from other users, and only keep non-completed for this user
                    updated = [
                        t for t in all_tasks 
                        if t.get("user_id") != session["user_id"] or not t.get("done", False)
                    ]
                    save_json(TASKS_FILE, updated)
                    flash("All completed tasks have been cleared.", "success")
                break

        save_json(USERS_FILE, users)
        return redirect(url_for("settings"))

    return render_template("settings.html", user=user)


# =====================================================================
# API ROUTE FOR FRONTEND AJAX / QUICK RETRIEVAL
# =====================================================================
@app.route("/api/tasks")
def api_tasks():
    """Returns the logged-in student's tasks in JSON format."""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user_tasks = get_user_tasks(session["user_id"])
    return jsonify(bubble_sort_tasks(user_tasks, "priority"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
