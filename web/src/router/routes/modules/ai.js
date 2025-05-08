import i18n from '~/i18n'
const { t } = i18n.global

import Layout from '@/layout/index.vue'

export default {
  name: 'AI',
  path: '/ai',
  component: Layout,
  meta: {
    title: 'AI助手',
    icon: 'material-symbols:smart-toy-outline',
    order: 5,
  },
  children: [
    {
      name: 'AIAssistant',
      path: 'assistant',
      component: () => import('@/views/agno/assistant/index.vue'),
      meta: {
        title: t('views.agno.label_assistant'),
        icon: 'material-symbols:support-agent',
      },
    },
    {
      name: 'AIChat',
      path: 'chat',
      component: () => import('@/views/agno/chat/list.vue'),
      meta: {
        title: t('views.agno.label_chat'),
        icon: 'material-symbols:chat-outline',
      },
    },
    {
      name: 'AIChatDetail',
      path: 'chat',
      component: () => import('@/views/agno/chat/index.vue'),
      meta: {
        title: t('views.agno.label_chat_detail'),
        icon: 'material-symbols:chat',
        hideInMenu: true,
      },
      props: (route) => {
        console.log('AI聊天路由参数:', route.params, route.query);
        let id = null;
        if (route.query && route.query.id) {
          id = parseInt(route.query.id, 10);
        } else if (route.params && route.params.id) {
          id = parseInt(route.params.id, 10);
        }
        
        console.log('处理后的ID:', id);
        return { id };
      },
    },
    {
      name: 'AIKnowledge',
      path: 'knowledge',
      component: () => import('@/views/agno/knowledge/index.vue'),
      meta: {
        title: t('views.agno.label_knowledge'),
        icon: 'material-symbols:menu-book-outline',
      },
    }
  ],
} 