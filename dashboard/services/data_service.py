#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERVICE DE DONNÉES - DASHBOARD MALAYSIA
======================================

Service pour le chargement et la gestion des données
générées par le projet Malaysia original

Version: 1.0.0
"""

import os
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataService:
    """Service de gestion des données pour le dashboard"""
    
    def __init__(self, exports_dir: str = "exports"):
        """
        Initialise le service de données
        
        Args:
            exports_dir: Dossier contenant les exports du projet Malaysia
        """
        self.exports_dir = Path(exports_dir)
        self.exports_dir.mkdir(exist_ok=True)
        
        # Cache des données
        self.data_cache = {
            'buildings': None,
            'consumption': None,
            'weather': None,
            'water': None,
            'last_loaded': None
        }
        
        # Mapping des fichiers attendus
        self.file_mapping = {
            'buildings': 'buildings_metadata.csv',
            'consumption': 'electricity_consumption.csv',
            'weather': 'weather_simulation.csv',
            'water': 'water_consumption.csv'
        }
        
        logger.info("✅ DataService initialisé")
    
    def load_malaysia_data(self) -> Dict:
        """
        Charge toutes les données disponibles du projet Malaysia
        
        Returns:
            Dict: Informations sur les données chargées
        """
        try:
            logger.info("📂 Chargement des données Malaysia...")
            
            loaded_files = {}
            data_info = {
                'success': True,
                'loaded_files': [],
                'failed_files': [],
                'total_records': 0,
                'load_time': datetime.now().isoformat()
            }
            
            # Chargement de chaque type de données
            for data_type, filename in self.file_mapping.items():
                file_path = self.exports_dir / filename
                
                try:
                    if file_path.exists():
                        df = pd.read_csv(file_path)
                        
                        # Validation et nettoyage des données
                        df_cleaned = self._clean_and_validate_data(df, data_type)
                        
                        self.data_cache[data_type] = df_cleaned
                        loaded_files[data_type] = {
                            'filename': filename,
                            'records': len(df_cleaned),
                            'columns': list(df_cleaned.columns),
                            'file_size_mb': file_path.stat().st_size / (1024 * 1024)
                        }
                        
                        data_info['loaded_files'].append(filename)
                        data_info['total_records'] += len(df_cleaned)
                        
                        logger.info(f"✅ {filename}: {len(df_cleaned)} enregistrements")
                    else:
                        logger.warning(f"⚠️ Fichier manquant: {filename}")
                        data_info['failed_files'].append(filename)
                        
                except Exception as e:
                    logger.error(f"❌ Erreur chargement {filename}: {e}")
                    data_info['failed_files'].append(filename)
            
            # Mise à jour du cache
            self.data_cache['last_loaded'] = datetime.now()
            
            # Informations complémentaires
            data_info['cache_info'] = {
                'buildings_count': len(self.data_cache['buildings']) if self.data_cache['buildings'] is not None else 0,
                'consumption_points': len(self.data_cache['consumption']) if self.data_cache['consumption'] is not None else 0,
                'weather_points': len(self.data_cache['weather']) if self.data_cache['weather'] is not None else 0,
                'water_points': len(self.data_cache['water']) if self.data_cache['water'] is not None else 0
            }
            
            logger.info(f"✅ Chargement terminé: {len(data_info['loaded_files'])} fichiers")
            return data_info
            
        except Exception as e:
            logger.error(f"❌ Erreur générale chargement: {e}")
            return {
                'success': False,
                'error': str(e),
                'loaded_files': [],
                'failed_files': list(self.file_mapping.values())
            }
    
    def get_current_data(self) -> Dict[str, pd.DataFrame]:
        """
        Retourne les données actuellement en cache
        
        Returns:
            Dict: Données en cache
        """
        return {
            'buildings': self.data_cache['buildings'],
            'consumption': self.data_cache['consumption'],
            'weather': self.data_cache['weather'],
            'water': self.data_cache['water']
        }
    
    def get_data_summary(self) -> Dict:
        """
        Génère un résumé statistique des données
        
        Returns:
            Dict: Résumé des données
        """
        try:
            summary = {
                'last_update': self.data_cache['last_loaded'].isoformat() if self.data_cache['last_loaded'] else None,
                'data_availability': {}
            }
            
            # === BÂTIMENTS ===
            buildings_df = self.data_cache['buildings']
            if buildings_df is not None and not buildings_df.empty:
                summary.update({
                    'total_buildings': len(buildings_df),
                    'building_types': buildings_df['building_type'].unique().tolist() if 'building_type' in buildings_df.columns else [],
                    'zones': buildings_df['zone_name'].unique().tolist() if 'zone_name' in buildings_df.columns else [],
                    'total_surface_m2': float(buildings_df['surface_area_m2'].sum()) if 'surface_area_m2' in buildings_df.columns else 0,
                    'avg_surface_m2': float(buildings_df['surface_area_m2'].mean()) if 'surface_area_m2' in buildings_df.columns else 0
                })
                summary['data_availability']['buildings'] = True
            else:
                summary.update({
                    'total_buildings': 0,
                    'building_types': [],
                    'zones': [],
                    'total_surface_m2': 0,
                    'avg_surface_m2': 0
                })
                summary['data_availability']['buildings'] = False
            
            # === CONSOMMATION ÉLECTRIQUE ===
            consumption_df = self.data_cache['consumption']
            if consumption_df is not None and not consumption_df.empty:
                if 'y' in consumption_df.columns:
                    summary.update({
                        'total_consumption': float(consumption_df['y'].sum()),
                        'avg_consumption': float(consumption_df['y'].mean()),
                        'max_consumption': float(consumption_df['y'].max()),
                        'min_consumption': float(consumption_df['y'].min()),
                        'consumption_points': len(consumption_df)
                    })
                
                if 'timestamp' in consumption_df.columns:
                    summary.update({
                        'consumption_period_start': consumption_df['timestamp'].min(),
                        'consumption_period_end': consumption_df['timestamp'].max()
                    })
                
                summary['data_availability']['consumption'] = True
            else:
                summary.update({
                    'total_consumption': 0,
                    'avg_consumption': 0,
                    'max_consumption': 0,
                    'min_consumption': 0,
                    'consumption_points': 0
                })
                summary['data_availability']['consumption'] = False
            
            # === DONNÉES MÉTÉO ===
            weather_df = self.data_cache['weather']
            if weather_df is not None and not weather_df.empty:
                weather_columns = [col for col in weather_df.columns if col not in ['unique_id', 'timestamp']]
                summary.update({
                    'weather_points': len(weather_df),
                    'weather_variables': len(weather_columns),
                    'weather_columns': weather_columns[:10]  # Limiter l'affichage
                })
                summary['data_availability']['weather'] = True
            else:
                summary.update({
                    'weather_points': 0,
                    'weather_variables': 0,
                    'weather_columns': []
                })
                summary['data_availability']['weather'] = False
            
            # === DONNÉES EAU ===
            water_df = self.data_cache['water']
            if water_df is not None and not water_df.empty:
                if 'y' in water_df.columns:
                    summary.update({
                        'total_water_consumption': float(water_df['y'].sum()),
                        'avg_water_consumption': float(water_df['y'].mean()),
                        'water_points': len(water_df)
                    })
                summary['data_availability']['water'] = True
            else:
                summary.update({
                    'total_water_consumption': 0,
                    'avg_water_consumption': 0,
                    'water_points': 0
                })
                summary['data_availability']['water'] = False
            
            # === TOTAUX ===
            summary['total_data_points'] = (
                summary.get('consumption_points', 0) +
                summary.get('weather_points', 0) +
                summary.get('water_points', 0)
            )
            
            # === PÉRIODE GLOBALE ===
            period_start = summary.get('consumption_period_start')
            period_end = summary.get('consumption_period_end')
            if period_start and period_end:
                summary['period'] = f"{period_start} à {period_end}"
            else:
                summary['period'] = "Non définie"
            
            return summary
            
        except Exception as e:
            logger.error(f"Erreur génération résumé: {e}")
            return {
                'error': str(e),
                'total_buildings': 0,
                'total_consumption': 0,
                'total_data_points': 0
            }
    
    def _clean_and_validate_data(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """
        Nettoie et valide les données selon leur type
        
        Args:
            df: DataFrame à nettoyer
            data_type: Type de données (buildings, consumption, weather, water)
            
        Returns:
            pd.DataFrame: DataFrame nettoyé
        """
        try:
            df_cleaned = df.copy()
            
            if data_type == 'buildings':
                df_cleaned = self._clean_buildings_data(df_cleaned)
            elif data_type == 'consumption':
                df_cleaned = self._clean_timeseries_data(df_cleaned, 'consumption')
            elif data_type == 'weather':
                df_cleaned = self._clean_weather_data(df_cleaned)
            elif data_type == 'water':
                df_cleaned = self._clean_timeseries_data(df_cleaned, 'water')
            
            return df_cleaned
            
        except Exception as e:
            logger.error(f"Erreur nettoyage données {data_type}: {e}")
            return df
    
    def _clean_buildings_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie les données de bâtiments"""
        # Suppression des doublons
        if 'unique_id' in df.columns:
            df = df.drop_duplicates(subset=['unique_id'])
        
        # Validation des coordonnées
        if 'latitude' in df.columns and 'longitude' in df.columns:
            # Limites Malaysia
            df = df[
                (df['latitude'].between(0.5, 7.5)) &
                (df['longitude'].between(99.0, 120.0)) &
                (df['latitude'].notna()) &
                (df['longitude'].notna())
            ]
        
        # Conversion des types
        numeric_columns = ['surface_area_m2', 'polygon_area_m2', 'floors_count']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Validation surface minimum
        if 'surface_area_m2' in df.columns:
            df = df[df['surface_area_m2'] > 0]
        
        return df
    
    def _clean_timeseries_data(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Nettoie les données de séries temporelles"""
        # Conversion timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])
        
        # Validation valeurs de consommation
        if 'y' in df.columns:
            df['y'] = pd.to_numeric(df['y'], errors='coerce')
            df = df.dropna(subset=['y'])
            # Suppression des valeurs négatives
            df = df[df['y'] >= 0]
            
            # Suppression des outliers extrêmes (> 99.9e percentile)
            if len(df) > 100:
                upper_limit = df['y'].quantile(0.999)
                df = df[df['y'] <= upper_limit]
        
        # Tri par timestamp
        if 'timestamp' in df.columns:
            df = df.sort_values(['unique_id', 'timestamp'] if 'unique_id' in df.columns else ['timestamp'])
        
        return df
    
    def _clean_weather_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie les données météorologiques"""
        # Conversion timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])
        
        # Validation des colonnes météo numériques
        weather_columns = [col for col in df.columns if col not in ['unique_id', 'timestamp']]
        
        for col in weather_columns:
            if df[col].dtype in ['object']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Suppression des lignes avec trop de valeurs manquantes
        threshold = len(weather_columns) * 0.5  # Au moins 50% des colonnes valides
        df = df.dropna(thresh=threshold + 2)  # +2 pour unique_id et timestamp
        
        return df
    
    def get_buildings_by_type(self, building_type: str) -> Optional[pd.DataFrame]:
        """
        Filtre les bâtiments par type
        
        Args:
            building_type: Type de bâtiment
            
        Returns:
            pd.DataFrame: Bâtiments filtrés
        """
        buildings_df = self.data_cache['buildings']
        
        if buildings_df is None or 'building_type' not in buildings_df.columns:
            return None
        
        if building_type == 'all':
            return buildings_df
        
        return buildings_df[buildings_df['building_type'] == building_type]
    
    def get_consumption_by_timerange(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Filtre la consommation par période
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            pd.DataFrame: Consommation filtrée
        """
        consumption_df = self.data_cache['consumption']
        
        if consumption_df is None or 'timestamp' not in consumption_df.columns:
            return None
        
        try:
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            mask = (
                (consumption_df['timestamp'] >= start_dt) &
                (consumption_df['timestamp'] <= end_dt)
            )
            
            return consumption_df[mask]
            
        except Exception as e:
            logger.error(f"Erreur filtrage temporel: {e}")
            return consumption_df
    
    def get_zone_statistics(self) -> Dict:
        """Statistiques par zone géographique"""
        buildings_df = self.data_cache['buildings']
        
        if buildings_df is None or 'zone_name' not in buildings_df.columns:
            return {}
        
        try:
            zone_stats = buildings_df.groupby('zone_name').agg({
                'unique_id': 'count',
                'surface_area_m2': ['sum', 'mean'],
                'building_type': lambda x: x.value_counts().to_dict(),
                'latitude': 'mean',
                'longitude': 'mean'
            }).round(2)
            
            zone_dict = {}
            for zone in zone_stats.index:
                stats = zone_stats.loc[zone]
                zone_dict[zone] = {
                    'building_count': int(stats[('unique_id', 'count')]),
                    'total_surface': float(stats[('surface_area_m2', 'sum')]),
                    'avg_surface': float(stats[('surface_area_m2', 'mean')]),
                    'building_types': stats[('building_type', '<lambda>')],
                    'center_lat': float(stats[('latitude', 'mean')]),
                    'center_lng': float(stats[('longitude', 'mean')])
                }
            
            return zone_dict
            
        except Exception as e:
            logger.error(f"Erreur statistiques zones: {e}")
            return {}
    
    def refresh_data(self) -> Dict:
        """Recharge toutes les données"""
        logger.info("🔄 Rechargement des données...")
        
        # Vider le cache
        for key in self.data_cache:
            if key != 'last_loaded':
                self.data_cache[key] = None
        
        # Recharger
        return self.load_malaysia_data()
    
    def is_data_loaded(self) -> bool:
        """Vérifie si des données sont chargées"""
        return any(
            self.data_cache[key] is not None 
            for key in ['buildings', 'consumption', 'weather', 'water']
        )
    
    def get_data_health(self) -> Dict:
        """État de santé des données"""
        health = {
            'overall_status': 'healthy',
            'issues': [],
            'recommendations': [],
            'data_quality': {}
        }
        
        try:
            # Vérification bâtiments
            buildings_df = self.data_cache['buildings']
            if buildings_df is not None:
                buildings_issues = []
                
                # Coordonnées manquantes
                missing_coords = buildings_df[
                    buildings_df['latitude'].isna() | buildings_df['longitude'].isna()
                ]
                if len(missing_coords) > 0:
                    buildings_issues.append(f"{len(missing_coords)} bâtiments sans coordonnées")
                
                # Surfaces nulles
                zero_surface = buildings_df[buildings_df['surface_area_m2'] <= 0]
                if len(zero_surface) > 0:
                    buildings_issues.append(f"{len(zero_surface)} bâtiments avec surface nulle")
                
                health['data_quality']['buildings'] = {
                    'total_records': len(buildings_df),
                    'issues_count': len(buildings_issues),
                    'issues': buildings_issues,
                    'quality_score': max(0, 100 - len(buildings_issues) * 10)
                }
            
            # Vérification consommation
            consumption_df = self.data_cache['consumption']
            if consumption_df is not None:
                consumption_issues = []
                
                # Valeurs négatives
                negative_values = consumption_df[consumption_df['y'] < 0]
                if len(negative_values) > 0:
                    consumption_issues.append(f"{len(negative_values)} valeurs négatives")
                
                # Doublons temporels
                if 'timestamp' in consumption_df.columns and 'unique_id' in consumption_df.columns:
                    duplicates = consumption_df.duplicated(subset=['unique_id', 'timestamp'])
                    if duplicates.sum() > 0:
                        consumption_issues.append(f"{duplicates.sum()} doublons temporels")
                
                health['data_quality']['consumption'] = {
                    'total_records': len(consumption_df),
                    'issues_count': len(consumption_issues),
                    'issues': consumption_issues,
                    'quality_score': max(0, 100 - len(consumption_issues) * 15)
                }
            
            # Score global
            scores = [
                quality['quality_score'] 
                for quality in health['data_quality'].values()
            ]
            
            if scores:
                overall_score = sum(scores) / len(scores)
                if overall_score >= 80:
                    health['overall_status'] = 'healthy'
                elif overall_score >= 60:
                    health['overall_status'] = 'warning'
                else:
                    health['overall_status'] = 'critical'
            
            return health
            
        except Exception as e:
            logger.error(f"Erreur évaluation santé données: {e}")
            return {
                'overall_status': 'error',
                'error': str(e)
            }


# ==============================================================================
# UTILITAIRES
# ==============================================================================

def test_data_service():
    """Test du service de données"""
    service = DataService()
    
    print("🧪 Test DataService:")
    
    # Test chargement
    result = service.load_malaysia_data()
    print(f"Chargement: {result.get('success', False)}")
    print(f"Fichiers chargés: {len(result.get('loaded_files', []))}")
    
    # Test résumé
    if service.is_data_loaded():
        summary = service.get_data_summary()
        print(f"Bâtiments: {summary.get('total_buildings', 0)}")
        print(f"Points consommation: {summary.get('consumption_points', 0)}")
    
    return service


if __name__ == '__main__':
    test_data_service()