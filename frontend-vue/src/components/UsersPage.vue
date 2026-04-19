<template>
  <div class="settings-page">
    <div class="settings-inner" style="max-width: 640px">
      <h2 class="settings-title">User Management</h2>

      <div class="users-toolbar">
        <button class="btn btn-copy" @click="openAdd">Add user</button>
        <span v-if="error" class="users-error">{{ error }}</span>
      </div>

      <table class="users-table">
        <thead>
          <tr>
            <th>Username</th>
            <th>Role</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.username }}</td>
            <td>
              <span :class="['role-badge', u.is_admin ? 'role-badge--admin' : 'role-badge--user']">
                {{ u.is_admin ? 'admin' : 'user' }}
              </span>
            </td>
            <td class="users-actions">
              <button class="btn btn-sm" @click="openEdit(u)">Edit</button>
              <button
                class="btn btn-sm btn-danger"
                :disabled="u.id === auth.userId"
                @click="confirmDelete(u)"
              >Delete</button>
            </td>
          </tr>
          <tr v-if="!users.length">
            <td colspan="3" style="text-align:center;color:var(--text-muted)">No users found</td>
          </tr>
        </tbody>
      </table>

      <!-- Add / Edit modal -->
      <div v-if="modal" class="modal-backdrop" @click.self="closeModal">
        <div class="modal-box">
          <h3 class="modal-title">{{ modal === 'add' ? 'Add user' : 'Edit user' }}</h3>
          <form @submit.prevent="handleSubmit" novalidate>
            <label class="auth-label">Username</label>
            <input v-model="form.username" class="auth-input" autocomplete="off" />

            <label class="auth-label">{{ modal === 'add' ? 'Password' : 'New password (leave blank to keep)' }}</label>
            <input v-model="form.password" type="password" class="auth-input" autocomplete="new-password" placeholder="••••••••" />

            <label class="auth-label" style="flex-direction:row;gap:8px;align-items:center;cursor:pointer">
              <input type="checkbox" v-model="form.isAdmin" />
              Admin
            </label>

            <div v-if="formError" class="auth-error" style="margin-top:10px">{{ formError }}</div>

            <div class="modal-footer">
              <button type="button" class="btn" @click="closeModal">Cancel</button>
              <button type="submit" class="btn btn-copy" :disabled="saving">
                {{ saving ? 'Saving…' : 'Save' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Delete confirm modal -->
      <div v-if="deleteTarget" class="modal-backdrop" @click.self="deleteTarget = null">
        <div class="modal-box">
          <h3 class="modal-title">Delete user</h3>
          <p style="color:var(--text);margin-bottom:20px">
            Delete <strong>{{ deleteTarget.username }}</strong>? This cannot be undone.
          </p>
          <div class="modal-footer">
            <button class="btn" @click="deleteTarget = null">Cancel</button>
            <button class="btn btn-danger" :disabled="saving" @click="handleDelete">
              {{ saving ? 'Deleting…' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { apiListUsers, apiCreateUser, apiUpdateUser, apiDeleteUser } from '../api/client.js'

const auth = useAuthStore()

const users = ref([])
const error = ref('')
const modal = ref(null) // 'add' | 'edit'
const editTarget = ref(null)
const deleteTarget = ref(null)
const saving = ref(false)
const formError = ref('')

const form = ref({ username: '', password: '', isAdmin: false })

onMounted(load)

async function load() {
  try {
    users.value = await apiListUsers()
    error.value = ''
  } catch (err) {
    error.value = err.message
  }
}

function openAdd() {
  form.value = { username: '', password: '', isAdmin: false }
  formError.value = ''
  modal.value = 'add'
}

function openEdit(u) {
  editTarget.value = u
  form.value = { username: u.username, password: '', isAdmin: u.is_admin }
  formError.value = ''
  modal.value = 'edit'
}

function closeModal() {
  modal.value = null
  editTarget.value = null
  formError.value = ''
}

function confirmDelete(u) {
  deleteTarget.value = u
}

async function handleSubmit() {
  formError.value = ''
  if (!form.value.username.trim()) { formError.value = 'Username required.'; return }
  if (modal.value === 'add' && form.value.password.length < 8) {
    formError.value = 'Password must be at least 8 characters.'; return
  }
  if (modal.value === 'edit' && form.value.password && form.value.password.length < 8) {
    formError.value = 'Password must be at least 8 characters.'; return
  }

  saving.value = true
  try {
    if (modal.value === 'add') {
      await apiCreateUser(form.value.username.trim(), form.value.password, form.value.isAdmin)
    } else {
      const updates = { username: form.value.username.trim(), is_admin: form.value.isAdmin }
      if (form.value.password) updates.password = form.value.password
      await apiUpdateUser(editTarget.value.id, updates)
    }
    await load()
    closeModal()
  } catch (err) {
    formError.value = err.message
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  saving.value = true
  try {
    await apiDeleteUser(deleteTarget.value.id)
    deleteTarget.value = null
    await load()
  } catch (err) {
    error.value = err.message
    deleteTarget.value = null
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.settings-page {
  flex: 1;
  overflow: auto;
  padding: 32px 28px;
  display: flex;
  justify-content: center;
}

.settings-inner {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.settings-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-strong);
  letter-spacing: -0.3px;
  margin-bottom: 24px;
}

.users-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.users-error {
  font-size: 12px;
  color: #f87171;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.users-table th {
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 6px 8px;
  border-bottom: 1px solid var(--border);
}

.users-table td {
  padding: 10px 8px;
  border-bottom: 1px solid var(--border);
  color: var(--text);
}

.users-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.role-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.role-badge--admin {
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.3);
}

.role-badge--user {
  background: var(--chip-bg);
  color: var(--text-muted);
  border: 1px solid var(--border);
}

.btn-sm {
  font-size: 12px;
  padding: 4px 10px;
}

.btn-danger {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
  border-color: rgba(239, 68, 68, 0.3);
}

.btn-danger:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-box {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  padding: 28px;
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.modal-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-strong);
  margin-bottom: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 20px;
}
</style>
