import tkinter as tk
from tkinter import ttk, messagebox
import f1_data
import track_viewer
import threading


class F1Launcher:
    def __init__(self, root):
        self.root = root
        self.root.title("F1 Telemetry System - Setup")
        self.root.geometry("400x600")

        # --- SEÇÃO 1: ANO ---
        lbl_year = tk.Label(root, text="1. Escolha o Ano (Ex: 2021, 2023):", font=("Arial", 10, "bold"))
        lbl_year.pack(pady=5)

        self.entry_year = tk.Entry(root)
        self.entry_year.insert(0, "2023")
        self.entry_year.pack(pady=5)

        btn_races = tk.Button(root, text="Carregar Calendário", command=self.load_races)
        btn_races.pack(pady=5)

        # --- SEÇÃO 2: CORRIDA E SESSÃO ---
        lbl_race = tk.Label(root, text="2. Escolha a Corrida:", font=("Arial", 10, "bold"))
        lbl_race.pack(pady=5)

        self.combo_races = ttk.Combobox(root, state="readonly", width=40)
        self.combo_races.pack(pady=5)

        lbl_session = tk.Label(root, text="Tipo de Sessão:", font=("Arial", 10))
        lbl_session.pack(pady=2)

        self.combo_session = ttk.Combobox(root, state="readonly", values=["R", "Q", "SQ", "FP1"])
        self.combo_session.current(0)  # Seleciona 'R' (Corrida) por padrão
        self.combo_session.pack(pady=5)

        btn_drivers = tk.Button(root, text="Carregar Pilotos Disponíveis", command=self.load_drivers)
        btn_drivers.pack(pady=10)

        # --- SEÇÃO 3: PILOTOS ---
        lbl_drivers = tk.Label(root, text="3. Selecione os Pilotos (Ctrl+Click):", font=("Arial", 10, "bold"))
        lbl_drivers.pack(pady=5)

        # Listbox com scrollbar para multipla seleção
        frame_list = tk.Frame(root)
        frame_list.pack()

        self.list_drivers = tk.Listbox(frame_list, selectmode=tk.MULTIPLE, width=20, height=10)
        self.list_drivers.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollbar = tk.Scrollbar(frame_list)
        scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.list_drivers.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.list_drivers.yview)

        # --- BOTÃO FINAL ---
        btn_start = tk.Button(root, text=">>> INICIAR SIMULAÇÃO <<<", bg="#ff4444", fg="white",
                              font=("Arial", 12, "bold"), command=self.start_app)
        btn_start.pack(pady=20, fill=tk.X, padx=20)

        # Status Label
        self.lbl_status = tk.Label(root, text="Aguardando...", fg="gray")
        self.lbl_status.pack(side=tk.BOTTOM, pady=5)

    def load_races(self):
        year = int(self.entry_year.get())
        self.lbl_status.config(text="Buscando calendário... aguarde.")
        self.root.update()

        # Chama o backend
        races = f1_data.get_schedule(year)

        self.combo_races['values'] = races
        if races:
            self.combo_races.current(0)
            self.lbl_status.config(text=f"Calendário {year} carregado!")
        else:
            self.lbl_status.config(text="Erro ao carregar calendário.")

    def load_drivers(self):
        year = int(self.entry_year.get())
        race = self.combo_races.get()
        session = self.combo_session.get()

        if not race:
            messagebox.showwarning("Aviso", "Selecione uma corrida primeiro.")
            return

        self.lbl_status.config(text="Buscando lista de pilotos... (Baixando dados leves)")
        self.root.update()

        # Chama backend (isso pode demorar uns segundos na primeira vez)
        drivers = f1_data.get_drivers_from_session(year, race, session)

        self.list_drivers.delete(0, tk.END)
        for driver in drivers:
            self.list_drivers.insert(tk.END, driver)

        self.lbl_status.config(text="Pilotos carregados. Selecione e inicie.")

    def start_app(self):
        # Coleta dados
        year = int(self.entry_year.get())
        race = self.combo_races.get()
        session = self.combo_session.get()

        # Pega indices selecionados na lista
        selected_indices = self.list_drivers.curselection()
        selected_drivers = [self.list_drivers.get(i) for i in selected_indices]

        if not selected_drivers:
            messagebox.showwarning("Aviso", "Selecione pelo menos um piloto!")
            return

        self.root.destroy()  # Fecha o menu

        # Inicia a visualização
        print(f"Iniciando: {year} {race} - Pilotos: {selected_drivers}")
        track_viewer.start_visualization(year, race, session, selected_drivers)


if __name__ == "__main__":
    root = tk.Tk()
    app = F1Launcher(root)
    root.mainloop()