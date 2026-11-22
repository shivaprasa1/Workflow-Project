
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ClipboardList,
  Clock,
  CheckCircle,
  Bell,
  LogOut,
  RefreshCw,
  Workflow,
} from "lucide-react";

import api from "../../api/axios";
import { useAuth } from "../../context/AuthContext";
import "../../styles/dashboard.css";

function EmployeeDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [statistics, setStatistics] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingTaskId, setUpdatingTaskId] = useState(null);
  const [actionMessage, setActionMessage] = useState("");

  const fetchDashboard = async () => {
    setLoading(true);
    setError("");

    try {
      const [
        dashboardResponse,
        tasksResponse,
        notificationResponse,
      ] = await Promise.all([
        api.get("/dashboard/"),
        api.get("/tasks/", {
          params: { skip: 0, limit: 5 },
        }),
        api.get("/notifications/unread-count"),
      ]);

      setStatistics(dashboardResponse.data.statistics);
      setTasks(tasksResponse.data);
      setUnreadCount(notificationResponse.data.unread_count);
    } catch (err) {
      console.error("Dashboard loading error:", err);
      setError("Unable to load dashboard data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const getNextStatus = (status) => {
    switch (status) {
      case "ASSIGNED":
        return "IN_PROGRESS";
      case "IN_PROGRESS":
        return "SUBMITTED";
      case "REJECTED":
        return "IN_PROGRESS";
      default:
        return null;
    }
  };

  const getActionLabel = (status) => {
    switch (status) {
      case "ASSIGNED":
        return "Start Task";
      case "IN_PROGRESS":
        return "Submit Task";
      case "REJECTED":
        return "Restart Task";
      default:
        return null;
    }
  };

  const handleTaskAction = async (task) => {
    const nextStatus = getNextStatus(task.status);

    if (!nextStatus) return;

    setUpdatingTaskId(task.id);
    setActionMessage("");
    setError("");

    try {
      await api.patch(`/tasks/${task.id}/status`, {
        status: nextStatus,
      });

      setActionMessage(
        `Task "${task.title}" updated successfully.`
      );

      await fetchDashboard();
    } catch (err) {
      const detail = err.response?.data?.detail;

      setActionMessage(
        typeof detail === "string"
          ? detail
          : "Unable to update task. Please try again."
      );
    } finally {
      setUpdatingTaskId(null);
    }
  };

  const formatDate = (date) => {
    if (!date) return "Not specified";

    return new Date(date).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  const getStatusClass = (status) => {
    return status.toLowerCase().replaceAll("_", "-");
  };

  const statCards = statistics
    ? [
        {
          title: "Total Tasks",
          value: statistics.total_tasks,
          icon: ClipboardList,
          color: "blue",
        },
        {
          title: "In Progress",
          value: statistics.in_progress_tasks,
          icon: Clock,
          color: "orange",
        },
        {
          title: "Approved",
          value: statistics.approved_tasks,
          icon: CheckCircle,
          color: "green",
        },
        {
          title: "Overdue",
          value: statistics.overdue_tasks,
          icon: Bell,
          color: "red",
        },
      ]
    : [];

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="dashboard-brand">
          <Workflow size={30} />
          <span>Smart Workflow</span>
        </div>

        <div className="dashboard-user">
          <div className="user-details">
            <strong>{user?.name || "Employee"}</strong>
            <span>{user?.role || "EMPLOYEE"}</span>
          </div>

          <button
            className="logout-button"
            onClick={handleLogout}
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-content">
        <section className="dashboard-welcome">
          <div>
            <h1>Employee Dashboard</h1>
            <p>
              Welcome back, {user?.name || "Employee"}!
              Here's your work overview.
            </p>

            {user?.department && (
              <span className="department-label">
                Department: {user.department}
              </span>
            )}
          </div>

          <button
            className="refresh-button"
            onClick={fetchDashboard}
            disabled={loading}
          >
            <RefreshCw size={17} />
            Refresh
          </button>
        </section>

        {error && (
          <div className="dashboard-error">
            {error}
          </div>
        )}

        {loading ? (
          <div className="dashboard-loading">
            Loading your dashboard...
          </div>
        ) : statistics ? (
          <>
            <section className="stats-grid">
              {statCards.map((card) => {
                const Icon = card.icon;

                return (
                  <div className="stat-card" key={card.title}>
                    <div className={`stat-icon ${card.color}`}>
                      <Icon size={23} />
                    </div>

                    <div>
                      <p>{card.title}</p>
                      <h2>{card.value}</h2>
                    </div>
                  </div>
                );
              })}
            </section>

            <section className="dashboard-secondary">
              <div className="dashboard-panel notification-panel">
                <div className="panel-icon">
                  <Bell size={23} />
                </div>

                <div>
                  <h3>Notifications</h3>
                  <p>
                    You have {unreadCount} unread notifications.
                  </p>
                </div>
              </div>

              <div className="dashboard-panel">
                <h3>Task Overview</h3>

                <div className="overview-row">
                  <span>Assigned</span>
                  <strong>{statistics.assigned_tasks}</strong>
                </div>

                <div className="overview-row">
                  <span>Submitted</span>
                  <strong>{statistics.submitted_tasks}</strong>
                </div>

                <div className="overview-row">
                  <span>Rejected</span>
                  <strong>{statistics.rejected_tasks}</strong>
                </div>
              </div>
            </section>

            <section className="dashboard-panel tasks-panel">
              <div className="panel-heading">
                <div>
                  <h2>Recent Tasks</h2>
                  <p>Your five most recent assigned tasks</p>
                </div>
              </div>

              {actionMessage && (
                <div className="dashboard-action-message">
                  {actionMessage}
                </div>
              )}

              {tasks.length === 0 ? (
                <div className="empty-tasks">
                  <ClipboardList size={35} />
                  <h3>No tasks assigned yet</h3>
                  <p>Your assigned tasks will appear here.</p>
                </div>
              ) : (
                <div className="table-wrapper">
                  <table className="tasks-table">
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
                      {tasks.map((task) => (
                        <tr key={task.id}>
                          <td>
                            <strong>{task.title}</strong>
                            <small>Task #{task.id}</small>
                          </td>

                          <td>
                            <span
                              className={`priority-badge ${task.priority.toLowerCase()}`}
                            >
                              {task.priority}
                            </span>
                          </td>

                          <td>
                            <span
                              className={`status-badge ${getStatusClass(task.status)}`}
                            >
                              {task.status.replaceAll("_", " ")}
                            </span>
                          </td>

                          <td>{formatDate(task.due_date)}</td>

                          <td>
                            {getNextStatus(task.status) ? (
                              <button
                                className="task-action-button"
                                onClick={() => handleTaskAction(task)}
                                disabled={updatingTaskId === task.id}
                              >
                                {updatingTaskId === task.id
                                  ? "Updating..."
                                  : getActionLabel(task.status)}
                              </button>
                            ) : (
                              <span className="waiting-label">
                                {task.status === "SUBMITTED"
                                  ? "Waiting for approval"
                                  : "Completed"}
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </>
        ) : null}
      </main>
    </div>
  );
}

export default EmployeeDashboard;
