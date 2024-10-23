@echo off
REM ------------------------------------------------------------
REM Script: schedule_task.bat
REM Finalidade: Agendar a execução semanal do script system_check.py
REM ------------------------------------------------------------

REM Configurações
SET "TASK_NAME=Windows System Maintenance"
SET "PYTHON_PATH=python"
SET "SCRIPT_PATH=C:\WindowsMaintenanceLogs\system_check.py"
SET "LOG_PATH=C:\WindowsMaintenanceLogs\schedule_task.log"
SET "SCHEDULE=Weekly"
SET "DAY=SUN"
SET "TIME=02:00"

REM Função para registrar mensagens no log
:log
echo %DATE% %TIME% - %~1 >> "%LOG_PATH%"
echo %~1
goto :eof

REM Verifica se o script Python existe
IF NOT EXIST "%SCRIPT_PATH%" (
    CALL :log "[Erro] O script Python não foi encontrado em %SCRIPT_PATH%."
    echo Por favor, verifique o caminho e tente novamente.
    pause
    exit /b 1
)

REM Verifica se a tarefa já está agendada
schtasks /Query /TN "%TASK_NAME%" >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    REM Tarefa existe, verificar a ação
    FOR /F "tokens=2,* delims=:" %%A IN ('schtasks /Query /TN "%TASK_NAME%" /V /FO LIST ^| findstr /I "Task To Run"') DO (
        SET "TASK_ACTION=%%B"
    )

    REM Remove espaços em branco no início da variável
    SET "TASK_ACTION=%TASK_ACTION:~1%"

    REM Verifica se a ação corresponde ao script atual
    ECHO %TASK_ACTION% | FINDSTR /I /C:"%SCRIPT_PATH%" >nul
    IF %ERRORLEVEL% EQU 0 (
        CALL :log "A tarefa agendada \"%TASK_NAME%\" já está configurada corretamente."
        echo Nenhuma ação necessária. A tarefa já está atualizada.
        pause
        exit /b 0
    ) ELSE (
        CALL :log "A tarefa agendada \"%TASK_NAME%\" existe, mas está executando um script diferente."
        CALL :log "Removendo a tarefa existente..."
        schtasks /Delete /TN "%TASK_NAME%" /F >> "%LOG_PATH%" 2>&1
        IF %ERRORLEVEL% NEQ 0 (
            CALL :log "[Erro] Falha ao remover a tarefa agendada \"%TASK_NAME%\"."
            echo Falha ao remover a tarefa agendada.
            pause
            exit /b 1
        )
    )
)

REM Cria a tarefa agendada
CALL :log "Criando a tarefa agendada \"%TASK_NAME%\" para executar semanalmente..."
schtasks /Create /TN "%TASK_NAME%" /TR "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" --version 1.0.0" /SC %SCHEDULE% /D %DAY% /ST %TIME% /RL HIGHEST /F >> "%LOG_PATH%" 2>&1

IF %ERRORLEVEL% EQU 0 (
    CALL :log "Tarefa agendada \"%TASK_NAME%\" criada com sucesso."
    REM Notifica o usuário
    powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('A tarefa agendada \"%TASK_NAME%\" foi criada com sucesso e será executada semanalmente.', 'Tarefa Agendada', [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)"
) ELSE (
    CALL :log "[Erro] Falha ao criar a tarefa agendada \"%TASK_NAME%\"."
    echo Falha ao criar a tarefa agendada.
    REM Notifica o usuário sobre o erro
    powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Falha ao criar a tarefa agendada \"%TASK_NAME%\". Verifique o log para mais detalhes.', 'Erro', [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)"
    pause
    exit /b 1
)

pause
exit /b 0
