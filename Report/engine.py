import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import sys
import os
import json
import calendar

class MainDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestão - Relatório de Drenagem")
        self.geometry("520x530")
        self.minsize(480, 480)

        # Configuração de estilo visual simples e moderno
        style = ttk.Style()
        style.theme_use("clam")

        self.criar_widgets()

    def criar_widgets(self):
        # Título Principal
        lbl_titulo = tk.Label(
            self, 
            text="Painel de Controle Principal", 
            font=("Arial", 16, "bold"), 
            fg="#001d37"
        )
        lbl_titulo.pack(pady=(15, 5))

        lbl_sub = tk.Label(
            self, 
            text="Informe os dados e selecione o módulo desejado:", 
            font=("Arial", 10), 
            fg="#555555"
        )
        lbl_sub.pack(pady=(0, 15))

        # --- SEÇÃO DO FORMULÁRIO (SEMANA, ANO, MÊS) ---
        frame_form = tk.LabelFrame(
            self, 
            text=" Configurações do Relatório ", 
            font=("Arial", 10, "bold"), 
            fg="#001d37", 
            padx=15, 
            pady=15
        )
        frame_form.pack(fill=tk.X, padx=40, pady=(0, 15))

        # Campo: Semana
        lbl_semana = tk.Label(frame_form, text="Semana:", font=("Arial", 10))
        lbl_semana.grid(row=0, column=0, sticky="w", pady=5)
        self.ent_semana = tk.Entry(frame_form, font=("Arial", 10), width=10)
        self.ent_semana.insert(0, "25")
        self.ent_semana.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # Campo: Ano
        lbl_ano = tk.Label(frame_form, text="Ano:", font=("Arial", 10))
        lbl_ano.grid(row=1, column=0, sticky="w", pady=5)
        self.ent_ano = tk.Entry(frame_form, font=("Arial", 10), width=10)
        self.ent_ano.insert(0, "2026")
        self.ent_ano.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        # Campo: Mês
        lbl_mes = tk.Label(frame_form, text="Mês (1-12):", font=("Arial", 10))
        lbl_mes.grid(row=2, column=0, sticky="w", pady=5)
        self.ent_mes = tk.Entry(frame_form, font=("Arial", 10), width=10)
        self.ent_mes.insert(0, "8")
        self.ent_mes.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        # Botão para Gerar e Salvar JSON
        btn_salvar_json = tk.Button(
            frame_form,
            text="💾 Gerar Arquivo JSON",
            command=self.gerar_json,
            bg="#001d37",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2"
        )
        btn_salvar_json.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        # --- FRAME DE BOTÕES DE MÓDULOS ---
        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill=tk.BOTH, expand=True, padx=40)

        # Botão 1: Conversor do Excel
        btn_converter = tk.Button(
            frame_botoes, 
            text="📊 Executar Conversor (Excel → JSONs)", 
            command=self.abrir_conversor,
            bg="#4a5568", 
            fg="white", 
            font=("Arial", 11, "bold"),
            padx=10, pady=10,
            cursor="hand2"
        )
        btn_converter.pack(fill=tk.X, pady=5)

        # Botão 2: Editor de Mapeamento de Áreas
        btn_editor = tk.Button(
            frame_botoes, 
            text="🗺️ Abrir Editor de Áreas (Ortofoto)", 
            command=self.abrir_editor_areas,
            bg="#21a85a", 
            fg="white", 
            font=("Arial", 11, "bold"),
            padx=10, pady=10,
            cursor="hand2"
        )
        btn_editor.pack(fill=tk.X, pady=5)

        # Rodapé com informações
        lbl_rodape = tk.Label(
            self, 
            text="Dica: Os scripts rodam de forma independente.", 
            font=("Arial", 8, "italic"), 
            fg="#888888"
        )
        lbl_rodape.pack(side=tk.BOTTOM, pady=10)

    def obter_dados_json(self):
        """Valida os campos de texto e constrói o dicionário no formato exigido."""
        try:
            semana = int(self.ent_semana.get().strip())
            ano = int(self.ent_ano.get().strip())
            mes = int(self.ent_mes.get().strip())

            if not (1 <= mes <= 12):
                raise ValueError("O mês deve ser um número entre 1 e 12.")

            # Calcula o último dia do mês e do ano especificados
            ultimo_dia = calendar.monthrange(ano, mes)[1]
            mes_referencia = f"{ano:04d}-{mes:02d}-{ultimo_dia:02d}"

            dados = {
                "data_status": "",
                "semana": semana,
                "ano": ano,
                "mes_referencia": mes_referencia,
                "Empresa": "TERRAM ENGENHARIA DE INFRAESTRUTURA S.A."
            }
            return dados

        except ValueError as e:
            messagebox.showerror("Erro de Validação", f"Verifique os dados inseridos:\n{e}")
            return None

    def gerar_json(self):
        """Salva a estrutura de dados num arquivo .json escolhido pelo usuário."""
        dados = self.obter_dados_json()
        if not dados:
            return

        caminho_arquivo = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os Arquivos", "*.*")],
            title="Salvar arquivo JSON de referência"
        )

        if caminho_arquivo:
            try:
                with open(caminho_arquivo, "w", encoding="utf-8") as f:
                    json.dump(dados, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Sucesso", f"Arquivo salvo com sucesso em:\n{caminho_arquivo}")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo:\n{e}")

    def abrir_conversor(self):
        script_nome = "Engine/converter.py"  # Certifique-se de que o arquivo se chama assim
        self.executar_script(script_nome)

    def abrir_editor_areas(self):
        script_nome = "Engine/Gerador-imagem.py"  # Nome do seu script atualizado
        self.executar_script(script_nome)

    def executar_script(self, nome_arquivo):
        if not os.path.exists(nome_arquivo):
            messagebox.showerror(
                "Erro", 
                f"O arquivo '{nome_arquivo}' não foi encontrado na pasta atual!\nCertifique-se de que ele está no mesmo diretório."
            )
            return
        
        try:
            # Abre o script em um processo separado usando o mesmo interpretador python ativo
            subprocess.Popen([sys.executable, nome_arquivo])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o script:\n{e}")

if __name__ == "__main__":
    app = MainDashboard()
    app.mainloop()
