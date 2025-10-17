@echo off
REM ǿ�� UTF-8 ��ʾ�������κ��������ǰ��
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

REM ========== ָ�����õ� Python��������ȷ�Ͽ��õ�·���� ==========
set "PYTHON_EXE=D:\python\python.exe"
if not exist "%PYTHON_EXE%" (
  echo [ERROR] δ�ҵ� Python��%PYTHON_EXE%
  echo Ո�_�Jԓ·�����ڣ���݋�� BAT �е� PYTHON_EXE �����_·����
  pause
  exit /b 1
)

REM ========== ·���O�ã���춱��n��λ�ã� ==========
set "HERE=%~dp0"
set "SCRIPT=%HERE%feed_your_snakes.py"
set "DATA=%HERE%data"
set "CSV=%DATA%\snake_feedings.csv"
set "CHARTS=%HERE%charts"
set "XLSX=%HERE%snake_feedings.xlsx"

if not exist "%SCRIPT%" (
  echo [ERROR] �Ҳ����_����%SCRIPT%
  echo Ո�����ļ����� feed_your_snakes.py ͬһĿ��¡�
  pause
  exit /b 1
)

:MENU
cls
echo =========================================================
echo          ?? ���ιʳӛ�ϵ�y��CSV + CLI + �D��
echo =========================================================
echo  Python : %PYTHON_EXE%
echo  Script : %SCRIPT%
echo  Data   : %CSV%
echo ---------------------------------------------------------
echo  1) ���ιʳӛ�
echo  2) �鿴ӛ䛣���� 20 �l��
echo  3) ���ɈD��ݔ���� charts��
echo  4) ���� Excel��snake_feedings.xlsx��
echo  5) ��Ք�������� CSV��
echo  6) ���_�����ļ��A
echo  7) �˳�
echo ---------------------------------------------------------
set /p CHO=Ոݔ���x� (1-7)�� 

if "%CHO%"=="1" goto ADD
if "%CHO%"=="2" goto LIST
if "%CHO%"=="3" goto CHARTS
if "%CHO%"=="4" goto EXPORT
if "%CHO%"=="5" goto CLEAR
if "%CHO%"=="6" goto OPEN_DIR
if "%CHO%"=="7" goto END
echo �oЧ�x헣�Ո��ԇ��
timeout /t 1 >nul
goto MENU

:ADD
cls
echo === ���ιʳӛ� ===
set /p NAME=�ߵ����֣����: 
if "%NAME%"=="" echo ���ֲ��ܞ�ա�&pause&goto MENU
set /p SPECIES=�ߵ�Ʒ�N�����x��: 
set /p FOOD=ʳ����: 
if "%FOOD%"=="" echo ʳ�ﲻ�ܞ�ա�&pause&goto MENU

:WEIGHT
set /p WEIGHT=ʳ��������g��: 
set "TMP=%WEIGHT:.=%"
for /f "delims=0123456789" %%A in ("%TMP%") do set NON=%%A
if defined NON (
  set "NON="
  echo Ոݔ�딵�֣����� 8 �� 12.5����
  goto WEIGHT
)

echo �x���Mʳ���
echo   1) ��   2) ����   3) ƫ��   4) ��ʳ
set /p APPSEL=ݔ�� 1-4�� 
if "%APPSEL%"=="1" set "APP=ǿ"
if "%APPSEL%"=="2" set "APP=����"
if "%APPSEL%"=="3" set "APP=ƫ��"
if "%APPSEL%"=="4" set "APP=��ʳ"
if not defined APP (
  echo �oЧ�x��
  pause
  goto MENU
)

set /p NOTES=���]�����x��: 

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
  echo δ�ҵ������ļ���%CSV%
  pause & goto MENU
)
for /f "usebackq delims=" %%T in (`powershell -NoProfile -Command "(Get-Date).ToString('yyyyMMdd_HHmmss')"`) do set TS=%%T
set "BACKUP=%HERE%snake_feedings_backup_%TS%.csv"
echo ���·����%BACKUP%
set /p OK=�_��Ҫ��Ն᣿(Y/N)�� 
if /I not "%OK%"=="Y" goto MENU

copy /y "%CSV%" "%BACKUP%" >nul
> "%CSV%" echo timestamp,snake_name,snake_species,food_species,food_weight_g,appetite,notes
echo ����ՁK��ݡ�
echo.
pause
goto MENU

:OPEN_DIR
start "" "%HERE%"
goto MENU

:END
echo ��Ҋ��
timeout /t 1 >nul
exit /b 0
