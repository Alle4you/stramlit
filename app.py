import streamlit as st
import pandas as pd
import sqlite3
from sqlite3 import Error
from datetime import date
import matplotlib.pyplot as plt

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    if conn:
        return conn


def create_tables(conn):
    try:
        sql_exercicio_table = """CREATE TABLE IF NOT EXISTS exercicios (
                                    id integer PRIMARY KEY,
                                    usuario text NOT NULL,
                                    data text NOT NULL,
                                    exercicio text,
                                    grupo_muscular text,
                                    carga integer,
                                    repeticoes integer
                                );"""
        sql_medida_table = """CREATE TABLE IF NOT EXISTS medidas (
                                id integer PRIMARY KEY,
                                usuario text NOT NULL,
                                data text NOT NULL,
                                grupo_muscular text,
                                medida real,
                                lado text
                            );"""
        sql_nutrientes_table = """CREATE TABLE IF NOT EXISTS nutrientes (
                                    id integer PRIMARY KEY,
                                    usuario text NOT NULL,
                                    data text NOT NULL,
                                    vitamina text,
                                    creatina boolean,
                                    proteina real,
                                    tipo_proteina text
                                );"""
        conn.execute(sql_exercicio_table)
        conn.execute(sql_medida_table)
        conn.execute(sql_nutrientes_table)
        conn.commit()
    except Error as e:
        print(e)


def add_exercicio(conn, exercicio):
    sql = '''INSERT INTO exercicios(usuario, data, exercicio, grupo_muscular, carga, repeticoes)
              VALUES(?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, exercicio)
    conn.commit()


def add_medida(conn, medida):
    sql = '''INSERT INTO medidas(usuario, data, grupo_muscular, medida, lado)
              VALUES(?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, medida)
    conn.commit()


