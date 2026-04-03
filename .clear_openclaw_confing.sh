#!/bin/zsh

echo "=============================== ==========="
echo "OpenClaw 敏感数据清理脚本,请先提前关闭 Openclaw 服务"
echo "=============================== ==========="
echo ""
echo "将删除以下内容："
echo "   - openclaw.json (含 API key)"
echo "   - agents/main/agent/auth-profiles.json"
echo "   - agents/main/agent/models.json"
echo "   - logs/、memory/、completions/"
echo "   - workspace/memory/、workspace/ros2_images/"
echo ""
echo "保留的内容："
echo "   - skills/、workspace/、identity/"
echo "   - devices/、canvas/、cron/"
echo ""
echo "=============================== ==========="
echo ""

read "confirm?确认删除？请输入 'yes' 并按回车继续： "

if [[ "$confirm" != "yes" ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "删除敏感配置文件..."
rm -f ~/.openclaw/openclaw.json
rm -f ~/.openclaw/openclaw.json.bak
rm -f ~/.openclaw/openclaw.json.bak.1
rm -f ~/.openclaw/update-check.json

echo "删除 agent 配置文件(含 API key)..."
rm -rf ~/.openclaw/agents/*

echo "删除日志和缓存..."
rm -rf ~/.openclaw/logs/
rm -rf ~/.openclaw/memory/
rm -rf ~/.openclaw/completions/

echo "删除 workspace 中的缓存和测试数据..."
rm -rf ~/.openclaw/workspace/memory/
rm -rf ~/.openclaw/workspace/ros2_images/

echo ""
echo "清理完成!如果需要Openclaw服务,请重新启动Openclaw,并重新进行配置"
