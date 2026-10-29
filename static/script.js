function searchTasks() {
    // Show only tasks that contain the text typed by the user.
    let searchText = document.getElementById("search").value.toLowerCase();
    let tasks = document.querySelectorAll(".task");

    tasks.forEach(function(task) {
        let taskText = task.innerText.toLowerCase();

        if (taskText.includes(searchText)) {
            task.style.display = "flex";
        } else {
            task.style.display = "none";
        }
    });
}

function showTasks(status) {
    // Filter the task cards by their current status.
    let tasks = document.querySelectorAll(".task");

    tasks.forEach(function(task) {
        if (status === "all" || task.dataset.status === status) {
            task.style.display = "flex";
        } else {
            task.style.display = "none";
        }
    });

    // Clear search text when changing the filter.
    document.getElementById("search").value = "";
}
