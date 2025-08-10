# Windows 环境运行指南

## 概述

这个基金监控系统使用 **SQLite 数据库**，只需要一个数据库文件，无需安装 MySQL 或其他数据库服务器。现在提供了多个 Windows 兼容的运行脚本，让你可以在 Windows 环境下轻松运行项目。

## 数据库说明

- **数据库类型**: SQLite（Python 内置支持）
- **数据库文件**: `fundweb.db`（自动创建在项目根目录）
- **优势**: 无需安装数据库服务器，文件型数据库，便于备份和迁移

## 问题解决

如果你遇到依赖安装问题（如 MarkupSafe 版本冲突），请使用以下解决方案：

### 方案一：使用 SQLite 专用启动脚本（推荐）
```cmd
# 一键安装依赖并启动（SQLite版本）
run_sqlite.bat
```

### 方案二：使用依赖修复脚本
```cmd
# 运行依赖修复脚本
python install_deps.py

# 然后运行应用
python run.py
```

### 方案三：使用简化启动脚本
```cmd
# 一键安装依赖并启动
run_simple.bat
```

## 运行脚本说明

### 1. `init_and_run.bat` - 一键初始化并启动（最推荐）
首次运行的最佳选择，自动初始化数据库并启动应用。

**使用方法：**
```cmd
init_and_run.bat
```

**特点：**
- 自动初始化数据库
- 自动启动应用
- 显示访问地址
- 错误处理和状态反馈
- 适合首次运行

### 2. `run_sqlite.bat` - SQLite专用启动脚本
专门为 SQLite 数据库优化的启动脚本，自动处理依赖安装和数据库初始化。

**使用方法：**
```cmd
run_sqlite.bat
```

**特点：**
- 自动修复依赖问题
- 自动初始化 SQLite 数据库
- 兼容 Python 3.12
- 一键启动
- 数据库文件自动创建

### 2. `install_deps.py` - 依赖修复脚本
专门解决依赖安装问题的 Python 脚本。

**使用方法：**
```cmd
python install_deps.py
```

**特点：**
- 升级 pip
- 安装兼容版本的依赖
- 验证关键依赖
- 无需 MySQL 相关依赖

### 3. `run_simple.bat` - 简化启动脚本
自动安装依赖并启动应用。

**使用方法：**
```cmd
run_simple.bat
```

### 4. `run.bat` - 基础批处理脚本
最简单的 Windows 批处理文件版本。

**使用方法：**
```cmd
run.bat
```

### 5. `run_advanced.bat` - 高级批处理脚本
更完善的版本，包含错误检查和详细的状态反馈。

**使用方法：**
```cmd
run_advanced.bat
```

### 6. `run.ps1` - PowerShell 脚本
功能最强大的版本，使用 PowerShell 提供最佳的用户体验。

**使用方法：**
```powershell
# 基本运行
.\run.ps1

# 跳过依赖安装
.\run.ps1 -SkipDeps

# 跳过数据库迁移
.\run.ps1 -SkipMigrations
```

## 环境要求

### 必需软件
1. **Python 3.7+**（推荐 3.8-3.11，3.12 可能需要使用修复脚本）
   - 下载地址：https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **pip**（通常随 Python 一起安装）

### 可选软件
1. **PowerShell 5.0+**（Windows 10 默认包含）
2. **Git Bash**（如果需要使用原始的 `run.sh`）

## 安装步骤

### 1. 克隆项目
```cmd
git clone <项目地址>
cd fundweb
```

### 2. 选择运行方式

#### 方式一：使用 SQLite 专用脚本（推荐）
```cmd
run_sqlite.bat
```

#### 方式二：手动修复依赖
```cmd
# 先修复依赖
python install_deps.py

# 再运行应用
python run.py
```

#### 方式三：使用简化脚本
```cmd
run_simple.bat
```

#### 方式四：使用 PowerShell
```powershell
# 首次运行（会安装依赖和迁移数据库）
.\run.ps1

# 后续运行（跳过依赖安装）
.\run.ps1 -SkipDeps
```

