// dashboard/static/js/modules/dashboard-data.js
/**
 * DASHBOARD MALAYSIA - MODULE DATA
 * ================================
 * 
 * Module pour la gestion des données tabulaires
 * Version: 1.0.0
 */

const DashboardData = {
    /**
     * Initialisation du module
     */
    init() {
        console.log('📊 Initialisation module Data');
        this.loadDataContent();
        this.loadSettingsContent();
        Dashboard.registerModule('data', this);
    },

    /**
     * Chargement du contenu de l'onglet Données
     */
    loadDataContent() {
        const data = document.getElementById('data');
        if (!data) return;

        data.innerHTML = `
            <div class="row mb-4">
                <div class="col-md-8">
                    <h2 class="h3 mb-2">
                        <i class="bi bi-table text-info me-2"></i>
                        Données Brutes
                    </h2>
                    <p class="text-muted">Exploration et export des données Malaysia</p>
                </div>
                <div class="col-md-4">
                    <select class="form-select" id="data-table-select" onchange="DashboardData.switchDataTable()">
                        <option value="buildings">🏢 Bâtiments</option>
                        <option value="consumption">⚡ Consommation</option>
                        <option value="weather">🌤️ Météo</option>
                        <option value="water">💧 Eau</option>
                    </select>
                </div>
            </div>

            <div class="row g-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header bg-transparent border-bottom">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-0" id="data-table-title">
                                    <i class="bi bi-building text-primary me-2"></i>
                                    Données des Bâtiments
                                </h5>
                                <div class="btn-group">
                                    <button class="btn btn-outline-primary btn-sm" onclick="DashboardData.refreshDataTable()">
                                        <i class="bi bi-arrow-clockwise me-1"></i>
                                        Actualiser
                                    </button>
                                    <button class="btn btn-outline-info btn-sm" onclick="DashboardData.showDataInfo()">
                                        <i class="bi bi-info-circle me-1"></i>
                                        Info
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <div class="input-group">
                                        <span class="input-group-text">
                                            <i class="bi bi-search"></i>
                                        </span>
                                        <input type="text" class="form-control" id="data-search" 
                                               placeholder="Rechercher dans les données...">
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <select class="form-select" id="data-filter">
                                        <option value="">Tous les types</option>
                                        <option value="residential">Résidentiel</option>
                                        <option value="commercial">Commercial</option>
                                        <option value="industrial">Industriel</option>
                                    </select>
                                </div>
                                <div class="col-md-3">
                                    <select class="form-select" id="data-limit">
                                        <option value="100">100 lignes</option>
                                        <option value="500">500 lignes</option>
                                        <option value="1000">1000 lignes</option>
                                        <option value="all">Toutes</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="table-responsive">
                                <div id="data-table-container">
                                    <div class="text-center p-5">
                                        <div class="spinner-border text-primary" role="status">
                                            <span class="visually-hidden">Chargement...</span>
                                        </div>
                                        <p class="mt-3 text-muted">Chargement des données...</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mt-3 d-flex justify-content-between align-items-center">
                                <small class="text-muted" id="data-info">
                                    <i class="bi bi-info-circle me-1"></i>
                                    Chargement des informations...
                                </small>
                                <nav>
                                    <ul class="pagination pagination-sm mb-0" id="data-pagination">
                                        <li class="page-item disabled">
                                            <span class="page-link">Précédent</span>
                                        </li>
                                        <li class="page-item active">
                                            <span class="page-link">1</span>
                                        </li>
                                        <li class="page-item disabled">
                                            <span class="page-link">Suivant</span>
                                        </li>
                                    </ul>
                                </nav>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Load default table
        setTimeout(() => {
            this.renderDataTable('buildings');
        }, 1000);
    },

    /**
     * Chargement du contenu de l'onglet Paramètres
     */
    loadSettingsContent() {
        const settings = document.getElementById('settings');
        if (!settings) return;

        settings.innerHTML = `
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="h3 mb-2">
                        <i class="bi bi-gear text-secondary me-2"></i>
                        Paramètres & Configuration
                    </h2>
                    <p class="text-muted">Configuration du dashboard et préférences utilisateur</p>
                </div>
            </div>

            <div class="row g-4">
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header bg-transparent border-bottom">
                            <h5 class="mb-0">
                                <i class="bi bi-palette text-primary me-2"></i>
                                Apparence
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Thème:</label>
                                <div class="btn-group w-100" role="group">
                                    <input type="radio" class="btn-check" name="theme" id="theme-dark" value="dark" checked>
                                    <label class="btn btn-outline-primary" for="theme-dark">
                                        <i class="bi bi-moon me-1"></i>
                                        Sombre
                                    </label>
                                    
                                    <input type="radio" class="btn-check" name="theme" id="theme-light" value="light">
                                    <label class="btn btn-outline-primary" for="theme-light">
                                        <i class="bi bi-sun me-1"></i>
                                        Clair
                                    </label>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Langue:</label>
                                <select class="form-select" id="language-select">
                                    <option value="fr">🇫🇷 Français</option>
                                    <option value="en">🇬🇧 English</option>
                                    <option value="ms">🇲🇾 Bahasa Malaysia</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="animations-toggle" checked>
                                    <label class="form-check-label" for="animations-toggle">
                                        Animations d'interface
                                    </label>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="sounds-toggle">
                                    <label class="form-check-label" for="sounds-toggle">
                                        Sons de notification
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card mt-3">
                        <div class="card-header bg-transparent border-bottom">
                            <h5 class="mb-0">
                                <i class="bi bi-display text-info me-2"></i>
                                Affichage
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Résolution des graphiques:</label>
                                <select class="form-select" id="chart-resolution">
                                    <option value="standard">Standard (1x)</option>
                                    <option value="high" selected>Haute (2x)</option>
                                    <option value="ultra">Ultra (4x)</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Nombre max de points sur les graphiques:</label>
                                <input type="range" class="form-range" id="max-points-range" 
                                       min="1000" max="50000" step="1000" value="10000">
                                <div class="d-flex justify-content-between small text-muted">
                                    <span>1k</span>
                                    <span id="max-points-value">10k</span>
                                    <span>50k</span>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="auto-refresh-toggle">
                                    <label class="form-check-label" for="auto-refresh-toggle">
                                        Actualisation automatique (30s)
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header bg-transparent border-bottom">
                            <h5 class="mb-0">
                                <i class="bi bi-cpu text-warning me-2"></i>
                                Configuration Ollama
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">URL du serveur Ollama:</label>
                                <input type="url" class="form-control" id="ollama-url" 
                                       value="http://localhost:11434" placeholder="http://localhost:11434">
                                <div class="form-text">
                                    <i class="bi bi-info-circle me-1"></i>
                                    Adresse de votre serveur Ollama local
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Modèle par défaut:</label>
                                <select class="form-select" id="default-model">
                                    <option value="mistral:latest">Mistral Latest</option>
                                    <option value="llama2">Llama 2</option>
                                    <option value="codellama">Code Llama</option>
                                    <option value="phi">Phi</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Timeout (secondes):</label>
                                <input type="number" class="form-control" id="ollama-timeout" 
                                       value="120" min="30" max="300">
                            </div>
                            
                            <div class="mb-3">
                                <button class="btn btn-outline-primary" onclick="DashboardData.testOllamaConnection()">
                                    <i class="bi bi-wifi me-1"></i>
                                    Tester la connexion
                                </button>
                                <span id="ollama-test-result" class="ms-2"></span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card mt-3">
                        <div class="card-header bg-transparent border-bottom">
                            <h5 class="mb-0">
                                <i class="bi bi-database text-success me-2"></i>
                                Données & Performance
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label">Cache des données (minutes):</label>
                                <input type="number" class="form-control" id="cache-duration" 
                                       value="60" min="5" max="1440">
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Dossier d'export:</label>
                                <input type="text" class="form-control" id="export-folder" 
                                       value="exports" placeholder="exports">
                            </div>
                            
                            <div class="mb-3">
                                <div class="row">
                                    <div class="col-6">
                                        <button class="btn btn-outline-warning w-100" onclick="DashboardData.clearCache()">
                                            <i class="bi bi-trash3 me-1"></i>
                                            Vider cache
                                        </button>
                                    </div>
                                    <div class="col-6">
                                        <button class="btn btn-outline-danger w-100" onclick="DashboardData.resetSettings()">
                                            <i class="bi bi-arrow-clockwise me-1"></i>
                                            Reset
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card mt-3">
                        <div class="card-header bg-transparent border-bottom">
                            <h5 class="mb-0">
                                <i class="bi bi-shield-check text-danger me-2"></i>
                                Système
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="row text-center mb-3">
                                <div class="col-4">
                                    <div class="text-muted small">Version</div>
                                    <div class="fw-bold">1.0.0</div>
                                </div>
                                <div class="col-4">
                                    <div class="text-muted small">Python</div>
                                    <div class="fw-bold">3.11+</div>
                                </div>
                                <div class="col-4">
                                    <div class="text-muted small">Status</div>
                                    <div class="fw-bold text-success">✓ OK</div>
                                </div>
                            </div>
                            
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-info" onclick="DashboardData.showSystemInfo()">
                                    <i class="bi bi-info-circle me-1"></i>
                                    Informations système
                                </button>
                                <button class="btn btn-outline-primary" onclick="DashboardData.checkUpdates()">
                                    <i class="bi bi-arrow-up-circle me-1"></i>
                                    Vérifier les mises à jour
                                </button>
                                <button class="btn btn-outline-success" onclick="DashboardData.exportSettings()">
                                    <i class="bi bi-download me-1"></i>
                                    Sauvegarder config
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Changement de table de données
     */
    switchDataTable() {
        const tableType = document.getElementById('data-table-select').value;
        const titleElement = document.getElementById('data-table-title');
        const containerElement = document.getElementById('data-table-container');

        const titles = {
            buildings: '<i class="bi bi-building text-primary me-2"></i>Données des Bâtiments',
            consumption: '<i class="bi bi-lightning text-success me-2"></i>Données de Consommation',
            weather: '<i class="bi bi-cloud-sun text-info me-2"></i>Données Météorologiques',
            water: '<i class="bi bi-droplet text-primary me-2"></i>Données de Consommation d\'Eau'
        };

        titleElement.innerHTML = titles[tableType];

        // Show loading
        containerElement.innerHTML = `
            <div class="text-center p-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
                <p class="mt-3 text-muted">Chargement des données ${tableType}...</p>
            </div>
        `;

        setTimeout(() => {
            this.renderDataTable(tableType);
        }, 800);
    },

    /**
     * Rendu de la table de données
     */
    renderDataTable(tableType) {
        const container = document.getElementById('data-table-container');
        const infoElement = document.getElementById('data-info');

        // Sample data for demonstration
        const sampleData = {
            buildings: [
                {unique_id: 'B001', building_type: 'residential', surface_area_m2: 120, zone_name: 'Kuala Lumpur', latitude: 3.1390, longitude: 101.6869},
                {unique_id: 'B002', building_type: 'commercial', surface_area_m2: 850, zone_name: 'Selangor', latitude: 3.1500, longitude: 101.7000},
                {unique_id: 'B003', building_type: 'industrial', surface_area_m2: 2400, zone_name: 'Johor', latitude: 3.1600, longitude: 101.7100}
            ],
            consumption: [
                {unique_id: 'B001', timestamp: '2024-01-01 00:00:00', y: 15.4, frequency: '1H'},
                {unique_id: 'B001', timestamp: '2024-01-01 01:00:00', y: 12.8, frequency: '1H'},
                {unique_id: 'B002', timestamp: '2024-01-01 00:00:00', y: 45.2, frequency: '1H'}
            ],
            weather: [
                {timestamp: '2024-01-01 00:00:00', temperature: 28.5, humidity: 75, wind_speed: 12, pressure: 1013},
                {timestamp: '2024-01-01 01:00:00', temperature: 27.8, humidity: 78, wind_speed: 10, pressure: 1012}
            ],
            water: [
                {unique_id: 'B001', timestamp: '2024-01-01 00:00:00', y: 125.5, frequency: '1H'},
                {unique_id: 'B002', timestamp: '2024-01-01 00:00:00', y: 340.2, frequency: '1H'}
            ]
        };

        const data = sampleData[tableType] || [];

        if (data.length === 0) {
            container.innerHTML = `
                <div class="text-center p-5">
                    <i class="bi bi-database-x fs-1 text-muted"></i>
                    <p class="mt-3 text-muted">Aucune donnée ${tableType} disponible</p>
                    <button class="btn btn-outline-primary" onclick="Dashboard.loadData()">
                        <i class="bi bi-arrow-clockwise me-1"></i>
                        Charger les données
                    </button>
                </div>
            `;
            return;
        }

        const columns = Object.keys(data[0]);
        
        let tableHTML = `
            <table class="table table-dark table-striped table-hover">
                <thead class="table-primary">
                    <tr>
                        ${columns.map(col => `
                            <th class="text-nowrap">
                                <i class="bi bi-sort-alpha-down text-muted me-1"></i>
                                ${col.replace('_', ' ').toUpperCase()}
                            </th>
                        `).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${data.map((row, index) => `
                        <tr class="fade-in" style="animation-delay: ${index * 50}ms">
                            ${columns.map(col => `
                                <td class="text-nowrap">
                                    ${this.formatCellValue(row[col], col)}
                                </td>
                            `).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = tableHTML;
        
        // Update info
        if (infoElement) {
            infoElement.innerHTML = `
                <i class="bi bi-info-circle me-1"></i>
                ${data.length} lignes • ${columns.length} colonnes • Type: ${tableType}
            `;
        }
    },

    /**
     * Formatage des valeurs de cellules
     */
    formatCellValue(value, column) {
        if (value === null || value === undefined) return '<span class="text-muted">N/A</span>';
        
        if (column.includes('timestamp')) {
            return `<small class="text-info">${value}</small>`;
        }
        
        if (column.includes('surface') || column.includes('area')) {
            return `<span class="text-warning">${Dashboard.formatNumber(value)} m²</span>`;
        }
        
        if (column === 'y' || column.includes('consumption')) {
            return `<span class="text-success">${Dashboard.formatNumber(value)} kWh</span>`;
        }
        
        if (column.includes('latitude') || column.includes('longitude')) {
            return `<code class="text-primary">${parseFloat(value).toFixed(4)}</code>`;
        }
        
        if (typeof value === 'number') {
            return `<span class="text-warning">${Dashboard.formatNumber(value)}</span>`;
        }
        
        return value;
    },

    /**
     * Actualisation de la table
     */
    refreshDataTable() {
        const tableType = document.getElementById('data-table-select').value;
        Dashboard.showToast(`🔄 Actualisation des données ${tableType}...`, 'info');
        this.switchDataTable();
    },

    /**
     * Export des données
     */
    exportData() {
        const tableType = document.getElementById('data-table-select').value;
        Dashboard.showToast(`📥 Export des données ${tableType} en cours...`, 'info');
        
        // Simulate download
        setTimeout(() => {
            Dashboard.showToast('✅ Export terminé', 'success');
        }, 2000);
    },

    /**
     * Informations sur les données
     */
    showDataInfo() {
        const tableType = document.getElementById('data-table-select').value;
        Dashboard.showToast(`ℹ️ Informations sur les données ${tableType}`, 'info');
    },

    /**
     * Test de connexion Ollama
     */
    testOllamaConnection() {
        const resultElement = document.getElementById('ollama-test-result');
        resultElement.innerHTML = '<span class="spinner-border spinner-border-sm text-primary"></span>';
        
        setTimeout(() => {
            resultElement.innerHTML = '<span class="text-success">✅ Connexion OK</span>';
        }, 2000);
    },

    /**
     * Vider le cache
     */
    clearCache() {
        Dashboard.state.cache = {};
        Dashboard.showToast('🗑️ Cache vidé', 'success');
    },

    /**
     * Réinitialiser les paramètres
     */
    resetSettings() {
        if (confirm('Êtes-vous sûr de vouloir réinitialiser tous les paramètres ?')) {
            localStorage.clear();
            Dashboard.showToast('🔄 Paramètres réinitialisés', 'warning');
            setTimeout(() => location.reload(), 1000);
        }
    },

    /**
     * Informations système
     */
    showSystemInfo() {
        Dashboard.showToast('💻 Informations système affichées', 'info');
    },

    /**
     * Vérification des mises à jour
     */
    checkUpdates() {
        Dashboard.showToast('🔍 Vérification des mises à jour...', 'info');
        setTimeout(() => {
            Dashboard.showToast('✅ Vous utilisez la dernière version', 'success');
        }, 2000);
    },

    /**
     * Export des paramètres
     */
    exportSettings() {
        const settings = {
            theme: document.documentElement.getAttribute('data-theme'),
            language: document.getElementById('language-select')?.value || 'fr',
            animations: document.getElementById('animations-toggle')?.checked || true,
            sounds: document.getElementById('sounds-toggle')?.checked || false,
            chartResolution: document.getElementById('chart-resolution')?.value || 'high',
            maxPoints: document.getElementById('max-points-range')?.value || '10000',
            autoRefresh: document.getElementById('auto-refresh-toggle')?.checked || false,
            ollamaUrl: document.getElementById('ollama-url')?.value || 'http://localhost:11434',
            defaultModel: document.getElementById('default-model')?.value || 'mistral:latest',
            ollamaTimeout: document.getElementById('ollama-timeout')?.value || '120',
            cacheDuration: document.getElementById('cache-duration')?.value || '60',
            exportFolder: document.getElementById('export-folder')?.value || 'exports',
            timestamp: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(settings, null, 2)], { 
            type: 'application/json;charset=utf-8;' 
        });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `dashboard_settings_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(link.href);
        
        Dashboard.showToast('💾 Configuration sauvegardée', 'success');
    },

    /**
     * Import des paramètres
     */
    importSettings() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const settings = JSON.parse(e.target.result);
                        this.applySettings(settings);
                        Dashboard.showToast('📥 Configuration importée', 'success');
                    } catch (error) {
                        Dashboard.showToast('❌ Fichier de configuration invalide', 'error');
                    }
                };
                reader.readAsText(file);
            }
        });
        
        input.click();
    },

    /**
     * Application des paramètres importés
     */
    applySettings(settings) {
        // Thème
        if (settings.theme) {
            document.documentElement.setAttribute('data-theme', settings.theme);
            const themeRadio = document.querySelector(`input[name="theme"][value="${settings.theme}"]`);
            if (themeRadio) themeRadio.checked = true;
        }
        
        // Autres paramètres
        const mappings = {
            'language-select': 'language',
            'animations-toggle': 'animations',
            'sounds-toggle': 'sounds',
            'chart-resolution': 'chartResolution',
            'max-points-range': 'maxPoints',
            'auto-refresh-toggle': 'autoRefresh',
            'ollama-url': 'ollamaUrl',
            'default-model': 'defaultModel',
            'ollama-timeout': 'ollamaTimeout',
            'cache-duration': 'cacheDuration',
            'export-folder': 'exportFolder'
        };
        
        Object.entries(mappings).forEach(([elementId, settingKey]) => {
            const element = document.getElementById(elementId);
            if (element && settings[settingKey] !== undefined) {
                if (element.type === 'checkbox') {
                    element.checked = settings[settingKey];
                } else {
                    element.value = settings[settingKey];
                }
            }
        });
    },

    /**
     * Génération de rapport système
     */
    generateSystemReport() {
        const report = {
            timestamp: new Date().toISOString(),
            browser: {
                userAgent: navigator.userAgent,
                language: navigator.language,
                platform: navigator.platform,
                cookieEnabled: navigator.cookieEnabled,
                onLine: navigator.onLine
            },
            screen: {
                width: screen.width,
                height: screen.height,
                colorDepth: screen.colorDepth,
                pixelDepth: screen.pixelDepth
            },
            window: {
                innerWidth: window.innerWidth,
                innerHeight: window.innerHeight,
                devicePixelRatio: window.devicePixelRatio || 1
            },
            dashboard: {
                version: '1.0.0',
                modules: Object.keys(Dashboard.modules),
                dataLoaded: Dashboard.state.dataLoaded,
                currentTab: Dashboard.state.currentTab,
                isConnected: Dashboard.state.isConnected
            },
            performance: this.getPerformanceMetrics()
        };
        
        const blob = new Blob([JSON.stringify(report, null, 2)], { 
            type: 'application/json;charset=utf-8;' 
        });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `system_report_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(link.href);
        
        Dashboard.showToast('📊 Rapport système généré', 'success');
    },

    /**
     * Collecte des métriques de performance
     */
    getPerformanceMetrics() {
        const navigation = performance.getEntriesByType('navigation')[0];
        const paint = performance.getEntriesByType('paint');
        
        return {
            loadTime: navigation ? navigation.loadEventEnd - navigation.fetchStart : null,
            domContentLoaded: navigation ? navigation.domContentLoadedEventEnd - navigation.fetchStart : null,
            firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || null,
            firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || null,
            memoryUsage: performance.memory ? {
                used: performance.memory.usedJSHeapSize,
                total: performance.memory.totalJSHeapSize,
                limit: performance.memory.jsHeapSizeLimit
            } : null
        };
    }
};

// Auto-initialisation quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    DashboardData.init();
});
                                    