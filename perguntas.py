import os
import json
import tkinter as tk
from tkinter import messagebox, ttk
from ttkbootstrap import Style
import random

# Função para salvar o nome do usuário
def save_user_name(user_name):
    user_directory = os.path.expanduser("~/Documents")  # Caminho para a pasta Documentos
    file_path = os.path.join(user_directory, "user_name.txt")
    
    with open(file_path, "w", encoding="utf-8") as file:  # Salvando com UTF-8
        file.write(user_name)

# Função para carregar o nome do usuário
def load_user_name():
    user_directory = os.path.expanduser("~/Documents")
    file_path = os.path.join(user_directory, "user_name.txt")
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:  # Lendo com UTF-8
            return file.read().strip()
    return None

# Função para salvar o score
def save_score(score):
    user_directory = os.path.expanduser("~/Documents")
    file_path = os.path.join(user_directory, "score.txt")
    
    with open(file_path, "w", encoding="utf-8") as file:  # Salvando com UTF-8
        file.write(str(score))

# Função para carregar o score
def load_score():
    user_directory = os.path.expanduser("~/Documents")
    file_path = os.path.join(user_directory, "score.txt")
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:  # Lendo com UTF-8
            return int(file.read().strip())
    return 0

# Função para carregar perguntas de um arquivo JSON
def load_questions():
    user_directory = os.path.expanduser("~/Documents")
    file_path = os.path.join(user_directory, "questions.json")
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:  # Lendo com UTF-8
            return json.load(file)
    else:
        messagebox.showerror("Erro", "Arquivo questions.json não encontrado!")
        return []

# Função para mostrar a pergunta
def show_question(root, question_data, user_name, score_label, unanswered_questions, style):
    # Limpar a janela atual para exibir nova pergunta
    for widget in root.winfo_children():
        widget.destroy()

    question = question_data["question"]
    options = question_data["options"]
    correct_answer = question_data["correct_answer"]

    # Label para o nome do usuário
    question_user = tk.Label(root, text='Nome: ' + user_name, font=("Helvetica", 14), wraplength=600, padx=20, pady=10)
    question_user.pack(anchor='w')

    # Label para a pontuação
    question_score = tk.Label(root, text='Pontos: ' + str(score_label.get()), font=("Helvetica", 14), wraplength=600, padx=20, pady=10)
    question_score.pack(anchor='e')

    # Frame para centralizar a pergunta
    question_frame = tk.Frame(root)
    question_frame.pack(pady=20, padx=20, fill='both', expand=True)

    # Label para a pergunta
    question_label = tk.Label(question_frame, text=question, font=("Helvetica", 16, "bold"), wraplength=600, justify="center")
    question_label.pack(pady=10)

    # Função para lidar com a seleção de resposta
    def handle_response(option):
        if option == correct_answer:
            messagebox.showinfo("Resposta correta", "Resposta correta! +1 ponto!")
            score_label.set(score_label.get() + 1)
        else:
            messagebox.showerror("Resposta incorreta", f"Resposta errada! -3 pontos!\nA resposta correta é: {correct_answer}")
            score_label.set(score_label.get() - 3)

        # Atualizar a pontuação na tela
        question_score.config(text='Pontos: ' + str(score_label.get()))

        # Exibir a próxima pergunta ou finalizar
        if unanswered_questions:
            show_question(root, unanswered_questions.pop(0), user_name, score_label, unanswered_questions, style)
        else:
            save_score(score_label.get())
            messagebox.showinfo("Fim", "Parabéns, você respondeu todas as perguntas!")
            root.quit()

    # Criando botões para as opções de resposta com fonte maior
    for option in options:
        button = ttk.Button(
            question_frame, 
            text=option, 
            style="primary.TButton",
            command=lambda opt=option: handle_response(opt)
        )
        button.pack(pady=5, fill='x')

    # Atualizar a janela para ajustar o tamanho
    root.update_idletasks()
    root.geometry("")  # Resetar o tamanho da janela para se ajustar ao conteúdo

# Função para filtrar perguntas por categoria
def filter_questions_by_category(questions, category):
    if category == "Geral":
        return [q for q in questions if not q.get("answered", False)]
    else:
        return [q for q in questions if q.get("category") == category and not q.get("answered", False)]

# Função para selecionar a categoria
def show_category_selection(user_name):
    # Criar a janela principal
    root = tk.Tk()
    root.title("Jogo de Perguntas")
    style = Style(theme='flatly')  # Tema mais moderno

    # Definir estilo para os botões com fonte maior
    style.configure('primary.TButton', font=("Helvetica", 14))
    style.configure('success.Outline.TButton', font=("Helvetica", 14))

    # Carregar perguntas
    questions = load_questions()
    if not questions:
        print("Não há perguntas disponíveis.")
        return

    def select_category(category):
        unanswered_questions = filter_questions_by_category(questions, category)
        if not unanswered_questions:
            messagebox.showinfo("Informação", "Não há perguntas disponíveis para a categoria selecionada.")
            return
        random.shuffle(unanswered_questions)

        # Carregar a pontuação atual do usuário
        score = tk.IntVar(value=load_score())

        # Exibir a primeira pergunta
        show_question(root, unanswered_questions.pop(0), user_name, score, unanswered_questions, style)

    # Interface de seleção de categoria
    category_label = tk.Label(root, text="Selecione a categoria:", font=("Helvetica", 16), wraplength=600, padx=20, pady=10)
    category_label.pack()

    categories = ["Geral", "Estoque", "PDV"]
    for category in categories:
        button = ttk.Button(
            root, 
            text=category, 
            style="success.Outline.TButton", 
            command=lambda c=category: select_category(c)
        )
        button.pack(pady=10, padx=20, fill='x')

    # Permitir que a janela redimensione conforme necessário
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Iniciar o loop principal da aplicação
    root.mainloop()

# Função principal
def main():
    # Verificar se já temos o nome do usuário salvo
    user_name = load_user_name()

    # Caso o nome não esteja salvo, solicite o nome do usuário
    if not user_name:
        root = tk.Tk()
        root.title("Jogo de Perguntas - Nome do Usuário")
        style = Style(theme='flatly')  # Tema mais moderno

        # Definir estilo para os botões com fonte maior
        style.configure('primary.TButton', font=("Helvetica", 14))

        def save_name():
            user_name_input = entry.get().strip()
            if user_name_input:
                save_user_name(user_name_input)
                root.destroy()  # Fechar a janela de entrada de nome
                show_category_selection(user_name_input)  # Exibir a seleção de categoria
            else:
                messagebox.showwarning("Aviso", "Por favor, insira um nome.")

        entry_label = tk.Label(root, text="Digite seu nome:", font=("Helvetica", 16))
        entry_label.pack(pady=20, padx=20)

        entry = ttk.Entry(root, font=("Helvetica", 14))
        entry.pack(pady=10, padx=20, fill='x')

        entry_button = ttk.Button(root, text="Salvar Nome", style="primary.TButton", command=save_name)
        entry_button.pack(pady=20, padx=20, fill='x')

        # Permitir que a janela redimensione conforme necessário
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        root.mainloop()
    else:
        show_category_selection(user_name)

# Executar a função principal
if __name__ == "__main__":
    main()
