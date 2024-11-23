# SystemOptimizer

O **SystemOptimizer** é um script Python que realiza otimizações gerais no sistema Windows, incluindo:

- Verificação e instalação de dependências.
- Criação de ambiente virtual para execução isolada.
- Criação de ponto de restauração do sistema.
- Análise e otimização do desempenho do sistema.
- Geração de relatórios detalhados.
- Notificação ao usuário sobre os resultados.

## **Pré-requisitos**

- **Windows 10 ou Windows 11**
- **Python 3.6+** instalado no sistema (recomendado utilizar o [Python 3.11](https://www.python.org/downloads/))
- **Privilégios de administrador** para criar pontos de restauração e executar otimizações do sistema.

## **Instruções de Uso**

### **1. Clonar o Repositório ou Baixar os Arquivos**

Baixe os arquivos do projeto e extraia-os em uma pasta de sua preferência, por exemplo, `C:\SystemOptimizer`.

### **2. Instalar o Python (se necessário)**

Se você não tiver o Python instalado, faça o download em [python.org](https://www.python.org/downloads/) e instale-o.

**Importante:** Durante a instalação, selecione a opção **"Add Python to PATH"**.

### **3. Executar o Script de Configuração**

Abra o **Prompt de Comando** ou **PowerShell** como **administrador**:

1. Clique no menu **Iniciar**.
2. Digite **"cmd"** ou **"PowerShell"**.
3. Clique com o botão direito em **Prompt de Comando** ou **PowerShell** e selecione **"Executar como administrador"**.

Navegue até o diretório do projeto:

```bash
cd C:\SystemOptimizer


---

## **7. Instruções Adicionais para Usuários Não Técnicos**

- **Passo a Passo Visual:**

  1. **Baixe e instale o Python** se ainda não o fez.
  2. **Baixe os arquivos do projeto** e extraia-os em uma pasta fácil de encontrar, como na área de trabalho.
  3. **Abra o Prompt de Comando como administrador**:
     - Clique no menu Iniciar.
     - Digite "cmd".
     - Clique com o botão direito em "Prompt de Comando" e selecione "Executar como administrador".
  4. **Navegue até a pasta do projeto**:
     ```bash
     cd C:\Users\SeuUsuario\Desktop\SystemOptimizer
     ```
  5. **Execute o script de configuração**:
     ```bash
     setup_env.bat
     ```
  6. **Execute o script principal**:
     ```bash
     python system_optimizer.py
     ```
  7. **Aguarde a conclusão** e verifique as notificações na tela.

- **Como Restaurar o Sistema:**

  - Caso algo não funcione como esperado após a otimização, você pode restaurar o sistema ao ponto de restauração criado:
    1. Abra o **Painel de Controle**.
    2. Vá para **Recuperação** > **Abrir Restauração do Sistema**.
    3. Selecione o ponto de restauração criado pelo **SystemOptimizer**.
    4. Siga as instruções na tela.

---

## **8. Considerações de Segurança**

- **Execução Segura:** O script foi projetado para ser seguro e não executar comandos maliciosos.
- **Código Aberto:** Você pode revisar o código fonte para verificar todas as ações realizadas pelo script.
- **Ponto de Restauração:** Um ponto de restauração é criado antes de qualquer modificação para garantir que você possa retornar ao estado anterior se necessário.

---

## **9. Conclusão**

Com este conjunto de scripts e instruções, qualquer pessoa, mesmo sem conhecimento técnico aprofundado, poderá executar o script de otimização do sistema no Windows 11. O script é modular e pode ser estendido ou modificado conforme necessário.

Se tiver dúvidas ou precisar de assistência adicional, sinta-se à vontade para pedir ajuda!
