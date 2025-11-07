# Importando as bibliotecas necessárias
import ttkbootstrap as ttk  # ttkbootstrap é uma versão moderna e estilizada do tkinter
from tkinter import messagebox  # usado para mostrar mensagens de aviso, erro ou sucesso
import sqlite3


# ======= CRIANDO A JANELA PRINCIPAL =======
janela = ttk.Window(themename="cosmo")  # cria a janela e define o tema visual ("minty")
janela.title("Sistema de Agendamentos")  # define o título da janela
janela.geometry("900x700")  # define o tamanho da janela (largura x altura)

# ======= FRAME PRINCIPAL =======
# Frame serve para organizar os widgets (rótulos, botões, etc.)
frame_janela = ttk.Frame(janela)
frame_janela.pack(pady=10)  # adiciona o frame à janela com espaçamento vertical


# ======= CAMPOS DE ENTRADA =======
# Cada par (Label + Entry) cria um campo para o usuário digitar informações


# Campo nome do cliente
ttk.Label(frame_janela, text="Cliente:").pack() #nome cliente
nome_cliente = ttk.Entry(frame_janela, width=20) #caixa de texto
nome_cliente.pack()

# Campo horário
ttk.Label(frame_janela, text="Horário:").pack()
hora_cliente = ttk.Entry(frame_janela, width=20)
hora_cliente.pack()

# Campo data
ttk.Label(frame_janela, text="Data:").pack()
data_cliente = ttk.DateEntry(frame_janela, width=20)
data_cliente.pack()

# Campo serviço
ttk.Label(frame_janela, text="Serviço:").pack()
servico_cliente = ttk.Entry(frame_janela, width=20)
servico_cliente.pack()


