#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MALAYSIA ELECTRICITY DASHBOARD - APPLICATION PRINCIPALE
======================================================

Dashboard moderne pour l'analyse des données électriques Malaysia
avec intégration Ollama (Mistral) et système RAG

Version: 1.0.0
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit

# Configuration des chemins
PROJECT_ROOT = Path(__file__).parent.absolute()
DATA_DIR = PROJECT_ROOT / 'data'
EXPORTS_DIR = PROJECT_ROOT / 'exports'
MODELS_DIR = PROJECT_ROOT / 'models'

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Imports des modules dashboard
from dashboard.services.ollama_service import OllamaService
from dashboard.services.rag_service import RAGService
from dashboard.services.data_service import DataService
from dashboard.services.map_service import MapService
from dashboard.utils.chart_generator import ChartGenerator
from dashboard.utils.helpers import setup_dashboard_logging

class DashboardApp:
    """Application Dashboard principale"""
    
    def __init__(self):
        """Initialise l'application dashboard"""
        self.app = Flask(__name__, static_folder='dashboard/static', template_folder='templates')
        self.app.secret_key = 'malaysia-dashboard-key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Services
        self.ollama_service = OllamaService()
        self.rag_service = RAGService()
        self.data_service = DataService()
        self.map_service = MapService()
        self.chart_generator = ChartGenerator()
        
        # Cache application
        self.cache = {
            'data_loaded': False,
            'last_update': None,
            'current_dataset': None,
            'analysis_history': []
        }
        
        self._setup_routes()
        logger.info("✅ Dashboard App initialisée")
    
    def _setup_routes(self):
        """Configure les routes Flask"""
        
        @self.app.route('/')
        def index():
            """Page dashboard principale"""
            return render_template('dashboard.html')
        
        @self.app.route('/api/data/load', methods=['POST'])
        def load_data():
            """Charge les données depuis les exports du projet Malaysia"""
            try:
                data_info = self.data_service.load_malaysia_data()
                self.cache['data_loaded'] = True
                self.cache['last_update'] = datetime.now()
                self.cache['current_dataset'] = data_info
                
                return jsonify({
                    'success': True,
                    'message': 'Données chargées avec succès',
                    'data_info': data_info
                })
            except Exception as e:
                logger.error(f"Erreur chargement données: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/data/summary')
        def data_summary():
            """Résumé des données actuelles"""
            if not self.cache['data_loaded']:
                return jsonify({'success': False, 'error': 'Aucune donnée chargée'})
            
            try:
                summary = self.data_service.get_data_summary()
                return jsonify({'success': True, 'summary': summary})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/charts/overview')
        def charts_overview():
            """Génère les graphiques de vue d'ensemble"""
            if not self.cache['data_loaded']:
                return jsonify({'success': False, 'error': 'Aucune donnée chargée'})
            
            try:
                charts = self.chart_generator.create_overview_charts(
                    self.data_service.get_current_data()
                )
                return jsonify({'success': True, 'charts': charts})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/charts/consumption')
        def charts_consumption():
            """Graphiques de consommation électrique"""
            try:
                time_range = request.args.get('range', '7d')
                building_type = request.args.get('type', 'all')
                
                charts = self.chart_generator.create_consumption_charts(
                    self.data_service.get_current_data(),
                    time_range=time_range,
                    building_type=building_type
                )
                return jsonify({'success': True, 'charts': charts})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/llm/analyze', methods=['POST'])
        def llm_analyze():
            """Analyse des données via Ollama"""
            try:
                data = request.get_json()
                question = data.get('question', '')
                
                if not question:
                    return jsonify({'success': False, 'error': 'Question requise'})
                
                # Recherche dans le RAG
                context = self.rag_service.search_context(question)
                
                # Analyse via Ollama
                analysis = self.ollama_service.analyze_data(
                    question=question,
                    context=context,
                    data_summary=self.data_service.get_data_summary()
                )
                
                # Stockage dans l'historique
                self.cache['analysis_history'].append({
                    'timestamp': datetime.now().isoformat(),
                    'question': question,
                    'analysis': analysis
                })
                
                return jsonify({
                    'success': True,
                    'analysis': analysis,
                    'context_used': len(context) > 0
                })
            except Exception as e:
                logger.error(f"Erreur analyse LLM: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/map/buildings')
        def map_buildings():
            """Données cartographiques des bâtiments"""
            if not self.cache['data_loaded']:
                return jsonify({'success': False, 'error': 'Aucune donnée chargée'})
            
            try:
                density = int(request.args.get('density', 100))
                building_type = request.args.get('type', 'all')
                
                buildings_data = self.data_service.get_current_data().get('buildings')
                
                # Filtrage par type si nécessaire
                if building_type != 'all' and buildings_data is not None:
                    buildings_data = buildings_data[
                        buildings_data['building_type'] == building_type
                    ]
                
                map_data = self.map_service.create_buildings_map_data(
                    buildings_data, density_percentage=density
                )
                
                return jsonify({'success': True, 'map_data': map_data})
                
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/map/consumption-heatmap')
        def map_consumption_heatmap():
            """Heatmap de consommation"""
            if not self.cache['data_loaded']:
                return jsonify({'success': False, 'error': 'Aucune donnée chargée'})
            
            try:
                current_data = self.data_service.get_current_data()
                
                heatmap_data = self.map_service.create_consumption_heatmap_data(
                    current_data.get('consumption'),
                    current_data.get('buildings')
                )
                
                return jsonify({'success': True, 'heatmap_data': heatmap_data})
                
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/map/zones')
        def map_zones():
            """Analyse cartographique par zone"""
            if not self.cache['data_loaded']:
                return jsonify({'success': False, 'error': 'Aucune donnée chargée'})
            
            try:
                buildings_data = self.data_service.get_current_data().get('buildings')
                
                zones_data = self.map_service.create_zone_analysis_data(buildings_data)
                
                return jsonify({'success': True, 'zones_data': zones_data})
                
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/map/statistics')
        def map_statistics():
            """Statistiques cartographiques"""
            if not self.cache['data_loaded']:
                return jsonify({'success': False, 'error': 'Aucune donnée chargée'})
            
            try:
                buildings_data = self.data_service.get_current_data().get('buildings')
                stats = self.map_service.get_map_statistics(buildings_data)
                
                return jsonify({'success': True, 'statistics': stats})
                
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/rag/update', methods=['POST'])
        def update_rag():
            """Met à jour la base de connaissances RAG"""
            try:
                # Index des données actuelles
                if self.cache['data_loaded']:
                    self.rag_service.index_current_data(
                        self.data_service.get_current_data()
                    )
                
                return jsonify({
                    'success': True,
                    'message': 'Base RAG mise à jour'
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.socketio.on('connect')
        def handle_connect():
            """Gestion connexion WebSocket"""
            logger.info("Client connecté au dashboard")
            emit('status', {'message': 'Connecté au dashboard Malaysia'})
        
        @self.socketio.on('request_analysis')
        def handle_analysis_request(data):
            """Gestion requête d'analyse en temps réel"""
            try:
                question = data.get('question', '')
                
                # Analyse asynchrone
                emit('analysis_started', {'question': question})
                
                # Recherche contexte
                context = self.rag_service.search_context(question)
                emit('context_found', {'context_items': len(context)})
                
                # Analyse LLM
                analysis = self.ollama_service.analyze_data_stream(
                    question=question,
                    context=context,
                    data_summary=self.data_service.get_data_summary()
                )
                
                emit('analysis_complete', {
                    'question': question,
                    'analysis': analysis
                })
                
            except Exception as e:
                emit('analysis_error', {'error': str(e)})

    def run(self, host='127.0.0.1', port=8080, debug=True):
        """Lance l'application dashboard"""
        logger.info(f"🚀 Lancement Dashboard Malaysia sur http://{host}:{port}")
        logger.info("📊 Fonctionnalités:")
        logger.info("   • Visualisation données électriques Malaysia")
        logger.info("   • Analyse LLM avec Ollama (Mistral)")
        logger.info("   • Système RAG pour contexte intelligent")
        logger.info("   • Dashboards interactifs temps réel")
        
        self.socketio.run(
            self.app,
            host=host,
            port=port,
            debug=debug
        )


# ==============================================================================
# POINT D'ENTRÉE
# ==============================================================================

if __name__ == '__main__':
    # Vérification Ollama
    import subprocess
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if 'mistral:latest' not in result.stdout:
            print("⚠️ Modèle mistral:latest non trouvé")
            print("🔧 Installez avec: ollama pull mistral:latest")
    except FileNotFoundError:
        print("❌ Ollama non installé")
        print("🔧 Installez depuis: https://ollama.ai")
    
    # Lancement de l'application
    app = DashboardApp()
    app.run()