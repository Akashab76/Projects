
const API_URL = "/api";

// ---------- Application state ----------
let token = localStorage.getItem("taskflowToken");
let currentUser = JSON.parse(
    localStorage.getItem("taskflowUser") || "null"
);
let tasks = [];
let isRegisterMode = false;
let editingTaskId = null;

// ---------- DOM elements ----------
const authSection = document.getElementById("auth-section");
const dashboardSection = document.getElementById("dashboard-section");
const authForm = document.getElementById("auth-form");
const authTitle = document.getElementById("auth-title");
const authSubtitle = document.getElementById("auth-subtitle");
const authButton = document.getElementById("auth-button");
const authMessage = document.getElementById("auth-message");
const usernameGroup = document.getElementById("username-group");
const switchLabel = document.getElementById("switch-label");
const switchAuthButton = document.getElementById("switch-auth");

const taskForm = document.getElementById("task-form");
const taskList = document.getElementById("task-list");
const taskMessage = document.getElementById("task-message");
const saveTaskButton = document.getElementById("save-task-button");
const cancelEditButton = document.getElementById("cancel-edit-button");
const taskFormTitle = document.getElementById("task-form-title");
const filterStatus = document.getElementById("filter-status");

// ---------- API helper ----------
async function apiRequest(path, options = {}) {
    const headers = {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers
    };

    const response = await fetch(`${API_URL}${path}`, {
        ...options,
        headers
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        if (response.status === 401 && token) {
            logout(false);
        }

        throw new Error(data.message || "Something went wrong.");
    }

    return data;
}

// ---------- Messages ----------
function showMessage(element, message, type = "error") {
    element.textContent = message;
    element.className = `message ${type}`;
}

function clearMessage(element) {
    element.textContent = "";
    element.className = "message";
}

// ---------- Switch between login and registration ----------
switchAuthButton.addEventListener("click", () => {
    isRegisterMode = !isRegisterMode;

    authTitle.textContent = isRegisterMode
        ? "Create your account"
        : "Welcome back";

    authSubtitle.textContent = isRegisterMode
        ? "Sign up to start organizing your tasks."
        : "Log in to manage your tasks.";

    authButton.textContent = isRegisterMode
        ? "Create Account"
        : "Log In";

    usernameGroup.classList.toggle("hidden", !isRegisterMode);
    document.getElementById("username").required = isRegisterMode;

    switchLabel.textContent = isRegisterMode
        ? "Already have an account?"
        : "New to TaskFlow?";

    switchAuthButton.textContent = isRegisterMode
        ? "Log in"
        : "Create an account";

    clearMessage(authMessage);
});

// ---------- Register or log in ----------
authForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage(authMessage);

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    const body = { email, password };

    if (isRegisterMode) {
        body.username = document.getElementById("username").value.trim();

        if (password.length < 8) {
            showMessage(
                authMessage,
                "Password must contain at least 8 characters."
            );
            return;
        }
    }

    authButton.disabled = true;
    authButton.textContent = "Please wait...";

    try {
        const endpoint = isRegisterMode ? "/auth/register" : "/auth/login";

        const data = await apiRequest(endpoint, {
            method: "POST",
            body: JSON.stringify(body)
        });

        if (isRegisterMode) {
            showMessage(
                authMessage,
                "Account created! You can now log in.",
                "success"
            );

            // Switch to login mode without submitting again.
            isRegisterMode = false;
            authTitle.textContent = "Welcome back";
            authSubtitle.textContent = "Log in to manage your tasks.";
            authButton.textContent = "Log In";
            usernameGroup.classList.add("hidden");
            document.getElementById("username").required = false;
            switchLabel.textContent = "New to TaskFlow?";
            switchAuthButton.textContent = "Create an account";
            document.getElementById("password").value = "";
        } else {
            token = data.token;
            currentUser = data.user;

            localStorage.setItem("taskflowToken", token);
            localStorage.setItem("taskflowUser", JSON.stringify(currentUser));

            await showDashboard();
        }
    } catch (error) {
        showMessage(authMessage, error.message);
    } finally {
        authButton.disabled = false;
        authButton.textContent = isRegisterMode
            ? "Create Account"
            : "Log In";
    }
});

