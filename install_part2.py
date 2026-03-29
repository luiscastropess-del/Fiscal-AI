#!/usr/bin/env python3
"""
🤖 FISCAL AI - INSTALADOR AUTOMÁTICO (PARTE 2/3)
Cria extractors e services
"""

print("🚀 Continuando instalação - PARTE 2/3...")
print("=" * 60)

# ============================================================================
# ARQUIVO: extractors/pdf_extractor.py
# ============================================================================
with open('extractors/pdf_extractor.py', 'w', encoding='utf-8') as f:
    f.write('''import pdfplumber
import PyPDF2
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from io import BytesIO

class PDFExtractor:
    """Extrator otimizado para PDFs bancários"""
    
    def __init__(self):
        self.patterns = {
            'date': [
                r'\\b(\\d{2})[/-](\\d{2})[/-](\\d{4})\\b',
                r'\\b(\\d{2})[/-](\\d{2})[/-](\\d{2})\\b',
                r'\\b(\\d{4})[/-](\\d{2})[/-](\\d{2})\\b'
            ],
            'value': [
                r'R?\\$?\\s*(\\d{1,3}(?:\\.\\d{3})*,\\d{2})',
                r'(\\d{1,3}(?:\\.\\d{3})*,\\d{2})',
                r'(\\d+,\\d{2})'
            ],
            'cpf': r'\\b(\\d{3}\\.?\\d{3}\\.?\\d{3}-?\\d{2})\\b',
            'cnpj': r'\\b(\\d{2}\\.?\\d{3}\\.?\\d{3}/?\\d{4}-?\\d{2})\\b'
        }
        
        self.bank_patterns = {
            'santander': {
                'identifier': ['santander', 'banco santander'],
                'transaction_pattern': r'(\\d{2}/\\d{2})\\s+(.+?)\\s+([\\d.,]+)(?:\\s+([CD]))?',
                'balance_keywords': ['saldo', 'saldo anterior', 'saldo atual']
            },
            'nubank': {
                'identifier': ['nubank', 'nu pagamentos'],
                'transaction_pattern': r'(\\d{2}\\s+\\w{3})\\s+(.+?)\\s+R\\$\\s*([\\d.,]+)',
                'balance_keywords': ['saldo disponível', 'limite disponível']
            },
            'inter': {
                'identifier': ['inter', 'banco inter'],
                'transaction_pattern': r'(\\d{2}/\\d{2}/\\d{4})\\s+(.+?)\\s+([\\d.,]+)',
                'balance_keywords': ['saldo', 'saldo em conta']
            },
            'mercadopago': {
                'identifier': ['mercado pago', 'mercadopago', 'mp'],
                'transaction_pattern': r'(\\d{2}/\\d{2}/\\d{4})\\s+(.+?)\\s+R\\$\\s*([\\d.,]+)',
                'balance_keywords': ['saldo', 'disponível']
            }
        }
    
    async def extract(self, file_content: bytes) -> Dict[str, Any]:
        """Extrai dados do PDF"""
        try:
            bank = self._detect_bank(file_content)
            transactions = await self._extract_with_pdfplumber(file_content, bank)
            
            if not transactions:
                transactions = await self._extract_with_pypdf2(file_content, bank)
            
            return {
                'bank': bank,
                'transactions': transactions,
                'total_found': len(transactions)
            }
        
        except Exception as e:
            raise Exception(f"Erro ao extrair PDF: {str(e)}")
    
    def _detect_bank(self, file_content: bytes) -> Optional[str]:
        """Detecta o banco pelo conteúdo do PDF"""
        try:
            with pdfplumber.open(BytesIO(file_content)) as pdf:
                first_page_text = pdf.pages[0].extract_text().lower()
                
                for bank, config in self.bank_patterns.items():
                    for identifier in config['identifier']:
                        if identifier in first_page_text:
                            return bank.upper()
            
            return 'GENERICO'
        
        except Exception:
            return 'GENERICO'
    
    async def _extract_with_pdfplumber(self, file_content: bytes, bank: str) -> List[Dict[str, Any]]:
        """Extração com pdfplumber"""
        transactions = []
        
        try:
            with pdfplumber.open(BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    
                    if tables:
                        for table in tables:
                            transactions.extend(self._parse_table(table, bank))
                    
                    if not tables:
                        text = page.extract_text()
                        if text:
                            transactions.extend(self._parse_text(text, bank))
        
        except Exception as e:
            print(f"Erro pdfplumber: {e}")
        
        return transactions
    
    async def _extract_with_pypdf2(self, file_content: bytes, bank: str) -> List[Dict[str, Any]]:
        """Extração com PyPDF2 (fallback)"""
        transactions = []
        
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    transactions.extend(self._parse_text(text, bank))
        
        except Exception as e:
            print(f"Erro PyPDF2: {e}")
        
        return transactions
    
    def _parse_table(self, table: List[List[str]], bank: str) -> List[Dict[str, Any]]:
        """Parse de tabela extraída"""
        transactions = []
        
        if not table or len(table) < 2:
            return transactions
        
        header = [str(cell).lower().strip() if cell else '' for cell in table[0]]
        
        date_idx = self._find_column_index(header, ['data', 'date', 'dt'])
        desc_idx = self._find_column_index(header, ['descrição', 'descricao', 'historico', 'description', 'lancamento', 'lançamento'])
        value_idx = self._find_column_index(header, ['valor', 'value', 'montante', 'debito', 'débito', 'credito', 'crédito'])
        
        for row in table[1:]:
            if not row or len(row) < 2:
                continue
            
            try:
                date_str = row[date_idx] if date_idx is not None and date_idx < len(row) else None
                desc_str = row[desc_idx] if desc_idx is not None and desc_idx < len(row) else ''
                value_str = row[value_idx] if value_idx is not None and value_idx < len(row) else None
                
                if not date_str or not value_str:
                    continue
                
                parsed_date = self._parse_date(str(date_str))
                parsed_value = self._parse_value(str(value_str))
                
                if parsed_date and parsed_value != 0:
                    transaction = {
                        'date': parsed_date,
                        'description': str(desc_str).strip(),
                        'value': parsed_value,
                        'cpf_cnpj': self._extract_cpf_cnpj(' '.join(str(cell) for cell in row if cell)),
                        'raw_data': ' | '.join(str(cell) for cell in row if cell)
                    }
                    transactions.append(transaction)
            
            except Exception:
                continue
        
        return transactions
    
    def _parse_text(self, text: str, bank: str) -> List[Dict[str, Any]]:
        """Parse de texto livre"""
        transactions = []
        lines = text.split('\\n')
        
        bank_config = self.bank_patterns.get(bank.lower(), {})
        pattern = bank_config.get('transaction_pattern')
        
        if pattern:
            for line in lines:
                match = re.search(pattern, line)
                if match:
                    try:
                        date_str = match.group(1)
                        description = match.group(2).strip()
                        value_str = match.group(3)
                        
                        parsed_date = self._parse_date(date_str)
                        parsed_value = self._parse_value(value_str)
                        
                        if parsed_date and parsed_value != 0:
                            transaction = {
                                'date': parsed_date,
                                'description': description,
                                'value': parsed_value,
                                'cpf_cnpj': self._extract_cpf_cnpj(line),
                                'raw_data': line
                            }
                            transactions.append(transaction)
                    except Exception:
                        continue
        
        if not transactions:
            for line in lines:
                dates = self._find_dates(line)
                values = self._find_values(line)
                
                if dates and values:
                    for date_str, value_str in zip(dates, values):
                        parsed_date = self._parse_date(date_str)
                        parsed_value = self._parse_value(value_str)
                        
                        if parsed_date and parsed_value != 0:
                            transaction = {
                                'date': parsed_date,
                                'description': line.strip(),
                                'value': parsed_value,
                                'cpf_cnpj': self._extract_cpf_cnpj(line),
                                'raw_data': line
                            }
                            transactions.append(transaction)
                            break
        
        return transactions
    
    def _find_dates(self, text: str) -> List[str]:
        dates = []
        for pattern in self.patterns['date']:
            matches = re.findall(pattern, text)
            if matches:
                dates.extend(['-'.join(m) if isinstance(m, tuple) else m for m in matches])
        return dates
    
    def _find_values(self, text: str) -> List[str]:
        values = []
        for pattern in self.patterns['value']:
            matches = re.findall(pattern, text)
            if matches:
                values.extend(matches)
        return values
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        if not date_str:
            return None
        
        date_str = str(date_str).strip()
        date_str = re.sub(r'[^\\d/-]', '', date_str)
        
        formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y',
            '%Y-%m-%d', '%Y/%m/%d',
            '%d%m%Y', '%d%m%y'
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                if parsed.year < 100:
                    parsed = parsed.replace(year=parsed.year + 2000)
                return parsed
            except ValueError:
                continue
        
        return None
    
    def _parse_value(self, value_str: str) -> float:
        if not value_str:
            return 0.0
        
        value_str = str(value_str).strip()
        value_str = re.sub(r'[R$\\s]', '', value_str)
        
        if ',' in value_str and '.' in value_str:
            value_str = value_str.replace('.', '').replace(',', '.')
        elif ',' in value_str:
            parts = value_str.split(',')
            if len(parts[-1]) == 2:
                value_str = value_str.replace(',', '.')
            else:
                value_str = value_str.replace(',', '')
        
        try:
            return float(value_str)
        except ValueError:
            return 0.0
    
    def _extract_cpf_cnpj(self, text: str) -> Optional[str]:
        if not text:
            return None
        
        cnpj_match = re.search(self.patterns['cnpj'], text)
        if cnpj_match:
            return cnpj_match.group(1)
        
        cpf_match = re.search(self.patterns['cpf'], text)
        if cpf_match:
            return cpf_match.group(1)
        
        return None
    
    def _find_column_index(self, header: List[str], keywords: List[str]) -> Optional[int]:
        for i, col in enumerate(header):
            if any(keyword in col for keyword in keywords):
                return i
        return None
''')
print("✅ extractors/pdf_extractor.py")

