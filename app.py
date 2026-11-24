
import streamlit as st
import pandas as pd
import banco


# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Stock Control",
    page_icon="📦",
    layout="wide"
)

# CRIAR TABELAS
banco.criar_tabelas()


# ESTILO CSS
st.markdown("""
<style>

.stApp {
    background-color: #0E1117;
    color: #FFFFFF;
}

[data-testid="stSidebar"] {
    background-color: #151B26;
}

h1, h2, h3 {
    color: #FFFFFF;
}

.metric-card {
    background-color: #192333;
    padding: 22px;
    border-radius: 12px;
    border: 1px solid #26364D;
}

.metric-title {
    color: #AAB7CA;
    font-size: 14px;
}

.metric-value {
    color: #FFFFFF;
    font-size: 28px;
    font-weight: bold;
}

.stButton button {
    background-color: #2563EB;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: bold;
}

.stButton button:hover {
    background-color: #1D4ED8;
    color: white;
}

div[data-testid="stForm"] {
    background-color: #151B26;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #26364D;
}

</style>
""", unsafe_allow_html=True)


# FUNÇÃO PARA MOSTRAR INDICADORES
def mostrar_card(titulo, valor):
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{titulo}</div>
            <div class="metric-value">{valor}</div>
        </div>
    """, unsafe_allow_html=True)


# MENU LATERAL
st.sidebar.title("📦 STOCK CONTROL")
st.sidebar.caption("Sistema de gerenciamento de estoque")

pagina = st.sidebar.radio(
    "NAVEGAÇÃO",
    [
        "Dashboard",
        "Produtos",
        "Movimentações",
        "Histórico",
        "Relatórios"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Sistema desenvolvido em Python + SQL")
st.sidebar.caption("Projeto de Algoritmos")


# ==================================================
# DASHBOARD
# ==================================================

if pagina == "Dashboard":

    st.title("📊 Dashboard")
    st.write("Visão geral do controle de estoque.")

    total_produtos, total_itens, valor_total, estoque_baixo = (
        banco.obter_estatisticas()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        mostrar_card("Produtos cadastrados", total_produtos)

    with col2:
        mostrar_card("Itens em estoque", total_itens)

    with col3:
        mostrar_card(
            "Valor do estoque",
            f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    with col4:
        mostrar_card("Estoque baixo", estoque_baixo)

    st.divider()

    st.subheader("Produtos cadastrados")

    produtos = banco.listar_produtos()

    if produtos:
        df = pd.DataFrame(
            produtos,
            columns=[
                "ID", "Nome", "Categoria",
                "Preço", "Quantidade", "Estoque mínimo"
            ]
        )

        st.dataframe(df, use_container_width=True, hide_index=True)

    else:
        st.info("Nenhum produto cadastrado ainda.")


# ==================================================
# PRODUTOS
# ==================================================

elif pagina == "Produtos":

    st.title("📦 Gerenciamento de Produtos")

    aba1, aba2, aba3 = st.tabs([
        "Cadastrar",
        "Editar",
        "Excluir"
    ])

    # CADASTRAR
    with aba1:

        st.subheader("Novo produto")

        with st.form("form_cadastro"):

            nome = st.text_input("Nome do produto")

            categoria = st.selectbox(
                "Categoria",
                ["Eletrônicos", "Alimentos", "Roupas",
                 "Informática", "Limpeza", "Outros"]
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                preco = st.number_input(
                    "Preço (R$)",
                    min_value=0.01,
                    value=10.00,
                    step=1.00
                )

            with col2:
                quantidade = st.number_input(
                    "Quantidade",
                    min_value=0,
                    value=1,
                    step=1
                )

            with col3:
                estoque_minimo = st.number_input(
                    "Estoque mínimo",
                    min_value=0,
                    value=5,
                    step=1
                )

            cadastrar = st.form_submit_button(
                
                "Cadastrar produto",
                use_container_width=True
            )

            if cadastrar:

                if not nome.strip():
                    st.error("Informe o nome do produto.")

                else:
                    banco.cadastrar_produto(
                        nome.strip(),
                        categoria,
                        preco,
                        quantidade,
                        estoque_minimo
                    )

                    st.success("Produto cadastrado com sucesso!")
                    st.rerun()

    # EDITAR
    with aba2:

        st.subheader("Editar produto")

        produtos = banco.listar_produtos()

        if produtos:

            opcoes = {
                f"{p[0]} - {p[1]}": p[0]
                for p in produtos
            }

            selecionado = st.selectbox(
                "Selecione o produto",
                list(opcoes.keys()),
                key="editar_produto"
            )

            id_produto = opcoes[selecionado]
            produto = banco.buscar_produto(id_produto)

            with st.form("form_edicao"):

                novo_nome = st.text_input(
                    "Nome",
                    value=produto[1]
                )

                nova_categoria = st.text_input(
                    "Categoria",
                    value=produto[2]
                )

                novo_preco = st.number_input(
                    "Preço",
                    min_value=0.01,
                    value=float(produto[3]),
                    step=1.0
                )

                novo_minimo = st.number_input(
                    "Estoque mínimo",
                    min_value=0,
                    value=int(produto[5])
                )

                salvar = st.form_submit_button(
                    "Salvar alterações"
                )

                if salvar:

                    if not novo_nome.strip() or not nova_categoria.strip():
                        st.error("Preencha todos os campos.")

                    else:
                        banco.editar_produto(
                            id_produto,
                            novo_nome.strip(),
                            nova_categoria.strip(),
                            novo_preco,
                            novo_minimo
                        )

                        st.success("Produto atualizado!")
                        st.rerun()

        else:
            st.info("Não existem produtos cadastrados.")

    # EXCLUIR
    with aba3:

        st.subheader("Excluir produto")

        produtos = banco.listar_produtos()

        if produtos:

            opcoes = {
                f"{p[0]} - {p[1]}": p[0]
                for p in produtos
            }

            selecionado = st.selectbox(
                "Produto para exclusão",
                list(opcoes.keys()),
                key="excluir_produto"
            )

            if st.button("Excluir produto", type="primary"):

                resultado = banco.excluir_produto(
                    opcoes[selecionado]
                )

                if resultado:
                    st.success("Produto excluído!")
                    st.rerun()

                else:
                    st.error(
                        "Não é possível excluir este produto, "
                        "pois existem movimentações registradas."
                    )

        else:
            st.info("Nenhum produto disponível.")


# ==================================================
# MOVIMENTAÇÕES
# ==================================================

elif pagina == "Movimentações":

    st.title("🔄 Movimentações de Estoque")

    produtos = banco.listar_produtos()

    if produtos:

        opcoes = {
            f"{p[0]} - {p[1]} (Estoque: {p[4]})": p[0]
            for p in produtos
        }

        with st.form("form_movimentacao"):

            produto_escolhido = st.selectbox(
                "Selecione o produto",
                list(opcoes.keys())
            )

            tipo = st.selectbox(
                "Tipo de movimentação",
                ["Entrada", "Saída"]
            )

            quantidade = st.number_input(
                "Quantidade",
                min_value=1,
                value=1,
                step=1
            )

            registrar = st.form_submit_button(
                "Registrar movimentação",
                use_container_width=True
            )

            if registrar:

                sucesso, mensagem = banco.movimentar_estoque(
                    opcoes[produto_escolhido],
                    tipo,
                    quantidade
                )

                if sucesso:
                    st.success(mensagem)
                    st.rerun()

                else:
                    st.error(mensagem)

    else:
        st.warning("Cadastre um produto antes de movimentar o estoque.")


# ==================================================
# HISTÓRICO
# ==================================================

elif pagina == "Histórico":

    st.title("📋 Histórico de Movimentações")

    movimentacoes = banco.listar_movimentacoes()

    if movimentacoes:

        df = pd.DataFrame(
            movimentacoes,
            columns=[
                "ID",
                "Produto",
                "Tipo",
                "Quantidade",
                "Data"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Nenhuma movimentação registrada.")


# ==================================================
# RELATÓRIOS
# ==================================================

elif pagina == "Relatórios":

    st.title("📈 Relatórios do Estoque")

    st.subheader("Produtos com estoque baixo")

    produtos = banco.produtos_estoque_baixo()

    if produtos:

        df = pd.DataFrame(
            produtos,
            columns=[
                "Produto",
                "Categoria",
                "Quantidade atual",
                "Estoque mínimo"
            ]
        )

        st.warning("Atenção! Existem produtos que precisam de reposição.")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success("Todos os produtos estão com estoque acima do mínimo.")

    st.divider()

    st.subheader("Resumo financeiro")

    total_produtos, total_itens, valor_total, estoque_baixo = (
        banco.obter_estatisticas()
    )

    st.metric(
        "Valor total dos produtos em estoque",
        f"R$ {valor_total:,.2f}"
    )

    st.metric(
        "Quantidade total de unidades",
        total_itens
    )

    st.metric(
        "Produtos cadastrados",
        total_produtos
    )

