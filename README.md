# 人事行政一体化 HR 系统

一个面向中小企业的人事、行政与审批协同场景的一体化管理系统，覆盖员工档案、考勤管理、绩效管理、薪酬核算、审批流转、行政资产管理与 AI 辅助分析等核心业务模块。项目采用前后端分离架构，前端提供多角色业务工作台，后端负责业务规则、数据存储、审批联动与智能分析能力输出。

---

## 项目简介

本项目围绕企业内部人力与行政管理场景构建，目标是提供一套可覆盖员工、部门经理与 HR 日常协同流程的业务平台。系统以角色视角组织功能入口，强调业务闭环、数据流转与多模块联动，支持从员工发起申请，到经理审核，再到 HR 汇总、核算与管理的完整链路。

系统当前聚焦以下三类核心角色：

- 员工：个人信息维护、考勤查询、薪资查询、绩效提交、申请发起
- 部门经理：部门员工管理、考勤查看、绩效审核、审批处理
- HR / 人事行政：员工档案管理、考勤报表、绩效管理、薪酬核算、审批中心、行政资产管理

---

## 核心能力

### 1. 员工管理

- 员工档案增删改查
- 部门与岗位元数据维护
- 员工证件照与档案附件管理
- 员工基础资料完整性校验
- 员工个人档案自助维护

### 2. 考勤管理

- 考勤总览与部门汇总
- 考勤明细展示
- Excel 考勤导入与解析
- 异常考勤识别与统计
- 请假、补卡等记录与考勤联动

### 3. 绩效管理

- 员工月度绩效提交
- 部门经理绩效评分与审核
- HR 绩效复核与发布
- 绩效导入、导出与明细管理
- 绩效分布规则校验
- AI 辅助评分、评论生成与绩效诊断

### 4. 薪酬核算

- 基于员工档案、考勤、请假、绩效记录进行月度薪资核算
- 支持应发工资、个税、社保、公积金、加班工资、请假扣款等维度计算
- HR 端薪酬总览
- 员工端工资条查询与导出

### 5. 审批中心

- 人事审批、资产审批、行政审批、综合审批统一收口
- 单条审批与批量审批
- 审批详情与历史流转可视化
- 请假、补卡、资产申请、行政资源申请等统一接入审批流
- 审批通过后联动业务数据状态更新

### 6. 行政与资产管理

- 行政资产汇总
- 办公用品领用
- 固定资产领用
- 会议室、公章、用车等行政资源申请
- 审批流与资产台账联动

### 7. AI 辅助能力

- 员工信息体检
- 人力结构分析报表
- 绩效自动评分
- 绩效评价生成
- 绩效诊断与分布分析
- 考勤汇总分析
- 智能问答助手

---

## 业务流程设计

系统以企业内部典型协同链路为基础进行设计，形成以下闭环：

### 员工申请闭环

员工发起请假、补卡、资产领用、行政资源申请等业务后，系统自动生成审批记录，并依据规则进入对应审批链路。

### 绩效流转闭环

员工提交月度绩效后，由部门经理完成评分与评价，再进入 HR 复核与发布流程，形成完整绩效闭环。

### 薪酬核算闭环

系统汇总员工档案、考勤记录、请假记录与绩效结果，统一输出薪酬核算结果，并同步至员工工资查询页面。

### 角色协同闭环

- 员工侧负责数据输入与业务发起
- 经理侧负责部门维度审核与评价
- HR 侧负责全局管理、汇总、审批与核算

---

## 技术架构

### 前端技术栈

- Vue 3
- Vite
- Element Plus
- Pinia
- Vue Router
- Axios
- xlsx

### 后端技术栈

- FastAPI
- Pydantic v2
- SQLModel
- PyJWT
- openpyxl
- python-multipart
- PyMuPDF

### 数据存储

- SQLite
- MongoDB

### AI 接入

- 兼容 Ark / Doubao 风格接口
- 支持智能分析、文本生成与业务辅助决策

---

## 系统架构说明

项目采用前后端分离架构。

### 前端职责

前端负责：

