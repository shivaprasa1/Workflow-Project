
import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import api from "../../api/axios";
import "../../styles/dashboard.css";

function ManagerDashboard() {
  const { user, logout } = useAuth();

  const [dashboard, setDashboard] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [updatingTaskId, setUpdatingTaskId] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    priority: "MEDIUM",
    due_date: "",
    assigned_to: "",
  });

  const loadDashboard = useCallback(async () => {
    try {
      setError("");

      const [
        dashboardResponse,
        tasksResponse,
        employeesResponse,
        notificationResponse,
      ] = await Promise.all([
        api.get("/dashboard/"),
        api.get("/tasks/?skip=0&limit=100"),
        api.get("/users/employees/"),
        api.get("/notifications/unread-count"),
      ]);

      setDashboard(dashboardResponse.data);
      setTasks(tasksResponse.data);
      setEmployees(employeesResponse.data);
      setUnreadCount(notificationResponse.data.unread_count);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to load manager dashboard."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const handleInputChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleCreateTask = async (event) => {
    event.preventDefault();

    try {
      setSubmitting(true);
      setError("");
      setMessage("");

      await api.post("/tasks/", {
        ...formData,
        assigned_to: Number(formData.assigned_to),
        due_date: new Date(formData.due_date).toISOString(),
      });

      setMessage("Task successfully assigned to employee.");

      setFormData({
        title: "",
        description: "",
        priority: "MEDIUM",
        due_date: "",
        assigned_to: "",
      });

      await loadDashboard();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to create task."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleReviewTask = async (taskId, status) => {
    try {
      setUpdatingTaskId(taskId);
      setError("");
      setMessage("");

      await api.patch(`/tasks/${taskId}/status`, {
        status,
      });

      setMessage(
        status === "APPROVED"
          ? "Task approved successfully."
          : "Task rejected successfully."
      );

      await loadDashboard();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to update task status."
      );
    } finally {
      setUpdatingTaskId(null);
    }
  };

  if (loading) {
    return <div className="dashboard-container">Loading dashboard...</div>;
  }

  const statistics = dashboard?.statistics || {};

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div>
          <h1>Manager Dashboard</h1>
          <p>Welcome, {user?.name}</p>
        </div>

        <div className="dashboard-header-actions">
          <span className="notification-count">
            Notifications: {unreadCount}
          </span>

          <button onClick={loadDashboard} className="refresh-button">
            Refresh
          </button>

          <button onClick={logout} className="logout-button">
            Logout
          </button>
        </div>
      </header>

      {error && (
        <div className="dashboard-error">{error}</div>
      )}

      {message && (
        <div className="dashboard-action-message">{message}</div>
      )}

      <section className="stats-grid">
        <div className="stat-card">
          <h3>Total Tasks</h3>
          <p>{statistics.total_tasks ?? 0}</p>
        </div>

        <div className="stat-card">
          <h3>Assigned</h3>
          <p>{statistics.assigned_tasks ?? 0}</p>
        </div>

        <div className="stat-card">
          <h3>In Progress</h3>
          <p>{statistics.in_progress_tasks ?? 0}</p>
        </div>

        <div className="stat-card">
          <h3>Submitted</h3>
          <p>{statistics.submitted_tasks ?? 0}</p>
        </div>

        <div className="stat-card">
          <h3>Approved</h3>
          <p>{statistics.approved_tasks ?? 0}</p>
        </div>

        <div className="stat-card">
          <h3>Overdue</h3>
          <p>{statistics.overdue_tasks ?? 0}</p>
        </div>
      </section>

      <section className="dashboard-section">
        <h2>Assign New Task</h2>

        <form onSubmit={handleCreateTask} className="task-form">
          <div className="form-group">
            <label>Task Title</label>
            <input
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              minLength={3}
              maxLength={200}
              required
              placeholder="Enter task title"
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Describe the task"
            />
          </div>

          <div className="form-group">
            <label>Priority</label>
            <select
              name="priority"
              value={formData.priority}
              onChange={handleInputChange}
            >
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="URGENT">Urgent</option>
            </select>
          </div>

          <div className="form-group">
            <label>Due Date and Time</label>
            <input
              type="datetime-local"
              name="due_date"
              value={formData.due_date}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Assign Employee</label>
            <select
              name="assigned_to"
              value={formData.assigned_to}
              onChange={handleInputChange}
              required
            >
              <option value="">Select Employee</option>

              {employees.map((employee) => (
                <option key={employee.id} value={employee.id}>
                  {employee.name} - {employee.department || "No Department"}
                </option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={submitting || employees.length === 0}
            className="submit-task-button"
          >
            {submitting ? "Assigning..." : "Assign Task"}
          </button>

          {employees.length === 0 && (
            <p>No active employees are currently available.</p>
          )}
        </form>
      </section>

      <section className="dashboard-section">
        <h2>Employee Workload</h2>

        {dashboard?.employee_workload?.length > 0 ? (
          <div className="table-wrapper">
            <table className="dashboard-table">
              <thead>
                <tr>
                  <th>Employee</th>
                  <th>Department</th>
                  <th>Total Tasks</th>
                  <th>In Progress</th>
                  <th>Completed</th>
                </tr>
              </thead>

              <tbody>
                {dashboard.employee_workload.map((employee) => (
                  <tr key={employee.employee_id}>
                    <td>{employee.employee_name}</td>
                    <td>{employee.department || "-"}</td>
                    <td>{employee.total_tasks}</td>
                    <td>{employee.in_progress_tasks}</td>
                    <td>{employee.completed_tasks}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No employee workload available yet.</p>
        )}
      </section>

      <section className="dashboard-section">
        <h2>Manage Tasks</h2>

        <div className="table-wrapper">
          <table className="dashboard-table">
            <thead>
              <tr>
                <th>Task</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Due Date</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {tasks.length > 0 ? (
                tasks.map((task) => (
                  <tr key={task.id}>
                    <td>{task.title}</td>
                    <td>{task.priority}</td>
                    <td>{task.status}</td>
                    <td>
                      {new Date(task.due_date).toLocaleString()}
                    </td>
                    <td>
                      {task.status === "SUBMITTED" ? (
                        <div className="task-review-actions">
                          <button
                            className="task-action-button"
                            disabled={updatingTaskId === task.id}
                            onClick={() =>
                              handleReviewTask(task.id, "APPROVED")
                            }
                          >
                            Approve
                          </button>

                          <button
                            className="task-reject-button"
                            disabled={updatingTaskId === task.id}
                            onClick={() =>
                              handleReviewTask(task.id, "REJECTED")
                            }
                          >
                            Reject
                          </button>
                        </div>
                      ) : (
                        <span className="waiting-label">
                          {task.status === "APPROVED"
                            ? "Completed"
                            : task.status === "REJECTED"
                              ? "Returned"
                              : "In progress"}
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5">No tasks created yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default ManagerDashboard;
