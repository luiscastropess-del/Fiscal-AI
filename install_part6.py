#!/usr/bin/env python3
"""
🤖 FISCAL AI - INSTALADOR AUTOMÁTICO (PARTE 6/6 - FRONTEND)
Cria HTML, CSS e JavaScript
"""

print("🚀 Criando FRONTEND - PARTE 6/6...")
print("=" * 60)

# ============================================================================
# ARQUIVO: templates/index.html
# ============================================================================
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write('''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Fiscal AI - Análise de Extratos Bancários</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <div class="header-content">
                <h1>🤖 Fiscal AI</h1>
                <p class="subtitle">Sistema Inteligente de Análise de Extratos Bancários</p>
            </div>
        </header>

        <!-- Upload Section -->
        <section class="upload-section" id="uploadSection">
            <div class="card">
                <h2>📤 Upload de Extrato</h2>
                <p class="info-text">Envie seu extrato bancário (PDF, Excel ou Word)</p>
                
                <div class="upload-area" id="uploadArea">
                    <input type="file" id="fileInput" accept=".pdf,.xlsx,.xls,.docx,.doc" hidden>
                    <div class="upload-content">
                        <span class="upload-icon">📁</span>
                        <p>Clique ou arraste o arquivo aqui</p>
                        <span class="file-types">PDF, Excel, Word (máx. 10MB)</span>
                    </div>
                </div>
                
                <div id="fileInfo" class="file-info hidden">
                    <span id="fileName"></span>
                    <button id="removeFile" class="btn-remove">✕</button>
                </div>
                
                <button id="uploadBtn" class="btn btn-primary" disabled>
                    Fazer Upload e Analisar
                </button>
                
                <div id="uploadProgress" class="progress-bar hidden">
                    <div class="progress-fill"></div>
                    <span class="progress-text">Processando...</span>
                </div>
            </div>
        </section>

        <!-- Results Section -->
        <section class="results-section hidden" id="resultsSection">
            <!-- Summary Card -->
            <div class="card">
                <h2>📊 Resumo Financeiro</h2>
                <div class="summary-grid">
                    <div class="summary-item">
                        <span class="summary-label">Banco Detectado</span>
                        <span class="summary-value" id="bankDetected">-</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Total de Transações</span>
                        <span class="summary-value" id="totalTransactions">-</span>
                    </div>
                    <div class="summary-item revenue">
                        <span class="summary-label">💰 Total Receitas</span>
                        <span class="summary-value" id="totalRevenue">R$ 0,00</span>
                    </div>
                    <div class="summary-item expense">
                        <span class="summary-label">💸 Total Despesas</span>
                        <span class="summary-value" id="totalExpense">R$ 0,00</span>
                    </div>
                    <div class="summary-item net-income">
                        <span class="summary-label">📈 Resultado Líquido</span>
                        <span class="summary-value" id="netIncome">R$ 0,00</span>
                    </div>
                </div>
            </div>

            <!-- Tax Calculation Card -->
            <div class="card">
                <h2>🧮 Cálculo de Impostos</h2>
                
                <div class="regime-selector">
                    <label for="regimeSelect">Selecione o Regime Tributário:</label>
                    <select id="regimeSelect" class="select-input">
                        <option value="SIMPLES">Simples Nacional</option>
                        <option value="LUCRO_PRESUMIDO">Lucro Presumido</option>
                        <option value="LUCRO_REAL">Lucro Real</option>
                        <option value="MEI">MEI - Microempreendedor Individual</option>
                        <option value="IRPF">IRPF - Pessoa Física</option>
                    </select>
                    <button id="calculateBtn" class="btn btn-secondary">Calcular Impostos</button>
                </div>

                <div id="taxResults" class="tax-results hidden">
                    <div class="tax-summary">
                        <h3>Resultado do Cálculo</h3>
                        <div class="tax-total">
                            <span>Total de Impostos:</span>
                            <span id="totalTax" class="tax-value">R$ 0,00</span>
                        </div>
                        <div id="taxBreakdown" class="tax-breakdown"></div>
                    </div>
                    
                    <div class="guidance-section">
                        <button id="showGuidanceBtn" class="btn btn-info">
                            📋 Ver Orientações da Receita Federal
                        </button>
                        <div id="guidanceContent" class="guidance-content hidden"></div>
                    </div>
                </div>
            </div>

            <!-- Transactions Table -->
            <div class="card">
                <div class="card-header">
                    <h2>📋 Transações Categorizadas</h2>
                    <button id="exportPdfBtn" class="btn btn-success">
                        📄 Exportar Relatório PDF
                    </button>
                </div>
                
                <div class="table-container">
                    <table class="transactions-table">
                        <thead>
                            <tr>
                                <th>Data</th>
                                <th>Descrição</th>
                                <th>Valor</th>
                                <th>Tipo</th>
                                <th>Categoria</th>
                                <th>CPF/CNPJ</th>
                                <th>Confiança</th>
                            </tr>
                        </thead>
                        <tbody id="transactionsBody">
                            <!-- Transações serão inseridas aqui -->
                        </tbody>
                    </table>
                </div>
                
                <div id="noTransactions" class="no-data hidden">
                    Nenhuma transação encontrada
                </div>
            </div>
        </section>

        <!-- Loading Overlay -->
        <div id="loadingOverlay" class="loading-overlay hidden">
            <div class="spinner"></div>
            <p>Processando...</p>
        </div>

        <!-- Footer -->
        <footer class="footer">
            <p>⚠️ <strong>Aviso Legal:</strong> Este sistema é uma ferramenta auxiliar. Sempre consulte um contador habilitado.</p>
            <p>Desenvolvido com ❤️ por <strong>Fiscal AI</strong></p>
        </footer>
    </div>

    <script src="/static/js/app.js"></script>
</body>
</html>
''')
print("✅ templates/index.html")

