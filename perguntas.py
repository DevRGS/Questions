import os
import json
import tkinter as tk
from tkinter import messagebox, ttk
from ttkbootstrap import Style
import random
import requests
import math # <-- Importado para cálculos de XP

# --- NOVAS FUNÇÕES PARA PROGRESSÃO DO USUÁRIO ---

# Função para carregar o progresso do usuário (XP e Nível)
def load_user_progress():
    user_directory = os.path.expanduser("~/Documents")
    file_path = os.path.join(user_directory, "user_progress.json")
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        # Retorna valores padrão se o arquivo não existir
        return {"xp": 0, "level": 1}

# Função para salvar o progresso do usuário
def save_user_progress(progress_data):
    user_directory = os.path.expanduser("~/Documents")
    file_path = os.path.join(user_directory, "user_progress.json")
    
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(progress_data, file, indent=4)

# Função para calcular o nível com base no XP e o XP necessário para o próximo
def calculate_level_info(xp):
    level = math.floor(0.1 * math.sqrt(xp)) + 1
    xp_for_next_level = int(((level) / 0.1) ** 2)
    return level, xp_for_next_level

# --- Funções existentes (sem grandes alterações) ---

def save_user_name(user_name):
    user_directory = os.path.expanduser("~/Documents")
    file_path = os.path.join(user_directory, "user_name.txt")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(user_name)

