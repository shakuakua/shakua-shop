#!/bin/bash
# ==========================================
# 电商平台 — 一键部署脚本
# 在腾讯云服务器上运行此脚本
# ==========================================

set -e

PROJECT_DIR="/home/ubuntu/shop"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_DIR="$PROJECT_DIR/backend"

echo "=== 1. 安装系统依赖 ==="
sudo apt update -y
sudo apt install -y python3 python3-venv python3-pip nginx

# 安装 Node.js 20.x（用于前端构建）
if ! command -v node &> /dev/null; then
    echo "安装 Node.js 20.x..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt install -y nodejs
fi

echo "=== 2. 创建项目目录 ==="
mkdir -p "$PROJECT_DIR"

echo "=== 3. 配置 Python 虚拟环境 ==="
cd "$BACKEND_DIR"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "=== 4. 初始化数据库 ==="
python seed_data.py

echo "=== 5. 构建前端 ==="
cd "$FRONTEND_DIR"
npm install
npm run build

echo "=== 6. 创建日志目录 ==="
sudo mkdir -p /var/log/shop
sudo chown -R ubuntu:ubuntu /var/log/shop

echo "=== 7. 配置 Nginx ==="
sudo cp "$PROJECT_DIR/deploy/nginx.conf" /etc/nginx/sites-available/shop
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/shop /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

echo "=== 8. 配置 Systemd 服务 ==="
sudo cp "$PROJECT_DIR/deploy/shop.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable shop
sudo systemctl restart shop

echo ""
echo "=== 部署完成 ==="
echo "访问 http://<服务器IP> 即可打开网站"
echo ""
echo "常用命令："
echo "  systemctl status shop   # 查看服务状态"
echo "  journalctl -u shop -f   # 查看实时日志"
echo "  systemctl restart shop  # 重启服务"
echo "  tail -f /var/log/shop/error.log  # 查看错误日志"
