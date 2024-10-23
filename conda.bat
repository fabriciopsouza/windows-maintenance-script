@echo off
:: Verificar se o script está sendo executado como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running script as an administrator...
    echo.

    :: Ativar o ambiente Conda base e executar o script
    call C:\Users\fpsou\anaconda3\Scripts\activate.bat base
    echo Iniciando verificação...
    python C:\Users\fpsou\PycharmProjects\windows-maintenance-script\system_check.py
    pause
) else (
    echo Requesting administrative privileges...
    echo.
    powershell Start-Process '%~f0' -Verb runAs
    exit
)