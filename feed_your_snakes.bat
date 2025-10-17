@echo off
REM 强制 UTF-8 显示（放在任何中文输出前）
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

REM ========== 指定可用的 Python（已用你确认可用的路径） ==========
set "PYTHON_EXE=D:\python\python.exe"
if not exist "%PYTHON_EXE%" (
  echo [ERROR] 未找到 Python：%PYTHON_EXE%
  echo 請確認該路徑存在，或編輯此 BAT 中的 PYTHON_EXE 為正確路徑。
  pause
  exit /b 1
)

REM ========== 路徑設置（基於本檔案位置） ==========
set "HERE=%~dp0"
set "SCRIPT=%HERE%feed_your_snakes.py"
set "DATA=%HERE%data"
set "CSV=%DATA%\snake_feedings.csv"
set "CHARTS=%HERE%charts"
set "XLSX=%HERE%snake_feedings.xlsx"

if not exist "%SCRIPT%" (
  echo [ERROR] 找不到腳本：%SCRIPT%
  echo 請將本文件放在 feed_your_snakes.py 同一目錄下。
  pause
  exit /b 1
)

:MENU
cls
echo =========================================================
echo          ?? 蛇類喂食記錄系統（CSV + CLI + 圖表）
echo =========================================================
echo  Python : %PYTHON_EXE%
echo  Script : %SCRIPT%
echo  Data   : %CSV%
echo ---------------------------------------------------------
echo  1) 添加喂食記錄
echo  2) 查看記錄（最近 20 條）
echo  3) 生成圖表（輸出到 charts）
echo  4) 導出 Excel（snake_feedings.xlsx）
echo  5) 清空數據（備份 CSV）
echo  6) 打開數據文件夾
echo  7) 退出
echo ---------------------------------------------------------
set /p CHO=請輸入選項 (1-7)： 

if "%CHO%"=="1" goto ADD
if "%CHO%"=="2" goto LIST
if "%CHO%"=="3" goto CHARTS
if "%CHO%"=="4" goto EXPORT
if "%CHO%"=="5" goto CLEAR
if "%CHO%"=="6" goto OPEN_DIR
if "%CHO%"=="7" goto END
echo 無效選項，請重試。
timeout /t 1 >nul
goto MENU

:ADD
cls
echo === 添加喂食記錄 ===
set /p NAME=蛇的名字（必填）: 
if "%NAME%"=="" echo 名字不能為空。&pause&goto MENU
set /p SPECIES=蛇的品種（可選）: 
set /p FOOD=食物（必填）: 
if "%FOOD%"=="" echo 食物不能為空。&pause&goto MENU

:WEIGHT
set /p WEIGHT=食物重量（g）: 
set "TMP=%WEIGHT:.=%"
for /f "delims=0123456789" %%A in ("%TMP%") do set NON=%%A
if defined NON (
  set "NON="
  echo 請輸入數字（例如 8 或 12.5）。
  goto WEIGHT
)

echo 選擇進食意願：
echo   1) 強   2) 正常   3) 偏弱   4) 拒食
set /p APPSEL=輸入 1-4： 
if "%APPSEL%"=="1" set "APP=强"
if "%APPSEL%"=="2" set "APP=正常"
if "%APPSEL%"=="3" set "APP=偏弱"
if "%APPSEL%"=="4" set "APP=拒食"
if not defined APP (
  echo 無效選擇。
  pause
  goto MENU
)

set /p NOTES=備註（可選）: 

pushd "%HERE%"
"%PYTHON_EXE%" "%SCRIPT%" add --name "%NAME%" --species "%SPECIES%" --food "%FOOD%" --weight %WEIGHT% --appetite "%APP%" --notes "%NOTES%"
echo.
pause
popd
goto MENU

:LIST
cls
pushd "%HERE%"
"%PYTHON_EXE%" "%SCRIPT%" list --limit 20
echo.
pause
popd
goto MENU

:CHARTS
cls
pushd "%HERE%"
"%PYTHON_EXE%" "%SCRIPT%" charts
if exist "%CHARTS%" start "" "%CHARTS%"
echo.
pause
popd
goto MENU

:EXPORT
cls
pushd "%HERE%"
"%PYTHON_EXE%" "%SCRIPT%" export-xlsx
if exist "%XLSX%" start "" "%XLSX%"
echo.
pause
popd
goto MENU

:CLEAR
cls
if not exist "%CSV%" (
  echo 未找到數據文件：%CSV%
  pause & goto MENU
)
for /f "usebackq delims=" %%T in (`powershell -NoProfile -Command "(Get-Date).ToString('yyyyMMdd_HHmmss')"`) do set TS=%%T
set "BACKUP=%HERE%snake_feedings_backup_%TS%.csv"
echo 備份路徑：%BACKUP%
set /p OK=確定要清空嗎？(Y/N)： 
if /I not "%OK%"=="Y" goto MENU

copy /y "%CSV%" "%BACKUP%" >nul
> "%CSV%" echo timestamp,snake_name,snake_species,food_species,food_weight_g,appetite,notes
echo 已清空並備份。
echo.
pause
goto MENU

:OPEN_DIR
start "" "%HERE%"
goto MENU

:END
echo 再見！
timeout /t 1 >nul
exit /b 0
