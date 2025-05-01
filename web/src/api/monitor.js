import { request } from '@/utils'

// 主机相关的API
export function getHostList(params) {
  return request({
    url: '/monitor/host',
    method: 'get',
    params
  })
}

export function createHost(data) {
  return request({
    url: '/monitor/host',
    method: 'post',
    data
  })
}

export function getHostById(params) {
  return request({
    url: `/monitor/host/${params.host_id}`,
    method: 'get'
  })
}

export function updateHost(hostId, data) {
  return request({
    url: `/monitor/host/${hostId}`,
    method: 'put',
    data
  })
}

export function deleteHost(hostId) {
  return request({
    url: `/monitor/host/${hostId}`,
    method: 'delete'
  })
}

export function pingHost(hostId) {
  return request({
    url: `/monitor/host/${hostId}/ping`,
    method: 'post'
  })
}

export function getMRTGData(hostId, params) {
  return request({
    url: `/monitor/host/${hostId}/mrtg`,
    method: 'get',
    params
  })
}

export function generateMockMRTGData(hostId) {
  return request({
    url: `/monitor/host/${hostId}/mrtg/mock`,
    method: 'post'
  })
}

// 服务相关API
export function getServiceList(params) {
  return request({
    url: '/monitor/service',
    method: 'get',
    params
  })
}

export function createService(data) {
  return request({
    url: '/monitor/service',
    method: 'post',
    data
  })
}

export function getServiceById(serviceId) {
  return request({
    url: `/monitor/service/${serviceId}`,
    method: 'get'
  })
}

export function updateService(serviceId, data) {
  return request({
    url: `/monitor/service/${serviceId}`,
    method: 'put',
    data
  })
}

export function deleteService(serviceId) {
  return request({
    url: `/monitor/service/${serviceId}`,
    method: 'delete'
  })
}

export function checkService(serviceId) {
  return request({
    url: `/monitor/service/${serviceId}/check`,
    method: 'post'
  })
}

export function getServiceHistory(serviceId, params) {
  return request({
    url: `/monitor/service/${serviceId}/history`,
    method: 'get',
    params
  })
}

// 监控面板数据
export function getDashboardData() {
  return request({
    url: '/monitor/dashboard',
    method: 'get'
  })
}

// 告警相关API
export function getAlertList(params) {
  return request({
    url: '/monitor/alert',
    method: 'get',
    params
  })
}

export function getAlertById(alertId) {
  return request({
    url: `/monitor/alert/${alertId}`,
    method: 'get'
  })
}

export function updateAlert(alertId, data) {
  return request({
    url: `/monitor/alert/${alertId}`,
    method: 'put',
    data
  })
}

export default {
  getHostList,
  createHost,
  getHostById,
  updateHost,
  deleteHost,
  pingHost,
  getMRTGData,
  generateMockMRTGData,
  getServiceList,
  createService,
  getServiceById,
  updateService,
  deleteService,
  checkService,
  getServiceHistory,
  getDashboardData,
  getAlertList,
  getAlertById,
  updateAlert
} 