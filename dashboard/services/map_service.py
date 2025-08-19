#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERVICE CARTOGRAPHIQUE - DASHBOARD MALAYSIA
==========================================

Service pour l'intégration de la cartographie interactive
avec les mêmes fonctionnalités que le projet Malaysia original

Version: 1.0.0
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class MapService:
    """Service cartographique pour le dashboard Malaysia"""
    
    def __init__(self):
        """Initialise le service cartographique"""
        self.default_center = [4.2105, 101.9758]  # Centre Malaysia
        self.default_zoom = 6
        
        # Configuration des clusters par densité
        self.density_thresholds = {
            'low': 10,
            'medium': 50,
            'high': 100
        }
        
        # Couleurs par type de bâtiment (même palette que projet original)
        self.building_colors = {
            'residential': '#28a745',      # Vert
            'commercial': '#007bff',       # Bleu
            'industrial': '#dc3545',       # Rouge
            'office': '#6f42c1',           # Violet
            'retail': '#fd7e14',           # Orange
            'warehouse': '#6c757d',        # Gris
            'hospital': '#e83e8c',         # Rose
            'school': '#20c997',           # Teal
            'hotel': '#ffc107',            # Jaune
            'mixed': '#343a40',            # Noir
            'other': '#17a2b8'             # Cyan
        }
        
        logger.info("✅ MapService initialisé")
    
    def create_buildings_map_data(self, buildings_df: pd.DataFrame, 
                                 density_percentage: int = 100) -> Dict:
        """
        Crée les données cartographiques pour les bâtiments
        
        Args:
            buildings_df: DataFrame des bâtiments
            density_percentage: Pourcentage de densité d'affichage
            
        Returns:
            Dict: Données pour la carte Leaflet
        """
        try:
            if buildings_df is None or buildings_df.empty:
                return self._create_empty_map_data()
            
            # Filtrage par densité
            if density_percentage < 100:
                sample_size = int(len(buildings_df) * density_percentage / 100)
                buildings_sample = buildings_df.sample(n=min(sample_size, len(buildings_df)))
            else:
                buildings_sample = buildings_df.copy()
            
            # Validation des coordonnées
            valid_buildings = self._filter_valid_coordinates(buildings_sample)
            
            if valid_buildings.empty:
                return self._create_empty_map_data()
            
            # Création des marqueurs
            markers = self._create_building_markers(valid_buildings)
            
            # Calcul du centre et zoom optimal
            center, zoom = self._calculate_optimal_view(valid_buildings)
            
            # Statistiques par type
            type_stats = self._calculate_type_statistics(valid_buildings)
            
            # Zones de densité
            density_zones = self._calculate_density_zones(valid_buildings)
            
            map_data = {
                'center': center,
                'zoom': zoom,
                'markers': markers,
                'statistics': {
                    'total_buildings': len(valid_buildings),
                    'displayed_buildings': len(markers),
                    'density_percentage': density_percentage,
                    'type_distribution': type_stats,
                    'geographic_bounds': self._get_geographic_bounds(valid_buildings)
                },
                'density_zones': density_zones,
                'legend': self._create_legend_data(),
                'controls': {
                    'show_clusters': len(markers) > 100,
                    'show_density_zones': len(markers) > 50,
                    'show_type_filter': len(type_stats) > 1
                }
            }
            
            logger.info(f"✅ Carte créée: {len(markers)} marqueurs, centre {center}")
            return map_data
            
        except Exception as e:
            logger.error(f"Erreur création carte: {e}")
            return self._create_empty_map_data()
    
    def create_consumption_heatmap_data(self, consumption_df: pd.DataFrame,
                                      buildings_df: pd.DataFrame) -> Dict:
        """
        Crée une heatmap de consommation
        
        Args:
            consumption_df: Données de consommation
            buildings_df: Données des bâtiments
            
        Returns:
            Dict: Données heatmap
        """
        try:
            if consumption_df is None or buildings_df is None:
                return {'heatmap_points': [], 'statistics': {}}
            
            # Agrégation de la consommation par bâtiment
            consumption_agg = consumption_df.groupby('unique_id')['y'].agg([
                'sum', 'mean', 'max', 'count'
            ]).reset_index()
            
            # Jointure avec les coordonnées des bâtiments
            merged_data = buildings_df.merge(
                consumption_agg, 
                on='unique_id', 
                how='inner'
            )
            
            # Filtrage des coordonnées valides
            valid_data = self._filter_valid_coordinates(merged_data)
            
            if valid_data.empty:
                return {'heatmap_points': [], 'statistics': {}}
            
            # Normalisation de l'intensité (0-1)
            max_consumption = valid_data['sum'].max()
            min_consumption = valid_data['sum'].min()
            
            if max_consumption > min_consumption:
                valid_data['intensity'] = (
                    (valid_data['sum'] - min_consumption) / 
                    (max_consumption - min_consumption)
                )
            else:
                valid_data['intensity'] = 0.5
            
            # Création des points heatmap
            heatmap_points = []
            for _, row in valid_data.iterrows():
                heatmap_points.append({
                    'lat': float(row['latitude']),
                    'lng': float(row['longitude']),
                    'intensity': float(row['intensity']),
                    'consumption_sum': float(row['sum']),
                    'consumption_avg': float(row['mean']),
                    'building_id': row['unique_id'],
                    'building_type': row.get('building_type', 'unknown')
                })
            
            # Statistiques
            statistics = {
                'total_points': len(heatmap_points),
                'max_consumption': float(max_consumption),
                'min_consumption': float(min_consumption),
                'avg_consumption': float(valid_data['mean'].mean()),
                'total_consumption': float(valid_data['sum'].sum()),
                'consumption_range': float(max_consumption - min_consumption)
            }
            
            logger.info(f"✅ Heatmap créée: {len(heatmap_points)} points")
            
            return {
                'heatmap_points': heatmap_points,
                'statistics': statistics,
                'center': self._calculate_optimal_view(valid_data)[0],
                'zoom': 7
            }
            
        except Exception as e:
            logger.error(f"Erreur création heatmap: {e}")
            return {'heatmap_points': [], 'statistics': {}}
    
    def create_zone_analysis_data(self, buildings_df: pd.DataFrame) -> Dict:
        """
        Analyse cartographique par zone
        
        Args:
            buildings_df: DataFrame des bâtiments
            
        Returns:
            Dict: Données d'analyse par zone
        """
        try:
            if buildings_df is None or buildings_df.empty:
                return {'zones': [], 'statistics': {}}
            
            # Groupement par zone
            if 'zone_name' not in buildings_df.columns:
                return {'zones': [], 'statistics': {}}
            
            zone_analysis = buildings_df.groupby('zone_name').agg({
                'latitude': ['mean', 'count'],
                'longitude': 'mean',
                'surface_area_m2': ['sum', 'mean'],
                'building_type': lambda x: x.value_counts().to_dict()
            }).round(4)
            
            zones_data = []
            for zone_name in zone_analysis.index:
                zone_stats = zone_analysis.loc[zone_name]
                
                zone_info = {
                    'name': zone_name,
                    'center': [
                        float(zone_stats[('latitude', 'mean')]),
                        float(zone_stats[('longitude', 'mean')])
                    ],
                    'building_count': int(zone_stats[('latitude', 'count')]),
                    'total_surface': float(zone_stats[('surface_area_m2', 'sum')]),
                    'avg_surface': float(zone_stats[('surface_area_m2', 'mean')]),
                    'building_types': zone_stats[('building_type', '<lambda>')],
                    'density_level': self._calculate_zone_density_level(
                        int(zone_stats[('latitude', 'count')])
                    )
                }
                
                zones_data.append(zone_info)
            
            # Tri par nombre de bâtiments
            zones_data.sort(key=lambda x: x['building_count'], reverse=True)
            
            # Statistiques globales
            statistics = {
                'total_zones': len(zones_data),
                'zones_with_most_buildings': zones_data[:5] if zones_data else [],
                'total_buildings': sum(zone['building_count'] for zone in zones_data),
                'avg_buildings_per_zone': np.mean([zone['building_count'] for zone in zones_data])
            }
            
            logger.info(f"✅ Analyse zones: {len(zones_data)} zones")
            
            return {
                'zones': zones_data,
                'statistics': statistics
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse zones: {e}")
            return {'zones': [], 'statistics': {}}
    
    def _filter_valid_coordinates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filtre les coordonnées valides pour Malaysia"""
        if df.empty:
            return df
        
        # Limites géographiques Malaysia
        malaysia_bounds = {
            'lat_min': 0.5,
            'lat_max': 7.5,
            'lon_min': 99.0,
            'lon_max': 120.0
        }
        
        valid_mask = (
            (df['latitude'].notna()) &
            (df['longitude'].notna()) &
            (df['latitude'] >= malaysia_bounds['lat_min']) &
            (df['latitude'] <= malaysia_bounds['lat_max']) &
            (df['longitude'] >= malaysia_bounds['lon_min']) &
            (df['longitude'] <= malaysia_bounds['lon_max'])
        )
        
        return df[valid_mask].copy()
    
    def _create_building_markers(self, buildings_df: pd.DataFrame) -> List[Dict]:
        """Crée les marqueurs de bâtiments"""
        markers = []
        
        for _, building in buildings_df.iterrows():
            building_type = building.get('building_type', 'other')
            color = self.building_colors.get(building_type, self.building_colors['other'])
            
            # Popup content
            popup_content = self._create_popup_content(building)
            
            marker = {
                'lat': float(building['latitude']),
                'lng': float(building['longitude']),
                'popup': popup_content,
                'color': color,
                'building_type': building_type,
                'building_id': building.get('unique_id', ''),
                'surface_area': float(building.get('surface_area_m2', 0)),
                'zone': building.get('zone_name', 'Unknown')
            }
            
            markers.append(marker)
        
        return markers
    
    def _create_popup_content(self, building: pd.Series) -> str:
        """Crée le contenu du popup pour un bâtiment"""
        building_id = building.get('unique_id', 'N/A')
        building_type = building.get('building_type', 'N/A')
        surface = building.get('surface_area_m2', 0)
        zone = building.get('zone_name', 'N/A')
        
        # Informations géométriques si disponibles
        geometry_info = ""
        if building.get('has_precise_geometry', False):
            geometry_info = f"""
            <br><small class="text-success">
                <i class="bi bi-geo-alt"></i> Géométrie précise OSM
            </small>"""
        
        # Étages si disponibles
        floors_info = ""
        if building.get('floors_count', 0) > 0:
            floors_info = f"""
            <br><small><i class="bi bi-building"></i> {building.get('floors_count')} étages</small>"""
        
        popup_html = f"""
        <div class="building-popup">
            <h6><i class="bi bi-building"></i> {building_id}</h6>
            <hr class="my-2">
            <p class="mb-1">
                <strong>Type:</strong> {building_type.title()}<br>
                <strong>Surface:</strong> {surface:,.0f} m²<br>
                <strong>Zone:</strong> {zone}
                {floors_info}
            </p>
            <small class="text-muted">
                <i class="bi bi-geo"></i> 
                {building.get('latitude', 0):.4f}, {building.get('longitude', 0):.4f}
            </small>
            {geometry_info}
        </div>
        """
        
        return popup_html
    
    def _calculate_optimal_view(self, buildings_df: pd.DataFrame) -> Tuple[List[float], int]:
        """Calcule le centre et zoom optimal pour la carte"""
        if buildings_df.empty:
            return self.default_center, self.default_zoom
        
        # Centre géographique
        center_lat = float(buildings_df['latitude'].mean())
        center_lng = float(buildings_df['longitude'].mean())
        center = [center_lat, center_lng]
        
        # Calcul du zoom basé sur la dispersion
        lat_range = buildings_df['latitude'].max() - buildings_df['latitude'].min()
        lng_range = buildings_df['longitude'].max() - buildings_df['longitude'].min()
        
        max_range = max(lat_range, lng_range)
        
        if max_range > 5:
            zoom = 5
        elif max_range > 2:
            zoom = 6
        elif max_range > 1:
            zoom = 7
        elif max_range > 0.5:
            zoom = 8
        elif max_range > 0.1:
            zoom = 10
        else:
            zoom = 12
        
        return center, zoom
    
    def _calculate_type_statistics(self, buildings_df: pd.DataFrame) -> Dict:
        """Calcule les statistiques par type de bâtiment"""
        if 'building_type' not in buildings_df.columns:
            return {}
        
        type_counts = buildings_df['building_type'].value_counts()
        total = len(buildings_df)
        
        type_stats = {}
        for building_type, count in type_counts.items():
            type_stats[building_type] = {
                'count': int(count),
                'percentage': round(count / total * 100, 1),
                'color': self.building_colors.get(building_type, self.building_colors['other'])
            }
        
        return type_stats
    
    def _calculate_density_zones(self, buildings_df: pd.DataFrame) -> List[Dict]:
        """Calcule les zones de densité"""
        if buildings_df.empty:
            return []
        
        # Grille de densité simplifiée
        lat_min, lat_max = buildings_df['latitude'].min(), buildings_df['latitude'].max()
        lng_min, lng_max = buildings_df['longitude'].min(), buildings_df['longitude'].max()
        
        # Création d'une grille 10x10
        lat_step = (lat_max - lat_min) / 10
        lng_step = (lng_max - lng_min) / 10
        
        density_zones = []
        
        for i in range(10):
            for j in range(10):
                lat_start = lat_min + i * lat_step
                lat_end = lat_min + (i + 1) * lat_step
                lng_start = lng_min + j * lng_step
                lng_end = lng_min + (j + 1) * lng_step
                
                # Compter les bâtiments dans cette zone
                in_zone = buildings_df[
                    (buildings_df['latitude'] >= lat_start) &
                    (buildings_df['latitude'] < lat_end) &
                    (buildings_df['longitude'] >= lng_start) &
                    (buildings_df['longitude'] < lng_end)
                ]
                
                if len(in_zone) > 0:
                    density_zones.append({
                        'bounds': [
                            [lat_start, lng_start],
                            [lat_end, lng_end]
                        ],
                        'count': len(in_zone),
                        'density_level': self._get_density_level(len(in_zone))
                    })
        
        return density_zones
    
    def _get_density_level(self, count: int) -> str:
        """Détermine le niveau de densité"""
        if count >= self.density_thresholds['high']:
            return 'high'
        elif count >= self.density_thresholds['medium']:
            return 'medium'
        elif count >= self.density_thresholds['low']:
            return 'low'
        else:
            return 'very_low'
    
    def _calculate_zone_density_level(self, building_count: int) -> str:
        """Calcule le niveau de densité d'une zone"""
        return self._get_density_level(building_count)
    
    def _get_geographic_bounds(self, buildings_df: pd.DataFrame) -> Dict:
        """Retourne les limites géographiques"""
        return {
            'north': float(buildings_df['latitude'].max()),
            'south': float(buildings_df['latitude'].min()),
            'east': float(buildings_df['longitude'].max()),
            'west': float(buildings_df['longitude'].min())
        }
    
    def _create_legend_data(self) -> Dict:
        """Crée les données de légende"""
        legend_items = []
        
        for building_type, color in self.building_colors.items():
            legend_items.append({
                'type': building_type,
                'label': building_type.replace('_', ' ').title(),
                'color': color
            })
        
        return {
            'title': 'Types de Bâtiments',
            'items': legend_items
        }
    
    def _create_empty_map_data(self) -> Dict:
        """Crée des données de carte vides"""
        return {
            'center': self.default_center,
            'zoom': self.default_zoom,
            'markers': [],
            'statistics': {
                'total_buildings': 0,
                'displayed_buildings': 0,
                'density_percentage': 100,
                'type_distribution': {},
                'geographic_bounds': {}
            },
            'density_zones': [],
            'legend': self._create_legend_data(),
            'controls': {
                'show_clusters': False,
                'show_density_zones': False,
                'show_type_filter': False
            }
        }
    
    def get_map_statistics(self, buildings_df: pd.DataFrame) -> Dict:
        """Retourne les statistiques cartographiques"""
        try:
            if buildings_df is None or buildings_df.empty:
                return {}
            
            valid_buildings = self._filter_valid_coordinates(buildings_df)
            
            stats = {
                'total_buildings': len(buildings_df),
                'valid_coordinates': len(valid_buildings),
                'invalid_coordinates': len(buildings_df) - len(valid_buildings),
                'coverage_percentage': len(valid_buildings) / len(buildings_df) * 100,
                'geographic_coverage': self._get_geographic_bounds(valid_buildings),
                'type_distribution': self._calculate_type_statistics(valid_buildings)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur statistiques carte: {e}")
            return {}


# ==============================================================================
# UTILITAIRES CARTOGRAPHIQUES
# ==============================================================================

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance entre deux points géographiques (formule haversine)
    
    Args:
        lat1, lon1: Coordonnées du premier point
        lat2, lon2: Coordonnées du second point
        
    Returns:
        float: Distance en kilomètres
    """
    from math import radians, cos, sin, asin, sqrt
    
    # Conversion en radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Formule haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Rayon de la Terre en km
    r = 6371
    
    return c * r


def is_point_in_malaysia(lat: float, lon: float) -> bool:
    """
    Vérifie si un point est dans les limites de Malaysia
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        bool: True si le point est en Malaysia
    """
    malaysia_bounds = {
        'lat_min': 0.5,
        'lat_max': 7.5,
        'lon_min': 99.0,
        'lon_max': 120.0
    }
    
    return (
        malaysia_bounds['lat_min'] <= lat <= malaysia_bounds['lat_max'] and
        malaysia_bounds['lon_min'] <= lon <= malaysia_bounds['lon_max']
    )


# ==============================================================================
# TESTS
# ==============================================================================

def test_map_service():
    """Test du service cartographique"""
    import pandas as pd
    
    # Données de test
    test_data = {
        'unique_id': ['B001', 'B002', 'B003'],
        'latitude': [3.1390, 3.1500, 3.1600],
        'longitude': [101.6869, 101.7000, 101.7100],
        'building_type': ['residential', 'commercial', 'industrial'],
        'surface_area_m2': [120, 500, 1200],
        'zone_name': ['Kuala Lumpur', 'Kuala Lumpur', 'Selangor']
    }
    
    buildings_df = pd.DataFrame(test_data)
    
    map_service = MapService()
    
    # Test création carte
    map_data = map_service.create_buildings_map_data(buildings_df)
    
    print("🗺️ Test MapService:")
    print(f"Marqueurs créés: {len(map_data['markers'])}")
    print(f"Centre: {map_data['center']}")
    print(f"Zoom: {map_data['zoom']}")
    print(f"Types de bâtiments: {list(map_data['statistics']['type_distribution'].keys())}")
    
    return map_data


if __name__ == '__main__':
    test_map_service()