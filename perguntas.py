import os
import json
import tkinter as tk
from tkinter import messagebox, ttk
from ttkbootstrap import Style
import random
import requests

# Função para salvar o nome do usuário
def save_user_name(user_name):
    user_directory = os.path.expanduser("~/Documents")
    file_path = os.path.join(user_directory, "user_name.txt")
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(user_name)

# Função para carregar o nome do usuário
def load_user_name():
    user_directory = os.path.expanduser("~/Documents")
    file_path = os.path.join(user_directory, "user_name.txt")
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    return None

# Função para salvar o score
def save_score(score):
    user_directory = os.path.expanduser("~/Documents")
    file_path = os.path.join(user_directory, "score.txt")
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(str(score))

# Função para carregar o score
def load_score():
    user_directory = os.path.expanduser("~/Documents")
    file_path = os.path.join(user_directory, "score.txt")
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return int(file.read().strip())
    return 0

# Função para carregar perguntas da URL do GitHub
def load_questions():
    url = "https://raw.githubusercontent.com/DevRGS/Questions/refs/heads/main/questions.json"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível carregar as perguntas da internet.\nVerifique sua conexão.\n\nErro: {e}")
        return []
    except json.JSONDecodeError:
        messagebox.showerror("Erro de Formato", "O arquivo de perguntas online parece estar corrompido (formato JSON inválido).")
        return []

# Função para mostrar a pergunta
def show_question(root, question_data, user_name, score_label, unanswered_questions, style):
    for widget in root.winfo_children():
        widget.destroy()

    question = question_data["question"]
    options = question_data["options"]
    correct_answer = question_data["correct_answer"]
    
    random.shuffle(options)

    question_user = tk.Label(root, text='Nome: ' + user_name, font=("Helvetica", 14), wraplength=600, padx=20, pady=10)
    question_user.pack(anchor='w')

    question_score = tk.Label(root, text='Pontos: ' + str(score_label.get()), font=("Helvetica", 14), wraplength=600, padx=20, pady=10)
    question_score.pack(anchor='e')

    question_frame = tk.Frame(root)
    question_frame.pack(pady=20, padx=20, fill='both', expand=True)

    question_label = tk.Label(question_frame, text=question, font=("Helvetica", 16, "bold"), wraplength=600, justify="center")
    question_label.pack(pady=10)

    def handle_response(option):
        if option == correct_answer:
            messagebox.showinfo("Resposta correta", "Resposta correta! +1 ponto!")
            score_label.set(score_label.get() + 1)
        else:
            messagebox.showerror("Resposta incorreta", f"Resposta errada! -3 pontos!\nA resposta correta é: {correct_answer}")
            score_label.set(score_label.get() - 3)

        question_score.config(text='Pontos: ' + str(score_label.get()))

        if unanswered_questions:
            show_question(root, unanswered_questions.pop(0), user_name, score_label, unanswered_questions, style)
        else:
            save_score(score_label.get())
            messagebox.showinfo("Fim", "Parabéns, você respondeu todas as perguntas!")
            root.quit()

    for option in options:
        button = ttk.Button(
            question_frame, 
            text=option, 
            style="primary.TButton",
            command=lambda opt=option: handle_response(opt)
        )
        button.pack(pady=5, fill='x')

    root.update_idletasks()
    root.geometry("")

# Função para filtrar perguntas por categoria
def filter_questions_by_category(questions, category):
    if category == "Geral":
        return [q for q in questions if not q.get("answered", False)]
    else:
        return [q for q in questions if q.get("category") == category and not q.get("answered", False)]

# Função para selecionar a categoria (MODIFICADA COM SCROLLBAR)
def show_category_selection(user_name):
    root = tk.Tk()
    root.title("Jogo de Perguntas")
    root.geometry("500x400") # Define um tamanho inicial para a janela
    style = Style(theme='flatly')

    style.configure('primary.TButton', font=("Helvetica", 14))
    style.configure('success.Outline.TButton', font=("Helvetica", 14))

    questions = load_questions()
    if not questions:
        print("Não foi possível carregar as perguntas. Encerrando o programa.")
        root.destroy()
        return

    # --- INÍCIO DAS MODIFICAÇÕES PARA O SCROLL ---
    
    # 1. Cria um frame principal para organizar o canvas e a scrollbar
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=1)

    # 2. Cria um Canvas
    my_canvas = tk.Canvas(main_frame)
    my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # 3. Adiciona uma Scrollbar ao frame principal
    my_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=my_canvas.yview)
    my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # 4. Configura o Canvas para usar a scrollbar
    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
    
    # --- Adiciona rolagem com a roda do mouse ---
    def _on_mouse_wheel(event):
        my_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    my_canvas.bind_all("<MouseWheel>", _on_mouse_wheel)


    # 5. Cria OUTRO frame DENTRO do Canvas. É neste frame que os botões serão colocados.
    second_frame = tk.Frame(my_canvas)

    # 6. Adiciona o novo frame ao Canvas
    my_canvas.create_window((0, 0), window=second_frame, anchor="nw")

    # --- FIM DAS MODIFICAÇÕES PARA O SCROLL ---


    def select_category(category):
        # Para a transição de janelas, destruímos o frame principal e o canvas
        main_frame.destroy()
        my_canvas.destroy()
        
        unanswered_questions = filter_questions_by_category(questions, category)
        if not unanswered_questions:
            messagebox.showinfo("Informação", "Não há perguntas disponíveis para a categoria selecionada.")
            root.quit()
            return
        random.shuffle(unanswered_questions)

        score = tk.IntVar(value=load_score())
        show_question(root, unanswered_questions.pop(0), user_name, score, unanswered_questions, style)

    # AGORA, os widgets são adicionados ao 'second_frame', e não mais a 'root'
    category_label = tk.Label(second_frame, text="Selecione a categoria:", font=("Helvetica", 16), wraplength=600, padx=20, pady=10)
    category_label.pack()

    categories = ["Geral"] + sorted(list(set(q['category'] for q in questions if 'category' in q)))
    
    for category in categories:
        button = ttk.Button(
            second_frame, # Adicionado ao frame rolável
            text=category, 
            style="success.Outline.TButton", 
            command=lambda c=category: select_category(c)
        )
        button.pack(pady=10, padx=20, fill='x')

    root.mainloop()

# Função principal
def main():
    user_name = load_user_name()

    if not user_name:
        root = tk.Tk()
        root.title("Jogo de Perguntas - Nome do Usuário")
        style = Style(theme='flatly')

        style.configure('primary.TButton', font=("Helvetica", 14))

        def save_name():
            user_name_input = entry.get().strip()
            if user_name_input:
                save_user_name(user_name_input)
                root.destroy()
                show_category_selection(user_name_input)
            else:
                messagebox.showwarning("Aviso", "Por favor, insira um nome.")

        entry_label = tk.Label(root, text="Digite seu nome:", font=("Helvetica", 16))
        entry_label.pack(pady=20, padx=20)

        entry = ttk.Entry(root, font=("Helvetica", 14))
        entry.pack(pady=10, padx=20, fill='x')

        entry_button = ttk.Button(root, text="Salvar Nome", style="primary.TButton", command=save_name)
        entry_button.pack(pady=20, padx=20, fill='x')

        root.mainloop()
    else:
        show_category_selection(user_name)

if __name__ == "__main__":
    main()