- 多角色界面与菜单组织
- 业务页面交互
- 审批详情展示
- 表格展示与导出
- 员工、经理、HR 三端工作台视图呈现

### 后端职责

后端负责：

- 统一接口编排
- 权限控制与角色访问范围限制
- 审批流逻辑
- 绩效与薪酬规则计算
- 仓储层封装与多数据源适配
- AI 服务调用与结果落库

### 数据访问层设计

系统通过仓储层对 SQLite / MongoDB 做统一封装，业务层无需关心底层存储实现，从而具备较好的扩展性与部署灵活性。

---

## 目录结构

```text
HR系统/
├─ frontend/
│  ├─ src/
│  │  ├─ api/                    # 接口封装
│  │  ├─ components/             # 公共组件
│  │  ├─ constants/              # 菜单与角色常量
│  │  ├─ layout/                 # 布局组件
│  │  ├─ router/                 # 路由配置
│  │  ├─ stores/                 # 状态管理
│  │  ├─ utils/                  # 工具函数
│  │  └─ views/                  # 页面视图
│  ├─ package.json
│  └─ .env.example
├─ backend/
│  ├─ app/
│  │  ├─ api/routes/             # 业务接口
│  │  ├─ core/                   # 配置层
│  │  ├─ db/                     # 数据库适配层
│  │  ├─ models/                 # 实体定义
│  │  ├─ performance/            # 绩效模块拆分子域
│  │  ├─ repositories/           # 仓储层
│  │  ├─ schemas/                # 数据模型
│  │  ├─ security/               # 鉴权模块
│  │  ├─ services/               # 服务层
│  │  └─ utils/                  # 公共工具
│  ├─ requirements.txt
│  └─ .env.example
├─ README.md
└─ .env.example
```

---

## 主要模块说明

### 前端页面模块

#### 员工端

- `frontend/src/views/employee/EmployeeProfileView.vue`
- `frontend/src/views/employee/EmployeeArchiveView.vue`
- `frontend/src/views/employee/EmployeeAttendanceView.vue`
- `frontend/src/views/employee/EmployeePayrollView.vue`
- `frontend/src/views/employee/EmployeePerformanceView.vue`
- `frontend/src/views/employee/EmployeeApplicationsView.vue`
- `frontend/src/views/employee/EmployeeAssistantView.vue`

#### 部门经理端

- `frontend/src/views/manager/ManagerDepartmentDashboardView.vue`
- `frontend/src/views/manager/ManagerDepartmentEmployeesView.vue`
- `frontend/src/views/manager/ManagerDepartmentAttendanceView.vue`
- `frontend/src/views/manager/ManagerPerformanceEntryView.vue`
- `frontend/src/views/manager/ManagerPerformanceCheckView.vue`
- `frontend/src/views/manager/ManagerApprovalsView.vue`

#### HR 端

- `frontend/src/views/hr/HRDashboardView.vue`
- `frontend/src/views/hr/HREmployeesView.vue`
- `frontend/src/views/hr/HRAttendanceImportView.vue`
- `frontend/src/views/hr/HRAttendanceReportView.vue`
- `frontend/src/views/hr/HRPerformanceView.vue`
- `frontend/src/views/hr/HRPayrollView.vue`
- `frontend/src/views/hr/HRApprovalsView.vue`
- `frontend/src/views/hr/HRAdministrationView.vue`

### 后端接口模块

位于 `backend/app/api/routes/`：

- `auth.py`：认证与当前用户信息
- `employees.py`：员工档案、组织元数据、附件管理
- `attendance.py`：考勤总览、导入、分析
- `leaves.py`：请假申请
- `supplements.py`：补卡申请
- `performance.py`：绩效全流程管理
- `payroll.py`：薪酬汇总与核算
- `approvals.py`：审批流转与批量处理
- `administration.py`：行政与资产相关业务
- `ai.py`：AI 能力接口
- `reports.py`：报表汇总
- `dashboard.py`：总览相关接口

---

## 项目亮点

### 1. 多角色业务工作台

系统不是单一管理后台，而是围绕员工、经理、HR 三类角色构建差异化入口与权限范围，体现了完整的企业内部协同场景设计。