# ============================================================================
# ARQUIVO: static/css/style.css
# ============================================================================
with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write('''/* Reset e Base */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --primary: #1e40af;
    --primary-dark: #1e3a8a;
    --secondary: #3b82f6;
    --success: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --info: #06b6d4;
    --light: #f3f4f6;
    --dark: #1f2937;
    --border: #e5e7eb;
    --text: #374151;
    --text-light: #6b7280;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: var(--text);
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* Header */
.header {
    background: white;
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 30px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.header h1 {
    font-size: 2.5rem;
    color: var(--primary);
    margin-bottom: 10px;
}

.subtitle {
    color: var(--text-light);
    font-size: 1.1rem;
}

/* Cards */
.card {
    background: white;
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 30px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card h2 {
    color: var(--primary);
    margin-bottom: 20px;
    font-size: 1.5rem;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

/* Upload Area */
.upload-area {
    border: 3px dashed var(--border);
    border-radius: 12px;
    padding: 60px 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-bottom: 20px;
}

.upload-area:hover {
    border-color: var(--primary);
    background: var(--light);
}

.upload-area.drag-over {
    border-color: var(--primary);
    background: #eff6ff;
}

.upload-icon {
    font-size: 4rem;
    display: block;
    margin-bottom: 15px;
}

.upload-content p {
    font-size: 1.2rem;
    color: var(--text);
    margin-bottom: 10px;
}

.file-types {
    color: var(--text-light);
    font-size: 0.9rem;
}

.file-info {
    background: var(--light);
    padding: 15px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.btn-remove {
    background: var(--danger);
    color: white;
    border: none;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 1.2rem;
    transition: all 0.3s ease;
}

.btn-remove:hover {
    background: #dc2626;
    transform: scale(1.1);
}

/* Buttons */
.btn {
    padding: 12px 30px;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-block;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-primary {
    background: var(--primary);
    color: white;
    width: 100%;
}

.btn-primary:hover:not(:disabled) {
    background: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(30, 64, 175, 0.3);
}

.btn-secondary {
    background: var(--secondary);
    color: white;
}

.btn-secondary:hover {
    background: #2563eb;
}

.btn-success {
    background: var(--success);
    color: white;
}

.btn-success:hover {
    background: #059669;
}

.btn-info {
    background: var(--info);
    color: white;
    width: 100%;
    margin-top: 20px;
}

.btn-info:hover {
    background: #0891b2;
}

/* Progress Bar */
.progress-bar {
    background: var(--light);
    border-radius: 8px;
    padding: 15px;
    margin-top: 20px;
    position: relative;
    overflow: hidden;
}

.progress-fill {
    height: 6px;
    background: var(--primary);
    border-radius: 3px;
    animation: progress 2s ease-in-out infinite;
}

.progress-text {
    display: block;
    text-align: center;
    margin-top: 10px;
    color: var(--text-light);
}

@keyframes progress {
    0% { width: 0%; }
    50% { width: 70%; }
    100% { width: 100%; }
}

/* Summary Grid */
.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}

.summary-item {
    background: var(--light);
    padding: 20px;
    border-radius: 8px;
    text-align: center;
}

.summary-item.revenue {
    background: #d1fae5;
    border-left: 4px solid var(--success);
}

.summary-item.expense {
    background: #fee2e2;
    border-left: 4px solid var(--danger);
}

.summary-item.net-income {
    background: #dbeafe;
    border-left: 4px solid var(--primary);
}

.summary-label {
    display: block;
    color: var(--text-light);
    font-size: 0.9rem;
    margin-bottom: 8px;
}

.summary-value {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--dark);
}

/* Regime Selector */
.regime-selector {
    display: flex;
    gap: 15px;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.regime-selector label {
    font-weight: 600;
    color: var(--text);
}

.select-input {
    flex: 1;
    min-width: 200px;
    padding: 10px 15px;
    border: 2px solid var(--border);
    border-radius: 8px;
    font-size: 1rem;
    background: white;
    cursor: pointer;
}

.select-input:focus {
    outline: none;
    border-color: var(--primary);
}

/* Tax Results */
.tax-results {
    margin-top: 20px;
}

.tax-summary {
    background: var(--light);
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.tax-summary h3 {
    color: var(--primary);
    margin-bottom: 15px;
}

.tax-total {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    background: white;
    border-radius: 8px;
    margin-bottom: 15px;
    font-size: 1.2rem;
    font-weight: 600;
}

.tax-value {
    color: var(--primary);
    font-size: 1.5rem;
}

.tax-breakdown {
    display: grid;
    gap: 10px;
}

.tax-item {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background: white;
    border-radius: 6px;
}

.guidance-content {
    background: #fffbeb;
    border-left: 4px solid var(--warning);
    padding: 20px;
    border-radius: 8px;
    margin-top: 15px;
    max-height: 500px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.8;
}

/* Table */
.table-container {
    overflow-x: auto;
}

.transactions-table {
    width: 100%;
    border-collapse: collapse;
}

.transactions-table th {
    background: var(--primary);
    color: white;
    padding: 12px;
    text-align: left;
    font-weight: 600;
    position: sticky;
    top: 0;
}

.transactions-table td {
    padding: 12px;
    border-bottom: 1px solid var(--border);
}

.transactions-table tbody tr:hover {
    background: var(--light);
}

.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
}

.badge-credit {
    background: #d1fae5;
    color: #065f46;
}

.badge-debit {
    background: #fee2e2;
    color: #991b1b;
}

.confidence-bar {
    width: 60px;
    height: 8px;
    background: var(--light);
    border-radius: 4px;
    overflow: hidden;
}

.confidence-fill {
    height: 100%;
    background: var(--success);
    transition: width 0.3s ease;
}

/* Loading Overlay */
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}

.spinner {
    width: 50px;
    height: 50px;
    border: 5px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.loading-overlay p {
    color: white;
    margin-top: 20px;
    font-size: 1.2rem;
}

/* Footer */
.footer {
    text-align: center;
    padding: 30px;
    color: white;
    margin-top: 50px;
}

.footer p {
    margin: 10px 0;
}

/* Utility Classes */
.hidden {
    display: none !important;
}

.info-text {
    color: var(--text-light);
    margin-bottom: 20px;
}

.no-data {
    text-align: center;
    padding: 40px;
    color: var(--text-light);
}

/* Responsive */
@media (max-width: 768px) {
    .header h1 {
        font-size: 1.8rem;
    }
    
    .card {
        padding: 20px;
    }
    
    .card-header {
        flex-direction: column;
        gap: 15px;
    }
    
    .regime-selector {
        flex-direction: column;
        align-items: stretch;
    }
    
    .summary-grid {
        grid-template-columns: 1fr;
    }
    
    .transactions-table {
        font-size: 0.85rem;
    }
    
    .transactions-table th,
    .transactions-table td {
        padding: 8px;
    }
}

@media (max-width: 480px) {
    .container {
        padding: 10px;
    }
    
    .header {
        padding: 20px;
    }
    
    .upload-area {
        padding: 40px 15px;
    }
    
    .upload-icon {
        font-size: 3rem;
    }
}
''')
print("✅ static/css/style.css")

print("\n" + "=" * 60)
print("✅ FRONTEND HTML/CSS CONCLUÍDO!")
print("=" * 60)
print("\n📋 Agora vamos criar o JavaScript...")
print("=" * 60)
