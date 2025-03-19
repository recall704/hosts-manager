# Linux Hosts 管理器

一个定期从自定义 hosts 文件读取并更新系统 `/etc/hosts` 文件的工具。可以直接运行或使用 Docker。

## 功能特点

- 自动使用自定义 hosts 文件中的条目更新 `/etc/hosts`
- 保留系统 hosts 文件中的现有内容
- 在进行更改前创建备份
- 实时监控变更并更新
- 可配置的更新间隔
- 全面的日志记录

## 系统要求

### 直接运行
- Python 3.6+
- 具有 sudo 权限的 Linux 系统

### 使用 Docker 运行
- Docker
- Docker Compose（可选）

## 使用方法

### 基本用法

```bash
# 以守护进程模式运行（默认设置）
python main.py

# 更新一次后退出
python main.py --update-once

# 指定自定义 hosts 文件
python main.py --hosts-file /path/to/your/hosts  # 默认为 /data2/code/hosts-manager/hosts

# 更改更新间隔（以秒为单位）
python main.py --interval 300  # 每5分钟检查一次（默认为60秒）
```

### 自定义 Hosts 文件格式

您的自定义 hosts 文件应在标记行之间包含条目：

```
# ================ hosts manager start ================
192.168.1.100  myserver.local
192.168.1.101  database.local
# ================ hosts manager end ================
```

只有这些标记之间的内容会被工具管理。

## 作为服务运行

要将 hosts 管理器作为 systemd 服务运行：

1. 创建 systemd 服务文件：

```bash
sudo nano /etc/systemd/system/hosts-manager.service
```

2. 添加以下内容（根据需要调整路径）：

```
[Unit]
Description=Hosts Manager Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /data2/code/hosts-manager/main.py
Restart=on-failure
User=root
Group=root

[Install]
WantedBy=multi-user.target
```

3. 启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable hosts-manager
sudo systemctl start hosts-manager
```

4. 检查状态：

```bash
sudo systemctl status hosts-manager
```

## 日志

日志仅输出到 stdout（标准输出）。使用 Docker 时，可以通过 Docker 日志系统查看日志。

## Docker 使用方法

hosts 管理器可以使用提供的 Dockerfile 和 docker-compose.yml 作为 Docker 容器运行。

### 使用 Docker Compose 构建和运行

```bash
# 创建日志目录
mkdir -p logs

# 构建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down
```

### 使用 Docker 构建和运行

```bash
# 构建 Docker 镜像
docker build -t hosts-manager .

# 运行容器
docker run -d \
  --name hosts-manager \
  --restart unless-stopped \
  --privileged \
  -v $(pwd)/hosts:/app/hosts \
  -v /etc/hosts:/etc/hosts \
  -v $(pwd)/logs:/logs \
  -e LOG_PATH=/logs/hosts-manager.log \
  hosts-manager

# 查看日志
docker logs -f hosts-manager

# 停止并删除容器
docker stop hosts-manager
docker rm hosts-manager
```

### Docker 注意事项

- 容器需要特权模式才能修改主机的 `/etc/hosts` 文件
- hosts 文件从主机系统挂载，因此对其所做的任何更改都将被容器检测到
- 日志存储在主机系统的 `./logs` 目录中
