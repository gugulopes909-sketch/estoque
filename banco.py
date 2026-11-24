
import sqlite3

NOME_BANCO = "estoque.db"


# CONEXÃO COM O BANCO
def conectar():
    conexao = sqlite3.connect(NOME_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


# CRIAÇÃO DAS TABELAS
def criar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL,
            estoque_minimo INTEGER DEFAULT 5
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produto_id)
            REFERENCES produtos(id)
            ON DELETE RESTRICT
        )
    """)

    conexao.commit()
    conexao.close()


# CADASTRAR PRODUTO
def cadastrar_produto(nome, categoria, preco, quantidade, estoque_minimo):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO produtos
        (nome, categoria, preco, quantidade, estoque_minimo)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, categoria, preco, quantidade, estoque_minimo))

    conexao.commit()
    conexao.close()


# LISTAR PRODUTOS
def listar_produtos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, categoria, preco, quantidade, estoque_minimo
        FROM produtos
        ORDER BY nome
    """)

    produtos = cursor.fetchall()
    conexao.close()

    return produtos


# BUSCAR PRODUTO PELO ID
def buscar_produto(id_produto):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT * FROM produtos WHERE id = ?",
        (id_produto,)
    )

    produto = cursor.fetchone()
    conexao.close()

    return produto


# EDITAR PRODUTO
def editar_produto(id_produto, nome, categoria, preco, estoque_minimo):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE produtos
        SET nome = ?, categoria = ?, preco = ?,
            estoque_minimo = ?
        WHERE id = ?
    """, (nome, categoria, preco, estoque_minimo, id_produto))

    conexao.commit()
    conexao.close()


# EXCLUIR PRODUTO
def excluir_produto(id_produto):
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            "DELETE FROM produtos WHERE id = ?",
            (id_produto,)
        )

        conexao.commit()
        return True

    except sqlite3.IntegrityError:
        conexao.rollback()
        return False

    finally:
        conexao.close()


# REGISTRAR ENTRADA OU SAÍDA
def movimentar_estoque(id_produto, tipo, quantidade):

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        if quantidade <= 0:
            return False, "A quantidade deve ser maior que zero."

        cursor.execute(
            "SELECT quantidade FROM produtos WHERE id = ?",
            (id_produto,)
        )

        resultado = cursor.fetchone()

        if resultado is None:
            return False, "Produto não encontrado."

        estoque_atual = resultado[0]

        if tipo == "Entrada":
            nova_quantidade = estoque_atual + quantidade

        elif tipo == "Saída":
            if quantidade > estoque_atual:
                return False, "Estoque insuficiente."

            nova_quantidade = estoque_atual - quantidade

        else:
            return False, "Tipo de movimentação inválido."

        cursor.execute("""
            UPDATE produtos
            SET quantidade = ?
            WHERE id = ?
        """, (nova_quantidade, id_produto))

        cursor.execute("""
            INSERT INTO movimentacoes
            (produto_id, tipo, quantidade)
            VALUES (?, ?, ?)
        """, (id_produto, tipo, quantidade))

        conexao.commit()

        return True, "Movimentação realizada com sucesso!"

    except sqlite3.Error as erro:
        conexao.rollback()
        return False, f"Erro no banco de dados: {erro}"

    finally:
        conexao.close()


# HISTÓRICO DE MOVIMENTAÇÕES
def listar_movimentacoes():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            movimentacoes.id,
            produtos.nome,
            movimentacoes.tipo,
            movimentacoes.quantidade,
            movimentacoes.data
        FROM movimentacoes
        INNER JOIN produtos
        ON movimentacoes.produto_id = produtos.id
        ORDER BY movimentacoes.id DESC
    """)

    movimentacoes = cursor.fetchall()
    conexao.close()

    return movimentacoes


# ESTATÍSTICAS DO ESTOQUE
def obter_estatisticas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            COALESCE(SUM(quantidade), 0),
            COALESCE(SUM(preco * quantidade), 0),
            COALESCE(SUM(
                CASE
                    WHEN quantidade <= estoque_minimo THEN 1
                    ELSE 0
                END
            ), 0)
        FROM produtos
    """)

    estatisticas = cursor.fetchone()
    conexao.close()

    return estatisticas


# PRODUTOS COM ESTOQUE BAIXO
def produtos_estoque_baixo():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT nome, categoria, quantidade, estoque_minimo
        FROM produtos
        WHERE quantidade <= estoque_minimo
        ORDER BY quantidade
    """)

    produtos = cursor.fetchall()
    conexao.close()

    return produtos
