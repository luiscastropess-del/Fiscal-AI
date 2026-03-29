#!/usr/bin/env python3
"""
🤖 FISCAL AI - INSTALADOR AUTOMÁTICO (PARTE 3/4)
Cria services (bank_parser, categorizer, tax_calculator, pdf_generator)
"""

print("🚀 Continuando instalação - PARTE 3/4...")
print("=" * 60)

# ============================================================================
# ARQUIVO: services/bank_parser.py
# ============================================================================
with open('services/bank_parser.py', 'w', encoding='utf-8') as f:
    f.write('''from typing import Dict, Any
import re

class BankParser:
    """Parser específico para cada banco"""
    
    def __init__(self):
        self.parsers = {
            'SANTANDER': self._parse_santander,
            'NUBANK': self._parse_nubank,
            'INTER': self._parse_inter,
            'MERCADOPAGO': self._parse_mercadopago,
            'GENERICO': self._parse_generic
        }
    
    def parse(self, transaction: Dict[str, Any], bank: str) -> Dict[str, Any]:
        """Parse transação específica do banco"""
        parser = self.parsers.get(bank, self._parse_generic)
        return parser(transaction)
    
    def _parse_santander(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Parse específico Santander"""
        description = transaction.get('description', '').upper()
        value = transaction.get('value', 0)
        
        if any(keyword in description for keyword in ['PIX RECEBIDO', 'TED RECEBIDA', 'DOC RECEBIDO', 'CREDITO']):
            transaction['transaction_type'] = 'CREDITO'
            transaction['value'] = abs(value)
        elif any(keyword in description for keyword in ['PIX ENVIADO', 'TED ENVIADA', 'DOC ENVIADO', 'DEBITO', 'PAGAMENTO']):
            transaction['transaction_type'] = 'DEBITO'
            transaction['value'] = abs(value)
        else:
            transaction['transaction_type'] = 'DEBITO' if value < 0 else 'CREDITO'
            transaction['value'] = abs(value)
        
        if 'PIX' in description:
            cpf_cnpj = self._extract_pix_key(description)
            if cpf_cnpj:
                transaction['cpf_cnpj'] = cpf_cnpj
        
        return transaction
    
    def _parse_nubank(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Parse específico Nubank"""
        description = transaction.get('description', '').upper()
        value = transaction.get('value', 0)
        
        if value > 0:
            transaction['transaction_type'] = 'CREDITO'
        else:
            transaction['transaction_type'] = 'DEBITO'
            transaction['value'] = abs(value)
        
        if 'PAGAMENTO' in description:
            transaction['hint_category'] = 'DESPESA_FORNECEDORES'
        elif 'TRANSFERENCIA RECEBIDA' in description:
            transaction['hint_category'] = 'RECEITA_VENDA_MERCADORIAS'
        
        return transaction
    
    def _parse_inter(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Parse específico Inter"""
        description = transaction.get('description', '').upper()
        value = transaction.get('value', 0)
        
        if '+' in description or value > 0:
            transaction['transaction_type'] = 'CREDITO'
            transaction['value'] = abs(value)
        else:
            transaction['transaction_type'] = 'DEBITO'
            transaction['value'] = abs(value)
        
        description = re.sub(r'^(COMPRA|PGTO|TRANSF|TED|PIX)\\s*-?\\s*', '', description)
        transaction['description'] = description.strip()
        
        return transaction
    
    def _parse_mercadopago(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Parse específico Mercado Pago"""
        description = transaction.get('description', '').upper()
        value = transaction.get('value', 0)
        
        if any(keyword in description for keyword in ['RECEBIDO', 'VENDA', 'PAGAMENTO APROVADO']):
            transaction['transaction_type'] = 'CREDITO'
            transaction['value'] = abs(value)
        elif any(keyword in description for keyword in ['ENVIADO', 'COMPRA', 'PAGAMENTO', 'SAQUE']):
            transaction['transaction_type'] = 'DEBITO'
            transaction['value'] = abs(value)
        else:
            transaction['transaction_type'] = 'DEBITO' if value < 0 else 'CREDITO'
            transaction['value'] = abs(value)
        
        if 'TAXA' in description:
            transaction['hint_category'] = 'DESPESA_FINANCEIRA'
        
        return transaction
    
    def _parse_generic(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Parse genérico"""
        value = transaction.get('value', 0)
        
        if value > 0:
            transaction['transaction_type'] = 'CREDITO'
        else:
            transaction['transaction_type'] = 'DEBITO'
            transaction['value'] = abs(value)
        
        return transaction
    
    def _extract_pix_key(self, text: str) -> str:
        """Extrai chave PIX (CPF/CNPJ) do texto"""
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
print("✅ services/bank_parser.py")

# ============================================================================
# ARQUIVO: services/categorizer.py
# ============================================================================
with open('services/categorizer.py', 'w', encoding='utf-8') as f:
    f.write('''import json
from typing import Dict, Any, List
from database import Database

class TransactionCategorizer:
    """Categoriza transações conforme Receita Federal"""
    
    def __init__(self):
        self.db = Database()
        self.categories = self._load_categories()
    
    def _load_categories(self) -> List[Dict[str, Any]]:
        """Carrega categorias do banco"""
        categories = self.db.get_categories()
        
        for cat in categories:
            if cat.get('keywords'):
                try:
                    cat['keywords'] = json.loads(cat['keywords'])
                except:
                    cat['keywords'] = []
        
        return categories
    
    def categorize(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Categoriza uma transação"""
        description = transaction.get('description', '').lower()
        transaction_type = transaction.get('transaction_type', 'DEBITO')
        hint_category = transaction.get('hint_category')
        
        if hint_category:
            category = self._get_category_by_name(hint_category)
            if category:
                return self._apply_category(transaction, category, confidence=0.9)
        
        best_match = None
        best_score = 0
        
        for category in self.categories:
            cat_type = 'CREDITO' if category['code'].startswith('3.') else 'DEBITO'
            if cat_type != transaction_type:
                continue
            
            score = 0
            keywords = category.get('keywords', [])
            
            for keyword in keywords:
                if keyword in description:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = category
        
        if best_match and best_score > 0:
            confidence = min(best_score / len(best_match.get('keywords', [1])), 1.0)
            return self._apply_category(transaction, best_match, confidence)
        
        default_category = self._get_default_category(transaction_type)
        return self._apply_category(transaction, default_category, confidence=0.0)
    
    def _apply_category(self, transaction: Dict[str, Any], category: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        """Aplica categoria à transação"""
        transaction['category_code'] = category['code']
        transaction['category_name'] = category['name']
        transaction['tax_rate'] = category.get('tax_rate', 0.0)
        transaction['confidence'] = confidence
        
        guidance = category.get('guidance', '')
        
        if not transaction.get('cpf_cnpj'):
            guidance += self._get_no_cpf_guidance(transaction)
        
        transaction['guidance'] = guidance
        
        return transaction
    
    def _get_no_cpf_guidance(self, transaction: Dict[str, Any]) -> str:
        """Orientação para transações sem CPF/CNPJ"""
        transaction_type = transaction.get('transaction_type')
        
        if transaction_type == 'CREDITO':
            return """

**⚠️ ATENÇÃO: Transação sem CPF/CNPJ identificado**

**Como lançar receitas sem identificação da fonte:**

1. **No e-CAC / DIRPF:**
   - Acesse "Rendimentos Tributáveis"
   - Use CNPJ fictício: **99.999.999/9999-99**
   - Nome da fonte: **"DIVERSOS"**
   - Informe o valor total recebido

2. **Na aba "Discriminação":**
   - Descreva detalhadamente a origem:
     * "Vendas diversas conforme extratos bancários"
     * "Prestação de serviços período XX/XX a XX/XX"
     * Anexe extratos como comprovação

3. **Documentação a manter:**
   - ✅ Extratos bancários completos
   - ✅ Notas fiscais emitidas (se houver)
   - ✅ Recibos de pagamento
   - ✅ Contratos ou acordos (se houver)

4. **Importante:**
   - A falta de identificação não isenta a declaração
   - Mantenha documentação por 5 anos
   - Em caso de fiscalização, apresente os comprovantes

**💡 Recomendação:** Sempre que possível, identifique a fonte pagadora para evitar questionamentos.
"""
        else:
            return """

**⚠️ ATENÇÃO: Despesa sem CPF/CNPJ identificado**

**Como lançar despesas sem identificação:**

1. **Livro Caixa / DIPJ:**
   - Categoria: "Outras Despesas Operacionais"
   - Descrição: detalhe a natureza da despesa
   - Valor: conforme comprovante

2. **Documentação OBRIGATÓRIA:**
   - ✅ Recibo com:
     * Nome completo do prestador/vendedor
     * CPF ou RG
     * Descrição do serviço/produto
     * Data e valor
     * Assinatura
   - ✅ Nota fiscal (quando aplicável)
   - ✅ Comprovante de pagamento

3. **Dedutibilidade:**
   - ⚠️ Despesas sem comprovação adequada podem ser **glosadas**
   - Dedutível apenas se relacionada à atividade empresarial
   - Proporção entre uso pessoal/empresarial deve ser demonstrada

4. **Casos Específicos:**
   
   **Compras de Pessoa Física (sem CNPJ):**
   - Exija recibo com RG do vendedor
   - Mantenha cópia do documento
   
   **Serviços informais:**
   - RPA (Recibo de Pagamento Autônomo)
   - Retenção de INSS se aplicável
   
   **Pequenas despesas (< R$ 100):**
   - Agrupe mensalmente
   - Discrimine "Despesas miúdas diversas"
   - Mantenha comprovantes individuais

**⚠️ IMPORTANTE:** A Receita pode questionar despesas sem identificação adequada. Regularize sempre que possível.
"""
    
    def _get_category_by_name(self, name: str) -> Dict[str, Any]:
        """Busca categoria por nome"""
        for cat in self.categories:
            if cat['name'] == name:
                return cat
        return None
    
    def _get_default_category(self, transaction_type: str) -> Dict[str, Any]:
        """Retorna categoria padrão"""
        if transaction_type == 'CREDITO':
            return {
                'code': '3.99.99',
                'name': 'OUTRAS_RECEITAS',
                'description': 'Outras receitas não classificadas',
                'tax_rate': 0.0,
                'guidance': 'Receita não categorizada automaticamente. Revise e classifique manualmente.'
            }
        else:
            return {
                'code': '4.99.99',
                'name': 'OUTRAS_DESPESAS',
                'description': 'Outras despesas não classificadas',
                'tax_rate': 0.0,
                'guidance': 'Despesa não categorizada automaticamente. Revise e classifique manualmente.'
            }
''')
print("✅ services/categorizer.py")

print("\n" + "=" * 60)
print("✅ PARTE 3 CONCLUÍDA!")
print("=" * 60)
print("\n📋 Agora execute a PARTE 4 para criar tax_calculator e pdf_generator!")
print("=" * 60)
