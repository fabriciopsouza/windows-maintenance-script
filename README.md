# Windows System Maintenance

## Visão Geral

O **Windows System Maintenance** é um conjunto de ferramentas automatizadas desenvolvidas para realizar análises abrangentes do sistema, monitorar o desempenho, verificar a saúde dos discos, monitorar serviços críticos e fornecer recomendações para otimização e manutenção. Ele também gerencia a agendamento dessas análises para execução semanalmente, garantindo que seu sistema esteja sempre saudável e funcionando de forma eficiente.

## Estrutura do Projeto

- `system_check.py`: Script Python responsável por realizar as análises do sistema, gerar relatórios, gerenciar tarefas agendadas e fornecer recomendações.
- `schedule_task.bat`: Script Batch para agendar a execução semanal do `system_check.py` no **Agendador de Tarefas** do Windows.
- `README.md`: Este documento, fornecendo instruções detalhadas sobre configuração e uso.

## 1. Requisitos

### 1.1. Sistema Operacional

- **Windows 10** ou superior.

### 1.2. Privilégios

- **Administrador**: É necessário executar os scripts com privilégios de administrador para que possam criar e gerenciar tarefas agendadas corretamente.

### 1.3. Python

- **Python 3.6** ou superior.
- **Pip**: Gerenciador de pacotes do Python.

### 1.4. Dependências Python

Os seguintes pacotes Python são necessários:

- `win10toast`: Para notificações no Windows.
- `colorama`: Para cores no console.
- `wmi`: Para interagir com a WMI do Windows.
- `psutil`: Para monitoramento de processos e recursos do sistema.

## 2. Instalação

### 2.1. Instalar o Python

Se ainda não tiver o Python instalado:

1. Baixe o instalador do Python a partir do [site oficial](https://www.python.org/downloads/windows/).
2. Execute o instalador e certifique-se de marcar a opção **"Add Python to PATH"** durante a instalação.

### 2.2. Verificar Instalação do Python

Abra o **Prompt de Comando** e execute:

```bash
python --version
