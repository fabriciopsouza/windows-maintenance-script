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

:: Função para mostrar progresso
:ShowProgress
echo %~1
echo %~1 >> "%logfile%"
timeout /t 1 /nobreak > nul
goto :eof

:: Verificar privilégios de administrador
net session >nul 2>&1
if errorlevel 1 (
    echo %vermelho%ERRO: Este script requer privilégios de administrador.%reset%
    echo Por favor, execute como administrador.
    pause
    exit /b 1
)

:: Iniciar verificações
call :ShowProgress "%verde%Iniciando verificação do sistema...%reset%"
echo ====================================== > "%logfile%"
echo Verificação do Sistema - %date% %time% >> "%logfile%"
echo ====================================== >> "%logfile%"

:: Informações do sistema
call :ShowProgress "%amarelo%[1/10] Coletando informações do sistema...%reset%"
systeminfo | findstr /C:"OS" /C:"System Type" /C:"Total Physical Memory" >> "%logfile%" 2>&1

:: Verificar status dos discos
call :ShowProgress "%amarelo%[2/10] Verificando status dos discos...%reset%"
wmic diskdrive get caption,status,size >> "%logfile%" 2>&1

:: Verificar espaço em disco
call :ShowProgress "%amarelo%[3/10] Verificando espaço em disco...%reset%"
wmic logicaldisk get deviceid,freespace,size >> "%logfile%" 2>&1

:: Verificar arquivos de erro do Windows
call :ShowProgress "%amarelo%[4/10] Verificando arquivos de erro do Windows...%reset%"
if exist C:\Windows\Memory.dmp (
    dir "C:\Windows\Memory.dmp" >> "%logfile%" 2>&1
)

:: Verificar arquivos temporários
call :ShowProgress "%amarelo%[5/10] Verificando arquivos temporários...%reset%"
dir /s "%TEMP%" | findstr "File(s)" >> "%logfile%" 2>&1

:: Verificar programas instalados
call :ShowProgress "%amarelo%[6/10] Verificando programas instalados...%reset%"
wmic product get name,version,installdate >> "%logfile%" 2>&1

:: Verificar serviços com erro
call :ShowProgress "%amarelo%[7/10] Verificando serviços com erro...%reset%"
sc query state= all | findstr "SERVICE_NAME STATE" | findstr /V "RUNNING" >> "%logfile%" 2>&1

:: Verificar logs de eventos
call :ShowProgress "%amarelo%[8/10] Verificando logs de eventos...%reset%"
wevtutil qe System /c:30 /f:text /rd:true >> "%logfile%" 2>&1

:: Verificar integridade do sistema
call :ShowProgress "%amarelo%[9/10] Verificando integridade do sistema...%reset%"
sfc /verifyonly >> "%logfile%" 2>&1

:: Verificar problemas de disco
call :ShowProgress "%amarelo%[10/10] Verificando problemas no disco...%reset%"
chkdsk C: /scan >> "%logfile%" 2>&1

:: Análise final e recomendações
call :ShowProgress "%verde%Gerando análise final...%reset%"
echo. >> "%logfile%"
echo === Recomendações === >> "%logfile%"

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