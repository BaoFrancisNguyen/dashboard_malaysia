#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DASHBOARD MALAYSIA - SCRIPT DE LANCEMENT
========================================

Script de lancement pour le dashboard Malaysia avec vérifications
et configuration automatique

Version: 1.0.0
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import argparse


def check_python_version():
    """Vérifie la version Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou supérieur requis")
        print(f"   Version actuelle: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_ollama():
    """Vérifie la disponibilité d'Ollama"""
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Ollama détecté")
            
            # Vérification du modèle Mistral
            if 'mistral:latest' in result.stdout:
                print("✅ Modèle mistral:latest disponible")
                return True
            else:
                print("⚠️  Modèle mistral:latest non trouvé")
                print("💡 Téléchargez avec: ollama pull mistral:latest")
                return False
        else:
            print("❌ Ollama non accessible")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Ollama timeout - vérifiez qu'il est démarré")
        return False
    except FileNotFoundError:
        print("❌ Ollama non installé")
        print("💡 Installez depuis: https://ollama.ai")
        return False
    except Exception as e:
        print(f"❌ Erreur Ollama: {e}")
        return False


def install_dependencies():
    """Installe les dépendances Python"""
    print("📦 Installation des dépendances...")
    
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
    
    try:
        for requirement in requirements:
            print(f"  📄 Installation de {requirement.split('>=')[0]}...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', requirement, '--quiet'
            ])
        
        print("✅ Dépendances installées avec succès")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation: {e}")
        return False


def check_exports_directory():
    """Vérifie le dossier exports"""
    exports_dir = Path('exports')
    
    if not exports_dir.exists():
        print("⚠️  Dossier 'exports' manquant")
        print("💡 Créez le dossier exports/ et copiez-y les fichiers du projet Malaysia")
        return False
    
    # Vérification des fichiers attendus
    expected_files = [
        'buildings_metadata.csv',
        'electricity_consumption.csv',
        'weather_simulation.csv',
        'water_consumption.csv'
    ]
    
    found_files = []
    for file in expected_files:
        if (exports_dir / file).exists():
            found_files.append(file)
    
    if found_files:
        print(f"✅ Fichiers trouvés: {len(found_files)}/{len(expected_files)}")
        for file in found_files:
            size_mb = (exports_dir / file).stat().st_size / (1024*1024)
            print(f"  📄 {file} ({size_mb:.1f} MB)")
        return True
    else:
        print("⚠️  Aucun fichier de données trouvé")
        print("💡 Générez d'abord les données avec le projet Malaysia")
        return False


def start_dashboard(port=8080, debug=False, auto_open=True):
    """Lance le dashboard"""
    print(f"🚀 Lancement du Dashboard Malaysia sur le port {port}")
    
    try:
        # Import de l'application
        from app import DashboardApp
        
        print("✅ Application importée")
        print("\n" + "="*60)
        print("📋 DASHBOARD MALAYSIA - ANALYSE INTELLIGENTE")
        print("="*60)
        print("🏗️  Architecture:")
        print("   📊 Visualisations interactives (Plotly + Leaflet)")
        print("   🤖 Analyse LLM locale (Ollama Mistral)")
        print("   🧠 Système RAG intelligent")
        print("   🗺️  Cartographie des bâtiments Malaysia")
        print()
        print("🌐 URL: http://localhost:8080")
        print("📁 Données: exports/")
        print("📋 Logs: logs/")
        print()
        print("🎯 Utilisation:")
        print("   1. Cliquez 'Charger Données' dans l'interface")
        print("   2. Explorez les onglets: Vue d'ensemble, Consommation, Bâtiments")
        print("   3. Posez vos questions à l'IA dans l'onglet 'Analyse LLM'")
        print()
        print("ℹ️  Ctrl+C pour arrêter")
        print("="*60)
        
        # Ouverture automatique du navigateur
        if auto_open:
            import webbrowser
            import threading
            
            def open_browser():
                time.sleep(2)  # Attendre que le serveur démarre
                webbrowser.open(f'http://localhost:{port}')
            
            threading.Thread(target=open_browser, daemon=True).start()
        
        # Lancement de l'application
        app = DashboardApp()
        app.run(host='0.0.0.0', port=port, debug=debug)
        
    except ImportError as e:
        print(f"❌ Erreur import application: {e}")
        print("💡 Vérifiez que tous les fichiers sont présents")
        return False
        
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du dashboard")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur démarrage: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Dashboard Malaysia - Analyse Électrique')
    parser.add_argument('--port', type=int, default=8080, help='Port du serveur (défaut: 8080)')
    parser.add_argument('--debug', action='store_true', help='Mode debug')
    parser.add_argument('--no-browser', action='store_true', help='Ne pas ouvrir le navigateur')
    parser.add_argument('--install-deps', action='store_true', help='Installer les dépendances')
    parser.add_argument('--check-only', action='store_true', help='Vérifier seulement les prérequis')
    
    args = parser.parse_args()
    
    print("🇲🇾 DASHBOARD MALAYSIA - DÉMARRAGE")
    print("="*50)
    
    # Vérifications des prérequis
    print("\n🔍 Vérification des prérequis...")
    
    if not check_python_version():
        return 1
    
    # Installation des dépendances si demandé
    if args.install_deps:
        if not install_dependencies():
            return 1
    
    # Vérification Ollama
    ollama_ok = check_ollama()
    if not ollama_ok:
        print("⚠️  Ollama non disponible - fonctionnalité LLM limitée")
    
    # Vérification des données
    data_ok = check_exports_directory()
    if not data_ok:
        print("⚠️  Données non trouvées - dashboard fonctionnera en mode démo")
    
    # Si vérification seulement
    if args.check_only:
        print("\n✅ Vérifications terminées")
        return 0
    
    # Démarrage du dashboard
    print("\n🚀 Démarrage du dashboard...")
    success = start_dashboard(
        port=args.port,
        debug=args.debug,
        auto_open=not args.no_browser
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())