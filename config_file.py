#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURATION - DASHBOARD MALAYSIA
=================================

Configuration centralisée pour le dashboard Malaysia

Version: 1.0.0
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class AppConfig:
    """Configuration de l'application"""
    name: str = "Malaysia Electricity Dashboard"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8080
    secret_key: str = "malaysia-dashboard-secret-key"


@dataclass
class OllamaConfig:
    """Configuration Ollama"""
    base_url: str = "http://localhost:11434"
    model: str = "mistral:latest"
    timeout: int = 120
    temperature: float = 0.1
    max_tokens: int = 2048


@dataclass
class RAGConfig:
    """Configuration RAG"""
    db_path: str = "data/rag_knowledge.db"
    max_embeddings: int = 10000
    similarity_threshold: float = 0.3
    use_sentence_transformers: bool = True
    sentence_model: str = "all-MiniLM-L6-v2"


@dataclass
class DataConfig:
    """Configuration des données"""
    exports_dir: str = "exports"
    cache_timeout: int = 3600  # 1 heure
    max_file_size_mb: int = 100
    supported_formats: list = None
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['csv', 'xlsx', 'parquet', 'json']


@dataclass
class MapConfig:
    """Configuration cartographique"""
    default_center: list = None
    default_zoom: int = 6
    max_markers: int = 10000
    cluster_threshold: int = 100
    malaysia_bounds: dict = None
    
    def __post_init__(self):
        if self.default_center is None:
            self.default_center = [4.2105, 101.9758]  # Centre Malaysia
        
        if self.malaysia_bounds is None:
            self.malaysia_bounds = {
                'lat_min': 0.5,
                'lat_max': 7.5,
                'lon_min': 99.0,
                'lon_max': 120.0
            }


@dataclass
class ChartConfig:
    """Configuration des graphiques"""
    theme: str = "dark"
    animation_duration: int = 500
    max_data_points: int = 50000
    color_palette: dict = None
    building_colors: dict = None
    
    def __post_init__(self):
        if self.color_palette is None:
            self.color_palette = {
                'primary': '#2563eb',
                'secondary': '#64748b', 
                'success': '#059669',
                'warning': '#d97706',
                'danger': '#dc2626',
                'info': '#0891b2'
            }
        
        if self.building_colors is None:
            self.building_colors = {
                'residential': '#28a745',
                'commercial': '#007bff',
                'industrial': '#dc3545',
                'office': '#6f42c1',
                'retail': '#fd7e14',
                'warehouse': '#6c757d',
                'hospital': '#e83e8c',
                'school': '#20c997',
                'hotel': '#ffc107',
                'mixed': '#343a40',
                'other': '#17a2b8'
            }


@dataclass
class LoggingConfig:
    """Configuration du logging"""
    level: str = "INFO"
    file: str = "logs/dashboard.log"
    max_size_mb: int = 10
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class Config:
    """Configuration principale du dashboard"""
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        """
        Initialise la configuration
        
        Args:
            config_dict: Configuration personnalisée optionnelle
        """
        # Configuration par défaut
        self.app = AppConfig()
        self.ollama = OllamaConfig()
        self.rag = RAGConfig()
        self.data = DataConfig()
        self.map = MapConfig()
        self.charts = ChartConfig()
        self.logging = LoggingConfig()
        
        # Application de la configuration personnalisée
        if config_dict:
            self._apply_custom_config(config_dict)
        
        # Variables d'environnement
        self._load_from_env()
    
    def _apply_custom_config(self, config_dict: Dict[str, Any]):
        """Applique une configuration personnalisée"""
        for section, values in config_dict.items():
            if hasattr(self, section):
                section_config = getattr(self, section)
                for key, value in values.items():
                    if hasattr(section_config, key):
                        setattr(section_config, key, value)
    
    def _load_from_env(self):
        """Charge la configuration depuis les variables d'environnement"""
        # App
        self.app.debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        self.app.host = os.getenv('FLASK_HOST', self.app.host)
        self.app.port = int(os.getenv('FLASK_PORT', self.app.port))
        
        # Ollama
        self.ollama.base_url = os.getenv('OLLAMA_BASE_URL', self.ollama.base_url)
        self.ollama.model = os.getenv('OLLAMA_MODEL', self.ollama.model)
        
        # RAG
        self.rag.db_path = os.getenv('RAG_DB_PATH', self.rag.db_path)
        
        # Data
        self.data.exports_dir = os.getenv('EXPORTS_DIR', self.data.exports_dir)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire"""
        return {
            'app': self.app.__dict__,
            'ollama': self.ollama.__dict__,
            'rag': self.rag.__dict__,
            'data': self.data.__dict__,
            'map': self.map.__dict__,
            'charts': self.charts.__dict__,
            'logging': self.logging.__dict__
        }
    
    def validate(self) -> Dict[str, Any]:
        """Valide la configuration"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validation des ports
        if not (1 <= self.app.port <= 65535):
            validation_result['errors'].append(f"Port invalide: {self.app.port}")
            validation_result['valid'] = False
        
        # Validation des chemins
        if not Path(self.data.exports_dir).exists():
            validation_result['warnings'].append(f"Dossier exports manquant: {self.data.exports_dir}")
        
        # Validation Ollama
        if not self.ollama.base_url.startswith(('http://', 'https://')):
            validation_result['errors'].append(f"URL Ollama invalide: {self.ollama.base_url}")
            validation_result['valid'] = False
        
        return validation_result


# Configuration globale par défaut
default_config = Config()

# Export de la configuration
__all__ = [
    'Config',
    'AppConfig',
    'OllamaConfig', 
    'RAGConfig',
    'DataConfig',
    'MapConfig',
    'ChartConfig',
    'LoggingConfig',
    'default_config'
]


def load_config(config_file: str = None) -> Config:
    """
    Charge la configuration depuis un fichier ou utilise les défauts
    
    Args:
        config_file: Chemin vers le fichier de configuration (optionnel)
        
    Returns:
        Config: Configuration chargée
    """
    if config_file and Path(config_file).exists():
        import json
        with open(config_file, 'r') as f:
            config_dict = json.load(f)
        return Config(config_dict)
    else:
        return Config()


def save_config(config: Config, config_file: str):
    """
    Sauvegarde la configuration dans un fichier
    
    Args:
        config: Configuration à sauvegarder
        config_file: Chemin du fichier de destination
    """
    import json
    with open(config_file, 'w') as f:
        json.dump(config.to_dict(), f, indent=2)


if __name__ == '__main__':
    # Test de la configuration
    config = Config()
    validation = config.validate()
    
    print("🔧 Test Configuration Dashboard Malaysia:")
    print(f"✅ Configuration valide: {validation['valid']}")
    if validation['errors']:
        print(f"❌ Erreurs: {validation['errors']}")
    if validation['warnings']:
        print(f"⚠️ Avertissements: {validation['warnings']}")
    
    print(f"\n📋 Configuration actuelle:")
    print(f"   App: {config.app.name} v{config.app.version}")
    print(f"   Port: {config.app.port}")
    print(f"   Ollama: {config.ollama.base_url}")
    print(f"   Modèle: {config.ollama.model}")
    print(f"   RAG DB: {config.rag.db_path}")
    print(f"   Exports: {config.data.exports_dir}")