#!/usr/bin/env python3
"""
🤖 FISCAL AI - INSTALADOR AUTOMÁTICO (PARTE 7/7 - JAVASCRIPT FINAL)
Cria app.js e finaliza instalação
"""

print("🚀 Criando JAVASCRIPT - PARTE 7/7 FINAL...")
print("=" * 60)

# ============================================================================
# ARQUIVO: static/js/app.js
# ============================================================================
with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write('''// Fiscal AI - Frontend JavaScript
class FiscalAI {
    constructor() {
        this.currentFileId = null;
        this.currentTransactions = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
    }

    setupEventListeners() {
        // Upload area click
        document.getElementById('uploadArea').addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });

        // File input change
        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // Remove file
        document.getElementById('removeFile').addEventListener('click', () => {
            this.clearFile();
        });

        // Upload button
        document.getElementById('uploadBtn').addEventListener('click', () => {
            this.uploadFile();
        });

        // Calculate taxes button
        document.getElementById('calculateBtn').addEventListener('click', () => {
            this.calculateTaxes();
        });

        // Show guidance button
        document.getElementById('showGuidanceBtn').addEventListener('click', () => {
            this.toggleGuidance();
        });

        // Export PDF button
        document.getElementById('exportPdfBtn').addEventListener('click', () => {
            this.exportPDF();
        });
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            const file = e.dataTransfer.files[0];
            if (file) {
                this.handleFileSelect(file);
            }
        });
    }

    handleFileSelect(file) {
        if (!file) return;

        // Validate file type
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                             'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                             'application/msword'];
        
        if (!allowedTypes.includes(file.type)) {
            this.showError('Tipo de arquivo não permitido. Use PDF, Excel ou Word.');
            return;
        }

        // Validate file size (10MB)
        if (file.size > 10 * 1024 * 1024) {
            this.showError('Arquivo muito grande. Tamanho máximo: 10MB');
            return;
        }

        // Store file
        this.selectedFile = file;

        // Show file info
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileInfo').classList.remove('hidden');
        document.getElementById('uploadBtn').disabled = false;
    }

    clearFile() {
        this.selectedFile = null;
        document.getElementById('fileInput').value = '';
        document.getElementById('fileInfo').classList.add('hidden');
        document.getElementById('uploadBtn').disabled = true;
    }

    async uploadFile() {
        if (!this.selectedFile) return;

        const formData = new FormData();
        formData.append('file', this.selectedFile);

        this.showLoading(true);
        document.getElementById('uploadProgress').classList.remove('hidden');

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Erro ao fazer upload');
            }

            this.currentFileId = data.file_id;
            
            // Show results
            this.displaySummary(data);
            await this.loadTransactions(data.file_id);
            
            // Hide upload section, show results
            document.getElementById('uploadSection').classList.add('hidden');
            document.getElementById('resultsSection').classList.remove('hidden');
            
            // Scroll to results
            document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            this.showError(error.message);
        } finally {
            this.showLoading(false);
            document.getElementById('uploadProgress').classList.add('hidden');
        }
    }

    displaySummary(data) {
        document.getElementById('bankDetected').textContent = data.bank_detected || 'N/A';
        document.getElementById('totalTransactions').textContent = data.total_transactions || 0;
        document.getElementById('totalRevenue').textContent = this.formatCurrency(data.total_revenue || 0);
        document.getElementById('totalExpense').textContent = this.formatCurrency(data.total_expense || 0);
        
        const netIncome = (data.total_revenue || 0) - (data.total_expense || 0);
        document.getElementById('netIncome').textContent = this.formatCurrency(netIncome);
    }

    async loadTransactions(fileId) {
        try {
            const response = await fetch(`/api/files/${fileId}/transactions`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Erro ao carregar transações');
            }

            this.currentTransactions = data.transactions;
            this.displayTransactions(data.transactions);

        } catch (error) {
            this.showError(error.message);
        }
    }

    displayTransactions(transactions) {
        const tbody = document.getElementById('transactionsBody');
        tbody.innerHTML = '';

        if (!transactions || transactions.length === 0) {
            document.getElementById('noTransactions').classList.remove('hidden');
            return;
        }

        document.getElementById('noTransactions').classList.add('hidden');

        transactions.forEach(trans => {
            const row = document.createElement('tr');
            
            const date = new Date(trans.date).toLocaleDateString('pt-BR');
            const type = trans.transaction_type === 'CREDITO' ? 'badge-credit' : 'badge-debit';
            const typeText = trans.transaction_type === 'CREDITO' ? '💰 Receita' : '💸 Despesa';
            const confidence = Math.round((trans.confidence || 0) * 100);
            
            row.innerHTML = `
                <td>${date}</td>
                <td>${this.truncate(trans.description, 50)}</td>
                <td><strong>${this.formatCurrency(trans.value)}</strong></td>
                <td><span class="badge ${type}">${typeText}</span></td>
                <td>${this.formatCategory(trans.category_name)}</td>
                <td>${trans.cpf_cnpj || '-'}</td>
                <td>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${confidence}%"></div>
                    </div>
                    <small>${confidence}%</small>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }

    async calculateTaxes() {
        if (!this.currentFileId) return;

        const regime = document.getElementById('regimeSelect').value;
        
        this.showLoading(true);

        try {
            const response = await fetch(`/api/files/${this.currentFileId}/calculate-taxes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ regime })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Erro ao calcular impostos');
            }

            this.displayTaxResults(data);

        } catch (error) {
            this.showError(error.message);
        } finally {
            this.showLoading(false);
        }
    }

    displayTaxResults(data) {
        const taxResults = document.getElementById('taxResults');
        taxResults.classList.remove('hidden');

        const taxCalc = data.tax_calculation;

        // Display total tax
        document.getElementById('totalTax').textContent = this.formatCurrency(taxCalc.total_tax || 0);

        // Display breakdown
        const breakdown = document.getElementById('taxBreakdown');
        breakdown.innerHTML = '';

        if (taxCalc.taxes) {
            Object.entries(taxCalc.taxes).forEach(([key, value]) => {
                const item = document.createElement('div');
                item.className = 'tax-item';
                item.innerHTML = `
                    <span>${this.formatTaxName(key)}</span>
                    <strong>${this.formatCurrency(value)}</strong>
                `;
                breakdown.appendChild(item);
            });
        }

        if (taxCalc.effective_rate) {
            const rateItem = document.createElement('div');
            rateItem.className = 'tax-item';
            rateItem.innerHTML = `
                <span>Alíquota Efetiva</span>
                <strong>${taxCalc.effective_rate.toFixed(2)}%</strong>
            `;
            breakdown.appendChild(rateItem);
        }

        if (taxCalc.monthly_average) {
            const monthlyItem = document.createElement('div');
            monthlyItem.className = 'tax-item';
            monthlyItem.innerHTML = `
                <span>Média Mensal</span>
                <strong>${this.formatCurrency(taxCalc.monthly_average)}</strong>
            `;
            breakdown.appendChild(monthlyItem);
        }

        // Store guidance
        this.currentGuidance = taxCalc.guidance || '';
        
        // Show guidance button
        document.getElementById('showGuidanceBtn').classList.remove('hidden');
    }

    toggleGuidance() {
        const guidanceContent = document.getElementById('guidanceContent');
        const btn = document.getElementById('showGuidanceBtn');
        
        if (guidanceContent.classList.contains('hidden')) {
            guidanceContent.textContent = this.currentGuidance;
            guidanceContent.classList.remove('hidden');
            btn.textContent = '📋 Ocultar Orientações';
        } else {
            guidanceContent.classList.add('hidden');
            btn.textContent = '📋 Ver Orientações da Receita Federal';
        }
    }

    async exportPDF() {
        if (!this.currentFileId) return;

        const regime = document.getElementById('regimeSelect').value;
        
        this.showLoading(true);

        try {
            const response = await fetch(`/api/files/${this.currentFileId}/export-pdf`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ regime })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Erro ao exportar PDF');
            }

            // Download PDF
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `relatorio_fiscal_${this.currentFileId}_${new Date().getTime()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.showSuccess('Relatório PDF exportado com sucesso!');

        } catch (error) {
            this.showError(error.message);
        } finally {
            this.showLoading(false);
        }
    }

    // Utility functions
    formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    }

    formatCategory(category) {
        if (!category) return '-';
        return category.replace(/_/g, ' ').toLowerCase()
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    formatTaxName(name) {
        const names = {
            'irpj': 'IRPJ',
            'csll': 'CSLL',
            'pis': 'PIS',
            'cofins': 'COFINS',
            'inss': 'INSS',
            'iss': 'ISS'
        };
        return names[name.toLowerCase()] || name.toUpperCase();
    }

    truncate(text, length) {
        if (!text) return '';
        if (text.length <= length) return text;
        return text.substring(0, length) + '...';
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }

    showError(message) {
        alert('❌ Erro: ' + message);
    }

    showSuccess(message) {
        alert('✅ ' + message);
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    new FiscalAI();
});
''')
print("✅ static/js/app.js")

