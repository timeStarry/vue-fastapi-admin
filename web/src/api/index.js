import { request } from '@/utils'
import monitor from './monitor'
import notification from './notification'

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
  
  // 工单模块API
  // 工单列表与基础操作
  getTicketList: (params = {}) => request.get('/ticket/list', { params }),
  getTicketById: (params = {}) => request.get('/ticket/get', { params }),
  createTicket: (data = {}) => request.post('/ticket/create', data),
  updateTicket: (data = {}) => request.post('/ticket/update', data),
  deleteTicket: (params = {}) => request.delete('/ticket/delete', { params }),
  
  // 工单处理操作
  processTicket: (data = {}) => request.post('/ticket/process', data),
  transferTicket: (data = {}) => request.post('/ticket/transfer', data),
  
  // 工单附件上传
  uploadAttachment: (data = {}, onUploadProgress) => 
    request.post('/ticket/upload', data, { 
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress,
    }),
  
  // 工单统计数据
  getTicketStatistics: (params = {}) => request.get('/ticket/statistics', { params }),
  
  // 监控模块API
  // 主机监控相关
  getHostList: (params = {}) => request.get('/monitor/host', { params }),
  getHostById: (params = {}) => request.get(`/monitor/host/${params.host_id}`),
  createHost: (data = {}) => request.post('/monitor/host', data),
  updateHost: (host_id, data = {}) => request.put(`/monitor/host/${host_id}`, data),
  deleteHost: (host_id) => request.delete(`/monitor/host/${host_id}`),
  pingHost: (host_id) => request.post(`/monitor/host/${host_id}/ping`),
  getMRTGData: (host_id, params = {}) => request.get(`/monitor/host/${host_id}/mrtg`, { params }),
  generateMockMRTGData: (host_id) => request.post(`/monitor/host/${host_id}/mrtg/mock`),
  
  // 服务监控相关
  getServiceList: (params = {}) => request.get('/monitor/service', { params }),
  getServiceById: (params = {}) => request.get(`/monitor/service/${params.service_id}`),
  createService: (data = {}) => request.post('/monitor/service', data),
  updateService: (service_id, data = {}) => request.put(`/monitor/service/${service_id}`, data),
  deleteService: (service_id) => request.delete(`/monitor/service/${service_id}`),
  checkService: (service_id) => request.post(`/monitor/service/${service_id}/check`),
  getServiceHistory: (service_id, params = {}) => request.get(`/monitor/service/${service_id}/history`, { params }),
  
  // 监控面板相关
  getDashboardData: () => request.get('/monitor/dashboard'),
  
  // 告警相关
  getAlertList: (params = {}) => request.get('/monitor/alert', { params }),
  getAlertById: (alert_id) => request.get(`/monitor/alert/${alert_id}`),
  updateAlert: (alert_id, data = {}) => request.put(`/monitor/alert/${alert_id}`, data),
  
  // 监控模块API
  ...monitor,
  
  // 通知模块API
  ...notification,
}
