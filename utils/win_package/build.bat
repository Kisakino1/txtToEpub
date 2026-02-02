@echo off
chcp 65001 >nul
echo 正在安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 请先安装 Python 并确保 pip 可用。
    pause
    exit /b 1
)

cd /d "%~dp0"
set ROOT=%~dp0
set DIST=%ROOT%dist
if not exist "%DIST%" mkdir "%DIST%"

echo.
echo 正在打包「书工具」GUI（一个窗口三个标签页）...
pyinstaller --onefile --windowed --distpath "%DIST%" --workpath "%ROOT%build" --specpath "%ROOT%" --name "书工具" "%ROOT%win_gui.py" --hidden-import "检查文件编码_win" --hidden-import "转换文件编码_win" --hidden-import "txtToEpub_win"

copy /y "%ROOT%打包说明.txt" "%DIST%\" >nul

echo.
echo 完成。可执行文件在: %DIST%
echo 双击「书工具.exe」打开界面，在三个标签页里选文件、填参数后点运行即可。
dir /b "%DIST%"
pause