# ============================================================================
# ARQUIVO: extractors/excel_extractor.py
# ============================================================================
with open('extractors/excel_extractor.py', 'w', encoding='utf-8') as f:
    f.write('''import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from io import BytesIO
import re

class ExcelExtractor:
    """Extrator para arquivos Excel"""
    
    def __init__(self):
        self.date_keywords = ['data', 'date', 'dt', 'dia']
        self.desc_keywords = ['descrição', 'descricao', 'historico', 'histórico', 'description', 'lancamento', 'lançamento']
        self.value_keywords = ['valor', 'value', 'montante', 'debito', 'débito', 'credito', 'crédito']
    
    async def extract(self, file_content: bytes) -> Dict[str, Any]:
        """Extrai dados do Excel"""
        try:
            df = pd.read_excel(BytesIO(file_content))
            
            date_col = self._find_column(df, self.date_keywords)
            desc_col = self._find_column(df, self.desc_keywords)
            value_col = self._find_column(df, self.value_keywords)
            
            if not date_col or not value_col:
                raise Exception("Não foi possível identificar colunas de data e valor")
            
            transactions = []
            
            for _, row in df.iterrows():
                try:
                    date_val = row[date_col]
                    desc_val = row[desc_col] if desc_col else ''
                    value_val = row[value_col]
                    
                    if pd.isna(date_val):
                        continue
                    
                    if isinstance(date_val, datetime):
                        parsed_date = date_val
                    else:
                        parsed_date = self._parse_date(str(date_val))
                    
                    if not parsed_date:
                        continue
                    
                    if pd.isna(value_val):
                        continue
                    
                    parsed_value = float(value_val) if isinstance(value_val, (int, float)) else self._parse_value(str(value_val))
                    
                    if parsed_value == 0:
                        continue
                    
                    transaction = {
                        'date': parsed_date,
                        'description': str(desc_val).strip() if desc_val else '',
                        'value': parsed_value,
                        'cpf_cnpj': self._extract_cpf_cnpj(str(row.to_dict())),
                        'raw_data': str(row.to_dict())
                    }
                    
                    transactions.append(transaction)
                
                except Exception:
                    continue
            
            return {
                'bank': 'EXCEL',
                'transactions': transactions,
                'total_found': len(transactions)
            }
        
        except Exception as e:
            raise Exception(f"Erro ao extrair Excel: {str(e)}")
    
    def _find_column(self, df: pd.DataFrame, keywords: List[str]) -> str:
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in keywords):
                return col
        return None
    
    def _parse_date(self, date_str: str) -> datetime:
        date_str = str(date_str).strip()
        
        formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y',
            '%Y-%m-%d', '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _parse_value(self, value_str: str) -> float:
        value_str = str(value_str).strip()
        value_str = re.sub(r'[R$\\s]', '', value_str)
        value_str = value_str.replace('.', '').replace(',', '.')
        
        try:
            return float(value_str)
        except ValueError:
            return 0.0
    
    def _extract_cpf_cnpj(self, text: str) -> str:
        cpf_pattern = r'\\b(\\d{3}\\.?\\d{3}\\.?\\d{3}-?\\d{2})\\b'
        cnpj_pattern = r'\\b(\\d{2}\\.?\\d{3}\\.?\\d{3}/?\\d{4}-?\\d{2})\\b'
        
        cnpj_match = re.search(cnpj_pattern, text)
        if cnpj_match:
            return cnpj_match.group(1)
        
        cpf_match = re.search(cpf_pattern, text)
        if cpf_match:
            return cpf_match.group(1)
        
        return None
''')
print("✅ extractors/excel_extractor.py")

