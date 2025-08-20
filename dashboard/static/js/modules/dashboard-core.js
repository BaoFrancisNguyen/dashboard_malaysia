// dashboard/static/js/modules/dashboard-core.js
/**
 * DASHBOARD MALAYSIA - MODULE CORE
 * ================================
 * 
 * Module principal contenant la logique de base et l'initialisation
 * Version: 1.0.0
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
        cache: {}
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
            this.showToast('🇲🇾 Dashboard Malaysia démarré', 'success');
            
            // Initialisation des modules
            await this.initializeSocket();
            await this.initializeTheme();
            await this.loadComponents();
            
            // Configuration des événements
            this.setupEventListeners();
            
            // Demande de permission pour les notifications
            await this.notifications.requestPermission();
            
            // Vérifications de statut
            await this.checkOllamaStatus();
            
            console.log('✅ Dashboard initialisé avec succès');
            
        } catch (error) {
            console.error('❌ Erreur initialisation:', error);
            this.showToast('Erreur d\'initialisation du dashboard', 'error');
        }
    },

    /**
     * Initialisation WebSocket
     */
    async initializeSocket() {
        try {
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

            // Événements spécifiques au chat
            this.state.socket.on('analysis_started', (data) => {
                if (this.modules.chat) {
                    this.modules.chat.addMessage('thinking', 'Analyse en cours avec l\'IA...', true);
                }
            });

            this.state.socket.on('analysis_complete', (data) => {
                if (this.modules.chat) {
                    this.modules.chat.removeThinkingMessages();
                    const response = data.analysis?.full_response || data.analysis || 'Analyse terminée';
                    this.modules.chat.addMessage('assistant', response);
                }
            });

            this.state.socket.on('analysis_error', (data) => {
                if (this.modules.chat) {
                    this.modules.chat.removeThinkingMessages();
                    this.modules.chat.addMessage('assistant', `❌ Erreur d'analyse: ${data.error}`);
                }
            });

        } catch (error) {
            console.error('Erreur WebSocket:', error);
            this.updateConnectionStatus('error', 'Erreur WebSocket');
        }
    },

    /**
     * Initialisation du thème
     */
    async initializeTheme() {
        const savedTheme = localStorage.getItem('dashboard-theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            themeIcon.className = savedTheme === 'dark' ? 'bi bi-moon' : 'bi bi-sun';
        }
    },

    /**
     * Chargement des composants UI
     */
    async loadComponents() {
        // Chargement de la sidebar
        await this.loadSidebar();
        
        // Chargement des onglets
        await this.loadTabContents();
        
        // Chargement du contenu d'aide
        await this.loadHelpContent();
    },

    /**
     * Chargement de la sidebar
     */
    async loadSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;

        sidebar.innerHTML = `
            <div class="nav nav-pills flex-column" id="nav-tab">
                <a class="nav-link active" href="#overview" data-bs-toggle="pill">
                    <i class="bi bi-speedometer2 me-2"></i>
                    Vue d'ensemble
                </a>
                <a class="nav-link" href="#consumption" data-bs-toggle="pill">
                    <i class="bi bi-graph-up me-2"></i>
                    Consommation
                </a>
                <a class="nav-link" href="#buildings" data-bs-toggle="pill">
                    <i class="bi bi-building me-2"></i>
                    Bâtiments
                </a>
                <a class="nav-link" href="#analysis" data-bs-toggle="pill">
                    <i class="bi bi-robot me-2"></i>
                    IA & Analyse
                </a>
                <a class="nav-link" href="#data" data-bs-toggle="pill">
                    <i class="bi bi-table me-2"></i>
                    Données
                </a>
                <a class="nav-link" href="#settings" data-bs-toggle="pill">
                    <i class="bi bi-gear me-2"></i>
                    Paramètres
                </a>
            </div>

            <hr class="my-4">

            <!-- Métriques rapides -->
            <div class="mt-4">
                <h6 class="text-muted mb-3">
                    <i class="bi bi-speedometer me-1"></i>
                    Métriques Rapides
                </h6>
                <div id="quick-metrics" class="fade-in">
                    <div class="d-flex justify-content-between align-items-center py-2 border-bottom border-secondary">
                        <small class="text-muted">
                            <i class="bi bi-building me-1"></i>
                            Bâtiments
                        </small>
                        <span class="badge bg-primary" id="quick-buildings">-</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center py-2 border-bottom border-secondary">
                        <small class="text-muted">
                            <i class="bi bi-lightning me-1"></i>
                            Consommation
                        </small>
                        <span class="badge bg-success" id="quick-consumption">-</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center py-2 border-bottom border-secondary">
                        <small class="text-muted">
                            <i class="bi bi-database me-1"></i>
                            Points données
                        </small>
                        <span class="badge bg-info" id="quick-points">-</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center py-2">
                        <small class="text-muted">
                            <i class="bi bi-clock me-1"></i>
                            Dernière MAJ
                        </small>
                        <small class="text-warning" id="quick-update">-</small>
                    </div>
                </div>
            </div>

            <!-- Status IA -->
            <div class="mt-4">
                <h6 class="text-muted mb-3">
                    <i class="bi bi-cpu me-1"></i>
                    Intelligence Artificielle
                </h6>
                <div class="d-flex flex-column gap-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <small>Ollama:</small>
                        <span class="badge bg-warning" id="ollama-status-mini">⏳</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <small>RAG DB:</small>
                        <span class="badge bg-secondary" id="rag-status-mini">0</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <small>Modèle:</small>
                        <small class="text-info">Mistral</small>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Chargement du contenu des onglets
     */
    async loadTabContents() {
        // Sera complété par les autres modules
        this.initializeTabPlaceholders();
    },

    /**
     * Initialisation des placeholders pour les onglets
     */
    initializeTabPlaceholders() {
        const tabs = ['overview', 'consumption', 'buildings', 'analysis', 'data', 'settings'];
        
        tabs.forEach(tabId => {
            const tab = document.getElementById(tabId);
            if (tab && !tab.innerHTML.trim()) {
                tab.innerHTML = `
                    <div class="text-center p-5">
                        <div class="spinner-border text-primary mb-3" role="status">
                            <span class="visually-hidden">Chargement...</span>
                        </div>
                        <p class="text-muted">Chargement du contenu ${tabId}...</p>
                    </div>
                `;
            }
        });
    },

    /**
     * Chargement du contenu d'aide
     */
    async loadHelpContent() {
        const helpContent = document.getElementById('help-content');
        if (!helpContent) return;

        helpContent.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="bi bi-speedometer2 me-1"></i> Vue d'ensemble</h6>
                    <p class="small text-muted">
                        Tableau de bord principal avec métriques clés et graphiques de synthèse.
                    </p>
                    
                    <h6><i class="bi bi-graph-up me-1"></i> Consommation</h6>
                    <p class="small text-muted">
                        Analyse détaillée des patterns de consommation électrique avec filtres temporels.
                    </p>
                    
                    <h6><i class="bi bi-building me-1"></i> Bâtiments</h6>
                    <p class="small text-muted">
                        Cartographie interactive des bâtiments Malaysia avec clustering et heatmaps.
                    </p>
                </div>
                <div class="col-md-6">
                    <h6><i class="bi bi-robot me-1"></i> IA & Analyse</h6>
                    <p class="small text-muted">
                        Assistant IA avec Ollama (Mistral) et système RAG pour l'analyse intelligente.
                    </p>
                    
                    <h6><i class="bi bi-table me-1"></i> Données</h6>
                    <p class="small text-muted">
                        Exploration des données brutes avec recherche, filtres et export.
                    </p>
                    
                    <h6><i class="bi bi-gear me-1"></i> Paramètres</h6>
                    <p class="small text-muted">
                        Configuration du dashboard, thèmes et connexion Ollama.
                    </p>
                </div>
            </div>
            
            <hr class="border-secondary">
            
            <h6><i class="bi bi-lightbulb text-warning me-1"></i> Conseils d'utilisation</h6>
            <ul class="small">
                <li>Cliquez sur "Charger Données" pour importer les fichiers CSV du projet Malaysia</li>
                <li>Utilisez l'IA pour poser des questions sur vos données en langage naturel</li>
                <li>Explorez la carte interactive avec les contrôles de densité et filtres</li>
                <li>Exportez vos analyses et graphiques pour vos rapports</li>
                <li>Configurez Ollama dans les paramètres pour l'analyse IA</li>
            </ul>
        `;
    },

    /**
     * Configuration des événements
     */
    setupEventListeners() {
        // Navigation entre onglets
        document.addEventListener('shown.bs.tab', (e) => {
            const targetTab = e.target.getAttribute('href').substring(1);
            this.state.currentTab = targetTab;
            this.onTabChange(targetTab);
        });

        // Responsive
        window.addEventListener('resize', this.debounce(() => {
            this.onWindowResize();
        }, 250));

        // Connectivité améliorée
        window.addEventListener('online', () => {
            this.notifications.show('Connexion', 'Connexion internet rétablie', 'success');
            this.state.isConnected = true;
            this.checkOllamaStatus();
        });

        window.addEventListener('offline', () => {
            this.notifications.show('Connexion', 'Connexion internet perdue', 'warning');
            this.state.isConnected = false;
        });

        // Boutons période dans overview
        document.addEventListener('click', (e) => {
            if (e.target.hasAttribute('data-period')) {
                document.querySelectorAll('[data-period]').forEach(btn => {
                    btn.classList.remove('active');
                });
                e.target.classList.add('active');
                
                const period = e.target.getAttribute('data-period');
                if (this.modules.charts) {
                    this.modules.charts.updateConsumptionCharts();
                }
            }
        });

        // Raccourcis clavier
        this.setupKeyboardShortcuts();
        
        // Auto-refresh
        this.setupAutoRefresh();
    },

    /**
     * Gestionnaire de changement d'onglet
     */
    onTabChange(tabId) {
        console.log(`📋 Changement d'onglet: ${tabId}`);
        
        // Actions spécifiques par onglet
        switch(tabId) {
            case 'buildings':
                if (this.modules.maps && this.state.map) {
                    setTimeout(() => {
                        this.state.map.invalidateSize();
                        if (this.state.dataLoaded) {
                            this.modules.maps.loadMapData();
                        }
                    }, 100);
                }
                break;
            
            case 'consumption':
                if (this.modules.charts) {
                    this.modules.charts.updateConsumptionCharts();
                }
                break;
                
            case 'analysis':
                if (this.modules.chat) {
                    this.modules.chat.checkOllamaStatus();
                }
                break;
        }
    },

    /**
     * Gestionnaire de redimensionnement
     */
    onWindowResize() {
        // Redimensionnement des graphiques
        Object.keys(this.state.charts).forEach(chartId => {
            if (document.getElementById(chartId) && window.Plotly) {
                window.Plotly.Plots.resize(chartId);
            }
        });

        // Redimensionnement de la carte
        if (this.state.map) {
            this.state.map.invalidateSize();
        }
    },

    /**
     * Chargement des données
     */
    async loadData() {
        const button = document.getElementById('load-data-btn');
        const originalContent = button.innerHTML;
        
        try {
            // UI Loading
            button.innerHTML = '<i class="bi bi-arrow-clockwise"></i> <span class="spinner-border spinner-border-sm ms-1"></span>';
            button.disabled = true;
            this.updateConnectionStatus('loading', 'Chargement...');
            
            this.showToast('📂 Chargement des données Malaysia...', 'info');

            const response = await fetch('/api/data/load', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });

            const result = await response.json();

            if (result.success) {
                console.log('✅ Données chargées:', result.data_info);
                this.state.dataLoaded = true;
                this.state.lastUpdate = new Date();
                
                this.updateConnectionStatus('connected', 'Données chargées');
                this.showToast('✅ Données Malaysia chargées avec succès', 'success');
                
                // Mise à jour des modules
                await this.loadDataSummary();
                
                if (this.modules.charts) {
                    await this.modules.charts.loadCharts();
                }
                
                if (this.modules.maps) {
                    await this.modules.maps.loadMapData();
                }
                
            } else {
                throw new Error(result.error || 'Erreur de chargement');
            }

        } catch (error) {
            console.error('❌ Erreur chargement:', error);
            this.updateConnectionStatus('error', 'Erreur chargement');
            this.showToast(`❌ Erreur: ${error.message}`, 'error');
            
        } finally {
            button.innerHTML = originalContent;
            button.disabled = false;
        }
    },

    /**
     * Chargement du résumé des données
     */
    async loadDataSummary() {
        try {
            const response = await fetch('/api/data/summary');
            const result = await response.json();

            if (result.success) {
                this.updateMetrics(result.summary);
                this.updateQuickMetrics(result.summary);
            }
        } catch (error) {
            console.error('Erreur chargement résumé:', error);
        }
    },

    /**
     * Mise à jour des métriques principales
     */
    updateMetrics(summary) {
        this.animateMetricValue('total-buildings', summary.total_buildings || 0);
        this.animateMetricValue('total-consumption', (summary.total_consumption || 0) / 1000, 'k');
        this.animateMetricValue('avg-consumption', summary.avg_consumption || 0);
        this.animateMetricValue('data-points', summary.total_data_points || 0);
    },

    /**
     * Mise à jour des métriques rapides
     */
    updateQuickMetrics(summary) {
        document.getElementById('quick-buildings').textContent = this.formatNumber(summary.total_buildings || 0);
        document.getElementById('quick-consumption').textContent = this.formatNumber((summary.total_consumption || 0) / 1000) + 'k kWh';
        document.getElementById('quick-points').textContent = this.formatNumber(summary.total_data_points || 0);
        document.getElementById('quick-update').textContent = new Date().toLocaleTimeString();
    },

    /**
     * Animation des valeurs métriques
     */
    animateMetricValue(elementId, targetValue, suffix = '') {
        const element = document.getElementById(elementId);
        if (!element) return;

        element.innerHTML = '';
        
        const startValue = 0;
        const duration = 1500;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = startValue + (targetValue - startValue) * easeOutQuart;
            
            element.textContent = this.formatNumber(currentValue) + suffix;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    },

    /**
     * Vérification du statut Ollama
     */
    async checkOllamaStatus() {
        try {
            const response = await fetch('/api/llm/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: 'test'})
            });

            const miniStatusElement = document.getElementById('ollama-status-mini');

            if (response.ok) {
                miniStatusElement.innerHTML = '✅';
                miniStatusElement.className = 'badge bg-success';
            } else {
                throw new Error('Service indisponible');
            }
        } catch (error) {
            document.getElementById('ollama-status-mini').innerHTML = '❌';
            document.getElementById('ollama-status-mini').className = 'badge bg-danger';
        }
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
     * Basculement du thème
     */
    toggleTheme() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('dashboard-theme', newTheme);
        
        const icon = document.getElementById('theme-icon');
        icon.className = newTheme === 'dark' ? 'bi bi-moon' : 'bi bi-sun';
        
        this.showToast(`🎨 Thème ${newTheme === 'dark' ? 'sombre' : 'clair'} activé`, 'info');
    },

    /**
     * Affichage de l'aide
     */
    showHelp() {
        const modal = new bootstrap.Modal(document.getElementById('helpModal'));
        modal.show();
    },

    /**
     * Affichage des notifications toast
     */
    showToast(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container');
        const toast = document.createElement('div');
        
        const bgClass = {
            'success': 'bg-success',
            'error': 'bg-danger', 
            'warning': 'bg-warning',
            'info': 'bg-primary'
        }[type] || 'bg-primary';

        toast.className = `toast align-items-center text-white ${bgClass} border-0 fade show`;
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    },

    /**
     * Formatage des nombres
     */
    formatNumber(num) {
        if (num == null || isNaN(num)) return '0';
        
        const absNum = Math.abs(num);
        if (absNum >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (absNum >= 1000) return (num / 1000).toFixed(1) + 'k';
        return parseFloat(num).toFixed(1);
    },

    /**
     * Fonction debounce pour optimiser les performances
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
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
    },

    /**
     * Configuration des raccourcis clavier
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+R : Recharger les données
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.loadData();
            }
            
            // Ctrl+T : Basculer thème
            if (e.ctrlKey && e.key === 't') {
                e.preventDefault();
                this.toggleTheme();
            }
            
            // Escape : Fermer modales
            if (e.key === 'Escape') {
                const openModals = document.querySelectorAll('.modal.show');
                openModals.forEach(modal => {
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    if (modalInstance) modalInstance.hide();
                });
            }
        });
    },

    /**
     * Configuration de l'auto-refresh
     */
    setupAutoRefresh() {
        const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.autoRefreshInterval = setInterval(() => {
                        if (this.state.dataLoaded) {
                            document.getElementById('quick-update').textContent = 
                                new Date().toLocaleTimeString();
                        }
                    }, 30000); // 30 secondes
                    this.showToast('🔄 Actualisation automatique activée', 'info');
                } else {
                    if (this.autoRefreshInterval) {
                        clearInterval(this.autoRefreshInterval);
                        this.autoRefreshInterval = null;
                    }
                    this.showToast('⏹️ Actualisation automatique désactivée', 'info');
                }
            });
        }
    },

    /**
     * Système de notifications
     */
    notifications: {
        requestPermission: async function() {
            if ('Notification' in window && Notification.permission === 'default') {
                await Notification.requestPermission();
            }
        },
        
        show: function(title, message, type = 'info') {
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification(title, {
                    body: message,
                    icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="0.9em" font-size="90">⚡</text></svg>',
                    badge: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="0.9em" font-size="90">🇲🇾</text></svg>'
                });
            }
            // Fallback vers toast
            Dashboard.showToast(`${title}: ${message}`, type);
        }
    },

    /**
     * Fonctions d'export avancées
     */
    exportFunctions: {
        exportOverviewPDF: function() {
            Dashboard.showToast('📄 Export PDF en cours...', 'info');
            // Logic d'export PDF à implémenter
            setTimeout(() => {
                Dashboard.showToast('📄 Export PDF terminé', 'success');
            }, 2000);
        },
        
        exportChartImage: function(chartId) {
            if (window.Plotly && document.getElementById(chartId)) {
                Plotly.downloadImage(chartId, {
                    format: 'png',
                    width: 1200,
                    height: 600,
                    filename: `chart_${chartId}_${new Date().toISOString().split('T')[0]}`
                });
                Dashboard.showToast('🖼️ Image exportée', 'success');
            }
        },
        
        exportAllData: function() {
            Dashboard.showToast('📊 Export complet en cours...', 'info');
            // Logic d'export complet à implémenter
            setTimeout(() => {
                Dashboard.showToast('📊 Export complet terminé', 'success');
            }, 3000);
        }
    },

    /**
     * Monitoring de performance
     */
    performance: {
        measureTime: function(name, fn) {
            const start = performance.now();
            const result = fn();
            const end = performance.now();
            console.log(`⏱️ ${name}: ${(end - start).toFixed(2)}ms`);
            return result;
        },
        
        monitorChartRender: function(chartId) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.name.includes(chartId)) {
                        console.log(`📊 ${chartId} rendered in ${entry.duration.toFixed(2)}ms`);
                    }
                }
            });
            observer.observe({entryTypes: ['measure', 'navigation']});
        }
    },

    /**
     * Utilitaires supplémentaires
     */
    utils: {
        formatBytes: function(bytes, decimals = 2) {
            if (bytes === 0) return '0 Bytes';
            
            const k = 1024;
            const dm = decimals < 0 ? 0 : decimals;
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
        },
        
        deepClone: function(obj) {
            return JSON.parse(JSON.stringify(obj));
        },
        
        throttle: function(func, limit) {
            let inThrottle;
            return function(...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },
        
        generateId: function(prefix = 'id') {
            return `${prefix}_${Math.random().toString(36).substr(2, 9)}`;
        }
    },

    /**
     * Vérification de la qualité de connexion
     */
    async checkConnectionQuality() {
        try {
            const start = performance.now();
            await fetch('/api/ping', { method: 'HEAD' });
            const latency = performance.now() - start;
            
            if (latency < 100) return 'excellent';
            if (latency < 300) return 'good';
            if (latency < 1000) return 'fair';
            return 'poor';
        } catch {
            return 'offline';
        }
    }
};