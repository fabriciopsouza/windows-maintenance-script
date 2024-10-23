@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: Cores
set "GREEN=[32m"
set "RED=[31m"
set "YELLOW=[33m"
set "BLUE=[34m"
set "RESET=[0m"

:: Título
title Verificação do Sistema Windows

:: Verifica Admin
net session >nul 2>&1
if errorlevel 1 (
    echo %RED%Este script requer privilégios de administrador!%RESET%
    echo Por favor, execute como administrador.
    pause
    exit /b 1
)

:: Banner
cls
echo %BLUE%=================================%RESET%
echo %BLUE%   Verificação do Sistema        %RESET%
echo %BLUE%=================================%RESET%
echo.

:: Verifica Python
echo %YELLOW%Verificando ambiente Python...%RESET%
where python >nul 2>&1
if errorlevel 1 (
    echo %RED%Python não encontrado!%RESET%
    echo Instalando dependências necessárias...

    :: Tenta usar o Conda se disponível
    where conda >nul 2>&1
    if errorlevel 1 (
        echo %RED%Conda não encontrado.%RESET%
        echo Por favor, instale Python ou Anaconda/Miniconda.
        pause
        exit /b 1
    )

    :: Configura ambiente Conda
    echo %YELLOW%Configurando ambiente Conda...%RESET%
    call conda activate base || (
        echo %RED%Erro ao ativar Conda.%RESET%
        pause
        exit /b 1
    )
)

:: Instala dependências
echo %YELLOW%Verificando dependências...%RESET%
python -m pip install --upgrade pip >nul
python -m pip install wmi psutil colorama >nul

:: Executa script principal
echo %GREEN%Iniciando verificação...%RESET%
echo.
python system_check.py

if errorlevel 1 (
    echo %RED%Erro na execução do script.%RESET%
    echo Verifique o log para mais detalhes.
    pause
    exit /b 1
)

endlocal