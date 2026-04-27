# Web前端启动指南

## 快速启动（3步走）

### 第1步：安装依赖
```bash
cd tianjin_bureau_system/municipal-system
npm install
```

### 第2步：启动API服务
```bash
# 在另一个终端窗口中
cd tianjin_bureau_system
python api_start.py
```

### 第3步：启动Web前端
```bash
npm run dev
```

或双击运行：
```
start_web.bat
```

---

## 详细启动步骤

### 1. 环境准备

#### 1.1 Node.js版本要求
- Node.js 16.0 或更高版本
- npm 8.0 或更高版本

#### 1.2 检查Node.js版本
```bash
node --version
```

#### 1.3 检查npm版本
```bash
npm --version
```

如果Node.js未安装，请访问：https://nodejs.org/

### 2. 安装依赖

#### 2.1 进入前端项目目录
```bash
cd tianjin_bureau_system/municipal-system
```

#### 2.2 安装项目依赖
```bash
npm install
```

首次安装可能需要5-10分钟，请耐心等待。

### 3. 启动API服务

Web前端需要API服务支持，请确保API服务已启动。

#### 3.1 启动API服务
```bash
# 在新终端窗口中
cd tianjin_bureau_system
python api_start.py
```

或使用：
```bash
start_api.bat
```

#### 3.2 验证API服务
```bash
curl http://localhost:8000/health
```

预期响应：
```json
{"status":"healthy"}
```

### 4. 启动Web前端

#### 方式1：使用启动脚本（推荐）
```bash
cd tianjin_bureau_system/municipal-system
start_web.bat
```

#### 方式2：使用npm命令
```bash
cd tianjin_bureau_system/municipal-system
npm run dev
```

#### 方式3：使用yarn（如果使用yarn）
```bash
yarn dev
```

---

## 访问Web应用

### 访问地址

**开发服务器：**
```
http://localhost:5173
```

**API服务：**
```
http://localhost:8000
```

**API文档：**
```
http://localhost:8000/docs
```

### 验证启动成功

当你在浏览器中访问 http://localhost:5173 并看到页面加载时，说明Web前端启动成功！

---

## 项目结构

```
municipal-system/
├── src/                    # 源代码
│   ├── components/          # 组件
│   ├── pages/               # 页面
│   ├── utils/               # 工具函数
│   ├── App.jsx              # 主应用组件
│   ├── index.css            # 全局样式
│   └── main.jsx             # 应用入口
├── index.html              # HTML模板
├── package.json            # 项目配置
├── vite.config.js         # Vite配置
├── tailwind.config.js     # TailwindCSS配置
└── start_web.bat          # 启动脚本
```

---

## 可用的npm脚本

| 命令 | 说明 |
|------|------|
| `npm run dev` | 启动开发服务器 |
| `npm run build` | 构建生产版本 |
| `npm run preview` | 预览构建后的应用 |
| `npm run lint` | 代码检查 |
| `npm run lint:fix` | 修复代码问题 |

---

## 技术栈

### 核心框架
- **React** 19.2.0 - UI框架
- **Vite** 5.1.4 - 构建工具
- **React Router** 7.9.6 - 路由管理

### 样式方案
- **TailwindCSS** 3.4.1 - CSS框架
- **PostCSS** 8.4.35 - CSS处理
- **Autoprefixer** 10.4.17 - CSS兼容性

### UI组件
- **Lucide React** 0.555.0 - 图标库
- **Framer Motion** 12.23.24 - 动画库
- **CLSX** 2.1.0 - 类名工具

### 数据可视化（可选）
- **ECharts** 5.5.0 - 图表库
- **Recharts** 2.12.0 - React图表库

### 工具库
- **GSAP** 3.12.5 - 动画工具
- **Lottie Web** 5.12.2 - Lottie动画

---

## 开发模式特性

### 热模块替换（HMR）
- 代码修改后自动刷新
- 保持应用状态
- 快速开发迭代

### 快速重载
- 组件修改即时生效
- 无需手动刷新

### 开发工具
- React DevTools
- Vite DevTools
- ESLint代码检查

---

## 生产构建

### 1. 构建生产版本
```bash
npm run build
```

构建产物会生成在 `dist/` 目录中。

### 2. 预览构建结果
```bash
npm run preview
```

### 3. 部署到服务器

将 `dist/` 目录的内容部署到Web服务器。

---

## 常见问题处理

### 问题1：Node.js版本过低

**错误信息：**
```
Error: The engine "node" is incompatible with this module
```

**解决方案：**
- 升级Node.js到16.0+版本
- 下载地址：https://nodejs.org/

### 问题2：端口被占用

**错误信息：**
```
Error: Port 5173 is already in use
```

**解决方案：**
```bash
# 查找占用5173端口的进程
netstat -ano | findstr :5173

# 结束进程
taskkill /PID <进程ID> /F

# 或修改Vite配置使用其他端口
```

### 问题3：依赖安装失败

**错误信息：**
```
npm ERR! code ERESOLVE
```

**解决方案：**
```bash
# 清理缓存
npm cache clean --force

# 删除node_modules
rmdir /s /q node_modules

# 重新安装
npm install
```

### 问题4：API连接失败

**错误信息：**
```
Network Error / Failed to fetch
```

**解决方案：**
1. 确保API服务已启动
2. 检查API服务地址是否为 http://localhost:8000
3. 检查浏览器控制台的网络请求

### 问题5：CORS错误

**错误信息：**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**解决方案：**
已在API服务中配置了CORS，如果仍有问题，检查API配置。

---

## 开发建议

### 1. 使用ESLint
```bash
npm run lint
```

### 2. 修复代码问题
```bash
npm run lint:fix
```

### 3. 使用React DevTools
- 安装浏览器扩展
- 检查组件状态
- 性能分析

### 4. 调试技巧
- 使用console.log调试
- 使用React DevTools
- 使用浏览器断点

---

## 性能优化

### 1. 减少构建体积
- 按需导入组件
- 使用Tree Shaking
- 压缩资源

### 2. 优化加载速度
- 代码分割
- 懒加载
- 图片优化

### 3. 提升用户体验
- 骨架屏
- 加载动画
- 错误边界

---

## 总结

### 快速启动命令
```bash
# 1. 安装依赖
cd tianjin_bureau_system/municipal-system
npm install

# 2. 启动API服务（新终端）
cd tianjin_bureau_system
python api_start.py

# 3. 启动Web前端
cd tianjin_bureau_system/municipal-system
npm run dev
```

### 访问地址
- **Web前端：** http://localhost:5173
- **API服务：** http://localhost:8000
- **API文档：** http://localhost:8000/docs

### 一键启动
```bash
start_web.bat
```

---

按照以上步骤，你就可以成功启动Web前端了！