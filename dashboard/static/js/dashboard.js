
/* static/js/dashboard.js */
/**
 * Dashboard Malaysia - JavaScript principal
 * Fonctions utilitaires et interactions
 */

// Configuration globale
const DASHBOARD_CONFIG = {
    apiBaseUrl: '',
    refreshInterval: 30000, // 30 secondes
    animationDuration: 500,
    maxRetries: 3
};

// État global de l'application
window.dashboardState = {
    isConnected: false,
    dataLoaded: false,
    currentTab: 'overview',
    lastUpdate: null,
    retryCount: 0
};

/**
 * Utilitaires de formatage
 */
const formatUtils = {
    number: (num, decimals = 1) => {
        if (num >= 1000000) return `${(num / 1000000).toFixed(decimals)}M`;
        if (num >= 1000) return `${(num / 1000).toFixed(decimals)}k`;
        return num.toFixed(decimals);
    },
    
    percentage: (value, decimals = 1) => {
        if (value >= 0 && value <= 1) value *= 100;
        return `${value.toFixed(decimals)}%`;
    },
    
    datetime: (dateString) => {
        return new Date(dateString).toLocaleString('fr-FR', {
            year: 'numeric',
            month: '2-digit', 
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    fileSize: (bytes) => {
        const sizes = ['B', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 B';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
    }
};

/**
 * Gestionnaire d'erreurs global
 */
const errorHandler = {
    show: (message, type = 'error') => {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        // Auto-dismiss après 5 secondes
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    },
    
    handle: (error, context = '') => {
        console.error(`Erreur ${context}:`, error);
        errorHandler.show(`Erreur ${context}: ${error.message}`);
    }
};

/**
 * Gestionnaire d'animations
 */
const animationUtils = {
    fadeIn: (element, duration = 300) => {
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
    
    countUp: (element, target, duration = 1000) => {
        const start = performance.now();
        const startValue = 0;
        
        const animate = (timestamp) => {
            const elapsed = timestamp - start;
            const progress = elapsed / duration;
            
            if (progress < 1) {
                const currentValue = startValue + (target - startValue) * progress;
                element.textContent = formatUtils.number(currentValue);
                requestAnimationFrame(animate);
            } else {
                element.textContent = formatUtils.number(target);
            }
        };
        
        requestAnimationFrame(animate);
    }
};

/**
 * API Client avec retry automatique
 */
const apiClient = {
    async request(url, options = {}) {
        const maxRetries = DASHBOARD_CONFIG.maxRetries;
        let retryCount = 0;
        
        while (retryCount <= maxRetries) {
            try {
                const response = await fetch(url, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    },
                    ...options
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                window.dashboardState.retryCount = 0; // Reset sur succès
                return data;
                
            } catch (error) {
                retryCount++;
                window.dashboardState.retryCount = retryCount;
                
                if (retryCount > maxRetries) {
                    throw new Error(`Échec après ${maxRetries} tentatives: ${error.message}`);
                }
                
                // Délai exponential backoff
                const delay = Math.pow(2, retryCount) * 1000;
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
};

/**
 * Gestionnaire de notifications temps réel
 */
const notificationManager = {
    show: (title, message, type = 'info') => {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/images/logo.png',
                badge: '/static/images/badge.png'
            });
        }
        
        // Notification in-app comme fallback
        errorHandler.show(`${title}: ${message}`, type);
    },
    
    requestPermission: async () => {
        if ('Notification' in window && Notification.permission === 'default') {
            await Notification.requestPermission();
        }
    }
};

/**
 * Utilitaires de performance
 */
const performanceUtils = {
    measureTime: (name, fn) => {
        const start = performance.now();
        const result = fn();
        const end = performance.now();
        console.log(`⏱️ ${name}: ${(end - start).toFixed(2)}ms`);
        return result;
    },
    
    debounce: (func, wait) => {
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
    
    throttle: (func, limit) => {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

/**
 * Gestionnaire de thème sombre/clair
 */
const themeManager = {
    current: 'dark',
    
    toggle: () => {
        themeManager.current = themeManager.current === 'dark' ? 'light' : 'dark';
        themeManager.apply();
    },
    
    apply: () => {
        document.documentElement.setAttribute('data-theme', themeManager.current);
        localStorage.setItem('dashboard-theme', themeManager.current);
    },
    
    init: () => {
        const saved = localStorage.getItem('dashboard-theme');
        if (saved) {
            themeManager.current = saved;
        }
        themeManager.apply();
    }
};

/**
 * Gestionnaire de responsive design
 */
const responsiveManager = {
    breakpoints: {
        xs: 576,
        sm: 768,
        md: 992,
        lg: 1200,
        xl: 1400
    },
    
    getCurrentBreakpoint: () => {
        const width = window.innerWidth;
        for (const [name, minWidth] of Object.entries(responsiveManager.breakpoints).reverse()) {
            if (width >= minWidth) return name;
        }
        return 'xs';
    },
    
    isMobile: () => {
        return responsiveManager.getCurrentBreakpoint() in ['xs', 'sm'];
    }
};

/**
 * Initialisation du dashboard
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Dashboard Malaysia - Initialisation JavaScript');
    
    // Configuration initiale
    themeManager.init();
    notificationManager.requestPermission();
    
    // Gestionnaires d'événements globaux
    window.addEventListener('resize', performanceUtils.debounce(() => {
        const breakpoint = responsiveManager.getCurrentBreakpoint();
        console.log(`📱 Breakpoint: ${breakpoint}`);
        
        // Réajuster les graphiques si nécessaire
        if (window.Plotly) {
            document.querySelectorAll('[id*="chart"]').forEach(chart => {
                window.Plotly.Plots.resize(chart);
            });
        }
    }, 250));
    
    // Gestion de la connectivité
    window.addEventListener('online', () => {
        notificationManager.show('Connexion', 'Connexion internet rétablie', 'success');
        window.dashboardState.isConnected = true;
    });
    
    window.addEventListener('offline', () => {
        notificationManager.show('Connexion', 'Connexion internet perdue', 'warning');
        window.dashboardState.isConnected = false;
    });
    
    console.log('✅ JavaScript Dashboard initialisé');
});

// Export des utilitaires pour utilisation globale
window.dashboardUtils = {
    formatUtils,
    errorHandler,
    animationUtils,
    apiClient,
    notificationManager,
    performanceUtils,
    themeManager,
    responsiveManager
};