### 2. 业务数据联动

请假、补卡、绩效、审批、薪酬、行政资产之间存在明确的数据联动关系，能够体现业务系统设计中的跨模块协同能力。

### 3. 审批流统一抽象

不同类型的业务申请统一接入审批中心，审批节点、流转状态、历史记录与源业务数据之间保持一致，有利于后续扩展更多审批类型。

### 4. 规则引擎化处理

请假规则、绩效等级分布规则、考勤判断规则、薪资核算规则集中在服务层处理，逻辑边界清晰，具备良好的可维护性。

### 5. 可扩展的数据源设计

通过仓储层与数据库工厂封装，项目具备从本地 SQLite 向 MongoDB 平滑切换的能力，适合原型验证与后续扩展部署。

### 6. AI 与业务深度结合

AI 并非独立聊天能力，而是与员工体检、绩效诊断、报表分析等实际业务场景结合，体现了 AI 赋能业务系统的设计思路。

---

## 环境要求

### 前端

- Node.js 18+
- npm 9+

### 后端

- Python 3.11+

---

## 安装与启动

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd HR系统
```

### 2. 前端启动

```bash
cd frontend
npm install
npm run dev
```

默认访问地址：

- `http://localhost:5173`

### 3. 后端启动

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

默认访问地址：

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

---

## 配置说明

### 前端环境变量

参考 `frontend/.env.example`：

```env
VITE_APP_TITLE=人事行政一体化HR系统
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_BRAND=YUHO HR
VITE_CLOUDBASE_ENV_ID=your-cloudbase-env-id
```

### 后端环境变量

参考 `backend/.env.example`：

```env
APP_NAME=人事行政一体化HR系统
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
CORS_ORIGINS=http://localhost:5173
DB_DRIVER=sqlite
SQLITE_PATH=./data/hr_system.db
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=hr_system
JWT_SECRET=replace-with-your-own-secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_API_KEY=replace-with-your-own-key
ARK_MODEL=your-model-id
```

---

## 数据存储方案

项目支持两类数据存储后端：

### SQLite

适用于：

- 本地开发
- 快速原型验证
- 单机演示环境

配置方式：

```env
DB_DRIVER=sqlite
SQLITE_PATH=./data/hr_system.db
```

### MongoDB

适用于：

- 服务化部署
- 多实例扩展场景
- 更高灵活性的数据持久化需求

配置方式：

```env
DB_DRIVER=mongodb
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=hr_system
```

---

## 典型业务链路

### 链路一：员工请假审批

1. 员工提交请假申请
2. 系统生成审批记录并进入审批链
3. 部门经理审核
4. 如规则要求，流转至 HR 审核
5. 审批结果回写业务数据

### 链路二：员工绩效提报与审核

1. 员工提交月度绩效
2. 部门经理评分并撰写评价
3. HR 复核与发布
4. 绩效结果可用于薪酬核算

### 链路三：薪酬核算

1. 汇总员工档案、考勤、请假、绩效数据
2. 计算绩效工资、加班工资、请假扣款、考勤扣款
3. 计算应发、个税、社保、公积金与实发工资
4. 生成 HR 汇总薪资表与员工工资条

### 链路四：行政资源申请

1. 员工发起办公用品、资产、公章、会议室、用车等申请
2. 系统统一纳入审批中心
3. 审批完成后同步业务状态
4. HR 端可从资产/行政模块查看结果

---

## 项目适用场景

- 企业内部人事行政一体化平台原型
- 多角色业务系统设计展示
- 企业流程审批与协同场景演示
- 前后端分离管理系统项目展示
- AI 与业务系统结合的应用型项目展示

---

## 后续扩展方向

- 用户体系与数据库用户表完全解耦并统一认证
- 更完整的组织架构树与权限模型
- 更精细的审批节点配置能力
- 更多 AI 驱动的管理分析能力
- 审计日志、操作留痕与消息通知能力
- 面向生产环境的部署与监控体系

---

## License

如需开源发布，可在此补充许可证信息。
