# Traffic Simulation Tool

Traffic Simulation Tool 是一个用于捕获、重放网络流量，以及模拟真实流量的项目。该项目包含前后端两个模块：
- **前端**：基于 Django 实现的简单的交互界面，用于执行流量生成任务、监控任务的运行过程以及管理任务配置文件。
- **后端**：基于 Scapy 实现流量捕获与重放，并可通过预构建的 Docker 容器模拟真实流量（如 Web 流量）。 

前后端通过数据库进行交互。前端将用户的任务请求保存到数据库中，后端从数据库读取请求并执行相应的任务。

## 功能特点

### 前端
- 提供用户友好的界面，便于配置和管理流量生成任务。
- 支持任务状态的监控和日志查看。
- 提供任务配置文件的导入与导出功能。

### 后端
- **流量捕获与重放**：使用 Scapy 捕获指定的网络流量，并可对流量进行精准重放。
- **模拟真实流量**：支持通过 Docker 容器运行不同应用服务（如 Web 服务），以模拟真实网络流量。
- **任务自动执行**：基于任务配置文件自动按要求运行任务，可指定任务启动日期时间。

## 安装与运行

### 前置要求

- **系统要求**：Linux（需支持 Docker）
- **环境依赖**：
  - Python 3.8+
  - Docker
  - Django
  - Scapy

### 安装步骤

1. 克隆项目代码：
   ```bash
   git clone https://github.com/your-repo/traffic-simulation-tool.git
   cd traffic-simulation-tool
   ```

2. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 修改代码中必要信息，补全样式文件。对于django部分，要在`models.py`中修改配置文件目录。对于后端部分，则要修改`main.py`中数据库文件的路径和配置文件目录。此外，django模板文件中使用的样式文件需要补全。

4. 迁移数据库：
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. 启动后端服务：
   ```bash
   python backend/src/main.py
   ```

6. 启动前端服务：
   ```bash
   python django/manage.py runserver
   ```

## 使用说明

1. 访问前端管理界面：
   打开浏览器访问 `http://127.0.0.1:8000`。

2. 配置任务并执行：
   - 在前端界面中，管理任务文件，上传或者删除。提交任务配置文件后，文件会保存在本地。
   - 选择任务文件，执行。

3. 执行任务：
   - 后端服务会自动从数据库中读取请求，并执行流量捕获、重放或容器模拟。

4. 查看任务结果：
   - 前端支持查看任务执行的状态和流量捕获结果。

更多信息参考[项目概要](docs/overview.md)和[接口说明](docs/interfaces.md)。

## 项目结构

```
traffic-simulation-tool/
├── backend/                 # 后端部分
│   ├── config-examples/     # 任务配置文件的案例和需要构建的容器的案例
│   ├── src                  # 后端代码
├── django/                  # 前端代码示例
├── docs/                    # 项目文档
├── requirements.txt         # Python 依赖列表
└── README.md                # 项目说明文件
```

## 贡献

欢迎贡献代码！如果您对该项目有任何建议或改进，请提交 issue 或发起 pull request。

## 许可证

本项目基于 MIT License 发布，详情请参阅 [LICENSE](LICENSE) 文件。

---

希望您喜欢这个项目并从中受益!
