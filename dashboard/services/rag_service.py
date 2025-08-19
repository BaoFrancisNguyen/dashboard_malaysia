#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERVICE RAG - RETRIEVAL AUGMENTED GENERATION
===========================================

Service RAG pour indexer et rechercher dans les données Malaysia
afin de fournir un contexte intelligent au LLM Ollama

Version: 1.0.0
"""

import json
import logging
import pickle
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import sqlite3

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class RAGService:
    """Service RAG pour la récupération de contexte intelligent"""
    
    def __init__(self, db_path: str = "data/rag_knowledge.db"):
        """
        Initialise le service RAG
        
        Args:
            db_path: Chemin vers la base de données RAG
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Modèles d'embedding
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        
        # Modèle de sentence embeddings (plus précis)
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_sentence_embeddings = True
            logger.info("✅ Sentence Transformers chargé")
        except Exception as e:
            logger.warning(f"⚠️ Sentence Transformers non disponible: {e}")
            self.sentence_model = None
            self.use_sentence_embeddings = False
        
        # Cache des embeddings
        self.embeddings_cache = {}
        self.text_corpus = []
        self.knowledge_items = []
        
        self._init_database()
        self._load_existing_knowledge()
        
        logger.info("✅ RAGService initialisé")
    
    def _init_database(self):
        """Initialise la base de données SQLite pour le RAG"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_hash TEXT UNIQUE,
                    content TEXT,
                    metadata TEXT,
                    embedding_tfidf BLOB,
                    embedding_sentence BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary_type TEXT,
                    content TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_content_hash 
                ON knowledge_items(content_hash)
            """)
            
            conn.commit()
    
    def _load_existing_knowledge(self):
        """Charge la base de connaissances existante"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT content, metadata, embedding_tfidf, embedding_sentence
                    FROM knowledge_items
                    ORDER BY created_at
                """)
                
                items = cursor.fetchall()
                
                self.knowledge_items = []
                self.text_corpus = []
                tfidf_embeddings = []
                sentence_embeddings = []
                
                for content, metadata_json, tfidf_blob, sentence_blob in items:
                    try:
                        metadata = json.loads(metadata_json) if metadata_json else {}
                        
                        self.knowledge_items.append({
                            'content': content,
                            'metadata': metadata
                        })
                        self.text_corpus.append(content)
                        
                        # Chargement des embeddings TF-IDF
                        if tfidf_blob:
                            tfidf_embedding = pickle.loads(tfidf_blob)
                            tfidf_embeddings.append(tfidf_embedding)
                        
                        # Chargement des embeddings de phrases
                        if sentence_blob and self.use_sentence_embeddings:
                            sentence_embedding = pickle.loads(sentence_blob)
                            sentence_embeddings.append(sentence_embedding)
                            
                    except Exception as e:
                        logger.warning(f"Erreur chargement item: {e}")
                
                # Reconstruction des matrices d'embeddings
                if tfidf_embeddings:
                    self.tfidf_matrix = np.vstack(tfidf_embeddings)
                    # Refit du vectorizer avec le corpus existant
                    if self.text_corpus:
                        self.tfidf_vectorizer.fit(self.text_corpus)
                
                if sentence_embeddings and self.use_sentence_embeddings:
                    self.sentence_embeddings = np.vstack(sentence_embeddings)
                
                logger.info(f"✅ {len(self.knowledge_items)} items chargés de la base RAG")
                
        except Exception as e:
            logger.error(f"Erreur chargement base RAG: {e}")
            self.knowledge_items = []
            self.text_corpus = []
    
    def index_current_data(self, data: Dict):
        """
        Indexe les données actuelles dans la base RAG
        
        Args:
            data: Données à indexer (buildings, consumption, etc.)
        """
        try:
            logger.info("🔍 Indexation des données dans RAG...")
            
            knowledge_items = []
            
            # === MÉTADONNÉES BÂTIMENTS ===
            if 'buildings' in data and data['buildings'] is not None:
                buildings_df = data['buildings']
                
                # Résumé par type de bâtiment
                if 'building_type' in buildings_df.columns:
                    type_summary = self._create_building_type_summary(buildings_df)
                    knowledge_items.extend(type_summary)
                
                # Résumé par zone géographique
                if 'zone_name' in buildings_df.columns:
                    zone_summary = self._create_zone_summary(buildings_df)
                    knowledge_items.extend(zone_summary)
                
                # Statistiques de surface
                surface_summary = self._create_surface_summary(buildings_df)
                knowledge_items.extend(surface_summary)
            
            # === DONNÉES DE CONSOMMATION ===
            if 'consumption' in data and data['consumption'] is not None:
                consumption_df = data['consumption']
                
                # Patterns de consommation
                consumption_patterns = self._create_consumption_patterns(consumption_df)
                knowledge_items.extend(consumption_patterns)
                
                # Statistiques temporelles
                temporal_stats = self._create_temporal_statistics(consumption_df)
                knowledge_items.extend(temporal_stats)
            
            # === DONNÉES MÉTÉO ===
            if 'weather' in data and data['weather'] is not None:
                weather_df = data['weather']
                weather_summary = self._create_weather_summary(weather_df)
                knowledge_items.extend(weather_summary)
            
            # === DONNÉES EAU ===
            if 'water' in data and data['water'] is not None:
                water_df = data['water']
                water_summary = self._create_water_summary(water_df)
                knowledge_items.extend(water_summary)
            
            # Indexation des nouveaux items
            for item in knowledge_items:
                self.add_knowledge_item(
                    content=item['content'],
                    metadata=item['metadata']
                )
            
            logger.info(f"✅ {len(knowledge_items)} nouveaux items indexés")
            
        except Exception as e:
            logger.error(f"Erreur indexation données: {e}")
    
    def add_knowledge_item(self, content: str, metadata: Dict = None):
        """
        Ajoute un item à la base de connaissances
        
        Args:
            content: Contenu textuel
            metadata: Métadonnées associées
        """
        try:
            if not content or not content.strip():
                return
            
            metadata = metadata or {}
            content = content.strip()
            
            # Hash du contenu pour éviter les doublons
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Vérification existence
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT id FROM knowledge_items WHERE content_hash = ?",
                    (content_hash,)
                )
                if cursor.fetchone():
                    return  # Item déjà existant
            
            # Génération des embeddings
            tfidf_embedding = None
            sentence_embedding = None
            
            # TF-IDF embedding
            try:
                # Ajout au corpus et re-fit si nécessaire
                if content not in self.text_corpus:
                    self.text_corpus.append(content)
                    
                    # Re-fit du vectorizer avec le nouveau corpus
                    self.tfidf_vectorizer.fit(self.text_corpus)
                    
                    # Recalcul de la matrice complète
                    self.tfidf_matrix = self.tfidf_vectorizer.transform(self.text_corpus)
                
                # Embedding pour le nouvel item
                tfidf_vector = self.tfidf_vectorizer.transform([content])
                tfidf_embedding = tfidf_vector.toarray()[0]
                
            except Exception as e:
                logger.warning(f"Erreur TF-IDF embedding: {e}")
            
            # Sentence embedding
            if self.use_sentence_embeddings and self.sentence_model:
                try:
                    sentence_embedding = self.sentence_model.encode([content])[0]
                except Exception as e:
                    logger.warning(f"Erreur sentence embedding: {e}")
            
            # Sauvegarde en base
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO knowledge_items 
                    (content_hash, content, metadata, embedding_tfidf, embedding_sentence)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    content_hash,
                    content,
                    json.dumps(metadata, ensure_ascii=False),
                    pickle.dumps(tfidf_embedding) if tfidf_embedding is not None else None,
                    pickle.dumps(sentence_embedding) if sentence_embedding is not None else None
                ))
                conn.commit()
            
            # Mise à jour du cache mémoire
            self.knowledge_items.append({
                'content': content,
                'metadata': metadata
            })
            
        except Exception as e:
            logger.error(f"Erreur ajout knowledge item: {e}")
    
    def search_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Recherche de contexte pertinent pour une requête
        
        Args:
            query: Requête de recherche
            top_k: Nombre de résultats à retourner
            
        Returns:
            List[Dict]: Items de contexte pertinents
        """
        try:
            if not self.knowledge_items:
                return []
            
            # Recherche hybride: TF-IDF + Sentence embeddings
            tfidf_scores = self._search_tfidf(query, top_k * 2)
            
            if self.use_sentence_embeddings:
                sentence_scores = self._search_sentence_embeddings(query, top_k * 2)
                # Fusion des scores
                combined_scores = self._combine_search_scores(tfidf_scores, sentence_scores)
            else:
                combined_scores = tfidf_scores
            
            # Sélection des meilleurs résultats
            top_indices = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
            
            results = []
            for idx, score in top_indices:
                if idx < len(self.knowledge_items):
                    item = self.knowledge_items[idx].copy()
                    item['relevance_score'] = float(score)
                    results.append(item)
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur recherche contexte: {e}")
            return []
    
    def _search_tfidf(self, query: str, top_k: int) -> Dict[int, float]:
        """Recherche TF-IDF"""
        try:
            if not hasattr(self, 'tfidf_matrix') or self.tfidf_matrix is None:
                return {}
            
            query_vector = self.tfidf_vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            
            # Indices triés par score
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            return {int(idx): float(similarities[idx]) for idx in top_indices if similarities[idx] > 0.1}
            
        except Exception as e:
            logger.error(f"Erreur recherche TF-IDF: {e}")
            return {}
    
    def _search_sentence_embeddings(self, query: str, top_k: int) -> Dict[int, float]:
        """Recherche par embeddings de phrases"""
        try:
            if not hasattr(self, 'sentence_embeddings') or self.sentence_embeddings is None:
                return {}
            
            query_embedding = self.sentence_model.encode([query])
            similarities = cosine_similarity(query_embedding, self.sentence_embeddings)[0]
            
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            return {int(idx): float(similarities[idx]) for idx in top_indices if similarities[idx] > 0.3}
            
        except Exception as e:
            logger.error(f"Erreur recherche sentence embeddings: {e}")
            return {}
    
    def _combine_search_scores(self, tfidf_scores: Dict, sentence_scores: Dict) -> Dict[int, float]:
        """Combine les scores TF-IDF et sentence embeddings"""
        combined = {}
        all_indices = set(tfidf_scores.keys()) | set(sentence_scores.keys())
        
        for idx in all_indices:
            tfidf_score = tfidf_scores.get(idx, 0)
            sentence_score = sentence_scores.get(idx, 0)
            
            # Pondération: 40% TF-IDF, 60% sentence embeddings
            combined_score = 0.4 * tfidf_score + 0.6 * sentence_score
            combined[idx] = combined_score
        
        return combined
    
    def _create_building_type_summary(self, buildings_df: pd.DataFrame) -> List[Dict]:
        """Crée des résumés par type de bâtiment"""
        summaries = []
        
        try:
            type_stats = buildings_df.groupby('building_type').agg({
                'surface_area_m2': ['count', 'mean', 'sum'],
                'latitude': 'count'
            }).round(2)
            
            for building_type in type_stats.index:
                stats = type_stats.loc[building_type]
                count = stats[('latitude', 'count')]
                avg_surface = stats[('surface_area_m2', 'mean')]
                total_surface = stats[('surface_area_m2', 'sum')]
                
                content = f"""Type de bâtiment: {building_type}