# ============================================================================
# ARQUIVO: extractors/word_extractor.py
# ============================================================================
with open('extractors/word_extractor.py', 'w', encoding='utf-8') as f:
    f.write('''from docx import Document
from typing import List, Dict, Any
from datetime import datetime
from io import BytesIO
import re

class WordExtractor:
    """Extrator para arquivos Word"""
    
    def __init__(self):
        self.patterns = {
            'date': r'\\b(\\d{2})[/-](\\d{2})[/-](\\d{4})\\b',
            'value': r'R?\\$?\\s*(\\d{1,3}(?:\\.\\d{3})*,\\d{2})',
            'cpf': r'\\b(\\d{3}\\.?\\d{3}\\.?\\d{3}-?\\d{2})\\b',
            'cnpj': r'\\b(\\d{2}\\.?\\d{3}\\.?\\d{3}/?\\d{4}-?\\d{2})\\b'
        }
    
    async def extract(self, file_content: bytes) -> Dict[str, Any]:
        """Extrai dados do Word"""
        try:
            doc = Document(BytesIO(file_content))
            transactions = []
            
            for table in doc.tables:
                table_data = [[cell.text for cell in row.cells] for row in table.rows]
                transactions.extend(self._parse_table(table_data))
            
            full_text = '\\n'.join([para.text for para in doc.paragraphs])
            transactions.extend(self._parse_text(full_text))
            
            return {
                'bank': 'WORD',
                'transactions': transactions,
                'total_found': len(transactions)
            }
        
        except Exception as e:
            raise Exception(f"Erro ao extrair Word: {str(e)}")
    
    def _parse_table(self, table: List[List[str]]) -> List[Dict[str, Any]]:
        transactions = []
        
        if not table or len(table) < 2:
            return transactions
        
        header = [str(cell).lower().strip() for cell in table[0]]
        
        date_idx = self._find_index(header, ['data', 'date', 'dt'])
        desc_idx = self._find_index(header, ['descrição', 'descricao', 'historico'])
        value_idx = self._find_index(header, ['valor', 'value'])
        
        for row in table[1:]:
            if len(row) < max(filter(None, [date_idx, desc_idx, value_idx]), default=0) + 1:
                continue
            
            try:
                date_str = row[date_idx] if date_idx is not None else None
                desc_str = row[desc_idx] if desc_idx is not None else ''
                value_str = row[value_idx] if value_idx is not None else None
                
                if not date_str or not value_str:
                    continue
                
                parsed_date = self._parse_date(date_str)
                parsed_value = self._parse_value(value_str)
                
                if parsed_date and parsed_value != 0:
                    transaction = {
                        'date': parsed_date,
                        'description': desc_str.strip(),
                        'value': parsed_value,
                        'cpf_cnpj': self._extract_cpf_cnpj(' '.join(row)),
                        'raw_data': ' | '.join(row)
                    }
                    transactions.append(transaction)
            
            except Exception:
                continue
        
        return transactions
    
    def _parse_text(self, text: str) -> List[Dict[str, Any]]:
        transactions = []
        lines = text.split('\\n')
        
        for line in lines:
            dates = re.findall(self.patterns['date'], line)
            values = re.findall(self.patterns['value'], line)
            
            if dates and values:
                date_str = f"{dates[0][0]}/{dates[0][1]}/{dates[0][2]}"
                value_str = values[0]
                
                parsed_date = self._parse_date(date_str)
                parsed_value = self._parse_value(value_str)
                
                if parsed_date and parsed_value != 0:
                    transaction = {
                        'date': parsed_date,
                        'description': line.strip(),
                        'value': parsed_value,
                        'cpf_cnpj': self._extract_cpf_cnpj(line),
                        'raw_data': line
                    }
                    transactions.append(transaction)
        
        return transactions
    
    def _parse_date(self, date_str: str) -> datetime:
        date_str = str(date_str).strip()
        
        formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _parse_value(self, value_str: str) -> float:
        value_str = str(value_str).strip()
        value_str = re.sub(r'[R$\\s]', '', value_str)
        value_str = value_str.replace('.', '').replace(',', '.')
        
        try:
            return float(value_str)
        except ValueError:
            return 0.0
    
    def _extract_cpf_cnpj(self, text: str) -> str:
        cnpj_match = re.search(self.patterns['cnpj'], text)
        if cnpj_match:
            return cnpj_match.group(1)
        
        cpf_match = re.search(self.patterns['cpf'], text)
        if cpf_match:
            return cpf_match.group(1)
        
        return None
    
    def _find_index(self, header: List[str], keywords: List[str]) -> int:
        for i, col in enumerate(header):
            if any(keyword in col for keyword in keywords):
                return i
        return None
''')
print("✅ extractors/word_extractor.py")

print("\n" + "=" * 60)
print("✅ PARTE 2 CONCLUÍDA!")
print("=" * 60)
print("\n📋 Agora execute a PARTE 3 para criar os services!")
print("=" * 60)
