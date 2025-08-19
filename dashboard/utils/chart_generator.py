#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GÉNÉRATEUR DE GRAPHIQUES - DASHBOARD MALAYSIA
============================================

Générateur de graphiques Plotly pour le dashboard Malaysia
avec les mêmes visualisations que le projet original

Version: 1.0.0
"""

import logging
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Générateur de graphiques pour le dashboard"""
    
    def __init__(self):
        """Initialise le générateur de graphiques"""
        
        # Palette de couleurs Malaysia
        self.color_palette = {
            'primary': '#2563eb',
            'secondary': '#64748b',
            'success': '#059669',
            'warning': '#d97706',
            'danger': '#dc2626',
            'info': '#0891b2',
            'purple': '#7c3aed',
            'pink': '#e91e63',
            'teal': '#14b8a6',
            'orange': '#f97316'
        }
        
        # Couleurs par type de bâtiment
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
        
        # Template de style sombre
        self.dark_template = {
            'layout': {
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'font': {'color': '#e2e8f0'},
                'xaxis': {
                    'gridcolor': '#334155',
                    'zerolinecolor': '#475569'
                },
                'yaxis': {
                    'gridcolor': '#334155',
                    'zerolinecolor': '#475569'
                }
            }
        }
        
        logger.info("✅ ChartGenerator initialisé")
    
    def create_overview_charts(self, data: Dict) -> Dict:
        """
        Crée les graphiques de vue d'ensemble
        
        Args:
            data: Données (buildings, consumption, etc.)
            
        Returns:
            Dict: Graphiques sérialisés pour Plotly.js
        """
        try:
            charts = {}
            
            # Graphique timeline de consommation
            if data.get('consumption') is not None:
                charts['consumption_timeline'] = self._create_consumption_timeline(
                    data['consumption']
                )
            
            # Graphique types de bâtiments
            if data.get('buildings') is not None:
                charts['building_types'] = self._create_building_types_chart(
                    data['buildings']
                )
            
            # Graphique de corrélation météo-consommation
            if data.get('consumption') is not None and data.get('weather') is not None:
                charts['weather_correlation'] = self._create_weather_correlation(
                    data['consumption'], data['weather']
                )
            
            return charts
            
        except Exception as e:
            logger.error(f"Erreur création graphiques overview: {e}")
            return {}
    
    def create_consumption_charts(self, data: Dict, time_range: str = '7d', 
                                building_type: str = 'all') -> Dict:
        """
        Crée les graphiques de consommation détaillés
        
        Args:
            data: Données
            time_range: Période (7d, 30d, 90d)
            building_type: Type de bâtiment
            
        Returns:
            Dict: Graphiques de consommation
        """
        try:
            charts = {}
            consumption_df = data.get('consumption')
            buildings_df = data.get('buildings')
            
            if consumption_df is None:
                return charts
            
            # Filtrage par période
            filtered_consumption = self._filter_by_timerange(consumption_df, time_range)
            
            # Filtrage par type de bâtiment
            if building_type != 'all' and buildings_df is not None:
                building_ids = buildings_df[
                    buildings_df['building_type'] == building_type
                ]['unique_id'].tolist()
                filtered_consumption = filtered_consumption[
                    filtered_consumption['unique_id'].isin(building_ids)
                ]
            
            # Graphique détaillé de consommation
            charts['detailed_consumption'] = self._create_detailed_consumption_chart(
                filtered_consumption
            )
            
            # Patterns horaires
            charts['hourly_patterns'] = self._create_hourly_patterns_chart(
                filtered_consumption
            )
            
            # Heatmap de consommation
            charts['consumption_heatmap'] = self._create_consumption_heatmap_chart(
                filtered_consumption
            )
            
            return charts
            
        except Exception as e:
            logger.error(f"Erreur création graphiques consommation: {e}")
            return {}
    
    def _create_consumption_timeline(self, consumption_df: pd.DataFrame) -> Dict:
        """Crée un graphique timeline de consommation"""
        try:
            if 'timestamp' not in consumption_df.columns or 'y' not in consumption_df.columns:
                return self._create_empty_chart("Timeline de Consommation")
            
            # Agrégation par heure
            consumption_df['timestamp'] = pd.to_datetime(consumption_df['timestamp'])
            hourly_data = consumption_df.groupby(
                consumption_df['timestamp'].dt.floor('h')
            )['y'].sum().reset_index()
            
            # Création du graphique
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=hourly_data['timestamp'],
                y=hourly_data['y'],
                mode='lines',
                name='Consommation Totale',
                line=dict(color=self.color_palette['primary'], width=2),
                fill='tonexty' if len(hourly_data) > 1 else None,
                fillcolor=f"rgba(37, 99, 235, 0.1)"
            ))
            
            # Mise en forme
            fig.update_layout(
                title='Évolution de la Consommation Électrique',
                xaxis_title='Temps',
                yaxis_title='Consommation (kWh)',
                hovermode='x unified',
                **self.dark_template['layout']
            )
            
            return json.loads(fig.to_json())
            
        except Exception as e:
            logger.error(f"Erreur timeline consommation: {e}")
            return self._create_empty_chart("Timeline de Consommation")
    
    def _create_building_types_chart(self, buildings_df: pd.DataFrame) -> Dict:
        """Crée un graphique en secteurs des types de bâtiments"""
        try:
            if 'building_type' not in buildings_df.columns:
                return self._create_empty_chart("Types de Bâtiments")
            
            # Comptage par type
            type_counts = buildings_df['building_type'].value_counts()
            
            # Couleurs pour chaque type
            colors = [
                self.building_colors.get(btype, self.color_palette['secondary'])
                for btype in type_counts.index
            ]
            
            # Création du graphique en secteurs
            fig = go.Figure(data=[go.Pie(
                labels=[btype.replace('_', ' ').title() for btype in type_counts.index],
                values=type_counts.values,
                hole=0.4,
                marker=dict(colors=colors),
                textinfo='label+percent',
                textposition='inside',
                hovertemplate='<b>%{label}</b><br>Bâtiments: %{value}<br>Pourcentage: %{percent}<extra></extra>'
            )])
            
            fig.update_layout(
                title='Répartition par Type de Bâtiment',
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.01
                ),
                **self.dark_template['layout']
            )
            
            return json.loads(fig.to_json())
            
        except Exception as e:
            logger.error(f"Erreur graphique types bâtiments: {e}")
            return self._create_empty_chart("Types de Bâtiments")
    
    def _create_detailed_consumption_chart(self, consumption_df: pd.DataFrame) -> Dict:
        """Graphique détaillé de consommation avec moyennes mobiles"""
        try:
            if consumption_df.empty or 'timestamp' not in consumption_df.columns:
                return self._create_empty_chart("Consommation Détaillée")
            
            # Préparation des données
            consumption_df['timestamp'] = pd.to_datetime(consumption_df['timestamp'])
            hourly_data = consumption_df.groupby(
                consumption_df['timestamp'].dt.floor('h')
            )['y'].agg(['sum', 'mean', 'count']).reset_index()
            
            # Moyennes mobiles
            hourly_data['ma_24h'] = hourly_data['sum'].rolling(window=24, center=True).mean()
            hourly_data['ma_7d'] = hourly_data['sum'].rolling(window=168, center=True).mean()  # 7*24h
            
            fig = go.Figure()
            
            # Consommation horaire
            fig.add_trace(go.Scatter(
                x=hourly_data['timestamp'],
                y=hourly_data['sum'],
                mode='lines',
                name='Consommation Horaire',
                line=dict(color=self.color_palette['primary'], width=1),
                opacity=0.7
            ))
            
            # Moyenne mobile 24h
            fig.add_trace(go.Scatter(
                x=hourly_data['timestamp'],
                y=hourly_data['ma_24h'],
                mode='lines',
                name='Moyenne 24h',
                line=dict(color=self.color_palette['warning'], width=2)
            ))
            
            # Moyenne mobile 7j
            if len(hourly_data) > 168:
                fig.add_trace(go.Scatter(
                    x=hourly_data['timestamp'],
                    y=hourly_data['ma_7d'],
                    mode='lines',
                    name='Moyenne 7 jours',
                    line=dict(color=self.color_palette['success'], width=3)
                ))
            
            fig.update_layout(
                title='Consommation Électrique Détaillée',
                xaxis_title='Temps',
                yaxis_title='Consommation (kWh)',
                hovermode='x unified',
                **self.dark_template['layout']
            )
            
            return json.loads(fig.to_json())
            
        except Exception as e:
            logger.error(f"Erreur graphique consommation détaillée: {e}")
            return self._create_empty_chart("Consommation Détaillée")
    
    def _create_hourly_patterns_chart(self, consumption_df: pd.DataFrame) -> Dict:
        """Graphique des patterns horaires de consommation"""
        try:
            if consumption_df.empty or 'timestamp' not in consumption_df.columns:
                return self._create_empty_chart("Patterns Horaires")
            
            # Extraction de l'heure
            consumption_df['timestamp'] = pd.to_datetime(consumption_df['timestamp'])
            consumption_df['hour'] = consumption_df['timestamp'].dt.hour
            consumption_df['day_of_week'] = consumption_df['timestamp'].dt.day_name()
            
            # Agrégation par heure
            hourly_avg = consumption_df.groupby('hour')['y'].mean()
            hourly_std = consumption_df.groupby('hour')['y'].std()
            
            fig = go.Figure()
            
            # Moyenne par heure
            fig.add_trace(go.Scatter(
                x=hourly_avg.index,
                y=hourly_avg.values,
                mode='lines+markers',
                name='Consommation Moyenne',
                line=dict(color=self.color_palette['primary'], width=3),
                marker=dict(size=8)
            ))
            
            # Zone d'écart-type
            fig.add_trace(go.Scatter(
                x=list(hourly_avg.index) + list(hourly_avg.index[::-1]),
                y=list(hourly_avg + hourly_std) + list((hourly_avg - hourly_std)[::-1]),
                fill='toself',
                fillcolor=f"rgba(37, 99, 235, 0.2)",
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False,
                name='Écart-type'
            ))
            
            fig.update_layout(**self.dark_template['layout'])

            # Puis configurer spécifiquement le titre et les axes
            fig.update_layout(
                title='Patterns de Consommation par Heure',
                yaxis_title='Consommation Moyenne (kWh)'
            )

            # Enfin configurer l'axe X séparément
            fig.update_xaxes(
                title='Heure de la Journée',
                tickmode='array',
                tickvals=list(range(0, 24, 2)),
                ticktext=[f"{h}h" for h in range(0, 24, 2)]
            )
            
            return json.loads(fig.to_json())
            
        except Exception as e:
            logger.error(f"Erreur patterns horaires: {e}")
            return self._create_empty_chart("Patterns Horaires")
    
    def _create_consumption_heatmap_chart(self, consumption_df: pd.DataFrame) -> Dict:
        """Heatmap de consommation (heure vs jour de la semaine)"""
        try:
            if consumption_df.empty or 'timestamp' not in consumption_df.columns:
                return self._create_empty_chart("Heatmap Consommation")
            
            print(f"🔍 DEBUG Heatmap - Données initiales: {len(consumption_df)} lignes")
            
            # Préparation des données
            consumption_df['timestamp'] = pd.to_datetime(consumption_df['timestamp'])
            consumption_df['hour'] = consumption_df['timestamp'].dt.hour
            consumption_df['day_of_week'] = consumption_df['timestamp'].dt.dayofweek
            consumption_df['day_name'] = consumption_df['timestamp'].dt.day_name()
            
            print(f"🔍 Période: {consumption_df['timestamp'].min()} à {consumption_df['timestamp'].max()}")
            print(f"🔍 Heures uniques: {sorted(consumption_df['hour'].unique())}")
            print(f"🔍 Jours uniques: {sorted(consumption_df['day_of_week'].unique())}")
            
            # Vérifier qu'on a la colonne 'y'
            if 'y' not in consumption_df.columns:
                print("❌ Colonne 'y' manquante")
                return self._create_empty_chart("Heatmap Consommation")
            
            # Agrégation par jour et heure - MOYENNE des consommations
            grouped_data = consumption_df.groupby(['day_of_week', 'hour'])['y'].mean().reset_index()
            print(f"🔍 Données groupées: {len(grouped_data)} combinaisons jour/heure")
            
            if grouped_data.empty:
                print("❌ Aucune donnée après groupement")
                return self._create_empty_chart("Heatmap Consommation")
            
            # Pivot table pour la heatmap
            heatmap_data = grouped_data.pivot(index='day_of_week', columns='hour', values='y')
            heatmap_data = heatmap_data.fillna(0)  # Remplacer NaN par 0
            
            print(f"🔍 Heatmap shape: {heatmap_data.shape}")
            print(f"🔍 Valeurs min/max: {heatmap_data.min().min():.2f} / {heatmap_data.max().max():.2f}")
            
            # Noms des jours en français
            day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            
            # S'assurer qu'on a tous les jours (0-6)
            all_days = list(range(7))
            heatmap_data = heatmap_data.reindex(all_days, fill_value=0)
            
            # S'assurer qu'on a toutes les heures (0-23)
            all_hours = list(range(24))
            heatmap_data = heatmap_data.reindex(columns=all_hours, fill_value=0)
            
            print(f"🔍 Heatmap finale shape: {heatmap_data.shape}")
            
            
            z_min = heatmap_data.min().min()
            z_max = heatmap_data.max().max()
            
            print(f"🔍 Valeurs pour colorscale: {z_min:.2f} - {z_max:.2f}")
            
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=[f"{h:02d}h" for h in range(24)],
                y=day_names,
                colorscale='Viridis',
                hoverongaps=False,
                showscale=True,
                # CORRECTION : Forcer l'échelle des couleurs
                zmin=z_min,
                zmax=z_max,
                # CORRECTION : Colorbar sans titleside
                colorbar=dict(
                    title="Consommation<br>Moyenne (kWh)",
                    thickness=15,
                    len=0.7
                ),
                hovertemplate='<b>%{y}</b><br>Heure: %{x}<br>Consommation: %{z:.1f} kWh<extra></extra>',
                # Options pour améliorer l'affichage
                xgap=1,  # Espacement entre les cellules
                ygap=1
            ))
            
            # Layout avec template d'abord
            fig.update_layout(**self.dark_template['layout'])
            
            # Configuration spécifique améliorée
            fig.update_layout(
                title='Heatmap de Consommation (Jour × Heure)',
                height=500,  # Plus haut pour mieux voir
                width=900,   # Plus large
                margin=dict(l=100, r=120, t=80, b=80),
                # AJOUT : Fond pour mieux voir la heatmap
                plot_bgcolor='rgba(0,0,0,0.1)'
            )
            
            # Configuration des axes
            fig.update_xaxes(
                title='Heure de la journée',
                side='bottom',
                tickmode='array',
                tickvals=list(range(0, 24, 2)),
                ticktext=[f"{h:02d}h" for h in range(0, 24, 2)]
            )
            fig.update_yaxes(
                title='Jour de la semaine',
                side='left'
            )
            
            return json.loads(fig.to_json())
            
        except Exception as e:
            logger.error(f"Erreur heatmap consommation: {e}")
            import traceback
            traceback.print_exc()
            return self._create_empty_chart("Heatmap Consommation")
    
    def _create_weather_correlation(self, consumption_df: pd.DataFrame, 
                                  weather_df: pd.DataFrame) -> Dict:
        """Graphique de corrélation météo-consommation"""
        try:
            if consumption_df.empty or weather_df.empty:
                return self._create_empty_chart("Corrélation Météo")
            
            # Agrégation par jour
            consumption_daily = consumption_df.groupby(
                pd.to_datetime(consumption_df['timestamp']).dt.date
            )['y'].sum().reset_index()
            consumption_daily.columns = ['date', 'total_consumption']
            
            # Météo quotidienne (moyenne)
            weather_df['date'] = pd.to_datetime(weather_df['timestamp']).dt.date
            weather_cols = [col for col in weather_df.columns if col not in ['unique_id', 'timestamp', 'date']]
            
            if weather_cols:
                # Prendre la première colonne météo (probablement température)
                temp_col = weather_cols[0]
                weather_daily = weather_df.groupby('date')[temp_col].mean().reset_index()
                weather_daily.columns = ['date', 'temperature']
                
                # Jointure des données
                merged_data = pd.merge(consumption_daily, weather_daily, on='date', how='inner')
                
                if not merged_data.empty:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=merged_data['temperature'],
                        y=merged_data['total_consumption'],
                        mode='markers',
                        name='Consommation vs Température',
                        marker=dict(
                            color=merged_data['total_consumption'],
                            colorscale='Viridis',
                            showscale=True,
                            size=8,
                            colorbar=dict(title="Consommation (kWh)")
                        ),
                        hovertemplate='<b>Température:</b> %{x:.1f}°C<br><b>Consommation:</b> %{y:.1f} kWh<extra></extra>'
                    ))
                    
                    # Ligne de tendance
                    z = np.polyfit(merged_data['temperature'], merged_data['total_consumption'], 1)
                    p = np.poly1d(z)
                    
                    fig.add_trace(go.Scatter(
                        x=merged_data['temperature'],
                        y=p(merged_data['temperature']),
                        mode='lines',
                        name='Tendance',
                        line=dict(color=self.color_palette['danger'], width=2, dash='dash')
                    ))
                    
                    fig.update_layout(
                        title='Corrélation Température vs Consommation',
                        xaxis_title='Température (°C)',
                        yaxis_title='Consommation Totale (kWh)',
                        **self.dark_template['layout']
                    )
                    
                    return json.loads(fig.to_json())
            
            return self._create_empty_chart("Corrélation Météo")
            
        except Exception as e:
            logger.error(f"Erreur corrélation météo: {e}")
            return self._create_empty_chart("Corrélation Météo")
    
    def create_zone_analysis_chart(self, buildings_df: pd.DataFrame, 
                                 consumption_df: pd.DataFrame = None) -> Dict:
        """Graphique d'analyse par zone"""
        try:
            if buildings_df.empty or 'zone_name' not in buildings_df.columns:
                return self._create_empty_chart("Analyse par Zone")
            
            # Statistiques par zone
            zone_stats = buildings_df.groupby('zone_name').agg({
                'unique_id': 'count',
                'surface_area_m2': 'sum'
            }).reset_index()
            zone_stats.columns = ['zone', 'building_count', 'total_surface']
            
            # Ajout de la consommation si disponible
            if consumption_df is not None and not consumption_df.empty:
                consumption_by_zone = consumption_df.groupby('unique_id')['y'].sum().reset_index()
                
                # Jointure avec les bâtiments pour obtenir les zones
                buildings_consumption = buildings_df[['unique_id', 'zone_name']].merge(
                    consumption_by_zone, on='unique_id', how='inner'
                )
                
                zone_consumption = buildings_consumption.groupby('zone_name')['y'].sum().reset_index()
                zone_consumption.columns = ['zone', 'total_consumption']
                
                zone_stats = zone_stats.merge(zone_consumption, on='zone', how='left')
                zone_stats['total_consumption'] = zone_stats['total_consumption'].fillna(0)
            
            # Tri par nombre de bâtiments
            zone_stats = zone_stats.sort_values('building_count', ascending=True)
            
            fig = go.Figure()
            
            # Barres horizontales pour les bâtiments
            fig.add_trace(go.Bar(
                y=zone_stats['zone'],
                x=zone_stats['building_count'],
                name='Nombre de Bâtiments',
                marker_color=self.color_palette['primary'],
                orientation='h'
            ))
            
            fig.update_layout(
                title='Nombre de Bâtiments par Zone',
                xaxis_title='Nombre de Bâtiments',
                yaxis_title='Zone',
                height=max(400, len(zone_stats) * 40),
                **self.dark_template['layout']
            )
            
            return json.loads(fig.to_json())
            
        except Exception as e:
            logger.error(f"Erreur analyse zones: {e}")
            return self._create_empty_chart("Analyse par Zone")
    
    def create_surface_distribution_chart(self, buildings_df: pd.DataFrame) -> Dict:
        """Distribution des surfaces de bâtiments"""
        try:
            if buildings_df.empty or 'surface_area_m2' not in buildings_df.columns:
                return self._create_empty_chart("Distribution des Surfaces")
            
            # Histogramme des surfaces
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=buildings_df['surface_area_m2'],
                nbinsx=30,
                name='Distribution des Surfaces',
                marker_color=self.color_palette['info'],
                opacity=0.7
            ))
            
            # Ligne de médiane
            median_surface = buildings_df['surface_area_m2'].median()
            fig.add_vline(
                x=median_surface,
                line_dash="dash",
                line_color=self.color_palette['danger'],
                annotation_text=f"Médiane: {median_surface:.0f} m²"
            )
            
            fig.update_layout(
                title='Distribution des Surfaces de Bâtiments',
                xaxis_title='Surface (m²)',
                yaxis_title='Nombre de Bâtiments',
                **self.dark_template['layout']
            )
            
            return json.loads(fig.to_json())
            
        except Exception as e:
            logger.error(f"Erreur distribution surfaces: {e}")
            return self._create_empty_chart("Distribution des Surfaces")
    
    def create_consumption_by_building_type_chart(self, buildings_df: pd.DataFrame,
                                                consumption_df: pd.DataFrame) -> Dict:
        """Consommation par type de bâtiment"""
        try:
            if buildings_df.empty or consumption_df.empty:
                return self._create_empty_chart("Consommation par Type")
            
            # Jointure des données
            consumption_by_building = consumption_df.groupby('unique_id')['y'].sum().reset_index()
            consumption_by_building.columns = ['unique_id', 'total_consumption']
            
            merged_data = buildings_df[['unique_id', 'building_type']].merge(
                consumption_by_building, on='unique_id', how='inner'
            )
            
            # Agrégation par type
            type_consumption = merged_data.groupby('building_type').agg({
                'total_consumption': ['sum', 'mean', 'count']
            }).round(2)
            
            type_consumption.columns = ['total_consumption', 'avg_consumption', 'building_count']
            type_consumption = type_consumption.reset_index()
            
            # Tri par consommation totale
            type_consumption = type_consumption.sort_values('total_consumption', ascending=False)
            
            fig = go.Figure()
            
            # Couleurs par type
            colors = [
                self.building_colors.get(btype, self.color_palette['secondary'])
                for btype in type_consumption['building_type']
            ]
            
            fig.add_trace(go.Bar(
                x=type_consumption['building_type'],
                y=type_consumption['total_consumption'],
                name='Consommation Totale',
                marker_color=colors,
                hovertemplate='<b>%{x}</b><br>Consommation: %{y:.1f} kWh<br>Bâtiments: %{customdata}<extra></extra>',
                customdata=type_consumption['building_count']
            ))
            
            fig.update_layout(
                title='Consommation Totale par Type de Bâtiment',
                xaxis_title='Type de Bâtiment',
                yaxis_title='Consommation Totale (kWh)',
                xaxis={'tickangle': 45},
                **self.dark_template['layout']
            )
            
            return json.loads(fig.to_json())
            
        except Exception as e:
            logger.error(f"Erreur consommation par type: {e}")
            return self._create_empty_chart("Consommation par Type")
    
    def _filter_by_timerange(self, df: pd.DataFrame, time_range: str) -> pd.DataFrame:
        """Filtre un DataFrame par période"""
        if df.empty or 'timestamp' not in df.columns:
            return df
        
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            end_date = df['timestamp'].max()
            
            if time_range == '7d':
                start_date = end_date - pd.Timedelta(days=7)
            elif time_range == '30d':
                start_date = end_date - pd.Timedelta(days=30)
            elif time_range == '90d':
                start_date = end_date - pd.Timedelta(days=90)
            else:
                return df
            
            return df[df['timestamp'] >= start_date]
            
        except Exception as e:
            logger.error(f"Erreur filtrage temporel: {e}")
            return df
    
    def _create_empty_chart(self, title: str) -> Dict:
        """Crée un graphique vide avec message"""
        fig = go.Figure()
        
        fig.add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="#6b7280")
        )
        
        fig.update_layout(
            title=title,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            **self.dark_template['layout']
        )
        
        return json.loads(fig.to_json())
    
    def create_kpi_metrics(self, data: Dict) -> Dict:
        """Crée les métriques KPI pour le dashboard"""
        try:
            kpis = {}
            
            # KPIs Bâtiments
            if data.get('buildings') is not None:
                buildings_df = data['buildings']
                kpis['buildings'] = {
                    'total_count': len(buildings_df),
                    'total_surface': float(buildings_df['surface_area_m2'].sum()) if 'surface_area_m2' in buildings_df.columns else 0,
                    'avg_surface': float(buildings_df['surface_area_m2'].mean()) if 'surface_area_m2' in buildings_df.columns else 0,
                    'unique_types': len(buildings_df['building_type'].unique()) if 'building_type' in buildings_df.columns else 0
                }
            
            # KPIs Consommation
            if data.get('consumption') is not None:
                consumption_df = data['consumption']
                if 'y' in consumption_df.columns:
                    kpis['consumption'] = {
                        'total_consumption': float(consumption_df['y'].sum()),
                        'avg_consumption': float(consumption_df['y'].mean()),
                        'peak_consumption': float(consumption_df['y'].max()),
                        'data_points': len(consumption_df)
                    }
            
            # KPIs Période
            if data.get('consumption') is not None and 'timestamp' in data['consumption'].columns:
                timestamps = pd.to_datetime(data['consumption']['timestamp'])
                kpis['period'] = {
                    'start_date': timestamps.min().isoformat(),
                    'end_date': timestamps.max().isoformat(),
                    'duration_days': (timestamps.max() - timestamps.min()).days
                }
            
            return kpis
            
        except Exception as e:
            logger.error(f"Erreur calcul KPIs: {e}")
            return {}
    
    def create_real_time_dashboard_data(self, data: Dict) -> Dict:
        """
        Crée un package complet de données pour le dashboard temps réel
        
        Args:
            data: Données complètes
            
        Returns:
            Dict: Package dashboard avec graphiques et métriques
        """
        try:
            dashboard_package = {
                'timestamp': pd.Timestamp.now().isoformat(),
                'status': 'success'
            }
            
            # KPIs principaux
            dashboard_package['kpis'] = self.create_kpi_metrics(data)
            
            # Graphiques overview
            dashboard_package['overview_charts'] = self.create_overview_charts(data)
            
            # Graphiques de consommation
            dashboard_package['consumption_charts'] = self.create_consumption_charts(data)
            
            # Graphiques supplémentaires
            if data.get('buildings') is not None:
                dashboard_package['building_charts'] = {
                    'zone_analysis': self.create_zone_analysis_chart(data['buildings'], data.get('consumption')),
                    'surface_distribution': self.create_surface_distribution_chart(data['buildings'])
                }
                
                if data.get('consumption') is not None:
                    dashboard_package['building_charts']['consumption_by_type'] = \
                        self.create_consumption_by_building_type_chart(data['buildings'], data['consumption'])
            
            # Méta-informations
            dashboard_package['meta'] = {
                'charts_generated': len([
                    v for v in dashboard_package.values() 
                    if isinstance(v, dict) and 'data' in str(v)
                ]),
                'data_sources': list(data.keys()),
                'generation_time': pd.Timestamp.now().isoformat()
            }
            
            return dashboard_package
            
        except Exception as e:
            logger.error(f"Erreur création package dashboard: {e}")
            return {
                'timestamp': pd.Timestamp.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }

    def get_chart_color_palette(self) -> Dict:
        """Retourne la palette de couleurs utilisée"""
        return {
            'colors': self.color_palette,
            'building_colors': self.building_colors,
            'theme': 'dark'
        }

    def validate_chart_data(self, data: Dict) -> Dict:
        """
        Valide les données avant génération de graphiques
        
        Args:
            data: Données à valider
            
        Returns:
            Dict: Résultat de validation
        """
        validation_result = {
            'valid': True,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Validation bâtiments
            if data.get('buildings') is not None:
                buildings_df = data['buildings']
                
                if buildings_df.empty:
                    validation_result['issues'].append("Données bâtiments vides")
                    validation_result['valid'] = False
                
                required_cols = ['unique_id', 'latitude', 'longitude']
                missing_cols = [col for col in required_cols if col not in buildings_df.columns]
                if missing_cols:
                    validation_result['issues'].append(f"Colonnes manquantes bâtiments: {missing_cols}")
                
                # Validation coordonnées
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
                        validation_result['issues'].append(
                            f"{len(invalid_coords)} bâtiments avec coordonnées invalides"
                        )
            
            # Validation consommation
            if data.get('consumption') is not None:
                consumption_df = data['consumption']
                
                if consumption_df.empty:
                    validation_result['issues'].append("Données consommation vides")
                    validation_result['valid'] = False
                
                if 'y' not in consumption_df.columns:
                    validation_result['issues'].append("Colonne 'y' manquante dans consommation")
                    validation_result['valid'] = False
                
                if 'timestamp' not in consumption_df.columns:
                    validation_result['issues'].append("Colonne 'timestamp' manquante dans consommation")
                
                # Validation valeurs négatives
                if 'y' in consumption_df.columns:
                    negative_values = consumption_df[consumption_df['y'] < 0]
                    if len(negative_values) > 0:
                        validation_result['issues'].append(
                            f"{len(negative_values)} valeurs de consommation négatives"
                        )
            
            # Recommandations
            if len(validation_result['issues']) == 0:
                validation_result['recommendations'].append("Données prêtes pour génération graphiques")
            else:
                validation_result['recommendations'].append("Nettoyer les données avant génération")
                validation_result['valid'] = False
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Erreur validation données: {e}")
            return {
                'valid': False,
                'issues': [f"Erreur validation: {str(e)}"],
                'recommendations': ["Vérifier l'intégrité des données"]
            }

    def get_chart_recommendations(self, data: Dict) -> List[str]:
        """
        Génère des recommandations pour améliorer les visualisations
        
        Args:
            data: Données disponibles
            
        Returns:
            List[str]: Liste de recommandations
        """
        recommendations = []
        
        try:
            buildings_df = data.get('buildings')
            consumption_df = data.get('consumption')
            weather_df = data.get('weather')
            
            # Recommandations basées sur les données disponibles
            if buildings_df is not None and not buildings_df.empty:
                if len(buildings_df) > 1000:
                    recommendations.append("Utilisez le clustering sur la carte pour améliorer les performances")
                
                if 'building_type' in buildings_df.columns:
                    unique_types = buildings_df['building_type'].nunique()
                    if unique_types > 10:
                        recommendations.append("Groupez les types de bâtiments moins fréquents dans 'Autres'")
            
            if consumption_df is not None and not consumption_df.empty:
                if len(consumption_df) > 50000:
                    recommendations.append("Utilisez l'agrégation temporelle pour réduire le nombre de points")
                
                # Vérification de la couverture temporelle
                if 'timestamp' in consumption_df.columns:
                    timestamps = pd.to_datetime(consumption_df['timestamp'])
                    duration = (timestamps.max() - timestamps.min()).days
                    
                    if duration < 7:
                        recommendations.append("Collectez plus de données historiques pour l'analyse de tendances")
                    elif duration > 365:
                        recommendations.append("Utilisez des filtres temporels pour les analyses détaillées")
            
            if weather_df is not None and not weather_df.empty:
                weather_cols = [col for col in weather_df.columns if col not in ['unique_id', 'timestamp']]
                if len(weather_cols) > 10:
                    recommendations.append("Créez une matrice de corrélation pour identifier les variables météo clés")
            
            # Recommandations générales
            if not recommendations:
                recommendations.append("Vos données sont bien structurées pour la visualisation")
            
            recommendations.append("Utilisez les filtres interactifs pour explorer différentes perspectives")
            recommendations.append("Exportez les graphiques pour vos rapports et présentations")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur génération recommandations: {e}")
            return ["Erreur lors de l'analyse - vérifiez la qualité des données"]


# ==============================================================================
# UTILITAIRES ET TESTS
# ==============================================================================

def test_chart_generator():
    """Test du générateur de graphiques"""
    import pandas as pd
    
    # Données de test
    buildings_data = pd.DataFrame({
        'unique_id': ['B001', 'B002', 'B003'],
        'building_type': ['residential', 'commercial', 'industrial'],
        'surface_area_m2': [120, 500, 1200],
        'zone_name': ['Kuala Lumpur', 'Selangor', 'Johor'],
        'latitude': [3.1390, 3.1500, 3.1600],
        'longitude': [101.6869, 101.7000, 101.7100]
    })
    
    consumption_data = pd.DataFrame({
        'unique_id': ['B001'] * 24 + ['B002'] * 24,
        'timestamp': pd.date_range('2024-01-01', periods=48, freq='H'),
        'y': np.random.uniform(10, 50, 48)
    })
    
    test_data = {
        'buildings': buildings_data,
        'consumption': consumption_data,
        'weather': None,
        'water': None
    }
    
    generator = ChartGenerator()
    
    print("📊 Test ChartGenerator:")
    
    # Validation des données
    validation = generator.validate_chart_data(test_data)
    print(f"Validation: {validation['valid']}")
    if validation['issues']:
        print(f"Issues: {validation['issues']}")
    
    # Test overview charts
    overview_charts = generator.create_overview_charts(test_data)
    print(f"Graphiques overview: {list(overview_charts.keys())}")
    
    # Test consumption charts
    consumption_charts = generator.create_consumption_charts(test_data)
    print(f"Graphiques consommation: {list(consumption_charts.keys())}")
    
    # Test KPIs
    kpis = generator.create_kpi_metrics(test_data)
    print(f"KPIs calculés: {list(kpis.keys())}")
    
    # Test package complet
    dashboard_package = generator.create_real_time_dashboard_data(test_data)
    print(f"Package dashboard: {dashboard_package['status']}")
    print(f"Méta: {dashboard_package.get('meta', {})}")
    
    return generator


if __name__ == '__main__':
    test_chart_generator()