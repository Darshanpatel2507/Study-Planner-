"""
dsa_operations.py - Data Structures & Algorithms for StudySpark
---------------------------------------------------------------
This file contains pure, beginner-friendly DSA implementations designed
for a college-level project presentation.

Implemented Concepts:
1. List & Dictionary: Core data structures for tasks.
2. Linear Search: O(N) search to find a task by its ID.
3. Bubble Sort: Classic O(N^2) sorting algorithm for task prioritization.
4. Priority Queue (Heap): Uses Python's heapq for smart task recommendation.
5. Stack: LIFO (Last-In-First-Out) for Undo functionality.
6. Hash Map: Fast O(1) task lookup by Task ID.
7. Filtering: Condition-based traversal for deadlines, priorities, and highlights.
"""

from datetime import datetime, date
import heapq


# =====================================================================
# 1. LINEAR SEARCH (Concept: Linear Search, Time Complexity: O(N))
# =====================================================================
def linear_search_task(tasks, task_id):
    """
    Finds a task by ID using Linear Search.
    Traverses the list one by one until the matching task is found.
    """
    for index, task in enumerate(tasks):
        if task.get("id") == task_id:
            return task, index
    return None, -1


# =====================================================================
# 2. HASH MAP (Concept: Hash Table / Dictionary, Time Complexity: O(1))
# =====================================================================
def build_task_hash_map(tasks):
    """
    Converts a list of tasks into a dictionary (Hash Map)
    where keys are task IDs for instant O(1) lookups.
    """
    task_map = {}
    for task in tasks:
        task_map[task["id"]] = task
    return task_map


# =====================================================================
# 3. BUBBLE SORT (Concept: Sorting Algorithm, Time Complexity: O(N^2))
# =====================================================================
def bubble_sort_tasks(tasks, sort_by="priority"):
    """
    Sorts a copy of the task list using the Bubble Sort algorithm.
    Swaps adjacent elements until the list is sorted.
    
    Supported criteria:
      - 'priority': High priority first, then earliest due date
      - 'due_date': Earliest due date first
      - 'alphabetical': Task title alphabetically A-Z
      - 'recent': Highest task ID first (most recently added)
    """
    # Create a shallow copy so the original list remains untouched
    sorted_tasks = list(tasks)
    n = len(sorted_tasks)

    for i in range(n):
        for j in range(0, n - i - 1):
            t1 = sorted_tasks[j]
            t2 = sorted_tasks[j + 1]
            swap = False

            if sort_by == "priority":
                # Convert priority to integer (High=3, Medium=2, Low=1)
                p1 = int(t1.get("priority", 1))
                p2 = int(t2.get("priority", 1))
                
                # Higher priority should come first
                if p1 < p2:
                    swap = True
                elif p1 == p2:
                    # If priorities are equal, earlier due date comes first
                    if t1.get("due_date", "") > t2.get("due_date", ""):
                        swap = True

            elif sort_by == "due_date":
                # Earliest due date first
                if t1.get("due_date", "") > t2.get("due_date", ""):
                    swap = True

            elif sort_by == "alphabetical":
                # A to Z by title
                if t1.get("title", "").lower() > t2.get("title", "").lower():
                    swap = True

            elif sort_by == "recent":
                # Newest ID first
                if t1.get("id", 0) < t2.get("id", 0):
                    swap = True

            if swap:
                sorted_tasks[j], sorted_tasks[j + 1] = sorted_tasks[j + 1], sorted_tasks[j]

    return sorted_tasks


