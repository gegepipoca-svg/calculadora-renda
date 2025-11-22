"""
CALCULADORA DE RENDA PRO - Streamlit
Análise automática de extratos bancários com IA

Criado para: Magalhães Negócios
Versão: 3.0 Professional
"""

import streamlit as st
import anthropic
import base64
from datetime import datetime
import pandas as pd
from io import BytesIO
import json

# Configuração da página
st.set_page_config(
    page_title="Calculadora de Renda PRO",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para interface profissional
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: none;
        font-size: 1.1rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #D1FAE5;
        border-left: 4px solid #10B981;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    h1 {
        color: #667eea;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar estado da sessão
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'results' not in st.session_state:
    st.session_state.results = None

# Sidebar para configurações
with st.sidebar:
    st.markdown("## ⚙️ Configurações")
    
    # Campo para API Key
    st.markdown("### 🔑 Chave API Anthropic")
    
    # Obter chave dos secrets ou input do usuário
    if 'ANTHROPIC_API_KEY' in st.secrets:
        api_key = st.secrets['ANTHROPIC_API_KEY']
        st.success("✅ Chave API configurada!")
        st.info("🔒 Chave gerenciada pelo administrador")
    else:
        api_key = st.text_input(
            "Cole sua chave API aqui:",
            type="password",
            help="Obtenha em: https://console.anthropic.com"
        )
        
        if not api_key:
            st.warning("⚠️ Adicione sua chave API para começar!")
            st.markdown("""
            **Como obter:**
            1. [console.anthropic.com](https://console.anthropic.com)
            2. Crie uma conta
            3. Vá em "API Keys"
            4. Crie uma nova chave
            5. Cole aqui
            """)
    
    st.markdown("---")
    
    # Informações
    st.markdown("### 📊 Informações")
    st.info("""
    **Custo por análise:**
    - ~R$ 0,10 por extrato
    - 6 extratos = R$ 0,60
    
    **Arquivos aceitos:**
    - PDF, JPG, PNG
    - Máximo: 6 arquivos
    """)
    
    st.markdown("---")
    st.markdown("### 💼 Sobre")
    st.markdown("""
    **Calculadora de Renda PRO**
    
    Versão 3.0
    
    © 2024 Magalhães Negócios
    """)

# Título principal
st.markdown("# 💰 Calculadora de Renda PRO")
st.markdown("### Análise automática de extratos bancários com Inteligência Artificial")
st.markdown("---")

# Verificar se tem API key
if not api_key:
    st.error("❌ Configure sua chave API na barra lateral para começar!")
    st.stop()

# Upload de arquivos
st.markdown("## 📄 Upload dos Extratos")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_files = st.file_uploader(
        "Arraste os extratos bancários aqui (até 6 arquivos)",
        type=['pdf', 'jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        help="Você pode selecionar múltiplos arquivos de uma vez"
    )

with col2:
    if uploaded_files:
        st.markdown(f"""
        <div class="success-box">
            <h4>✅ Arquivos Carregados</h4>
            <p style="font-size: 1.5rem; font-weight: bold; margin: 0;">{len(uploaded_files)}/6</p>
        </div>
        """, unsafe_allow_html=True)

# Mostrar lista de arquivos
if uploaded_files:
    st.markdown("### 📋 Arquivos Selecionados:")
    for i, file in enumerate(uploaded_files, 1):
        file_size = len(file.getvalue()) / 1024  # KB
        st.markdown(f"**{i}.** {file.name} ({file_size:.1f} KB)")
    
    if len(uploaded_files) > 6:
        st.error("❌ Máximo de 6 arquivos permitidos!")
        st.stop()

st.markdown("---")

# Botão de análise
if uploaded_files and len(uploaded_files) <= 6:
    if st.button("🚀 Analisar Extratos"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        all_transactions = []
        
        try:
            for i, file in enumerate(uploaded_files):
                progress = (i) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.markdown(f"### ⏳ Analisando extrato {i + 1} de {len(uploaded_files)}...")
                
                file_bytes = file.getvalue()
                base64_file = base64.b64encode(file_bytes).decode('utf-8')
                
                if file.type == 'application/pdf':
                    media_type = 'application/pdf'
                    content_type = 'document'
                elif file.type in ['image/jpeg', 'image/jpg']:
                    media_type = 'image/jpeg'
                    content_type = 'image'
                elif file.type == 'image/png':
                    media_type = 'image/png'
                    content_type = 'image'
                
                client = anthropic.Anthropic(api_key=api_key)
                
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": content_type,
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": base64_file
                                }
                            },
                            {
                                "type": "text",
                                "text": """Analise este extrato bancário e extraia APENAS as ENTRADAS.

REGRAS:
- IGNORE transferências entre contas do mesmo titular
- IGNORE transferências de família (mãe, pai, irmão, irmã)
- CONSIDERE apenas: salários, rendimentos, vendas, recebimentos

Retorne JSON:
{
  "transacoes": [
    {"data": "YYYY-MM-DD", "descricao": "texto", "valor": 1234.56}
  ]
}

IMPORTANTE: 
- Valores sem R$ ou pontos (ex: 1234.56)
- Data formato YYYY-MM-DD
- Retorne APENAS o JSON"""
                            }
                        ]
                    }]
                )
                
                content = message.content[0].text
                json_text = content
                if '```json' in content:
                    json_text = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    json_text = content.split('```')[1].split('```')[0].strip()
                
                result = json.loads(json_text)
                if result.get('transacoes'):
                    all_transactions.extend(result['transacoes'])
            
            progress_bar.progress(1.0)
            status_text.markdown("### ✅ Análise concluída!")
            
            if all_transactions:
                df = pd.DataFrame(all_transactions)
                df['data'] = pd.to_datetime(df['data'])
                df['mes'] = df['data'].dt.to_period('M')
                
                monthly = df.groupby('mes')['valor'].sum().reset_index()
                monthly['mes_nome'] = monthly['mes'].dt.strftime('%B/%Y')
                monthly['mes_nome'] = monthly['mes_nome'].str.capitalize()
                
                meses_pt = {
                    'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
                    'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
                    'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
                    'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
                }
                for eng, pt in meses_pt.items():
                    monthly['mes_nome'] = monthly['mes_nome'].str.replace(eng, pt)
                
                total = df['valor'].sum()
                media = monthly['valor'].mean()
                
                st.session_state.results = {
                    'total': total,
                    'media': media,
                    'monthly': monthly,
                    'transactions': df
                }
                
                st.success("✅ Análise concluída com sucesso!")
            else:
                st.error("❌ Nenhuma transação de entrada encontrada.")
                
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")

