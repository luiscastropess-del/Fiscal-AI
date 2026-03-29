#!/usr/bin/env python3
"""
🤖 FISCAL AI - INSTALADOR AUTOMÁTICO (PARTE 4/5)
Cria tax_calculator e pdf_generator
"""

print("🚀 Continuando instalação - PARTE 4/5...")
print("=" * 60)

# ============================================================================
# ARQUIVO: services/tax_calculator.py
# ============================================================================
with open('services/tax_calculator.py', 'w', encoding='utf-8') as f:
    f.write('''from typing import Dict, Any, List
from datetime import datetime

class TaxCalculator:
    """Calculadora de impostos por regime tributário"""
    
    def __init__(self):
        self.regimes = {
            'SIMPLES': self._calculate_simples,
            'LUCRO_PRESUMIDO': self._calculate_lucro_presumido,
            'LUCRO_REAL': self._calculate_lucro_real,
            'MEI': self._calculate_mei,
            'IRPF': self._calculate_irpf
        }
    
    def calculate_taxes(self, transactions: List[Dict[str, Any]], regime: str = 'SIMPLES') -> Dict[str, Any]:
        """Calcula impostos baseado no regime"""
        
        summary = self._calculate_summary(transactions)
        
        calculator = self.regimes.get(regime, self._calculate_simples)
        tax_calculation = calculator(summary)
        
        breakdown = self._calculate_breakdown(transactions)
        
        return {
            'summary': summary,
            'tax_calculation': tax_calculation,
            'breakdown': breakdown,
            'regime': regime
        }
    
    def _calculate_summary(self, transactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcula resumo financeiro"""
        total_revenue = 0
        total_expense = 0
        
        for trans in transactions:
            if trans.get('transaction_type') == 'CREDITO':
                total_revenue += trans.get('value', 0)
            else:
                total_expense += trans.get('value', 0)
        
        net_income = total_revenue - total_expense
        
        return {
            'total_revenue': round(total_revenue, 2),
            'total_expense': round(total_expense, 2),
            'net_income': round(net_income, 2)
        }
    
    def _calculate_breakdown(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula breakdown por categoria"""
        revenues_by_category = {}
        expenses_by_category = {}
        
        for trans in transactions:
            category = trans.get('category_name', 'NÃO CATEGORIZADO')
            value = trans.get('value', 0)
            trans_type = trans.get('transaction_type')
            
            if trans_type == 'CREDITO':
                revenues_by_category[category] = revenues_by_category.get(category, 0) + value
            else:
                expenses_by_category[category] = expenses_by_category.get(category, 0) + value
        
        return {
            'revenues_by_category': {k: round(v, 2) for k, v in revenues_by_category.items()},
            'expenses_by_category': {k: round(v, 2) for k, v in expenses_by_category.items()}
        }
    
    def _calculate_simples(self, summary: Dict[str, float]) -> Dict[str, Any]:
        """Simples Nacional"""
        revenue = summary['total_revenue']
        
        # Anexo III (Serviços) - Faixas do Simples Nacional
        if revenue <= 180000:  # Até R$ 180.000/ano
            rate = 0.06  # 6%
            deduction = 0
        elif revenue <= 360000:  # Até R$ 360.000/ano
            rate = 0.112  # 11.2%
            deduction = 9360
        elif revenue <= 720000:  # Até R$ 720.000/ano
            rate = 0.135  # 13.5%
            deduction = 17640
        elif revenue <= 1800000:  # Até R$ 1.800.000/ano
            rate = 0.16  # 16%
            deduction = 35640
        elif revenue <= 3600000:  # Até R$ 3.600.000/ano
            rate = 0.21  # 21%
            deduction = 125640
        elif revenue <= 4800000:  # Até R$ 4.800.000/ano
            rate = 0.33  # 33%
            deduction = 648000
        else:
            return {
                'error': 'Receita acima do limite do Simples Nacional (R$ 4.800.000/ano)',
                'recommendation': 'Considere migrar para Lucro Presumido ou Lucro Real',
                'total_tax': 0
            }
        
        # Cálculo com alíquota efetiva
        effective_rate = ((revenue * rate) - deduction) / revenue if revenue > 0 else 0
        total_tax = (revenue * rate) - deduction
        
        monthly_average = total_tax / 12
        
        guidance = f"""
**Regime: Simples Nacional - Anexo III (Serviços)**

**Cálculo:**
- Receita Bruta Anual: R$ {revenue:,.2f}
- Alíquota Nominal: {rate * 100:.1f}%
- Dedução: R$ {deduction:,.2f}
- **Alíquota Efetiva: {effective_rate * 100:.2f}%**

**Imposto Total Anual: R$ {total_tax:,.2f}**
**Média Mensal: R$ {monthly_average:,.2f}**

**Como Pagar:**
1. Acesse o Portal do Simples Nacional
2. Gere DAS (Documento de Arrecadação do Simples)
3. Vencimento: até dia 20 do mês seguinte
4. Pagamento único inclui todos os tributos:
   - IRPJ, CSLL, PIS, COFINS, CPP, ICMS, ISS

**⚠️ Importante:**
- Faturamento deve ser proporcional aos meses de atividade
- Anexo pode mudar conforme fator "r" (folha/receita)
- Consulte contador para cálculo preciso do fator "r"
"""
        
        return {
            'regime': 'SIMPLES',
            'total_tax': round(total_tax, 2),
            'effective_rate': round(effective_rate * 100, 2),
            'monthly_average': round(monthly_average, 2),
            'guidance': guidance
        }
    
    def _calculate_lucro_presumido(self, summary: Dict[str, float]) -> Dict[str, Any]:
        """Lucro Presumido"""
        revenue = summary['total_revenue']
        
        # Presunção de lucro: 32% para serviços, 8% para comércio
        presumed_profit = revenue * 0.32  # Usando 32% (serviços)
        
        # IRPJ: 15% sobre lucro presumido
        irpj = presumed_profit * 0.15
        
        # Adicional IRPJ: 10% sobre lucro > R$ 20.000/mês
        monthly_profit = presumed_profit / 12
        additional_irpj = 0
        if monthly_profit > 20000:
            additional_irpj = (monthly_profit - 20000) * 0.10 * 12
        
        # CSLL: 9% sobre lucro presumido
        csll = presumed_profit * 0.09
        
        # PIS: 0,65% sobre receita bruta
        pis = revenue * 0.0065
        
        # COFINS: 3% sobre receita bruta
        cofins = revenue * 0.03
        
        total_tax = irpj + additional_irpj + csll + pis + cofins
        effective_rate = (total_tax / revenue * 100) if revenue > 0 else 0
        
        guidance = f"""
**Regime: Lucro Presumido**

**Base de Cálculo:**
- Receita Bruta: R$ {revenue:,.2f}
- Lucro Presumido (32%): R$ {presumed_profit:,.2f}

**Tributos Calculados:**

1. **IRPJ (15%):** R$ {irpj:,.2f}
2. **Adicional IRPJ (10%):** R$ {additional_irpj:,.2f}
3. **CSLL (9%):** R$ {csll:,.2f}
4. **PIS (0,65%):** R$ {pis:,.2f}
5. **COFINS (3%):** R$ {cofins:,.2f}

**Total de Impostos: R$ {total_tax:,.2f}**
**Alíquota Efetiva: {effective_rate:.2f}%**

**Como Pagar:**
- **IRPJ e CSLL:** Trimestral (DARF)
  * Códigos: 2089 (IRPJ) e 2372 (CSLL)
  * Vencimento: último dia útil do mês seguinte ao trimestre
  
- **PIS e COFINS:** Mensal (DARF)
  * Códigos: 8109 (PIS) e 2172 (COFINS)
  * Vencimento: até dia 25 do mês seguinte

**⚠️ Observações:**
- Presunção de 32% é para prestação de serviços
- Comércio usa 8% de presunção
- Indústria usa 8% de presunção
- Consulte contador para atividade específica
"""
        
        return {
            'regime': 'LUCRO_PRESUMIDO',
            'taxes': {
                'irpj': round(irpj + additional_irpj, 2),
                'csll': round(csll, 2),
                'pis': round(pis, 2),
                'cofins': round(cofins, 2)
            },
            'total_tax': round(total_tax, 2),
            'effective_rate': round(effective_rate, 2),
            'guidance': guidance
        }
    
    def _calculate_lucro_real(self, summary: Dict[str, float]) -> Dict[str, Any]:
        """Lucro Real"""
        revenue = summary['total_revenue']
        expense = summary['total_expense']
        net_income = summary['net_income']
        
        if net_income <= 0:
            return {
                'regime': 'LUCRO_REAL',
                'error': 'Prejuízo fiscal - Não há imposto a pagar',
                'guidance': 'Prejuízo pode ser compensado em períodos futuros (até 30% do lucro)',
                'total_tax': 0
            }
        
        # IRPJ: 15% sobre lucro real
        irpj = net_income * 0.15
        
        # Adicional IRPJ: 10% sobre lucro > R$ 20.000/mês
        monthly_income = net_income / 12
        additional_irpj = 0
        if monthly_income > 20000:
            additional_irpj = (monthly_income - 20000) * 0.10 * 12
        
        # CSLL: 9% sobre lucro real
        csll = net_income * 0.09
        
        # PIS: 1,65% sobre receita bruta
        pis = revenue * 0.0165
        
        # COFINS: 7,6% sobre receita bruta
        cofins = revenue * 0.076
        
        total_tax = irpj + additional_irpj + csll + pis + cofins
        effective_rate = (total_tax / revenue * 100) if revenue > 0 else 0
        
        guidance = f"""
**Regime: Lucro Real**

**Demonstrativo:**
- Receita Bruta: R$ {revenue:,.2f}
- (-) Despesas Dedutíveis: R$ {expense:,.2f}
- (=) **Lucro Real: R$ {net_income:,.2f}**

**Tributos Calculados:**

1. **IRPJ (15%):** R$ {irpj:,.2f}
2. **Adicional IRPJ (10%):** R$ {additional_irpj:,.2f}
3. **CSLL (9%):** R$ {csll:,.2f}
4. **PIS (1,65%):** R$ {pis:,.2f}
5. **COFINS (7,6%):** R$ {cofins:,.2f}

**Total de Impostos: R$ {total_tax:,.2f}**
**Alíquota Efetiva: {effective_rate:.2f}%**

**Como Pagar:**
- **IRPJ e CSLL:** Trimestral ou Anual (DARF)
  * Apuração trimestral: 31/03, 30/06, 30/09, 31/12
  * Códigos: 2089 (IRPJ) e 2372 (CSLL)
  
- **PIS e COFINS:** Mensal (DARF)
  * Códigos: 6912 (PIS) e 5856 (COFINS)
  * Vencimento: até dia 25 do mês seguinte

**⚠️ Importante:**
- Exige contabilidade completa
- Permite dedução de todas as despesas operacionais
- Créditos de PIS/COFINS sobre insumos
- Obrigatório para receita > R$ 78 milhões/ano
- Consulte contador para apuração correta
"""
        
        return {
            'regime': 'LUCRO_REAL',
            'taxes': {
                'irpj': round(irpj + additional_irpj, 2),
                'csll': round(csll, 2),
                'pis': round(pis, 2),
                'cofins': round(cofins, 2)
            },
            'total_tax': round(total_tax, 2),
            'effective_rate': round(effective_rate, 2),
            'guidance': guidance
        }
    
    def _calculate_mei(self, summary: Dict[str, float]) -> Dict[str, Any]:
        """MEI - Microempreendedor Individual"""
        revenue = summary['total_revenue']
        
        # Limite MEI: R$ 81.000/ano
        if revenue > 81000:
            return {
                'regime': 'MEI',
                'error': f'Receita (R$ {revenue:,.2f}) acima do limite MEI (R$ 81.000/ano)',
                'recommendation': 'Migre para Simples Nacional - Microempresa',
                'total_tax': 0
            }
        
        # Valores fixos mensais MEI (2024)
        inss = 67.00  # 5% do salário mínimo
        icms = 1.00   # Se comércio/indústria
        iss = 5.00    # Se serviços
        
        monthly_tax = inss + iss  # Considerando prestação de serviços
        annual_tax = monthly_tax * 12
        
        guidance = f"""
**Regime: MEI - Microempreendedor Individual**

**Limites:**
- Receita Máxima Anual: R$ 81.000,00
- Sua Receita: R$ {revenue:,.2f}
- Status: {'✅ Dentro do limite' if revenue <= 81000 else '❌ ACIMA DO LIMITE'}

**Valor Mensal Fixo (DAS-MEI):**
- INSS (5% salário mínimo): R$ 67,00
- ISS (Serviços): R$ 5,00
- **Total Mensal: R$ {monthly_tax:.2f}**

**Total Anual: R$ {annual_tax:.2f}**

**Como Pagar:**
1. Acesse: www.gov.br/empresas-e-negocios
2. Entre em "Portal do Empreendedor"
3. Gere DAS-MEI
4. Vencimento: dia 20 de cada mês
5. Pagamento via:
   - Internet Banking
   - Aplicativo do banco
   - Casas lotéricas
   - Correspondentes bancários

**Obrigações:**
- ✅ Pagar DAS-MEI mensalmente
- ✅ Declaração Anual (DASN-SIMEI) até 31/05
- ✅ Emitir nota fiscal (quando cliente for PJ)
- ✅ Manter controle de receitas

**Benefícios:**
- ✅ Aposentadoria por idade
- ✅ Auxílio-doença
- ✅ Salário-maternidade
- ✅ Pensão por morte
- ✅ CNPJ sem custo

**⚠️ Atenção:**
- Não pode ter sócio
- Não pode ter filial
- Não pode participar de outra empresa
- Máximo 1 funcionário
"""
        
        return {
            'regime': 'MEI',
            'monthly_tax': round(monthly_tax, 2),
            'annual_tax': round(annual_tax, 2),
            'total_tax': round(annual_tax, 2),
            'guidance': guidance
        }
    
    def _calculate_irpf(self, summary: Dict[str, float]) -> Dict[str, Any]:
        """IRPF - Imposto de Renda Pessoa Física"""
        revenue = summary['total_revenue']
        expense = summary['total_expense']
        
        # Rendimento tributável (receita - despesas dedutíveis)
        taxable_income = revenue - expense
        
        # Tabela progressiva IRPF 2024 (mensal)
        monthly_income = taxable_income / 12
        
        if monthly_income <= 2112.00:
            rate = 0
            deduction = 0
            bracket = "Isento"
        elif monthly_income <= 2826.65:
            rate = 0.075
            deduction = 158.40
            bracket = "7,5%"
        elif monthly_income <= 3751.05:
            rate = 0.15
            deduction = 370.40
            bracket = "15%"
        elif monthly_income <= 4664.68:
            rate = 0.225
            deduction = 651.73
            bracket = "22,5%"
        else:
            rate = 0.275
            deduction = 884.96
            bracket = "27,5%"
        
        monthly_tax = (monthly_income * rate) - deduction
        annual_tax = monthly_tax * 12
        
        # Carnê-Leão (mensal)
        carne_leao = monthly_tax
        
        guidance = f"""
**Regime: IRPF - Pessoa Física**

**Rendimentos:**
- Receita Anual: R$ {revenue:,.2f}
- Despesas Dedutíveis: R$ {expense:,.2f}
- **Rendimento Tributável: R$ {taxable_income:,.2f}**
- Rendimento Mensal Médio: R$ {monthly_income:,.2f}

**Faixa: {bracket}**

**Imposto Calculado:**
- Mensal (Carnê-Leão): R$ {carne_leao:,.2f}
- **Anual: R$ {annual_tax:,.2f}**

**Como Pagar:**

**1. Carnê-Leão (Mensal):**
- Acesse: www.gov.br/receitafederal
- Programa Carnê-Leão
- Vencimento: último dia útil do mês seguinte
- DARF código: 0190

**2. Declaração Anual (DIRPF):**
- Prazo: até 31/05 de cada ano
- Programa IRPF disponível em março
- Informe todos os rendimentos e despesas

**Despesas Dedutíveis:**
- ✅ Educação (limite legal)
- ✅ Saúde (sem limite)
- ✅ Previdência privada (até 12% renda)
- ✅ Dependentes (R$ 2.275,08/ano cada)
- ✅ Pensão alimentícia
- ✅ Livro Caixa (despesas profissionais)

**⚠️ Importante:**
- Guarde todos os comprovantes por 5 anos
- Rendimentos sem CNPJ: informar como "DIVERSOS"
- Consulte contador para otimizar deduções
- Atraso gera multa de 0,33% ao dia (máx. 20%)

**Livro Caixa:**
- Profissionais autônomos podem deduzir despesas
- Aluguel, água, luz, telefone (proporcionais)
- Material de trabalho
- Cursos e capacitação
"""
        
        return {
            'regime': 'IRPF',
            'monthly_tax': round(carne_leao, 2),
            'annual_tax': round(annual_tax, 2),
            'total_tax': round(annual_tax, 2),
            'bracket': bracket,
            'guidance': guidance
        }
''')
print("✅ services/tax_calculator.py")

print("\n" + "=" * 60)
print("✅ PARTE 4 CONCLUÍDA!")
print("=" * 60)
print("\n📋 Agora execute a PARTE 5 para criar pdf_generator e frontend!")
print("=" * 60)
