#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERVICE OLLAMA - INTÉGRATION LLM LOCAL
=====================================

Service pour l'intégration avec Ollama (Mistral) pour l'analyse
intelligente des données de consommation électrique Malaysia

Version: 1.0.0
"""

import json
import logging
import requests
import time
from typing import Dict, List, Optional, Any, Generator
from datetime import datetime

logger = logging.getLogger(__name__)


class OllamaService:
    """Service d'intégration avec Ollama pour l'analyse LLM"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialise le service Ollama
        
        Args:
            base_url: URL de base d'Ollama
        """
        self.base_url = base_url
        self.model = "mistral:latest"
        self.session = requests.Session()
        self.session.timeout = 120
        
        self._check_ollama_availability()
        logger.info("✅ OllamaService initialisé")
    
    def _check_ollama_availability(self):
        """Vérifie la disponibilité d'Ollama"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                if self.model in model_names:
                    logger.info(f"✅ Modèle {self.model} disponible")
                else:
                    logger.warning(f"⚠️ Modèle {self.model} non trouvé")
                    logger.info(f"Modèles disponibles: {model_names}")
            else:
                logger.error("❌ Ollama non accessible")
        except Exception as e:
            logger.error(f"❌ Erreur connexion Ollama: {e}")
    
    def analyze_data(
        self, 
        question: str, 
        context: List[Dict], 
        data_summary: Dict
    ) -> Dict:
        """
        Analyse des données via LLM avec contexte RAG
        
        Args:
            question: Question utilisateur
            context: Contexte RAG
            data_summary: Résumé des données
            
        Returns:
            Dict: Résultat de l'analyse
        """
        try:
            # Construction du prompt intelligent
            prompt = self._build_analysis_prompt(question, context, data_summary)
            
            # Appel au modèle
            response = self._call_ollama(prompt)
            
            # Parsing de la réponse
            analysis = self._parse_analysis_response(response)
            
            return {
                'success': True,
                'analysis': analysis,
                'model_used': self.model,
                'timestamp': datetime.now().isoformat(),
                'prompt_tokens': len(prompt.split()),
                'context_items': len(context)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_analysis': self._generate_fallback_analysis(question, data_summary)
            }
    
    def analyze_data_stream(
        self, 
        question: str, 
        context: List[Dict], 
        data_summary: Dict
    ) -> Generator[Dict, None, None]:
        """
        Analyse en streaming pour réponses temps réel
        
        Args:
            question: Question utilisateur
            context: Contexte RAG
            data_summary: Résumé des données
            
        Yields:
            Dict: Chunks de réponse en streaming
        """
        try:
            prompt = self._build_analysis_prompt(question, context, data_summary)
            
            for chunk in self._call_ollama_stream(prompt):
                yield {
                    'type': 'chunk',
                    'content': chunk,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            yield {
                'type': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _build_analysis_prompt(
        self, 
        question: str, 
        context: List[Dict], 
        data_summary: Dict
    ) -> str:
        """Construit un prompt intelligent pour l'analyse"""
        
        # Template de prompt spécialisé pour l'analyse énergétique
        prompt_template = """Tu es un expert en analyse de données énergétiques pour la Malaisie.

CONTEXTE DES DONNÉES:
- Dataset: Consommation électrique et métadonnées de bâtiments Malaysia
- Période: {period}
- Bâtiments: {buildings_count}
- Types de bâtiments: {building_types}
- Zones géographiques: {zones}

RÉSUMÉ STATISTIQUE:
{data_summary}

CONTEXTE RAG PERTINENT:
{rag_context}

QUESTION DE L'UTILISATEUR:
{question}

INSTRUCTIONS:
1. Analyse les données de manière précise et factuelle
2. Utilise le contexte RAG pour enrichir ta réponse
3. Fournis des insights actionnables
4. Inclus des métriques spécifiques quand possible
5. Suggère des visualisations pertinentes
6. Format ta réponse en sections claires

RÉPONSE STRUCTURÉE:"""

        # Extraction des informations clés
        period = data_summary.get('period', 'Non spécifié')
        buildings_count = data_summary.get('total_buildings', 0)
        building_types = ', '.join(data_summary.get('building_types', []))
        zones = ', '.join(data_summary.get('zones', []))
        
        # Formatage du contexte RAG
        rag_context = "\n".join([
            f"- {item.get('content', '')}" for item in context[:5]
        ]) if context else "Aucun contexte spécifique trouvé"
        
        # Formatage du résumé
        summary_text = json.dumps(data_summary, indent=2, ensure_ascii=False)
        
        return prompt_template.format(
            period=period,
            buildings_count=buildings_count,
            building_types=building_types,
            zones=zones,
            data_summary=summary_text,
            rag_context=rag_context,
            question=question
        )
    
    def _call_ollama(self, prompt: str) -> str:
        """Appel synchrone à Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Réponses plus factuelles
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 2048
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                raise Exception(f"Erreur Ollama: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erreur appel Ollama: {e}")
            raise
    
    def _call_ollama_stream(self, prompt: str) -> Generator[str, None, None]:
        """Appel streaming à Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'response' in chunk:
                            yield chunk['response']
                        if chunk.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.error(f"Erreur streaming Ollama: {e}")
            raise
    
    def _parse_analysis_response(self, response: str) -> Dict:
        """Parse et structure la réponse d'analyse"""
        try:
            # Extraction des sections principales
            sections = {}
            current_section = "overview"
            current_content = []
            
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Détection des sections
                if any(keyword in line.lower() for keyword in [
                    'résumé', 'synthèse', 'insights', 'recommandations', 
                    'métriques', 'tendances', 'conclusions'
                ]):
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    current_section = line.lower().replace(':', '').strip()
                    current_content = []
                else:
                    if line:
                        current_content.append(line)
            
            # Ajout de la dernière section
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            
            # Structure finale
            parsed = {
                'full_response': response,
                'sections': sections,
                'summary': sections.get('overview', response[:200] + '...'),
                'insights': self._extract_insights(response),
                'recommendations': self._extract_recommendations(response),
                'metrics': self._extract_metrics(response)
            }
            
            return parsed
            
        except Exception as e:
            logger.error(f"Erreur parsing réponse: {e}")
            return {
                'full_response': response,
                'sections': {'raw': response},
                'summary': response[:200] + '...',
                'insights': [],
                'recommendations': [],
                'metrics': {}
            }
    
    def _extract_insights(self, response: str) -> List[str]:
        """Extrait les insights clés de la réponse"""
        insights = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            # Recherche de patterns d'insights
            if any(pattern in line.lower() for pattern in [
                'on observe', 'il apparaît', 'les données montrent',
                'tendance', 'pic', 'baisse', 'augmentation'
            ]):
                insights.append(line)
        
        return insights[:5]  # Limiter à 5 insights
    
    def _extract_recommendations(self, response: str) -> List[str]:
        """Extrait les recommandations de la réponse"""
        recommendations = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            # Recherche de patterns de recommandations
            if any(pattern in line.lower() for pattern in [
                'recommande', 'suggère', 'devrait', 'pourrait',
                'optimiser', 'améliorer', 'réduire'
            ]):
                recommendations.append(line)
        
        return recommendations[:3]  # Limiter à 3 recommandations
    
    def _extract_metrics(self, response: str) -> Dict:
        """Extrait les métriques numériques de la réponse"""
        import re
        
        metrics = {}
        
        # Patterns pour extraire des métriques
        number_patterns = [
            r'(\d+(?:\.\d+)?)\s*%',  # Pourcentages
            r'(\d+(?:\.\d+)?)\s*kWh',  # Kilowatt-heures
            r'(\d+(?:\.\d+)?)\s*MW',   # Megawatts
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, response)
            if matches:
                if 'kWh' in pattern:
                    metrics['energy_kwh'] = [float(m) for m in matches]
                elif 'MW' in pattern:
                    metrics['power_mw'] = [float(m) for m in matches]
                elif '%' in pattern:
                    metrics['percentages'] = [float(m) for m in matches]
        
        return metrics
    
    def _generate_fallback_analysis(self, question: str, data_summary: Dict) -> str:
        """Génère une analyse de secours en cas d'erreur LLM"""
        
        fallback = f"""
ANALYSE DE SECOURS - Données Malaysia

Question: {question}

Résumé des données disponibles:
- Bâtiments total: {data_summary.get('total_buildings', 'N/A')}
- Période: {data_summary.get('period', 'N/A')}
- Types de bâtiments: {', '.join(data_summary.get('building_types', []))}

Note: Cette analyse simplifiée est générée en cas d'indisponibilité du modèle LLM.
Pour une analyse complète, vérifiez la connexion à Ollama.
"""
        
        return fallback.strip()
    
    def get_model_info(self) -> Dict:
        """Informations sur le modèle utilisé"""
        try:
            response = self.session.get(f"{self.base_url}/api/show", 
                                      json={"name": self.model})
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Modèle non disponible"}
        except Exception as e:
            return {"error": str(e)}
    
    def health_check(self) -> Dict:
        """Vérification de santé du service"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/tags")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                return {
                    'status': 'healthy',
                    'response_time_ms': round(response_time * 1000, 2),
                    'models_available': len(models),
                    'target_model_available': any(m['name'] == self.model for m in models)
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }


# ==============================================================================
# UTILITAIRES
# ==============================================================================

def test_ollama_connection():
    """Test de connexion à Ollama"""
    service = OllamaService()
    health = service.health_check()
    
    print("🔍 Test connexion Ollama:")
    print(f"Status: {health.get('status')}")
    if health.get('response_time_ms'):
        print(f"Temps de réponse: {health['response_time_ms']}ms")
    if health.get('error'):
        print(f"Erreur: {health['error']}")
    
    return health.get('status') == 'healthy'


if __name__ == '__main__':
    test_ollama_connection()