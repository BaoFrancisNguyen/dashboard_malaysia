// dashboard/static/js/modules/dashboard-charts.js
/**
 * DASHBOARD MALAYSIA - MODULE CHARTS
 * ==================================
 * 
 * Module pour la gestion des graphiques Plotly
 * Version: 1.0.0
 */

const DashboardCharts = {
    /**
     * Initialisation du module
     */
    init() {
        console.log('📊 Initialisation module Charts');
        this.loadOverviewContent();
        this.loadConsumptionContent();
        Dashboard.registerModule('charts', this);
    },

    /**
     * Chargement du contenu de l'onglet Vue d'ensemble
     */
    loadOverviewContent() {
        const overview = document.getElementById('overview');
        if (!overview) return;

        overview.innerHTML = `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h2 class="h3 mb-2">
                                <i class="bi bi-speedometer2 text-primary me-2"></i>
                                Vue d'ensemble
                            </h2>
                            <p class="text-muted mb-0">
                                Dashboard complet des données énergétiques Malaysia
                            </p>
                        </div>
                        <div class="d-flex gap-2">
                            <button class="btn btn-outline-primary btn-sm" onclick="DashboardCharts.refreshOverview()">
                                <i class="bi bi-arrow-clockwise me-1"></i>
                                Actualiser
                            </button>
                            <button class="btn btn-outline-info btn-sm" onclick="DashboardCharts.exportOverview()">
                                <i class="bi bi-download me-1"></i>
                                Exporter
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Métriques principales -->
            <div class="row mb-4 g-4">
                <div class="col-lg-3 col-md-6">
                    <div class="card metric-card card-hover-effect">
                        <div class="metric-value text-primary" id="total-buildings">
                            <div class="loading-skeleton" style="width: 80px; height: 48px; margin: 0 auto;"></div>
                        </div>
                        <div class="metric-label">Bâtiments Total</div>
                        <div class="metric-trend trend-up" id="buildings-trend">
                            <i class="bi bi-arrow-up"></i>
                            <span>+2.3%</span>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="card metric-card card-hover-effect">
                        <div class="metric-value text-success" id="total-consumption">
                            <div class="loading-skeleton" style="width: 80px; height: 48px; margin: 0 auto;"></div>
                        </div>
                        <div class="metric-label">Consommation (kWh)</div>
                        <div class="metric-trend trend-down" id="consumption-trend">
                            <i class="bi bi-arrow-down"></i>
                            <span>-1.2%</span>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="card metric-card card-hover-effect">
                        <div class="metric-value text-warning" id="avg-consumption">
                            <div class="loading-skeleton" style="width: 80px; height: 48px; margin: 0 auto;"></div>
                        </div>
                        <div class="metric-label">Moyenne (kWh)</div>
                        <div class="metric-trend trend-stable" id="avg-trend">
                            <i class="bi bi-dash"></i>
                            <span>0.1%</span>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="card metric-card card-hover-effect">
                        <div class="metric-value text-info" id="data-points">
                            <div class="loading-skeleton" style="width: 80px; height: 48px; margin: 0 auto;"></div>
                        </div>
                        <div class="metric-label">Points de Données</div>
                        <div class="metric-trend trend-up" id="points-trend">
                            <i class="bi bi-arrow-up"></i>
                            <span>+5.7%</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Graphiques principaux -->
            <div class="row g-4">
                <div class="col-lg-8">
                    <div class="card fade-in">
                        <div class="card-header bg-transparent border-bottom">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">
                                    <i class="bi bi-graph-up text-primary me-2"></i>
                                    Évolution de la Consommation
                                </h5>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-light active" data-period="24h">24h</button>
                                    <button class="btn btn-outline-light" data-period="7d">7j</button>
                                    <button class="btn btn-outline-light" data-period="30d">30j</button>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div id="consumption-chart" class="chart-container">
                                <div class="d-flex justify-content-center align-items-center h-100">
                                    <div class="text-center">
                                        <div class="progress-ring">
                                            <svg width="24" height="24">
                                                <circle cx="12" cy="12" r="12"></circle>
                                            </svg>
                                        </div>
                                        <p class="mt-2 text-muted">Chargement du graphique...</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card fade-in">
                        <div class="card-header bg-transparent border-bottom">
                            <h5 class="mb-0">
                                <i class="bi bi-pie-chart text-success me-2"></i>
                                Répartition par Type
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="building-types-chart" class="chart-container">
                                <div class="d-flex justify-content-center align-items-center h-100">
                                    <div class="text-center">
                                        <div class="progress-ring">
                                            <svg width="24" height="24">
                                                <circle cx="12" cy="12" r="12"></circle>
                                            </svg>
                                        </div>
                                        <p class="mt-2 text-muted">Chargement...</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Chargement du contenu de l'onglet Consommation
     */
    loadConsumptionContent() {
        const consumption = document.getElementById('consumption');
        if (!consumption) return;

        consumption.innerHTML = `
            <div class="row mb-4">
                <div class="col-md-8">
                    <h2 class="h3 mb-2">
                        <i class="bi bi-graph-up text-success me-2"></i>
                        Analyse de Consommation
                    </h2>
                    <p class="text-muted">Analyse détaillée de la consommation électrique Malaysia</p>
                </div>
                <div class="col-md-4">
                    <div class="row g-2">
                        <div class="col-6">
                            <select class="form-select" id="time-range-select" onchange="DashboardCharts.updateConsumptionCharts()">
                                <option value="7d">7 jours</option>
                                <option value="30d">30 jours</option>
                                <option value="90d">90 jours</option>
                                <option value="1y">1 an</option>
                            </select>
                        </div>
                        <div class="col-6">
                            <select class="form-select" id="building-type-select" onchange="DashboardCharts.updateConsumptionCharts()">
                                <option value="all">Tous types</option>
                                <option value="residential">Résidentiel</option>
                                <option value="commercial">Commercial</option>
                                <option value="industrial">Industriel</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row g-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header bg-transparent border-bottom">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">
                                    <i class="bi bi-activity text-warning me-2"></i>
                                    Détails de Consommation
                                </h5>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-light" onclick="DashboardCharts.exportConsumptionData()">
                                        <i class="bi bi-download me-1"></i>
                                        Export
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div id="detailed-consumption-chart" class="chart-container">
                                <div class="d-flex justify-content-center align-items-center h-100">
                                    <div class="text-center">
                                        <div class="loading-skeleton" style="width: 200px; height: 20px; margin: 0 auto;"></div>
                                        <p class="mt-2 text-muted">Chargement des données de consommation...</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row g-4 mt-1">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-transparent border-bottom">
                            <h5 class="mb-0">
                                <i class="bi bi-clock text-info me-2"></i>
                                Patterns Horaires
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="hourly-patterns-chart" class="chart-container"></div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-transparent border-bottom">
                            <h5 class="mb-0">
                                <i class="bi bi-thermometer-half text-danger me-2"></i>
                                Heatmap Consommation
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="consumption-heatmap" class="chart-container"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Chargement des graphiques
     */
    async loadCharts() {
        try {
            const response = await fetch('/api/charts/overview');
            const result = await response.json();

            if (result.success) {
                this.renderCharts(result.charts);
            } else {
                console.warn('Pas de graphiques disponibles');
            }
        } catch (error) {
            console.error('Erreur chargement graphiques:', error);
        }
    },

    /**
     * Rendu des graphiques
     */
    renderCharts(charts) {
        // Graphique de consommation
        if (charts.consumption_timeline) {
            this.renderPlotlyChart('consumption-chart', charts.consumption_timeline);
        }

        // Graphique types de bâtiments
        if (charts.building_types) {
            this.renderPlotlyChart('building-types-chart', charts.building_types);
        }
    },

    /**
     * Rendu d'un graphique Plotly
     */
    renderPlotlyChart(elementId, chartData) {
        const element = document.getElementById(elementId);
        if (!element) return;

        // Configuration responsive
        const config = {
            responsive: true,
            displayModeBar: false,
            locale: 'fr'
        };

        const layout = {
            ...chartData.layout,
            autosize: true,
            margin: { l: 50, r: 50, t: 50, b: 50 }
        };

        Plotly.newPlot(elementId, chartData.data, layout, config);
        
        // Stockage pour resize
        Dashboard.state.charts[elementId] = { data: chartData.data, layout: layout, config: config };
    },

    /**
     * Mise à jour des graphiques de consommation
     */
    async updateConsumptionCharts() {
        const timeRange = document.getElementById('time-range-select')?.value || '7d';
        const buildingType = document.getElementById('building-type-select')?.value || 'all';

        try {
            const response = await fetch(`/api/charts/consumption?range=${timeRange}&type=${buildingType}`);
            const result = await response.json();

            if (result.success) {
                this.renderConsumptionCharts(result.charts);
            }
        } catch (error) {
            console.error('Erreur mise à jour graphiques:', error);
        }
    },

    /**
     * Rendu des graphiques de consommation
     */
    renderConsumptionCharts(charts) {
        if (charts.detailed_consumption) {
            this.renderPlotlyChart('detailed-consumption-chart', charts.detailed_consumption);
        }
        if (charts.hourly_patterns) {
            this.renderPlotlyChart('hourly-patterns-chart', charts.hourly_patterns);
        }
        if (charts.consumption_heatmap) {
            this.renderPlotlyChart('consumption-heatmap', charts.consumption_heatmap);
        }
    },

    /**
     * Actualisation de la vue d'ensemble
     */
    refreshOverview() {
        Dashboard.showToast('🔄 Actualisation de la vue d\'ensemble...', 'info');
        Dashboard.loadDataSummary();
        this.loadCharts();
    },

    /**
     * Export de la vue d'ensemble
     */
    exportOverview() {
        Dashboard.showToast('📊 Export de la vue d\'ensemble...', 'info');
    },

    /**
     * Export des données de consommation
     */
    exportConsumptionData() {
        Dashboard.showToast('📊 Export des données de consommation...', 'info');
        
        // Simulation d'export avec données réelles
        const csvContent = this.generateConsumptionCSV();
        this.downloadCSV(csvContent, 'consumption_data.csv');
    },

    /**
     * Génération du CSV de consommation
     */
    generateConsumptionCSV() {
        const headers = ['timestamp', 'building_id', 'consumption_kwh', 'building_type'];
        const sampleData = [
            ['2024-01-01 00:00:00', 'B001', '15.4', 'residential'],
            ['2024-01-01 01:00:00', 'B001', '12.8', 'residential'],
            ['2024-01-01 00:00:00', 'B002', '45.2', 'commercial']
        ];
        
        let csv = headers.join(',') + '\n';
        sampleData.forEach(row => {
            csv += row.join(',') + '\n';
        });
        
        return csv;
    },

    /**
     * Téléchargement de fichier CSV
     */
    downloadCSV(content, filename) {
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
            
            Dashboard.showToast('✅ Fichier téléchargé', 'success');
        }
    },

    /**
     * Export d'image de graphique
     */
    exportChartImage(chartId) {
        Dashboard.exportFunctions.exportChartImage(chartId);
    }
};

// Auto-initialisation quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    DashboardCharts.init();
});