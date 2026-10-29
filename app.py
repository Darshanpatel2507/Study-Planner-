from flask import Flask, render_template, request, redirect, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = "tasks.json"


def load_tasks():
    # Read saved tasks. If the file does not exist, start with an empty list.
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as file:
        return json.load(file)


def save_tasks(tasks):
    # Save the task list so tasks remain after closing the app.
    with open(DATA_FILE, "w") as file:
        json.dump(tasks, file, indent=4)


def sort_tasks(tasks):
    # Tasks with higher priority come first. Earlier dates come first for equal priority.
    return sorted(tasks, key=lambda task: (-int(task["priority"]), task["due_date"]))


@app.route("/")
def home():
    tasks = sort_tasks(load_tasks())
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    tasks = load_tasks()

    new_task = {
        "id": max([task["id"] for task in tasks], default=0) + 1,
        "title": request.form["title"].strip(),
        "subject": request.form["subject"].strip(),
        "due_date": request.form["due_date"],
        "priority": request.form["priority"],
        "done": False
    }

    if new_task["title"]:
        tasks.append(new_task)
        save_tasks(tasks)

    return redirect("/")


@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    tasks = load_tasks()

    for task in tasks:
        if task["id"] == task_id:
            task["done"] = not task["done"]
            break

    save_tasks(tasks)
    return redirect("/")


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task["id"] != task_id]
    save_tasks(tasks)
    return redirect("/")


@app.route("/api/tasks")
def get_tasks():
    # This small API route returns tasks as JSON.
    return jsonify(sort_tasks(load_tasks()))


if __name__ == "__main__":
    app.run(debug=True)