// ---------- Show dashboard ----------
async function showDashboard() {
    authSection.classList.add("hidden");
    dashboardSection.classList.remove("hidden");

    const username = currentUser?.username || currentUser?.name || "there";
    document.getElementById("welcome-message").textContent =
        `Welcome, ${username}! Let's get things done.`;

    await loadTasks();
}

// ---------- Fetch tasks ----------
async function loadTasks() {
    taskList.textContent = "Loading tasks...";

    try {
        const data = await apiRequest("/tasks");
        tasks = data.tasks || [];
        renderTasks();
        updateStats();
    } catch (error) {
        taskList.textContent = "";
        showMessage(taskMessage, error.message);
    }
}

// ---------- Render task cards ----------
function renderTasks() {
    taskList.replaceChildren();

    const selectedStatus = filterStatus.value;
    const filteredTasks = selectedStatus === "All"
        ? tasks
        : tasks.filter(task => task.status === selectedStatus);

    if (filteredTasks.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty-state";
        empty.textContent = selectedStatus === "All"
            ? "No tasks yet. Create your first task above!"
            : `No ${selectedStatus.toLowerCase()} tasks found.`;

        taskList.appendChild(empty);
        return;
    }

    filteredTasks.forEach(task => {
        const card = document.createElement("article");
        card.className = "task-card";

        const title = document.createElement("h3");
        title.textContent = task.title;

        const description = document.createElement("p");
        description.className = "description";
        description.textContent = task.description || "No description provided.";

        const meta = document.createElement("div");
        meta.className = "task-meta";

        const priorityTag = document.createElement("span");
        priorityTag.className = "tag";
        if (task.priority === "High") priorityTag.classList.add("high");
        if (task.priority === "Low") priorityTag.classList.add("low");
        priorityTag.textContent = `${task.priority} priority`;

        const statusTag = document.createElement("span");
        statusTag.className = "tag";
        if (task.status === "Completed") statusTag.classList.add("completed");
        statusTag.textContent = task.status;

        meta.append(priorityTag, statusTag);

        if (task.dueDate) {
            const dueDate = document.createElement("span");
            dueDate.className = "tag";

            const date = new Date(task.dueDate);
            dueDate.textContent = `Due: ${date.toLocaleDateString("en-GB", {
                day: "2-digit",
                month: "short",
                year: "numeric",
                timeZone: "UTC"
            })}`;

            meta.appendChild(dueDate);
        }

        const actions = document.createElement("div");
        actions.className = "task-actions";

        const editButton = document.createElement("button");
        editButton.type = "button";
        editButton.textContent = "Edit";
        editButton.addEventListener("click", () => startEditing(task));

        const statusButton = document.createElement("button");
        statusButton.type = "button";
        statusButton.className = "secondary-button";
        statusButton.textContent = task.status === "Completed"
            ? "Mark Pending"
            : "Complete";
        statusButton.addEventListener("click", () => toggleTaskStatus(task));

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "delete-button";
        deleteButton.textContent = "Delete";
        deleteButton.addEventListener("click", () => deleteTask(task));

        actions.append(editButton, statusButton, deleteButton);
        card.append(title, description, meta, actions);
        taskList.appendChild(card);
    });
}

// ---------- Dashboard statistics ----------
function updateStats() {
    document.getElementById("total-count").textContent = tasks.length;

    document.getElementById("progress-count").textContent =
        tasks.filter(task => task.status === "In Progress").length;

    document.getElementById("completed-count").textContent =
        tasks.filter(task => task.status === "Completed").length;
}