# ======= BANCO DE DADOS =======
def criar_tabela_usuario():
    conexao = sqlite3.connect("bd_treeview.sqlite")
    cursor = conexao.cursor() #é um comando que faz o sql conversar com o python
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Agendamento (
            Cliente TEXT primary key,
            Horario TEXT,
            Data DATE,
            Servico TEXT
        )
    """)
    conexao.commit()
    conexao.close()

criar_tabela_usuario()  #ele cria o banco de dados se ele nao existe ainda

# ======= FUNÇÃO PARA LIMPAR TODOS OS CAMPOS =======
def limpar_camposozinho():
    nome_cliente.delete(0, "end")
    hora_cliente.delete(0, "end")
    data_cliente.entry.delete(0, "end")
    servico_cliente.delete(0, "end")

# ======= FUNÇÃO PARA CARREGAR DADOS DO BANCO =======
def carregar_agendamentos():
    conexao = sqlite3.connect("bd_treeview.sqlite")
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM Agendamento")
    dados = cursor.fetchall()
    conexao.commit()
    conexao.close()

    for item in treeview.get_children():
        treeview.delete(item)
                                                    #isso faz atualizar, apaga e atualiza
    for linha in dados:
        treeview.insert("", "end", values=linha)

# ======= FUNÇÃO PARA ADICIONAR UM AGENDAMENTO =======
def adicionar_agendamento():
    # pega os valores digitados nas caixinhas
    cliente = nome_cliente.get()
    horario = hora_cliente.get()
    data = data_cliente.get_date()
    servico = servico_cliente.get()

    if not cliente or not horario or not data or not servico:
        messagebox.showwarning("Aviso", "Preencha todos os campos!")
        return

    try:
        conexao = sqlite3.connect("bd_treeview.sqlite")
        cursor = conexao.cursor()

        cursor.execute("SELECT * FROM Agendamento WHERE Data=? AND Horario=?", (data, horario))
        agendamento_existente = cursor.fetchall()  # Recupera todas as linhas que correspondem à consulta
        print(agendamento_existente)
        conexao.close()
        if agendamento_existente:
            messagebox.showerror("Error", "Já existe um agendamento para esse horário e data!")
            return
        
        conexao = sqlite3.connect("bd_treeview.sqlite")
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO Agendamento VALUES (?, ?, ?, ?)", (cliente, horario, data, servico))
        conexao.commit()
        conexao.close()

        # adiciona na tabela da tela
        treeview.insert("", "end", values=(cliente, horario, data, servico))
        limpar_camposozinho()
        messagebox.showinfo("Sucesso", "Agendamento adicionado!")

    except sqlite3.IntegrityError:
       None


    # conexao = sqlite3.connect(bd_treeview.sqlite)

    # treeview.insert("", "end", values=(cliente, horario, data, servico))
    # limpar_camposozinho()  
    # # se estiver tudo certo, adiciona na tabela
    # treeview.insert("", "end", values=(cliente, horario, data, servico))

    # # limpa os campos após adicionar
    # limpar_camposozinho()

# ======= FUNÇÃO PARA ALTERAR UM AGENDAMENTO EXISTENTE =======
def alterar_agendamento():
    selecionado = treeview.selection()  # pega o item selecionado na tabela

    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione um agendamento para alterar.")
        return

    item = selecionado[0]  # pega o primeiro item selecionado
    valores_antigos = treeview.item(item, "values")
    horario_antigo = valores_antigos[1]
    data_antiga = valores_antigos[2]

    # lê os novos valores digitados
    cliente = nome_cliente.get()
    horario = hora_cliente.get()
    data = data_cliente.get_date()
    servico = servico_cliente.get()

    # verifica se os campos não estão vazios
    if not cliente or not servico or not data or not horario:
        messagebox.showwarning("Aviso", "Preencha todos os campos!")
        return

    try:
        conexao = sqlite3.connect("bd_treeview.sqlite")
        cursor = conexao.cursor()
        #verifica se já existe outro agendamento igual (mesma DATA E HORARIO)
        cursor.execute("""
        SELECT * FROM Agendamento
        WHERE Data=? AND Horario=? AND NOT (Data=? AND Horario=?)
                       """, (data, horario, data_antiga, horario_antigo))
        conflito = cursor.fetchall()

        if conflito:
            messagebox.showerror("Erro", "Já existe um agendamento para esse horário de data!")
            conexao.close()
            return

        #Atualiza o agendamento
        cursor.execute("""
            UPDATE Agendamento
            SET Cliente=?, Horario=?, Data=?, Servico=?
            WHERE Horario=? AND Data=?
        """, (cliente, horario, data, servico, horario_antigo, data_antiga))

        conexao.commit()
        conexao.close()

        treeview.item(item, values=(cliente, horario, data, servico))
        limpar_camposozinho()
        messagebox.showinfo("Sucesso", "Agendamento alterado!")

    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Já existe um agendamento com esse horário!")
    treeview.item(item, values=(cliente, horario, data, servico))

    # limpa os campos depois de alterar
    limpar_camposozinho()

# ======= FUNÇÃO QUE PREENCHE OS CAMPOS AO CLICAR NA TABELA =======
def preencher_campos(event):
    selecionado = treeview.selection()
    if not selecionado:
        return

    # pega os valores da linha selecionada
    valores = treeview.item(selecionado[0], "values")

    # limpa os campos antigos
    nome_cliente.delete(0, "end")
    hora_cliente.delete(0, "end")
    data_cliente.delete(0, "end")
    servico_cliente.delete(0, "end")

    # insere os novos valores (da linha clicada)
    nome_cliente.insert(0, valores[0])
    hora_cliente.insert(0, valores[1])
    data_cliente.insert(0, valores[2])
    servico_cliente.insert(0, valores[3])


# ======= FUNÇÃO PARA APAGAR AGENDAMENTOS =======
def apagar_clientes():
    selecionado = treeview.selection()  # verifica se há algo selecionado
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione um agendamento para apagar.")
        return
    conexao = sqlite3.connect("bd_treeview.sqlite")
    cursor = conexao.cursor()

    for item in selecionado:
        valores = treeview.item(item, "values")
        horario = valores[1]
        cursor.execute("DELETE FROM Agendamento WHERE Horario=?", (horario,))
        treeview.delete(item)

    conexao.commit()
    conexao.close()
    messagebox.showinfo("Sucesso", "Agendamento apagado!")
    


    # deleta cada item selecionado
    for item in selecionado:
        treeview.delete(item)

# ======= FRAME DOS BOTÕES =======
frame_botoes = ttk.Frame(janela)
frame_botoes.pack(pady=10)

# cria botões e liga cada um à sua função
ttk.Button(frame_botoes, text="Adicionar", command=adicionar_agendamento, bootstyle="success").pack(side="left", padx=5)
ttk.Button(frame_botoes, text="Alterar", command=alterar_agendamento, bootstyle="info").pack(side="left", padx=5)
ttk.Button(frame_botoes, text="Apagar", command=apagar_clientes, bootstyle="danger").pack(side="left", padx=5)

# ======= CRIAÇÃO DA TABELA (TREEVIEW) =======
treeview = ttk.Treeview(janela)
treeview.pack(fill="both", expand=True, padx=10, pady=10)

# define as colunas
treeview["columns"] = ("cliente", "horario", "data", "servico")
treeview["show"] = "headings"  # mostra apenas os títulos das colunas

# define os títulos das colunas
treeview.heading("cliente", text="Nome Completo")
treeview.heading("horario", text="Horário")
treeview.heading("data", text="Data")
treeview.heading("servico", text="Serviço")

# define o tamanho e alinhamento de cada coluna
treeview.column("cliente", width=150)
treeview.column("horario", width=120)
treeview.column("data", width=100, anchor="center")
treeview.column("servico", width=200, anchor="center")



# # ======= INSERE ALGUNS EXEMPLOS NA TABELA =======
# treeview.insert("", "end", values=["Maria Benta", "13:30", "31/10/2025", "Luzes"])
# treeview.insert("", "end", values=["Joaquina Cirila", "15:00", "31/10/2025", "Corte"])
# treeview.insert("", "end", values=["Cíntia", "17:00", "31/10/2025", "Mechas rosas"])

        
#isso carrega os agendamentos totais
carregar_agendamentos()






# ======= INICIA O LOOP PRINCIPAL (mantém a janela aberta) =======
janela.mainloop()