Nombre de bâtiments: {count}
Surface moyenne: {avg_surface} m²
Surface totale: {total_surface} m²
Représente {count/len(buildings_df)*100:.1f}% du total des bâtiments"""
                
                summaries.append({
                    'content': content,
                    'metadata': {
                        'type': 'building_type_summary',
                        'building_type': building_type,
                        'count': int(count),
                        'avg_surface': float(avg_surface),
                        'total_surface': float(total_surface)
                    }
                })
        
        except Exception as e:
            logger.error(f"Erreur création résumé types: {e}")
        
        return summaries
    
    def _create_zone_summary(self, buildings_df: pd.DataFrame) -> List[Dict]:
        """Crée des résumés par zone géographique"""
        summaries = []
        
        try:
            if 'zone_name' in buildings_df.columns:
                zone_stats = buildings_df.groupby('zone_name').agg({
                    'building_type': lambda x: x.value_counts().to_dict(),
                    'surface_area_m2': ['count', 'mean', 'sum'],
                    'latitude': ['mean'],
                    'longitude': ['mean']
                })
                
                for zone in zone_stats.index:
                    stats = zone_stats.loc[zone]
                    count = stats[('surface_area_m2', 'count')]
                    avg_surface = stats[('surface_area_m2', 'mean')]
                    center_lat = stats[('latitude', 'mean')]
                    center_lon = stats[('longitude', 'mean')]
                    
                    content = f"""Zone géographique: {zone}
