// dashboard/static/js/modules/dashboard-maps.js
/**
 * DASHBOARD MALAYSIA - MODULE MAPS
 * ================================
 * 
 * Module pour la gestion de la cartographie Leaflet
 * Version: 1.0.0
 */

const DashboardMaps = {
    /**
     * Initialisation du module
     */
    init() {
        console.log('🗺️ Initialisation module Maps');
        this.loadBuildingsContent();
        this.initializeMap();
        Dashboard.registerModule('maps', this);
    },

    /**
     * Chargement du contenu de l'onglet Bâtiments
     */
    loadBuildingsContent() {
        const buildings = document.getElementById('buildings');
        if (!buildings) return;

        buildings.innerHTML = `
            <div class="row mb-4">
                <div class="col-md-8">
                    <h2 class="h3 mb-2">
                        <i class="bi bi-building text-primary me-2"></i>
                        Analyse des Bâtiments
                    </h2>
                    <p class="text-muted">Cartographie interactive et analyse géospatiale</p>
                </div>
                <div class="col-md-4">
                    <div class="btn-group w-100">
                        <button class="btn btn-outline-primary active" onclick="DashboardMaps.showBuildingsView()">
                            <i class="bi bi-building me-1"></i>
                            Bâtiments
                        </button>
                        <button class="btn btn-outline-danger" onclick="DashboardMaps.showHeatmapView()">
                            <i class="bi bi-thermometer-half me-1"></i>
                            Heatmap
                        </button>
                    </div>
                </div>
            </div>

            <div class="row g-4">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header bg-transparent border-bottom">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">
                                    <i class="bi bi-geo-alt text-success me-2"></i>
                                    Carte Interactive Malaysia
                                </h5>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-light" onclick="DashboardMaps.fitMapToData()">
                                        <i class="bi bi-arrows-fullscreen me-1"></i>
                                        Ajuster
                                    </button>
                                    <button class="btn btn-outline-light" onclick="DashboardMaps.resetMapView()">
                                        <i class="bi bi-arrow-clockwise me-1"></i>
                                        Reset
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="card-body p-0 position-relative">
                            <div id="buildings-map" class="map-container">
                                <div class="d-flex justify-content-center align-items-center h-100">
                                    <div class="text-center">
                                        <i class="bi bi-geo-alt fs-1 text-muted"></i>
                                        <p class="mt-2 text-muted">Initialisation de la carte...</p>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Contrôles carte -->
                            <div class="map-controls">
                                <div class="d-flex flex-column gap-3">
                                    <div>
                                        <label class="form-label text-light small mb-2">
                                            <i class="bi bi-layers me-1"></i>
                                            Densité d'affichage:
                                        </label>
                                        <input type="range" class="form-range" id="map-density" 
                                               min="10" max="100" value="100" step="10"
                                               onchange="DashboardMaps.updateMapDensity(this.value)">
                                        <div class="d-flex justify-content-between">
                                            <small class="text-muted">10%</small>
                                            <small class="text-warning fw-bold">
                                                <span id="density-display">100</span>%
                                            </small>
                                            <small class="text-muted">100%</small>
                                        </div>
                                    </div>
                                    <div>
                                        <label class="form-label text-light small mb-2">
                                            <i class="bi bi-funnel me-1"></i>
                                            Filtre par type:
                                        </label>
                                        <select class="form-select form-select-sm" id="map-type-filter" 
                                                onchange="DashboardMaps.updateMapTypeFilter(this.value)">
                                            <option value="all">Tous types</option>
                                            <option value="residential">Résidentiel</option>
                                            <option value="commercial">Commercial</option>
                                            <option value="industrial">Industriel</option>
                                            <option value="office">Bureau</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Légende -->
                            <div class="map-legend" id="map-legend">
                                <h6 class="small mb-2">
                                    <i class="bi bi-palette me-1"></i>
                                    Types de Bâtiments
                                </h6>
                                <div id="legend-items">
                                    <div class="d-flex align-items-center mb-1">
                                        <div class="rounded-circle me-2" style="width: 12px; height: 12px; background: #28a745;"></div>
                                        <small>Résidentiel</small>
                                    </div>
                                    <div class="d-flex align-items-center mb-1">
                                        <div class="rounded-circle me-2" style="width: 12px; height: 12px; background: #007bff;"></div>
                                        <small>Commercial</small>
                                    </div>
                                    <div class="d-flex align-items-center mb-1">
                                        <div class="rounded-circle me-2" style="width: 12px; height: 12px; background: #dc3545;"></div>
                                        <small>Industriel</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card mb-3">
                        <div class="card-header bg-transparent border-bottom">
                            <h5 class="mb-0">
                                <i class="bi bi-bar-chart text-info me-2"></i>
                                Statistiques Carte
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="map-statistics">
                                <div class="row text-center mb-3">
                                    <div class="col-6">
                                        <div class="border-end">
                                            <div class="h4 text-primary mb-1" id="map-total-buildings">-</div>
                                            <small class="text-muted">Total</small>
                                        </div>
                                    </div>
                                    <div class="col-6">
                                        <div class="h4 text-success mb-1" id="map-displayed">-</div>
                                        <small class="text-muted">Affichés</small>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <h6 class="small mb-2">
                                        <i class="bi bi-pie-chart me-1"></i>
                                        Répartition par Type
                                    </h6>
                                    <div id="type-breakdown">
                                        <div class="loading-skeleton mb-2"></div>
                                        <div class="loading-skeleton mb-2"></div>
                                        <div class="loading-skeleton"></div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <h6 class="small mb-2">
                                        <i class="bi bi-compass me-1"></i>
                                        Couverture Géographique
                                    </h6>
                                    <div class="row text-center small">
                                        <div class="col-6">
                                            <div class="text-muted">Nord</div>
                                            <div class="fw-bold" id="geo-north">-</div>
                                        </div>
                                        <div class="col-6">
                                            <div class="text-muted">Sud</div>
                                            <div class="fw-bold" id="geo-south">-</div>
                                        </div>
                                    </div>
                                    <div class="row text-center small mt-2">
                                        <div class="col-6">
                                            <div class="text-muted">Est</div>
                                            <div class="fw-bold" id="geo-east">-</div>
                                        </div>
                                        <div class="col-6">
                                            <div class="text-muted">Ouest</div>
                                            <div class="fw-bold" id="geo-west">-</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header bg-transparent border-bottom">
                            <h5 class="mb-0">
                                <i class="bi bi-list-ol text-warning me-2"></i>
                                Zones Principales
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="top-zones">
                                <div class="loading-skeleton mb-3" style="height: 60px;"></div>
                                <div class="loading-skeleton mb-3" style="height: 60px;"></div>
                                <div class="loading-skeleton" style="height: 60px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Initialisation de la carte Leaflet
     */
    async initializeMap() {
        try {
            Dashboard.state.map = L.map('buildings-map', {
                center: [4.2105, 101.9758],
                zoom: 6,
                zoomControl: true,
                scrollWheelZoom: true
            });

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 18
            }).addTo(Dashboard.state.map);

            console.log('✅ Carte Leaflet initialisée');
        } catch (error) {
            console.error('Erreur initialisation carte:', error);
        }
    },

    /**
     * Chargement des données cartographiques
     */
    async loadMapData() {
        if (!Dashboard.state.map) return;

        try {
            await this.showBuildingsView();
            await this.updateMapStatistics();
        } catch (error) {
            console.error('Erreur chargement données carte:', error);
        }
    },

    /**
     * Affichage des bâtiments sur la carte
     */
    async showBuildingsView() {
        try {
            const density = document.getElementById('map-density')?.value || 100;
            const typeFilter = document.getElementById('map-type-filter')?.value || 'all';

            const response = await fetch(`/api/map/buildings?density=${density}&type=${typeFilter}`);
            const result = await response.json();

            if (result.success) {
                this.renderBuildingsOnMap(result.map_data);
            }
        } catch (error) {
            console.error('Erreur affichage bâtiments:', error);
        }
    },

    /**
     * Rendu des bâtiments sur la carte
     */
    renderBuildingsOnMap(mapData) {
        if (!Dashboard.state.map || !mapData.markers) return;

        // Clear existing layers
        Dashboard.state.map.eachLayer(layer => {
            if (layer instanceof L.CircleMarker) {
                Dashboard.state.map.removeLayer(layer);
            }
        });

        // Add markers
        mapData.markers.forEach(markerData => {
            const marker = L.circleMarker([markerData.lat, markerData.lng], {
                radius: 6,
                fillColor: markerData.color,
                color: '#fff',
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            });

            marker.bindPopup(markerData.popup);
            marker.addTo(Dashboard.state.map);
        });

        // Update map view
        if (mapData.center && mapData.zoom) {
            Dashboard.state.map.setView(mapData.center, mapData.zoom);
        }

        console.log(`✅ ${mapData.markers.length} bâtiments affichés`);
    },

    /**
     * Affichage de la heatmap
     */
    async showHeatmapView() {
        try {
            Dashboard.showToast('🌡️ Chargement de la heatmap...', 'info');
            
            const response = await fetch('/api/map/consumption-heatmap');
            const result = await response.json();

            if (result.success) {
                this.renderConsumptionHeatmap(result.heatmap_data);
            }
        } catch (error) {
            console.error('Erreur heatmap:', error);
        }
    },

    /**
     * Rendu de la heatmap de consommation
     */
    renderConsumptionHeatmap(heatmapData) {
        if (!Dashboard.state.map || !heatmapData.heatmap_points) return;

        // Clear existing layers
        Dashboard.state.map.eachLayer(layer => {
            if (layer instanceof L.CircleMarker || layer instanceof L.HeatLayer) {
                Dashboard.state.map.removeLayer(layer);
            }
        });

        if (heatmapData.heatmap_points.length > 0) {
            // Prepare heatmap data
            const heatPoints = heatmapData.heatmap_points.map(point => [
                point.lat,
                point.lng,
                point.intensity
            ]);

            // Create heat layer
            const heatLayer = L.heatLayer(heatPoints, {
                radius: 25,
                blur: 15,
                maxZoom: 17,
                gradient: {
                    0.0: 'blue',
                    0.3: 'cyan',
                    0.5: 'lime',
                    0.7: 'yellow',
                    1.0: 'red'
                }
            });

            heatLayer.addTo(Dashboard.state.map);

            // Adjust view
            if (heatmapData.center) {
                Dashboard.state.map.setView(heatmapData.center, heatmapData.zoom || 7);
            }

            console.log(`✅ Heatmap avec ${heatmapData.heatmap_points.length} points`);
        }
    },

    /**
     * Mise à jour des statistiques cartographiques
     */
    async updateMapStatistics() {
        try {
            const [statsResponse, zonesResponse] = await Promise.all([
                fetch('/api/map/statistics'),
                fetch('/api/map/zones')
            ]);

            const statsResult = await statsResponse.json();
            const zonesResult = await zonesResponse.json();

            if (statsResult.success) {
                this.updateMapStatsDisplay(statsResult.statistics);
            }

            if (zonesResult.success) {
                this.updateTopZones(zonesResult.zones_data.zones);
            }
        } catch (error) {
            console.error('Erreur statistiques carte:', error);
        }
    },

    /**
     * Mise à jour de l'affichage des statistiques
     */
    updateMapStatsDisplay(stats) {
        document.getElementById('map-total-buildings').textContent = Dashboard.formatNumber(stats.total_buildings || 0);
        document.getElementById('map-displayed').textContent = Dashboard.formatNumber(stats.valid_coordinates || 0);
        
        if (stats.geographic_coverage) {
            const bounds = stats.geographic_coverage;
            document.getElementById('geo-north').textContent = bounds.north?.toFixed(3) || '-';
            document.getElementById('geo-south').textContent = bounds.south?.toFixed(3) || '-';
            document.getElementById('geo-east').textContent = bounds.east?.toFixed(3) || '-';
            document.getElementById('geo-west').textContent = bounds.west?.toFixed(3) || '-';
        }
    },

    /**
     * Mise à jour des zones principales
     */
    updateTopZones(zones) {
        const container = document.getElementById('top-zones');
        container.innerHTML = '';

        if (zones && zones.length > 0) {
            zones.slice(0, 5).forEach((zone, index) => {
                const zoneElement = document.createElement('div');
                zoneElement.className = 'mb-3 p-3 border rounded-3 bg-dark';
                zoneElement.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <strong class="text-primary">${zone.name}</strong>
                        <span class="badge bg-primary">#${index + 1}</span>
                    </div>
                    <div class="row text-center small">
                        <div class="col-4">
                            <div class="text-muted">Bâtiments</div>
                            <div class="fw-bold">${zone.building_count}</div>
                        </div>
                        <div class="col-4">
                            <div class="text-muted">Surface</div>
                            <div class="fw-bold">${Dashboard.formatNumber(zone.total_surface / 1000)}k m²</div>
                        </div>
                        <div class="col-4">
                            <div class="text-muted">Densité</div>
                            <span class="badge bg-${this.getDensityColor(zone.density_level)}">${zone.density_level}</span>
                        </div>
                    </div>
                `;
                container.appendChild(zoneElement);
            });
        }
    },

    /**
     * Couleur selon le niveau de densité
     */
    getDensityColor(level) {
        const colors = {
            'high': 'danger',
            'medium': 'warning', 
            'low': 'info',
            'very_low': 'secondary'
        };
        return colors[level] || 'secondary';
    },

    /**
     * Mise à jour de la densité d'affichage
     */
    updateMapDensity(value) {
        document.getElementById('density-display').textContent = value;
        this.showBuildingsView();
    },

    /**
     * Mise à jour du filtre par type
     */
    updateMapTypeFilter(value) {
        this.showBuildingsView();
    },

    /**
     * Ajustement de la carte aux données
     */
    fitMapToData() {
        if (Dashboard.state.map) {
            Dashboard.state.map.fitBounds([[1, 99], [7, 120]]);
        }
    },

    /**
     * Remise à zéro de la vue
     */
    resetMapView() {
        if (Dashboard.state.map) {
            Dashboard.state.map.setView([4.2105, 101.9758], 6);
        }
    },

    /**
     * Export des données cartographiques
     */
    exportMapData() {
        Dashboard.showToast('🗺️ Export des données cartographiques...', 'info');
        
        // Génération des données de la carte
        const mapData = this.generateMapDataCSV();
        this.downloadMapCSV(mapData, 'buildings_map_data.csv');
    },

    /**
     * Génération du CSV des données cartographiques
     */
    generateMapDataCSV() {
        const headers = ['building_id', 'latitude', 'longitude', 'building_type', 'surface_area_m2', 'zone_name'];
        const sampleData = [
            ['B001', '3.1390', '101.6869', 'residential', '120', 'Kuala Lumpur'],
            ['B002', '3.1500', '101.7000', 'commercial', '850', 'Selangor'],
            ['B003', '3.1600', '101.7100', 'industrial', '2400', 'Johor']
        ];
        
        let csv = headers.join(',') + '\n';
        sampleData.forEach(row => {
            csv += row.join(',') + '\n';
        });
        
        return csv;
    },

    /**
     * Téléchargement de fichier CSV cartographique
     */
    downloadMapCSV(content, filename) {
        const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            Dashboard.showToast('✅ Données cartographiques exportées', 'success');
        }
    },

    /**
     * Screenshot de la carte
     */
    exportMapScreenshot() {
        Dashboard.showToast('📸 Capture de la carte...', 'info');
        
        const mapElement = document.getElementById('buildings-map');
        if (mapElement) {
            // Utilisation de html2canvas si disponible, sinon simulation
            if (window.html2canvas) {
                html2canvas(mapElement).then(canvas => {
                    const link = document.createElement('a');
                    link.download = `map_screenshot_${new Date().toISOString().split('T')[0]}.png`;
                    link.href = canvas.toDataURL();
                    link.click();
                    Dashboard.showToast('📸 Capture sauvegardée', 'success');
                });
            } else {
                setTimeout(() => {
                    Dashboard.showToast('📸 Capture simulée (html2canvas requis)', 'warning');
                }, 1000);
            }
        }
    }
};

// Auto-initialisation quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    DashboardMaps.init();
});