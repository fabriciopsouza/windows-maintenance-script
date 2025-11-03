# SystemOptimizer v3.0.0

O **SystemOptimizer** é um script Python completo e robusto que realiza otimizações avançadas no sistema Windows 11 Pro, incluindo:

## 🚀 **Funcionalidades Principais**

### **Limpeza e Otimização**
- ✅ Limpeza profunda de arquivos temporários (sistema, usuário, prefetch)
- ✅ Limpeza de cache de navegadores (Chrome, Edge, Firefox, Brave)
- ✅ Limpeza de cache do Windows (DNS, Windows Update, INetCache)
- ✅ Limpeza de registro do Windows (entradas inválidas)
- ✅ Remoção de atalhos quebrados (Desktop, Menu Iniciar)
- ✅ Detecção de instalações antigas e quebradas

### **Verificação e Reparo**
- ✅ SFC (System File Checker) - Verificação de integridade do sistema
- ✅ DISM completo (CheckHealth, ScanHealth, RestoreHealth, ComponentCleanup)
- ✅ Verificação de drivers com detecção de problemas
- ✅ Análise de saúde dos discos (SMART, uso, partições)

### **Otimização de Disco**
- ✅ **Desfragmentação com CONFIRMAÇÃO OBRIGATÓRIA** (timeout de 30s)
- ✅ Detecção automática de SSDs vs HDDs
- ✅ TRIM para SSDs (sem desfragmentação)
- ✅ Desfragmentação apenas para HDDs
- ⚠️ **IMPORTANTE**: Se não confirmar desfragmentação, o script ENCERRA

### **Monitoramento e Relatórios**
- ✅ Análise completa de desempenho (CPU, RAM, processos)
- ✅ Relatórios detalhados em TXT e JSON
- ✅ Sistema de logs robusto com rotação (máx 10MB, 5 backups)
- ✅ Rastreamento de erros e avisos
- ✅ Notificações do sistema

### **Segurança**
- ✅ Criação automática de ponto de restauração
- ✅ Verificação de privilégios de administrador
- ✅ Tratamento robusto de erros
- ✅ Cancelamento seguro (Ctrl+C)

## **Pré-requisitos**

