import { request } from '@/utils'

// 通知队列API
export function getQueueList(params = {}) {
  return request.get('/notification/queue', { params }).then(res => {
    return {
      items: res.data,
      total: res.total,
      page: res.page,
      page_size: res.page_size
    }
  })
}

export function createNotification(data = {}) {
  return request.post('/notification/queue', data)
}

export function createFromTemplate(data = {}) {
  return request.post('/notification/queue/from-template', data)
}

export function getNotification(id) {
  return request.get(`/notification/queue/${id}`).then(res => {
    return res.data;
  });
}

export function updateNotification(id, data = {}) {
  return request.put(`/notification/queue/${id}`, data)
}

export function deleteNotification(id) {
  return request.delete(`/notification/queue/${id}`)
}

// 通知渠道API
export function getChannelList(params = {}) {
  return request.get('/notification/channel', { params }).then(res => {
    return {
      items: res.data,
      total: res.total,
      page: res.page,
      page_size: res.page_size
    }
  })
}

export function createChannel(data = {}) {
  return request.post('/notification/channel', data)
}

export function getChannel(id) {
  return request.get(`/notification/channel/${id}`)
}

export function updateChannel(id, data = {}) {
  return request.put(`/notification/channel/${id}`, data)
}

export function deleteChannel(id) {
  return request.delete(`/notification/channel/${id}`)
}

// 测试通知渠道
export function testChannel(data = {}) {
  return request.post('/notification/channel/test', data)
}

// 通知模板API
export function getTemplateList(params = {}) {
  return request.get('/notification/template', { params }).then(res => {
    return {
      items: res.data,
      total: res.total,
      page: res.page,
      page_size: res.page_size
    }
  })
}

export function createTemplate(data = {}) {
  return request.post('/notification/template', data)
}

export function getTemplate(id) {
  return request.get(`/notification/template/${id}`)
}

export function getTemplateByKey(key) {
  return request.get(`/notification/template/key/${key}`)
}

export function updateTemplate(id, data = {}) {
  return request.put(`/notification/template/${id}`, data)
}

export function deleteTemplate(id) {
  return request.delete(`/notification/template/${id}`)
}

// 通知设置API
export function getUserSettings(userId) {
  return request.get(`/notification/setting/user/${userId}`).then(res => {
    return res.data;
  });
}

export function getUserSourceSetting(userId, source) {
  return request.get(`/notification/setting/user/${userId}/source/${source}`).then(res => {
    return res.data;
  });
}

export function createOrUpdateSetting(data = {}) {
  return request.post('/notification/setting', data).then(res => {
    return res.data;
  });
}

export function deleteSetting(id) {
  return request.delete(`/notification/setting/${id}`)
}

// 集成API
export function addMonitorAlertToQueue(alertId) {
  return request.post(`/notification/monitor-alert/${alertId}`)
}

export function addTicketStatusChangeToQueue(ticketId, oldStatus, newStatus) {
  return request.post(`/notification/ticket-status-change/${ticketId}`, {
    old_status: oldStatus,
    new_status: newStatus
  })
}

export default {
  // 队列相关
  getQueueList,
  createNotification,
  createFromTemplate,
  getNotification,
  updateNotification,
  deleteNotification,
  
  // 渠道相关
  getChannelList,
  createChannel,
  getChannel,
  updateChannel,
  deleteChannel,
  testChannel,
  
  // 模板相关
  getTemplateList,
  createTemplate,
  getTemplate,
  getTemplateByKey,
  updateTemplate,
  deleteTemplate,
  
  // 设置相关
  getUserSettings,
  getUserSourceSetting,
  createOrUpdateSetting,
  deleteSetting,
  
  // 集成API
  addMonitorAlertToQueue,
  addTicketStatusChangeToQueue
} 