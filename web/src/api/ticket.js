import request from '@/utils/request'

// 获取工单列表
export function getTicketList(params) {
  return request({
    url: '/tickets/list',
    method: 'get',
    params
  })
}

// 获取工单详情
export function getTicket(params) {
  return request({
    url: '/tickets/get',
    method: 'get',
    params
  })
}

// 创建工单
export function createTicket(data) {
  return request({
    url: '/tickets/create',
    method: 'post',
    data
  })
}

// 更新工单
export function updateTicket(data) {
  return request({
    url: '/tickets/update',
    method: 'post',
    data
  })
}

// 处理工单
export function processTicket(data) {
  return request({
    url: '/tickets/process',
    method: 'post',
    data
  })
}

// 删除工单
export function deleteTicket(params) {
  return request({
    url: '/tickets/delete',
    method: 'delete',
    params
  })
}

// 上传附件
export function uploadTicketFile(data) {
  return request({
    url: '/tickets/upload',
    method: 'post',
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    data
  })
}

// 获取统计数据
export function getTicketStatistics(params) {
  return request({
    url: '/tickets/statistics',
    method: 'get',
    params
  })
}

// 智能生成工单
export function generateTicket(data) {
  return request({
    url: '/tickets/generate',
    method: 'post',
    data
  })
}

export default {
  getTicketList,
  getTicket,
  createTicket,
  updateTicket,
  processTicket,
  deleteTicket,
  uploadTicketFile,
  getTicketStatistics,
  generateTicket
} 