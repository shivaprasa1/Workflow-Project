
import { useCallback, useEffect, useState } from "react";
import {
  Users,
  ClipboardList,
  CheckCircle,
  Clock,
  AlertTriangle,
  LogOut,
  RefreshCw,
  ShieldCheck,
  UserCheck,
  UserX,
} from "lucide-react";

import { useAuth } from "../../context/AuthContext";
import api from "../../api/axios";
import "../../styles/admin.css";

function AdminDashboard() {
  const { user, logout } = useAuth();

  const [dashboard, setDashboard] = useState(null);
  const [users, setUsers] = useState([]);
  const [tasks, setTasks] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionMessage, setActionMessage] = useState("");

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [dashboardResponse, usersResponse, tasksResponse] =
        await Promise.all([
          api.get("/dashboard/"),
          api.get("/users/?skip=0&limit=100"),
          api.get("/tasks/?skip=0&limit=100"),
        ]);

      setDashboard(dashboardResponse.data);
      setUsers(usersResponse.data);
      setTasks(tasksResponse.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load Admin Dashboard."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const updateRole = async (userId, newRole) => {
    setError("");
    setActionMessage("");

    try {
      await api.patch(`/users/${userId}/role`, {
        role: newRole,
      });

      setActionMessage("User role updated successfully.");
      await loadDashboard();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to update user role."
      );
    }
  };

  const toggleUserStatus = async (selectedUser) => {
    setError("");
    setActionMessage("");

    try {
      await api.patch(`/users/${selectedUser.id}/status`, {
        is_active: !selectedUser.is_active,
      });

      setActionMessage("User status updated successfully.");
      await loadDashboard();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to update user status."
      );
    }
  };

  const statistics = dashboard?.statistics || {};

  const statCards = [
    {
      label: "Total Tasks",
      value: statistics.total_tasks ?? 0,
      icon: ClipboardList,
    },
    {
      label: "Assigned",
      value: statistics.assigned_tasks ?? 0,
      icon: Clock,
    },
    {
      label: "In Progress",
      value: statistics.in_progress_tasks ?? 0,
      icon: RefreshCw,
    },
    {
      label: "Submitted",
      value: statistics.submitted_tasks ?? 0,
      icon: AlertTriangle,
    },
    {
      label: "Approved",
      value: statistics.approved_tasks ?? 0,
      icon: CheckCircle,
    },
    {
      label: "Overdue",
      value: statistics.overdue_tasks ?? 0,
      icon: AlertTriangle,
    },
  ];

  if (loading && !dashboard) {
    return (
      <div className="admin-loading">
        Loading Admin Dashboard...
      </div>
    );
  }

  return (
    <div className="admin-page">
      <header className="admin-header">
        <div className="admin-brand">
          <div className="admin-brand-icon">
            <ShieldCheck size={25} />
          </div>

          <div>
            <h1>Workflow Admin</h1>
            <p>System Management</p>
          </div>
        </div>

        <div className="admin-header-user">
          <div>
            <strong>{user?.name}</strong>
            <span>Administrator</span>
          </div>

          <button
            className="admin-logout-button"
            onClick={logout}
          >
            <LogOut size={17} />
            Logout
          </button>
        </div>
      </header>

      <main className="admin-content">
        <section className="admin-welcome">
          <div>
            <h2>Admin Dashboard</h2>
            <p>
              Monitor your organization, users and workflow tasks.
            </p>
          </div>

          <button
            className="admin-refresh-button"
            onClick={loadDashboard}
            disabled={loading}
          >
            <RefreshCw size={17} />
            Refresh
          </button>
        </section>

        {error && (
          <div className="admin-message admin-error">
            {error}
          </div>
        )}

        {actionMessage && (
          <div className="admin-message admin-success">
            {actionMessage}
          </div>
        )}

        <section className="admin-stats-grid">
          {statCards.map((stat) => {
            const Icon = stat.icon;

            return (
              <article className="admin-stat-card" key={stat.label}>
                <div className="admin-stat-icon">
                  <Icon size={22} />
                </div>

                <div>
                  <p>{stat.label}</p>
                  <h3>{stat.value}</h3>
                </div>
              </article>
            );
          })}
        </section>

        <section className="admin-panel">
          <div className="admin-panel-heading">
            <div>
              <h2>
                <Users size={20} />
                User Management
              </h2>
              <p>Manage user roles and account status.</p>
            </div>

            <span className="admin-count">
              {users.length} users
            </span>
          </div>

          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Department</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {users.map((item) => {
                  const isCurrentUser = item.id === user?.id;

                  return (
                    <tr key={item.id}>
                      <td>#{item.id}</td>
                      <td>{item.name}</td>
                      <td>{item.email}</td>
                      <td>{item.department || "—"}</td>

                      <td>
                        <select
                          className="admin-role-select"
                          value={item.role}
                          disabled={isCurrentUser}
                          onChange={(event) =>
                            updateRole(item.id, event.target.value)
                          }
                        >
                          <option value="EMPLOYEE">Employee</option>
                          <option value="MANAGER">Manager</option>
                          <option value="ADMIN">Admin</option>
                        </select>
                      </td>

                      <td>
                        <span
                          className={`admin-status ${
                            item.is_active ? "active" : "inactive"
                          }`}
                        >
                          {item.is_active ? "Active" : "Inactive"}
                        </span>
                      </td>

                      <td>
                        <button
                          className={`admin-status-button ${
                            item.is_active ? "deactivate" : "activate"
                          }`}
                          disabled={isCurrentUser}
                          onClick={() => toggleUserStatus(item)}
                          title={
                            isCurrentUser
                              ? "You cannot deactivate your own account"
                              : ""
                          }
                        >
                          {item.is_active ? (
                            <>
                              <UserX size={15} />
                              Deactivate
                            </>
                          ) : (
                            <>
                              <UserCheck size={15} />
                              Activate
                            </>
                          )}
                        </button>
                      </td>
                    </tr>
                  );
                })}

                {users.length === 0 && (
                  <tr>
                    <td colSpan="7" className="admin-empty">
                      No users found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="admin-panel">
          <div className="admin-panel-heading">
            <div>
              <h2>
                <ClipboardList size={20} />
                All Tasks
              </h2>
              <p>Monitor tasks across the organization.</p>
            </div>

            <span className="admin-count">
              {tasks.length} tasks
            </span>
          </div>

          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Task ID</th>
                  <th>Title</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Assigned To</th>
                  <th>Due Date</th>
                </tr>
              </thead>

              <tbody>
                {tasks.map((task) => {
                  const assignedUser = users.find(
                    (item) => item.id === task.assigned_to
                  );

                  return (
                    <tr key={task.id}>
                      <td>#{task.id}</td>
                      <td>{task.title}</td>
                      <td>
                        <span
                          className={`admin-priority ${task.priority?.toLowerCase()}`}
                        >
                          {task.priority}
                        </span>
                      </td>
                      <td>
                        <span
                          className={`admin-task-status ${task.status?.toLowerCase()}`}
                        >
                          {task.status?.replace("_", " ")}
                        </span>
                      </td>
                      <td>
                        {assignedUser?.name || `User #${task.assigned_to}`}
                      </td>
                      <td>
                        {task.due_date
                          ? new Date(task.due_date).toLocaleString()
                          : "—"}
                      </td>
                    </tr>
                  );
                })}

                {tasks.length === 0 && (
                  <tr>
                    <td colSpan="6" className="admin-empty">
                      No tasks found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}

export default AdminDashboard;