# =====================================================================
# 4. PRIORITY QUEUE / HEAP (Concept: Heap / Priority Queue)
# =====================================================================
def get_smart_recommendation(tasks):
    """
    Recommends the single most critical pending task using a Priority Queue (Min-Heap).
    Completed tasks are excluded.
    
    Urgency Score Formula:
      Higher priority (High=3, Medium=2, Low=1) + closer deadline = highest priority.
      We negate urgency so Python's min-heap (heapq) pops the most urgent item first.
    """
    pending_tasks = [t for t in tasks if not t.get("done", False)]
    if not pending_tasks:
        return None

    today = date.today()
    heap = []

    for task in pending_tasks:
        priority = int(task.get("priority", 1))
        due_date_str = task.get("due_date", "")
        
        days_left = 999
        if due_date_str:
            try:
                task_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                days_left = (task_date - today).days
            except ValueError:
                days_left = 999

        # Calculate urgency score
        # Base priority weight: High=300, Medium=200, Low=100
        # Closer due dates give extra score
        urgency = priority * 100
        if days_left < 0:
            urgency += 150  # Overdue is super critical!
            status_text = "Overdue! Needs immediate attention."
        elif days_left == 0:
            urgency += 100  # Due today
            status_text = "Due today! High urgency."
        elif days_left <= 3:
            urgency += 50   # Due in 1-3 days
            status_text = f"Due in {days_left} day(s)."
        else:
            status_text = f"Due on {due_date_str}."

        # Negate urgency because heapq is a min-heap
        # Tuple format: (-urgency, days_left, task_id, task, reason)
        heapq.heappush(heap, (-urgency, days_left, task.get("id"), task, status_text))

    if heap:
        best = heapq.heappop(heap)
        recommended_task = best[3]
        reason = best[4]
        p_name = {3: "High", 2: "Medium", 1: "Low"}.get(int(recommended_task.get("priority", 1)), "Normal")
        
        return {
            "task": recommended_task,
            "reason": f"Recommended because it has {p_name} priority and {reason.lower()}"
        }

    return None


# =====================================================================
# 5. STACK FOR UNDO FUNCTIONALITY (Concept: LIFO Stack)
# =====================================================================
class ActionStack:
    """
    A simple in-memory Stack data structure for undoing task actions.
    Uses push() and pop() following Last-In, First-Out (LIFO).
    """
    def __init__(self):
        self.stack = []

    def push(self, action):
        """Pushes an action onto the top of the stack."""
        self.stack.append(action)

    def pop(self):
        """Pops and returns the most recent action from the stack."""
        if self.is_empty():
            return None
        return self.stack.pop()

    def is_empty(self):
        """Checks if the stack is empty."""
        return len(self.stack) == 0

    def peek(self):
        """Returns the top item without removing it."""
        if self.is_empty():
            return None
        return self.stack[-1]

    def clear(self):
        """Clears all actions."""
        self.stack.clear()


# Global in-memory stack for undo actions
undo_stack = ActionStack()


# =====================================================================
# 6. FILTERING (Concept: Traversals and Conditionals)
# =====================================================================
def get_task_counts(tasks):
    """
    Calculates summary statistics using a single loop traversal.
    Returns total, completed, pending, and progress percentage.
    """
    total = len(tasks)
    completed = 0
    pending = 0

    for task in tasks:
        if task.get("done", False):
            completed += 1
        else:
            pending += 1

    progress = round((completed / total * 100), 1) if total > 0 else 0

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "progress": progress
    }


def filter_tasks_by_category(tasks, category):
    """
    Filters tasks based on student criteria (Highlights / Status).
    """
    today_str = date.today().strftime("%Y-%m-%d")
    today = date.today()
    result = []

    for task in tasks:
        due = task.get("due_date", "")
        done = task.get("done", False)
        priority = str(task.get("priority", "1"))
        highlighted = task.get("is_highlighted", False)

        if category == "all":
            result.append(task)
        elif category == "pending" and not done:
            result.append(task)
        elif category == "completed" and done:
            result.append(task)
        elif category == "high" and priority == "3":
            result.append(task)
        elif category == "medium" and priority == "2":
            result.append(task)
        elif category == "low" and priority == "1":
            result.append(task)
        elif category == "starred" and highlighted:
            result.append(task)
        elif category == "today" and not done and due == today_str:
            result.append(task)
        elif category == "overdue" and not done and due and due < today_str:
            result.append(task)
        elif category == "upcoming" and not done and due and due > today_str:
            try:
                task_date = datetime.strptime(due, "%Y-%m-%d").date()
                if 0 < (task_date - today).days <= 7:
                    result.append(task)
            except ValueError:
                pass

    return result
