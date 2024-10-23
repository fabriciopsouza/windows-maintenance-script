import os
import sys
import wmi
import time
import psutil
import winreg
import logging
import platform
import subprocess
import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from colorama import init, Fore, Style, Back

# Força UTF-8
sys.stdout.reconfigure(encoding='utf-8')
os.system('chcp 65001')


class WindowsSystemCheck:
    def __init__(self):
        init(autoreset=True)  # Inicializa colorama com autoreset
        self.wmi = wmi.WMI()
        self.log_dir = Path("C:\\WindowsMaintenanceLogs")
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"system_check_{self.timestamp}.log"
        self.total_steps = 10
        self.current_step = 0
        self.setup_logging()

    def setup_logging(self):
        """Configura sistema de logs."""
        self.log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8', errors='replace'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def update_progress(self, message: str):
        """Atualiza barra de progresso."""
        self.current_step += 1
        percentage = (self.current_step / self.total_steps) * 100
        bar_length = 40
        filled_length = int(bar_length * self.current_step // self.total_steps)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)

        print(f'\r{Fore.GREEN}[{bar}] {percentage:.1f}% - {message}', end='\r')
        if self.current_step == self.total_steps:
            print()  # Nova linha ao completar

        self.logger.info(message)
        time.sleep(0.5)  # Pequeno delay para visualização

    def run_command(self, command: str, timeout=30) -> str:
        """Executa comando com timeout."""
        try:
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout
            )
            return process.stdout
        except subprocess.TimeoutExpired:
            self.logger.error(f"Comando excedeu timeout de {timeout}s: {command}")
            return "Timeout ao executar comando"
        except Exception as e:
            self.logger.error(f"Erro ao executar comando: {str(e)}")
            return f"Erro: {str(e)}"

    def check_admin(self) -> bool:
        """Verifica privilégios de administrador."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_checks(self):
        """Executa verificações do sistema."""
        print(f"{Back.BLUE}{Fore.WHITE} Iniciando Verificação do Sistema {Style.RESET_ALL}\n")

        if not self.check_admin():
            print(f"{Back.RED}{Fore.WHITE} Este script precisa ser executado como administrador! {Style.RESET_ALL}")
            sys.exit(1)

        try:
            # Informações do Sistema
            self.update_progress("Coletando informações do sistema...")
            system_info = platform.uname()
            self.logger.info(f"Sistema: {system_info.system} {system_info.release}")

            # Status dos Discos
            self.update_progress("Verificando discos...")
            for disk in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(disk.mountpoint)
                    self.logger.info(f"Disco {disk.mountpoint}: {usage.percent}% usado")
                except:
                    continue

            # Memória
            self.update_progress("Verificando memória...")
            memory = psutil.virtual_memory()
            self.logger.info(f"Memória: {memory.percent}% em uso")

            # Processos
            self.update_progress("Analisando processos...")
            for proc in psutil.process_iter(['name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 50:
                        self.logger.info(f"Processo com alto uso de CPU: {proc.info['name']}")
                except:
                    continue

            # Serviços Windows
            self.update_progress("Verificando serviços...")
            services_output = self.run_command('sc query state= all')
            self.logger.info("Verificação de serviços concluída")

            # Arquivos temporários
            self.update_progress("Verificando arquivos temporários...")
            temp_size = self.run_command('dir /s %TEMP%')
            self.logger.info("Verificação de arquivos temporários concluída")

            # Windows Update
            self.update_progress("Verificando Windows Update...")
            updates = self.run_command('wmic qfe list brief')
            self.logger.info("Verificação de atualizações concluída")

            # Logs de Eventos
            self.update_progress("Analisando logs de eventos...")
            events = self.run_command('wevtutil qe System /c:5 /f:text')
            self.logger.info("Análise de logs concluída")

            # Verificação do Sistema
            self.update_progress("Executando verificação do sistema...")
            sfc_output = self.run_command('sfc /verifyonly')
            self.logger.info("Verificação SFC concluída")

            # SMART dos discos
            self.update_progress("Verificando saúde dos discos...")
            for disk in self.wmi.Win32_DiskDrive():
                self.logger.info(f"Disco {disk.Caption}: Status {disk.Status}")

            # Relatório Final
            print(f"\n{Back.GREEN}{Fore.WHITE} Verificação Concluída! {Style.RESET_ALL}")
            print(f"\nRelatório salvo em: {self.log_file}")

            # Abre o arquivo de log
            os.startfile(self.log_file)

        except Exception as e:
            print(f"\n{Back.RED}{Fore.WHITE} Erro durante a verificação: {str(e)} {Style.RESET_ALL}")
            self.logger.error(f"Erro durante a verificação: {str(e)}")


if __name__ == "__main__":
    checker = WindowsSystemCheck()
    checker.run_checks()