#### 方式五：使用 Docker（如果已安装 Docker Desktop）
```cmd
docker-compose up --build
```

### 3. 访问应用
启动成功后，在浏览器中访问：
- 主页：http://localhost:5000/
- 健康检查：http://localhost:5000/health
- API 文档：查看 `API_DOCUMENTATION.md`
- 手动获取数据：http://localhost:5000/api/funds/refresh

### 4. 数据库文件
- 数据库文件：`fundweb.db`（自动创建在项目根目录）
- 备份：直接复制 `fundweb.db` 文件即可备份

## 常见问题

### 1. MarkupSafe 版本冲突
**解决方案：** 使用 `install_deps.py` 脚本或 `run_sqlite.bat`

### 2. Flask-SQLAlchemy 未安装
**解决方案：** 运行 `python install_deps.py`

### 3. 数据库连接错误
**解决方案：** 
- 确保 `fundweb.db` 文件存在
- 检查文件权限
- 重新运行 `run_sqlite.bat` 初始化数据库

### 4. PowerShell 执行策略错误
如果遇到执行策略错误，运行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 5. 端口被占用
如果 5000 端口被占用，可以修改 `run.py` 中的端口号：
```python
app.run(host="0.0.0.0", debug=True, use_reloader=False, port=5001)
```

### 6. Python 3.12 兼容性问题
如果使用 Python 3.12 遇到问题：
- 使用 `install_deps.py` 脚本
- 或降级到 Python 3.11

## 测试

运行测试脚本：
```cmd
# 运行所有测试
python run_tests.py

# 运行 API 测试
python test_api.py

# 运行单元测试
python -m unittest discover tests -v
```

## 开发建议

1. **使用虚拟环境**：
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   python install_deps.py
   ```

2. **使用 SQLite 专用脚本**：`run_sqlite.bat` 是最稳定的启动方式

3. **定期备份数据库**：
   ```cmd
   copy fundweb.db fundweb_backup.db
   ```

4. **定期更新依赖**：
   ```cmd
   python install_deps.py
   ```

## 文件说明

- `init_and_run.bat` - 一键初始化并启动脚本（首次运行最推荐）
- `init_db.py` - 数据库初始化和管理脚本
- `run_sqlite.bat` - SQLite专用启动脚本
- `install_deps.py` - 依赖修复脚本
- `run_simple.bat` - 简化启动脚本
- `run.bat` - 基础 Windows 批处理脚本
- `run_advanced.bat` - 高级 Windows 批处理脚本
- `run.ps1` - PowerShell 脚本
- `run.sh` - 原始 Linux/Unix 脚本
- `run.py` - Python 启动文件
- `requirements.txt` - Python 依赖列表（已移除MySQL依赖）
- `fundweb.db` - SQLite 数据库文件（自动创建）
- `test_api.py` - API 测试脚本
- `API_DOCUMENTATION.md` - API 文档

## 快速开始

### 首次运行（推荐方式）
1. 确保安装了 Python 3.7+
2. 在项目根目录运行：`init_and_run.bat`
3. 等待数据库初始化和应用启动完成
4. 应用将在 http://localhost:5000 启动
5. 手动获取基金数据：访问 http://localhost:5000/api/funds/refresh
6. 查看基金数据：访问 http://localhost:5000/api/funds/today-changes

### 首次运行（手动方式）
1. 确保安装了 Python 3.7+
2. 初始化数据库：`python init_db.py init`
3. 在项目根目录运行：`run_sqlite.bat`
4. 等待依赖安装和数据库初始化完成
5. 应用将在 http://localhost:5000 启动
6. 手动获取基金数据：访问 http://localhost:5000/api/funds/refresh
7. 查看基金数据：访问 http://localhost:5000/api/funds/today-changes

### 后续运行
1. 直接运行：`run_sqlite.bat`
2. 应用将在 http://localhost:5000 启动

### 数据库管理
```cmd
# 检查数据库状态
python init_db.py check

# 重置数据库（会删除所有数据）
python init_db.py reset
```

选择最适合你的脚本运行项目！ 