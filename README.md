# 人事行政一体化 HR 系统

一个面向中小企业的人事行政一体化管理系统，覆盖员工管理、考勤报表、绩效管理、薪酬核算、审批中心、行政资产与 AI 辅助能力。

## 项目概览

- 前端：`Vue 3` + `Vite` + `Element Plus` + `Pinia`
- 后端：`FastAPI` + `Pydantic` + `SQLModel`
- 数据库：开发/测试支持 `SQLite`，可切换到 `MongoDB`
- AI：支持接入 Doubao Seed 1.6 兼容接口
- 导入导出：支持 Excel 解析与导出

## 目录结构

```text
HR系统/
├─ frontend/                 # 前端项目
│  ├─ src/
│  │  ├─ api/                # 接口请求封装
│  │  ├─ layout/             # 主布局
│  │  ├─ mock/               # 本地开发 mock 数据与 devApi 兜底
│  │  ├─ router/             # 路由与菜单
│  │  ├─ stores/             # Pinia 状态管理
│  │  ├─ utils/              # 工具函数
│  │  └─ views/              # 页面视图
│  ├─ package.json
│  └─ .env.example
├─ backend/                  # 后端项目
│  ├─ app/
│  │  ├─ api/routes/         # 各业务模块接口
│  │  ├─ core/               # 配置
│  │  ├─ db/                 # SQLite / MongoDB 适配层
│  │  ├─ repositories/       # 数据访问层
│  │  ├─ services/           # 业务服务层
│  │  └─ utils/              # 响应与 AI 工具
│  ├─ requirements.txt
│  └─ main.py
├─ 产品需求文档.mdc
├─ 架构设计文档.mdc
└─ .env.example
```

## 当前功能

- 员工管理
  - 员工档案增删改查
  - 部门/岗位维护
  - 附件上传、预览、下载
  - 基础资料校验
- 考勤管理
  - 考勤 Excel 导入与解析
  - 部门汇总报表
  - 考勤明细查看
- 绩效管理
  - 绩效列表、详情、编辑、导入
  - AI 指标生成、AI 评分、AI 诊断
- 薪酬核算
  - 月度工资汇总
  - 一键核算
  - 工资表导出
- 审批中心
  - 审批列表、详情、单条/批量审批
  - 资产类审批通过后同步行政资产数据
- 行政管理
  - 行政资产台账与明细展示
- AI 能力
  - 员工信息体检
  - 人力结构报表
  - 绩效/考勤 AI 分析

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd HR系统
```

### 2. 配置环境变量

根目录已有示例文件：`.env.example`

你可以先复制为根目录 `.env`：

```bash
cp .env.example .env
```

Windows PowerShell 可手动复制或新建 `.env`。

> 注意：示例里的 AI Key / URL 请按你自己的环境替换，不建议直接把真实密钥提交到仓库。

---

## 前端启动

### 安装依赖

```bash
cd frontend
npm install
```

### 启动开发环境

```bash
npm run dev
```

默认访问：

- `http://localhost:5173`

### 前端环境变量

参考 `frontend/.env.example`：

```env
VITE_APP_TITLE=人事行政一体化HR系统
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_BRAND=YUHO HR
VITE_CLOUDBASE_ENV_ID=your-cloudbase-env-id
```

### 开发态本地数据说明

当前前端增加了开发态本地数据兜底层，方便在后端未完全联通时调试员工、审批、绩效、薪酬、考勤等模块。

- 开发环境下默认可使用本地 mock 数据
- 页面右上角出现 `DEV MOCK` 标签时，表示当前看到的是本地开发数据
- 如果你要强制连接真实后端接口，设置：

```env
VITE_FORCE_REMOTE_API=true
```

然后重启前端即可。

---

## 后端启动

### 安装依赖

建议使用 Python 3.11+。

```bash
cd backend
pip install -r requirements.txt
```

### 启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

默认地址：

- API：`http://localhost:8000`
- OpenAPI：`http://localhost:8000/docs`

### 后端环境变量

根目录 `.env.example` 中已包含主要配置：

```env
APP_NAME=人事行政一体化HR系统
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
CORS_ORIGINS=http://localhost:5173,https://your-cloudbase-domain.com

DB_DRIVER=sqlite
SQLITE_PATH=./data/hr_system.db
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=hr_system

ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_API_KEY=your-api-key
ARK_MODEL=Yuho/ep-20260121115833-nw6t4
```

---

## 数据库切换

项目后端已做数据库适配层，支持在 `SQLite` 与 `MongoDB` 之间切换。

### 使用 SQLite

```env
DB_DRIVER=sqlite
SQLITE_PATH=./data/hr_system.db
```

适合：

- 本地开发
- 原型验证
- 快速测试

### 使用 MongoDB

```env
DB_DRIVER=mongodb
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=hr_system
```

适合：

- 更接近生产环境
- 后续云端部署

---

## 常见开发说明

### 1. 为什么我改了 `frontend/src/mock/data.js`，页面却没变化？

因为大部分业务页面默认走 `@/api/modules` 对应的接口请求，不是直接读取 `mock/data.js`。

如果你当前处于开发态 mock 模式，页面数据由：

- `frontend/src/mock/devApi.js`

统一兜底。

### 2. `DEV MOCK` 会不会影响以后切数据库？

不会影响真实数据库结构和后端切换逻辑，但会影响你“当前看到的数据来源”。

联调真实后端时，请设置：

```env
VITE_FORCE_REMOTE_API=true
```

### 3. 审批通过后的资产同步在哪里？

相关前端逻辑位于：

- `frontend/src/utils/assetApprovalSync.js`
- `frontend/src/views/hr/HRApprovalsView.vue`

---

## 主要接口模块

后端接口位于：`backend/app/api/routes/`

包含：

- `auth.py`
- `dashboard.py`
- `employees.py`
- `attendance.py`
- `performance.py`
- `payroll.py`
- `approvals.py`
- `administration.py`
- `reports.py`
- `ai.py`

---

## 构建

### 前端构建

```bash
cd frontend
npm run build
```

### 后端生产启动示例

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 文档参考

仓库内已包含：

- `产品需求文档.mdc`
- `架构设计文档.mdc`
- `美术需求文档.mdc`
- `测试文档.md`

如果你要进一步完善部署、测试或接口说明，建议后续继续补充：

- 部署文档
- API 文档说明
- 数据库迁移说明
- 测试账号说明

---

## License

如需开源发布，可在此处补充许可证信息。
