// dashboard/static/js/modules/dashboard-core.js
/**
 * DASHBOARD MALAYSIA - MODULE CORE AVEC VRAIES DONNÉES
 * ===================================================
 * 
 * Module principal connecté aux vraies données CSV Malaysia
 * Version: 1.1.0 - DONNÉES RÉELLES
 */

// Namespace principal
window.Dashboard = {
    // Configuration
    config: {
        apiBaseUrl: '',
        refreshInterval: 30000,
        animationDuration: 500,
        maxRetries: 3,
        socketTimeout: 10000
    },

    // État global
    state: {
        isConnected: false,
        dataLoaded: false,
        currentTab: 'overview',
        lastUpdate: null,
        retryCount: 0,
        socket: null,
        map: null,
        charts: {},
        cache: {},
        realData: null
    },

    // Modules
    modules: {
        charts: null,
        maps: null,
        chat: null,
        data: null,
        ui: null
    },

    /**
     * Initialisation principale du dashboard
     */
    async init() {
        try {
            console.log('🚀 Dashboard Malaysia - Initialisation...');
            
            // Forcer l'initialisation immédiate du contenu
            this.loadInitialContent();
            
            // Initialisation des modules
            await this.initializeSocket();
            await this.initializeTheme();
            
            // Configuration des événements
            this.setupEventListeners();
            this.setupTabEvents();
            
            // Chargement automatique des vraies données
            await this.loadRealData();
            
            this.showToast('🇲🇾 Dashboard Malaysia démarré avec vraies données', 'success');
            console.log('✅ Dashboard initialisé avec succès');
            
        } catch (error) {
            console.error('❌ Erreur initialisation:', error);
            this.showToast('Erreur d\'initialisation du dashboard', 'error');
        }
    },

    /**
     * Chargement immédiat du contenu initial
     */
    loadInitialContent() {
        console.log('📄 Chargement du contenu initial...');
        
        // Charger le contenu de la sidebar
        this.loadSidebarContent();
        
        // Charger le contenu de l'onglet overview
        this.loadOverviewContent();
    },

    /**
     * Chargement de la sidebar
     */
    loadSidebarContent() {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;

        sidebar.innerHTML = `
            <div class="nav nav-pills flex-column" id="nav-tab" role="tablist">
                <button class="nav-link active" id="overview-tab" data-bs-toggle="pill" data-bs-target="#overview" type="button" role="tab">
                    <i class="bi bi-speedometer2 me-2"></i>
                    Vue d'ensemble
                </button>
                <button class="nav-link" id="consumption-tab" data-bs-toggle="pill" data-bs-target="#consumption" type="button" role="tab">
                    <i class="bi bi-lightning me-2"></i>
                    Consommation
                </button>
                <button class="nav-link" id="buildings-tab" data-bs-toggle="pill" data-bs-target="#buildings" type="button" role="tab">
                    <i class="bi bi-building me-2"></i>
                    Bâtiments
                </button>
                <button class="nav-link" id="analysis-tab" data-bs-toggle="pill" data-bs-target="#analysis" type="button" role="tab">
                    <i class="bi bi-robot me-2"></i>
                    Analyse LLM
                </button>
                <button class="nav-link" id="data-tab" data-bs-toggle="pill" data-bs-target="#data" type="button" role="tab">
                    <i class="bi bi-table me-2"></i>
                    Données
                </button>
                <button class="nav-link" id="settings-tab" data-bs-toggle="pill" data-bs-target="#settings" type="button" role="tab">
                    <i class="bi bi-gear me-2"></i>
                    Paramètres
                </button>
            </div>
        `;
    },

    /**
     * Chargement du contenu overview
     */
    loadOverviewContent() {
        const overview = document.getElementById('overview');
        if (!overview) return;

        overview.innerHTML = `
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="h3 mb-2">
                        <i class="bi bi-speedometer2 text-primary me-2"></i>
                        Vue d'ensemble - Données Malaysia
                    </h2>
                    <p class="text-muted">Analyse des données électriques réelles Malaysia (CSV)</p>
                </div>
            </div>

            <div class="row g-4 mb-4">
                <!-- Statistiques principales -->
                <div class="col-lg-3 col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex align-items-center">
                                <div class="me-3">
                                    <i class="bi bi-building-gear text-primary" style="font-size: 2rem;"></i>
                                </div>
                                <div>
                                    <h3 class="mb-0" id="total-buildings">
                                        <div class="loading-skeleton" style="width: 60px; height: 30px;"></div>
                                    </h3>
                                    <small class="text-muted">Bâtiments Malaysia</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-3 col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex align-items-center">
                                <div class="me-3">
                                    <i class="bi bi-lightning text-warning" style="font-size: 2rem;"></i>
                                </div>
                                <div>
                                    <h3 class="mb-0" id="total-consumption">
                                        <div class="loading-skeleton" style="width: 80px; height: 30px;"></div>
                                    </h3>
                                    <small class="text-muted">kWh Malaysia</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-3 col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex align-items-center">
                                <div class="me-3">
                                    <i class="bi bi-water text-info" style="font-size: 2rem;"></i>
                                </div>
                                <div>
                                    <h3 class="mb-0" id="total-water">
                                        <div class="loading-skeleton" style="width: 70px; height: 30px;"></div>
                                    </h3>
                                    <small class="text-muted">Litres Malaysia</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-3 col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex align-items-center">
                                <div class="me-3">
                                    <i class="bi bi-thermometer text-success" style="font-size: 2rem;"></i>
                                </div>
                                <div>
                                    <h3 class="mb-0" id="avg-temperature">
                                        <div class="loading-skeleton" style="width: 50px; height: 30px;"></div>
                                    </h3>
                                    <small class="text-muted">°C Malaysia</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Graphiques réels -->
            <div class="row g-4">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-graph-up me-2"></i>
                                Consommation électrique Malaysia (Données CSV)
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="consumption-timeline" style="height: 400px;">
                                <div class="text-center p-5">
                                    <div class="spinner-border text-primary" role="status"></div>
                                    <p class="text-muted mt-3">Chargement des données Malaysia...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="bi bi-pie-chart me-2"></i>
                                Types de bâtiments Malaysia
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="building-types-pie" style="height: 400px;">
                                <div class="text-center p-5">
                                    <div class="spinner-border text-primary" role="status"></div>
                                    <p class="text-muted mt-3">Chargement des données...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * CHARGEMENT DES VRAIES DONNÉES MALAYSIA
     */
    async loadRealData() {
        try {
            console.log('🔄 Chargement des vraies données Malaysia depuis CSV...');
            this.showToast('Chargement des données Malaysia...', 'info');
            
            // Étape 1: Charger les données depuis les CSV
            const loadResponse = await fetch('/api/data/load', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!loadResponse.ok) {
                throw new Error(`Erreur ${loadResponse.status}: ${loadResponse.statusText}`);
            }
            
            const loadResult = await loadResponse.json();
            console.log('✅ Réponse chargement données:', loadResult);
            
            if (!loadResult.success) {
                throw new Error(loadResult.error || 'Erreur chargement données');
            }
            
            // Étape 2: Récupérer le résumé des données
            await this.loadDataSummary();
            
            // Étape 3: Charger les graphiques
            await this.loadRealCharts();
            
            this.state.dataLoaded = true;
            this.state.realData = loadResult.data_info;
            this.updateConnectionStatus('connected', 'Données Malaysia chargées');
            this.showToast('✅ Données Malaysia chargées avec succès', 'success');
            
        } catch (error) {
            console.error('❌ Erreur chargement données Malaysia:', error);
            this.showToast('Erreur: ' + error.message, 'error');
            
            // Fallback: données simulées
            this.loadFallbackData();
        }
    },

    /**
     * Chargement du résumé des données
     */
    async loadDataSummary() {
        try {
            const summaryResponse = await fetch('/api/data/summary');
            
            if (summaryResponse.ok) {
                const summaryResult = await summaryResponse.json();
                console.log('📊 Résumé des données Malaysia:', summaryResult);
                
                if (summaryResult.success && summaryResult.summary) {
                    this.updateStatistics(summaryResult.summary);
                }
            } else {
                console.warn('⚠️ Impossible de récupérer le résumé des données');
            }
        } catch (error) {
            console.error('❌ Erreur résumé données:', error);
        }
    },

    /**
     * Mise à jour des statistiques avec les vraies données
     */
    updateStatistics(summary) {
        const stats = {
            buildings: summary.total_buildings || summary.buildings_count || 0,
            consumption: summary.total_consumption || summary.electricity_total || 0,
            water: summary.total_water || summary.water_total || 0,
            temperature: summary.avg_temperature || summary.temperature_avg || 0
        };
        
        // Formatage et affichage
        document.getElementById('total-buildings').textContent = this.formatNumber(stats.buildings, 0);
        document.getElementById('total-consumption').textContent = this.formatNumber(stats.consumption) + ' kWh';
        document.getElementById('total-water').textContent = this.formatNumber(stats.water) + ' L';
        document.getElementById('avg-temperature').textContent = stats.temperature.toFixed(1) + '°C';
        
        console.log('📈 Statistiques mises à jour:', stats);
    },

    /**
     * Chargement des vrais graphiques depuis l'API
     */
    async loadRealCharts() {
        try {
            console.log('📊 Chargement des graphiques Malaysia...');
            
            // Graphiques overview
            const chartsResponse = await fetch('/api/charts/overview');
            
            if (chartsResponse.ok) {
                const chartsResult = await chartsResponse.json();
                console.log('📈 Données graphiques reçues:', chartsResult);
                
                if (chartsResult.success && chartsResult.charts) {
                    this.renderRealCharts(chartsResult.charts);
                } else {
                    console.warn('⚠️ Pas de données graphiques disponibles');
                    this.createFallbackCharts();
                }
            } else {
                console.warn('⚠️ API graphiques non disponible');
                this.createFallbackCharts();
            }
            
        } catch (error) {
            console.error('❌ Erreur chargement graphiques:', error);
            this.createFallbackCharts();
        }
    },

    /**
     * Rendu des vrais graphiques Plotly
     */
    renderRealCharts(charts) {
        if (typeof Plotly === 'undefined') {
            console.error('❌ Plotly non disponible');
            return;
        }
        
        try {
            // Graphique de consommation temporelle
            const timelineDiv = document.getElementById('consumption-timeline');
            if (timelineDiv && charts.timeline) {
                const layout = {
                    ...charts.timeline.layout,
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: { color: '#f9fafb' },
                    title: 'Consommation électrique Malaysia (données réelles)'
                };
                
                Plotly.newPlot(timelineDiv, charts.timeline.data, layout, {responsive: true});
                console.log('✅ Graphique timeline rendu');
            }
            
            // Graphique de répartition
            const pieDiv = document.getElementById('building-types-pie');
            if (pieDiv && charts.pie) {
                const layout = {
                    ...charts.pie.layout,
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    font: { color: '#f9fafb' },
                    title: 'Répartition bâtiments Malaysia'
                };
                
                Plotly.newPlot(pieDiv, charts.pie.data, layout, {responsive: true});
                console.log('✅ Graphique pie rendu');
            }
            
        } catch (error) {
            console.error('❌ Erreur rendu graphiques:', error);
            this.createFallbackCharts();
        }
    },

    /**
     * Graphiques de secours si les API ne marchent pas
     */
    createFallbackCharts() {
        if (typeof Plotly === 'undefined') {
            console.warn('⚠️ Plotly non disponible pour les graphiques de secours');
            return;
        }
        
        // Graphique de consommation simple
        const timelineDiv = document.getElementById('consumption-timeline');
        if (timelineDiv) {
            const data = [{
                x: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul'],
                y: [2100, 2400, 1900, 2800, 2200, 2600, 2900],
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: '#3b82f6', width: 3 },
                marker: { size: 8 },
                name: 'Consommation Malaysia'
            }];
            
            const layout = {
                title: 'Consommation électrique Malaysia (données exemple)',
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: { color: '#f9fafb' },
                xaxis: { gridcolor: '#374151' },
                yaxis: { gridcolor: '#374151', title: 'kWh' }
            };
            
            Plotly.newPlot(timelineDiv, data, layout, {responsive: true});
        }
        
        // Graphique pie simple
        const pieDiv = document.getElementById('building-types-pie');
        if (pieDiv) {
            const data = [{
                values: [45, 35, 20],
                labels: ['Résidentiel', 'Commercial', 'Industriel'],
                type: 'pie',
                marker: {
                    colors: ['#3b82f6', '#6366f1', '#10b981']
                },
                textinfo: 'label+percent'
            }];
            
            const layout = {
                title: 'Types de bâtiments Malaysia',
                paper_bgcolor: 'rgba(0,0,0,0)',
                font: { color: '#f9fafb' }
            };
            
            Plotly.newPlot(pieDiv, data, layout, {responsive: true});
        }
        
        console.log('📊 Graphiques de secours créés');
    },

    /**
     * Données de secours si le chargement échoue
     */
    loadFallbackData() {
        console.log('🔄 Chargement des données de secours...');
        
        document.getElementById('total-buildings').textContent = '1,247';
        document.getElementById('total-consumption').textContent = '2.4M kWh';
        document.getElementById('total-water').textContent = '356K L';
        document.getElementById('avg-temperature').textContent = '28.5°C';
        
        this.createFallbackCharts();
        this.updateConnectionStatus('connected', 'Mode démo');
    },

    /**
     * Configuration des événements d'onglets
     */
    setupTabEvents() {
        const tabButtons = document.querySelectorAll('[data-bs-toggle="pill"]');
        tabButtons.forEach(button => {
            button.addEventListener('shown.bs.tab', (event) => {
                const targetId = event.target.getAttribute('data-bs-target').substring(1);
                this.state.currentTab = targetId;
                console.log(`📝 Onglet actif: ${targetId}`);
                
                // Charger le contenu spécifique
                this.loadTabContent(targetId);
            });
        });
    },

    /**
     * Chargement du contenu des onglets
     */
    loadTabContent(tabId) {
        switch(tabId) {
            case 'overview':
                // Déjà chargé
                break;
            case 'consumption':
                this.loadConsumptionContent();
                break;
            case 'buildings':
                this.loadBuildingsContent();
                break;
            case 'analysis':
                this.loadAnalysisContent();
                break;
            case 'data':
                this.loadDataContent();
                break;
            case 'settings':
                this.loadSettingsContent();
                break;
        }
    },

    /**
     * Chargement contenu onglet Consommation
     */
    loadConsumptionContent() {
        const consumption = document.getElementById('consumption');
        if (!consumption || consumption.dataset.loaded) return;

        consumption.innerHTML = `
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="h3 mb-2">
                        <i class="bi bi-lightning text-warning me-2"></i>
                        Analyse de consommation Malaysia
                    </h2>
                    <p class="text-muted">Détails de la consommation électrique Malaysia (données CSV)</p>
                </div>
            </div>

            <div class="row g-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div class="text-center p-4">
                                <button class="btn btn-primary" onclick="Dashboard.loadConsumptionData()">
                                    <i class="bi bi-lightning me-2"></i>
                                    Charger données consommation Malaysia
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        consumption.dataset.loaded = 'true';
    },

    /**
     * Chargement contenu onglet Bâtiments
     */
    loadBuildingsContent() {
        const buildings = document.getElementById('buildings');
        if (!buildings || buildings.dataset.loaded) return;

        buildings.innerHTML = `
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="h3 mb-2">
                        <i class="bi bi-building text-info me-2"></i>
                        Bâtiments Malaysia
                    </h2>
                    <p class="text-muted">Données des bâtiments Malaysia (CSV)</p>
                </div>
            </div>

            <div class="row g-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div class="text-center p-4">
                                <button class="btn btn-primary" onclick="Dashboard.loadBuildingsData()">
                                    <i class="bi bi-building me-2"></i>
                                    Charger données bâtiments Malaysia
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        buildings.dataset.loaded = 'true';
    },

    /**
     * Chargement contenu onglet Analyse
     */
    loadAnalysisContent() {
        const analysis = document.getElementById('analysis');
        if (!analysis || analysis.dataset.loaded) return;

        analysis.innerHTML = `
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="h3 mb-2">
                        <i class="bi bi-robot text-success me-2"></i>
                        Analyse LLM - Données Malaysia
                    </h2>
                    <p class="text-muted">Posez vos questions sur les données électriques Malaysia</p>
                </div>
            </div>

            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div id="chat-messages" style="height: 400px; overflow-y: auto; border: 1px solid #4b5563; border-radius: 8px; padding: 20px; margin-bottom: 20px; background: #1f2937;">
                                <div class="text-center text-muted">
                                    <i class="bi bi-chat-dots" style="font-size: 3rem; margin-bottom: 10px;"></i>
                                    <p>Posez vos questions sur les données Malaysia...</p>
                                    <small>Exemple: "Quelle est la consommation moyenne des bâtiments commerciaux ?"</small>
                                </div>
                            </div>
                            
                            <div class="input-group">
                                <input type="text" class="form-control" id="chat-input" placeholder="Analysez les données électriques Malaysia...">
                                <button class="btn btn-primary" type="button" onclick="Dashboard.sendChatMessage()">
                                    <i class="bi bi-send"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        analysis.dataset.loaded = 'true';
    },

    /**
     * Chargement contenu onglet Données
     */
    loadDataContent() {
        const data = document.getElementById('data');
        if (!data || data.dataset.loaded) return;

        data.innerHTML = `
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="h3 mb-2">
                        <i class="bi bi-table text-secondary me-2"></i>
                        Données brutes Malaysia
                    </h2>
                    <p class="text-muted">Visualisation des fichiers CSV Malaysia</p>
                </div>
            </div>

            <div class="row g-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div class="text-center p-4">
                                <h5>Fichiers de données Malaysia disponibles:</h5>
                                <ul class="list-unstyled mt-3">
                                    <li><i class="bi bi-file-text text-primary me-2"></i>buildings_metadata.csv</li>
                                    <li><i class="bi bi-file-text text-warning me-2"></i>electricity_consumption.csv</li>
                                    <li><i class="bi bi-file-text text-success me-2"></i>weather_simulation.csv</li>
                                    <li><i class="bi bi-file-text text-info me-2"></i>water_consumption.csv</li>
                                </ul>
                                <button class="btn btn-primary mt-3" onclick="Dashboard.viewRawData()">
                                    <i class="bi bi-table me-2"></i>
                                    Afficher données tabulaires
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        data.dataset.loaded = 'true';
    },

    /**
     * Chargement contenu onglet Paramètres
     */
    loadSettingsContent() {
        const settings = document.getElementById('settings');
        if (!settings || settings.dataset.loaded) return;

        settings.innerHTML = `
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="h3 mb-2">
                        <i class="bi bi-gear text-secondary me-2"></i>
                        Paramètres Dashboard Malaysia
                    </h2>
                    <p class="text-muted">Configuration et préférences</p>
                </div>
            </div>

            <div class="row g-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Données</h5>
                        </div>
                        <div class="card-body">
                            <button class="btn btn-outline-primary w-100 mb-2" onclick="Dashboard.loadRealData()">
                                <i class="bi bi-arrow-clockwise me-2"></i>
                                Recharger données Malaysia
                            </button>
                            <button class="btn btn-outline-info w-100" onclick="Dashboard.updateRAG()">
                                <i class="bi bi-database me-2"></i>
                                Mettre à jour base RAG
                            </button>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Interface</h5>
                        </div>
                        <div class="card-body">
                            <button class="btn btn-outline-secondary w-100 mb-2" onclick="Dashboard.toggleTheme()">
                                <i class="bi bi-moon me-2"></i>
                                Basculer thème
                            </button>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="autoRefresh" checked>
                                <label class="form-check-label" for="autoRefresh">
                                    Actualisation automatique
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        settings.dataset.loaded = 'true';
    },

    /**
     * Initialisation WebSocket
     */
    async initializeSocket() {
        try {
            if (typeof io !== 'undefined') {
                this.state.socket = io({
                    timeout: this.config.socketTimeout,
                    reconnection: true,
                    reconnectionDelay: 1000
                });

                this.state.socket.on('connect', () => {
                    console.log('✅ WebSocket connecté');
                    this.updateConnectionStatus('connected', 'Connecté');
                    this.state.isConnected = true;
                });

                this.state.socket.on('disconnect', () => {
                    console.log('❌ WebSocket déconnecté');
                    this.updateConnectionStatus('error', 'Déconnecté');
                    this.state.isConnected = false;
                });
            } else {
                console.log('⚠️ Socket.IO non disponible');
                this.updateConnectionStatus('connected', 'Mode local');
            }
        } catch (error) {
            console.error('❌ Erreur WebSocket:', error);
            this.updateConnectionStatus('error', 'Erreur connexion');
        }
    },

    /**
     * Configuration du thème
     */
    async initializeTheme() {
        const savedTheme = localStorage.getItem('dashboard-theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
    },

    /**
     * Configuration des événements
     */
    setupEventListeners() {
        // Gestion des erreurs globales
        window.addEventListener('error', (event) => {
            console.error('Erreur JavaScript:', event.error);
        });

        // Raccourcis clavier
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.loadRealData();
            }
            if (e.ctrlKey && e.key === 't') {
                e.preventDefault();
                this.toggleTheme();
            }
            if (e.key === 'Enter' && e.target.id === 'chat-input') {
                this.sendChatMessage();
            }
        });
    },

    /**
     * Mise à jour du statut de connexion
     */
    updateConnectionStatus(status, text) {
        const indicator = document.querySelector('.status-indicator');
        const statusText = document.getElementById('status-text');
        
        if (indicator && statusText) {
            indicator.className = `status-indicator status-${status}`;
            statusText.textContent = text;
        }
    },

    /**
     * Affichage des toasts
     */
    showToast(message, type = 'info') {
        // Créer le container s'il n'existe pas
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '1055';
            document.body.appendChild(toastContainer);
        }
        
        const toastId = 'toast-' + Date.now();
        const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-primary';
        
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = document.getElementById(toastId);
        
        if (typeof bootstrap !== 'undefined') {
            const toast = new bootstrap.Toast(toastElement);
            toast.show();
        }
        
        setTimeout(() => {
            if (toastElement) toastElement.remove();
        }, 5000);
    },

    /**
     * Utilitaires - Fonction debounce
     */
    debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    },

    /**
     * Utilitaires - Formatage des nombres
     */
    formatNumber(num, decimals = 1) {
        if (typeof num !== 'number') return num;
        if (num >= 1000000000) return `${(num / 1000000000).toFixed(decimals)}B`;
        if (num >= 1000000) return `${(num / 1000000).toFixed(decimals)}M`;
        if (num >= 1000) return `${(num / 1000).toFixed(decimals)}k`;
        return num.toFixed(decimals);
    },

    /**
     * Utilitaires - Formatage des dates
     */
    formatDate(dateString) {
        if (!dateString) return '';
        return new Date(dateString).toLocaleDateString('fr-FR');
    },

    /**
     * Utilitaires - Formatage des pourcentages
     */
    formatPercentage(value, decimals = 1) {
        if (typeof value !== 'number') return value;
        if (value >= 0 && value <= 1) value *= 100;
        return `${value.toFixed(decimals)}%`;
    },

    /**
     * Utilitaires - Formatage des tailles de fichier
     */
    formatFileSize(bytes) {
        if (!bytes) return '0 B';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
    },

    /**
     * FONCTIONS POUR LES BOUTONS ET INTERACTIONS
     */

    /**
     * Fonction pour bouton "Charger" - Reload des données
     */
    async loadData() {
        this.showToast('Rechargement des données Malaysia...', 'info');
        await this.loadRealData();
    },

    /**
     * Basculer le thème
     */
    toggleTheme() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('dashboard-theme', newTheme);
        this.showToast(`Thème changé: ${newTheme}`, 'info');
    },

    /**
     * Afficher l'aide
     */
    showHelp() {
        this.showToast('Dashboard Malaysia - Analysez vos données électriques', 'info');
    },

    /**
     * Envoyer message chat
     */
    async sendChatMessage() {
        const input = document.getElementById('chat-input');
        const messagesDiv = document.getElementById('chat-messages');
        
        if (!input || !input.value.trim() || !messagesDiv) return;
        
        const message = input.value.trim();
        const timestamp = new Date().toLocaleTimeString();
        
        // Ajouter le message utilisateur
        messagesDiv.innerHTML += `
            <div class="mb-3">
                <div class="d-flex">
                    <div class="me-2">
                        <i class="bi bi-person-circle text-primary"></i>
                    </div>
                    <div class="flex-grow-1">
                        <strong>Vous:</strong> <small class="text-muted">(${timestamp})</small>
                        <div class="mt-1">${message}</div>
                    </div>
                </div>
            </div>
        `;
        
        // Vider l'input
        input.value = '';
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
        // Ajouter un indicateur de traitement
        messagesDiv.innerHTML += `
            <div class="mb-3" id="processing-message">
                <div class="d-flex">
                    <div class="me-2">
                        <i class="bi bi-robot text-success"></i>
                    </div>
                    <div class="flex-grow-1">
                        <strong>Assistant IA:</strong>
                        <div class="mt-1">
                            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                            Analyse des données Malaysia en cours...
                        </div>
                    </div>
                </div>
            </div>
        `;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
        try {
            // Appel à l'API d'analyse
            const response = await fetch('/api/llm/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: message })
            });
            
            // Supprimer l'indicateur de traitement
            const processingMsg = document.getElementById('processing-message');
            if (processingMsg) processingMsg.remove();
            
            if (response.ok) {
                const result = await response.json();
                
                if (result.success && result.analysis) {
                    // Afficher la réponse de l'IA
                    messagesDiv.innerHTML += `
                        <div class="mb-3">
                            <div class="d-flex">
                                <div class="me-2">
                                    <i class="bi bi-robot text-success"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <strong>Assistant IA:</strong> <small class="text-muted">(${new Date().toLocaleTimeString()})</small>
                                    <div class="mt-1">${result.analysis.full_response || result.analysis}</div>
                                    ${result.context_used ? '<small class="text-info"><i class="bi bi-database me-1"></i>Basé sur les données Malaysia</small>' : ''}
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    throw new Error(result.error || 'Réponse invalide');
                }
            } else {
                throw new Error(`Erreur ${response.status}`);
            }
            
        } catch (error) {
            // Supprimer l'indicateur de traitement
            const processingMsg = document.getElementById('processing-message');
            if (processingMsg) processingMsg.remove();
            
            // Afficher une réponse d'erreur
            messagesDiv.innerHTML += `
                <div class="mb-3">
                    <div class="d-flex">
                        <div class="me-2">
                            <i class="bi bi-robot text-warning"></i>
                        </div>
                        <div class="flex-grow-1">
                            <strong>Assistant IA:</strong> <small class="text-muted">(${new Date().toLocaleTimeString()})</small>
                            <div class="mt-1">
                                <div class="alert alert-warning alert-sm">
                                    <i class="bi bi-exclamation-triangle me-2"></i>
                                    Désolé, je ne peux pas analyser vos données pour le moment. 
                                    ${error.message.includes('404') ? 'Le service d\'analyse n\'est pas encore configuré.' : 'Erreur: ' + error.message}
                                </div>
                                <p>En attendant, voici une analyse basique de votre question sur les données Malaysia...</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    },

    /**
     * Charger données de consommation spécifiques
     */
    async loadConsumptionData() {
        try {
            this.showToast('Chargement données consommation...', 'info');
            
            const response = await fetch('/api/charts/consumption');
            if (response.ok) {
                const result = await response.json();
                console.log('📊 Données consommation:', result);
                this.showToast('Données consommation chargées', 'success');
            } else {
                throw new Error('API consommation non disponible');
            }
        } catch (error) {
            console.error('❌ Erreur consommation:', error);
            this.showToast('Erreur chargement consommation', 'error');
        }
    },

    /**
     * Charger données de bâtiments spécifiques
     */
    async loadBuildingsData() {
        try {
            this.showToast('Chargement données bâtiments...', 'info');
            
            const response = await fetch('/api/map/buildings');
            if (response.ok) {
                const result = await response.json();
                console.log('🏢 Données bâtiments:', result);
                this.showToast('Données bâtiments chargées', 'success');
            } else {
                throw new Error('API bâtiments non disponible');
            }
        } catch (error) {
            console.error('❌ Erreur bâtiments:', error);
            this.showToast('Erreur chargement bâtiments', 'error');
        }
    },

    /**
     * Afficher données brutes
     */
    async viewRawData() {
        try {
            this.showToast('Chargement données tabulaires...', 'info');
            
            // Cette fonction pourrait ouvrir une modal avec les données CSV
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-xl">
                    <div class="modal-content bg-dark">
                        <div class="modal-header">
                            <h5 class="modal-title">Données Malaysia - Vue tabulaire</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="text-center p-4">
                                <div class="spinner-border text-primary" role="status"></div>
                                <p class="mt-3">Chargement des données CSV Malaysia...</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();
            
            // Nettoyer la modal quand elle se ferme
            modal.addEventListener('hidden.bs.modal', () => {
                document.body.removeChild(modal);
            });
            
        } catch (error) {
            console.error('❌ Erreur données brutes:', error);
            this.showToast('Erreur affichage données', 'error');
        }
    },

    /**
     * Mettre à jour la base RAG
     */
    async updateRAG() {
        try {
            this.showToast('Mise à jour base RAG...', 'info');
            
            const response = await fetch('/api/rag/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                this.showToast('Base RAG mise à jour avec succès', 'success');
            } else {
                throw new Error('Erreur mise à jour RAG');
            }
        } catch (error) {
            console.error('❌ Erreur RAG:', error);
            this.showToast('Erreur mise à jour RAG', 'error');
        }
    },

    /**
     * Enregistrement d'un module
     */
    registerModule(name, module) {
        this.modules[name] = module;
        console.log(`📦 Module ${name} enregistré`);
    },

    /**
     * Récupération d'un module
     */
    getModule(name) {
        return this.modules[name];
    }
};

// Initialisation automatique
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Initialisation Dashboard Malaysia...');
    Dashboard.init();
});

console.log('✅ Dashboard Core Module - Version avec vraies données Malaysia chargée');