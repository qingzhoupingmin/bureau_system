// 市政工程管理系统 API 客户端

// 生产环境使用空字符串（同源请求），开发环境由 Vite proxy 处理
const API_BASE_URL = '';

// 获取 token
const getToken = () => localStorage.getItem('token');
const getUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

// 通用请求方法
const request = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getToken();

  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.message || '请求失败');
    }

    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

// 认证 API
export const authAPI = {
  login: (username, password) =>
    request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  logout: (userId) =>
    request(`/api/auth/logout?user_id=${userId}`, {
      method: 'POST',
    }),

  changePassword: (userId, oldPassword, newPassword) =>
    request('/api/auth/password', {
      method: 'PUT',
      body: JSON.stringify({ user_id: userId, old_password: oldPassword, new_password: newPassword }),
    }),
};

// 用户 API
export const usersAPI = {
  getUsers: (page = 1, pageSize = 20, role = null) => {
    let url = `/api/users?page=${page}&page_size=${pageSize}`;
    if (role) url += `&role=${role}`;
    return request(url);
  },

  getUser: (userId) => request(`/api/users/${userId}`),

  createUser: (userData) =>
    request('/api/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),

  updateUser: (userId, userData) =>
    request(`/api/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    }),

  deleteUser: (userId) =>
    request(`/api/users/${userId}`, {
      method: 'DELETE',
    }),
};

// 资产 API
export const assetsAPI = {
  getAssets: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/assets${query ? '?' + query : ''}`);
  },

  getAsset: (assetId) => request(`/api/assets/${assetId}`),

  createAsset: (assetData) =>
    request('/api/assets', {
      method: 'POST',
      body: JSON.stringify(assetData),
    }),

  updateAsset: (assetId, assetData) =>
    request(`/api/assets/${assetId}`, {
      method: 'PUT',
      body: JSON.stringify(assetData),
    }),

  deleteAsset: (assetId) =>
    request(`/api/assets/${assetId}`, {
      method: 'DELETE',
    }),

  getStatistics: () => request('/api/assets/statistics'),

  getLevelStats: () => request('/api/assets/level-stats'),

  getApplications: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/assets/applications${query ? '?' + query : ''}`);
  },

  approveApplication: (appId, approverId, comment = '') =>
    request(`/api/assets/applications/${appId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ approver_id: approverId, comment }),
    }),

  rejectApplication: (appId, approverId, comment = '') =>
    request(`/api/assets/applications/${appId}/reject`, {
      method: 'POST',
      body: JSON.stringify({ approver_id: approverId, comment }),
    }),
};

// 预算 API
export const budgetsAPI = {
  getBudgets: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/budgets${query ? '?' + query : ''}`);
  },

  getBudget: (budgetId) => request(`/api/budgets/${budgetId}`),

  createBudget: (budgetData) =>
    request('/api/budgets', {
      method: 'POST',
      body: JSON.stringify(budgetData),
    }),

  updateBudget: (budgetId, budgetData) =>
    request(`/api/budgets/${budgetId}`, {
      method: 'PUT',
      body: JSON.stringify(budgetData),
    }),

  deleteBudget: (budgetId) =>
    request(`/api/budgets/${budgetId}`, {
      method: 'DELETE',
    }),

  getStatistics: () => request('/api/budgets/statistics'),
};

// 公文 API
export const documentsAPI = {
  getDocuments: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/documents${query ? '?' + query : ''}`);
  },

  getDocument: (docId) => request(`/api/documents/${docId}`),

  createDocument: (docData) =>
    request('/api/documents', {
      method: 'POST',
      body: JSON.stringify(docData),
    }),

  updateDocument: (docId, docData) =>
    request(`/api/documents/${docId}`, {
      method: 'PUT',
      body: JSON.stringify(docData),
    }),

  deleteDocument: (docId) =>
    request(`/api/documents/${docId}`, {
      method: 'DELETE',
    }),
};

// 消息 API
export const messagesAPI = {
  getMessages: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/messages${query ? '?' + query : ''}`);
  },

  getUnreadCount: (userId) => request(`/api/messages/unread-count?user_id=${userId}`),

  sendMessage: (messageData) =>
    request('/api/messages', {
      method: 'POST',
      body: JSON.stringify(messageData),
    }),

  markAsRead: (messageId) =>
    request(`/api/messages/${messageId}/read`, {
      method: 'PUT',
    }),
};

// 组织 API
export const organizationsAPI = {
  getOrganizations: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/api/organizations${query ? '?' + query : ''}`);
  },

  getOrganization: (orgId) => request(`/api/organizations/${orgId}`),

  createOrganization: (orgData) =>
    request('/api/organizations', {
      method: 'POST',
      body: JSON.stringify(orgData),
    }),

  updateOrganization: (orgId, orgData) =>
    request(`/api/organizations/${orgId}`, {
      method: 'PUT',
      body: JSON.stringify(orgData),
    }),

  deleteOrganization: (orgId) =>
    request(`/api/organizations/${orgId}`, {
      method: 'DELETE',
    }),
};

export { getToken, getUser, API_BASE_URL };