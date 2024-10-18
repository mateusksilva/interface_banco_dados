import tkinter as tk
from tkinter import ttk, font, messagebox
from PIL import Image, ImageTk
import sqlite3

# Função para conectar ao banco de dados
def conectar_bd():
    conn = sqlite3.connect('tarefas.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tarefas (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 tarefa TEXT NOT NULL)''')
    conn.commit()
    return conn

# Função para carregar as tarefas do banco de dados
def carregar_tarefas():
    conn = conectar_bd()
    c = conn.cursor()
    c.execute("SELECT * FROM tarefas")
    todas_tarefas = c.fetchall()
    for tarefa in todas_tarefas:
        adicionar_item_tarefas(tarefa[1])
    conn.close()

# Função para adicionar tarefas ao banco de dados
def adicionar_tarefas_bd(tarefa):
    conn = conectar_bd()
    c = conn.cursor()
    c.execute("INSERT INTO tarefas (tarefa) VALUES (?)", (tarefa,))
    conn.commit()
    conn.close()

# Função para deletar tarefas do banco de dados
def deletar_tarefas_bd(tarefa_texto):
    conn = conectar_bd()
    c = conn.cursor()
    c.execute("DELETE FROM tarefas WHERE tarefa = ?", (tarefa_texto,))
    conn.commit()
    conn.close()

# Função para atualizar tarefas no banco de dados
def atualizar_tarefas_bd(tarefa_antiga, tarefa_nova):
    conn = conectar_bd()
    c = conn.cursor()
    c.execute("UPDATE tarefas SET tarefa = ? WHERE tarefa = ?", (tarefa_nova, tarefa_antiga))
    conn.commit()
    conn.close()

# Variável global para rastrear a tarefa em edição
tarefa_em_edicao = None
frame_em_edicao = None

# Função para adicionar tarefas na interface e no banco de dados
def adicionar_tarefas():
    global frame_em_edicao, tarefa_em_edicao
    tarefa = entrada_tarefa.get().strip()
    
    if tarefa and tarefa != 'escreva sua tarefa aqui':
        if frame_em_edicao is not None:
            atualizar_tarefas_bd(tarefa_em_edicao, tarefa)  # Atualiza no banco de dados
            # Atualiza a tarefa na interface
            label_tarefa = frame_em_edicao.children['!label']
            label_tarefa.config(text=tarefa)  # Atualiza o texto da tarefa na interface
            frame_em_edicao = None
            entrada_tarefa.delete(0, tk.END)  # Limpa a entrada
        else:
            adicionar_item_tarefas(tarefa)
            adicionar_tarefas_bd(tarefa)  # Salva no banco de dados
            entrada_tarefa.delete(0, tk.END)
    else:
        messagebox.showwarning('Entrada Inválida', 'Por favor, insira uma tarefa')

# Função para preparar a edição de uma tarefa
def prepara_edicao(frame_tarefa, label_tarefa):
    global frame_em_edicao, tarefa_em_edicao
    entrada_tarefa.delete(0, tk.END)  # Limpa a entrada de tarefa
    entrada_tarefa.insert(0, label_tarefa.cget('text'))  # Insere o texto da tarefa na entrada
    frame_em_edicao = frame_tarefa
    tarefa_em_edicao = label_tarefa.cget('text')  # Armazena a tarefa atual para referência

# Função para adicionar tarefas na lista (parte visual)
def adicionar_item_tarefas(tarefa):
    frame_tarefa = tk.Frame(cnavas_interior, bg='white', bd=1, relief=tk.SOLID)
    label_tarefa = tk.Label(frame_tarefa, text=tarefa, font=('Garamond', 16), bg='white', width=25, height=2, anchor='w')
    label_tarefa.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=5)

    botao_edita = tk.Button(frame_tarefa, image=icon_editar, command=lambda f=frame_tarefa, l=label_tarefa: prepara_edicao(f, l), bg='white', width=25, relief=tk.FLAT)
    botao_edita.pack(side=tk.RIGHT, padx=5)

    botao_deletar = tk.Button(frame_tarefa, image=icon_deletar, command=lambda f=frame_tarefa, l=label_tarefa: deletar_tarefas(f, l), bg='white', width=25, relief=tk.FLAT)
    botao_deletar.pack(side=tk.RIGHT, padx=5)

    frame_tarefa.pack(fill=tk.X, padx=5, pady=5)
    checkbutton = ttk.Checkbutton(frame_tarefa, command=lambda label=label_tarefa: altera_sublinhado(label))
    checkbutton.pack(side=tk.RIGHT, padx=5)

    cnavas_interior.update_idletasks()
    canvas.config(scrollregion=canvas.bbox('all'))

# Função para deletar tarefas na interface e no banco de dados
def deletar_tarefas(frame_tarefa, label_tarefa):
    deletar_tarefas_bd(label_tarefa.cget('text'))  # Deletar do banco de dados
    frame_tarefa.destroy()
    cnavas_interior.update_idletasks()
    canvas.config(scrollregion=canvas.bbox('all'))

# Ao iniciar o programa, carregar as tarefas salvas
def altera_sublinhado(label):
    fonte_atual = label.cget('font')
    if 'overstrike' in fonte_atual:
        nova_fonrte = fonte_atual.replace(' overstrike', '')
    else:
        nova_fonrte = fonte_atual + ' overstrike'
    label.config(font=nova_fonrte)

# Configuração da janela principal
janala = tk.Tk()
janala.title('Meu App De Tarefas')
janala.configure(bg='#C0C0C0')
janala.geometry('500x600')

# Carregar a imagem e redimensioná-la proporcionalmente
imagem_editar = Image.open('editar.png')
imagem_editar = imagem_editar.resize((25, 25), Image.LANCZOS)  # Ajuste o tamanho proporcionalmente
icon_editar = ImageTk.PhotoImage(imagem_editar)

imagem_deletar = Image.open('lixo.png')
imagem_deletar = imagem_deletar.resize((25, 25), Image.LANCZOS)
icon_deletar = ImageTk.PhotoImage(imagem_deletar)

# Título
fonte_cabecalho = font.Font(family='Garamond', size=24, weight='bold')
rotulo_cabecalho = tk.Label(janala, text='Meu App De Tarefas', pady=20, font=fonte_cabecalho, bg='#C0C0C0', fg='#333').pack()

frame = tk.Frame(janala, bg='#C0C0C0')
frame.pack(pady=10)
entrada_tarefa = tk.Entry(frame, font=('Garamond', 14), relief=tk.FLAT, bg='white', fg='gray', width=30)
entrada_tarefa.pack(side=tk.LEFT, padx=10)
butao_adicionar = tk.Button(frame, command=adicionar_tarefas, text='Adicionar Tarefas', bg='#908ef5', fg='white', height=1, width=15, font=('Roboto', 11), relief=tk.FLAT)
butao_adicionar.pack(side=tk.LEFT, padx=10)

# Criar um frame para lista de tarefas com rolagem
frame_lista_tarefas = tk.Frame(janala, bg='white')
frame_lista_tarefas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

canvas = tk.Canvas(frame_lista_tarefas, bg='white')
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrool_bar = ttk.Scrollbar(frame_lista_tarefas, orient='vertical', command=canvas.yview)
scrool_bar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.config(yscrollcommand=scrool_bar.set)
cnavas_interior = tk.Frame(canvas, bg='white')
canvas.create_window((0, 0), window=cnavas_interior, anchor='nw')
cnavas_interior.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
carregar_tarefas()
janala.mainloop()
