#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SETUP - DASHBOARD MALAYSIA
=========================

Script de setup et installation automatique
pour le dashboard Malaysia

Version: 1.0.0
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List


class DashboardSetup:
    """Setup automatique du dashboard Malaysia"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.python_exe = sys.executable
        
    def run_setup(self):
        """Lance le setup complet"""
        print("🚀 SETUP DASHBOARD MALAYSIA")
        print("=" * 50)
        
        steps = [
            ("🐍 Vérification Python", self.check_python),
            ("📦 Installation dépendances", self.install_dependencies),
            ("🔧 Configuration Ollama", self.check_ollama),
            ("📋 Création fichiers", self.create_files),
            ("✅ Tests finaux", self.run_tests)
        ]
        
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            try:
                step_func()
                print(f"✅ {step_name} terminé")
            except Exception as e:
                print(f"❌ Erreur {step_name}: {e}")
                return False
        
        print("\n🎉 SETUP TERMINÉ AVEC SUCCÈS!")
        self.print_usage_instructions()
        return True
    
    def check_python(self):
        """Vérifie la version Python"""
        if sys.version_info < (3, 8):
            raise Exception(f"Python 3.8+ requis (actuel: {sys.version})")
        print(f"   Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ✓")
    
    def install_dependencies(self):
        """Installe les dépendances Python"""
        requirements = [
            'flask>=3.0.0',
            'flask-socketio>=5.3.6',
            'pandas>=2.0.0',
            'numpy>=1.24.0',
            'plotly>=5.17.0',
            'scikit-learn>=1.3.0',
            'sentence-transformers>=2.2.2',
            'requests>=2.31.0',
            'python-socketio>=5.9.0',
            'eventlet>=0.33.3'
        ]
        
        print("   Installation des packages...")
        for requirement in requirements:
            try:
                subprocess.check_call([
                    self.python_exe, '-m', 'pip', 'install', requirement, '--quiet'
                ])
                package_name = requirement.split('>=')[0]
                print(f"   ✓ {package_name}")
            except subprocess.CalledProcessError:
                print(f"   ⚠️ Échec: {requirement}")
    
    def check_ollama(self):
        """Vérifie et configure Ollama"""
        try:
            # Test commande ollama
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("   ✓ Ollama installé")
                
                # Vérification du modèle Mistral
                list_result = subprocess.run(['ollama', 'list'], 
                                           capture_output=True, text=True, timeout=10)
                
                if 'mistral:latest' in list_result.stdout:
                    print("   ✓ Modèle mistral:latest disponible")
                else:
                    print("   ⚠️ Modèle mistral:latest manquant")
                    print("   💡 Installez avec: ollama pull mistral:latest")
            else:
                raise Exception("Ollama non fonctionnel")
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("   ❌ Ollama non installé")
            print("   💡 Installez depuis: https://ollama.ai")
            raise Exception("Ollama requis pour l'IA")
    
    def create_files(self):
        """Crée les fichiers de configuration"""
        
        # requirements.txt
        requirements_content = """# Dashboard Malaysia - Requirements
flask>=3.0.0
flask-socketio>=5.3.6
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
scikit-learn>=1.3.0
sentence-transformers>=2.2.2
requests>=2.31.0
python-socketio>=5.9.0
eventlet>=0.33.3
"""
        
        with open('requirements.txt', 'w') as f:
            f.write(requirements_content)
        print("   📄 requirements.txt")
        
        # .env exemple
        env_content = """# Dashboard Malaysia - Configuration
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=8080
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:latest
RAG_DB_PATH=data/rag_knowledge.db
EXPORTS_DIR=exports
"""
        
        with open('.env.example', 'w') as f:
            f.write(env_content)
        print("   📄 .env.example")
        
        # .gitignore
        gitignore_content = """# Dashboard Malaysia - Git Ignore
__pycache__/
*.py[cod]
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
env/
venv/
ENV/
env.bak/
venv.bak/
.venv/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
Thumbs.db
desktop.ini

# Application specific
data/
exports/
logs/
*.log
.env
.env.local

# Temporary files
temp/
tmp/
*.tmp
*.temp
"""
        
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("   📄 .gitignore")
        
        # Configuration JSON
        config_data = {
            "app": {
                "name": "Malaysia Electricity Dashboard",
                "version": "1.0.0",
                "debug": True,
                "port": 8080
            },
            "ollama": {
                "base_url": "http://localhost:11434",
                "model": "mistral:latest",
                "timeout": 120
            },
            "rag": {
                "db_path": "data/rag_knowledge.db",
                "max_embeddings": 10000
            },
            "data": {
                "exports_dir": "exports",
                "cache_timeout": 3600
            }
        }
        
        with open('config.json', 'w') as f:
            json.dump(config_data, f, indent=2)
        print("   📄 config.json")
    
    def run_tests(self):
        """Lance des tests basiques"""
        print("   🧪 Test imports...")
        
        # Test import des packages principaux
        test_imports = [
            'flask',
            'pandas',
            'numpy',
            'plotly',
            'sklearn',
            'requests'
        ]
        
        for package in test_imports:
            try:
                __import__(package)
                print(f"   ✓ {package}")
            except ImportError:
                print(f"   ❌ {package} manquant")
        
        # Test création base RAG (seulement si le dossier data existe)
        if Path('data').exists():
            try:
                import sqlite3
                conn = sqlite3.connect('data/test.db')
                conn.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER)')
                conn.close()
                os.remove('data/test.db')
                print("   ✓ SQLite fonctionnel")
            except Exception as e:
                print(f"   ❌ SQLite: {e}")
        else:
            print("   ⚠️ Dossier data non trouvé (normal si structure existante)")
    
    def print_usage_instructions(self):
        """Affiche les instructions d'utilisation"""
        print("\n📋 INSTRUCTIONS D'UTILISATION:")
        print("=" * 50)
        print("1. 📁 Générez les données avec le projet Malaysia original:")
        print("   cd /chemin/vers/malaysia-project")
        print("   python run.py")
        print()
        print("2. 📋 Copiez les fichiers CSV vers ce dashboard:")
        print("   cp malaysia-project/exports/*.csv malaysia-dashboard/exports/")
        print()
        print("3. 🚀 Démarrez Ollama (terminal séparé):")
        print("   ollama serve")
        print()
        print("4. 🎯 Lancez le dashboard:")
        print("   python run_dashboard.py")
        print()
        print("5. 🌐 Accédez à l'interface:")
        print("   http://localhost:8080")
        print()
        print("📚 Fichiers créés:")
        print("   • requirements.txt - Dépendances Python")
        print("   • config.json - Configuration")
        print("   • .env.example - Variables d'environnement")
        print("   • .gitignore - Fichiers à ignorer")
        print()
        print("🎉 Dashboard Malaysia prêt à l'emploi!")


def main():
    """Point d'entrée principal"""
    setup = DashboardSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("🔧 Setup Dashboard Malaysia")
        print("Usage: python setup.py [--help]")
        print()
        print("Ce script installe et configure automatiquement")
        print("le dashboard Malaysia avec toutes ses dépendances.")
        return
    
    try:
        success = setup.run_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur setup: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()