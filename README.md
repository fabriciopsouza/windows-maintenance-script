# Windows System Maintenance Script

Script automatizado para manutenção preventiva e corretiva do Windows, desenvolvido para facilitar a rotina de verificações e reparos do sistema.

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
- 📈 Análise de desempenho
- 💻 Verificação de processos
- 🔋 Monitoramento de energia
- 🌡️ Verificação de temperatura
- 🔍 Análise de registro do Windows

### Relatórios
- 📊 Sistema de logs detalhado
- 📝 Recomendações automáticas
- 📈 Análise de tendências
- 🔔 Alertas de problemas
- 📤 Exportação de resultados

## Como Usar

### Versão Python
1. Instale as dependências:
```bash
pip install wmi psutil colorama
```

2. Execute o script como administrador:
```bash
python system_check.py
```

### Versão Batch
1. Execute o script como administrador:
```bash
system_check.bat
```

### Geral
- Aguarde a conclusão das verificações
- Verifique o relatório gerado automaticamente
- Siga as recomendações fornecidas
- Reinicie o computador quando solicitado

## Logs

Os logs são salvos automaticamente em:
```
C:\WindowsMaintenanceLogs\
```

O nome do arquivo inclui data e hora da execução.

## Pré-requisitos

- Windows 10 ou 11
- Direitos de administrador
- Python 3.8+ (para versão Python)
- Bibliotecas Python: wmi, psutil, colorama

## Recursos Adicionais

- Interface colorida para melhor visualização
- Detecção automática de problemas
- Recomendações personalizadas
- Análise detalhada de componentes
- Suporte a múltiplos idiomas
- Tratamento de exceções robusto

## Autor

**Fabricio Pinheiro Souza**
- 📧 Email: fabriciopsouza@gmail.com
- 🌐 GitHub: [@fabriciopsouza](https://github.com/fabriciopsouza)

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Status do Projeto

🚧 Em desenvolvimento ativo

## Contribuições

Contribuições são bem-vindas! Por favor, sinta-se à vontade para submeter pull requests.