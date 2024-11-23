@echo off
REM Configura o ambiente virtual e instala as dependências

python -m venv env
call env\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
echo Ambiente virtual configurado e dependências instaladas.
