class NotificationService {
  constructor(notification) {
    this.notification = notification
  }

  /**
   * 发送通知
   * @param {string} title - 通知标题
   * @param {string} content - 通知内容
   * @param {string} type - 通知类型 (info/success/warning/error)
   */
  send(title, content, type = 'info') {
    this.notification[type]({
      title,
      content,
      duration: 5000,
      keepAliveOnHover: true
    })
  }

  info(title, content) {
    this.send(title, content, 'info')
  }

  success(title, content) {
    this.send(title, content, 'success')
  }

  warning(title, content) {
    this.send(title, content, 'warning')
  }

  error(title, content) {
    this.send(title, content, 'error')
  }
}

export function setupNotification(notification) {
  window.$notify = new NotificationService(notification)
} 