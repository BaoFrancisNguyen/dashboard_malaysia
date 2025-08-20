// dashboard/static/js/modules/dashboard-ui.js
/**
 * DASHBOARD MALAYSIA - MODULE UI
 * ==============================
 * 
 * Module pour les utilitaires d'interface utilisateur
 * Version: 1.0.0
 */

const DashboardUI = {
    /**
     * Initialisation du module
     */
    init() {
        console.log('🎨 Initialisation module UI');
        this.setupProgressRings();
        this.setupThemeHandlers();
        this.setupRangeInputs();
        this.initializeDefaultValues();
        Dashboard.registerModule('ui', this);
    },

    /**
     * Configuration des anneaux de progression
     */
    setupProgressRings() {
        const style = document.createElement('style');
        style.textContent = `
            .progress-ring {
                width: 24px;
                height: 24px;
            }

            .progress-ring circle {
                fill: none;
                stroke: var(--primary-color);
                stroke-width: 2;
                stroke-dasharray: 75.4;
                stroke-dashoffset: 75.4;
                animation: progress 2s linear infinite;
            }

            @keyframes progress {
                to {
                    stroke-dashoffset: 0;
                }
            }

            .loading-skeleton {
                background: linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
                border-radius: 8px;
                height: 20px;
            }

            @keyframes loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }

            .fade-in {
                animation: fadeIn 0.5s ease-out;
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            .slide-up {
                animation: slideUp 0.4s ease-out;
            }

            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .card-hover-effect {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            .card-hover-effect:hover {
                transform: translateY(-4px) scale(1.02);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            }

            .metric-card {
                text-align: center;
                padding: 2rem 1.5rem;
                position: relative;
            }

            .metric-value {
                font-size: 3rem;
                font-weight: 800;
                line-height: 1;
                margin-bottom: 0.5rem;
                background: var(--gradient-primary);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .metric-label {
                color: var(--secondary-color);
                font-size: 0.95rem;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .metric-trend {
                margin-top: 0.75rem;
                font-size: 0.875rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.25rem;
            }

            .trend-up { color: var(--success-color); }
            .trend-down { color: var(--danger-color); }
            .trend-stable { color: var(--warning-color); }

            .chart-container {
                height: 450px;
                position: relative;
                padding: 1rem;
            }

            .map-container {
                height: 550px;
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid var(--border-color);
                position: relative;
            }

            .status-indicator {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                display: inline-block;
                margin-right: 0.5rem;
                position: relative;
            }

            .status-connected { 
                background: var(--success-color);
                box-shadow: 0 0 8px rgba(5, 150, 105, 0.5);
            }

            .status-loading { 
                background: var(--warning-color);
                animation: pulse 2s infinite;
            }

            .status-error { 
                background: var(--danger-color);
                box-shadow: 0 0 8px rgba(220, 38, 38, 0.5);
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
        `;
        document.head.appendChild(style);
    },

    /**
     * Configuration des gestionnaires de thème
     */
    setupThemeHandlers() {
        // Gestionnaire pour les boutons radio de thème
        const themeRadios = document.querySelectorAll('input[name="theme"]');
        themeRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.applyTheme(e.target.value);
                }
            });
        });

        // Initialiser le thème actuel
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const activeRadio = document.querySelector(`input[name="theme"][value="${currentTheme}"]`);
        if (activeRadio) {
            activeRadio.checked = true;
        }
    },

    /**
     * Application d'un thème
     */
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('dashboard-theme', theme);
        
        const icon = document.getElementById('theme-icon');
        if (icon) {
            icon.className = theme === 'dark' ? 'bi bi-moon' : 'bi bi-sun';
        }
        
        Dashboard.showToast(`🎨 Thème ${theme === 'dark' ? 'sombre' : 'clair'} activé`, 'info');
    },

    /**
     * Configuration des inputs range
     */
    setupRangeInputs() {
        // Gestionnaire pour max-points-range
        const maxPointsRange = document.getElementById('max-points-range');
        if (maxPointsRange) {
            maxPointsRange.addEventListener('input', function() {
                const valueElement = document.getElementById('max-points-value');
                if (valueElement) {
                    valueElement.textContent = (this.value / 1000) + 'k';
                }
            });
        }

        // Gestionnaire pour temperature-range (dans le chat)
        const temperatureRange = document.getElementById('temperature-range');
        if (temperatureRange) {
            temperatureRange.addEventListener('input', function() {
                const valueElement = document.getElementById('temp-value');
                if (valueElement) {
                    valueElement.textContent = this.value;
                }
            });
        }

        // Gestionnaire pour map-density
        const mapDensity = document.getElementById('map-density');
        if (mapDensity) {
            mapDensity.addEventListener('input', function() {
                const displayElement = document.getElementById('density-display');
                if (displayElement) {
                    displayElement.textContent = this.value;
                }
            });
        }
    },

    /**
     * Initialisation des valeurs par défaut
     */
    initializeDefaultValues() {
        // Valeurs par défaut pour RAG
        setTimeout(() => {
            if (!Dashboard.state.dataLoaded) {
                const ragItems = document.getElementById('rag-items');
                const ragTypes = document.getElementById('rag-types');
                const ragStatusMini = document.getElementById('rag-status-mini');
                
                if (ragItems) ragItems.textContent = '0';
                if (ragTypes) ragTypes.textContent = '0';
                if (ragStatusMini) ragStatusMini.textContent = '0';
                
                Dashboard.showToast('💡 Cliquez sur "Charger Données" pour importer vos fichiers Malaysia', 'info');
            }
        }, 3000);
    },

    /**
     * Animation de compteur
     */
    animateCounter(elementId, targetValue, duration = 1000, suffix = '') {
        const element = document.getElementById(elementId);
        if (!element) return;

        const startValue = 0;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Fonction d'easing
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = startValue + (targetValue - startValue) * easeOutQuart;
            
            element.textContent = Dashboard.formatNumber(currentValue) + suffix;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    },

    /**
     * Animation de fade in pour un élément
     */
    fadeIn(element, duration = 300) {
        if (!element) return;
        
        element.style.opacity = '0';
        element.style.display = 'block';
        
        let start = performance.now();
        const animate = (timestamp) => {
            const elapsed = timestamp - start;
            const progress = elapsed / duration;
            
            if (progress < 1) {
                element.style.opacity = progress;
                requestAnimationFrame(animate);
            } else {
                element.style.opacity = '1';
            }
        };
        
        requestAnimationFrame(animate);
    },

    /**
     * Animation de slide up pour un élément
     */
    slideUp(element, duration = 400) {
        if (!element) return;
        
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.display = 'block';
        
        let start = performance.now();
        const animate = (timestamp) => {
            const elapsed = timestamp - start;
            const progress = elapsed / duration;
            
            if (progress < 1) {
                const easeOut = 1 - Math.pow(1 - progress, 3);
                element.style.opacity = progress;
                element.style.transform = `translateY(${20 * (1 - easeOut)}px)`;
                requestAnimationFrame(animate);
            } else {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        };
        
        requestAnimationFrame(animate);
    },

    /**
     * Création d'un indicateur de chargement
     */
    createLoadingIndicator(text = 'Chargement...') {
        const indicator = document.createElement('div');
        indicator.className = 'text-center p-4';
        indicator.innerHTML = `
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Chargement...</span>
            </div>
            <p class="text-muted">${text}</p>
        `;
        return indicator;
    },

    /**
     * Création d'un message d'erreur
     */
    createErrorMessage(message, retryCallback = null) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'text-center p-4';
        
        let retryButton = '';
        if (retryCallback) {
            const retryId = 'retry-' + Math.random().toString(36).substr(2, 9);
            retryButton = `
                <button class="btn btn-outline-primary btn-sm mt-2" onclick="(${retryCallback.toString()})()">
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    Réessayer
                </button>
            `;
        }
        
        errorDiv.innerHTML = `
            <i class="bi bi-exclamation-triangle fs-1 text-warning mb-3"></i>
            <p class="text-muted">${message}</p>
            ${retryButton}
        `;
        
        return errorDiv;
    },

    /**
     * Création d'un message vide
     */
    createEmptyMessage(message, actionText = null, actionCallback = null) {
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'text-center p-5';
        
        let actionButton = '';
        if (actionText && actionCallback) {
            actionButton = `
                <button class="btn btn-outline-primary mt-3" onclick="(${actionCallback.toString()})()">
                    <i class="bi bi-plus-circle me-1"></i>
                    ${actionText}
                </button>
            `;
        }
        
        emptyDiv.innerHTML = `
            <i class="bi bi-inbox fs-1 text-muted mb-3"></i>
            <p class="text-muted">${message}</p>
            ${actionButton}
        `;
        
        return emptyDiv;
    },

    /**
     * Mise à jour d'un badge avec animation
     */
    updateBadgeWithAnimation(elementId, newValue, color = 'primary') {
        const element = document.getElementById(elementId);
        if (!element) return;

        // Animation de sortie
        element.style.transform = 'scale(0.8)';
        element.style.opacity = '0.5';
        
        setTimeout(() => {
            element.textContent = newValue;
            element.className = `badge bg-${color}`;
            
            // Animation d'entrée
            element.style.transform = 'scale(1.1)';
            element.style.opacity = '1';
            
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 150);
        }, 150);
    },

    /**
     * Gestion responsive des éléments
     */
    handleResponsive() {
        const isMobile = window.innerWidth < 768;
        
        // Ajustements pour mobile
        if (isMobile) {
            // Réduire la taille des graphiques
            document.querySelectorAll('.chart-container').forEach(container => {
                container.style.height = '300px';
            });
            
            // Réduire la hauteur de la carte
            const mapContainer = document.querySelector('.map-container');
            if (mapContainer) {
                mapContainer.style.height = '350px';
            }
            
            // Ajuster la sidebar
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                sidebar.style.height = 'auto';
                sidebar.style.borderRight = 'none';
                sidebar.style.borderBottom = '1px solid var(--border-color)';
            }
        } else {
            // Restaurer les tailles desktop
            document.querySelectorAll('.chart-container').forEach(container => {
                container.style.height = '450px';
            });
            
            const mapContainer = document.querySelector('.map-container');
            if (mapContainer) {
                mapContainer.style.height = '550px';
            }
        }
    },

    /**
     * Gestion des tooltips Bootstrap
     */
    initializeTooltips() {
        // Initialiser tous les tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    /**
     * Création d'un skeleton loader
     */
    createSkeletonLoader(lines = 3, height = '20px') {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton-container';
        
        for (let i = 0; i < lines; i++) {
            const line = document.createElement('div');
            line.className = 'loading-skeleton mb-2';
            line.style.height = height;
            line.style.width = i === lines - 1 ? '75%' : '100%';
            skeleton.appendChild(line);
        }
        
        return skeleton;
    },

    /**
     * Validation d'un formulaire
     */
    validateForm(formElement) {
        let isValid = true;
        const requiredFields = formElement.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    },

    /**
     * Formatage d'une date relative
     */
    formatRelativeTime(date) {
        const now = new Date();
        const diff = now - new Date(date);
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `il y a ${days} jour${days > 1 ? 's' : ''}`;
        if (hours > 0) return `il y a ${hours} heure${hours > 1 ? 's' : ''}`;
        if (minutes > 0) return `il y a ${minutes} minute${minutes > 1 ? 's' : ''}`;
        return 'à l\'instant';
    },

    /**
     * Copie de texte dans le presse-papiers
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            Dashboard.showToast('📋 Copié dans le presse-papiers', 'success');
        } catch (err) {
            console.error('Erreur copie:', err);
            Dashboard.showToast('❌ Erreur lors de la copie', 'error');
        }
    },

    /**
     * Téléchargement d'un fichier
     */
    downloadFile(content, filename, contentType = 'text/plain') {
        const blob = new Blob([content], { type: contentType });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        window.URL.revokeObjectURL(url);
    },

    /**
     * Gestion de la visibilité de page
     */
    handlePageVisibility() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                console.log('🔇 Page masquée - pause des animations');
                // Pause des animations coûteuses
            } else {
                console.log('👁️ Page visible - reprise des animations');
                // Reprise des animations
                Dashboard.checkOllamaStatus();
            }
        });
    }
};

// Auto-initialisation quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    DashboardUI.init();
    
    // Configuration responsive
    window.addEventListener('resize', Dashboard.debounce(() => {
        DashboardUI.handleResponsive();
    }, 250));
    
    // Gestion de la visibilité
    DashboardUI.handlePageVisibility();
    
    // Initialisation des tooltips
    setTimeout(() => {
        DashboardUI.initializeTooltips();
    }, 1000);
});