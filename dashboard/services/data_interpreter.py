#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTERPRÉTEUR DE DONNÉES - DASHBOARD MALAYSIA
===========================================

Service d'interprétation automatique des données par le LLM
pour générer des insights intelligents dès le chargement

Version: 1.0.0
"""

import logging
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class DataInterpreter:
    """Service d'interprétation automatique des données par LLM"""
    
    def __init__(self, ollama_service, rag_service, data_service):
        """
        Initialise l'interpréteur de données
        
        Args:
            ollama_service: Service Ollama pour l'IA
            rag_service: Service RAG pour le contexte
            data_service: Service de données
        """
        self.ollama_service = ollama_service
        self.rag_service = rag_service
        self.data_service = data_service
        
        # Base de données pour stocker les interprétations
        self.db_path = Path("data/interpretations.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_interpretations_db()
        
        # Templates d'analyse par type de données
        self.analysis_templates = {
            'overview': self._get_overview_template(),
            'consumption': self._get_consumption_template(),
            'buildings': self._get_buildings_template(),
            'weather': self._get_weather_template(),
            'water': self._get_water_template(),
            'trends': self._get_trends_template(),
            'anomalies': self._get_anomalies_template(),
            'recommendations': self._get_recommendations_template()
        }
        
        logger.info("✅ DataInterpreter initialisé")
    
    def _init_interpretations_db(self):
        """Initialise la base de données des interprétations"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interpretations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    interpretation_type TEXT,
                    data_hash TEXT,
                    analysis_content TEXT,
                    insights TEXT,
                    recommendations TEXT,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interpretation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    interpretation_id INTEGER,
                    user_feedback TEXT,
                    usefulness_score INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (interpretation_id) REFERENCES interpretations (id)
                )
            """)
            
            conn.commit()
    
    async def interpret_loaded_data(self, force_refresh: bool = False) -> Dict:
        """
        Lance l'interprétation complète des données chargées
        
        Args:
            force_refresh: Force une nouvelle analyse même si déjà fait
            
        Returns:
            Dict: Résultats de toutes les interprétations
        """
        try:
            logger.info("🧠 Démarrage interprétation automatique des données...")
            
            # Récupération des données actuelles
            current_data = self.data_service.get_current_data()
            data_summary = self.data_service.get_data_summary()
            
            if not any(current_data.values()):
                return {
                    'success': False,
                    'error': 'Aucune donnée chargée à interpréter'
                }
            
            # Calcul du hash des données pour éviter les analyses répétées
            data_hash = self._calculate_data_hash(current_data)
            
            if not force_refresh and self._interpretation_exists(data_hash):
                logger.info("📋 Interprétation existante trouvée, récupération...")
                return self._get_existing_interpretation(data_hash)
            
            # Analyses par composant
            interpretations = {}
            
            # 1. Vue d'ensemble générale
            interpretations['overview'] = await self._analyze_overview(
                current_data, data_summary
            )
            
            # 2. Analyse de consommation
            if current_data.get('consumption') is not None:
                interpretations['consumption'] = await self._analyze_consumption(
                    current_data['consumption'], current_data.get('buildings')
                )
            
            # 3. Analyse des bâtiments
            if current_data.get('buildings') is not None:
                interpretations['buildings'] = await self._analyze_buildings(
                    current_data['buildings']
                )
            
            # 4. Corrélations météo (si disponible)
            if current_data.get('weather') is not None:
                interpretations['weather'] = await self._analyze_weather_correlation(
                    current_data['weather'], current_data.get('consumption')
                )
            
            # 5. Détection d'anomalies
            interpretations['anomalies'] = await self._detect_anomalies(
                current_data
            )
            
            # 6. Tendances temporelles
            interpretations['trends'] = await self._analyze_trends(
                current_data
            )
            
            # 7. Recommandations stratégiques
            interpretations['recommendations'] = await self._generate_recommendations(
                current_data, data_summary, interpretations
            )
            
            # Sauvegarde des résultats
            self._save_interpretation_results(data_hash, interpretations)
            
            # Création d'un résumé exécutif
            executive_summary = await self._create_executive_summary(interpretations)
            
            final_result = {
                'success': True,
                'interpretations': interpretations,
                'executive_summary': executive_summary,
                'analysis_timestamp': datetime.now().isoformat(),
                'data_hash': data_hash,
                'confidence_score': self._calculate_overall_confidence(interpretations)
            }
            
            logger.info("✅ Interprétation automatique terminée")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Erreur interprétation données: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_analysis': self._generate_fallback_analysis(data_summary)
            }
    
    async def _analyze_overview(self, data: Dict, summary: Dict) -> Dict:
        """Analyse vue d'ensemble des données"""
        try:
            # Préparation du contexte statistique
            stats_context = f"""
RÉSUMÉ DES DONNÉES MALAYSIA:
- Période analysée: {summary.get('period', 'Non définie')}
- Nombre total de bâtiments: {summary.get('total_buildings', 0):,}
- Types de bâtiments: {', '.join(summary.get('building_types', []))}
- Zones géographiques: {', '.join(summary.get('zones', []))}
- Consommation totale: {summary.get('total_consumption', 0):,.0f} kWh
- Consommation moyenne: {summary.get('avg_consumption', 0):.1f} kWh
- Points de données: {summary.get('total_data_points', 0):,}

DISPONIBILITÉ DES DONNÉES:
- Bâtiments: {'✓' if summary.get('data_availability', {}).get('buildings') else '✗'}
- Consommation: {'✓' if summary.get('data_availability', {}).get('consumption') else '✗'}
- Météo: {'✓' if summary.get('data_availability', {}).get('weather') else '✗'}
- Eau: {'✓' if summary.get('data_availability', {}).get('water') else '✗'}
"""
            
            # Recherche de contexte RAG pertinent
            rag_context = self.rag_service.search_context(
                "vue d'ensemble données énergétiques Malaysia", top_k=3
            )
            
            # Construction du prompt d'analyse
            prompt = self.analysis_templates['overview'].format(
                stats_context=stats_context,
                rag_context=self._format_rag_context(rag_context)
            )
            
            # Analyse par le LLM
            analysis = self.ollama_service.analyze_data(
                question="Analyse et interprète cette vue d'ensemble des données énergétiques",
                context=rag_context,
                data_summary=summary
            )
            
            if analysis.get('success'):
                return {
                    'type': 'overview',
                    'content': analysis['analysis']['full_response'],
                    'insights': analysis['analysis'].get('insights', []),
                    'confidence': 0.9,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception(f"Échec analyse LLM: {analysis.get('error')}")
                
        except Exception as e:
            logger.error(f"Erreur analyse overview: {e}")
            return {
                'type': 'overview',
                'content': f"Analyse automatique non disponible: {e}",
                'insights': [],
                'confidence': 0.1,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _analyze_consumption(self, consumption_df: pd.DataFrame, 
                                 buildings_df: pd.DataFrame = None) -> Dict:
        """Analyse détaillée de la consommation"""
        try:
            # Calcul de statistiques avancées
            consumption_stats = self._calculate_consumption_statistics(consumption_df)
            
            # Analyse temporelle
            temporal_analysis = self._analyze_temporal_patterns(consumption_df)
            
            # Corrélation avec les bâtiments si disponible
            building_correlation = ""
            if buildings_df is not None:
                building_correlation = self._analyze_building_consumption_correlation(
                    consumption_df, buildings_df
                )
            
            # Construction du contexte
            analysis_context = f"""
STATISTIQUES DE CONSOMMATION DÉTAILLÉES:
{consumption_stats}

ANALYSE TEMPORELLE:
{temporal_analysis}

{building_correlation}
"""
            
            # Recherche RAG contexte
            rag_context = self.rag_service.search_context(
                "analyse consommation électrique patterns temporels", top_k=3
            )
            
            # Prompt spécialisé consommation
            prompt = self.analysis_templates['consumption'].format(
                analysis_context=analysis_context,
                rag_context=self._format_rag_context(rag_context)
            )
            
            # Analyse LLM
            analysis = self.ollama_service.analyze_data(
                question="Analyse en détail ces patterns de consommation électrique",
                context=rag_context,
                data_summary={'consumption_data': analysis_context}
            )
            
            insights = []
            if analysis.get('success'):
                content = analysis['analysis']['full_response']
                insights = analysis['analysis'].get('insights', [])
                
                # Ajout d'insights calculés
                insights.extend(self._extract_consumption_insights(consumption_df))
                
                return {
                    'type': 'consumption',
                    'content': content,
                    'insights': insights,
                    'statistics': consumption_stats,
                    'confidence': 0.85,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception("Échec analyse consommation")
                
        except Exception as e:
            logger.error(f"Erreur analyse consommation: {e}")
            return {
                'type': 'consumption',
                'content': f"Analyse consommation indisponible: {e}",
                'insights': [],
                'confidence': 0.1,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _analyze_buildings(self, buildings_df: pd.DataFrame) -> Dict:
        """Analyse du patrimoine de bâtiments"""
        try:
            # Statistiques par type
            type_analysis = self._analyze_building_types(buildings_df)
            
            # Analyse géographique
            geo_analysis = self._analyze_geographic_distribution(buildings_df)
            
            # Analyse des surfaces
            surface_analysis = self._analyze_surface_distribution(buildings_df)
            
            buildings_context = f"""
ANALYSE DU PATRIMOINE BÂTIMENTS:

RÉPARTITION PAR TYPE:
{type_analysis}

DISTRIBUTION GÉOGRAPHIQUE:
{geo_analysis}

ANALYSE DES SURFACES:
{surface_analysis}
"""
            
            rag_context = self.rag_service.search_context(
                "analyse bâtiments types patrimoine immobilier", top_k=3
            )
            
            prompt = self.analysis_templates['buildings'].format(
                buildings_context=buildings_context,
                rag_context=self._format_rag_context(rag_context)
            )
            
            analysis = self.ollama_service.analyze_data(
                question="Analyse le patrimoine de bâtiments et ses caractéristiques",
                context=rag_context,
                data_summary={'buildings_data': buildings_context}
            )
            
            if analysis.get('success'):
                return {
                    'type': 'buildings',
                    'content': analysis['analysis']['full_response'],
                    'insights': analysis['analysis'].get('insights', []),
                    'building_statistics': {
                        'types': type_analysis,
                        'geography': geo_analysis,
                        'surfaces': surface_analysis
                    },
                    'confidence': 0.8,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception("Échec analyse bâtiments")
                
        except Exception as e:
            logger.error(f"Erreur analyse bâtiments: {e}")
            return {
                'type': 'buildings',
                'content': f"Analyse bâtiments indisponible: {e}",
                'insights': [],
                'confidence': 0.1,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _detect_anomalies(self, data: Dict) -> Dict:
        """Détection d'anomalies dans les données"""
        try:
            anomalies_found = []
            
            # Anomalies de consommation
            if data.get('consumption') is not None:
                consumption_anomalies = self._detect_consumption_anomalies(
                    data['consumption']
                )
                anomalies_found.extend(consumption_anomalies)
            
            # Anomalies de bâtiments
            if data.get('buildings') is not None:
                building_anomalies = self._detect_building_anomalies(
                    data['buildings']
                )
                anomalies_found.extend(building_anomalies)
            
            # Incohérences entre datasets
            cross_anomalies = self._detect_cross_dataset_anomalies(data)
            anomalies_found.extend(cross_anomalies)
            
            anomalies_context = f"""
ANOMALIES DÉTECTÉES:
Nombre total d'anomalies: {len(anomalies_found)}

DÉTAILS:
""" + "\n".join([f"- {anomaly}" for anomaly in anomalies_found])
            
            # Analyse par LLM des anomalies
            rag_context = self.rag_service.search_context(
                "anomalies données énergétiques validation qualité", top_k=2
            )
            
            analysis = self.ollama_service.analyze_data(
                question="Analyse ces anomalies détectées dans les données",
                context=rag_context,
                data_summary={'anomalies': anomalies_context}
            )
            
            if analysis.get('success'):
                return {
                    'type': 'anomalies',
                    'content': analysis['analysis']['full_response'],
                    'anomalies_list': anomalies_found,
                    'severity': 'low' if len(anomalies_found) < 5 else 'medium' if len(anomalies_found) < 15 else 'high',
                    'confidence': 0.7,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception("Échec analyse anomalies")
                
        except Exception as e:
            logger.error(f"Erreur détection anomalies: {e}")
            return {
                'type': 'anomalies',
                'content': f"Détection anomalies indisponible: {e}",
                'anomalies_list': [],
                'confidence': 0.1,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _generate_recommendations(self, data: Dict, summary: Dict, 
                                       interpretations: Dict) -> Dict:
        """Génère des recommandations stratégiques"""
        try:
            # Compilation des insights de toutes les analyses
            all_insights = []
            for analysis in interpretations.values():
                if isinstance(analysis, dict) and 'insights' in analysis:
                    all_insights.extend(analysis.get('insights', []))
            
            # Contexte pour les recommandations
            recommendations_context = f"""
CONTEXTE POUR RECOMMANDATIONS:

DONNÉES DISPONIBLES:
- {summary.get('total_buildings', 0)} bâtiments analysés
- {summary.get('total_consumption', 0):,.0f} kWh de consommation
- Types: {', '.join(summary.get('building_types', []))}

INSIGHTS DÉTECTÉS:
""" + "\n".join([f"• {insight}" for insight in all_insights[:10]])  # Top 10 insights
            
            rag_context = self.rag_service.search_context(
                "recommandations optimisation énergétique efficacité", top_k=4
            )
            
            analysis = self.ollama_service.analyze_data(
                question="Génère des recommandations stratégiques d'optimisation énergétique",
                context=rag_context,
                data_summary={'context': recommendations_context}
            )
            
            if analysis.get('success'):
                recommendations = self._parse_recommendations(
                    analysis['analysis']['full_response']
                )
                
                return {
                    'type': 'recommendations',
                    'content': analysis['analysis']['full_response'],
                    'recommendations': recommendations,
                    'priority_actions': recommendations[:3],  # Top 3
                    'confidence': 0.75,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception("Échec génération recommandations")
                
        except Exception as e:
            logger.error(f"Erreur génération recommandations: {e}")
            return {
                'type': 'recommendations',
                'content': f"Recommandations indisponibles: {e}",
                'recommendations': [],
                'confidence': 0.1,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _create_executive_summary(self, interpretations: Dict) -> Dict:
        """Crée un résumé exécutif de toutes les analyses"""
        try:
            # Compilation des points clés
            key_points = []
            recommendations = []
            
            for analysis in interpretations.values():
                if isinstance(analysis, dict):
                    # Points clés
                    insights = analysis.get('insights', [])
                    if insights:
                        key_points.extend(insights[:2])  # Top 2 par analyse
                    
                    # Recommandations
                    if analysis.get('type') == 'recommendations':
                        recs = analysis.get('recommendations', [])
                        recommendations.extend(recs[:3])  # Top 3
            
            summary_context = f"""
POINTS CLÉS IDENTIFIÉS:
""" + "\n".join([f"• {point}" for point in key_points[:8]])
            
            summary_context += f"""

RECOMMANDATIONS PRIORITAIRES:
""" + "\n".join([f"• {rec}" for rec in recommendations[:5]])
            
            # Génération du résumé exécutif
            rag_context = self.rag_service.search_context(
                "résumé exécutif synthèse analyse énergétique", top_k=2
            )
            
            analysis = self.ollama_service.analyze_data(
                question="Crée un résumé exécutif concis de cette analyse énergétique",
                context=rag_context,
                data_summary={'summary_context': summary_context}
            )
            
            if analysis.get('success'):
                return {
                    'executive_summary': analysis['analysis']['full_response'],
                    'key_metrics': self._extract_key_metrics(interpretations),
                    'top_insights': key_points[:5],
                    'priority_actions': recommendations[:3],
                    'confidence': 0.8,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception("Échec résumé exécutif")
                
        except Exception as e:
            logger.error(f"Erreur résumé exécutif: {e}")
            return {
                'executive_summary': f"Résumé exécutif indisponible: {e}",
                'key_metrics': {},
                'confidence': 0.1,
                'timestamp': datetime.now().isoformat()
            }
    
    # =========================================================================
    # MÉTHODES UTILITAIRES D'ANALYSE
    # =========================================================================
    
    def _calculate_consumption_statistics(self, consumption_df: pd.DataFrame) -> str:
        """Calcule des statistiques avancées de consommation"""
        try:
            if 'y' not in consumption_df.columns:
                return "Colonne de consommation 'y' manquante"
            
            consumption = consumption_df['y']
            
            stats = f"""
• Consommation totale: {consumption.sum():,.0f} kWh
• Consommation moyenne: {consumption.mean():.1f} kWh
• Médiane: {consumption.median():.1f} kWh
• Écart-type: {consumption.std():.1f} kWh
• Coefficient de variation: {(consumption.std()/consumption.mean()*100):.1f}%
• Minimum: {consumption.min():.1f} kWh
• Maximum: {consumption.max():.1f} kWh
• 95e percentile: {consumption.quantile(0.95):.1f} kWh"""
            
            return stats
            
        except Exception as e:
            return f"Erreur calcul statistiques: {e}"
    
    def _analyze_temporal_patterns(self, consumption_df: pd.DataFrame) -> str:
        """Analyse les patterns temporels"""
        try:
            if 'timestamp' not in consumption_df.columns:
                return "Colonne timestamp manquante"
            
            consumption_df['timestamp'] = pd.to_datetime(consumption_df['timestamp'])
            consumption_df['hour'] = consumption_df['timestamp'].dt.hour
            consumption_df['day_of_week'] = consumption_df['timestamp'].dt.dayofweek
            
            # Patterns horaires
            hourly_avg = consumption_df.groupby('hour')['y'].mean()
            peak_hour = hourly_avg.idxmax()
            low_hour = hourly_avg.idxmin()
            
            # Patterns hebdomadaires
            daily_avg = consumption_df.groupby('day_of_week')['y'].mean()
            peak_day = daily_avg.idxmax()
            low_day = daily_avg.idxmin()
            
            day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            
            patterns = f"""
• Pic horaire: {peak_hour}h ({hourly_avg[peak_hour]:.1f} kWh moyenne)
• Creux horaire: {low_hour}h ({hourly_avg[low_hour]:.1f} kWh moyenne)
• Variation journalière: {((hourly_avg.max() - hourly_avg.min()) / hourly_avg.mean() * 100):.1f}%
• Jour le plus consommateur: {day_names[peak_day]} ({daily_avg[peak_day]:.1f} kWh)
• Jour le moins consommateur: {day_names[low_day]} ({daily_avg[low_day]:.1f} kWh)"""
            
            return patterns
            
        except Exception as e:
            return f"Erreur analyse temporelle: {e}"
    
    def _detect_consumption_anomalies(self, consumption_df: pd.DataFrame) -> List[str]:
        """Détecte les anomalies de consommation"""
        anomalies = []
        
        try:
            if 'y' not in consumption_df.columns:
                return ["Colonne consommation manquante"]
            
            consumption = consumption_df['y']
            
            # Valeurs négatives
            negative_count = (consumption < 0).sum()
            if negative_count > 0:
                anomalies.append(f"{negative_count} valeurs de consommation négatives")
            
            # Valeurs nulles
            zero_count = (consumption == 0).sum()
            if zero_count > len(consumption) * 0.05:  # > 5%
                anomalies.append(f"{zero_count} valeurs nulles ({zero_count/len(consumption)*100:.1f}%)")
            
            # Outliers extrêmes (> 3 écarts-types)
            z_scores = np.abs((consumption - consumption.mean()) / consumption.std())
            extreme_outliers = (z_scores > 3).sum()
            if extreme_outliers > 0:
                anomalies.append(f"{extreme_outliers} valeurs extrêmes (>3σ)")
            
            # Variations brutales (> 10x la moyenne)
            if 'timestamp' in consumption_df.columns:
                consumption_sorted = consumption_df.sort_values('timestamp')
                diffs = consumption_sorted['y'].diff().abs()
                sudden_changes = (diffs > consumption.mean() * 10).sum()
                if sudden_changes > 0:
                    anomalies.append(f"{sudden_changes} variations brutales détectées")
            
        except Exception as e:
            anomalies.append(f"Erreur détection anomalies consommation: {e}")
        
        return anomalies
    
    def _detect_building_anomalies(self, buildings_df: pd.DataFrame) -> List[str]:
        """Détecte les anomalies dans les données de bâtiments"""
        anomalies = []
        
        try:
            # Coordonnées invalides
            if 'latitude' in buildings_df.columns and 'longitude' in buildings_df.columns:
                invalid_coords = buildings_df[
                    (buildings_df['latitude'].isna()) | 
                    (buildings_df['longitude'].isna()) |
                    (buildings_df['latitude'] < 0.5) |
                    (buildings_df['latitude'] > 7.5) |
                    (buildings_df['longitude'] < 99.0) |
                    (buildings_df['longitude'] > 120.0)
                ]
                if len(invalid_coords) > 0:
                    anomalies.append(f"{len(invalid_coords)} bâtiments avec coordonnées invalides")
            
            # Surfaces anormales
            if 'surface_area_m2' in buildings_df.columns:
                surfaces = buildings_df['surface_area_m2']
                
                # Surfaces nulles ou négatives
                invalid_surfaces = (surfaces <= 0).sum()
                if invalid_surfaces > 0:
                    anomalies.append(f"{invalid_surfaces} bâtiments avec surface invalide")
                
                # Surfaces extrêmes
                very_large = (surfaces > 50000).sum()  # > 50,000 m²
                if very_large > 0:
                    anomalies.append(f"{very_large} bâtiments avec surface très importante (>50k m²)")
            
            # Doublons d'IDs
            if 'unique_id' in buildings_df.columns:
                duplicates = buildings_df['unique_id'].duplicated().sum()
                if duplicates > 0:
                    anomalies.append(f"{duplicates} IDs de bâtiments dupliqués")
            
        except Exception as e:
            anomalies.append(f"Erreur détection anomalies bâtiments: {e}")
        
        return anomalies
    
    # =========================================================================
    # TEMPLATES D'ANALYSE
    # =========================================================================
    
    def _get_overview_template(self) -> str:
        return """Tu es un expert en analyse de données énergétiques pour la Malaysia.

DONNÉES À ANALYSER:
{stats_context}

CONTEXTE EXPERT:
{rag_context}

INSTRUCTIONS:
1. Analyse globale de la qualité et completude des données
2. Identification des tendances principales 
3. Points d'attention ou limitations
4. Première évaluation de la performance énergétique
5. Recommandations pour analyses plus poussées

Réponds de manière structurée et accessible, en te concentrant sur les insights les plus importants."""
    
    def _get_consumption_template(self) -> str:
        return """Tu es un analyste spécialisé en consommation énergétique.

ANALYSE DÉTAILLÉE:
{analysis_context}

CONTEXTE EXPERT:
{rag_context}

INSTRUCTIONS:
1. Interprète les patterns de consommation identifiés
2. Évalue l'efficacité énergétique par rapport aux standards
3. Identifie les opportunités d'optimisation
4. Analyse les variations temporelles et leur signification
5. Compare avec les benchmarks industry si disponibles

Fournis une analyse approfondie avec des recommandations concrètes."""
    
    def _get_buildings_template(self) -> str:
        return """Tu es un expert en patrimoine immobilier et efficacité énergétique.

ANALYSE PATRIMOINE:
{buildings_context}

CONTEXTE EXPERT:
{rag_context}

INSTRUCTIONS:
1. Analyse la composition du patrimoine bâtiments
2. Évalue la répartition géographique et ses implications
3. Identifie les typologies dominantes et leurs caractéristiques
4. Analyse la distribution des surfaces et son impact énergétique
5. Propose des stratégies d'optimisation par type/zone

Concentre-toi sur les implications énergétiques et les opportunités d'amélioration."""
    
    def _get_weather_template(self) -> str:
        return """Tu es un spécialiste en corrélations météo-énergétiques.

DONNÉES MÉTÉOROLOGIQUES:
{weather_context}

CONTEXTE EXPERT:
{rag_context}

INSTRUCTIONS:
1. Analyse l'impact des conditions météo sur la consommation
2. Identifie les corrélations significatives
3. Évalue la sensibilité climatique du parc de bâtiments
4. Propose des stratégies d'adaptation climatique
5. Recommande des mesures de résilience énergétique

Focus sur les implications pratiques pour la gestion énergétique."""
    
    def _get_trends_template(self) -> str:
        return """Tu es un analyste en tendances énergétiques.

ANALYSE TEMPORELLE:
{trends_context}

CONTEXTE EXPERT:
{rag_context}

INSTRUCTIONS:
1. Identifie les tendances d'évolution significatives
2. Analyse la saisonnalité et les cycles
3. Détecte les changements de comportement
4. Projette les évolutions futures probables
5. Recommande des actions préventives ou correctives

Privilégie l'analyse prédictive et l'aide à la décision."""
    
    def _get_anomalies_template(self) -> str:
        return """Tu es un expert en détection d'anomalies énergétiques.

ANOMALIES DÉTECTÉES:
{anomalies_context}

CONTEXTE EXPERT:
{rag_context}

INSTRUCTIONS:
1. Interprète la signification des anomalies détectées
2. Évalue leur impact sur la fiabilité des analyses
3. Propose des actions correctives pour les données
4. Identifie les anomalies nécessitant une investigation
5. Recommande des processus de validation améliorés

Focus sur l'amélioration de la qualité des données."""
    
    def _get_recommendations_template(self) -> str:
        return """Tu es un consultant senior en optimisation énergétique.

CONTEXTE GLOBAL:
{recommendations_context}

CONTEXTE EXPERT:
{rag_context}

INSTRUCTIONS:
1. Synthétise les opportunités d'optimisation identifiées
2. Priorise les actions par impact/effort
3. Propose un plan d'action structuré
4. Estime les bénéfices potentiels
5. Identifie les risques et conditions de succès

Fournis des recommandations stratégiques actionnables avec ROI estimé."""
    
    # =========================================================================
    # MÉTHODES UTILITAIRES SUPPLÉMENTAIRES
    # =========================================================================
    
    def _calculate_data_hash(self, data: Dict) -> str:
        """Calcule un hash unique des données pour éviter les re-analyses"""
        import hashlib
        
        hash_components = []
        
        for key, df in data.items():
            if df is not None and hasattr(df, 'shape'):
                # Hash basé sur la forme et quelques valeurs
                hash_components.append(f"{key}:{df.shape}")
                if hasattr(df, 'columns'):
                    hash_components.append(str(list(df.columns)))
        
        combined = "|".join(hash_components)
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _interpretation_exists(self, data_hash: str) -> bool:
        """Vérifie si une interprétation existe déjà pour ce hash"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT id FROM interpretations WHERE data_hash = ? AND created_at > datetime('now', '-24 hours')",
                    (data_hash,)
                )
                return cursor.fetchone() is not None
        except:
            return False
    
    def _get_existing_interpretation(self, data_hash: str) -> Dict:
        """Récupère une interprétation existante"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT interpretation_type, analysis_content, insights, 
                           recommendations, confidence_score, created_at
                    FROM interpretations 
                    WHERE data_hash = ? 
                    ORDER BY created_at DESC
                """, (data_hash,))
                
                rows = cursor.fetchall()
                
                interpretations = {}
                for row in rows:
                    interpretations[row[0]] = {
                        'type': row[0],
                        'content': row[1],
                        'insights': json.loads(row[2]) if row[2] else [],
                        'recommendations': json.loads(row[3]) if row[3] else [],
                        'confidence': row[4],
                        'timestamp': row[5]
                    }
                
                return {
                    'success': True,
                    'interpretations': interpretations,
                    'from_cache': True,
                    'cache_timestamp': rows[0][5] if rows else None
                }
                
        except Exception as e:
            logger.error(f"Erreur récupération cache: {e}")
            return {'success': False, 'error': str(e)}
    
    def _save_interpretation_results(self, data_hash: str, interpretations: Dict):
        """Sauvegarde les résultats d'interprétation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for interp_type, result in interpretations.items():
                    if isinstance(result, dict):
                        conn.execute("""
                            INSERT OR REPLACE INTO interpretations
                            (interpretation_type, data_hash, analysis_content, 
                             insights, recommendations, confidence_score, metadata)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            interp_type,
                            data_hash,
                            result.get('content', ''),
                            json.dumps(result.get('insights', []), ensure_ascii=False),
                            json.dumps(result.get('recommendations', []), ensure_ascii=False),
                            result.get('confidence', 0.5),
                            json.dumps(result.get('metadata', {}), ensure_ascii=False)
                        ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Erreur sauvegarde interprétations: {e}")
    
    def _format_rag_context(self, rag_context: List[Dict]) -> str:
        """Formate le contexte RAG pour les prompts"""
        if not rag_context:
            return "Aucun contexte expert spécifique trouvé."
        
        formatted = "CONNAISSANCES EXPERTES PERTINENTES:\n"
        for i, item in enumerate(rag_context[:3], 1):
            content = item.get('content', '')[:300]  # Limiter à 300 chars
            formatted += f"{i}. {content}...\n"
        
        return formatted
    
    def _extract_consumption_insights(self, consumption_df: pd.DataFrame) -> List[str]:
        """Extrait des insights automatiques de consommation"""
        insights = []
        
        try:
            if 'y' not in consumption_df.columns:
                return insights
            
            consumption = consumption_df['y']
            
            # Insight sur la variabilité
            cv = consumption.std() / consumption.mean() * 100
            if cv > 50:
                insights.append(f"Forte variabilité de consommation ({cv:.1f}% de coefficient de variation)")
            elif cv < 20:
                insights.append(f"Consommation stable ({cv:.1f}% de coefficient de variation)")
            
            # Insight sur la distribution
            skewness = consumption.skew()
            if abs(skewness) > 1:
                direction = "positive" if skewness > 0 else "négative"
                insights.append(f"Distribution asymétrique {direction} des consommations")
            
            # Insight sur les extremes
            q95 = consumption.quantile(0.95)
            q05 = consumption.quantile(0.05)
            ratio = q95 / q05 if q05 > 0 else float('inf')
            
            if ratio > 5:
                insights.append(f"Large écart entre consommations faibles et élevées (ratio 95/5: {ratio:.1f})")
            
        except Exception as e:
            logger.debug(f"Erreur extraction insights: {e}")
        
        return insights
    
    def _analyze_building_types(self, buildings_df: pd.DataFrame) -> str:
        """Analyse la répartition par type de bâtiment"""
        try:
            if 'building_type' not in buildings_df.columns:
                return "Colonne building_type manquante"
            
            type_counts = buildings_df['building_type'].value_counts()
            total = len(buildings_df)
            
            analysis = "RÉPARTITION PAR TYPE:\n"
            for btype, count in type_counts.items():
                percentage = count / total * 100
                analysis += f"• {btype}: {count} bâtiments ({percentage:.1f}%)\n"
            
            # Type dominant
            dominant_type = type_counts.index[0]
            analysis += f"\nType dominant: {dominant_type} ({type_counts.iloc[0]/total*100:.1f}%)"
            
            return analysis
            
        except Exception as e:
            return f"Erreur analyse types: {e}"
    
    def _analyze_geographic_distribution(self, buildings_df: pd.DataFrame) -> str:
        """Analyse la distribution géographique"""
        try:
            analysis = ""
            
            if 'zone_name' in buildings_df.columns:
                zone_counts = buildings_df['zone_name'].value_counts()
                analysis += "RÉPARTITION PAR ZONE:\n"
                for zone, count in zone_counts.head(5).items():
                    percentage = count / len(buildings_df) * 100
                    analysis += f"• {zone}: {count} bâtiments ({percentage:.1f}%)\n"
            
            if 'latitude' in buildings_df.columns and 'longitude' in buildings_df.columns:
                lat_range = buildings_df['latitude'].max() - buildings_df['latitude'].min()
                lng_range = buildings_df['longitude'].max() - buildings_df['longitude'].min()
                
                analysis += f"\nÉTENDUE GÉOGRAPHIQUE:\n"
                analysis += f"• Latitude: {lat_range:.3f}° ({buildings_df['latitude'].min():.3f} à {buildings_df['latitude'].max():.3f})\n"
                analysis += f"• Longitude: {lng_range:.3f}° ({buildings_df['longitude'].min():.3f} à {buildings_df['longitude'].max():.3f})"
            
            return analysis
            
        except Exception as e:
            return f"Erreur analyse géographique: {e}"
    
    def _analyze_surface_distribution(self, buildings_df: pd.DataFrame) -> str:
        """Analyse la distribution des surfaces"""
        try:
            if 'surface_area_m2' not in buildings_df.columns:
                return "Colonne surface_area_m2 manquante"
            
            surfaces = buildings_df['surface_area_m2']
            
            analysis = f"""DISTRIBUTION DES SURFACES:
• Superficie totale: {surfaces.sum():,.0f} m²
• Superficie moyenne: {surfaces.mean():.0f} m²
• Superficie médiane: {surfaces.median():.0f} m²
• Plus grand bâtiment: {surfaces.max():,.0f} m²
• Plus petit bâtiment: {surfaces.min():.0f} m²

RÉPARTITION PAR TAILLE:"""
            
            # Catégories de taille
            small = (surfaces < 200).sum()
            medium = ((surfaces >= 200) & (surfaces < 1000)).sum()
            large = ((surfaces >= 1000) & (surfaces < 5000)).sum()
            very_large = (surfaces >= 5000).sum()
            
            total = len(surfaces)
            analysis += f"""
• Petits (<200 m²): {small} ({small/total*100:.1f}%)
• Moyens (200-1000 m²): {medium} ({medium/total*100:.1f}%)
• Grands (1000-5000 m²): {large} ({large/total*100:.1f}%)
• Très grands (≥5000 m²): {very_large} ({very_large/total*100:.1f}%)"""
            
            return analysis
            
        except Exception as e:
            return f"Erreur analyse surfaces: {e}"
    
    def _detect_cross_dataset_anomalies(self, data: Dict) -> List[str]:
        """Détecte les incohérences entre datasets"""
        anomalies = []
        
        try:
            buildings_df = data.get('buildings')
            consumption_df = data.get('consumption')
            
            if buildings_df is not None and consumption_df is not None:
                # IDs de bâtiments incohérents
                if 'unique_id' in buildings_df.columns and 'unique_id' in consumption_df.columns:
                    building_ids = set(buildings_df['unique_id'].unique())
                    consumption_ids = set(consumption_df['unique_id'].unique())
                    
                    missing_in_consumption = building_ids - consumption_ids
                    missing_in_buildings = consumption_ids - building_ids
                    
                    if missing_in_consumption:
                        anomalies.append(f"{len(missing_in_consumption)} bâtiments sans données de consommation")
                    
                    if missing_in_buildings:
                        anomalies.append(f"{len(missing_in_buildings)} consommations sans bâtiment correspondant")
            
        except Exception as e:
            anomalies.append(f"Erreur vérification cohérence: {e}")
        
        return anomalies
    
    def _parse_recommendations(self, llm_response: str) -> List[str]:
        """Parse les recommandations de la réponse LLM"""
        recommendations = []
        
        try:
            lines = llm_response.split('\n')
            current_rec = ""
            
            for line in lines:
                line = line.strip()
                
                # Détection d'une nouvelle recommandation
                if (line.startswith('•') or line.startswith('-') or 
                    line.startswith('*') or any(word in line.lower() for word in 
                    ['recommande', 'suggère', 'devrait', 'pourrait', 'optimiser'])):
                    
                    if current_rec:
                        recommendations.append(current_rec.strip())
                    
                    current_rec = line.lstrip('•-* ')
                elif current_rec and line:
                    current_rec += " " + line
            
            # Ajouter la dernière recommandation
            if current_rec:
                recommendations.append(current_rec.strip())
        
        except Exception as e:
            logger.debug(f"Erreur parsing recommandations: {e}")
        
        return recommendations[:10]  # Limiter à 10 recommandations
    
    def _extract_key_metrics(self, interpretations: Dict) -> Dict:
        """Extrait les métriques clés de toutes les analyses"""
        metrics = {}
        
        try:
            for analysis_type, analysis in interpretations.items():
                if isinstance(analysis, dict):
                    confidence = analysis.get('confidence', 0)
                    
                    # Métriques par type d'analyse
                    if analysis_type == 'consumption':
                        stats = analysis.get('statistics', '')
                        # Extraire les valeurs numériques des stats
                        # (implémentation simplifiée)
                        metrics['consumption_confidence'] = confidence
                    
                    elif analysis_type == 'buildings':
                        building_stats = analysis.get('building_statistics', {})
                        metrics['buildings_confidence'] = confidence
                    
                    elif analysis_type == 'anomalies':
                        anomalies_list = analysis.get('anomalies_list', [])
                        metrics['anomalies_count'] = len(anomalies_list)
                        metrics['data_quality_score'] = max(0, 100 - len(anomalies_list) * 5)
            
            # Score global de confiance
            confidences = [a.get('confidence', 0) for a in interpretations.values() 
                          if isinstance(a, dict)]
            if confidences:
                metrics['overall_confidence'] = sum(confidences) / len(confidences)
        
        except Exception as e:
            logger.debug(f"Erreur extraction métriques: {e}")
        
        return metrics
    
    def _calculate_overall_confidence(self, interpretations: Dict) -> float:
        """Calcule le score de confiance global"""
        try:
            confidences = []
            
            for analysis in interpretations.values():
                if isinstance(analysis, dict) and 'confidence' in analysis:
                    confidences.append(analysis['confidence'])
            
            if confidences:
                return sum(confidences) / len(confidences)
            else:
                return 0.5
                
        except:
            return 0.5
    
    def _generate_fallback_analysis(self, data_summary: Dict) -> str:
        """Génère une analyse de secours si le LLM échoue"""
        fallback = f"""
ANALYSE AUTOMATIQUE DE SECOURS

Résumé des données chargées:
• {data_summary.get('total_buildings', 0)} bâtiments
• {data_summary.get('total_consumption', 0):,.0f} kWh de consommation totale  
• Types: {', '.join(data_summary.get('building_types', []))}
• Zones: {', '.join(data_summary.get('zones', []))}

Points d'attention:
• Vérifiez la qualité des données chargées
• Assurez-vous que tous les fichiers nécessaires sont présents
• Consultez les logs pour identifier les problèmes éventuels

Cette analyse simplifiée est générée car le service d'IA n'est pas disponible.
Relancez l'analyse une fois Ollama connecté.
"""
        return fallback
    
    # =========================================================================
    # MÉTHODES PUBLIQUES ADDITIONNELLES
    # =========================================================================
    
    def get_interpretation_history(self, limit: int = 10) -> List[Dict]:
        """Récupère l'historique des interprétations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT interpretation_type, created_at, confidence_score,
                           substr(analysis_content, 1, 200) as preview
                    FROM interpretations
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'type': row[0],
                        'timestamp': row[1],
                        'confidence': row[2],
                        'preview': row[3] + "..." if len(row[3]) == 200 else row[3]
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Erreur récupération historique: {e}")
            return []
    
    def get_interpretation_stats(self) -> Dict:
        """Statistiques des interprétations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Nombre total
                cursor = conn.execute("SELECT COUNT(*) FROM interpretations")
                total = cursor.fetchone()[0]
                
                # Par type
                cursor = conn.execute("""
                    SELECT interpretation_type, COUNT(*), AVG(confidence_score)
                    FROM interpretations
                    GROUP BY interpretation_type
                """)
                by_type = cursor.fetchall()
                
                # Dernières 24h
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM interpretations
                    WHERE created_at > datetime('now', '-24 hours')
                """)
                recent = cursor.fetchone()[0]
                
                return {
                    'total_interpretations': total,
                    'recent_24h': recent,
                    'by_type': {
                        row[0]: {
                            'count': row[1],
                            'avg_confidence': round(row[2], 2)
                        } for row in by_type
                    }
                }
                
        except Exception as e:
            logger.error(f"Erreur stats interprétations: {e}")
            return {}
    
    def clear_old_interpretations(self, days_old: int = 30) -> int:
        """Supprime les anciennes interprétations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM interpretations 
                    WHERE created_at < datetime('now', '-{} days')
                """.format(days_old))
                
                deleted = cursor.rowcount
                conn.commit()
                
                logger.info(f"🗑️ {deleted} anciennes interprétations supprimées")
                return deleted
                
        except Exception as e:
            logger.error(f"Erreur nettoyage interprétations: {e}")
            return 0


# ==============================================================================
# INTÉGRATION AVEC L'APPLICATION PRINCIPALE
# ==============================================================================

def create_interpreter_api_routes(app, data_interpreter):
    """Crée les routes API pour l'interpréteur de données"""
    
    @app.route('/api/interpret/analyze', methods=['POST'])
    def interpret_data():
        """Lance l'interprétation des données"""
        try:
            from flask import request, jsonify
            
            data = request.get_json() or {}
            force_refresh = data.get('force_refresh', False)
            
            # Lancement asynchrone (simulation)
            import asyncio
            result = asyncio.run(data_interpreter.interpret_loaded_data(force_refresh))
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/interpret/history')
    def interpretation_history():
        """Historique des interprétations"""
        try:
            from flask import request, jsonify
            
            limit = int(request.args.get('limit', 10))
            history = data_interpreter.get_interpretation_history(limit)
            
            return jsonify({'success': True, 'history': history})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/interpret/stats')
    def interpretation_stats():
        """Statistiques des interprétations"""
        try:
            from flask import jsonify
            
            stats = data_interpreter.get_interpretation_stats()
            return jsonify({'success': True, 'stats': stats})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


# ==============================================================================
# TEST ET UTILISATION
# ==============================================================================

def test_data_interpreter():
    """Test de l'interpréteur de données"""
    
    # Simulation des services requis
    class MockOllamaService:
        def analyze_data(self, question, context, data_summary):
            return {
                'success': True,
                'analysis': {
                    'full_response': f"Analyse simulée pour: {question}",
                    'insights': ["Insight 1", "Insight 2"]
                }
            }
    
    class MockRAGService:
        def search_context(self, query, top_k=5):
            return [
                {'content': f"Contexte simulé pour {query}", 'relevance_score': 0.8}
            ]
    
    class MockDataService:
        def get_current_data(self):
            return {
                'buildings': pd.DataFrame({
                    'unique_id': ['B1', 'B2'],
                    'building_type': ['residential', 'commercial'],
                    'surface_area_m2': [100, 500]
                }),
                'consumption': pd.DataFrame({
                    'unique_id': ['B1', 'B1', 'B2'],
                    'timestamp': pd.date_range('2024-01-01', periods=3, freq='H'),
                    'y': [10, 12, 25]
                })
            }
        
        def get_data_summary(self):
            return {
                'total_buildings': 2,
                'total_consumption': 47,
                'building_types': ['residential', 'commercial'],
                'period': '2024-01-01 à 2024-01-02'
            }
    
    # Test
    interpreter = DataInterpreter(
        MockOllamaService(),
        MockRAGService(), 
        MockDataService()
    )
    
    print("🧪 Test DataInterpreter:")
    
    # Test interprétation
    import asyncio
    result = asyncio.run(interpreter.interpret_loaded_data())
    
    print(f"✅ Interprétation: {result.get('success', False)}")
    if result.get('success'):
        print(f"📊 Analyses: {list(result.get('interpretations', {}).keys())}")
        print(f"📋 Résumé exécutif disponible: {'executive_summary' in result}")
        print(f"🎯 Confiance globale: {result.get('confidence_score', 0):.2f}")
    
    # Test historique
    history = interpreter.get_interpretation_history()
    print(f"📚 Historique: {len(history)} interprétations")
    
    # Test statistiques
    stats = interpreter.get_interpretation_stats()
    print(f"📈 Stats: {stats.get('total_interpretations', 0)} interprétations totales")
    
    return interpreter


if __name__ == '__main__':
    test_data_interpreter()