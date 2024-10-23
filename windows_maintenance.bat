@echo off
title Manutencao Completa do Windows
setlocal EnableDelayedExpansion

:: Verificar privilégios de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Este script precisa ser executado como Administrador.
    echo Por favor, execute novamente com privilegios de administrador.
    pause
    exit /b 1
)

:: Criar pasta para logs
if not exist "C:\WindowsMaintenanceLogs" mkdir "C:\WindowsMaintenanceLogs"
set logfile="C:\WindowsMaintenanceLogs\manutencao_%date:~0,2%-%date:~3,2%-%date:~6,4%.txt"

echo ================================================
echo   Script de Manutencao Completa do Windows
echo   Data de execucao: %date% - %time%
echo ================================================
echo.

:: Iniciar log
echo Inicio da Manutencao - %date% %time% > %logfile%

:: 1. Verificação do Sistema (SFC)
echo 1. Executando verificacao do sistema (SFC)...
echo ================================================ >> %logfile%
echo Verificacao SFC iniciada em: %time% >> %logfile%
sfc /scannow >> %logfile%

:: 2. DISM
echo 2. Executando DISM...
echo ================================================ >> %logfile%
echo DISM Check Health iniciado em: %time% >> %logfile%
DISM /Online /Cleanup-Image /CheckHealth >> %logfile%
echo DISM Scan Health iniciado em: %time% >> %logfile%
DISM /Online /Cleanup-Image /ScanHealth >> %logfile%
echo DISM Restore Health iniciado em: %time% >> %logfile%
DISM /Online /Cleanup-Image /RestoreHealth >> %logfile%

:: 3. Verificação do Disco
echo 3. Agendando verificacao do disco...
echo ================================================ >> %logfile%
echo Verificacao de Disco agendada em: %time% >> %logfile%
chkdsk C: /f /r >> %logfile%

:: 4. Limpeza de Arquivos Temporários
echo 4. Limpando arquivos temporarios...
echo ================================================ >> %logfile%
echo Limpeza de temporarios iniciada em: %time% >> %logfile%
del /s /f /q %WinDir%\Temp\*.* >> %logfile% 2>&1
del /s /f /q %Temp%\*.* >> %logfile% 2>&1
del /s /f /q %AppData%\Temp\*.* >> %logfile% 2>&1

:: 5. Verificar e Iniciar Serviços do Windows Update
echo 5. Verificando servicos do Windows Update...
echo ================================================ >> %logfile%
echo Verificacao de servicos iniciada em: %time% >> %logfile%
net start "Windows Update" >> %logfile% 2>&1
net start wuauserv >> %logfile% 2>&1
net start bits >> %logfile% 2>&1
net start cryptsvc >> %logfile% 2>&1

:: 6. Limpeza de Registro
echo 6. Limpando registros pendentes...
echo ================================================ >> %logfile%
echo Limpeza de registro iniciada em: %time% >> %logfile%
Reg.exe delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending" /f >> %logfile% 2>&1
Reg.exe delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired" /f >> %logfile% 2>&1

:: 7. Reset de Componentes de Rede
echo 7. Resetando componentes de rede...
echo ================================================ >> %logfile%
echo Reset de rede iniciado em: %time% >> %logfile%
netsh winsock reset >> %logfile%
netsh int ip reset >> %logfile%
ipconfig /flushdns >> %logfile%

:: 8. Desfragmentação (apenas para HDDs)
echo 8. Analisando necessidade de desfragmentacao...
echo ================================================ >> %logfile%
echo Analise de desfragmentacao iniciada em: %time% >> %logfile%
defrag C: /A >> %logfile%

echo.
echo ================================================
echo Manutencao concluida!
echo Verifique o log em: %logfile%
echo IMPORTANTE: O computador precisa ser reiniciado
echo para completar algumas alteracoes.
echo ================================================

:: Perguntar se deseja reiniciar
choice /C SN /M "Deseja reiniciar o computador agora? (S/N)"
if errorlevel 2 goto end
if errorlevel 1 shutdown /r /t 60 /c "O computador sera reiniciado em 60 segundos para concluir a manutencao."

:end
echo.
echo Se escolheu nao reiniciar, lembre-se de fazer isso manualmente depois.
pause