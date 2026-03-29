import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self, db_name: str = "fiscal_ai.db"):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Inicializa banco de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de arquivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                bank_detected TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'PENDING',
                total_transactions INTEGER DEFAULT 0,
                total_revenue REAL DEFAULT 0,
                total_expense REAL DEFAULT 0
            )
        ''')
        
        # Tabela de transações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                date DATE NOT NULL,
                description TEXT NOT NULL,
                value REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                cpf_cnpj TEXT,
                category_code TEXT,
                category_name TEXT,
                tax_rate REAL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                confidence REAL DEFAULT 0,
                guidance TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files (id)
            )
        ''')
        
        # Tabela de categorias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                tax_rate REAL DEFAULT 0,
                guidance TEXT,
                keywords TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Popula categorias padrão
        self.populate_categories()
    
    def populate_categories(self):
        """Popula categorias fiscais padrão"""
        categories = [
            {
                'code': '3.01.01',
                'name': 'RECEITA_VENDA_MERCADORIAS',
                'description': 'Receitas de vendas de mercadorias',
                'tax_rate': 0.0,
                'keywords': json.dumps(['venda', 'vendas', 'receita', 'faturamento', 'pix recebido', 'ted recebida', 'transferencia recebida']),
                'guidance': 'Lançar em Rendimentos Tributáveis. Se sem CPF/CNPJ, usar código 99.99.999/9999-99 e nome "DIVERSOS".'
            },
            {
                'code': '3.02.01',
                'name': 'RECEITA_PRESTACAO_SERVICOS',
                'description': 'Receitas de prestação de serviços',
                'tax_rate': 0.0,
                'keywords': json.dumps(['servico', 'serviço', 'consultoria', 'honorario', 'honorário', 'pagamento recebido']),
                'guidance': 'DIRPF → Rendimentos Tributáveis Recebidos de PJ. Sem CNPJ: informar "DIVERSOS" e detalhar.'
            },
            {
                'code': '3.03.01',
                'name': 'RECEITA_ALUGUEL',
                'description': 'Receitas de aluguéis',
                'tax_rate': 0.0,
                'keywords': json.dumps(['aluguel', 'aluguer', 'locacao', 'locação', 'rent']),
                'guidance': 'Rendimentos de Aluguéis. Sem CPF: discriminar imóvel e período na declaração.'
            },
            {
                'code': '4.01.01',
                'name': 'DESPESA_FORNECEDORES',
                'description': 'Despesas com fornecedores',
                'tax_rate': 0.0,
                'keywords': json.dumps(['compra', 'fornecedor', 'mercadoria', 'estoque', 'pagamento', 'pix enviado', 'ted enviada']),
                'guidance': 'Livro Caixa → Despesas Operacionais. Sem CNPJ: manter recibos com RG do vendedor.'
            },
            {
                'code': '4.02.01',
                'name': 'DESPESA_PESSOAL',
                'description': 'Despesas com pessoal',
                'tax_rate': 0.0,
                'keywords': json.dumps(['salario', 'salário', 'folha', 'funcionario', 'funcionário', 'pro-labore', 'pró-labore']),
                'guidance': 'DIPJ → Despesas com Pessoal. CPF obrigatório para funcionários e sócios.'
            },
            {
                'code': '4.03.01',
                'name': 'DESPESA_TRIBUTARIA',
                'description': 'Tributos e contribuições',
                'tax_rate': 0.0,
                'keywords': json.dumps(['imposto', 'taxa', 'contribuicao', 'contribuição', 'tributo', 'darf', 'das', 'inss', 'fgts']),
                'guidance': 'DIPJ → Tributos e Contribuições. Anexar DARFs e comprovantes.'
            },
            {
                'code': '4.04.01',
                'name': 'DESPESA_ADMINISTRATIVA',
                'description': 'Despesas administrativas',
                'tax_rate': 0.0,
                'keywords': json.dumps(['agua', 'água', 'luz', 'energia', 'telefone', 'internet', 'aluguel', 'escritorio', 'escritório', 'material']),
                'guidance': 'Livro Caixa → Despesas Administrativas. Dedutível proporcionalmente ao uso empresarial.'
            },
            {
                'code': '4.05.01',
                'name': 'DESPESA_FINANCEIRA',
                'description': 'Despesas financeiras',
                'tax_rate': 0.0,
                'keywords': json.dumps(['juros', 'tarifa', 'taxa bancaria', 'taxa bancária', 'emprestimo', 'empréstimo', 'financiamento', 'iof']),
                'guidance': 'DIPJ → Despesas Financeiras. Apenas juros são dedutíveis (não o principal).'
            }
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for cat in categories:
            cursor.execute('''
                INSERT OR IGNORE INTO categories (code, name, description, tax_rate, keywords, guidance)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (cat['code'], cat['name'], cat['description'], cat['tax_rate'], cat['keywords'], cat['guidance']))
        
        conn.commit()
        conn.close()
    
    def create_file(self, filename: str, file_type: str, bank_detected: str = None) -> int:
        """Cria registro de arquivo"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO files (filename, file_type, bank_detected, status)
            VALUES (?, ?, ?, 'PROCESSING')
        ''', (filename, file_type, bank_detected))
        
        file_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return file_id
    
    def create_transaction(self, file_id: int, transaction: Dict[str, Any]) -> int:
        """Cria registro de transação"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions (
                file_id, date, description, value, transaction_type,
                cpf_cnpj, category_code, category_name, tax_rate,
                tax_amount, confidence, guidance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_id,
            transaction.get('date'),
            transaction.get('description'),
            transaction.get('value'),
            transaction.get('transaction_type'),
            transaction.get('cpf_cnpj'),
            transaction.get('category_code'),
            transaction.get('category_name'),
            transaction.get('tax_rate', 0),
            transaction.get('tax_amount', 0),
            transaction.get('confidence', 0),
            transaction.get('guidance')
        ))
        
        trans_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return trans_id
    
    def update_file_status(self, file_id: int, status: str, total_transactions: int = 0,
                          total_revenue: float = 0, total_expense: float = 0):
        """Atualiza status do arquivo"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE files 
            SET status = ?, total_transactions = ?, total_revenue = ?, total_expense = ?
            WHERE id = ?
        ''', (status, total_transactions, total_revenue, total_expense, file_id))
        
        conn.commit()
        conn.close()
    
    def get_file(self, file_id: int) -> Optional[Dict[str, Any]]:
        """Busca arquivo por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM files WHERE id = ?', (file_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_transactions(self, file_id: int) -> List[Dict[str, Any]]:
        """Busca transações de um arquivo"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE file_id = ? 
            ORDER BY date DESC
        ''', (file_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Busca todas as categorias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM categories ORDER BY code')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def cleanup_old_files(self, days: int = 7):
        """Remove arquivos antigos (economia de espaço)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM transactions 
            WHERE file_id IN (
                SELECT id FROM files 
                WHERE upload_date < datetime('now', '-' || ? || ' days')
            )
        ''', (days,))
        
        cursor.execute('''
            DELETE FROM files 
            WHERE upload_date < datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        conn.commit()
        conn.close()
