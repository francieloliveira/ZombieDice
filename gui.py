"""Protótipo Tkinter para jogar Zombie Dice usando a lógica de ``jogo``."""

import json
import random
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog

import jogo


SAVE_PATH = Path(__file__).with_name("partida_gui.json")
CORES = {"Verde": "#5a9b55", "Amarelo": "#d6ad32", "Vermelho": "#c94d4d"}
NOMES_FACE = {jogo.CEREBRO: "Cérebro", jogo.PASSO: "Passos", jogo.TIRO: "Tiro"}


def _json_tuplas(valor):
    """Converte listas do JSON de volta para tuplas no estado do gerador."""
    if isinstance(valor, list):
        return tuple(_json_tuplas(item) for item in valor)
    return valor


def salvar_partida(partida, caminho=SAVE_PATH):
    estado = {
        "jogadores": partida.jogadores,
        "placar": partida.placar,
        "copo": [jogo.cor_do_dado(dado) for dado in partida.copo],
        "vencedor": partida.vencedor,
        "eliminados": partida.eliminados,
        "jogados": sorted(partida.jogados),
        "jogador_atual": partida.jogador_atual,
        "turno": partida.turno,
        "dados_passo": [jogo.cor_do_dado(dado) for dado in partida.dados_passo],
        "rng": partida.random.getstate(),
    }
    caminho.write_text(json.dumps(estado, ensure_ascii=False), encoding="utf-8")


def carregar_partida(caminho=SAVE_PATH):
    estado = json.loads(caminho.read_text(encoding="utf-8"))
    gerador = random.Random()
    gerador.setstate(_json_tuplas(estado["rng"]))
    partida = jogo.Partida(estado["jogadores"], random=gerador)
    dados_por_cor = {
        "Verde": jogo.DADO_VERDE,
        "Amarelo": jogo.DADO_AMARELO,
        "Vermelho": jogo.DADO_VERMELHO,
    }
    partida.placar = estado["placar"]
    partida.copo = [dados_por_cor[cor] for cor in estado["copo"]]
    partida.vencedor = estado["vencedor"]
    partida.eliminados = estado["eliminados"]
    partida.jogados = set(estado["jogados"])
    partida.jogador_atual = estado["jogador_atual"]
    partida.turno = estado["turno"]
    partida.dados_passo = [dados_por_cor[cor] for cor in estado["dados_passo"]]
    return partida


