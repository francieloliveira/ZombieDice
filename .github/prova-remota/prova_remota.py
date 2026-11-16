#!/usr/bin/env python3
"""Prova remota no Linux (FRA-620), instalada pelo TuttiDash.

Fonte: tuttidash/tools/prova-remota-linux. Não edite a cópia do projeto: o
`tools/instalar-prova-remota` do TuttiDash regenera estes arquivos.

Linux não compila app da Apple. Então a prova só fica verde quando o PR mexe
apenas no que dá para conferir aqui (Python, shell, docs e dados fora das
pastas do app). Qualquer arquivo do app, ou da própria prova, deixa o check
vermelho com "precisa da prova no Mac": nunca há verde sem teste.

Este arquivo vale como blob da base. `classificar` roda no runner;
`executar` roda dentro do container sem rede, com o código do PR só leitura.

Uso:
  prova_remota.py classificar CONFIG.json < nomes separados por NUL   (imprime JSON)
  prova_remota.py executar '<json do classificar>'                    (no container)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import PurePosixPath

# A própria prova mora toda em .github/: o PR não decide como é provado.
DA_PROVA = (".github/",)
EXTENSOES_OK = {
    ".py", ".sh", ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".cfg",
    ".ini", ".conf", ".csv", ".ndjson",
}
NOMES_OK = {".gitignore", ".gitattributes"}
TIMEOUT_TESTES_S = 15 * 60


def pastas_do_app(config: dict) -> tuple[str, ...]:
    """Prefixos (com `/` no fim) das pastas que só o Mac prova, vindos do config."""
    saida = []
    for p in config.get("pastas_do_app") or []:
        p = str(p).strip().strip("/")
        if p and ".." not in PurePosixPath(p).parts:
            saida.append(p + "/")
    return tuple(saida)


def motivo_vermelho(nome: str, app: tuple[str, ...]) -> str | None:
    """Por que este arquivo exige o Mac (ou a revisão do dono). None = Linux prova."""
    if not nome or nome.startswith("/") or ".." in PurePosixPath(nome).parts:
        return f"caminho inválido: {nome!r}"
    if nome.startswith(DA_PROVA):
        return f"mexe na própria prova: {nome}"
    if app and nome.startswith(app):
        return f"mexe no app: {nome}"
    caminho = PurePosixPath(nome)
    if caminho.name in NOMES_OK or nome.startswith("docs/"):
        return None
    if caminho.suffix.lower() not in EXTENSOES_OK:
        return f"tipo de arquivo que o Linux não prova: {nome}"
    return None


def classificar(nomes: list[str], config: dict) -> dict:
    app = pastas_do_app(config)
    nomes = sorted({n for n in nomes if n})
    motivos = [m for m in (motivo_vermelho(n, app) for n in nomes) if m]
    return {
        "verde": bool(nomes) and not motivos,
        "motivos": motivos if nomes else ["o PR não muda nenhum arquivo"],
        "py": [n for n in nomes if n.endswith(".py")],
        "sh": [n for n in nomes if n.endswith(".sh")],
        "arquivos": nomes,
    }


def pastas_com_testes(arquivos: list[str], existe=os.path.isdir, listar=os.listdir) -> list[str]:
    """Para cada arquivo, a pasta mais próxima (subindo) que tem `test_*.py`."""
    achadas = set()
    for nome in arquivos:
        pasta = PurePosixPath(nome).parent
        while str(pasta) not in ("", "."):
            p = str(pasta)
            if existe(p) and any(f.startswith("test_") and f.endswith(".py") for f in listar(p)):
                achadas.add(p)
                break
            pasta = pasta.parent
    return sorted(achadas)


def executar(dados: dict) -> int:
    """No container: compila os .py, `bash -n` nos .sh, roda os testes das pastas tocadas."""
    falhas = 0
    for nome in dados.get("py", []):
        if not os.path.isfile(nome):
            continue                                   # removido no PR
        try:
            with open(nome, encoding="utf-8") as f:
                compile(f.read(), nome, "exec")        # sem gravar .pyc (código só leitura)
            print(f"ok compila: {nome}")
        except (SyntaxError, UnicodeDecodeError) as exc:
            print(f"FALHA compila: {nome}: {exc}")
            falhas += 1
    for nome in dados.get("sh", []):
        if not os.path.isfile(nome):
            continue
        r = subprocess.run(["bash", "-n", nome], capture_output=True, text=True)
        print(("ok bash -n: " if r.returncode == 0 else "FALHA bash -n: ") + nome + r.stderr)
        falhas += r.returncode != 0
    for pasta in pastas_com_testes(dados.get("arquivos", [])):
        print(f"== testes em {pasta}")
        r = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", pasta, "-t", pasta, "-p", "test_*.py"],
            timeout=TIMEOUT_TESTES_S)
        falhas += r.returncode != 0
    print("prova-remota: verde" if not falhas else f"prova-remota: {falhas} falha(s)")
    return 1 if falhas else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["classificar"] and len(argv) == 2:
        with open(argv[1], encoding="utf-8") as f:
            config = json.load(f)
        nomes = sys.stdin.buffer.read().decode("utf-8", "surrogateescape").split("\0")
        print(json.dumps(classificar(nomes, config), ensure_ascii=False))
        return 0
    if argv[:1] == ["executar"] and len(argv) == 2:
        return executar(json.loads(argv[1]))
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
