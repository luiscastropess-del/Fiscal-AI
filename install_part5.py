#!/usr/bin/env python3
"""
🤖 FISCAL AI - INSTALADOR AUTOMÁTICO (PARTE 5/5 - FINAL)
Cria pdf_generator, main.py e frontend completo
"""

print("🚀 Instalação FINAL - PARTE 5/5...")
print("=" * 60)

# ============================================================================
# ARQUIVO: services/pdf_generator.py
# ============================================================================
with open('services/pdf_generator.py', 'w', encoding='utf-8') as f:
    f.write('''from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List

class PDFGenerator:
    """Gerador de relatórios PDF"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos customizados"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=10,
            spaceBefore=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
    
    def generate_report(self, file_data: Dict[str, Any], transactions: List[Dict[str, Any]], 
                       tax_calculation: Dict[str, Any]) -> BytesIO:
        """Gera relatório PDF completo"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm,
                               topMargin=20*mm, bottomMargin=20*mm)
        
        story = []
        
        # Cabeçalho
        story.extend(self._create_header(file_data))
        story.append(Spacer(1, 10*mm))
        
        # Resumo Financeiro
        story.extend(self._create_summary(file_data))
        story.append(Spacer(1, 8*mm))
        
        # Cálculo de Impostos
        story.extend(self._create_tax_section(tax_calculation))
        story.append(Spacer(1, 8*mm))
        
        # Transações
        story.extend(self._create_transactions_table(transactions))
        
        # Rodapé
        story.append(PageBreak())
        story.extend(self._create_footer())
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_header(self, file_data: Dict[str, Any]) -> List:
        """Cria cabeçalho do relatório"""
        elements = []
        
        title = Paragraph("🤖 FISCAL AI - RELATÓRIO DE ANÁLISE FISCAL", self.styles['CustomTitle'])
        elements.append(title)
        
        date_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        subtitle = Paragraph(f"Gerado em: {date_str}", self.styles['CustomBody'])
        elements.append(subtitle)
        
        elements.append(Spacer(1, 5*mm))
        
        # Informações do arquivo
        info_data = [
            ['Arquivo:', file_data.get('filename', 'N/A')],
            ['Banco Detectado:', file_data.get('bank_detected', 'N/A')],
            ['Data de Upload:', file_data.get('upload_date', 'N/A')],
            ['Total de Transações:', str(file_data.get('total_transactions', 0))]
        ]
        
        info_table = Table(info_data, colWidths=[50*mm, 120*mm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        elements.append(info_table)
        
        return elements
    
    def _create_summary(self, file_data: Dict[str, Any]) -> List:
        """Cria resumo financeiro"""
        elements = []
        
        heading = Paragraph("📊 RESUMO FINANCEIRO", self.styles['CustomHeading'])
        elements.append(heading)
        
        total_revenue = file_data.get('total_revenue', 0)
        total_expense = file_data.get('total_expense', 0)
        net_income = total_revenue - total_expense
        
        summary_data = [
            ['Descrição', 'Valor (R$)'],
            ['Total de Receitas', f'R$ {total_revenue:,.2f}'],
            ['Total de Despesas', f'R$ {total_expense:,.2f}'],
            ['Resultado Líquido', f'R$ {net_income:,.2f}']
        ]
        
        summary_table = Table(summary_data, colWidths=[100*mm, 70*mm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f3f4f6')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
        ]))
        
        elements.append(summary_table)
        
        return elements
    
    def _create_tax_section(self, tax_calculation: Dict[str, Any]) -> List:
        """Cria seção de impostos"""
        elements = []
        
        heading = Paragraph("🧮 CÁLCULO DE IMPOSTOS", self.styles['CustomHeading'])
        elements.append(heading)
        
        regime = tax_calculation.get('regime', 'N/A')
        regime_text = Paragraph(f"<b>Regime Tributário:</b> {regime}", self.styles['CustomBody'])
        elements.append(regime_text)
        elements.append(Spacer(1, 3*mm))
        
        tax_calc = tax_calculation.get('tax_calculation', {})
        
        if tax_calc.get('error'):
            error_text = Paragraph(f"<b>⚠️ {tax_calc['error']}</b>", self.styles['CustomBody'])
            elements.append(error_text)
            if tax_calc.get('recommendation'):
                rec_text = Paragraph(f"<i>{tax_calc['recommendation']}</i>", self.styles['CustomBody'])
                elements.append(rec_text)
        else:
            # Tabela de impostos
            tax_data = [['Descrição', 'Valor (R$)']]
            
            if 'taxes' in tax_calc:
                taxes = tax_calc['taxes']
                tax_data.append(['IRPJ', f"R$ {taxes.get('irpj', 0):,.2f}"])
                tax_data.append(['CSLL', f"R$ {taxes.get('csll', 0):,.2f}"])
                tax_data.append(['PIS', f"R$ {taxes.get('pis', 0):,.2f}"])
                tax_data.append(['COFINS', f"R$ {taxes.get('cofins', 0):,.2f}"])
            
            total_tax = tax_calc.get('total_tax', 0)
            tax_data.append(['TOTAL', f"R$ {total_tax:,.2f}"])
            
            tax_table = Table(tax_data, colWidths=[100*mm, 70*mm])
            tax_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fef3c7')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
            ]))
            
            elements.append(tax_table)
            
            if tax_calc.get('effective_rate'):
                rate_text = Paragraph(
                    f"<b>Alíquota Efetiva:</b> {tax_calc['effective_rate']:.2f}%",
                    self.styles['CustomBody']
                )
                elements.append(Spacer(1, 3*mm))
                elements.append(rate_text)
        
        return elements
    
    def _create_transactions_table(self, transactions: List[Dict[str, Any]]) -> List:
        """Cria tabela de transações"""
        elements = []
        
        heading = Paragraph("📋 DETALHAMENTO DE TRANSAÇÕES", self.styles['CustomHeading'])
        elements.append(heading)
        
        # Limita a 50 transações no PDF
        limited_transactions = transactions[:50]
        
        trans_data = [['Data', 'Descrição', 'Valor', 'Tipo', 'Categoria']]
        
        for trans in limited_transactions:
            date_str = trans.get('date', 'N/A')
            if isinstance(date_str, str) and 'T' in date_str:
                date_str = date_str.split('T')[0]
            
            desc = trans.get('description', '')[:40]
            value = trans.get('value', 0)
            trans_type = trans.get('transaction_type', 'N/A')
            category = trans.get('category_name', 'N/A')[:20]
            
            trans_data.append([
                date_str,
                desc,
                f"R$ {value:,.2f}",
                trans_type,
                category
            ])
        
        if len(transactions) > 50:
            trans_data.append(['...', f'(+{len(transactions) - 50} transações)', '', '', ''])
        
        trans_table = Table(trans_data, colWidths=[25*mm, 60*mm, 30*mm, 25*mm, 30*mm])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        
        elements.append(trans_table)
        
        return elements
    
    def _create_footer(self) -> List:
        """Cria rodapé do relatório"""
        elements = []
        
        elements.append(Spacer(1, 10*mm))
        
        disclaimer = Paragraph(
            "<b>⚠️ AVISO LEGAL:</b> Este relatório é uma ferramenta auxiliar gerada automaticamente. "
            "Os cálculos apresentados são estimativas baseadas nas informações fornecidas. "
            "<b>Sempre consulte um contador habilitado</b> para validação final e cumprimento "
            "de todas as obrigações fiscais e tributárias.",
            self.styles['CustomBody']
        )
        elements.append(disclaimer)
        
        elements.append(Spacer(1, 5*mm))
        
        footer = Paragraph(
            "Desenvolvido com ❤️ por <b>Fiscal AI</b> - Sistema de Análise de Extratos Bancários",
            self.styles['CustomBody']
        )
        elements.append(footer)
        
        return elements
''')
print("✅ services/pdf_generator.py")

