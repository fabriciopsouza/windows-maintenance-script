import subprocess
import sys
import os
import logging
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import psutil
import threading

try:
    import wmi
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'wmi'])
    import wmi

try:
    from plyer import notification
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'plyer'])
    from plyer import notification

try:
    from colorama import init, Fore
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'colorama'])
    from colorama import init, Fore

# Inicializa o colorama
init(autoreset=True)

class SystemOptimizer:
    VERSION = "2.0.0"
    LOG_PATH = r"C:\WindowsMaintenanceLogs\system_optimizer.log"
    REPORT_PATH = r"C:\WindowsMaintenanceLogs\relatorio_{date}.txt"
    JSON_REPORT_PATH = r"C:\WindowsMaintenanceLogs\report_{date}.json"
    THRESHOLDS = {
        'disk_critical': 90,
        'disk_high': 80
    }
    STARTUP_PROGRAMS = []

    def __init__(self):
        # Configura o logger
        os.makedirs(os.path.dirname(self.LOG_PATH), exist_ok=True)
        logging.basicConfig(
            filename=self.LOG_PATH,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger()
        try:
            self.wmi = wmi.WMI()
        except Exception as e:
            self.logger.error(f"Erro ao inicializar WMI: {e}")
            self.wmi = None
        self.results = {}
        self.total_steps = 8  # Total de etapas no processo de otimização
        self.current_step = 0
        self.start_time = time.time()

    def update_progress(self, message: str):
        """Atualiza o progresso e informa o usuário."""
        self.current_step += 1
        elapsed_time = time.time() - self.start_time
        estimated_total_time = (elapsed_time / self.current_step) * self.total_steps
        remaining_time = estimated_total_time - elapsed_time
        print(f"{Fore.CYAN}[{self.current_step}/{self.total_steps}] {message}")
        print(f"{Fore.YELLOW}Tempo estimado restante: {remaining_time/60:.2f} minutos")
        self.logger.info(message)

    def check_app_version(self):
        """Verifica se há uma versão mais recente do aplicativo."""
        self.update_progress("Verificando a versão do aplicativo...")
        # Implementar a lógica para verificar a versão mais recente (por exemplo, via GitHub API)
        # Para simplificar, assumiremos que a versão está atualizada
        latest_version = "2.0.0"
        if self.VERSION != latest_version:
            self.logger.warning(f"Uma nova versão ({latest_version}) está disponível.")
            print(f"{Fore.YELLOW}Uma nova versão ({latest_version}) está disponível.")
        else:
            self.logger.info("O aplicativo está atualizado.")

    def check_and_install_dependencies(self):
        """Verifica e instala dependências faltantes."""
        self.update_progress("Verificando dependências...")
        required_packages = ['psutil', 'wmi', 'plyer', 'colorama']
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                self.logger.warning(f"Pacote {package} não encontrado. Instalando...")
                print(f"{Fore.YELLOW}Instalando dependência: {package}")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

    def create_system_restore_point(self):
        """Cria um ponto de restauração do sistema."""
        self.update_progress("Criando ponto de restauração do sistema...")
        try:
            restore_point_script = os.path.join(os.getcwd(), 'create_restore_point.ps1')
            subprocess.check_call([
                'powershell.exe',
                '-ExecutionPolicy', 'Bypass',
                '-File', restore_point_script
            ])
            self.logger.info("Ponto de restauração criado com sucesso.")
        except Exception as e:
            self.logger.error(f"Erro ao criar ponto de restauração: {e}")
            print(f"{Fore.RED}Erro ao criar ponto de restauração: {e}")

    def clean_temp_files(self):
        """Limpa arquivos temporários e desnecessários."""
        self.update_progress("Limpando arquivos temporários...")
        temp_dirs = [
            os.getenv('TEMP'),
            os.path.join(os.getenv('SYSTEMROOT'), 'Temp'),
        ]
        total_files_deleted = 0
        for temp_dir in temp_dirs:
            try:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                            total_files_deleted += 1
                        except Exception:
                            pass
                self.logger.info(f"Arquivos temporários limpos em: {temp_dir}")
            except Exception as e:
                self.logger.error(f"Erro ao limpar {temp_dir}: {e}")
        print(f"{Fore.GREEN}Total de arquivos temporários deletados: {total_files_deleted}")

    def run_system_file_checker(self):
        """Executa o SFC /scannow para verificar e reparar arquivos do sistema."""
        self.update_progress("Executando verificação do SFC...")
        try:
            subprocess.check_call(['sfc', '/scannow'], shell=True)
            self.logger.info("Verificação do SFC concluída.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao executar SFC: {e}")
            print(f"{Fore.RED}Erro ao executar SFC: {e}")

    def run_dism_commands(self):
        """Executa comandos DISM para reparar a imagem do sistema."""
        self.update_progress("Executando reparo DISM...")
        try:
            subprocess.check_call(['DISM', '/Online', '/Cleanup-Image', '/CheckHealth'], shell=True)
            subprocess.check_call(['DISM', '/Online', '/Cleanup-Image', '/ScanHealth'], shell=True)
            subprocess.check_call(['DISM', '/Online', '/Cleanup-Image', '/RestoreHealth'], shell=True)
            self.logger.info("Comandos DISM concluídos.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao executar DISM: {e}")
            print(f"{Fore.RED}Erro ao executar DISM: {e}")

    def schedule_memory_check(self):
        """Agenda uma verificação de memória na próxima inicialização."""
        self.update_progress("Agendando verificação de memória...")
        try:
            subprocess.check_call(['mdsched.exe', '/restart'], shell=True)
            self.logger.info("Verificação de memória agendada.")
            print(f"{Fore.GREEN}Verificação de memória será executada na próxima reinicialização.")
        except Exception as e:
            self.logger.error(f"Erro ao agendar verificação de memória: {e}")
            print(f"{Fore.RED}Erro ao agendar verificação de memória: {e}")

    def optimize_startup_programs(self):
        """Otimiza programas de inicialização desabilitando programas desnecessários."""
        self.update_progress("Otimizando programas de inicialização...")
        try:
            # Usando WMI para listar programas de inicialização
            startup_items = self.wmi.Win32_StartupCommand()
            for item in startup_items:
                self.STARTUP_PROGRAMS.append({
                    'Name': item.Name,
                    'Command': item.Command,
                    'Location': item.Location,
                    'User': item.User
                })
            # Desabilitar programas não essenciais (exemplo)
            unnecessary_programs = ['Adobe Reader', 'Skype', 'OneDrive']
            disabled_programs = []
            for program in self.STARTUP_PROGRAMS:
                for un_prog in unnecessary_programs:
                    if un_prog.lower() in program['Name'].lower():
                        # Remover a entrada do registro
                        subprocess.call(['reg', 'delete', program['Location'], '/v', program['Name'], '/f'], shell=True)
                        disabled_programs.append(program['Name'])
                        self.logger.info(f"Desabilitado programa de inicialização: {program['Name']}")
            print(f"{Fore.GREEN}Programas desabilitados: {', '.join(disabled_programs)}")
        except Exception as e:
            self.logger.error(f"Erro ao otimizar programas de inicialização: {e}")
            print(f"{Fore.RED}Erro ao otimizar programas de inicialização: {e}")

    def optimize_system(self):
        """Executa otimizações gerais no sistema."""
        self.update_progress("Realizando otimizações gerais...")
        # Por exemplo, ajustar configurações de desempenho, desfragmentar discos (se aplicável), etc.
        try:
            # Desfragmentação (somente para HDDs, não SSDs)
            for partition in psutil.disk_partitions():
                if 'fixed' in partition.opts.lower():
                    subprocess.call(['defrag', partition.device, '/U', '/V'], shell=True)
            self.logger.info("Otimização do sistema concluída.")
        except Exception as e:
            self.logger.error(f"Erro durante otimização do sistema: {e}")
            print(f"{Fore.RED}Erro durante otimização do sistema: {e}")

    def check_disk_health(self) -> Dict[str, Any]:
        """Verificação da saúde dos discos."""
        self.update_progress("Analisando saúde dos discos...")
        disk_info = {}

        if self.wmi is None:
            self.logger.error("WMI não está disponível. Pulando verificação de discos físicos.")
            return disk_info

        # Verificação física
        for disk in self.wmi.Win32_DiskDrive():
            serial_number = disk.SerialNumber.strip() if disk.SerialNumber else "N/A"
            disk_info[disk.DeviceID] = {
                "Modelo": disk.Model,
                "Tamanho": self.format_size(int(disk.Size or 0)),
                "Status": disk.Status,
                "Interface": disk.InterfaceType,
                "Serial": serial_number,
                "Partições": disk.Partitions,
                "Bytes/Setor": disk.BytesPerSector
            }

            # Verificação SMART
            smart_status = disk.Status
            disk_info[disk.DeviceID]["SMART"] = smart_status
            if smart_status != "OK":
                self.logger.warning(f"Disco {disk.DeviceID} com possível problema!")

        # Verificação lógica
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                device = partition.device
                if device not in disk_info:
                    disk_info[device] = {}
                disk_info[device].update({
                    "Ponto de Montagem": partition.mountpoint,
                    "Sistema de Arquivos": partition.fstype,
                    "Total": self.format_size(usage.total),
                    "Usado": self.format_size(usage.used),
                    "Livre": self.format_size(usage.free),
                    "Porcentagem Uso": f"{usage.percent}%"
                })

                # Avaliação do uso
                if usage.percent >= self.THRESHOLDS['disk_critical']:
                    self.logger.critical(
                        f"Espaço crítico em {partition.mountpoint}: {usage.percent}%"
                    )
                elif usage.percent >= self.THRESHOLDS['disk_high']:
                    self.logger.warning(
                        f"Espaço baixo em {partition.mountpoint}: {usage.percent}%"
                    )

            except Exception as e:
                self.logger.error(f"Erro ao verificar partição {partition.mountpoint}: {e}")

        self.results['disk_health'] = disk_info
        return disk_info

    def check_system_performance(self):
        """Analisa o desempenho do sistema."""
        self.update_progress("Analisando desempenho do sistema...")

        # Análise de CPU
        cpu_percent_per_core = psutil.cpu_percent(interval=1, percpu=True)
        cpu_total = psutil.cpu_percent(interval=1)
        self.results['cpu'] = {
            "Uso por Núcleo": [f"{percent}%" for percent in cpu_percent_per_core],
            "Uso Total": f"{cpu_total}%",
            "Núcleos Físicos": psutil.cpu_count(logical=False),
            "Núcleos Lógicos": psutil.cpu_count(logical=True),
            "Frequência Atual": f"{psutil.cpu_freq().current}MHz",
            "Frequência Mínima": f"{psutil.cpu_freq().min}MHz",
            "Frequência Máxima": f"{psutil.cpu_freq().max}MHz",
            "Tempo Sistema": f"{psutil.cpu_times().system / 3600:.2f}h",
            "Tempo Usuário": f"{psutil.cpu_times().user / 3600:.2f}h",
            "Tempo Ocioso": f"{psutil.cpu_times().idle / 3600:.2f}h"
        }
        self.logger.info(f"Uso Total de CPU: {cpu_total}%")

        # Análise de Memória
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()
        self.results['memory'] = {
            "RAM Total": self.format_size(virtual_mem.total),
            "RAM Disponível": self.format_size(virtual_mem.available),
            "RAM Usada": self.format_size(virtual_mem.used),
            "RAM Porcentagem": f"{virtual_mem.percent}%",
            "Swap Total": self.format_size(swap_mem.total),
            "Swap Usado": self.format_size(swap_mem.used),
            "Swap Porcentagem": f"{swap_mem.percent}%"
        }
        self.logger.info(f"Memória RAM Usada: {virtual_mem.percent}%")
        self.logger.info(f"Memória Swap Usada: {swap_mem.percent}%")

        # Processos mais ativos
        processes = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
                           key=lambda p: p.info['cpu_percent'], reverse=True)[:5]
        self.results['top_processes'] = [
            {
                "Nome": proc.info['name'],
                "CPU": f"{proc.info['cpu_percent']}%",
                "Memória": f"{proc.info['memory_percent']:.2f}%"
            } for proc in processes
        ]
        self.logger.info("Processos mais ativos:")
        for proc in self.results['top_processes']:
            self.logger.info(f"{proc['Nome']}: CPU {proc['CPU']}, Memória {proc['Memória']}")

    def format_size(self, size_bytes: int) -> str:
        """Formata o tamanho em bytes para uma string legível."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"

    def save_reports(self):
        """Salva os relatórios em TXT e JSON."""
        self.update_progress("Salvando relatórios...")
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        text_file = self.REPORT_PATH.format(date=date_str)
        json_file = self.JSON_REPORT_PATH.format(date=date_str)
        os.makedirs(os.path.dirname(text_file), exist_ok=True)

        # Salva o relatório TXT
        try:
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write("==================================================\n")
                f.write("Relatório de Otimização do Sistema\n")
                f.write("==================================================\n\n")
                f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                f.write("Desempenho do Sistema:\n")
                for key, value in self.results.get('cpu', {}).items():
                    f.write(f"  {key}: {value}\n")
                for key, value in self.results.get('memory', {}).items():
                    f.write(f"  {key}: {value}\n")
                f.write("\nProcessos Mais Ativos:\n")
                for proc in self.results.get('top_processes', []):
                    f.write(f"  {proc['Nome']}: CPU {proc['CPU']}, Memória {proc['Memória']}\n")
                f.write("\nSaúde dos Discos:\n")
                for device, info in self.results.get('disk_health', {}).items():
                    f.write(f"\nDisco {device}:\n")
                    for k, v in info.items():
                        f.write(f"  {k}: {v}\n")
            self.logger.info(f"Relatório TXT salvo em: {text_file}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar relatório TXT: {e}")

        # Salva o relatório JSON
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=4)
            self.logger.info(f"Relatório JSON salvo em: {json_file}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar relatório JSON: {e}")

    def notify_user(self):
        """Notifica o usuário sobre os resultados da otimização."""
        try:
            notification.notify(
                title="Otimização do Sistema Concluída",
                message="Seu sistema foi otimizado com sucesso!",
                timeout=10  # Duração em segundos
            )
        except Exception as e:
            self.logger.error(f"Erro ao notificar usuário: {e}")

    def run(self):
        """Executa todas as etapas de otimização."""
        self.start_time = time.time()
        self.check_app_version()
        self.check_and_install_dependencies()
        self.create_system_restore_point()
        self.clean_temp_files()
        self.run_system_file_checker()
        self.run_dism_commands()
        self.schedule_memory_check()
        self.check_disk_health()
        self.check_system_performance()
        self.optimize_startup_programs()
        self.optimize_system()
        self.save_reports()
        self.notify_user()
        total_time = (time.time() - self.start_time) / 60
        print(Fore.GREEN + f"Otimização Concluída com Sucesso em {total_time:.2f} minutos!")
        self.logger.info(f"Otimização concluída em {total_time:.2f} minutos.")

if __name__ == "__main__":
    optimizer = SystemOptimizer()
    optimizer.run()
