// dashboard/static/js/modules/dashboard-chat.js
/**
 * DASHBOARD MALAYSIA - MODULE CHAT
 * ================================
 * 
 * Module pour la gestion du chat IA avec Ollama
 * Version: 1.0.0
 */

const DashboardChat = {
    /**
     * Initialisation du module
     */
    init() {
        console.log('🤖 Initialisation module Chat');
        this.loadAnalysisContent();
        this.checkOllamaStatus();
        Dashboard.registerModule('chat', this);
    },

    /**
     * Chargement du contenu de l'onglet Analyse
     */
    loadAnalysisContent() {
        const analysis = document.getElementById('analysis');
        if (!analysis) return;

        analysis.innerHTML = `
            <div class="row mb-4">
                <div class="col-md-8">
                    <h2 class="h3 mb-2">
                        <i class="bi bi-robot text-primary me-2"></i>
                        Intelligence Artificielle & Analyse
                    </h2>
                    <p class="text-muted">
                        <i class="bi bi-cpu me-1"></i>
                        Analyse intelligente avec Ollama (Mistral) et système RAG
                    </p>
                </div>
                <div class="col-md-4">
                    <div class="card border-primary">
                        <div class="card-body text-center py-3">
                            <div class="d-flex align-items-center justify-content-center">
                                <i class="bi bi-cpu text-primary me-2 fs-4"></i>
                                <div>
                                    <div class="fw-bold">Ollama Status</div>
                                    <span id="ollama-status" class="badge bg-warning">Vérification...</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row g-4">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header bg-transparent border-bottom">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">
                                    <i class="bi bi-chat-left-text text-success me-2"></i>
                                    Assistant IA Malaysia
                                </h5>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-light" onclick="DashboardChat.clearChat()">
                                        <i class="bi bi-trash3 me-1"></i>
                                        Effacer
                                    </button>
                                    <button class="btn btn-outline-light" onclick="DashboardChat.exportChat()">
                                        <i class="bi bi-download me-1"></i>
                                        Export
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="chat-container">
                                <div class="chat-messages" id="chat-messages">
                                    <div class="chat-message message-assistant fade-in">
                                        <div class="d-flex align-items-start">
                                            <i class="bi bi-robot text-primary me-2 mt-1"></i>
                                            <div>
                                                <strong>Assistant IA Malaysia:</strong>
                                                <p class="mb-0 mt-1">
                                                    Bonjour ! Je suis votre assistant d'analyse des données énergétiques de Malaysia. 
                                                    Posez-moi vos questions sur la consommation électrique, les bâtiments, 
                                                    les tendances ou demandez-moi des recommandations d'optimisation.
                                                    <br><br>
                                                    <em class="text-muted">
                                                        💡 Tip: Utilisez les suggestions ci-contre pour commencer !
                                                    </em>
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="input-group">
                                    <input type="text" class="form-control chat-input" id="chat-input" 
                                           placeholder="Posez votre question sur les données Malaysia..." 
                                           onkeypress="DashboardChat.handleKeyPress(event)">
                                    <button class="btn btn-primary" onclick="DashboardChat.sendMessage()" id="send-btn">
                                        <i class="bi bi-send"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card mb-3">
                        <div class="card-header bg-transparent border-bottom">
                            <h5 class="mb-0">
                                <i class="bi bi-lightbulb text-warning me-2"></i>
                                Questions Suggérées
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-light btn-sm text-start d-flex align-items-center" 
                                        onclick="DashboardChat.askSuggestedQuestion('Quelle est la consommation moyenne par type de bâtiment ?')">
                                    <i class="bi bi-graph-up text-primary me-2"></i>
                                    <span>Consommation par type</span>
                                </button>
                                <button class="btn btn-outline-light btn-sm text-start d-flex align-items-center" 
                                        onclick="DashboardChat.askSuggestedQuestion('Quels sont les pics de consommation horaires ?')">
                                    <i class="bi bi-clock text-warning me-2"></i>
                                    <span>Pics de consommation</span>
                                </button>
                                <button class="btn btn-outline-light btn-sm text-start d-flex align-items-center" 
                                        onclick="DashboardChat.askSuggestedQuestion('Quelles zones géographiques consomment le plus ?')">
                                    <i class="bi bi-geo-alt text-danger me-2"></i>
                                    <span>Zones consommatrices</span>
                                </button>
                                <button class="btn btn-outline-light btn-sm text-start d-flex align-items-center" 
                                        onclick="DashboardChat.askSuggestedQuestion('Y a-t-il des tendances saisonnières dans la consommation ?')">
                                    <i class="bi bi-calendar3 text-info me-2"></i>
                                    <span>Tendances saisonnières</span>
                                </button>
                                <button class="btn btn-outline-light btn-sm text-start d-flex align-items-center" 
                                        onclick="DashboardChat.askSuggestedQuestion('Quelles sont vos recommandations d\\'optimisation énergétique ?')">
                                    <i class="bi bi-lightbulb text-success me-2"></i>
                                    <span>Optimisations suggérées</span>
                                </button>
                                <button class="btn btn-outline-light btn-sm text-start d-flex align-items-center" 
                                        onclick="DashboardChat.askSuggestedQuestion('Analysez les corrélations entre météo et consommation électrique')">
                                    <i class="bi bi-cloud-sun text-secondary me-2"></i>
                                    <span>Corrélations météo</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="card mb-3">
                        <div class="card-header bg-transparent border-bottom">
                            <h6 class="mb-0">
                                <i class="bi bi-database text-info me-2"></i>
                                Base de Connaissances RAG
                            </h6>
                        </div>
                        <div class="card-body">
                            <div class="row text-center mb-3">
                                <div class="col-6">
                                    <div class="border-end">
                                        <div class="h5 text-primary mb-1" id="rag-items">-</div>
                                        <small class="text-muted">Items</small>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="h5 text-success mb-1" id="rag-types">-</div>
                                    <small class="text-muted">Types</small>
                                </div>
                            </div>
                            <button class="btn btn-outline-warning btn-sm w-100" onclick="DashboardChat.updateRAG()">
                                <i class="bi bi-arrow-clockwise me-1"></i>
                                Mettre à jour RAG
                            </button>
                            <div class="mt-2">
                                <small class="text-muted">
                                    <i class="bi bi-info-circle me-1"></i>
                                    Le système RAG indexe automatiquement vos données pour des réponses plus précises.
                                </small>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header bg-transparent border-bottom">
                            <h6 class="mb-0">
                                <i class="bi bi-gear text-secondary me-2"></i>
                                Configuration IA
                            </h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label small">Modèle:</label>
                                <select class="form-select form-select-sm" id="model-select">
                                    <option value="mistral:latest">Mistral Latest</option>
                                    <option value="llama2">Llama 2</option>
                                    <option value="codellama">Code Llama</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label small">Température: <span id="temp-value">0.1</span></label>
                                <input type="range" class="form-range" id="temperature-range" 
                                       min="0" max="1" step="0.1" value="0.1"
                                       oninput="DashboardChat.updateTemperature(this.value)">
                            </div>
                            <div class="small text-muted">
                                <i class="bi bi-info-circle me-1"></i>
                                Température faible = réponses plus factuelles
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Vérification du statut d'Ollama
     */
    async checkOllamaStatus() {
        try {
            const response = await fetch('/api/llm/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: 'test'})
            });

            const statusElement = document.getElementById('ollama-status');

            if (response.ok) {
                statusElement.innerHTML = '<span class="badge bg-success">✅ Mistral disponible</span>';
            } else {
                throw new Error('Service indisponible');
            }
        } catch (error) {
            document.getElementById('ollama-status').innerHTML = '<span class="badge bg-warning">⚠️ Ollama non connecté</span>';
        }
    },

    /**
     * Gestion de la touche Entrée
     */
    handleKeyPress(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    },

    /**
     * Envoi d'un message
     */
    sendMessage() {
        const input = document.getElementById('chat-input');
        const question = input.value.trim();

        if (!question) return;

        this.addMessage('user', question);
        input.value = '';

        if (Dashboard.state.isConnected && Dashboard.state.socket) {
            Dashboard.state.socket.emit('request_analysis', { question: question });
        } else {
            this.addMessage('assistant', 'Connexion WebSocket non disponible. Vérifiez la connexion au serveur.');
        }
    },

    /**
     * Question suggérée
     */
    askSuggestedQuestion(question) {
        document.getElementById('chat-input').value = question;
        this.sendMessage();
    },

    /**
     * Ajout d'un message au chat
     */
    addMessage(type, content, isThinking = false) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');

        messageDiv.className = `chat-message message-${type}`;
        if (isThinking) messageDiv.className += ' message-thinking';

        const icon = type === 'user' ? 'bi-person-circle' : 'bi-robot';
        const prefix = type === 'user' ? 'Vous' : 'Assistant IA Malaysia';

        messageDiv.innerHTML = `
            <div class="d-flex align-items-start">
                <i class="bi ${icon} text-${type === 'user' ? 'primary' : 'success'} me-2 mt-1"></i>
                <div class="flex-grow-1">
                    <strong>${prefix}:</strong>
                    <div class="mt-1">${content}</div>
                </div>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    },

    /**
     * Suppression des messages de réflexion
     */
    removeThinkingMessages() {
        const thinkingMessages = document.querySelectorAll('.message-thinking');
        thinkingMessages.forEach(msg => msg.remove());
    },

    /**
     * Effacement du chat
     */
    clearChat() {
        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.innerHTML = `
            <div class="chat-message message-assistant fade-in">
                <div class="d-flex align-items-start">
                    <i class="bi bi-robot text-success me-2 mt-1"></i>
                    <div>
                        <strong>Assistant IA Malaysia:</strong>
                        <p class="mb-0 mt-1">Chat réinitialisé. Comment puis-je vous aider avec l'analyse des données Malaysia ?</p>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Mise à jour de la base RAG
     */
    async updateRAG() {
        try {
            Dashboard.showToast('🧠 Mise à jour de la base RAG...', 'info');
            
            const response = await fetch('/api/rag/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });

            const result = await response.json();

            if (result.success) {
                this.addMessage('assistant', '✅ Base de connaissances RAG mise à jour avec succès !');
                document.getElementById('rag-items').textContent = '500+';
                document.getElementById('rag-types').textContent = '8';
                document.getElementById('rag-status-mini').textContent = '500+';
                Dashboard.showToast('✅ Base RAG mise à jour', 'success');
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.addMessage('assistant', `❌ Erreur mise à jour RAG: ${error.message}`);
            Dashboard.showToast('❌ Erreur mise à jour RAG', 'error');
        }
    },

    /**
     * Mise à jour de la température
     */
    updateTemperature(value) {
        document.getElementById('temp-value').textContent = value;
    },

    /**
     * Export du chat
     */
    exportChat() {
        Dashboard.showToast('💬 Export de la conversation...', 'info');
        
        const chatMessages = document.querySelectorAll('.chat-message');
        let chatContent = '# Conversation Dashboard Malaysia\n\n';
        chatContent += `Date: ${new Date().toLocaleString('fr-FR')}\n\n`;
        
        chatMessages.forEach((message, index) => {
            const isUser = message.classList.contains('message-user');
            const isThinking = message.classList.contains('message-thinking');
            
            if (!isThinking) {
                const speaker = isUser ? 'Utilisateur' : 'Assistant IA';
                const content = message.textContent.replace(/^(Vous:|Assistant IA Malaysia:)/, '').trim();
                
                chatContent += `## ${speaker}\n\n${content}\n\n`;
            }
        });
        
        // Téléchargement du fichier markdown
        const blob = new Blob([chatContent], { type: 'text/markdown;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `chat_malaysia_${new Date().toISOString().split('T')[0]}.md`;
        link.click();
        URL.revokeObjectURL(link.href);
        
        Dashboard.showToast('💬 Conversation exportée', 'success');
    },

    /**
     * Sauvegarde de la configuration du chat
     */
    saveConfiguration() {
        const config = {
            model: document.getElementById('model-select')?.value || 'mistral:latest',
            temperature: document.getElementById('temperature-range')?.value || '0.1',
            ollamaUrl: document.getElementById('ollama-url')?.value || 'http://localhost:11434',
            timestamp: new Date().toISOString()
        };
        
        localStorage.setItem('dashboard-chat-config', JSON.stringify(config));
        Dashboard.showToast('⚙️ Configuration sauvegardée', 'success');
    },

    /**
     * Chargement de la configuration du chat
     */
    loadConfiguration() {
        try {
            const config = JSON.parse(localStorage.getItem('dashboard-chat-config') || '{}');
            
            if (config.model) {
                const modelSelect = document.getElementById('model-select');
                if (modelSelect) modelSelect.value = config.model;
            }
            
            if (config.temperature) {
                const tempRange = document.getElementById('temperature-range');
                const tempValue = document.getElementById('temp-value');
                if (tempRange) tempRange.value = config.temperature;
                if (tempValue) tempValue.textContent = config.temperature;
            }
            
            if (config.ollamaUrl) {
                const ollamaUrl = document.getElementById('ollama-url');
                if (ollamaUrl) ollamaUrl.value = config.ollamaUrl;
            }
            
        } catch (error) {
            console.warn('Erreur chargement configuration chat:', error);
        }
    },

    /**
     * Analyse de sentiment des messages
     */
    analyzeSentiment(message) {
        const positiveWords = ['excellent', 'parfait', 'super', 'génial', 'merci', 'bravo'];
        const negativeWords = ['erreur', 'problème', 'bug', 'cassé', 'mauvais', 'nul'];
        
        const words = message.toLowerCase().split(/\s+/);
        let score = 0;
        
        words.forEach(word => {
            if (positiveWords.includes(word)) score += 1;
            if (negativeWords.includes(word)) score -= 1;
        });
        
        if (score > 0) return 'positive';
        if (score < 0) return 'negative';
        return 'neutral';
    }
};

// Auto-initialisation quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    DashboardChat.init();
    
    // Chargement de la configuration sauvegardée
    setTimeout(() => {
        DashboardChat.loadConfiguration();
    }, 500);
});