#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AMÉLIORATIONS RAG SERVICE - DASHBOARD MALAYSIA
=============================================

Extensions du service RAG pour supporter l'alimentation
par documents et améliorer la recherche de contexte

Version: 1.0.0
"""

import logging
import sqlite3
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class EnhancedRAGService:
    """Service RAG amélioré avec support des documents"""
    
    def __init__(self, db_path: str = "data/rag_knowledge.db"):
        """Initialise le service RAG amélioré"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Héritage du service RAG de base
        from dashboard.services.rag_service import RAGService
        self.base_rag = RAGService(str(db_path))
        
        # Extensions pour les documents
        self._init_document_extensions()
        
        logger.info("✅ Enhanced RAG Service initialisé")
    
    def _init_document_extensions(self):
        """Initialise les extensions pour les documents"""
        with sqlite3.connect(self.db_path) as conn:
            # Table pour les sources de documents
            conn.execute("""
                CREATE TABLE IF NOT EXISTS document_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT UNIQUE,
                    source_type TEXT,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_chunks INTEGER DEFAULT 0,
                    metadata TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Table pour le mapping chunks -> sources
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chunk_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    knowledge_item_id INTEGER,
                    source_id INTEGER,
                    chunk_index INTEGER,
                    relevance_score REAL DEFAULT 1.0,
                    FOREIGN KEY (source_id) REFERENCES document_sources (id)
                )
            """)
            
            # Index pour optimiser les recherches
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunk_sources_knowledge 
                ON chunk_sources(knowledge_item_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunk_sources_source 
                ON chunk_sources(source_id)
            """)
            
            conn.commit()
    
    def add_document_source(self, source_name: str, source_type: str, 
                          metadata: Dict = None) -> int:
        """
        Enregistre une nouvelle source de document
        
        Args:
            source_name: Nom du document source
            source_type: Type (pdf, docx, txt, etc.)
            metadata: Métadonnées additionnelles
            
        Returns:
            int: ID de la source créée
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT OR REPLACE INTO document_sources 
                    (source_name, source_type, metadata)
                    VALUES (?, ?, ?)
                """, (
                    source_name,
                    source_type,
                    json.dumps(metadata or {}, ensure_ascii=False)
                ))
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"Erreur ajout source document: {e}")
            return 0
    
    def add_knowledge_item_with_source(self, content: str, metadata: Dict = None, 
                                     source_name: str = None, chunk_index: int = 0) -> bool:
        """
        Ajoute un item de connaissance en liant à une source
        
        Args:
            content: Contenu textuel
            metadata: Métadonnées
            source_name: Nom du document source
            chunk_index: Index du chunk dans le document
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            # Ajout dans le RAG de base
            self.base_rag.add_knowledge_item(content, metadata)
            
            # Liaison avec la source si spécifiée
            if source_name:
                # Récupération de l'ID de la source
                source_id = self._get_or_create_source_id(source_name, metadata)
                
                if source_id:
                    # Récupération de l'ID du knowledge item (approximatif)
                    knowledge_item_id = self._get_latest_knowledge_item_id()
                    
                    # Liaison chunk <-> source
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            INSERT INTO chunk_sources 
                            (knowledge_item_id, source_id, chunk_index)
                            VALUES (?, ?, ?)
                        """, (knowledge_item_id, source_id, chunk_index))
                        
                        # Mise à jour du compteur de chunks
                        conn.execute("""
                            UPDATE document_sources 
                            SET total_chunks = total_chunks + 1
                            WHERE id = ?
                        """, (source_id,))
                        
                        conn.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur ajout knowledge item avec source: {e}")
            return False
    
    def search_context_with_sources(self, query: str, top_k: int = 5, 
                                  source_types: List[str] = None) -> List[Dict]:
        """
        Recherche de contexte avec informations sur les sources
        
        Args:
            query: Requête de recherche
            top_k: Nombre de résultats
            source_types: Types de sources à privilégier
            
        Returns:
            List[Dict]: Items avec informations de source
        """
        try:
            # Recherche de base
            base_results = self.base_rag.search_context(query, top_k * 2)
            
            # Enrichissement avec les informations de source
            enriched_results = []
            
            for result in base_results:
                # Tentative de récupération de la source
                source_info = self._get_source_info_for_content(result['content'])
                
                # Application du filtre par type de source
                if source_types and source_info and source_info.get('source_type') not in source_types:
                    continue
                
                # Enrichissement du résultat
                enriched_result = result.copy()
                if source_info:
                    enriched_result.update({
                        'source_name': source_info.get('source_name'),
                        'source_type': source_info.get('source_type'),
                        'chunk_index': source_info.get('chunk_index'),
                        'source_metadata': source_info.get('source_metadata', {})
                    })
                
                enriched_results.append(enriched_result)
                
                if len(enriched_results) >= top_k:
                    break
            
            return enriched_results
            
        except Exception as e:
            logger.error(f"Erreur recherche contexte avec sources: {e}")
            return []
    
    def get_sources_statistics(self) -> Dict:
        """Statistiques des sources de documents"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Statistiques générales
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_sources,
                        SUM(total_chunks) as total_chunks,
                        AVG(total_chunks) as avg_chunks_per_source
                    FROM document_sources 
                    WHERE is_active = 1
                """)
                general_stats = cursor.fetchone()
                
                # Par type de source
                cursor = conn.execute("""
                    SELECT 
                        source_type,
                        COUNT(*) as count,
                        SUM(total_chunks) as chunks,
                        AVG(total_chunks) as avg_chunks
                    FROM document_sources 
                    WHERE is_active = 1
                    GROUP BY source_type
                """)
                type_stats = cursor.fetchall()
                
                # Sources les plus contributives
                cursor = conn.execute("""
                    SELECT source_name, source_type, total_chunks
                    FROM document_sources 
                    WHERE is_active = 1
                    ORDER BY total_chunks DESC
                    LIMIT 10
                """)
                top_sources = cursor.fetchall()
                
                return {
                    'total_sources': general_stats[0] or 0,
                    'total_chunks': general_stats[1] or 0,
                    'avg_chunks_per_source': round(general_stats[2] or 0, 1),
                    'by_type': {
                        row[0]: {
                            'count': row[1],
                            'chunks': row[2],
                            'avg_chunks': round(row[3], 1)
                        } for row in type_stats
                    },
                    'top_sources': [
                        {
                            'name': row[0],
                            'type': row[1],
                            'chunks': row[2]
                        } for row in top_sources
                    ]
                }
                
        except Exception as e:
            logger.error(f"Erreur statistiques sources: {e}")
            return {}
    
    def remove_source_and_chunks(self, source_name: str) -> bool:
        """
        Supprime une source et tous ses chunks associés
        
        Args:
            source_name: Nom de la source à supprimer
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Récupération de l'ID de la source
                cursor = conn.execute(
                    "SELECT id FROM document_sources WHERE source_name = ?",
                    (source_name,)
                )
                source_row = cursor.fetchone()
                
                if not source_row:
                    logger.warning(f"Source non trouvée: {source_name}")
                    return False
                
                source_id = source_row[0]
                
                # Récupération des IDs des knowledge items à supprimer
                cursor = conn.execute("""
                    SELECT knowledge_item_id FROM chunk_sources 
                    WHERE source_id = ?
                """, (source_id,))
                
                knowledge_item_ids = [row[0] for row in cursor.fetchall()]
                
                # Suppression des chunks dans la table principale RAG
                # Note: Ceci nécessiterait une méthode dans le RAG de base
                # Pour l'instant, on marque comme inactif
                
                # Suppression des liaisons
                conn.execute("DELETE FROM chunk_sources WHERE source_id = ?", (source_id,))
                
                # Marquer la source comme inactive
                conn.execute(
                    "UPDATE document_sources SET is_active = 0 WHERE id = ?",
                    (source_id,)
                )
                
                conn.commit()
                
                logger.info(f"✅ Source supprimée: {source_name} ({len(knowledge_item_ids)} chunks)")
                return True
                
        except Exception as e:
            logger.error(f"Erreur suppression source: {e}")
            return False
    
    def rebuild_source_index(self) -> bool:
        """Reconstruit l'index des sources à partir du contenu RAG"""
        try:
            logger.info("🔄 Reconstruction de l'index des sources...")
            
            # Récupération de tous les knowledge items avec métadonnées source
            knowledge_items = self.base_rag.knowledge_items
            
            # Nettoyage des anciennes liaisons
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM chunk_sources")
                conn.execute("UPDATE document_sources SET total_chunks = 0")
                
                # Reconstruction
                for i, item in enumerate(knowledge_items):
                    metadata = item.get('metadata', {})
                    source_document = metadata.get('source_document')
                    
                    if source_document:
                        # Récupération ou création de la source
                        source_id = self._get_or_create_source_id(source_document, metadata)
                        
                        if source_id:
                            chunk_index = metadata.get('chunk_index', 0)
                            
                            # Ajout de la liaison
                            conn.execute("""
                                INSERT INTO chunk_sources 
                                (knowledge_item_id, source_id, chunk_index)
                                VALUES (?, ?, ?)
                            """, (i, source_id, chunk_index))
                            
                            # Mise à jour du compteur
                            conn.execute("""
                                UPDATE document_sources 
                                SET total_chunks = total_chunks + 1
                                WHERE id = ?
                            """, (source_id,))
                
                conn.commit()
            
            logger.info("✅ Index des sources reconstruit")
            return True
            
        except Exception as e:
            logger.error(f"Erreur reconstruction index: {e}")
            return False
    
    def get_context_with_citations(self, query: str, top_k: int = 5) -> Dict:
        """
        Recherche de contexte avec citations complètes des sources
        
        Args:
            query: Requête de recherche
            top_k: Nombre de résultats
            
        Returns:
            Dict: Contexte avec citations formatées
        """
        try:
            # Recherche enrichie
            results = self.search_context_with_sources(query, top_k)
            
            if not results:
                return {
                    'context_items': [],
                    'sources_used': [],
                    'citations': [],
                    'formatted_context': "Aucun contexte pertinent trouvé."
                }
            
            # Regroupement par source
            sources_used = {}
            context_items = []
            
            for result in results:
                source_name = result.get('source_name', 'Source inconnue')
                source_type = result.get('source_type', 'unknown')
                
                if source_name not in sources_used:
                    sources_used[source_name] = {
                        'type': source_type,
                        'chunks': [],
                        'total_relevance': 0
                    }
                
                sources_used[source_name]['chunks'].append(result)
                sources_used[source_name]['total_relevance'] += result.get('relevance_score', 0)
                
                context_items.append(result)
            
            # Génération des citations
            citations = []
            formatted_context = ""
            
            for i, (source_name, source_info) in enumerate(sources_used.items(), 1):
                # Citation bibliographique
                citation = f"[{i}] {source_name}"
                if source_info['type'] != 'unknown':
                    citation += f" ({source_info['type'].upper()})"
                citations.append(citation)
                
                # Contexte formaté avec références
                for chunk in source_info['chunks']:
                    chunk_text = chunk['content']
                    if len(chunk_text) > 300:
                        chunk_text = chunk_text[:300] + "..."
                    
                    formatted_context += f"\n[Réf. {i}] {chunk_text}\n"
            
            return {
                'context_items': context_items,
                'sources_used': list(sources_used.keys()),
                'citations': citations,
                'formatted_context': formatted_context.strip(),
                'total_sources': len(sources_used),
                'total_chunks': len(context_items)
            }
            
        except Exception as e:
            logger.error(f"Erreur contexte avec citations: {e}")
            return {
                'context_items': [],
                'sources_used': [],
                'citations': [],
                'formatted_context': f"Erreur récupération contexte: {e}"
            }
    
    def export_knowledge_base(self, output_file: str = "knowledge_export.json") -> bool:
        """
        Exporte la base de connaissances complète
        
        Args:
            output_file: Fichier de sortie
            
        Returns:
            bool: Succès de l'export
        """
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'knowledge_items': [],
                'sources': [],
                'statistics': self.get_sources_statistics()
            }
            
            # Export des knowledge items
            for item in self.base_rag.knowledge_items:
                export_data['knowledge_items'].append({
                    'content': item['content'],
                    'metadata': item['metadata']
                })
            
            # Export des sources
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT source_name, source_type, total_chunks, metadata
                    FROM document_sources WHERE is_active = 1
                """)
                
                for row in cursor.fetchall():
                    export_data['sources'].append({
                        'name': row[0],
                        'type': row[1],
                        'chunks': row[2],
                        'metadata': json.loads(row[3]) if row[3] else {}
                    })
            
            # Sauvegarde
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Base de connaissances exportée: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur export base: {e}")
            return False
    
    def import_knowledge_base(self, import_file: str) -> bool:
        """
        Importe une base de connaissances
        
        Args:
            import_file: Fichier à importer
            
        Returns:
            bool: Succès de l'import
        """
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Import des sources
            sources_map = {}
            for source in import_data.get('sources', []):
                source_id = self.add_document_source(
                    source['name'],
                    source['type'],
                    source.get('metadata', {})
                )
                sources_map[source['name']] = source_id
            
            # Import des knowledge items
            imported_count = 0
            for item in import_data.get('knowledge_items', []):
                source_name = item.get('metadata', {}).get('source_document')
                
                success = self.add_knowledge_item_with_source(
                    item['content'],
                    item['metadata'],
                    source_name
                )
                
                if success:
                    imported_count += 1
            
            logger.info(f"✅ Base importée: {imported_count} items, {len(sources_map)} sources")
            return True
            
        except Exception as e:
            logger.error(f"Erreur import base: {e}")
            return False
    
    def _get_or_create_source_id(self, source_name: str, metadata: Dict = None) -> int:
        """Récupère ou crée l'ID d'une source"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Tentative de récupération
                cursor = conn.execute(
                    "SELECT id FROM document_sources WHERE source_name = ?",
                    (source_name,)
                )
                row = cursor.fetchone()
                
                if row:
                    return row[0]
                
                # Création si inexistant
                source_type = 'unknown'
                if metadata:
                    source_type = metadata.get('document_type', 'unknown')
                
                cursor = conn.execute("""
                    INSERT INTO document_sources (source_name, source_type, metadata)
                    VALUES (?, ?, ?)
                """, (
                    source_name,
                    source_type,
                    json.dumps(metadata or {}, ensure_ascii=False)
                ))
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"Erreur get/create source ID: {e}")
            return 0
    
    def _get_latest_knowledge_item_id(self) -> int:
        """Récupère l'ID du dernier knowledge item (approximatif)"""
        # Cette méthode est une approximation
        # Dans un vrai système, il faudrait un ID réel retourné par add_knowledge_item
        return len(self.base_rag.knowledge_items) - 1
    
    def _get_source_info_for_content(self, content: str) -> Optional[Dict]:
        """Récupère les informations de source pour un contenu donné"""
        try:
            # Hash du contenu pour la recherche
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        ds.source_name,
                        ds.source_type,
                        ds.metadata,
                        cs.chunk_index
                    FROM document_sources ds
                    JOIN chunk_sources cs ON ds.id = cs.source_id
                    JOIN knowledge_items ki ON cs.knowledge_item_id = ki.id
                    WHERE ki.content_hash = ?
                    LIMIT 1
                """, (content_hash,))
                
                row = cursor.fetchone()
                
                if row:
                    return {
                        'source_name': row[0],
                        'source_type': row[1],
                        'source_metadata': json.loads(row[2]) if row[2] else {},
                        'chunk_index': row[3]
                    }
                
        except Exception as e:
            logger.debug(f"Info source non trouvée pour le contenu: {e}")
        
        return None
    
    def health_check(self) -> Dict:
        """Vérification de santé du service RAG amélioré"""
        try:
            health = {
                'status': 'healthy',
                'base_rag_health': 'unknown',
                'database_accessible': False,
                'sources_count': 0,
                'knowledge_items_count': 0,
                'issues': []
            }
            
            # Vérification base RAG
            try:
                base_stats = self.base_rag.get_knowledge_stats()
                health['base_rag_health'] = 'healthy'
                health['knowledge_items_count'] = base_stats.get('total_items', 0)
            except Exception as e:
                health['base_rag_health'] = 'error'
                health['issues'].append(f"Base RAG: {e}")
            
            # Vérification base de données
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM document_sources WHERE is_active = 1")
                    health['sources_count'] = cursor.fetchone()[0]
                    health['database_accessible'] = True
            except Exception as e:
                health['issues'].append(f"Database: {e}")
            
            # Détermination du statut global
            if health['issues']:
                health['status'] = 'warning' if len(health['issues']) < 3 else 'error'
            
            return health
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# ==============================================================================
# INTÉGRATION AVEC LE DOCUMENT PROCESSOR
# ==============================================================================

def integrate_document_processor_with_enhanced_rag():
    """
    Modifie le DocumentProcessor pour utiliser le RAG amélioré
    
    Cette fonction montre comment adapter le DocumentProcessor existant
    """
    
    # Exemple d'utilisation dans DocumentProcessor
    enhanced_rag_example = """
    
    # Dans DocumentProcessor.__init__():
    from rag_enhancements import EnhancedRAGService
    self.enhanced_rag = EnhancedRAGService()
    
    # Dans process_single_document():
    # Remplacer:
    # self.rag_service.add_knowledge_item(content, metadata)
    
    # Par:
    self.enhanced_rag.add_knowledge_item_with_source(
        content=chunk,
        metadata=chunk_metadata,
        source_name=file_path.name,
        chunk_index=i
    )
    
    """
    
    return enhanced_rag_example


# ==============================================================================
# API ROUTES POUR L'INTERFACE WEB
# ==============================================================================

def create_enhanced_rag_api_routes(app, enhanced_rag_service):
    """Crée les routes API pour le RAG amélioré"""
    
    @app.route('/api/rag/sources/stats')
    def rag_sources_stats():
        """Statistiques des sources RAG"""
        try:
            stats = enhanced_rag_service.get_sources_statistics()
            return jsonify({'success': True, 'stats': stats})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/rag/search-with-sources', methods=['POST'])
    def search_with_sources():
        """Recherche avec informations de sources"""
        try:
            data = request.get_json()
            query = data.get('query', '')
            top_k = data.get('top_k', 5)
            source_types = data.get('source_types', None)
            
            results = enhanced_rag_service.search_context_with_sources(
                query, top_k, source_types
            )
            
            return jsonify({
                'success': True,
                'results': results,
                'query': query
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/rag/context-with-citations', methods=['POST'])
    def context_with_citations():
        """Contexte avec citations complètes"""
        try:
            data = request.get_json()
            query = data.get('query', '')
            top_k = data.get('top_k', 5)
            
            context = enhanced_rag_service.get_context_with_citations(query, top_k)
            
            return jsonify({
                'success': True,
                'context': context,
                'query': query
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/rag/export', methods=['POST'])
    def export_knowledge_base():
        """Export de la base de connaissances"""
        try:
            output_file = f"knowledge_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            success = enhanced_rag_service.export_knowledge_base(output_file)
            
            if success:
                return jsonify({
                    'success': True,
                    'export_file': output_file,
                    'message': 'Base de connaissances exportée'
                })
            else:
                return jsonify({'success': False, 'error': 'Échec export'}), 500
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/rag/sources/remove/<source_name>', methods=['DELETE'])
    def remove_source():
        """Supprime une source et ses chunks"""
        try:
            success = enhanced_rag_service.remove_source_and_chunks(source_name)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Source {source_name} supprimée'
                })
            else:
                return jsonify({'success': False, 'error': 'Source non trouvée'}), 404
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/rag/health')
    def rag_health():
        """État de santé du RAG"""
        try:
            health = enhanced_rag_service.health_check()
            return jsonify({'success': True, 'health': health})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


# ==============================================================================
# TESTS ET UTILITAIRES
# ==============================================================================

def test_enhanced_rag_service():
    """Test du service RAG amélioré"""
    
    # Création du service
    enhanced_rag = EnhancedRAGService("test_enhanced_rag.db")
    
    print("🧪 Test Enhanced RAG Service:")
    
    # Test ajout de source
    source_id = enhanced_rag.add_document_source(
        "test_document.pdf",
        "pdf",
        {"title": "Document de test", "author": "Test"}
    )
    print(f"✅ Source ajoutée: ID {source_id}")
    
    # Test ajout de knowledge items avec source
    chunks = [
        "La Malaysia est un pays d'Asie du Sud-Est avec une économie diversifiée.",
        "L'électricité en Malaysia provient principalement du gaz naturel et du charbon.",
        "Les bâtiments résidentiels représentent environ 25% de la consommation électrique."
    ]
    
    for i, chunk in enumerate(chunks):
        success = enhanced_rag.add_knowledge_item_with_source(
            content=chunk,
            metadata={"type": "general_info", "chunk_index": i},
            source_name="test_document.pdf",
            chunk_index=i
        )
        print(f"✅ Chunk {i+1} ajouté: {success}")
    
    # Test recherche avec sources
    results = enhanced_rag.search_context_with_sources(
        "consommation électrique Malaysia",
        top_k=3
    )
    print(f"🔍 Recherche: {len(results)} résultats")
    for result in results:
        print(f"   • Source: {result.get('source_name', 'N/A')}")
        print(f"     Score: {result.get('relevance_score', 0):.3f}")
        print(f"     Contenu: {result['content'][:100]}...")
    
    # Test contexte avec citations
    context = enhanced_rag.get_context_with_citations("Malaysia électricité")
    print(f"📚 Citations: {len(context['citations'])} sources")
    for citation in context['citations']:
        print(f"   {citation}")
    
    # Test statistiques
    stats = enhanced_rag.get_sources_statistics()
    print(f"📊 Statistiques:")
    print(f"   Sources: {stats['total_sources']}")
    print(f"   Chunks: {stats['total_chunks']}")
    print(f"   Par type: {stats['by_type']}")
    
    # Test santé
    health = enhanced_rag.health_check()
    print(f"🏥 Santé: {health['status']}")
    if health.get('issues'):
        print(f"   Issues: {health['issues']}")
    
    return enhanced_rag


if __name__ == '__main__':
    test_enhanced_rag_service()