class TelaTurno:
    def __init__(self, root):
        self.root = root
        self.root.title("Zombie Dice — turno")
        self.partida = None
        self.resultado = None
        self.status = tk.StringVar(value="Inicie uma partida ou retome uma salva.")
        self._montar()
        self._oferecer_retomar()

    def _montar(self):
        tk.Label(self.root, text="Zombie Dice", font=("TkDefaultFont", 20, "bold")).pack(pady=8)
        self.status_label = tk.Label(self.root, textvariable=self.status, font=("TkDefaultFont", 13))
        self.status_label.pack(pady=4)
        self.dados = tk.Frame(self.root)
        self.dados.pack(pady=10)
        self.placar = tk.Label(self.root, text="", justify="left", font=("TkDefaultFont", 12))
        self.placar.pack(pady=8)
        botoes = tk.Frame(self.root)
        botoes.pack(pady=8)
        self.roll_button = tk.Button(botoes, text="Rolar", command=self.rolar, state="disabled")
        self.roll_button.pack(side="left", padx=5)
        self.stop_button = tk.Button(botoes, text="Parar", command=self.parar, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        tk.Button(botoes, text="Interromper", command=self.interromper).pack(side="left", padx=5)
        self.start_button = tk.Button(self.root, text="Nova partida", command=self.nova_partida)
        self.start_button.pack(pady=4)

    def _oferecer_retomar(self):
        if SAVE_PATH.exists() and messagebox.askyesno("Partida salva", "Deseja retomar a partida salva?"):
            try:
                self.partida = carregar_partida()
                self._atualizar()
                self._preparar_vez()
            except (OSError, ValueError, KeyError, TypeError) as erro:
                messagebox.showerror("Erro ao retomar", str(erro))

    def nova_partida(self):
        nomes = simpledialog.askstring("Jogadores", "Nomes separados por vírgula (mínimo 2):")
        if nomes is None:
            return
        jogadores = [nome.strip() for nome in nomes.split(",") if nome.strip()]
        try:
            self.partida = jogo.Partida(jogadores, random=random.Random())
        except ValueError as erro:
            messagebox.showerror("Jogadores inválidos", str(erro))
            return
        self.resultado = None
        self._atualizar()
        self._preparar_vez()

    def _preparar_vez(self):
        p = self.partida
        if p is None:
            return
        if p.vencedor:
            self.status.set("Vencedor: " + p.vencedor)
            self.roll_button.config(state="disabled")
            self.stop_button.config(state="disabled")
            return
        if p.jogador_atual is None:
            nome = p.proximo_jogador()
            if nome is None:
                self.status.set("Partida encerrada: não há jogadores ativos.")
                self.roll_button.config(state="disabled")
                self.stop_button.config(state="disabled")
                return
            p.iniciar_turno(nome)
            self.resultado = None
        self.status.set("Vez de " + p.jogador_atual)
        self.roll_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self._atualizar()

    def rolar(self):
        if self.partida is None or self.partida.jogador_atual is None:
            return
        self.resultado = self.partida.lancar()
        estado = self.partida.estado_do_jogador()
        self._atualizar()
        self._mostrar_dados()
        if estado == jogo.STATUS_ELIMINADO:
            nome = self.partida.jogador_atual
            self.partida.eliminar_jogador(nome)
            self.status.set(nome + " foi eliminado após 3 tiros.")
            self._atualizar()
            self.root.after(900, self._preparar_vez)
        elif estado == jogo.STATUS_VITORIA:
            nome = self.partida.jogador_atual
            self.partida.finalizar_vitoria(nome)
            self.status.set("Vencedor: " + nome)
            self.roll_button.config(state="disabled")
            self.stop_button.config(state="disabled")
            self._atualizar()
        else:
            self.status.set("Vez de %s — escolha continuar ou parar" % self.partida.jogador_atual)
            self.roll_button.config(state="normal")
            self.stop_button.config(state="normal")

    def parar(self):
        if self.partida is None or self.partida.jogador_atual is None:
            return
        self.partida.parar_turno()
        self.resultado = None
        self._atualizar()
        self._preparar_vez()

    def interromper(self):
        if self.partida is None:
            self.root.destroy()
            return
        try:
            salvar_partida(self.partida)
            self.root.destroy()
        except OSError as erro:
            messagebox.showerror("Erro ao salvar", str(erro))

    def _mostrar_dados(self):
        for widget in self.dados.winfo_children():
            widget.destroy()
        for cor, face in zip(self.resultado["cores"], self.resultado["faces"]):
            tk.Label(self.dados, text=NOMES_FACE[face], bg=CORES[cor], fg="white",
                     width=12, height=3, font=("TkDefaultFont", 12, "bold"),
                     relief="raised", borderwidth=3).pack(side="left", padx=5)

    def _atualizar(self):
        if self.partida is None:
            return
        linhas = ["Placar"]
        for nome, stats in self.partida.placar_com_turno().items():
            marca = " (eliminado)" if nome in self.partida.eliminados else ""
            vez = " ← vez" if nome == self.partida.jogador_atual else ""
            linhas.append("%s%s%s  |  Cérebros %d  Tiros %d" %
                          (nome, marca, vez, stats["cerebro"], stats["tiro"]))
        linhas.append("Turno: %d cérebros · %d tiros" %
                      (self.partida.turno["cerebro"], self.partida.turno["tiro"]))
        self.placar.config(text="\n".join(linhas))


def main():
    root = tk.Tk()
    TelaTurno(root)
    root.mainloop()


if __name__ == "__main__":
    main()