Nombre de bâtiments: {count}
Surface moyenne: {avg_surface:.1f} m²
Centre géographique: {center_lat:.4f}, {center_lon:.4f}
Densité de bâtiments dans cette zone de Malaysia"""
                    
                    summaries.append({
                        'content': content,
                        'metadata': {
                            'type': 'zone_summary',
                            'zone_name': zone,
                            'count': int(count),
                            'avg_surface': float(avg_surface),
                            'center_coordinates': [float(center_lat), float(center_lon)]
                        }
                    })
        
        except Exception as e:
            logger.error(f"Erreur création résumé zones: {e}")
        
        return summaries
    
    def _create_consumption_patterns(self, consumption_df: pd.DataFrame) -> List[Dict]:
        """Analyse les patterns de consommation"""
        summaries = []
        
        try:
            if 'timestamp' in consumption_df.columns and 'y' in consumption_df.columns:
                # Conversion timestamp
                consumption_df['datetime'] = pd.to_datetime(consumption_df['timestamp'])
                consumption_df['hour'] = consumption_df['datetime'].dt.hour
                consumption_df['day_of_week'] = consumption_df['datetime'].dt.day_name()
                
                # Patterns horaires
                hourly_avg = consumption_df.groupby('hour')['y'].mean()
                peak_hour = hourly_avg.idxmax()
                min_hour = hourly_avg.idxmin()
                
                content = f"""Patterns de consommation électrique:
Pic de consommation: {peak_hour}h ({hourly_avg[peak_hour]:.2f} kWh moyenne)
Minimum de consommation: {min_hour}h ({hourly_avg[min_hour]:.2f} kWh moyenne)
Variation journalière: {hourly_avg.max() - hourly_avg.min():.2f} kWh
Consommation moyenne 24h: {hourly_avg.mean():.2f} kWh"""
                
                summaries.append({
                    'content': content,
                    'metadata': {
                        'type': 'consumption_patterns',
                        'peak_hour': int(peak_hour),
                        'min_hour': int(min_hour),
                        'daily_variation': float(hourly_avg.max() - hourly_avg.min()),
                        'avg_consumption': float(hourly_avg.mean())
                    }
                })
                
                # Patterns hebdomadaires
                weekly_avg = consumption_df.groupby('day_of_week')['y'].mean()
                week_content = f"""Patterns hebdomadaires de consommation:
Jour de plus forte consommation: {weekly_avg.idxmax()} ({weekly_avg.max():.2f} kWh)
Jour de plus faible consommation: {weekly_avg.idxmin()} ({weekly_avg.min():.2f} kWh)
Variation hebdomadaire: {weekly_avg.max() - weekly_avg.min():.2f} kWh"""
                
                summaries.append({
                    'content': week_content,
                    'metadata': {
                        'type': 'weekly_patterns',
                        'peak_day': weekly_avg.idxmax(),
                        'min_day': weekly_avg.idxmin(),
                        'weekly_variation': float(weekly_avg.max() - weekly_avg.min())
                    }
                })
        
        except Exception as e:
            logger.error(f"Erreur patterns consommation: {e}")
        
        return summaries
    
    def _create_surface_summary(self, buildings_df: pd.DataFrame) -> List[Dict]:
        """Statistiques de surface des bâtiments"""
        summaries = []
        
        try:
            if 'surface_area_m2' in buildings_df.columns:
                surfaces = buildings_df['surface_area_m2']
                
                content = f"""Statistiques de surface des bâtiments:
Surface totale: {surfaces.sum():,.0f} m²
Surface moyenne: {surfaces.mean():.1f} m²
Surface médiane: {surfaces.median():.1f} m²
Plus grand bâtiment: {surfaces.max():,.0f} m²
Plus petit bâtiment: {surfaces.min():.0f} m²
Écart-type: {surfaces.std():.1f} m²"""
                
                summaries.append({
                    'content': content,
                    'metadata': {
                        'type': 'surface_statistics',
                        'total_surface': float(surfaces.sum()),
                        'mean_surface': float(surfaces.mean()),
                        'median_surface': float(surfaces.median()),
                        'max_surface': float(surfaces.max()),
                        'min_surface': float(surfaces.min()),
                        'std_surface': float(surfaces.std())
                    }
                })
        
        except Exception as e:
            logger.error(f"Erreur statistiques surface: {e}")
        
        return summaries
    
    def _create_temporal_statistics(self, consumption_df: pd.DataFrame) -> List[Dict]:
        """Statistiques temporelles de consommation"""
        summaries = []
        
        try:
            if 'timestamp' in consumption_df.columns and 'y' in consumption_df.columns:
                start_date = consumption_df['timestamp'].min()
                end_date = consumption_df['timestamp'].max()
                total_points = len(consumption_df)
                
                content = f"""Statistiques temporelles des données:
