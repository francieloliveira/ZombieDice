"""Protótipo Tkinter para jogar Zombie Dice usando a lógica de ``jogo``."""

import random
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog

import jogo
import persistencia


SAVE_PATH = Path(__file__).with_name("partida_gui.json")
CORES = {"Verde": "#5a9b55", "Amarelo": "#d6ad32", "Vermelho": "#c94d4d"}
NOMES_FACE = {jogo.CEREBRO: "Cérebro", jogo.PASSO: "Passos", jogo.TIRO: "Tiro"}


class TelaTurno:
    def __init__(self, root):
        self.root = root
        self.root.title("Zombie Dice — turno")
        self.partida = None
        self.resultado = None
        self.encerrada = False
        self.status = tk.StringVar(value="Inicie uma partida ou retome uma salva.")
        self._montar()
        self.root.protocol("WM_DELETE_WINDOW", self.interromper)
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

    def _apagar_save(self):
        """Um único ponto apaga o save: o estado encerrado não volta ao abrir."""
        SAVE_PATH.unlink(missing_ok=True)

    def _oferecer_retomar(self):
        if SAVE_PATH.exists() and messagebox.askyesno("Partida salva", "Deseja retomar a partida salva?"):
            try:
                self.partida, self.resultado = persistencia.carregar(SAVE_PATH)
                self.encerrada = False
                self._atualizar()
                if self.resultado:
                    self._mostrar_dados()
                self._preparar_vez()
            except (OSError, ValueError, KeyError, TypeError) as erro:
                messagebox.showerror("Erro ao retomar", str(erro))
        elif SAVE_PATH.exists():
            self._apagar_save()

    def nova_partida(self):
        em_andamento = (self.partida is not None and not self.encerrada
                        and not self.partida.vencedor)
        if em_andamento and not messagebox.askyesno(
                "Nova partida", "A partida em andamento será descartada. Continuar?"):
            return
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
        self.encerrada = False
        self._atualizar()
        self._preparar_vez()

    def _preparar_vez(self):
        p = self.partida
        if p is None:
            return
        if p.vencedor:
            self._apagar_save()
            self.status.set("Vencedor: " + p.vencedor)
            self.roll_button.config(state="disabled")
            self.stop_button.config(state="disabled")
            return
        if p.jogador_atual is None:
            nome = p.proximo_jogador()
            if nome is None:
                # Fim normal de partida sem 13 cérebros: encerrada, não retomável.
                self.encerrada = True
                self._apagar_save()
                self.status.set("Partida encerrada: todos já jogaram.")
                self.roll_button.config(state="disabled")
                self.stop_button.config(state="disabled")
                return
            p.iniciar_turno(nome)
            self.resultado = None
        self.status.set("Vez de " + p.jogador_atual)
        self.roll_button.config(state="normal")
        em_andamento = any(p.turno.values()) or bool(self.resultado)
        self.stop_button.config(state="normal" if em_andamento else "disabled")
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
            self._apagar_save()
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
            if self.partida.vencedor or self.encerrada:
                # Partida acabada não vira save: não se oferece retomar o que terminou.
                self._apagar_save()
            else:
                persistencia.salvar(self.partida, self.resultado, SAVE_PATH)
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
