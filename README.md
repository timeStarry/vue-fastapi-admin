# 智能网络运维系统

基于 [vue-fastapi-admin](http://vue-fastapi-admin.com) 框架开发的智能网络运维系统，采用现代化的前后端分离架构，集成了网络设备管理、监控、配置和自动化运维等功能。

本项目是一个本科毕业设计，鄙陋之处多多海涵，仅作学习用途。关于框架和编码的更多内容请参考[vue-fastapi-admin](http://vue-fastapi-admin.com)原项目。

## 系统特性

### 技术栈
- **后端**：Python 3.11 + FastAPI 高性能异步框架
- **前端**：Vue3 + Vite + Naive UI
- **数据库**：SQLite（支持其他数据库扩展）
- **包管理**：后端使用 uv/pip，前端使用 pnpm

### 核心功能
- **网络设备管理**：支持多种网络设备的统一管理和配置
- **智能监控**：实时监控网络设备状态和性能指标
- **自动化运维**：支持网络配置的自动化部署和更新
- **权限管理**：基于 RBAC 的细粒度权限控制系统
- **动态路由**：支持动态菜单和路由配置
- **JWT 认证**：安全可靠的用户认证机制

### 智能运维能力
- **AI 助手系统**：集成大语言模型的智能助手，支持运维知识问答和引导
- **知识库管理**：内置网络设备文档知识库，支持文档的自动检索和语义理解
- **智能工单系统**：基于AI的工单分类、优先级排序和自动分配
- **多维度监控**：
  - 主机监控：支持 Ping 测试、网络流量监测和性能指标采集
  - 服务监控：支持 HTTP/HTTPS 服务状态检测和响应时间监控
  - 可视化仪表盘：实时数据展示和历史数据分析
- **智能告警系统**：基于规则的异常检测和告警通知，支持多级告警
- **自动运维工作流**：预设运维流程模板，支持常见网络故障的自动诊断和修复
- **智能日志分析**：日志聚合和异常模式识别，帮助快速定位问题
- **网络拓扑可视化**：自动发现和绘制网络拓扑图，支持交互式操作
- **智能配置管理**：
  - 配置版本控制：跟踪和管理配置变更历史
  - 配置模板：标准化配置模板库，减少手动配置错误
  - 配置分析：自动检查配置合规性和最佳实践
- **可扩展工具集成**：支持自定义工具集成，扩展智能助手能力

### 系统架构
- **前端**：采用 Vue3 组件化开发，使用 Naive UI 构建现代化界面
- **后端**：基于 FastAPI 的 RESTful API 设计，支持异步处理
- **数据库**：使用 ORM 框架进行数据管理，支持多种数据库
- **安全**：集成 JWT 认证，支持细粒度的权限控制

## 快速开始

### 环境要求
- Python 3.11+
- Node.js v18.8.0+
- Docker（可选）

### 安装部署

#### 方法一：Docker 部署（推荐）

1. 拉取镜像
```sh
docker pull mizhexiaoxiao/vue-fastapi-admin:latest 
```

2. 运行容器
```sh
docker run -d --restart=always --name=vue-fastapi-admin -p 9999:80 mizhexiaoxiao/vue-fastapi-admin
```

#### 方法二：本地部署

1. 后端部署
```sh
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.\.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py
```

2. 前端部署
```sh
cd web
pnpm install
pnpm dev
```

### 访问系统
- 地址：http://localhost:9999
- 默认账号：admin
- 默认密码：123456

## 项目结构

```
├── app                   // 后端应用目录
│   ├── api              // API 接口
│   ├── controllers      // 控制器
│   ├── core            // 核心功能
│   ├── models          // 数据模型
│   └── utils           // 工具类
├── web                  // 前端应用目录
│   ├── src             // 源代码
│   ├── public          // 静态资源
│   └── build           // 构建配置
├── deploy              // 部署相关
└── test_scripts       // 测试脚本
```

## 开发指南

### 后端开发
1. 遵循 FastAPI 最佳实践
2. 使用 Pydantic 进行数据验证
3. 采用异步编程模式
4. 遵循 RESTful API 设计规范

### 前端开发
1. 使用 Vue3 组合式 API
2. 遵循组件化开发原则
3. 使用 TypeScript 进行类型检查
4. 采用 Naive UI 组件库

## 贡献指南
1. Fork 本仓库
2. 创建特性分支
3. 提交变更
4. 发起 Pull Request

## 许可证
本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。


