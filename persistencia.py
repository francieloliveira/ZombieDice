"""Leitura e gravação do estado retomável de uma partida."""

import json
import random

import jogo


_DADOS_POR_COR = {
    "Verde": jogo.DADO_VERDE,
    "Amarelo": jogo.DADO_AMARELO,
    "Vermelho": jogo.DADO_VERMELHO,
}


def _tuplas(valor):
    if isinstance(valor, list):
        return tuple(_tuplas(item) for item in valor)
    return valor


def _cores(dados):
    return [jogo.cor_do_dado(dado) for dado in dados]


def salvar(partida, resultado, caminho):
    """Grava partida e dados exibidos, sem salvar uma partida já vencida."""
    if partida.vencedor:
        caminho.unlink(missing_ok=True)
        return
    estado = {
        "jogadores": partida.jogadores,
        "placar": partida.placar,
        "copo": _cores(partida.copo),
        "vencedor": partida.vencedor,
        "eliminados": partida.eliminados,
        "jogados": sorted(partida.jogados),
        "jogador_atual": partida.jogador_atual,
        "turno": partida.turno,
        "dados_passo": _cores(partida.dados_passo),
        "rng": partida.random.getstate(),
        "resultado": ({"cores": resultado["cores"], "faces": resultado["faces"]}
                      if resultado else None),
    }
    caminho.write_text(json.dumps(estado, ensure_ascii=False), encoding="utf-8")


def carregar(caminho):
    """Retorna (Partida, último resultado visual), preservando RNG e estado."""
    estado = json.loads(caminho.read_text(encoding="utf-8"))
    gerador = random.Random()
    gerador.setstate(_tuplas(estado["rng"]))
    partida = jogo.Partida(estado["jogadores"], random=gerador)
    partida.placar = estado["placar"]
    partida.copo = [_DADOS_POR_COR[cor] for cor in estado["copo"]]
    partida.vencedor = estado["vencedor"]
    partida.eliminados = estado["eliminados"]
    partida.jogados = set(estado["jogados"])
    partida.jogador_atual = estado["jogador_atual"]
    partida.turno = estado["turno"]
    partida.dados_passo = [_DADOS_POR_COR[cor] for cor in estado["dados_passo"]]
    return partida, estado.get("resultado")
