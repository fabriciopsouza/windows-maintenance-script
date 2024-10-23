@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

:: Definir cores
set "verde=[32m"
set "vermelho=[31m"
set "amarelo=[33m"
set "reset=[0m"

:: Criar pasta de logs se não existir
if not exist "C:\Logs de Scripts" (
    mkdir "C:\Logs de Scripts" 2>nul
    if errorlevel 1 (
        echo %vermelho%Erro: Não foi possível criar a pasta de logs. Verifique as permissões.%reset%
        pause
        exit /b 1
    )
)

:: Definir nome do arquivo de log com timestamp
set "datetime=%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "datetime=%datetime: =0%"
set "logfile=C:\Logs de Scripts\system_check_%datetime%.log"

:: Iniciar log com encoding UTF-8
echo %verde%Iniciando verificação do sistema...%reset%
echo ====================================== > "%logfile%"
echo Verificação do Sistema - %date% %time% >> "%logfile%"
echo ====================================== >> "%logfile%"

:: Verificar privilégios de administrador
net session >nul 2>&1
if errorlevel 1 (
    echo %vermelho%ERRO: Este script requer privilégios de administrador.%reset%
    echo Por favor, execute como administrador.
    pause
    exit /b 1
)

:: Informações do sistema
echo.
echo %amarelo%Coletando informações do sistema...%reset%
echo. >> "%logfile%"
echo === Informações do Sistema === >> "%logfile%"
systeminfo | findstr /C:"OS" /C:"System Type" /C:"Total Physical Memory" >> "%logfile%"

:: Verificar status dos discos
echo %amarelo%Verificando status dos discos...%reset%
echo. >> "%logfile%"
echo === Status dos Discos === >> "%logfile%"
wmic diskdrive get caption,status,size >> "%logfile%" 2>&1

:: Verificar espaço em disco
echo %amarelo%Verificando espaço em disco...%reset%
echo. >> "%logfile%"
echo === Espaço em Disco === >> "%logfile%"
wmic logicaldisk get deviceid,freespace,size >> "%logfile%" 2>&1

:: Verificar arquivos de erro do Windows
echo %amarelo%Verificando arquivos de erro do Windows...%reset%
echo. >> "%logfile%"
echo === Arquivos de Erro do Windows === >> "%logfile%"
if exist C:\Windows\Memory.dmp (
    echo Memory.dmp encontrado: >> "%logfile%"
    dir "C:\Windows\Memory.dmp" >> "%logfile%" 2>&1
)
if exist C:\Windows\Minidump (
    echo Arquivos em Minidump: >> "%logfile%"
    dir "C:\Windows\Minidump" >> "%logfile%" 2>&1
)

:: Verificar arquivos temporários
echo %amarelo%Verificando arquivos temporários...%reset%
echo. >> "%logfile%"
echo === Arquivos Temporários === >> "%logfile%"
echo Pasta TEMP: >> "%logfile%"
dir /s "%TEMP%" | findstr "File(s)" >> "%logfile%" 2>&1
echo Pasta Windows\Temp: >> "%logfile%"
dir /s "C:\Windows\Temp" | findstr "File(s)" >> "%logfile%" 2>&1

:: Verificar programas instalados
echo %amarelo%Verificando programas instalados...%reset%
echo. >> "%logfile%"
echo === Programas Instalados === >> "%logfile%"
wmic product get name,version,installdate >> "%logfile%" 2>&1

:: Verificar serviços com erro
echo %amarelo%Verificando serviços com erro...%reset%
echo. >> "%logfile%"
echo === Serviços com Erro === >> "%logfile%"
sc query state= all | findstr "SERVICE_NAME STATE" | findstr /V "RUNNING" >> "%logfile%" 2>&1

:: Verificar logs de eventos do sistema
echo %amarelo%Verificando logs de eventos...%reset%
echo. >> "%logfile%"
echo === Logs de Eventos (Últimas 24 horas) === >> "%logfile%"
wevtutil qe System /c:30 /f:text /rd:true >> "%logfile%" 2>&1

:: Verificar integridade do sistema
echo %amarelo%Verificando integridade do sistema...%reset%
echo. >> "%logfile%"
echo === Verificação de Integridade do Sistema === >> "%logfile%"
sfc /verifyonly >> "%logfile%" 2>&1

:: Verificar problemas de disco
echo %amarelo%Verificando problemas no disco...%reset%
echo. >> "%logfile%"
echo === Verificação de Problemas no Disco === >> "%logfile%"
chkdsk C: /scan >> "%logfile%" 2>&1

:: Verificar atualizações pendentes
echo %amarelo%Verificando atualizações pendentes...%reset%
echo. >> "%logfile%"
echo === Atualizações Pendentes === >> "%logfile%"
wmic qfe list brief >> "%logfile%" 2>&1

:: Verificar drivers com problemas
echo %amarelo%Verificando drivers...%reset%
echo. >> "%logfile%"
echo === Drivers com Problemas === >> "%logfile%"
driverquery /FO list >> "%logfile%" 2>&1

:: Verificar registro do Windows
echo %amarelo%Verificando registro...%reset%
echo. >> "%logfile%"
echo === Verificando Registro === >> "%logfile%"
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" >> "%logfile%" 2>&1

:: Análise de Recomendações
echo %amarelo%Gerando recomendações...%reset%
echo. >> "%logfile%"
echo === Recomendações === >> "%logfile%"

:: Verificar espaço livre em C:
for /f "tokens=2 delims==" %%a in ('wmic logicaldisk where "DeviceID='C:'" get FreeSpace /value') do set "freespace=%%a"
set /a "freespace_gb=%freespace:~0,-1%/1024/1024/1024"
if %freespace_gb% LSS 50 (
    echo %vermelho%[ALERTA] Espaço livre no disco C: menor que 50GB%reset%
    echo [ALERTA] Espaço livre no disco C: menor que 50GB. Recomenda-se liberar espaço. >> "%logfile%"
)

:: Verificar arquivos temporários grandes
dir /s "%TEMP%\*.*" | findstr "bytes" > nul
if not errorlevel 1 (
    echo %amarelo%[RECOMENDAÇÃO] Há arquivos temporários que podem ser limpos%reset%
    echo [RECOMENDAÇÃO] Há arquivos temporários que podem ser limpos >> "%logfile%"
)

:: Conclusão
echo. >> "%logfile%"
echo === Verificação Concluída === >> "%logfile%"
echo Arquivo de log salvo em: %logfile% >> "%logfile%"

:: Mensagens finais
echo.
echo %verde%Verificação concluída com sucesso!%reset%
echo %amarelo%O relatório foi salvo em:%reset%
echo %logfile%
echo.
echo %verde%Pressione qualquer tecla para abrir o relatório e encerrar...%reset%
pause > nul

:: Abrir o relatório
start notepad "%logfile%"

endlocal
exit /b 0