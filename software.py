# Sistema de Análises de Laboratório com layout melhorado e tema de laboratório
import sqlite3
from datetime import datetime
import os
import tkinter as tk
from tkinter import messagebox, ttk

# Criar pasta de dados se não existir
if not os.path.exists("data"):
    os.makedirs("data")

# Banco de dados
conn = sqlite3.connect("data/lab_system.db")
c = conn.cursor()

# Criar tabelas
c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    usuario TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS amostras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    origem TEXT NOT NULL,
    tipo_analise TEXT NOT NULL,
    diluicao TEXT,
    volume_aliquota TEXT,
    resultado REAL,
    id_usuario INTEGER,
    FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
)''')

conn.commit()

# Cores do tema
COR_FUNDO = "#e6f2ff"  # azul claro
COR_BOTAO = "#007acc"
COR_TEXTO = "#003366"
FONTE_TITULO = ("Arial", 14, "bold")
FONTE_NORMAL = ("Arial", 10)

# Interface gráfica principal
class LabApp:
    def __init__(self, master):
        self.master = master
        master.title("Sistema de Laboratório")
        master.geometry("400x300")
        master.configure(bg=COR_FUNDO)
        self.user_id = None

        self.frame_inicio()

    def limpar_frame(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def frame_inicio(self):
        self.limpar_frame()
        tk.Label(self.master, text="Bem-vindo ao sistema", font=FONTE_TITULO, bg=COR_FUNDO, fg=COR_TEXTO).pack(pady=10)
        tk.Button(self.master, text="Cadastrar Usuário", bg=COR_BOTAO, fg="white", command=self.cadastrar_usuario).pack(pady=5)
        tk.Button(self.master, text="Login", bg=COR_BOTAO, fg="white", command=self.login).pack(pady=5)
        tk.Button(self.master, text="Sair", bg="red", fg="white", command=self.master.quit).pack(pady=5)

    def frame_usuario(self):
        self.limpar_frame()
        tk.Label(self.master, text="Menu do Usuário", font=FONTE_TITULO, bg=COR_FUNDO, fg=COR_TEXTO).pack(pady=10)
        tk.Button(self.master, text="Nova Amostra", bg=COR_BOTAO, fg="white", command=self.janela_nova_amostra).pack(pady=5)
        tk.Button(self.master, text="Consultar Resultados", bg=COR_BOTAO, fg="white", command=self.consultar_resultados).pack(pady=5)
        tk.Button(self.master, text="Logout", bg="gray", fg="white", command=self.frame_inicio).pack(pady=20)

    def cadastrar_usuario(self):
        def salvar():
            nome = e_nome.get()
            usuario = e_usuario.get()
            senha = e_senha.get()
            if not nome or not usuario or not senha:
                messagebox.showinfo("Erro", "Preencha todos os campos!")
                return
            try:
                c.execute("INSERT INTO usuarios (nome, usuario, senha) VALUES (?, ?, ?)", (nome, usuario, senha))
                conn.commit()
                messagebox.showinfo("Sucesso", "Usuário cadastrado!")
                win.destroy()
            except sqlite3.IntegrityError:
                messagebox.showinfo("Erro", "Usuário já existe!")

        win = tk.Toplevel(bg=COR_FUNDO)
        win.title("Cadastro de Usuário")
        for i, texto in enumerate(["Nome:", "Usuário:", "Senha:"]):
            tk.Label(win, text=texto, bg=COR_FUNDO, fg=COR_TEXTO).grid(row=i, column=0, sticky="e", padx=5, pady=2)
        e_nome = tk.Entry(win)
        e_usuario = tk.Entry(win)
        e_senha = tk.Entry(win, show="*")
        e_nome.grid(row=0, column=1, pady=2)
        e_usuario.grid(row=1, column=1, pady=2)
        e_senha.grid(row=2, column=1, pady=2)
        tk.Button(win, text="Cadastrar", bg=COR_BOTAO, fg="white", command=salvar).grid(row=3, columnspan=2, pady=10)

    def login(self):
        def autenticar():
            usuario = e_usuario.get()
            senha = e_senha.get()
            c.execute("SELECT id FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
            resultado = c.fetchone()
            if resultado:
                self.user_id = resultado[0]
                messagebox.showinfo("Login", "Sucesso!")
                win.destroy()
                self.frame_usuario()
            else:
                messagebox.showinfo("Erro", "Usuário ou senha incorretos")

        win = tk.Toplevel(bg=COR_FUNDO)
        win.title("Login")
        tk.Label(win, text="Usuário:", bg=COR_FUNDO, fg=COR_TEXTO).grid(row=0, column=0, sticky="e", padx=5, pady=2)
        tk.Label(win, text="Senha:", bg=COR_FUNDO, fg=COR_TEXTO).grid(row=1, column=0, sticky="e", padx=5, pady=2)
        e_usuario = tk.Entry(win)
        e_senha = tk.Entry(win, show="*")
        e_usuario.grid(row=0, column=1, pady=2)
        e_senha.grid(row=1, column=1, pady=2)
        tk.Button(win, text="Entrar", bg=COR_BOTAO, fg="white", command=autenticar).grid(row=2, columnspan=2, pady=10)

    def janela_nova_amostra(self):
        win = tk.Toplevel(bg=COR_FUNDO)
        win.title("Nova Amostra")
        campos = ["Data (dd/mm/aaaa):", "Origem:", "Tipo de Análise:", "Diluição:", "Volume da Alíquota:", "Resultado:"]
        entradas = []

        for i, campo in enumerate(campos):
            tk.Label(win, text=campo, bg=COR_FUNDO, fg=COR_TEXTO).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            entry = tk.Entry(win)
            entry.grid(row=i, column=1, pady=2)
            entradas.append(entry)

        def salvar():
            data, origem, tipo, diluicao, volume, resultado = [e.get() for e in entradas]
            try:
                datetime.strptime(data, "%d/%m/%Y")
                c.execute("INSERT INTO amostras (data, origem, tipo_analise, diluicao, volume_aliquota, resultado, id_usuario) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (data, origem, tipo, diluicao, volume, resultado, self.user_id))
                conn.commit()
                messagebox.showinfo("Sucesso", "Amostra registrada!")
                win.destroy()
            except ValueError:
                messagebox.showinfo("Erro", "Data inválida! Use o formato dd/mm/aaaa")

        tk.Button(win, text="Salvar", bg=COR_BOTAO, fg="white", command=salvar).grid(row=len(campos), columnspan=2, pady=10)

    def consultar_resultados(self):
        win = tk.Toplevel(bg=COR_FUNDO)
        win.title("Resultados")

        filtro_frame = tk.Frame(win, bg=COR_FUNDO)
        filtro_frame.pack(pady=5)

        tk.Label(filtro_frame, text="Filtrar por data (dd/mm/aaaa):", bg=COR_FUNDO, fg=COR_TEXTO).pack(side="left")
        data_entry = tk.Entry(filtro_frame)
        data_entry.pack(side="left", padx=5)

        tree = ttk.Treeview(win, columns=("ID", "Data", "Origem", "Tipo", "Resultado"), show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill="both", expand=True)

        def carregar_dados(data_filtro=None):
            tree.delete(*tree.get_children())
            if data_filtro:
                c.execute('''SELECT id, data, origem, tipo_analise, resultado FROM amostras WHERE id_usuario = ? AND data = ?''',
                          (self.user_id, data_filtro))
            else:
                c.execute('''SELECT id, data, origem, tipo_analise, resultado FROM amostras WHERE id_usuario = ?''',
                          (self.user_id,))
            for row in c.fetchall():
                tree.insert("", "end", values=row)

        def aplicar_filtro():
            data = data_entry.get()
            if data:
                try:
                    datetime.strptime(data, "%d/%m/%Y")
                    carregar_dados(data)
                except ValueError:
                    messagebox.showinfo("Erro", "Data inválida!")
            else:
                carregar_dados()

        tk.Button(filtro_frame, text="Aplicar Filtro", bg=COR_BOTAO, fg="white", command=aplicar_filtro).pack(side="left", padx=5)

        carregar_dados()

if __name__ == "__main__":
    root = tk.Tk()
    app = LabApp(root)
    root.mainloop()
    conn.close()
