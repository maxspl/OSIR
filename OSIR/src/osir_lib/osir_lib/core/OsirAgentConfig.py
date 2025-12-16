import os
import yaml
from typing import Optional, List, Dict, Any

# Assurez-vous d'avoir Pydantic v2 ou v1
from pydantic import BaseModel, Field
from osir_lib.core.OsirConstants import OSIR_PATHS
from osir_lib.logger import AppLogger
from osir_lib.core.OsirSingleton import singleton
from osir_lib.core.FileManager import FileManager
logger = AppLogger(__name__).get_logger()

# --- MODÈLES PYDANTIC MIS À JOUR ---

class BoxDetails(BaseModel):
    """Modèle pour les détails de connexion d'une boîte distante (Remote Box)."""
    host: str
    user: str
    password: str
    custom_mountpoint: str = Field(default='C')

class WindowsBoxConfig(BaseModel):
    """Modèle pour la configuration de la Windows Box (inclut 'cores' si présent)."""
    location: str
    cores: Optional[int] = None  # Ajout de cores, rendu optionnel
    remote_box: BoxDetails

class MasterConfig(BaseModel):
    """Modèle pour la configuration du Master."""
    host: str

class SplunkConfig(BaseModel):
    """Modèle pour la configuration Splunk détaillée."""
    host: str
    user: str
    password: str
    port: int
    mport: int
    ssl: bool # booléen pour True/False

class FullAgentConfig(BaseModel):
    """Modèle racine qui valide l'intégralité du fichier agent.yml."""
    master: MasterConfig
    windows_box: WindowsBoxConfig
    splunk: SplunkConfig 

@singleton
class OsirAgentConfig:
    """
    Classe Singleton qui charge et valide la configuration à partir du YAML en utilisant Pydantic.
    """
    config_data: FullAgentConfig
    host_hostname: str
    host_ip_list: List[str]
    wsl_host: str
    standalone: bool
    is_wsl_mode: bool

    def __init__(self):
        """
        Initialise l'objet AgentConfig en lisant le YAML, en le validant avec Pydantic,
        et en initialisant les propriétés dérivées.
        """
        self._load_config()
        self.host_hostname = os.getenv('HOST_HOSTNAME', '')
        self.host_ip_list = os.getenv('HOST_IP_LIST', '').split(",") if os.getenv('HOST_IP_LIST') else []
        self.wsl_host = os.getenv('OSIR_PATH', '')
        self.is_wsl_mode = self._is_wsl()
        self.standalone = self._is_standalone()
        
    def _load_config(self):
        """
        Charge le fichier YAML et le valide en utilisant le modèle FullAgentConfig de Pydantic.
        """
        try:
            with open(FileManager.get_config_path('agent'), 'r') as file:
                data = yaml.safe_load(file)
            
            # Pydantic valide et désérialise les données
            self.config_data = FullAgentConfig.model_validate(data)
        except yaml.YAMLError as e:
            logger.error(f"Erreur de parsing YAML : {e}")
            raise
        except Exception as e:
            logger.error("Échec du chargement ou de la validation de la configuration de l'agent. " + str(e))
            raise

    @property
    def master_host(self) -> str:
        return self.config_data.master.host
        
    @property
    def windows_location(self) -> str:
        return self.config_data.windows_box.location

    @property
    def windows_user(self) -> str:
        return self.config_data.windows_box.remote_box.user

    @property
    def windows_password(self) -> str:
        return self.config_data.windows_box.remote_box.password

    @property
    def windows_mnt_point(self) -> str:
        return self.config_data.windows_box.remote_box.custom_mountpoint
        
    @property
    def windows_host(self) -> str:
        return self.config_data.windows_box.remote_box.host
        
    @property
    def splunk_host(self) -> str:
        return self.config_data.splunk.host
        
    @property
    def splunk_user(self) -> str:
        return self.config_data.splunk.user
        
    @property
    def splunk_password(self) -> str:
        return self.config_data.splunk.password
        
    @property
    def splunk_port(self) -> int:
        return self.config_data.splunk.port
        
    @property
    def splunk_mport(self) -> int:
        return self.config_data.splunk.mport
        
    @property
    def splunk_ssl(self) -> bool:
        return self.config_data.splunk.ssl

    def _is_standalone(self) -> bool:
        """Détermine si l'agent est en mode autonome."""
        master_host = self.master_host

        if master_host in ["127.0.0.1", "localhost", "host.docker.internal"]:
            return True
        elif master_host == self.host_hostname:
            return True
        else:
            for host_ip in self.host_ip_list:
                if host_ip == master_host:
                    return True
        return False

    def _is_wsl(self) -> bool:
        """Vérifie si le script s'exécute dans WSL."""
        try:
            with open('/proc/sys/kernel/osrelease', 'rt') as f:
                return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
        except FileNotFoundError:
            pass
        try:
            with open('/proc/version', 'rt') as f:
                return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
        except FileNotFoundError:
            return False