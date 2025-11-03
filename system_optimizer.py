import subprocess
import sys
import os
import logging
import json
import time
import re
import shutil
import winreg
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from logging.handlers import RotatingFileHandler
import psutil
import threading
import ctypes

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
    from colorama import init, Fore, Style
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'colorama'])
    from colorama import init, Fore, Style

# Inicializa o colorama
init(autoreset=True)

class SystemOptimizer:
    VERSION = "3.0.0"
    LOG_PATH = r"C:\WindowsMaintenanceLogs\system_optimizer.log"
    REPORT_PATH = r"C:\WindowsMaintenanceLogs\relatorio_{date}.txt"
    JSON_REPORT_PATH = r"C:\WindowsMaintenanceLogs\report_{date}.json"
    THRESHOLDS = {
        'disk_critical': 90,
        'disk_high': 80,
        'memory_high': 85,
        'cpu_high': 80
    }
    STARTUP_PROGRAMS = []

    # Caminhos de navegadores para limpeza
    BROWSER_CACHE_PATHS = {
        'Chrome': [
            r'{LOCALAPPDATA}\Google\Chrome\User Data\Default\Cache',
            r'{LOCALAPPDATA}\Google\Chrome\User Data\Default\Code Cache',
            r'{LOCALAPPDATA}\Google\Chrome\User Data\Default\GPUCache',
        ],
        'Edge': [
            r'{LOCALAPPDATA}\Microsoft\Edge\User Data\Default\Cache',
            r'{LOCALAPPDATA}\Microsoft\Edge\User Data\Default\Code Cache',
            r'{LOCALAPPDATA}\Microsoft\Edge\User Data\Default\GPUCache',
        ],
        'Firefox': [
            r'{APPDATA}\Mozilla\Firefox\Profiles',
        ],
        'Brave': [
            r'{LOCALAPPDATA}\BraveSoftware\Brave-Browser\User Data\Default\Cache',
            r'{LOCALAPPDATA}\BraveSoftware\Brave-Browser\User Data\Default\Code Cache',
        ]
    }

    def __init__(self):
        # Verifica privilégios de administrador
        if not self.is_admin():
            print(f"{Fore.RED}ERRO: Este script precisa ser executado como Administrador!")
            self.logger.error("Script executado sem privilégios de administrador")
            sys.exit(1)

        # Configura o logger com rotação
        os.makedirs(os.path.dirname(self.LOG_PATH), exist_ok=True)

        # Remove handlers antigos
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Configura novo handler com rotação (máx 10MB, 5 backups)
        handler = RotatingFileHandler(
            self.LOG_PATH,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))

        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        self.logger = logger

        self.logger.info(f"=== Iniciando System Optimizer v{self.VERSION} ===")

        try:
            self.wmi = wmi.WMI()
            self.logger.info("WMI inicializado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar WMI: {e}")
            self.wmi = None

        self.results = {}
        self.total_steps = 17  # Total de etapas no processo de otimização
        self.current_step = 0
        self.start_time = time.time()
        self.errors = []
        self.warnings = []

    def is_admin(self) -> bool:
        """Verifica se o script está sendo executado como administrador."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def update_progress(self, message: str):
        """Atualiza o progresso e informa o usuário."""
        self.current_step += 1
        elapsed_time = time.time() - self.start_time
        estimated_total_time = (elapsed_time / self.current_step) * self.total_steps
        remaining_time = max(0, estimated_total_time - elapsed_time)
        print(f"\n{Fore.CYAN}{Style.BRIGHT}[{self.current_step}/{self.total_steps}] {message}")
        print(f"{Fore.YELLOW}Tempo estimado restante: {remaining_time/60:.2f} minutos")
        self.logger.info(message)

    def log_error(self, message: str, exception: Exception = None):
        """Registra um erro no log e na lista de erros."""
        error_msg = f"{message}: {str(exception)}" if exception else message
        self.logger.error(error_msg)
        self.errors.append(error_msg)
        print(f"{Fore.RED}ERRO: {error_msg}")

    def log_warning(self, message: str):
        """Registra um aviso no log e na lista de avisos."""
        self.logger.warning(message)
        self.warnings.append(message)
        print(f"{Fore.YELLOW}AVISO: {message}")

    def get_user_confirmation(self, message: str, timeout: int = 30) -> bool:
        """
        Solicita confirmação do usuário com timeout.
        Retorna True se usuário confirmar (S/s), False se negar (N/n) ou timeout.
        """
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}{message}")
        print(f"{Fore.CYAN}Digite 'S' para SIM ou 'N' para NÃO (Timeout em {timeout}s):")

        user_input = [None]

        def get_input():
            try:
                user_input[0] = input().strip().upper()
            except:
                pass

        input_thread = threading.Thread(target=get_input)
        input_thread.daemon = True
        input_thread.start()
        input_thread.join(timeout)

        if user_input[0] in ['S', 'SIM', 'YES', 'Y']:
            self.logger.info(f"Usuário confirmou: {message}")
            return True
        elif user_input[0] in ['N', 'NAO', 'NÃO', 'NO']:
            self.logger.info(f"Usuário negou: {message}")
            return False
        else:
            self.logger.warning(f"Timeout na confirmação: {message}")
            print(f"\n{Fore.RED}Timeout! Operação cancelada.")
            return False

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
            os.path.join(os.getenv('SYSTEMROOT'), 'Prefetch'),
            os.path.join(os.getenv('SYSTEMROOT'), 'SoftwareDistribution', 'Download'),
            os.path.join(os.getenv('LOCALAPPDATA'), 'Temp'),
        ]

        total_files_deleted = 0
        total_size_freed = 0

        for temp_dir in temp_dirs:
            if not os.path.exists(temp_dir):
                continue

            try:
                for root, dirs, files in os.walk(temp_dir, topdown=False):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            total_files_deleted += 1
                            total_size_freed += file_size
                        except PermissionError:
                            pass
                        except Exception as e:
                            self.logger.debug(f"Não foi possível remover {file_path}: {e}")

                    # Remove diretórios vazios
                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        try:
                            if not os.listdir(dir_path):
                                os.rmdir(dir_path)
                        except:
                            pass

                self.logger.info(f"Arquivos temporários limpos em: {temp_dir}")
            except Exception as e:
                self.log_error(f"Erro ao limpar {temp_dir}", e)

        print(f"{Fore.GREEN}Total de arquivos temporários deletados: {total_files_deleted}")
        print(f"{Fore.GREEN}Espaço liberado: {self.format_size(total_size_freed)}")
        self.results['temp_cleanup'] = {
            'files_deleted': total_files_deleted,
            'space_freed': self.format_size(total_size_freed)
        }

    def clean_browser_cache(self):
        """Limpa cache de navegadores populares."""
        self.update_progress("Limpando cache dos navegadores...")
        total_size_freed = 0
        browsers_cleaned = []

        for browser, paths in self.BROWSER_CACHE_PATHS.items():
            try:
                for path_template in paths:
                    # Expande variáveis de ambiente
                    path = path_template.format(
                        LOCALAPPDATA=os.getenv('LOCALAPPDATA'),
                        APPDATA=os.getenv('APPDATA')
                    )

                    if 'Profiles' in path and browser == 'Firefox':
                        # Firefox tem múltiplos perfis
                        if os.path.exists(path):
                            for profile in os.listdir(path):
                                profile_path = os.path.join(path, profile, 'cache2', 'entries')
                                if os.path.exists(profile_path):
                                    try:
                                        size = self.get_dir_size(profile_path)
                                        shutil.rmtree(profile_path, ignore_errors=True)
                                        total_size_freed += size
                                    except Exception as e:
                                        self.logger.debug(f"Erro ao limpar cache Firefox: {e}")
                    else:
                        if os.path.exists(path):
                            try:
                                size = self.get_dir_size(path)
                                shutil.rmtree(path, ignore_errors=True)
                                total_size_freed += size
                                self.logger.info(f"Cache limpo: {browser} - {path}")
                            except Exception as e:
                                self.logger.debug(f"Erro ao limpar {browser}: {e}")

                browsers_cleaned.append(browser)
            except Exception as e:
                self.log_warning(f"Erro ao limpar cache do {browser}: {e}")

        print(f"{Fore.GREEN}Navegadores limpos: {', '.join(browsers_cleaned)}")
        print(f"{Fore.GREEN}Espaço liberado: {self.format_size(total_size_freed)}")
        self.results['browser_cleanup'] = {
            'browsers': browsers_cleaned,
            'space_freed': self.format_size(total_size_freed)
        }

    def clean_windows_cache(self):
        """Limpa cache do Windows e arquivos desnecessários."""
        self.update_progress("Limpando cache do Windows...")

        cache_dirs = [
            os.path.join(os.getenv('SYSTEMROOT'), 'Logs'),
            os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Windows', 'INetCache'),
            os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Windows', 'WebCache'),
            os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Windows', 'Explorer', 'thumbcache_*.db'),
        ]

        total_size_freed = 0

        # Limpa cache DNS
        try:
            subprocess.run(['ipconfig', '/flushdns'], capture_output=True, shell=True)
            self.logger.info("Cache DNS limpo com sucesso")
        except Exception as e:
            self.log_warning(f"Erro ao limpar cache DNS: {e}")

        # Limpa Windows Update cache
        try:
            subprocess.run(['net', 'stop', 'wuauserv'], capture_output=True, shell=True)
            wusvc_path = os.path.join(os.getenv('SYSTEMROOT'), 'SoftwareDistribution')
            if os.path.exists(wusvc_path):
                size = self.get_dir_size(wusvc_path)
                shutil.rmtree(wusvc_path, ignore_errors=True)
                total_size_freed += size
                self.logger.info("Cache do Windows Update limpo")
            subprocess.run(['net', 'start', 'wuauserv'], capture_output=True, shell=True)
        except Exception as e:
            self.log_warning(f"Erro ao limpar cache do Windows Update: {e}")

        # Limpa outros caches
        for cache_dir in cache_dirs:
            if '*' in cache_dir:
                # Padrão com wildcard
                base_dir = os.path.dirname(cache_dir)
                pattern = os.path.basename(cache_dir)
                if os.path.exists(base_dir):
                    for file in Path(base_dir).glob(pattern):
                        try:
                            file_size = file.stat().st_size
                            file.unlink()
                            total_size_freed += file_size
                        except:
                            pass
            elif os.path.exists(cache_dir):
                try:
                    size = self.get_dir_size(cache_dir)
                    shutil.rmtree(cache_dir, ignore_errors=True)
                    total_size_freed += size
                    self.logger.info(f"Cache limpo: {cache_dir}")
                except Exception as e:
                    self.logger.debug(f"Erro ao limpar {cache_dir}: {e}")

        print(f"{Fore.GREEN}Cache do Windows limpo. Espaço liberado: {self.format_size(total_size_freed)}")
        self.results['windows_cache_cleanup'] = {
            'space_freed': self.format_size(total_size_freed)
        }

    def get_dir_size(self, path: str) -> int:
        """Calcula o tamanho total de um diretório."""
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    total += self.get_dir_size(entry.path)
        except PermissionError:
            pass
        except Exception:
            pass
        return total

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
        """Executa comandos DISM para reparar a imagem do sistema (Windows 11 otimizado)."""
        self.update_progress("Executando reparo DISM...")
        try:
            # CheckHealth - Verifica se há corrupções
            print(f"{Fore.CYAN}Verificando integridade da imagem do sistema...")
            subprocess.run(['DISM', '/Online', '/Cleanup-Image', '/CheckHealth'],
                          capture_output=True, shell=True, check=True)

            # ScanHealth - Escaneia corrupções (mais profundo)
            print(f"{Fore.CYAN}Escaneando por corrupções...")
            subprocess.run(['DISM', '/Online', '/Cleanup-Image', '/ScanHealth'],
                          capture_output=True, shell=True, check=True)

            # RestoreHealth - Repara corrupções encontradas
            print(f"{Fore.CYAN}Reparando imagem do sistema...")
            subprocess.run(['DISM', '/Online', '/Cleanup-Image', '/RestoreHealth'],
                          capture_output=True, shell=True, check=True)

            # StartComponentCleanup - Limpa componentes supersedidos (Windows 11)
            print(f"{Fore.CYAN}Limpando componentes antigos...")
            subprocess.run(['DISM', '/Online', '/Cleanup-Image', '/StartComponentCleanup'],
                          capture_output=True, shell=True, check=True)

            # AnalyzeComponentStore - Analisa loja de componentes
            print(f"{Fore.CYAN}Analisando armazenamento de componentes...")
            subprocess.run(['DISM', '/Online', '/Cleanup-Image', '/AnalyzeComponentStore'],
                          capture_output=True, shell=True, check=True)

            self.logger.info("Comandos DISM concluídos com sucesso.")
            print(f"{Fore.GREEN}DISM completado com sucesso!")
        except subprocess.CalledProcessError as e:
            self.log_error("Erro ao executar DISM", e)

    def clean_registry(self):
        """Limpa entradas inválidas do registro do Windows."""
        self.update_progress("Limpando registro do Windows...")

        entries_cleaned = 0

        # Chaves comuns que podem ter entradas inválidas
        registry_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache"),
        ]

        try:
            for hive, path in registry_paths:
                try:
                    key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)

                            # Verifica se o valor aponta para um arquivo que não existe
                            if isinstance(value, str) and (':\\' in value or '\\\\' in value):
                                # Extrai caminho do arquivo
                                file_path = value.split('"')[1] if '"' in value else value.split()[0]

                                if not os.path.exists(file_path):
                                    try:
                                        winreg.DeleteValue(key, name)
                                        entries_cleaned += 1
                                        self.logger.info(f"Entrada de registro removida: {name} -> {file_path}")
                                    except:
                                        pass
                            i += 1
                        except OSError:
                            break

                    winreg.CloseKey(key)
                except FileNotFoundError:
                    pass
                except PermissionError:
                    self.log_warning(f"Permissão negada para acessar: {path}")
                except Exception as e:
                    self.logger.debug(f"Erro ao processar chave {path}: {e}")

        except Exception as e:
            self.log_error("Erro durante limpeza de registro", e)

        print(f"{Fore.GREEN}Entradas de registro limpas: {entries_cleaned}")
        self.results['registry_cleanup'] = {'entries_cleaned': entries_cleaned}

    def check_broken_shortcuts(self):
        """Verifica e remove atalhos quebrados."""
        self.update_progress("Verificando atalhos quebrados...")

        shortcuts_removed = 0

        # Locais comuns de atalhos
        shortcut_locations = [
            os.path.join(os.getenv('USERPROFILE'), 'Desktop'),
            os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
            os.path.join(os.getenv('PROGRAMDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
            os.path.join(os.getenv('USERPROFILE'), 'AppData', 'Roaming', 'Microsoft', 'Internet Explorer', 'Quick Launch'),
        ]

        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")

            for location in shortcut_locations:
                if not os.path.exists(location):
                    continue

                for root, dirs, files in os.walk(location):
                    for file in files:
                        if file.endswith('.lnk'):
                            shortcut_path = os.path.join(root, file)
                            try:
                                shortcut = shell.CreateShortCut(shortcut_path)
                                target = shortcut.Targetpath

                                # Verifica se o alvo existe
                                if target and not os.path.exists(target):
                                    os.remove(shortcut_path)
                                    shortcuts_removed += 1
                                    self.logger.info(f"Atalho quebrado removido: {shortcut_path} -> {target}")
                            except Exception as e:
                                self.logger.debug(f"Erro ao verificar atalho {shortcut_path}: {e}")

        except ImportError:
            self.log_warning("Módulo pywin32 não disponível. Instalando...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pywin32'])
                self.log_warning("pywin32 instalado. Execute o script novamente para verificar atalhos.")
            except Exception as e:
                self.log_error("Não foi possível instalar pywin32", e)
        except Exception as e:
            self.log_error("Erro ao verificar atalhos quebrados", e)

        print(f"{Fore.GREEN}Atalhos quebrados removidos: {shortcuts_removed}")
        self.results['broken_shortcuts'] = {'shortcuts_removed': shortcuts_removed}

    def check_old_installations(self):
        """Verifica instalações antigas e quebradas."""
        self.update_progress("Verificando instalações antigas...")

        old_installations = []

        try:
            # Verifica Windows.old (instalações antigas do Windows)
            windows_old = os.path.join(os.getenv('SYSTEMDRIVE'), '\\', 'Windows.old')
            if os.path.exists(windows_old):
                size = self.get_dir_size(windows_old)
                old_installations.append({
                    'path': windows_old,
                    'size': self.format_size(size),
                    'type': 'Windows Antigo'
                })
                self.log_warning(f"Instalação antiga encontrada: {windows_old} ({self.format_size(size)})")

            # Verifica programas não instalados corretamente via WMI
            if self.wmi:
                try:
                    for product in self.wmi.Win32_Product():
                        # Verifica se o caminho de instalação existe
                        if hasattr(product, 'InstallLocation') and product.InstallLocation:
                            if not os.path.exists(product.InstallLocation):
                                old_installations.append({
                                    'name': product.Name,
                                    'path': product.InstallLocation,
                                    'type': 'Instalação Quebrada'
                                })
                                self.log_warning(f"Instalação quebrada: {product.Name} em {product.InstallLocation}")
                except Exception as e:
                    self.logger.debug(f"Erro ao verificar produtos WMI: {e}")

            # Sugere usar Limpeza de Disco do Windows para Windows.old
            if any(inst['type'] == 'Windows Antigo' for inst in old_installations):
                print(f"{Fore.YELLOW}RECOMENDAÇÃO: Execute 'cleanmgr' e selecione 'Instalações Anteriores do Windows' para liberar espaço.")

        except Exception as e:
            self.log_error("Erro ao verificar instalações antigas", e)

        print(f"{Fore.GREEN}Instalações problemáticas encontradas: {len(old_installations)}")
        self.results['old_installations'] = old_installations

    def check_drivers(self):
        """Verifica o status dos drivers do sistema."""
        self.update_progress("Verificando drivers do sistema...")

        driver_issues = []

        try:
            if self.wmi:
                # Verifica drivers do sistema
                for driver in self.wmi.Win32_PnPSignedDriver():
                    # Verifica drivers com problemas
                    if hasattr(driver, 'Status') and driver.Status and driver.Status != 'OK':
                        driver_issues.append({
                            'name': driver.DeviceName if hasattr(driver, 'DeviceName') else 'Desconhecido',
                            'status': driver.Status,
                            'manufacturer': driver.Manufacturer if hasattr(driver, 'Manufacturer') else 'N/A'
                        })
                        self.log_warning(f"Driver com problema: {driver.DeviceName} - Status: {driver.Status}")

                # Verifica dispositivos com problemas
                for device in self.wmi.Win32_PnPEntity():
                    if hasattr(device, 'ConfigManagerErrorCode') and device.ConfigManagerErrorCode != 0:
                        error_code = device.ConfigManagerErrorCode
                        device_name = device.Name if hasattr(device, 'Name') else 'Desconhecido'

                        if error_code not in [0, 22]:  # 22 = dispositivo desabilitado (normal)
                            driver_issues.append({
                                'name': device_name,
                                'error_code': error_code,
                                'type': 'Dispositivo com erro'
                            })
                            self.log_warning(f"Dispositivo com erro: {device_name} - Código: {error_code}")

            # Executa verificação de drivers do Windows
            print(f"{Fore.CYAN}Executando verificação de drivers...")
            try:
                result = subprocess.run(
                    ['pnputil', '/enum-drivers'],
                    capture_output=True,
                    text=True,
                    shell=True
                )
                self.logger.info("Verificação de drivers concluída via pnputil")
            except Exception as e:
                self.logger.debug(f"Erro ao executar pnputil: {e}")

        except Exception as e:
            self.log_error("Erro ao verificar drivers", e)

        if driver_issues:
            print(f"{Fore.YELLOW}Problemas de driver encontrados: {len(driver_issues)}")
            print(f"{Fore.YELLOW}RECOMENDAÇÃO: Atualize os drivers usando o Windows Update ou o site do fabricante.")
        else:
            print(f"{Fore.GREEN}Nenhum problema de driver detectado!")

        self.results['driver_check'] = {
            'issues_found': len(driver_issues),
            'issues': driver_issues[:10]  # Limita a 10 para não sobrecarregar o relatório
        }

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
        """Executa otimizações gerais no sistema com confirmação para desfragmentação."""
        self.update_progress("Preparando otimizações do sistema...")

        try:
            # Detecta SSDs vs HDDs
            hdd_partitions = []
            ssd_partitions = []

            if self.wmi:
                try:
                    for disk in self.wmi.Win32_DiskDrive():
                        # Detecta SSDs (geralmente MediaType contém "SSD" ou não tem partes móveis)
                        media_type = disk.MediaType if hasattr(disk, 'MediaType') else ''
                        is_ssd = 'SSD' in str(media_type).upper() or disk.InterfaceType in ['NVME', 'NVMe']

                        for partition in psutil.disk_partitions():
                            if 'fixed' in partition.opts.lower():
                                if is_ssd:
                                    ssd_partitions.append(partition.device)
                                else:
                                    hdd_partitions.append(partition.device)
                except Exception as e:
                    self.logger.debug(f"Erro ao detectar tipo de disco: {e}")
                    # Fallback: trata todos como HDD
                    hdd_partitions = [p.device for p in psutil.disk_partitions() if 'fixed' in p.opts.lower()]

            # Informação sobre SSDs
            if ssd_partitions:
                print(f"{Fore.CYAN}SSDs detectados: {', '.join(ssd_partitions)}")
                print(f"{Fore.YELLOW}SSDs NÃO precisam de desfragmentação. Otimização automática habilitada.")
                self.logger.info(f"SSDs detectados (não serão desfragmentados): {ssd_partitions}")

            # Pergunta sobre desfragmentação para HDDs
            if hdd_partitions:
                print(f"\n{Fore.CYAN}HDDs detectados: {', '.join(hdd_partitions)}")
                print(f"{Fore.YELLOW}A desfragmentação pode levar MUITO tempo (30min - 2h ou mais).")

                # Solicita confirmação com timeout de 30s
                if self.get_user_confirmation(
                    "Deseja executar a DESFRAGMENTAÇÃO dos HDDs?",
                    timeout=30
                ):
                    print(f"{Fore.GREEN}Iniciando desfragmentação dos HDDs...")
                    for partition in hdd_partitions:
                        try:
                            print(f"{Fore.CYAN}Desfragmentando {partition}...")
                            subprocess.run(
                                ['defrag', partition, '/U', '/V'],
                                shell=True,
                                check=True
                            )
                            self.logger.info(f"Desfragmentação concluída: {partition}")
                        except Exception as e:
                            self.log_error(f"Erro ao desfragmentar {partition}", e)
                else:
                    print(f"{Fore.RED}Desfragmentação CANCELADA pelo usuário ou timeout.")
                    print(f"{Fore.RED}ENCERRANDO processo de limpeza conforme solicitado!")
                    self.logger.warning("Desfragmentação cancelada. Processo de limpeza encerrado.")

                    # Salva relatório parcial antes de encerrar
                    self.save_reports()

                    print(f"\n{Fore.YELLOW}{'='*60}")
                    print(f"{Fore.YELLOW}Processo encerrado devido à não confirmação da desfragmentação.")
                    print(f"{Fore.YELLOW}Limpezas já realizadas foram salvas no relatório.")
                    print(f"{Fore.YELLOW}{'='*60}\n")

                    sys.exit(0)

            # Otimiza SSDs (TRIM)
            if ssd_partitions:
                print(f"{Fore.CYAN}Otimizando SSDs (TRIM)...")
                for partition in ssd_partitions:
                    try:
                        subprocess.run(
                            ['defrag', partition, '/L'],  # /L = TRIM para SSDs
                            shell=True,
                            check=True
                        )
                        self.logger.info(f"TRIM executado em SSD: {partition}")
                    except Exception as e:
                        self.logger.debug(f"Erro ao executar TRIM em {partition}: {e}")

            self.logger.info("Otimização do sistema concluída.")
            print(f"{Fore.GREEN}Otimização do sistema concluída com sucesso!")

        except Exception as e:
            self.log_error("Erro durante otimização do sistema", e)

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
        """Salva os relatórios em TXT e JSON com informações detalhadas."""
        try:
            self.update_progress("Salvando relatórios...")
        except:
            pass  # Caso seja chamado fora do fluxo normal

        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        text_file = self.REPORT_PATH.format(date=date_str)
        json_file = self.JSON_REPORT_PATH.format(date=date_str)
        os.makedirs(os.path.dirname(text_file), exist_ok=True)

        # Salva o relatório TXT
        try:
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write(f"{'RELATÓRIO DE OTIMIZAÇÃO DO SISTEMA':^70}\n")
                f.write(f"{'Version ' + self.VERSION:^70}\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Duração: {(time.time() - self.start_time) / 60:.2f} minutos\n\n")

                # Resumo de limpeza
                f.write("-" * 70 + "\n")
                f.write("RESUMO DE LIMPEZA\n")
                f.write("-" * 70 + "\n")

                if 'temp_cleanup' in self.results:
                    f.write(f"\nArquivos Temporários:\n")
                    f.write(f"  Arquivos deletados: {self.results['temp_cleanup']['files_deleted']}\n")
                    f.write(f"  Espaço liberado: {self.results['temp_cleanup']['space_freed']}\n")

                if 'browser_cleanup' in self.results:
                    f.write(f"\nLimpeza de Navegadores:\n")
                    f.write(f"  Navegadores: {', '.join(self.results['browser_cleanup']['browsers'])}\n")
                    f.write(f"  Espaço liberado: {self.results['browser_cleanup']['space_freed']}\n")

                if 'windows_cache_cleanup' in self.results:
                    f.write(f"\nCache do Windows:\n")
                    f.write(f"  Espaço liberado: {self.results['windows_cache_cleanup']['space_freed']}\n")

                if 'registry_cleanup' in self.results:
                    f.write(f"\nLimpeza de Registro:\n")
                    f.write(f"  Entradas removidas: {self.results['registry_cleanup']['entries_cleaned']}\n")

                if 'broken_shortcuts' in self.results:
                    f.write(f"\nAtalhos Quebrados:\n")
                    f.write(f"  Atalhos removidos: {self.results['broken_shortcuts']['shortcuts_removed']}\n")

                # Desempenho do Sistema
                f.write("\n" + "-" * 70 + "\n")
                f.write("DESEMPENHO DO SISTEMA\n")
                f.write("-" * 70 + "\n")

                if 'cpu' in self.results:
                    f.write("\nCPU:\n")
                    for key, value in self.results['cpu'].items():
                        f.write(f"  {key}: {value}\n")

                if 'memory' in self.results:
                    f.write("\nMemória:\n")
                    for key, value in self.results['memory'].items():
                        f.write(f"  {key}: {value}\n")

                if 'top_processes' in self.results:
                    f.write("\nProcessos Mais Ativos:\n")
                    for proc in self.results['top_processes']:
                        f.write(f"  {proc['Nome']}: CPU {proc['CPU']}, Memória {proc['Memória']}\n")

                # Saúde dos Discos
                if 'disk_health' in self.results:
                    f.write("\n" + "-" * 70 + "\n")
                    f.write("SAÚDE DOS DISCOS\n")
                    f.write("-" * 70 + "\n")
                    for device, info in self.results['disk_health'].items():
                        f.write(f"\nDisco {device}:\n")
                        for k, v in info.items():
                            f.write(f"  {k}: {v}\n")

                # Verificação de Drivers
                if 'driver_check' in self.results:
                    f.write("\n" + "-" * 70 + "\n")
                    f.write("VERIFICAÇÃO DE DRIVERS\n")
                    f.write("-" * 70 + "\n")
                    f.write(f"\nProblemas encontrados: {self.results['driver_check']['issues_found']}\n")
                    if self.results['driver_check']['issues']:
                        f.write("\nDetalhes dos problemas:\n")
                        for issue in self.results['driver_check']['issues']:
                            f.write(f"  - {issue.get('name', 'N/A')}: {issue.get('status', issue.get('error_code', 'N/A'))}\n")

                # Instalações Antigas
                if 'old_installations' in self.results and self.results['old_installations']:
                    f.write("\n" + "-" * 70 + "\n")
                    f.write("INSTALAÇÕES ANTIGAS/QUEBRADAS\n")
                    f.write("-" * 70 + "\n")
                    for inst in self.results['old_installations']:
                        f.write(f"\n  Tipo: {inst['type']}\n")
                        f.write(f"  Caminho: {inst.get('path', 'N/A')}\n")
                        if 'size' in inst:
                            f.write(f"  Tamanho: {inst['size']}\n")
                        if 'name' in inst:
                            f.write(f"  Nome: {inst['name']}\n")

                # Avisos e Erros
                if self.warnings:
                    f.write("\n" + "-" * 70 + "\n")
                    f.write("AVISOS\n")
                    f.write("-" * 70 + "\n")
                    for warning in self.warnings:
                        f.write(f"  - {warning}\n")

                if self.errors:
                    f.write("\n" + "-" * 70 + "\n")
                    f.write("ERROS\n")
                    f.write("-" * 70 + "\n")
                    for error in self.errors:
                        f.write(f"  - {error}\n")

                f.write("\n" + "=" * 70 + "\n")
                f.write(f"{'FIM DO RELATÓRIO':^70}\n")
                f.write("=" * 70 + "\n")

            self.logger.info(f"Relatório TXT salvo em: {text_file}")
            print(f"{Fore.GREEN}Relatório TXT salvo: {text_file}")
        except Exception as e:
            self.log_error("Erro ao salvar relatório TXT", e)

        # Salva o relatório JSON
        try:
            report_data = {
                'version': self.VERSION,
                'timestamp': datetime.now().isoformat(),
                'duration_minutes': (time.time() - self.start_time) / 60,
                'results': self.results,
                'warnings': self.warnings,
                'errors': self.errors
            }

            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=4)

            self.logger.info(f"Relatório JSON salvo em: {json_file}")
            print(f"{Fore.GREEN}Relatório JSON salvo: {json_file}")
        except Exception as e:
            self.log_error("Erro ao salvar relatório JSON", e)

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
        """Executa todas as etapas de otimização com tratamento robusto de erros."""
        self.start_time = time.time()

        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*70}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'WINDOWS MAINTENANCE SCRIPT - OTIMIZADOR DE SISTEMA':^70}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'Version ' + self.VERSION:^70}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*70}\n")

        try:
            # Etapa 1: Verificação de versão
            self.check_app_version()

            # Etapa 2: Verificação de dependências
            self.check_and_install_dependencies()

            # Etapa 3: Ponto de restauração
            self.create_system_restore_point()

            # Etapa 4: Análise inicial do sistema
            self.check_disk_health()
            self.check_system_performance()

            # Etapa 5: Limpeza de arquivos temporários
            self.clean_temp_files()

            # Etapa 6: Limpeza de cache de navegadores
            self.clean_browser_cache()

            # Etapa 7: Limpeza de cache do Windows
            self.clean_windows_cache()

            # Etapa 8: Limpeza de registro
            self.clean_registry()

            # Etapa 9: Verificação de atalhos quebrados
            self.check_broken_shortcuts()

            # Etapa 10: Verificação de instalações antigas
            self.check_old_installations()

            # Etapa 11: Verificação de drivers
            self.check_drivers()

            # Etapa 12: Verificação e reparo de arquivos do sistema
            self.run_system_file_checker()

            # Etapa 13: Reparo DISM
            self.run_dism_commands()

            # Etapa 14: Otimização de programas de inicialização
            self.optimize_startup_programs()

            # Etapa 15: Otimização do sistema (inclui confirmação de desfragmentação)
            # IMPORTANTE: Se usuário não confirmar desfragmentação, o script encerra aqui
            self.optimize_system()

            # Etapa 16: Salvar relatórios
            self.save_reports()

            # Etapa 17: Notificar usuário
            self.notify_user()

            # Resumo final
            total_time = (time.time() - self.start_time) / 60
            print(f"\n{Fore.GREEN}{Style.BRIGHT}{'='*70}")
            print(f"{Fore.GREEN}{Style.BRIGHT}{'OTIMIZAÇÃO CONCLUÍDA COM SUCESSO!':^70}")
            print(f"{Fore.GREEN}{Style.BRIGHT}{'='*70}")
            print(f"\n{Fore.CYAN}Tempo total: {total_time:.2f} minutos")
            print(f"{Fore.CYAN}Erros: {len(self.errors)}")
            print(f"{Fore.CYAN}Avisos: {len(self.warnings)}")

            if self.errors:
                print(f"\n{Fore.YELLOW}Alguns erros ocorreram durante a execução:")
                for i, error in enumerate(self.errors[:5], 1):  # Mostra os primeiros 5
                    print(f"  {i}. {error}")
                if len(self.errors) > 5:
                    print(f"  ... e mais {len(self.errors) - 5} erro(s)")
                print(f"\n{Fore.YELLOW}Verifique o relatório completo para mais detalhes.")

            print(f"\n{Fore.GREEN}Logs salvos em: {self.LOG_PATH}")
            print(f"{Fore.GREEN}{'='*70}\n")

            self.logger.info(f"Otimização concluída com sucesso em {total_time:.2f} minutos.")
            self.logger.info(f"Total de erros: {len(self.errors)}, Total de avisos: {len(self.warnings)}")

        except KeyboardInterrupt:
            print(f"\n\n{Fore.RED}Operação cancelada pelo usuário!")
            self.logger.warning("Operação cancelada pelo usuário (Ctrl+C)")
            self.save_reports()
            sys.exit(1)

        except Exception as e:
            print(f"\n\n{Fore.RED}Erro crítico durante a execução: {e}")
            self.log_error("Erro crítico durante a execução", e)
            self.save_reports()
            sys.exit(1)

if __name__ == "__main__":
    optimizer = SystemOptimizer()
    optimizer.run()