# Mostrar resultados
if st.session_state.results:
    results = st.session_state.results
    
    st.markdown("---")
    st.markdown("## 📊 Resultados da Análise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p style="font-size: 1rem; margin: 0; opacity: 0.9;">Média Mensal</p>
            <h2 style="font-size: 2.5rem; margin: 0.5rem 0;">R$ {results['media']:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p style="font-size: 1rem; margin: 0; opacity: 0.9;">Total de Entradas</p>
            <h2 style="font-size: 2.5rem; margin: 0.5rem 0;">R$ {results['total']:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📅 Detalhamento Mensal")
    
    for _, row in results['monthly'].iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{row['mes_nome']}**")
        with col2:
            st.markdown(f"**R$ {row['valor']:,.2f}**")
    
    st.markdown("---")
    st.markdown("### 📥 Baixar Relatório")
    
    df_export = results['transactions'].copy()
    df_export['data'] = df_export['data'].dt.strftime('%d/%m/%Y')
    df_export = df_export[['data', 'descricao', 'valor']]
    df_export.columns = ['Data', 'Descrição', 'Valor']
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name='Transações')
        
        resumo_data = {
            'Métrica': ['Total', 'Média Mensal', 'Meses'],
            'Valor': [
                f"R$ {results['total']:,.2f}",
                f"R$ {results['media']:,.2f}",
                len(results['monthly'])
            ]
        }
        pd.DataFrame(resumo_data).to_excel(writer, index=False, sheet_name='Resumo')
    
    excel_data = output.getvalue()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="📥 Baixar Relatório Excel",
            data=excel_data,
            file_name=f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>Calculadora de Renda PRO</strong> - Versão 3.0</p>
    <p>© 2024 Magalhães Negócios</p>
</div>
""", unsafe_allow_html=True)
