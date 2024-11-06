import pandas as pd
import streamlit as st
from langchain.llms import OpenAI  # Correção da importação
from langchain_experimental.agents import create_pandas_dataframe_agent
import openai
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Verificação da chave de API
openai_api_key = os.getenv("OPENAI_API_KEY")  # Busca a chave do ambiente
if not openai_api_key:
    st.error("Erro: A chave da API OpenAI não foi configurada. Verifique as configurações.")
else:
    try:
        # Configura o modelo de linguagem com a chave fornecida
        llm = OpenAI(openai_api_key=openai_api_key)
    except Exception as e:
        st.error(f"Erro ao inicializar o modelo de linguagem: {e}")

# Função para carregar o arquivo Excel com cache para otimização
@st.cache_data
def carregar_dados(file_path):
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo de dados: {e}")
        return None

# Carregando a planilha Faturamento Abate das Fazendas.xlsx
file_path = 'Fazendas.xlsx'
df = carregar_dados(file_path)

# Verifica se o DataFrame foi carregado corretamente e se o modelo de linguagem foi configurado
if df is not None and 'llm' in locals():
    # Criando o agente que permite interagir com o DataFrame
    try:
        agent = create_pandas_dataframe_agent(llm, df, allow_dangerous_code=True)
    except Exception as e:
        st.error(f"Erro ao criar o agente: {e}")

    # Interface do Streamlit
    st.title("Análise do Faturamento Abate das Fazendas")

    # Exibindo o DataFrame para o usuário visualizar os dados
    with st.expander("Visualizar Dados Carregados"):
        st.dataframe(df)

    # Função para gerar narrativa com base nos dados
    def gerar_narrativa(df, contexto):
        prompt = f"""
        A seguir estão os dados da fazenda:
        {df.to_string(index=False)}

        Como um assistente de gestão da fazenda e escritório, crie um resumo narrativo para o contexto de {contexto}, destacando as principais tendências, pontos de atenção e sugestões para melhoria.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um assistente que ajuda a administrar uma fazenda e realizar trabalhos de escritório."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500  # Aumentado para respostas mais completas
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            st.error(f"Erro ao gerar narrativa: {e}")
            return None

    # Caixa de texto para perguntas do usuário
    user_question = st.text_input("Faça uma pergunta sobre os dados:")

    # Botão para enviar a pergunta
    if st.button("Consultar"):
        if user_question:
            try:
                response = agent.invoke(user_question)
                st.write("Resposta:")
                st.write(response)
            except Exception as e:
                st.error(f"Erro ao processar a pergunta: {e}")
        else:
            st.warning("Por favor, insira uma pergunta.")

    # Sugestões de Perguntas para Usuários
    st.sidebar.title("Sugestões de Perguntas")
    suggested_questions = [
        "QUAL FOI A QUANTIDADE DE BOIS ABATIDOS EM 2023?",
        "QUAL FOI A QUANTIDADE DE BOIS ABATIDOS EM DEZEMBRO DE 2023?",
        "QUAL FOI O PESO TOTAL DOS BOIS ABATIDOS EM DEZEMBRO DE 2023?",
        "QUAL FOI A QUANTIDADE DE BOIS ABATIDOS EM 2024?",
        "QUAL FOI O VALOR FUNRURAL EM 2023?",
    ]
    for question in suggested_questions:
        if st.sidebar.button(question):
            user_question = question
            try:
                response = agent.invoke(user_question)
                st.write("Resposta:")
                st.write(response)
            except Exception as e:
                st.error(f"Erro ao processar a pergunta: {e}")

else:
    st.error("Não foi possível carregar os dados ou configurar o modelo de linguagem.")
