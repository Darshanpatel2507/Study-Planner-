/**
 * main.js - Client-side interactions for StudySpark
 * Student-friendly JavaScript for modals, live search, and mobile navigation.
 */

// Wait for DOM to fully load
document.addEventListener("DOMContentLoaded", function () {
    // 1. Auto-dismiss flash notification toasts after 4 seconds
    const toasts = document.querySelectorAll(".flash-toast");
    toasts.forEach(function (toast) {
        setTimeout(function () {
            toast.style.transition = "opacity 0.4s ease, transform 0.4s ease";
            toast.style.opacity = "0";
            toast.style.transform = "translateX(50px)";
            setTimeout(function () {
                toast.remove();
            }, 400);
        }, 4000);
    });

    // 2. Mobile Sidebar Toggle
    const mobileBtn = document.getElementById("mobile-menu-toggle");
    const sidebar = document.getElementById("app-sidebar");
    if (mobileBtn && sidebar) {
        mobileBtn.addEventListener("click", function () {
            sidebar.classList.toggle("open");
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener("click", function (e) {
            if (sidebar.classList.contains("open") && !sidebar.contains(e.target) && !mobileBtn.contains(e.target)) {
                sidebar.classList.remove("open");
            }
        });
    }

    // 3. Client-side Real-time Search
    const searchInput = document.getElementById("task-search-input");
    if (searchInput) {
        searchInput.addEventListener("input", function () {
            const query = searchInput.value.toLowerCase().trim();
            const taskCards = document.querySelectorAll(".task-card");

            taskCards.forEach(function (card) {
                const title = card.querySelector(".task-title")?.innerText.toLowerCase() || "";
                const subject = card.querySelector(".badge-subject")?.innerText.toLowerCase() || "";
                const desc = card.querySelector(".task-desc")?.innerText.toLowerCase() || "";

                if (title.includes(query) || subject.includes(query) || desc.includes(query)) {
                    card.style.display = "flex";
                } else {
                    card.style.display = "none";
                }
            });
        });
    }
});

/**
 * Open Modal helper
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add("active");
    }
}

/**
 * Close Modal helper
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove("active");
    }
}

/**
 * Pre-populate and open the Edit Task Modal
 */
function openEditModal(id, title, subject, desc, dueDate, priority, estHours) {
    const modal = document.getElementById("edit-task-modal");
    const form = document.getElementById("edit-task-form");

    if (modal && form) {
        form.action = "/tasks/edit/" + id;
        document.getElementById("edit-title").value = title;
        document.getElementById("edit-subject").value = subject;
        document.getElementById("edit-desc").value = desc;
        document.getElementById("edit-due-date").value = dueDate;
        document.getElementById("edit-priority").value = priority;
        document.getElementById("edit-est-hours").value = estHours || 1;

        openModal("edit-task-modal");
    }
}

/**
 * Confirmation dialog before deleting a task
 */
function confirmDelete(taskTitle) {
    return confirm("Are you sure you want to delete the task: '" + taskTitle + "'?");
}
