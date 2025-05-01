import { Layout } from '@/layout'
import { renderIcon } from '@/utils'

/**
 * @param name 路由名称, 必须设置,且不能重名
 * @param meta 路由元信息（路由附带扩展信息）
 * @param redirect 重定向地址, 访问这个路由时,自定进行重定向
 * @param meta.disabled 禁用整个菜单
 * @param meta.title 菜单名称
 * @param meta.icon 菜单图标
 * @param meta.keepAlive 缓存该路由
 * @param meta.sort 排序越小越排前
 *
 * */
const routes = {
  path: '/monitor',
  name: 'Monitor',
  component: Layout,
  meta: {
    title: '监控管理',
    icon: renderIcon('material-symbols:monitoring'),
    sort: 3,
  },
  children: [
    {
      path: 'host',
      name: 'MonitorHost',
      component: () => import('@/views/monitor/host/index.vue'),
      meta: {
        title: '主机监控',
      },
    },
    {
      path: 'service',
      name: 'MonitorService',
      component: () => import('@/views/monitor/service/index.vue'),
      meta: {
        title: '服务监控',
      },
    },
    {
      path: 'dashboard',
      name: 'MonitorDashboard',
      component: () => import('@/views/monitor/dashboard/index.vue'),
      meta: {
        title: '监控面板',
      },
    },
    {
      path: 'config',
      name: 'MonitorConfig',
      component: () => import('@/views/monitor/config/index.vue'),
      meta: {
        title: '监控配置',
      },
    },
  ],
}

export default routes 