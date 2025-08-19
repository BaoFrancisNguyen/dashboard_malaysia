#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UTILITAIRES ET HELPERS - DASHBOARD MALAYSIA
==========================================

Fonctions utilitaires et helpers pour le dashboard Malaysia

Version: 1.0.0
"""

import os
import sys
import logging
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import hashlib


def setup_dashboard_logging(log_level: str = 'INFO', log_file: str = None) -> logging.Logger:
    """
    Configure le système de logging pour le dashboard
    
    Args:
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR)
        log_file: Fichier de log (optionnel)
        
    Returns:
        logging.Logger: Logger configuré
    """
    # Configuration du format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configuration du niveau
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configuration de base
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format
    )
    
    # Logger principal
    logger = logging.getLogger('dashboard_malaysia')
    
    # Ajout d'un handler fichier si spécifié
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        logger.addHandler(file_handler)
    
    logger.info("✅ Système de logging initialisé")
    return logger


def validate_malaysia_coordinates(lat: float, lon: float) -> bool:
    """
    Valide si des coordonnées sont dans les limites de Malaysia
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        bool: True si valide
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


def clean_building_type(building_type: str) -> str:
    """
    Nettoie et normalise les types de bâtiments
    
    Args:
        building_type: Type de bâtiment brut
        
    Returns:
        str: Type normalisé
    """
    if not isinstance(building_type, str):
        return 'other'
    
    # Nettoyage de base
    cleaned = building_type.lower().strip()
    
    # Mapping des types courants
    type_mapping = {
        'residential': ['residential', 'house', 'apartment', 'home', 'residence'],
        'commercial': ['commercial', 'shop', 'store', 'mall', 'retail'],
        'industrial': ['industrial', 'factory', 'warehouse', 'manufacturing'],
        'office': ['office', 'business', 'corporate'],
        'school': ['school', 'education', 'university', 'college'],
        'hospital': ['hospital', 'medical', 'clinic', 'healthcare'],
        'hotel': ['hotel', 'accommodation', 'lodge', 'resort'],
        'mixed': ['mixed', 'mixed_use', 'multiple']
    }
    
    # Recherche du type correspondant
    for standard_type, variants in type_mapping.items():
        if any(variant in cleaned for variant in variants):
            return standard_type
    
    return 'other'


def calculate_building_efficiency(consumption: float, surface_area: float) -> float:
    """
    Calcule l'efficacité énergétique d'un bâtiment
    
    Args:
        consumption: Consommation totale (kWh)
        surface_area: Surface du bâtiment (m²)
        
    Returns:
        float: Efficacité (kWh/m²)
    """
    if surface_area <= 0:
        return float('inf')
    
    return consumption / surface_area


def categorize_efficiency(efficiency: float) -> str:
    """
    Catégorise l'efficacité énergétique
    
    Args:
        efficiency: Efficacité (kWh/m²)
        
    Returns:
        str: Catégorie (excellent, good, average, poor, very_poor)
    """
    if efficiency <= 50:
        return 'excellent'
    elif efficiency <= 100:
        return 'good'
    elif efficiency <= 150:
        return 'average'
    elif efficiency <= 200:
        return 'poor'
    else:
        return 'very_poor'


def generate_unique_id(prefix: str = 'ID', length: int = 8) -> str:
    """
    Génère un identifiant unique
    
    Args:
        prefix: Préfixe de l'ID
        length: Longueur de la partie aléatoire
        
    Returns:
        str: ID unique
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = hashlib.md5(timestamp.encode()).hexdigest()[:length]
    return f"{prefix}_{random_part}"


def format_number(number: Union[int, float], unit: str = '', decimals: int = 1) -> str:
    """
    Formate un nombre pour l'affichage
    
    Args:
        number: Nombre à formater
        unit: Unité à ajouter
        decimals: Nombre de décimales
        
    Returns:
        str: Nombre formaté
    """
    if pd.isna(number) or number is None:
        return 'N/A'
    
    try:
        if abs(number) >= 1_000_000:
            formatted = f"{number/1_000_000:.{decimals}f}M"
        elif abs(number) >= 1_000:
            formatted = f"{number/1_000:.{decimals}f}k"
        else:
            formatted = f"{number:.{decimals}f}"
        
        return f"{formatted} {unit}".strip()
        
    except (ValueError, TypeError):
        return str(number)


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formate un pourcentage
    
    Args:
        value: Valeur (0-1 ou 0-100)
        decimals: Nombre de décimales
        
    Returns:
        str: Pourcentage formaté
    """
    if pd.isna(value) or value is None:
        return 'N/A'
    
    try:
        # Si la valeur est entre 0 et 1, multiplier par 100
        if 0 <= value <= 1:
            percentage = value * 100
        else:
            percentage = value
        
        return f"{percentage:.{decimals}f}%"
        
    except (ValueError, TypeError):
        return str(value)


def format_datetime(dt: Union[str, datetime, pd.Timestamp], format_type: str = 'default') -> str:
    """
    Formate une date/heure
    
    Args:
        dt: Date/heure à formater
        format_type: Type de format (default, short, long, time_only)
        
    Returns:
        str: Date/heure formatée
    """
    if pd.isna(dt) or dt is None:
        return 'N/A'
    
    try:
        if isinstance(dt, str):
            dt = pd.to_datetime(dt)
        
        formats = {
            'default': '%Y-%m-%d %H:%M',
            'short': '%d/%m/%Y',
            'long': '%d %B %Y à %H:%M',
            'time_only': '%H:%M',
            'iso': '%Y-%m-%dT%H:%M:%S'
        }
        
        format_str = formats.get(format_type, formats['default'])
        return dt.strftime(format_str)
        
    except (ValueError, TypeError):
        return str(dt)


def calculate_time_range_dates(range_type: str) -> tuple:
    """
    Calcule les dates de début et fin pour une période
    
    Args:
        range_type: Type de période (7d, 30d, 90d, 1y)
        
    Returns:
        tuple: (start_date, end_date)
    """
    end_date = datetime.now()
    
    range_mapping = {
        '7d': timedelta(days=7),
        '30d': timedelta(days=30),
        '90d': timedelta(days=90),
        '1y': timedelta(days=365),
        '1h': timedelta(hours=1),
        '24h': timedelta(hours=24),
        '1w': timedelta(weeks=1),
        '1m': timedelta(days=30)
    }
    
    delta = range_mapping.get(range_type, timedelta(days=7))
    start_date = end_date - delta
    
    return start_date, end_date


def detect_outliers(data: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
    """
    Détecte les valeurs aberrantes dans une série
    
    Args:
        data: Série de données
        method: Méthode de détection ('iqr', 'zscore', 'percentile')
        threshold: Seuil de détection
        
    Returns:
        pd.Series: Masque booléen des outliers
    """
    if data.empty:
        return pd.Series([], dtype=bool)
    
    try:
        if method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            return (data < lower_bound) | (data > upper_bound)
        
        elif method == 'zscore':
            z_scores = np.abs((data - data.mean()) / data.std())
            return z_scores > threshold
        
        elif method == 'percentile':
            lower_percentile = data.quantile(threshold / 100)
            upper_percentile = data.quantile(1 - threshold / 100)
            return (data < lower_percentile) | (data > upper_percentile)
        
        else:
            return pd.Series([False] * len(data), index=data.index)
            
    except Exception:
        return pd.Series([False] * len(data))