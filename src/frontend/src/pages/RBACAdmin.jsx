// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Admin RBAC management page for roles, permissions, and assignments. Fetches and displays roles/permissions, allows CRUD, and assignment of roles to users and permissions to roles. Uses api.js RBAC methods.
// Why: Enables enterprise-grade governance and least-privilege workflows for admin users.
// Root Cause: No UI existed for managing roles, permissions, or assignments.
// Context: Use in admin dashboard. Future: add org/team scoping, search/filter, and fine-grained permission checks.
// Model Suitability: For React admin panels, GPT-4.1 is sufficient; for advanced UX, consider Claude 3 or Gemini 1.5.

import { useEffect, useState } from 'react';
import api from '../services/api';

export default function RBACAdmin() {
    const [roles, setRoles] = useState([]);
    const [permissions, setPermissions] = useState([]);
    const [users, setUsers] = useState([]);
    const [newRole, setNewRole] = useState('');
    const [newPermission, setNewPermission] = useState('');
    const [selectedUser, setSelectedUser] = useState('');
    const [selectedRole, setSelectedRole] = useState('');
    const [selectedPermission, setSelectedPermission] = useState('');
    const [message, setMessage] = useState('');

    useEffect(() => {
        fetchAll();
    }, []);

    async function fetchAll() {
        setRoles(await api.getRoles());
        setPermissions(await api.getPermissions());
        setUsers(await api.getUsersSimple());
    }

    async function handleCreateRole() {
        if (!newRole) return;
        await api.createRole({ name: newRole });
        setNewRole('');
        fetchAll();
        setMessage('Role created');
    }

    async function handleDeleteRole(roleId) {
        await api.deleteRole(roleId);
        fetchAll();
        setMessage('Role deleted');
    }

    async function handleCreatePermission() {
        if (!newPermission) return;
        await api.createPermission({ name: newPermission });
        setNewPermission('');
        fetchAll();
        setMessage('Permission created');
    }

    async function handleDeletePermission(permissionId) {
        await api.deletePermission(permissionId);
        fetchAll();
        setMessage('Permission deleted');
    }

    async function handleAssignRole() {
        if (!selectedUser || !selectedRole) return;
        await api.assignRoleToUser(selectedUser, selectedRole);
        setMessage('Role assigned to user');
    }

    async function handleRemoveRole() {
        if (!selectedUser || !selectedRole) return;
        await api.removeRoleFromUser(selectedUser, selectedRole);
        setMessage('Role removed from user');
    }

    async function handleAssignPermission() {
        if (!selectedRole || !selectedPermission) return;
        await api.assignPermissionToRole(selectedRole, selectedPermission);
        setMessage('Permission assigned to role');
    }

    async function handleRemovePermission() {
        if (!selectedRole || !selectedPermission) return;
        await api.removePermissionFromRole(selectedRole, selectedPermission);
        setMessage('Permission removed from role');
    }

    return (
        <div style={{ padding: 24 }}>
            <h2>RBAC Management</h2>
            {message && <div style={{ color: 'green', marginBottom: 8 }}>{message}</div>}
            <div style={{ display: 'flex', gap: 32 }}>
                <div>
                    <h3>Roles</h3>
                    <ul>
                        {roles.map(r => (
                            <li key={r.id}>{r.name} <button onClick={() => handleDeleteRole(r.id)}>Delete</button></li>
                        ))}
                    </ul>
                    <input value={newRole} onChange={e => setNewRole(e.target.value)} placeholder="New role name" />
                    <button onClick={handleCreateRole}>Create Role</button>
                </div>
                <div>
                    <h3>Permissions</h3>
                    <ul>
                        {permissions.map(p => (
                            <li key={p.id}>{p.name} <button onClick={() => handleDeletePermission(p.id)}>Delete</button></li>
                        ))}
                    </ul>
                    <input value={newPermission} onChange={e => setNewPermission(e.target.value)} placeholder="New permission name" />
                    <button onClick={handleCreatePermission}>Create Permission</button>
                </div>
            </div>
            <div style={{ marginTop: 32 }}>
                <h3>Assign Roles to Users</h3>
                <select value={selectedUser} onChange={e => setSelectedUser(e.target.value)}>
                    <option value="">Select user</option>
                    {users.map(u => <option key={u.id} value={u.id}>{u.name} ({u.email})</option>)}
                </select>
                <select value={selectedRole} onChange={e => setSelectedRole(e.target.value)}>
                    <option value="">Select role</option>
                    {roles.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
                </select>
                <button onClick={handleAssignRole}>Assign</button>
                <button onClick={handleRemoveRole}>Remove</button>
            </div>
            <div style={{ marginTop: 32 }}>
                <h3>Assign Permissions to Roles</h3>
                <select value={selectedRole} onChange={e => setSelectedRole(e.target.value)}>
                    <option value="">Select role</option>
                    {roles.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
                </select>
                <select value={selectedPermission} onChange={e => setSelectedPermission(e.target.value)}>
                    <option value="">Select permission</option>
                    {permissions.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
                <button onClick={handleAssignPermission}>Assign</button>
                <button onClick={handleRemovePermission}>Remove</button>
            </div>
        </div>
    );
}
