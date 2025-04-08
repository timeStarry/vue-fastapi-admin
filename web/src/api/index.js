import { request } from '@/utils'

export default {
  login: (data) => request.post('/base/access_token', data, { noNeedToken: true }),
  getUserInfo: () => request.get('/base/userinfo'),
  getUserMenu: () => request.get('/base/usermenu'),
  getUserApi: () => request.get('/base/userapi'),
  // profile
  updatePassword: (data = {}) => request.post('/base/update_password', data),
  // users
  getUserList: (params = {}) => request.get('/user/list', { params }),
  getUserById: (params = {}) => request.get('/user/get', { params }),
  createUser: (data = {}) => request.post('/user/create', data),
  updateUser: (data = {}) => request.post('/user/update', data),
  deleteUser: (params = {}) => request.delete(`/user/delete`, { params }),
  resetPassword: (data = {}) => request.post(`/user/reset_password`, data),
  // role
  getRoleList: (params = {}) => request.get('/role/list', { params }),
  createRole: (data = {}) => request.post('/role/create', data),
  updateRole: (data = {}) => request.post('/role/update', data),
  deleteRole: (params = {}) => request.delete('/role/delete', { params }),
  updateRoleAuthorized: (data = {}) => request.post('/role/authorized', data),
  getRoleAuthorized: (params = {}) => request.get('/role/authorized', { params }),
  // menus
  getMenus: (params = {}) => request.get('/menu/list', { params }),
  createMenu: (data = {}) => request.post('/menu/create', data),
  updateMenu: (data = {}) => request.post('/menu/update', data),
  deleteMenu: (params = {}) => request.delete('/menu/delete', { params }),
  // apis
  getApis: (params = {}) => request.get('/api/list', { params }),
  createApi: (data = {}) => request.post('/api/create', data),
  updateApi: (data = {}) => request.post('/api/update', data),
  deleteApi: (params = {}) => request.delete('/api/delete', { params }),
  refreshApi: (data = {}) => request.post('/api/refresh', data),
  // depts
  getDepts: (params = {}) => request.get('/dept/list', { params }),
  createDept: (data = {}) => request.post('/dept/create', data),
  updateDept: (data = {}) => request.post('/dept/update', data),
  deleteDept: (params = {}) => request.delete('/dept/delete', { params }),
  // auditlog
  getAuditLogList: (params = {}) => request.get('/auditlog/list', { params }),

  // 工单管理
  getTicketList: async (params) => await request.get('ticket/list', { params }),
  createTicket: async (data) => await request.post('ticket/create', data),
  updateTicket: async (data) => await request.put(`ticket/${data.id}`, data),
  closeTicket: async (data) => await request.delete(`ticket/${data.id}`, data),
  getTicketDetail: async (id) => await request.get(`ticket/${id}`),
  // monitor_host_group
  getHostGroups: () => request.get('/monitor/host/groups'),
  createHostGroup: (data = {}) => request.post('/monitor/host/group/create', data),
  updateHostGroup: (data = {}) => request.post(`/monitor/host/group/${data.id}`, data),
  deleteHostGroup: (params = {}) => request.delete(`/monitor/host/group/${params.id}`),
  setDefaultHostGroup: (params = {}) => request.post(`/monitor/host/group/${params.id}/set-default`),
  // monitor_host
  getMonitorHostList: (params = {}) => request.get('/monitor/host/list', { params }),
  createMonitorHost: (data = {}) => request.post('/monitor/host/create', data),
  updateMonitorHost: (data = {}) => request.post(`/monitor/host/${data.id}`, data),
  deleteMonitorHost: (params = {}) => request.delete(`/monitor/host/${params.id}`),
  testHostConnection: (data = {}) => request.post('/monitor/host/test-connection', data),
  // 工单相关接口
  getTicketList: (params = {}) => request.get('/ticket/list', { params }),
  createTicket: (data = {}) => request.post('/ticket/create', data),
  updateTicket: (data = {}) => request.post('/ticket/update', data),
  deleteTicket: (params = {}) => request.delete('/ticket/delete', { params }),
  getTicketComments: (params = {}) => request.get('/ticket/comments', { params }),
  createTicketComment: (data = {}) => request.post('/ticket/comment/create', data),
}