// ---------- Create or update a task ----------
taskForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage(taskMessage);

    const title = document.getElementById("task-title").value.trim();

    if (!title) {
        showMessage(taskMessage, "Please enter a task title.");
        return;
    }

    const body = {
        title,
        description: document.getElementById("task-description").value.trim(),
        priority: document.getElementById("priority").value,
        status: document.getElementById("status").value,
        dueDate: document.getElementById("due-date").value || null
    };

    saveTaskButton.disabled = true;

    try {
        if (editingTaskId) {
            await apiRequest(`/tasks/${editingTaskId}`, {
                method: "PUT",
                body: JSON.stringify(body)
            });

            showMessage(taskMessage, "Task updated successfully!", "success");
        } else {
            await apiRequest("/tasks", {
                method: "POST",
                body: JSON.stringify(body)
            });

            showMessage(taskMessage, "Task created successfully!", "success");
        }

        resetTaskForm();
        await loadTasks();
    } catch (error) {
        showMessage(taskMessage, error.message);
    } finally {
        saveTaskButton.disabled = false;
    }
});

// ---------- Start editing a task ----------
function startEditing(task) {
    editingTaskId = task._id;

    document.getElementById("task-title").value = task.title;
    document.getElementById("task-description").value = task.description || "";
    document.getElementById("priority").value = task.priority;
    document.getElementById("status").value = task.status;
    document.getElementById("due-date").value = task.dueDate
        ? task.dueDate.slice(0, 10)
        : "";

    taskFormTitle.textContent = "Edit task";
    saveTaskButton.textContent = "Save Changes";
    cancelEditButton.classList.remove("hidden");
    clearMessage(taskMessage);

    taskForm.scrollIntoView({ behavior: "smooth", block: "center" });
}

// ---------- Reset task form ----------
function resetTaskForm() {
    editingTaskId = null;
    taskForm.reset();

    taskFormTitle.textContent = "Create a task";
    saveTaskButton.textContent = "Add Task";
    cancelEditButton.classList.add("hidden");
}

cancelEditButton.addEventListener("click", () => {
    resetTaskForm();
    clearMessage(taskMessage);
});

// ---------- Change task status ----------
async function toggleTaskStatus(task) {
    const newStatus = task.status === "Completed"
        ? "Pending"
        : "Completed";

    try {
        await apiRequest(`/tasks/${task._id}`, {
            method: "PUT",
            body: JSON.stringify({ status: newStatus })
        });

        await loadTasks();
    } catch (error) {
        showMessage(taskMessage, error.message);
    }
}

// ---------- Delete task ----------
async function deleteTask(task) {
    const confirmed = window.confirm(
        `Are you sure you want to delete "${task.title}"?`
    );

    if (!confirmed) return;

    try {
        await apiRequest(`/tasks/${task._id}`, {
            method: "DELETE"
        });

        if (editingTaskId === task._id) {
            resetTaskForm();
        }

        showMessage(taskMessage, "Task deleted successfully!", "success");
        await loadTasks();
    } catch (error) {
        showMessage(taskMessage, error.message);
    }
}

// ---------- Filter tasks ----------
filterStatus.addEventListener("change", renderTasks);

// ---------- Log out ----------
function logout(showLogin = true) {
    token = null;
    currentUser = null;
    tasks = [];

    localStorage.removeItem("taskflowToken");
    localStorage.removeItem("taskflowUser");

    dashboardSection.classList.add("hidden");
    authSection.classList.remove("hidden");

    resetTaskForm();
    taskList.replaceChildren();
    updateStats();

    if (showLogin) {
        clearMessage(authMessage);
        document.getElementById("password").value = "";
    }
}

document.getElementById("logout-button").addEventListener("click", () => {
    logout();
});

// ---------- Restore session on page refresh ----------
async function initializeApp() {
    if (token) {
        try {
            await showDashboard();
            return;
        } catch (error) {
            logout();
            showMessage(authMessage, "Please log in again.");
        }
    }

    authSection.classList.remove("hidden");
    dashboardSection.classList.add("hidden");
}

initializeApp();
