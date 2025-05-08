import i18n from '~/i18n'
const { t } = i18n.global

const Layout = () => import('@/layout/index.vue')

export default {
  name: 'Agno',
  path: '/agno',
  component: Layout,
  meta: {
    title: 'Agno AI',
    icon: 'material-symbols:smart-toy-outline',
    order: 5,
  },
  children: [
    {
      name: 'AgnoAssistant',
      path: 'assistant',
      component: () => import('@/views/agno/assistant/index.vue'),
      meta: {
        title: t('views.agno.label_assistant'),
        icon: 'material-symbols:support-agent',
      },
    },
    {
      name: 'AgnoChat',
      path: 'chat',
      component: () => import('@/views/agno/chat/list.vue'),
      meta: {
        title: t('views.agno.label_chat'),
        icon: 'material-symbols:chat-outline',
      },
    },
    {
      name: 'AgnoChatDetail',
      path: 'chat/:id',
      component: () => import('@/views/agno/chat/index.vue'),
      meta: {
        title: t('views.agno.label_chat_detail'),
        icon: 'material-symbols:chat',
        hideInMenu: true,
      },
      props: (route) => {
        return { 
          id: route.params.id || null 
        }
      },
    },
    {
      name: 'AgnoKnowledge',
      path: 'knowledge',
      component: () => import('@/views/agno/knowledge/index.vue'),
      meta: {
        title: t('views.agno.label_knowledge'),
        icon: 'material-symbols:menu-book-outline',
      },
    }
  ],
} 