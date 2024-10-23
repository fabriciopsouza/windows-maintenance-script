# Windows System Maintenance Script

Script automatizado para manutenção preventiva e corretiva do Windows, desenvolvido para facilitar a rotina de verificações e reparos do sistema.

## Características Principais

- 🎯 Interface visual com barra de progresso
- 🔄 Feedback em tempo real das verificações
- 🌈 Interface colorida para melhor visualização
- 📝 Logs formatados em UTF-8
- ⏱️ Sistema de timeout para operações
- 🛡️ Verificações completas do sistema

## Funcionalidades

### Verificações do Sistema
- ✅ Verificação de integridade do sistema (SFC)
- 🛠️ Reparo de imagem do sistema (DISM)
- 💽 Verificação de disco (CHKDSK)
- 🔍 Análise SMART dos discos
- 📊 Monitoramento de temperatura do CPU
- 💾 Verificação de memória RAM

### Manutenção
- 🧹 Limpeza de arquivos temporários
- 🔄 Verificação de serviços do Windows Update
- 🌐 Reset de componentes de rede
- 📝 Verificação de logs de eventos
- 🛡️ Análise de drivers e dispositivos

### Monitoramento
- 📈 Análise de desempenho em tempo real
- 💻 Verificação de processos
- 🔋 Monitoramento de energia
- 🌡️ Verificação de temperatura
- 🔍 Análise de registro do Windows

### Relatórios
- 📊 Sistema de logs detalhado em UTF-8
- 📝 Recomendações automáticas
- 📈 Análise de tendências
- 🔔 Alertas de problemas
- 📤 Exportação de resultados formatados

## Como Usar

### Método Recomendado
1. Execute `run_check.bat` como administrador
2. Aguarde a verificação automática de dependências
3. Observe o progresso na barra visual
4. Verifique o relatório que abrirá automaticamente

### Execução Manual Python
```bash
# Ambiente Conda
conda activate base
python system_check.py

# OU Python direto
python system_check.py
```

### Dependências
Instaladas automaticamente pelo script:
```bash
pip install wmi psutil colorama
```

## Estrutura do Projeto
```
windows-maintenance-script/
├── system_check.py     # Script principal Python
├── run_check.bat       # Launcher com verificações
└── README.md          # Documentação
```

## Logs

Os logs são salvos automaticamente em:
```
C:\WindowsMaintenanceLogs\system_check_YYYYMMDD_HHMMSS.log
```

Características dos logs:
- Codificação UTF-8
- Timestamp em cada entrada
- Informações detalhadas
- Formatação clara
- Abertura automática após conclusão

## Pré-requisitos

- Windows 10 ou 11
- Direitos de administrador
- Python 3.8+ ou Anaconda/Miniconda
- Conexão com internet (para instalação de dependências)

## Recursos Adicionais

- 🎨 Interface colorida para melhor visualização
- 🔄 Barra de progresso em tempo real
- 🔍 Detecção automática de problemas
- 📊 Recomendações personalizadas
- 🌐 Suporte a múltiplos idiomas
- ⚡ Timeouts em operações longas
- 🛠️ Tratamento de exceções robusto

## Autor

**Fabricio Pinheiro Souza**
- 📧 Email: fabriciopsouza@gmail.com
- 🌐 GitHub: [@fabriciopsouza](https://github.com/fabriciopsouza)

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Status do Projeto

🚧 Em desenvolvimento ativo

## Contribuições

Contribuições são bem-vindas! Por favor:
1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature
3. Faça seus commits
4. Envie um Pull Request

## Últimas Atualizações

- ✨ Adicionada barra de progresso visual
- 🔄 Melhorado feedback em tempo real
- 📝 Corrigido encoding para UTF-8
- ⚡ Adicionado sistema de timeout
- 🎨 Interface colorida aprimorada