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
  path: '/ticket',
  name: 'Ticket',
  component: Layout,
  meta: {
    title: '工单管理',
    icon: renderIcon('material-symbols:receipt-long'),
    sort: 2,
  },
  children: [
    {
      path: 'list',
      name: 'TicketList',
      component: () => import('@/views/ticket/list/index.vue'),
      meta: {
        title: '工单列表',
      },
    },
    {
      path: 'dashboard',
      name: 'TicketDashboard',
      component: () => import('@/views/ticket/dashboard/index.vue'),
      meta: {
        title: '工单面板',
      },
    },
    {
      path: 'process',
      name: 'TicketProcess',
      component: () => import('@/views/ticket/process/index.vue'),
      meta: {
        title: '工单处理',
        hidden: true, // 在菜单中隐藏
      },
    },
  ],
}

export default routes 