Période couverte: {start_date} à {end_date}
Points de données: {total_points:,}
Consommation totale: {consumption_df['y'].sum():.2f} kWh
Consommation moyenne: {consumption_df['y'].mean():.2f} kWh
Pic de consommation: {consumption_df['y'].max():.2f} kWh
Consommation minimale: {consumption_df['y'].min():.2f} kWh"""
                
                summaries.append({
                    'content': content,
                    'metadata': {
                        'type': 'temporal_statistics',
                        'start_date': str(start_date),
                        'end_date': str(end_date),
                        'total_points': int(total_points),
                        'total_consumption': float(consumption_df['y'].sum()),
                        'avg_consumption': float(consumption_df['y'].mean()),
                        'max_consumption': float(consumption_df['y'].max()),
                        'min_consumption': float(consumption_df['y'].min())
                    }
                })
        
        except Exception as e:
            logger.error(f"Erreur statistiques temporelles: {e}")
        
        return summaries
    
    def _create_weather_summary(self, weather_df: pd.DataFrame) -> List[Dict]:
        """Résumé des données météorologiques"""
        summaries = []
        
        try:
            # Analyse basique des colonnes météo
            weather_columns = [col for col in weather_df.columns if col not in ['unique_id', 'timestamp']]
            
            content = f"""Données météorologiques disponibles:
Colonnes météo: {len(weather_columns)}
Période: {weather_df['timestamp'].min()} à {weather_df['timestamp'].max()}
Points de données: {len(weather_df):,}
Variables suivies: température, humidité, précipitations, vent, pression"""
            
            summaries.append({
                'content': content,
                'metadata': {
                    'type': 'weather_summary',
                    'columns_count': len(weather_columns),
                    'data_points': int(len(weather_df))
                }
            })
        
        except Exception as e:
            logger.error(f"Erreur résumé météo: {e}")
        
        return summaries
    
    def _create_water_summary(self, water_df: pd.DataFrame) -> List[Dict]:
        """Résumé des données de consommation d'eau"""
        summaries = []
        
        try:
            if 'y' in water_df.columns:
                content = f"""Données de consommation d'eau:
Points de données: {len(water_df):,}
Consommation totale: {water_df['y'].sum():.2f} L
Consommation moyenne: {water_df['y'].mean():.2f} L
Pic de consommation: {water_df['y'].max():.2f} L
Consommation minimale: {water_df['y'].min():.2f} L"""
                
                summaries.append({
                    'content': content,
                    'metadata': {
                        'type': 'water_summary',
                        'data_points': int(len(water_df)),
                        'total_consumption': float(water_df['y'].sum()),
                        'avg_consumption': float(water_df['y'].mean()),
                        'max_consumption': float(water_df['y'].max()),
                        'min_consumption': float(water_df['y'].min())
                    }
                })
        
        except Exception as e:
            logger.error(f"Erreur résumé eau: {e}")
        
        return summaries
    
    def get_knowledge_stats(self) -> Dict:
        """Statistiques de la base de connaissances"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM knowledge_items")
                total_items = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT metadata, COUNT(*) 
                    FROM knowledge_items 
                    GROUP BY json_extract(metadata, '$.type')
                """)
                type_counts = cursor.fetchall()
            
            return {
                'total_items': total_items,
                'type_distribution': dict(type_counts),
                'corpus_size': len(self.text_corpus),
                'embeddings_available': {
                    'tfidf': hasattr(self, 'tfidf_matrix'),
                    'sentence': hasattr(self, 'sentence_embeddings')
                }
            }
        
        except Exception as e:
            logger.error(f"Erreur stats RAG: {e}")
            return {}
    
    def clear_knowledge_base(self):
        """Vide la base de connaissances"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM knowledge_items")
                conn.execute("DELETE FROM data_summaries")
                conn.commit()
            
            self.knowledge_items = []
            self.text_corpus = []
            self.embeddings_cache = {}
            
            logger.info("✅ Base de connaissances vidée")
            
        except Exception as e:
            logger.error(f"Erreur effacement base: {e}")


# ==============================================================================
# TESTS ET UTILITAIRES
# ==============================================================================

def test_rag_service():
    """Test du service RAG"""
    rag = RAGService("test_rag.db")
    
    # Test ajout d'items
    rag.add_knowledge_item(
        "La consommation électrique en Malaysia varie selon les types de bâtiments",
        {"type": "test", "category": "energy"}
    )
    
    rag.add_knowledge_item(
        "Les bâtiments résidentiels consomment en moyenne 150 kWh par mois",
        {"type": "test", "category": "residential"}
    )
    
    # Test recherche
    results = rag.search_context("consommation électrique résidentiel", top_k=2)
    
    print("🔍 Test RAG Service:")
    print(f"Items ajoutés: 2")
    print(f"Résultats recherche: {len(results)}")
    for i, result in enumerate(results):
        print(f"  {i+1}. Score: {result.get('relevance_score', 0):.3f}")
        print(f"     Content: {result['content'][:100]}...")
    
    # Stats
    stats = rag.get_knowledge_stats()
    print(f"Stats: {stats}")


if __name__ == '__main__':
    test_rag_service()