def add_nutrientes(conn, nutrientes):
    usuario, data, vitaminas, creatina, proteina, tipo_proteina = nutrientes
    vitaminas_str = ",".join(vitaminas)
    sql = '''INSERT INTO nutrientes(usuario, data, vitamina, creatina, proteina, tipo_proteina)
              VALUES(?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, (usuario, data, vitaminas_str, creatina, proteina, tipo_proteina))
    conn.commit()

def view_data(conn, tipo_dados, usuario):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {tipo_dados} WHERE usuario=? ORDER BY id DESC LIMIT 1", (usuario,))

    rows = cur.fetchall()

    for row in rows:
        st.write(row)


def generate_daily_report(conn, usuario):
    st.subheader("Relatório Diário")

    # Obter dados de medidas
    df_medidas = pd.read_sql_query(f"SELECT * FROM medidas WHERE usuario='{usuario}'", conn)
    if df_medidas.empty:
        st.warning("Nenhum dado de medidas encontrado.")
    else:
        df_medidas['data'] = pd.to_datetime(df_medidas['data'])
        df_medidas.set_index('data', inplace=True)

        # Gráfico de evolução de medidas por grupo muscular
        st.subheader("Evolução de Medidas")
        fig, ax = plt.subplots()
        for grupo_muscular in df_medidas['grupo_muscular'].unique():
            df_grupo = df_medidas[df_medidas['grupo_muscular'] == grupo_muscular]
            ax.plot(df_grupo.index, df_grupo['medida'], label=grupo_muscular)
        ax.legend()
        st.pyplot(fig)

    # Obter dados de nutrientes
    df_nutrientes = pd.read_sql_query(f"SELECT * FROM nutrientes WHERE usuario='{usuario}'", conn)
    if df_nutrientes.empty:
        st.warning("Nenhum dado de nutrientes encontrado.")
    else:
        df_nutrientes['data'] = pd.to_datetime(df_nutrientes['data'])
        df_nutrientes.set_index('data', inplace=True)

        # Gráfico de evolução de nutrientes
        st.subheader("Evolução de Nutrientes")
        fig, ax = plt.subplots()
        ax.plot(df_nutrientes.index, df_nutrientes['proteina'])
        ax.set_ylabel("Quantidade de Proteína (gramas)")
        st.pyplot(fig)

    # Cálculo de total de peso levantado por grupo muscular
    df_exercicios = pd.read_sql_query(f"SELECT * FROM exercicios WHERE usuario='{usuario}'", conn)
    if df_exercicios.empty:
        st.warning("Nenhum dado de exercícios encontrado.")
    else:
        st.subheader("Cálculo de Total de Peso Levantado por Grupo Muscular")
        df_exercicios['peso_total'] = df_exercicios['carga'] * df_exercicios['repeticoes']
        df_total_peso = df_exercicios.groupby('grupo_muscular')['peso_total'].sum()
        st.bar_chart(df_total_peso)


def main():
    st.title("App de Registro de Treinos")

    db_file = 'my_training.db'
    conn = create_connection(db_file)
    create_tables(conn)

    # User Authentication
    users = {"Lucca": "077612", "Alexandre": "077612"}
    user = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")
    login = st.sidebar.button("Login")
    if login:
        if user in users and users[user] == password:
            st.sidebar.success("Logged In successfully.")
        else:
            st.sidebar.error("Incorrect Username/Password")
            return

    # Navigational Menu
    menu = ["Adicionar Exercício", "Adicionar Medidas", "Adicionar Nutrientes"]
    choice = st.sidebar.selectbox("Menu", menu)

    if st.sidebar.button("Relatório Diário"):
        if user in users and users[user] == password:
            generate_daily_report(conn, user)

    grupos_musculares = ["Peito", "Costas", "Braços", "Pernas", "Abdômen", "Panturrilha"]
    exercicios_por_grupo = {
        "Peito": ["Supino", "Crossover", "Peck Deck", "Flexão de Braço", "Supino Inclinado", "Supino Declinado", "Crucifixo", "Pull Over", "Press Militar", "Mergulho em Barras Paralelas"],
        "Costas": ["Remada", "Puxada na Polia", "Levantamento Terra", "Remada Invertida", "Pullover", "Hyperextensions", "Remada Curvada", "Good Morning", "Puxada Frontal", "Chin Ups"],
        "Braços": ["Rosca Direta", "Rosca Martelo", "Tríceps na Polia", "Rosca Invertida", "Rosca Scott", "Tríceps Testa", "Tríceps Francês", "Tríceps Coice", "Tríceps Mergulho", "Rosca Concentrada"],
        "Pernas": ["Agachamento", "Leg Press", "Stiff", "Mesa Flexora", "Cadeira Extensora", "Cadeira Adutora", "Cadeira Abdutora", "Panturrilha em Pé", "Panturrilha Sentado", "Agachamento Frontal"],
        "Abdômen": ["Abdominal", "Prancha", "Abdominal Invertido", "Abdominal Lateral", "Abdominal Infra", "Abdominal Oblíquo", "Abdominal no Pulley", "Abdominal na Bola", "Abdominal com Peso", "Abdominal Bicicleta"],
        "Panturrilha": ["Panturrilha em Pé", "Panturrilha Sentado", "Panturrilha no Leg Press"]
    }

    if choice == "Adicionar Exercício":
        st.subheader("Adicionar Exercício")
        data = date.today().isoformat()
        grupo_muscular_exercicio = st.selectbox("Grupo Muscular", grupos_musculares)
        exercicio = st.selectbox("Exercício", exercicios_por_grupo[grupo_muscular_exercicio])
        carga = st.number_input("Carga (kg)", min_value=0, step=1)
        repeticoes = st.number_input("Repetições", min_value=0, step=1)
        if st.button("Salvar Exercício"):
            add_exercicio(conn, (user, data, exercicio, grupo_muscular_exercicio, carga, repeticoes))
            st.success("Exercício salvo com sucesso!")
            view_data(conn, 'exercicios', user)

    elif choice == "Adicionar Medidas":
        st.subheader("Adicionar Medidas")
        data = date.today().isoformat()
        grupo_muscular_medida = st.selectbox("Grupo Muscular", grupos_musculares)
        medida = st.number_input("Medida (cm)", min_value=0.0, step=0.1)
        lado = st.selectbox("Lado", ["Esquerdo", "Direito"])
        if st.button("Salvar Medida"):
            add_medida(conn, (user, data, grupo_muscular_medida, medida, lado))
            st.success("Medida salva com sucesso!")
            view_data(conn, 'medidas', user)

    elif choice == "Adicionar Nutrientes":
        st.subheader("Adicionar Nutrientes")
        data = date.today().isoformat()
        vitamina = st.multiselect("Vitaminas", ["B12", "D", "C", "Multi Vitamínico", "Ginkgo"])
        creatina = st.checkbox("Creatina")
        proteina = st.number_input("Quantidade de Proteína (gramas)", min_value=0.0, step=0.1)
        tipo_proteina = st.selectbox("Tipo de Proteína", ["Carne Vermelha", "Frango", "Peixe"])
        if st.button("Salvar Nutrientes"):
            add_nutrientes(conn, (user, data, vitamina, creatina, proteina, tipo_proteina))
            st.success("Nutrientes salvos com sucesso!")
            view_data(conn, 'nutrientes', user)


if __name__ == "__main__":
    main()