# ============================================================================
# ARQUIVO: .gitignore
# ============================================================================
with open('.gitignore', 'w', encoding='utf-8') as f:
    f.write('''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Database
*.db
*.sqlite
*.sqlite3

# Uploads
uploads/
*.pdf
*.xlsx
*.xls
*.docx
*.doc

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment
.env
.env.local
''')
print("✅ .gitignore")

# ============================================================================
# ARQUIVO: README.md
# ============================================================================
with open('README.md', 'w', encoding='utf-8') as f:
    f.write('''# 🤖 Fiscal AI - Sistema de Análise de Extratos Bancários

Sistema inteligente para análise automática de extratos bancários com categorização fiscal e cálculo de impostos.

## 🚀 Funcionalidades

- ✅ **Upload de Extratos**: PDF, Excel, Word
- ✅ **Detecção Automática de Bancos**: Santander, Nubank, Inter, Mercado Pago
- ✅ **Categorização Fiscal Inteligente**: Baseada em palavras-chave da Receita Federal
- ✅ **Cálculo de Impostos**: Simples Nacional, Lucro Presumido, Lucro Real, MEI, IRPF
- ✅ **Orientações da Receita Federal**: Guidance específico por categoria
- ✅ **Exportação em PDF**: Relatório completo profissional
- ✅ **Interface Responsiva**: Funciona em desktop e mobile

## 📋 Requisitos

- Python 3.11+
- Flask
- pdfplumber
- pandas
- reportlab

## 🔧 Instalação

### Método 1: Replit (Recomendado)

1. Acesse [replit.com](https://replit.com)
2. Crie novo Repl Python
3. Cole os scripts de instalação (Partes 1-7)
4. Execute cada parte em sequência
5. Renomeie `_main.py` para `main.py`
6. Clique em Run

### Método 2: Local

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/fiscal-ai.git
cd fiscal-ai

# Instale dependências
pip install -r requirements.txt

# Execute
python main.py