# ============================================================================
# ARQUIVO: _main.py (será renomeado para main.py depois)
# ============================================================================
with open('_main.py', 'w', encoding='utf-8') as f:
    f.write('''from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import asyncio
from datetime import datetime

from database import Database
from extractors.pdf_extractor import PDFExtractor
from extractors.excel_extractor import ExcelExtractor
from extractors.word_extractor import WordExtractor
from services.bank_parser import BankParser
from services.categorizer import TransactionCategorizer
from services.tax_calculator import TaxCalculator
from services.pdf_generator import PDFGenerator

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'fiscal-ai-secret-key-2024'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = Database()
pdf_extractor = PDFExtractor()
excel_extractor = ExcelExtractor()
word_extractor = WordExtractor()
bank_parser = BankParser()
categorizer = TransactionCategorizer()
tax_calculator = TaxCalculator()
pdf_generator = PDFGenerator()

ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls', 'docx', 'doc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Arquivo vazio'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
        filename = secure_filename(file.filename)
        file_content = file.read()
        file_type = filename.rsplit('.', 1)[1].lower()
        
        if file_type == 'pdf':
            result = asyncio.run(pdf_extractor.extract(file_content))
        elif file_type in ['xlsx', 'xls']:
            result = asyncio.run(excel_extractor.extract(file_content))
        elif file_type in ['docx', 'doc']:
            result = asyncio.run(word_extractor.extract(file_content))
        else:
            return jsonify({'error': 'Formato não suportado'}), 400
        
        bank = result.get('bank', 'GENERICO')
        transactions = result.get('transactions', [])
        
        file_id = db.create_file(filename, file_type, bank)
        
        total_revenue = 0
        total_expense = 0
        
        for trans in transactions:
            trans = bank_parser.parse(trans, bank)
            trans = categorizer.categorize(trans)
            
            trans['file_id'] = file_id
            
            db.create_transaction(file_id, trans)
            
            if trans.get('transaction_type') == 'CREDITO':
                total_revenue += trans.get('value', 0)
            else:
                total_expense += trans.get('value', 0)
        
        db.update_file_status(file_id, 'COMPLETED', len(transactions), total_revenue, total_expense)
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'bank_detected': bank,
            'total_transactions': len(transactions),
            'total_revenue': total_revenue,
            'total_expense': total_expense
        })
    
    except Exception as e:
        print(f"Erro no upload: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<int:file_id>', methods=['GET'])
def get_file(file_id):
    try:
        file_data = db.get_file(file_id)
        
        if not file_data:
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        return jsonify(file_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<int:file_id>/transactions', methods=['GET'])
def get_transactions(file_id):
    try:
        transactions = db.get_transactions(file_id)
        
        return jsonify({
            'file_id': file_id,
            'transactions': transactions,
            'total': len(transactions)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<int:file_id>/calculate-taxes', methods=['POST'])
def calculate_taxes(file_id):
    try:
        data = request.get_json()
        regime = data.get('regime', 'SIMPLES')
        
        transactions = db.get_transactions(file_id)
        
        result = tax_calculator.calculate_taxes(transactions, regime)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<int:file_id>/export-pdf', methods=['POST'])
def export_pdf(file_id):
    try:
        data = request.get_json()
        regime = data.get('regime', 'SIMPLES')
        
        file_data = db.get_file(file_id)
        transactions = db.get_transactions(file_id)
        tax_result = tax_calculator.calculate_taxes(transactions, regime)
        
        pdf_buffer = pdf_generator.generate_report(file_data, transactions, tax_result)
        
        filename = f"relatorio_fiscal_{file_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    try:
        db.cleanup_old_files(days=7)
        return jsonify({'success': True, 'message': 'Limpeza realizada'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Fiscal AI iniciando...")
    print("📊 Banco de dados inicializado")
    print("🌐 Servidor rodando em http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
''')
print("✅ _main.py")

print("\n" + "=" * 60)
print("✅ BACKEND CONCLUÍDO!")
print("=" * 60)
print("\n📋 Agora vamos criar o FRONTEND (HTML, CSS, JS)...")
print("=" * 60)
