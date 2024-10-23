import os
import sys
import subprocess
import ctypes
import logging
import platform
import json
import socket
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
import importlib
import getpass

# Definição da versão do script
__version__ = "1.0.0"


# Função para instalar pacotes com subprocess.run e tratamento de erros
def install_package(package_name: str, install_name: str):
    """
    :param package_name: The name of the package to be installed.
    :param install_name: The name used to install the package via pip.
    :return: None
    """
    try:
        print(f"Instalando dependência necessária: {install_name}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", install_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Falha na instalação do pacote {install_name}: {e.stderr}{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}Erro inesperado durante a instalação do pacote {install_name}: {e}{Style.RESET_ALL}")
        sys.exit(1)


# Tentativa de importar módulos necessários, instalar se ausente
required_packages = [
    ('win10toast', 'win10toast'),
    ('colorama', 'colorama'),
    ('wmi', 'wmi'),
    ('psutil', 'psutil'),
]

for package_name, install_name in required_packages:
    try:
        globals()[package_name] = importlib.import_module(package_name)
    except ImportError:
        install_package(package_name, install_name)
        globals()[package_name] = importlib.import_module(package_name)

from win10toast import ToastNotifier
from colorama import init, Fore, Back, Style

# Inicialização do Colorama
init(autoreset=True)


class SystemAnalyzer:
    """
    A classe SystemAnalyzer efetua a análise e manutenção do sistema Windows.

    TASK_NAME: Nome da tarefa agendada para manutenção do sistema.
    PYTHON_PATH: Caminho para o executável Python atual.
    SCRIPT_PATH: Caminho completo para este script.
    SCHEDULE: Frequência de execução da tarefa agendada.
    DAY: Dia da semana para execução da tarefa agendada.
    TIME: Horário para execução da tarefa agendada.
    LOG_PATH: Caminho para o arquivo de log da manutenção do sistema.

    Métodos:
        __init__(self):
            Inicializa a classe configurando o sistema, logging, WMI, barra de progresso e tarefa agendada.

        init_system(self):
            Inicialização do sistema com configurações aprimoradas.

        setup_logging(self):
            Configuração avançada do sistema de logging.

        setup_progress(self):
            Configuração da barra de progresso.

        setup_wmi(self):
            Configuração WMI com tratamento de erros.

        update_progress(self, message: str, status: str = 'info'):
            Barra de progresso com feedback visual aprimorado.

        run_command(self, command: str, timeout: int = 30) -> Tuple[str, bool]:
            Executa comando com tratamento de erros aprimorado.

        format_size(self, size_bytes: float) -> str:
            Formata tamanhos de arquivo de forma amigável.

        check_system_info(self) -> Dict[str, Any]:
            Verificação detalhada do sistema.
    """
    TASK_NAME = "Windows System Maintenance"
    PYTHON_PATH = sys.executable  # Caminho para o executável Python atual
    SCRIPT_PATH = Path(__file__).resolve()  # Caminho completo para este script
    SCHEDULE = "Weekly"
    DAY = "SUN"
    TIME = "02:00"
    LOG_PATH = Path("C:/WindowsMaintenanceLogs/system_check.log")

    def __init__(self):
        self.init_system()
        self.setup_logging()
        self.setup_wmi()
        self.setup_progress()
        self.toast = ToastNotifier()
        self.results = {}  # Armazena resultados para recomendações contextualizadas
        self.manage_scheduled_task()

    def init_system(self):
        """Inicialização do sistema com configurações aprimoradas."""
        self.base_dir = Path("C:/WindowsMaintenanceLogs")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.base_dir / f"system_check_{self.timestamp}.log"
        self.thresholds = {
            'cpu_warning': 70,
            'cpu_high': 80,
            'cpu_critical': 90,
            'memory_warning': 70,
            'memory_high': 80,
            'memory_critical': 90,
            'disk_warning': 75,
            'disk_high': 85,
            'disk_critical': 95,
            'temp_warning': 70,
            'temp_high': 80,
            'temp_critical': 90,
            'services_critical': [
                'wuauserv',  # Windows Update
                'WinDefend',  # Windows Defender
                'sppsvc',  # Software Protection
                'Dhcp',  # DHCP Client
                'Dnscache',  # DNS Client
                'wscsvc',  # Security Center
                'WSearch',  # Windows Search
                'EventLog',  # Event Log
                'MpsSvc'  # Windows Firewall
            ]
        }

    def setup_logging(self):
        """Configuração avançada do sistema de logging."""
        self.logger = logging.getLogger('SystemAnalyzer')
        self.logger.setLevel(logging.INFO)

        # Handler para arquivo
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Handler para console com cores
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            f'{Fore.CYAN}%(asctime)s{Style.RESET_ALL} - '
            f'%(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def setup_progress(self):
        """Configuração da barra de progresso."""
        self.total_steps = 30  # Atualizado para refletir todas as verificações
        self.current_step = 0

    def setup_wmi(self):
        """Configuração WMI com tratamento de erros."""
        if platform.system() != "Windows":
            self.logger.error("Este script só pode ser executado no Windows.")
            print(f"{Fore.RED}Este script só pode ser executado no Windows.{Style.RESET_ALL}")
            sys.exit(1)
        try:
            self.wmi = wmi.WMI()
            self.logger.info("WMI inicializado com sucesso.")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar WMI: {e}")
            self.wmi = None

    def update_progress(self, message: str, status: str = 'info'):
        """Barra de progresso com feedback visual aprimorado."""
        if self.current_step < self.total_steps:
            self.current_step += 1
        percentage = (self.current_step / self.total_steps) * 100
        bar_width = 50
        filled = int(bar_width * percentage / 100)
        bar = '█' * filled + '░' * (bar_width - filled)
        color_map = {
            'info': Fore.CYAN,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'critical': Fore.RED + Style.BRIGHT
        }
        color = color_map.get(status, Fore.CYAN)
        progress = f'\r{color}[{bar}] {percentage:.1f}% - {message}{Style.RESET_ALL}'
        print(progress, end='', flush=True)
        if self.current_step == self.total_steps:
            print(f"\n{Fore.GREEN}Verificação concluída!{Style.RESET_ALL}")
        log_levels = {
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        self.logger.log(log_levels.get(status, logging.INFO), message)

    def run_command(self, command: str, timeout: int = 30) -> Tuple[str, bool]:
        """Executa comando com tratamento de erros aprimorado."""
        try:
            # Divide o comando em lista para evitar shell=True
            args = command.split()
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            output = result.stdout if result.returncode == 0 else result.stderr
            if result.returncode != 0:
                self.logger.warning(f"Comando falhou: {' '.join(args)}")
                self.logger.warning(f"Erro: {output.strip()}")
            return output.strip(), result.returncode == 0
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout ao executar: {' '.join(command.split())}")
            return f"Comando excedeu limite de {timeout}s", False
        except Exception as e:
            self.logger.error(f"Erro ao executar {' '.join(command.split())}: {str(e)}")
            return f"Erro: {str(e)}", False

    def format_size(self, size_bytes: float) -> str:
        """Formata tamanhos de arquivo de forma amigável."""
        if size_bytes < 0:
            return "0 B"
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        size = float(size_bytes)
        unit_index = 0
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        if units[unit_index] in ['B', 'KB']:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.2f} {units[unit_index]}"

    def check_system_info(self) -> Dict[str, Any]:
        """Verificação detalhada do sistema."""
        self.update_progress("Coletando informações do sistema", "info")
        info = {
            "Sistema": f"{platform.system()} {platform.release()}",
            "Versão": platform.version(),
            "Arquitetura": platform.machine(),
            "Processador": platform.processor(),
            "Nome do Computador": platform.node(),
            "Memória Total": self.format_size(psutil.virtual_memory().total),
            "Usuário": getpass.getuser(),
            "Boot Time": datetime.fromtimestamp(psutil.boot_time()).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }
        # Informações de rede
        try:
            network_info = {}
            for iface, addrs in psutil.net_if_addrs().items():
                iface_info = []
                for addr in addrs:
                    if addr.family == socket.AF_INET:  # IPv4
                        iface_info.append(f"IPv4: {addr.address}")
                    elif addr.family == socket.AF_INET6:  # IPv6
                        iface_info.append(f"IPv6: {addr.address}")
                    elif addr.family == psutil.AF_LINK:  # MAC address
                        iface_info.append(f"MAC: {addr.address}")
                network_info[iface] = iface_info
            info["Rede"] = network_info
        except Exception as e:
            self.logger.error(f"Erro ao coletar informações de rede: {e}")

        # Registro no log
        for key, value in info.items():
            if isinstance(value, dict):
                self.logger.info(f"{key}:")
                for sub_key, sub_value in value.items():
                    self.logger.info(f"  {sub_key}: {sub_value}")
            else:
                self.logger.info(f"{key}: {value}")

        self.results['system_info'] = info
        return info

    def check_disk_health(self) -> Dict[str, Any]:
        """Verificação avançada de saúde dos discos."""
        self.update_progress("Analisando saúde dos discos", "info")
        disk_info = {}

        if not self.wmi:
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
            smart_output, success = self.run_command('wmic diskdrive get status')
            if success:
                status = "OK" if "OK" in smart_output else "Atenção"
                disk_info[disk.DeviceID]["SMART"] = status
                if status != "OK":
                    self.logger.warning(f"Disco {disk.DeviceID} com possível problema!")

        # Verificação lógica
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.device] = {
                    "Ponto de Montagem": partition.mountpoint,
                    "Sistema de Arquivos": partition.fstype,
                    "Total": self.format_size(usage.total),
                    "Usado": self.format_size(usage.used),
                    "Livre": self.format_size(usage.free),
                    "Porcentagem Uso": f"{usage.percent}%"
                }

                # Avaliação do uso
                if usage.percent >= self.thresholds['disk_critical']:
                    self.logger.critical(
                        f"Espaço crítico em {partition.mountpoint}: {usage.percent}%"
                    )
                elif usage.percent >= self.thresholds['disk_high']:
                    self.logger.warning(
                        f"Espaço baixo em {partition.mountpoint}: {usage.percent}%"
                    )

            except Exception as e:
                self.logger.error(f"Erro ao verificar partição {partition.mountpoint}: {e}")

        self.results['disk_health'] = disk_info
        return disk_info

    def check_performance(self) -> Dict[str, Any]:
        """Monitoramento avançado de desempenho."""
        self.update_progress("Analisando desempenho do sistema", "info")
        perf_info = {}

        # CPU
        cpu_times = psutil.cpu_times()
        cpu_freq = psutil.cpu_freq()
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)

        cpu_info = {
            "Uso por Núcleo": [f"{p}%" for p in cpu_percent],
            "Uso Total": f"{sum(cpu_percent) / len(cpu_percent):.1f}%",
            "Núcleos Físicos": psutil.cpu_count(logical=False),
            "Núcleos Lógicos": psutil.cpu_count(),
            "Frequência Atual": f"{cpu_freq.current:.2f}MHz" if cpu_freq else "N/A",
            "Frequência Mínima": f"{cpu_freq.min:.2f}MHz" if cpu_freq else "N/A",
            "Frequência Máxima": f"{cpu_freq.max:.2f}MHz" if cpu_freq else "N/A",
            "Tempo Sistema": f"{cpu_times.system / 3600:.2f}h",
            "Tempo Usuário": f"{cpu_times.user / 3600:.2f}h",
            "Tempo Ocioso": f"{cpu_times.idle / 3600:.2f}h"
        }

        # Memória
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        memory_info = {
            "RAM Total": self.format_size(mem.total),
            "RAM Disponível": self.format_size(mem.available),
            "RAM Usada": self.format_size(mem.used),
            "RAM Porcentagem": f"{mem.percent}%",
            "Swap Total": self.format_size(swap.total),
            "Swap Usado": self.format_size(swap.used),
            "Swap Porcentagem": f"{swap.percent}%"
        }

        # Processos
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] > 0 or pinfo['memory_percent'] > 0:
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cpu': pinfo['cpu_percent'],
                        'memory': pinfo['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        top_processes = sorted(
            processes,
            key=lambda x: (x['cpu'], x['memory']),
            reverse=True
        )[:5]

        perf_info = {
            'cpu': cpu_info,
            'memory': memory_info,
            'top_processes': top_processes
        }

        # Avaliação e logs
        cpu_total = sum(cpu_percent) / len(cpu_percent)
        if cpu_total >= self.thresholds['cpu_critical']:
            self.logger.critical(f"Uso crítico de CPU: {cpu_total:.1f}%")
        elif cpu_total >= self.thresholds['cpu_high']:
            self.logger.warning(f"Uso elevado de CPU: {cpu_total:.1f}%")

        if mem.percent >= self.thresholds['memory_critical']:
            self.logger.critical(f"Uso crítico de memória: {mem.percent}%")
        elif mem.percent >= self.thresholds['memory_high']:
            self.logger.warning(f"Uso elevado de memória: {mem.percent}%")

        self.results['performance'] = perf_info
        return perf_info

    def check_services(self) -> Dict[str, Any]:
        """Verificação detalhada de serviços."""
        self.update_progress("Verificando serviços do sistema", "info")
        services_info = {
            'problema': [],
            'ok': []
        }

        critical_services = self.thresholds['services_critical']

        if not self.wmi:
            self.logger.error("WMI não está disponível. Pulando verificação de serviços.")
            return services_info

        for service in self.wmi.Win32_Service():
            service_info = {
                'nome': service.DisplayName,
                'status': service.State,
                'inicio': service.StartMode,
                'descricao': service.Description
            }

            if (service.Name in critical_services and
                    (service.State != 'Running' or service.StartMode != 'Auto')):
                services_info['problema'].append(service_info)
                self.logger.warning(
                    f"Serviço crítico com problema: {service.DisplayName} - Estado: {service.State}, Início: {service.StartMode}"
                )
            else:
                services_info['ok'].append(service_info)

        self.results['services'] = services_info
        return services_info

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Gera recomendações contextualizadas baseadas nas análises."""
        self.update_progress("Gerando recomendações", "info")
        recommendations = []

        # Análise de CPU
        if 'performance' in self.results:
            cpu_usage_str = self.results['performance']['cpu']['Uso Total']
            cpu_usage = float(cpu_usage_str.rstrip('%'))
            if cpu_usage >= self.thresholds['cpu_critical']:
                recommendations.append({
                    'categoria': 'CPU',
                    'severidade': 'Crítica',
                    'mensagem': f'Uso crítico de CPU: {cpu_usage}%',
                    'impacto': 'Sistema pode estar extremamente lento ou instável.',
                    'acoes': [
                        'Verifique processos consumindo muito processamento.',
                        'Encerre aplicações não essenciais.',
                        'Verifique por malware.',
                        'Considere atualizar o hardware se o problema persistir.'
                    ],
                    'explicacao': 'O uso crítico da CPU pode levar à instabilidade do sistema e degradação do desempenho geral.'
                })
            elif cpu_usage >= self.thresholds['cpu_high']:
                recommendations.append({
                    'categoria': 'CPU',
                    'severidade': 'Alta',
                    'mensagem': f'Uso elevado de CPU: {cpu_usage}%',
                    'impacto': 'Sistema pode estar mais lento que o normal.',
                    'acoes': [
                        'Monitore os processos mais pesados.',
                        'Feche programas não utilizados.',
                        'Verifique programas em segundo plano.'
                    ],
                    'explicacao': 'Um alto uso da CPU pode indicar que muitos processos estão consumindo recursos, o que pode afetar o desempenho do sistema.'
                })

        # Análise de Memória
        if 'performance' in self.results:
            mem_info = self.results['performance']['memory']
            mem_usage_str = mem_info['RAM Porcentagem']
            mem_usage = float(mem_usage_str.rstrip('%'))
            if mem_usage >= self.thresholds['memory_critical']:
                recommendations.append({
                    'categoria': 'Memória',
                    'severidade': 'Crítica',
                    'mensagem': f'Uso crítico de memória: {mem_usage}%',
                    'impacto': 'Sistema pode travar ou estar extremamente lento.',
                    'acoes': [
                        'Feche programas que consomem muita memória.',
                        'Reinicie o computador.',
                        'Considere aumentar a memória RAM.',
                        'Verifique por memory leaks.'
                    ],
                    'explicacao': 'Um uso crítico da memória pode causar travamentos frequentes e lentidão significativa no sistema.'
                })
            elif mem_usage >= self.thresholds['memory_high']:
                recommendations.append({
                    'categoria': 'Memória',
                    'severidade': 'Alta',
                    'mensagem': f'Uso elevado de memória: {mem_usage}%',
                    'impacto': 'Sistema pode ficar lento.',
                    'acoes': [
                        'Feche programas não utilizados.',
                        'Evite manter muitas abas do navegador abertas.',
                        'Considere aumentar a memória RAM.'
                    ],
                    'explicacao': 'Um uso elevado da memória pode reduzir a quantidade de recursos disponíveis para processos essenciais, impactando o desempenho.'
                })

        # Análise de Disco
        if 'disk_health' in self.results:
            for device, info in self.results['disk_health'].items():
                if 'Porcentagem Uso' in info:
                    usage_str = info['Porcentagem Uso']
                    usage = float(usage_str.rstrip('%'))
                    if usage >= self.thresholds['disk_critical']:
                        recommendations.append({
                            'categoria': 'Disco',
                            'severidade': 'Crítica',
                            'mensagem': f'Espaço crítico em {info["Ponto de Montagem"]}: {usage}%',
                            'impacto': 'Sistema pode parar de funcionar por falta de espaço.',
                            'acoes': [
                                'Execute limpeza de disco imediatamente.',
                                'Remova programas não utilizados.',
                                'Mova arquivos grandes para armazenamento externo.',
                                'Considere expandir o armazenamento.'
                            ],
                            'explicacao': 'Espaço crítico no disco pode impedir a instalação de atualizações e o funcionamento adequado do sistema.'
                        })
                    elif usage >= self.thresholds['disk_high']:
                        recommendations.append({
                            'categoria': 'Disco',
                            'severidade': 'Alta',
                            'mensagem': f'Pouco espaço em {info["Ponto de Montagem"]}: {usage}%',
                            'impacto': 'Pode impedir atualizações e gravação de arquivos.',
                            'acoes': [
                                'Execute limpeza de disco.',
                                'Remova arquivos temporários.',
                                'Use programas de limpeza de disco.'
                            ],
                            'explicacao': 'Pouco espaço no disco pode causar problemas na gravação de arquivos e na instalação de atualizações.'
                        })

        # Análise de Serviços
        if 'services' in self.results:
            problematic_services = self.results['services']['problema']
            if problematic_services:
                recommendations.append({
                    'categoria': 'Serviços',
                    'severidade': 'Alta',
                    'mensagem': f'Serviços críticos com problema ({len(problematic_services)} serviços)',
                    'impacto': 'Pode afetar a segurança e funcionamento do sistema.',
                    'acoes': [
                        'Verifique e reinicie os serviços problemáticos.',
                        'Execute o diagnóstico de serviços do Windows.',
                        'Verifique por atualizações pendentes.',
                        'Considere restaurar os serviços para configuração padrão.'
                    ],
                    'explicacao': 'Serviços críticos com problemas podem comprometer a segurança e o funcionamento geral do sistema.'
                })

        # Análise de Processos
        if 'performance' in self.results:
            top_processes = self.results['performance']['top_processes']
            high_usage_processes = [p for p in top_processes if p['cpu'] > 20]
            if high_usage_processes:
                process_names = ', '.join(p['name'] for p in high_usage_processes)
                recommendations.append({
                    'categoria': 'Processos',
                    'severidade': 'Média',
                    'mensagem': 'Processos consumindo recursos excessivos',
                    'impacto': 'Pode causar lentidão e aquecimento do sistema.',
                    'acoes': [
                        f"Verifique os processos: {process_names}.",
                        'Atualize os programas problemáticos.',
                        'Verifique por malware.',
                        'Considere alternativas mais leves para esses programas.'
                    ],
                    'explicacao': 'Processos que consomem muitos recursos podem reduzir o desempenho do sistema e aumentar a temperatura do hardware.'
                })

        # Análise de Temperatura (Placeholder: Implementar coleta de temperatura se possível)
        # Exemplo:
        # if 'temperature' in self.results:
        #     temp_info = self.results['temperature']
        #     if any(t > self.thresholds['temp_high'] for t in temp_info.values()):
        #         recommendations.append({
        #             'categoria': 'Temperatura',
        #             'severidade': 'Alta',
        #             'mensagem': 'Temperatura elevada detectada',
        #             'impacto': 'Pode causar instabilidade e danos ao hardware',
        #             'acoes': [
        #                 'Verifique a ventilação do computador.',
        #                 'Limpe o sistema de refrigeração.',
        #                 'Verifique a pasta térmica do processador.',
        #                 'Evite bloquear as saídas de ar.'
        #             ],
        #             'explicacao': 'Temperaturas elevadas podem levar à degradação do hardware e instabilidade do sistema.'
        #         })

        self.results['recommendations'] = recommendations
        return recommendations

    def generate_report(self) -> str:
        """Gera relatório completo em formato amigável."""
        self.update_progress("Gerando relatório final", "info")
        report = [
            f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}",
            f"{Fore.CYAN}Relatório de Análise do Sistema{Style.RESET_ALL}",
            f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}\n",
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        ]

        # Informações do Sistema
        if 'system_info' in self.results:
            report.append(f"{Fore.GREEN}Informações do Sistema:{Style.RESET_ALL}")
            for key, value in self.results['system_info'].items():
                if isinstance(value, dict):
                    report.append(f"\n{key}:")
                    for sub_key, sub_value in value.items():
                        report.append(f"  {sub_key}: {sub_value}")
                else:
                    report.append(f"{key}: {value}")
            report.append("")

        # Performance
        if 'performance' in self.results:
            report.append(f"{Fore.GREEN}Performance:{Style.RESET_ALL}")

            report.append("\nCPU:")
            for key, value in self.results['performance']['cpu'].items():
                report.append(f"  {key}: {value}")

            report.append("\nMemória:")
            for key, value in self.results['performance']['memory'].items():
                report.append(f"  {key}: {value}")

            if 'top_processes' in self.results['performance']:
                report.append("\nProcessos mais ativos:")
                for proc in self.results['performance']['top_processes']:
                    report.append(
                        f"  {proc['name']}: CPU {proc['cpu']}%, "
                        f"Memória {proc['memory']}%"
                    )
            report.append("")

        # Saúde do Disco
        if 'disk_health' in self.results:
            report.append(f"{Fore.GREEN}Saúde dos Discos:{Style.RESET_ALL}")
            for device, info in self.results['disk_health'].items():
                report.append(f"\nDisco {device}:")
                for key, value in info.items():
                    report.append(f"  {key}: {value}")
            report.append("")

        # Serviços
        if 'services' in self.results:
            services_info = self.results['services']
            report.append(f"{Fore.GREEN}Serviços do Sistema:{Style.RESET_ALL}")

            report.append("\nServiços com Problemas:")
            if services_info['problema']:
                for svc in services_info['problema']:
                    report.append(f"  - {svc['nome']} (Estado: {svc['status']}, Início: {svc['inicio']})")
            else:
                report.append("  Nenhum serviço crítico com problemas.")

            report.append("\nServiços OK:")
            if services_info['ok']:
                for svc in services_info['ok']:
                    report.append(f"  - {svc['nome']} (Estado: {svc['status']}, Início: {svc['inicio']})")
            else:
                report.append("  Nenhum serviço OK encontrado.")
            report.append("")

        # Recomendações
        recommendations = self.results.get('recommendations', [])
        if recommendations:
            report.append(f"{Fore.YELLOW}Recomendações:{Style.RESET_ALL}")
            for rec in recommendations:
                # Cabeçalho da recomendação
                severity_color = {
                    'Crítica': Fore.RED + Style.BRIGHT,
                    'Alta': Fore.YELLOW,
                    'Média': Fore.BLUE,
                    'Baixa': Fore.GREEN
                }.get(rec['severidade'], Fore.WHITE)
                report.append(f"\n{severity_color}[{rec['categoria']} - {rec['severidade']}]{Style.RESET_ALL}")

                # Problema e Impacto
                report.append(f"{Fore.CYAN}Problema:{Style.RESET_ALL} {rec['mensagem']}")
                report.append(f"{Fore.CYAN}Impacto:{Style.RESET_ALL} {rec['impacto']}")

                # Ações
                report.append(f"{Fore.CYAN}Ações recomendadas:{Style.RESET_ALL}")
                for i, acao in enumerate(rec['acoes'], 1):
                    report.append(f"  {i}. {acao}")

                # Explicação
                report.append(f"{Fore.CYAN}Explicação:{Style.RESET_ALL} {rec['explicacao']}")
            report.append("")

        return "\n".join(report)

    def save_report(self, report: str) -> bool:
        """Salva o relatório em arquivo."""
        report_file = self.base_dir / f"relatorio_{self.timestamp}.txt"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            self.logger.info(f"Relatório salvo em: {report_file}")
            print(f"\n{Fore.GREEN}Relatório salvo em: {report_file}{Style.RESET_ALL}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar relatório: {e}")
            print(f"\n{Fore.RED}Erro ao salvar relatório: {e}{Style.RESET_ALL}")
            return False

    def save_json_report(self, recommendations: List[Dict[str, Any]]) -> str:
        """Salva relatório em formato JSON para notificações."""
        json_file = self.base_dir / f"report_{self.timestamp}.json"

        summary = []
        if 'performance' in self.results:
            cpu_usage = self.results['performance']['cpu']['Uso Total']
            mem_usage = self.results['performance']['memory']['RAM Porcentagem']
            summary.append(f"CPU: {cpu_usage}")
            summary.append(f"Memória: {mem_usage}")

        if 'disk_health' in self.results:
            critical_disks = []
            for device, info in self.results['disk_health'].items():
                if 'Porcentagem Uso' in info:
                    usage = float(info['Porcentagem Uso'].rstrip('%'))
                    if usage >= self.thresholds['disk_high']:
                        critical_disks.append(f"{info['Ponto de Montagem']}: {usage}%")
            if critical_disks:
                summary.append(f"Discos críticos: {', '.join(critical_disks)}")

        if 'services' in self.results:
            problematic_services = len(self.results['services']['problema'])
            if problematic_services > 0:
                summary.append(f"Serviços com problemas: {problematic_services}")

        report_data = {
            'timestamp': self.timestamp,
            'summary': ' | '.join(summary),
            'recommendations': recommendations,
            'system_info': self.results.get('system_info', {}),
            'performance': self.results.get('performance', {}),
            'disk_health': self.results.get('disk_health', {}),
            'services': self.results.get('services', {})
        }

        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Relatório JSON salvo em: {json_file}")
            return str(json_file)
        except Exception as e:
            self.logger.error(f"Erro ao salvar relatório JSON: {e}")
            return ""

    def notify_user(self, recommendations: List[Dict[str, Any]]):
        """Notifica o usuário sobre os resultados da análise."""
        try:
            json_file = self.save_json_report(recommendations)
            if json_file:
                summary = ' | '.join([rec['mensagem'] for rec in recommendations])
                self.toast.show_toast(
                    "Análise do Sistema Concluída",
                    summary,
                    duration=10,
                    threaded=True
                )
        except Exception as e:
            self.logger.error(f"Erro ao notificar usuário: {e}")

    def manage_scheduled_task(self):
        """Verifica e gerencia a tarefa agendada."""
        self.logger.info("Gerenciando tarefa agendada...")
        task_exists = False
        task_action = ""

        # Verifica se a tarefa já existe
        query_command = f'schtasks /Query /TN "{self.TASK_NAME}" /FO LIST /V'
        query_output, success = self.run_command(query_command)
        if success:
            task_exists = True
            # Extrai a ação da tarefa
            for line in query_output.splitlines():
                if line.strip().startswith("Task To Run:"):
                    task_action = line.split(":", 1)[1].strip()
                    break

        if task_exists:
            self.logger.info(f"Tarefa agendada '{self.TASK_NAME}' encontrada.")
            # Verifica se a tarefa está executando a versão atual do script
            expected_action = f'"{self.PYTHON_PATH}" "{self.SCRIPT_PATH}" --version {__version__}'
            if task_action == expected_action:
                self.logger.info("A tarefa agendada está configurada corretamente.")
                print(
                    f"{Fore.GREEN}A tarefa agendada '{self.TASK_NAME}' já está configurada corretamente.{Style.RESET_ALL}")
                return
            else:
                self.logger.warning("A tarefa agendada está executando uma versão anterior do script.")
                # Remove a tarefa existente
                delete_command = f'schtasks /Delete /TN "{self.TASK_NAME}" /F'
                delete_output, delete_success = self.run_command(delete_command)
                if delete_success:
                    self.logger.info(f"Tarefa agendada '{self.TASK_NAME}' removida com sucesso.")
                else:
                    self.logger.error(f"Falha ao remover a tarefa agendada '{self.TASK_NAME}'.")
                    print(
                        f"{Fore.RED}Falha ao remover a tarefa agendada '{self.TASK_NAME}'. Verifique o log para mais detalhes.{Style.RESET_ALL}")
                    return

        # Cria a tarefa agendada
        self.logger.info(f"Criação da tarefa agendada '{self.TASK_NAME}'...")
        create_command = (
            f'schtasks /Create /TN "{self.TASK_NAME}" '
            f'/TR "{self.PYTHON_PATH}" "{self.SCRIPT_PATH}" --version {__version__}" '
            f'/SC {self.SCHEDULE} /D {self.DAY} /ST {self.TIME} '
            f'/RL HIGHEST /F'
        )
        create_output, create_success = self.run_command(create_command)
        if create_success:
            self.logger.info(f"Tarefa agendada '{self.TASK_NAME}' criada com sucesso.")
            print(f"{Fore.GREEN}Tarefa agendada '{self.TASK_NAME}' criada com sucesso.{Style.RESET_ALL}")
            # Notifica o usuário
            self.toast.show_toast(
                "Tarefa Agendada Criada",
                f"A tarefa '{self.TASK_NAME}' foi criada e será executada semanalmente.",
                duration=10,
                threaded=True
            )
        else:
            self.logger.error(f"Falha ao criar a tarefa agendada '{self.TASK_NAME}'.")
            print(
                f"{Fore.RED}Falha ao criar a tarefa agendada '{self.TASK_NAME}'. Verifique o log para mais detalhes.{Style.RESET_ALL}")
            # Notifica o usuário sobre o erro
            self.toast.show_toast(
                "Erro na Criação da Tarefa Agendada",
                f"Falha ao criar a tarefa '{self.TASK_NAME}'.",
                duration=10,
                threaded=True
            )

    def run_analysis(self):
        """Executa análise completa do sistema."""
        print(f"\n{Fore.CYAN}{'=' * 50}")
        print(f"{Fore.CYAN}Iniciando Análise Completa do Sistema{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}\n")

        try:
            # Executa verificações
            system_info = self.check_system_info()
            self.results['system_info'] = system_info

            disk_health = self.check_disk_health()
            self.results['disk_health'] = disk_health

            performance = self.check_performance()
            self.results['performance'] = performance

            services = self.check_services()
            self.results['services'] = services

            # Gera recomendações e relatórios
            recommendations = self.generate_recommendations()
            report = self.generate_report()

            # Salva relatório texto
            if self.save_report(report):
                print(report)  # Exibe relatório no console

            # Notifica usuário
            if recommendations:
                self.notify_user(recommendations)

            print(f"\n{Fore.GREEN}Análise Concluída com Sucesso!{Style.RESET_ALL}")
            self.logger.info("Análise concluída com sucesso.")

        except Exception as e:
            error_msg = f"Erro durante a análise: {str(e)}"
            print(f"\n{Fore.RED}ERRO: {error_msg}{Style.RESET_ALL}")
            self.logger.error(error_msg)
            # Tenta notificar mesmo em caso de erro
            try:
                self.toast.show_toast(
                    "Erro na Análise do Sistema",
                    error_msg,
                    duration=10,
                    threaded=True
                )
            except:
                pass
            raise


def main():
    """
    Executes the main routine to initiate system analysis.

    :return: None
    """
    try:
        analyzer = SystemAnalyzer()
        analyzer.run_analysis()

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Análise interrompida pelo usuário.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Erro crítico: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
