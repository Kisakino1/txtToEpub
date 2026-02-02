#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
ROOT="$(pwd)"
DIST="$ROOT/dist"
VENV="$ROOT/.venv"

# Homebrew 的 Python 默认不带 tkinter，需先安装
if ! python3 -c "import tkinter" 2>/dev/null; then
  VER=$(python3 -c "import sys; print(sys.version_info.minor)" 2>/dev/null || echo "13")
  echo "当前 Python 没有 tkinter，需要先安装。请执行："
  echo "  brew install python-tk@3.$VER"
  echo "安装完成后重新运行本脚本。"
  exit 1
fi

if [ ! -d "$VENV" ]; then
  echo "创建虚拟环境..."
  python3 -m venv "$VENV"
fi
echo "激活虚拟环境并安装依赖..."
source "$VENV/bin/activate"
# Mac 上 Python 若未配置 SSL 证书会报 CERTIFICATE_VERIFY_FAILED，用 --trusted-host 可绕过
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

echo ""
echo "正在打包「书工具」Mac 版（.app）..."
pyinstaller --windowed --name "书工具" \
  --distpath "$DIST" --workpath "$ROOT/build" --specpath "$ROOT" \
  "$ROOT/win_gui.py" \
  --hidden-import "检查文件编码_gui" \
  --hidden-import "转换文件编码_gui" \
  --hidden-import "txtToEpub_gui"

cp "$ROOT/打包说明.txt" "$DIST/" 2>/dev/null || true

echo ""
echo "完成。应用在: $DIST/书工具.app"
echo "双击「书工具.app」即可打开界面。"