- **Windows 11 Pro** (otimizado para esta versão, mas funciona em Windows 10)
- **Python 3.8+** instalado no sistema (recomendado utilizar o [Python 3.11+](https://www.python.org/downloads/))
- **Privilégios de administrador** (OBRIGATÓRIO - o script verifica e aborta se não executado como admin)
- **Conexão com internet** (para instalação automática de dependências, se necessário)

### **Dependências Python (instaladas automaticamente)**
- `psutil` - Monitoramento de sistema
- `wmi` - Interface WMI do Windows
- `pywin32` - APIs do Windows (instalado sob demanda)
- `plyer` - Notificações do sistema
- `colorama` - Interface colorida no terminal

## **Instruções de Uso**

### **Método 1: Instalação Rápida (Recomendado)**

1. **Clone ou baixe o repositório:**
   ```bash
   git clone https://github.com/SEU-USUARIO/windows-maintenance-script.git
   cd windows-maintenance-script
   ```

2. **Execute o setup (cria ambiente virtual e instala dependências):**
   ```bash
   setup_env.bat
   ```

3. **Execute o script como administrador:**
   - Abra o **PowerShell** ou **CMD** como **Administrador**
   - Navegue até a pasta do projeto
   - Execute:
   ```bash
   python system_optimizer.py
   ```

### **Método 2: Execução Direta (sem ambiente virtual)**

1. **Abra PowerShell/CMD como Administrador**

2. **Navegue até a pasta do projeto:**
   ```bash
   cd C:\caminho\para\windows-maintenance-script
   ```

3. **Execute o script:**
   ```bash
   python system_optimizer.py
   ```
   > O script instalará automaticamente todas as dependências necessárias

---

## **⚠️ Importante: Processo de Desfragmentação**

Durante a execução, o script irá:

1. **Detectar automaticamente** se seus discos são SSDs ou HDDs
2. Para **SSDs**: Executará TRIM automaticamente (rápido e seguro)
3. Para **HDDs**: **SOLICITARÁ CONFIRMAÇÃO** para desfragmentação

### **Comportamento da Confirmação:**
```
Deseja executar a DESFRAGMENTAÇÃO dos HDDs?
Digite 'S' para SIM ou 'N' para NÃO (Timeout em 30s):
```

- ✅ **Se você digitar 'S'**: Desfragmentação será executada
- ❌ **Se você digitar 'N' ou não responder em 30s**:
  - O script **ENCERRARÁ IMEDIATAMENTE**
  - Todas as limpezas já realizadas serão **SALVAS NO RELATÓRIO**
  - Nenhuma outra operação será executada

> **DICA**: A desfragmentação pode levar de 30 minutos a 2+ horas dependendo do tamanho e fragmentação do disco. Execute apenas se tiver tempo disponível.

---

## **📊 Relatórios e Logs**

### **Localização dos Arquivos**

Todos os relatórios e logs são salvos em:
```
C:\WindowsMaintenanceLogs\
```

### **Tipos de Arquivos Gerados**

1. **`system_optimizer.log`** - Log principal com todas as operações
   - Rotação automática (máx 10MB, mantém 5 backups)
   - Formato: `YYYY-MM-DD HH:MM:SS - LEVEL - [FUNÇÃO] - Mensagem`

2. **`relatorio_YYYYMMDD_HHMMSS.txt`** - Relatório em texto
   - Resumo completo de todas as operações
   - Estatísticas de limpeza
   - Erros e avisos encontrados

3. **`report_YYYYMMDD_HHMMSS.json`** - Relatório em JSON
   - Dados estruturados para análise automatizada
   - Inclui metadados (versão, timestamp, duração)

### **Conteúdo dos Relatórios**

- ✅ Resumo de limpeza (arquivos deletados, espaço liberado)
- ✅ Desempenho do sistema (CPU, RAM, processos)
- ✅ Saúde dos discos (status SMART, uso, partições)
- ✅ Verificação de drivers (problemas detectados)
- ✅ Instalações antigas/quebradas encontradas
- ✅ Lista completa de erros e avisos
- ✅ Tempo total de execução

---

## **🔧 Etapas de Execução**

O script executa as seguintes etapas em ordem:

1. ✅ Verificação de privilégios de administrador
2. ✅ Verificação de versão do aplicativo
3. ✅ Instalação automática de dependências
4. ✅ Criação de ponto de restauração
5. ✅ Análise inicial do sistema (discos e performance)
6. ✅ Limpeza de arquivos temporários
7. ✅ Limpeza de cache de navegadores
8. ✅ Limpeza de cache do Windows
9. ✅ Limpeza de registro
10. ✅ Remoção de atalhos quebrados
11. ✅ Verificação de instalações antigas
12. ✅ Verificação de drivers
13. ✅ SFC (System File Checker)
14. ✅ DISM (Reparo de imagem do sistema)
15. ✅ Otimização de programas de inicialização
16. ⚠️ **Otimização de disco (COM CONFIRMAÇÃO)**
17. ✅ Geração de relatórios
18. ✅ Notificação ao usuário

---

## **🔒 Segurança e Restauração**

### **Ponto de Restauração**

- Criado **AUTOMATICAMENTE** antes de qualquer modificação
- Nome: "Ponto de Restauração Criado pelo SystemOptimizer"
- Tipo: MODIFY_SETTINGS

### **Como Restaurar o Sistema**

Caso algo não funcione como esperado:

1. Pressione `Win + R`
2. Digite: `rstrui.exe`
3. Clique em **OK**
4. Selecione o ponto de restauração do **SystemOptimizer**
5. Siga as instruções na tela

### **Considerações de Segurança**

- ✅ **Código Aberto** - Você pode revisar todo o código fonte
- ✅ **Sem Telemetria** - Nenhum dado é enviado para servidores externos
- ✅ **Operações Reversíveis** - Ponto de restauração garante reversão
- ✅ **Logs Detalhados** - Todas as ações são registradas
- ✅ **Tratamento de Erros** - Falhas não comprometem o sistema

---

## **❓ Perguntas Frequentes (FAQ)**

### **Q: O script funciona no Windows 10?**
**A:** Sim, mas é otimizado para Windows 11 Pro. Algumas funcionalidades podem ter comportamento ligeiramente diferente no Windows 10.

### **Q: Preciso desinstalar meu antivírus?**
**A:** Não. O script é seguro e não interfere com antivírus. Porém, alguns antivírus podem alertar sobre modificações no sistema - isso é normal.

### **Q: Quanto espaço em disco será liberado?**
**A:** Varia muito. Tipicamente entre 2GB a 20GB, dependendo de quanto tempo o sistema não é otimizado.

### **Q: O script pode danificar meu sistema?**
**A:** Não. Todas as operações são seguras e um ponto de restauração é criado. Em caso de problemas, basta restaurar o sistema.

### **Q: Posso cancelar durante a execução?**
**A:** Sim. Pressione `Ctrl+C`. O script salvará um relatório parcial das operações já realizadas.

### **Q: Com que frequência devo executar?**
**A:** Recomenda-se executar mensalmente para manter o sistema otimizado.

### **Q: O que fazer se aparecerem erros?**
**A:** Verifique o arquivo `system_optimizer.log` na pasta `C:\WindowsMaintenanceLogs\` para detalhes. A maioria dos erros é não-crítica.

---

## **🛠️ Solução de Problemas**

### **Erro: "Script precisa ser executado como Administrador"**
- **Solução**: Clique com botão direito no PowerShell/CMD e selecione "Executar como administrador"

### **Erro: "WMI não está disponível"**
- **Solução**: Execute `winmgmt /verifyrepository` como admin e reinicie o computador

### **Erro: Módulo não encontrado**
- **Solução**: Execute `pip install -r requirements.txt` manualmente

### **Desfragmentação muito lenta**
- **Normal**: HDDs grandes podem levar 2+ horas. Considere executar durante a noite.

---

## **📝 Licença**

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## **👤 Autor**

Desenvolvido com ❤️ para otimização de sistemas Windows

---

## **🤝 Contribuições**

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests

---

## **📞 Suporte**

Para dúvidas ou assistência:
- Abra uma [issue](https://github.com/SEU-USUARIO/windows-maintenance-script/issues) no GitHub
- Revise a documentação acima
- Consulte os logs em `C:\WindowsMaintenanceLogs\`