def load_user_name():
    user_directory = os.path.expanduser("~/Documents")
    file_path = os.path.join(user_directory, "user_name.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    return None

def save_score(score):
    user_directory = os.path.expanduser("~/Documents")
    file_path = os.path.join(user_directory, "score.txt")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(str(score))

def load_score():
    user_directory = os.path.expanduser("~/Documents")
    file_path = os.path.join(user_directory, "score.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return int(file.read().strip())
    return 0

def load_questions():
    url = "https://raw.githubusercontent.com/DevRGS/Questions/refs/heads/main/questions.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível carregar as perguntas da internet.\n\nErro: {e}")
        return []
    except json.JSONDecodeError:
        messagebox.showerror("Erro de Formato", "O arquivo de perguntas online não está em um formato JSON válido.")
        return []

# --- FUNÇÃO SHOW_QUESTION MODIFICADA PARA INCLUIR O CRONÔMETRO E XP ---
# --- FUNÇÃO SHOW_QUESTION MODIFICADA PARA QUEBRA DE LINHA AUTOMÁTICA ---
def show_question(root, question_data, user_name, score_label, unanswered_questions, style):
    # Limpa a janela de widgets antigos
    for widget in root.winfo_children():
        widget.destroy()

    # Carrega o progresso do usuário e calcula o nível
    user_progress = load_user_progress()
    current_level, xp_for_next = calculate_level_info(user_progress['xp'])

    # Constantes do jogo
    QUESTION_TIME = 20
    XP_PER_CORRECT = 15

    # Extrai os dados da pergunta
    question = question_data["question"]
    options = question_data["options"]
    correct_answer = question_data["correct_answer"]
    random.shuffle(options)

    # --- Criação dos Widgets (igual ao código anterior) ---

    # Frame de informações do topo
    top_info_frame = tk.Frame(root)
    top_info_frame.pack(fill='x', padx=20, pady=10)
    tk.Label(top_info_frame, text=f'Nome: {user_name}', font=("Helvetica", 12)).pack(side='left')
    tk.Label(top_info_frame, text=f'Pontos: {score_label.get()}', font=("Helvetica", 12)).pack(side='right')
    tk.Label(top_info_frame, text=f"Level: {current_level} (XP: {user_progress['xp']}/{xp_for_next})", font=("Helvetica", 12, "bold")).pack(side='right', padx=20)
    
    # Frame principal da pergunta
    question_frame = tk.Frame(root)
    question_frame.pack(pady=20, padx=20, fill='both', expand=True)

    # Label da pergunta com quebra de linha
    tk.Label(question_frame, text=question, font=("Helvetica", 16, "bold"), wraplength=450, justify="center").pack(pady=10)

    # Lógica e UI do Cronômetro
    time_left = tk.IntVar(value=QUESTION_TIME)
    timer_id = None
    progress_bar = ttk.Progressbar(question_frame, orient='horizontal', mode='determinate', maximum=QUESTION_TIME, length=300)
    progress_bar.pack(pady=10)
    progress_bar['value'] = QUESTION_TIME
    timer_label = tk.Label(question_frame, text=f"Tempo: {time_left.get()}", font=("Helvetica", 14, "italic"))
    timer_label.pack(pady=5)
    
    # Funções internas (update_timer, handle_response, next_question)
    def update_timer():
        nonlocal timer_id
        current_time = time_left.get()
        if current_time > 0:
            time_left.set(current_time - 1)
            timer_label.config(text=f"Tempo: {time_left.get()}")
            progress_bar['value'] = time_left.get()
            timer_id = root.after(1000, update_timer)
        else:
            messagebox.showwarning("Tempo Esgotado!", "O tempo para responder acabou. -3 pontos!")
            score_label.set(score_label.get() - 3)
            next_question()

    def handle_response(option):
        if timer_id:
            root.after_cancel(timer_id)
        if option == correct_answer:
            messagebox.showinfo("Resposta Correta", f"Resposta correta! +1 ponto e +{XP_PER_CORRECT} XP!")
            score_label.set(score_label.get() + 1)
            progress = load_user_progress()
            old_level, _ = calculate_level_info(progress['xp'])
            progress['xp'] += XP_PER_CORRECT
            new_level, _ = calculate_level_info(progress['xp'])
            save_user_progress(progress)
            if new_level > old_level:
                messagebox.showinfo("Level Up!", f"Parabéns, você alcançou o Level {new_level}!")
        else:
            messagebox.showerror("Resposta Incorreta", f"Resposta errada! -3 pontos!\nA resposta correta é: {correct_answer}")
            score_label.set(score_label.get() - 3)
        next_question()

    def next_question():
        if unanswered_questions:
            show_question(root, unanswered_questions.pop(0), user_name, score_label, unanswered_questions, style)
        else:
            save_score(score_label.get())
            messagebox.showinfo("Fim", "Parabéns, você respondeu todas as perguntas!")
            root.quit()
    
    # Criação dos botões de resposta com quebra de linha
    for option in options:
        button = tk.Button(
            question_frame, text=option, font=("Helvetica", 12), wraplength=450,
            justify="center", command=lambda opt=option: handle_response(opt),
            bg="#2C3E50", fg="white", relief="flat", padx=10, pady=10
        )
        button.pack(pady=5, fill='x')

    # --- NOVA SEÇÃO PARA AJUSTAR E CENTRALIZAR A JANELA ---
    # Garante que todos os widgets estão no lugar antes de calcular o tamanho
    root.update_idletasks()

    # Calcula a largura e altura necessárias para exibir todo o conteúdo
    required_width = root.winfo_reqwidth()
    required_height = root.winfo_reqheight()

    # Pega as dimensões da tela
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calcula a posição para centralizar a janela
    position_x = (screen_width // 2) - (required_width // 2)
    position_y = (screen_height // 2) - (required_height // 2)

    # Define a nova geometria da janela (tamanho + posição)
    root.geometry(f"{required_width}x{required_height}+{position_x}+{position_y}")
    # --- FIM DA NOVA SEÇÃO ---

    # Inicia o cronômetro
    timer_id = root.after(1000, update_timer)

def filter_questions_by_category(questions, category):
    if category == "Geral":
        return questions
    else:
        return [q for q in questions if q.get("category") == category]

# Função de seleção de categoria (sem grandes alterações)
def show_category_selection(user_name):
    # O restante do código, como a tela de seleção de categoria e a função main,
    # permanece praticamente o mesmo.
    root = tk.Tk()
    root.title("Jogo de Perguntas")
    root.geometry("500x400")
    style = Style(theme='flatly')

    style.configure('primary.TButton', font=("Helvetica", 14))
    style.configure('success.Outline.TButton', font=("Helvetica", 14))

    questions = load_questions()
    if not questions:
        root.destroy()
        return

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=1)

    my_canvas = tk.Canvas(main_frame)
    my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    my_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=my_canvas.yview)
    my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
    
    def _on_mouse_wheel(event):
        my_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    my_canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

    second_frame = tk.Frame(my_canvas)
    my_canvas.create_window((0, 0), window=second_frame, anchor="nw")

    def select_category(category):
        main_frame.destroy()
        my_canvas.destroy()
        
        filtered_questions = filter_questions_by_category(questions, category)
        if not filtered_questions:
            messagebox.showinfo("Informação", "Não há perguntas disponíveis para a categoria selecionada.")
            root.quit()
            return
        random.shuffle(filtered_questions)

        score = tk.IntVar(value=load_score())
        show_question(root, filtered_questions.pop(0), user_name, score, filtered_questions, style)

    category_label = tk.Label(second_frame, text="Selecione a categoria:", font=("Helvetica", 16), wraplength=600, padx=20, pady=10)
    category_label.pack()

    categories = ["Geral"] + sorted(list(set(q['category'] for q in questions if 'category' in q)))
    
    for category in categories:
        button = ttk.Button(
            second_frame, 
            text=category, 
            style="success.Outline.TButton", 
            command=lambda c=category: select_category(c)
        )
        button.pack(pady=10, padx=20, fill='x')

    root.mainloop()

# Função main (sem alterações)
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
