"""Servidor HTTP e WebSocket autoritativo para partidas Zombie Dice.

Protocolo WebSocket: primeiro JSON {"acao":"criar|entrar", "nome":...,
"sala":...}; em seguida {"acao":"rolar|parar"}. Cada resposta inclui o
estado completo e é enviada a todos os clientes da sala.
"""

import asyncio
import base64
import hashlib
import json
import random
import secrets
import struct
from urllib.parse import urlparse

import jogo


class ErroAcao(ValueError):
    """Ação inválida, recusada sem alterar a partida."""


class Sala:
    def __init__(self, codigo, nome):
        self.codigo = codigo
        self.partida = None
        self.nomes = [nome]
        self.clientes = set()
        self.resultado = None
        self.jogadas = 0

    def estado(self, erro=None):
        p = self.partida
        estado = {
            "sala": self.codigo,
            "jogadores": list(self.nomes),
            "iniciada": p is not None,
            "placar": p.placar_com_turno() if p else {
                nome: {"cerebro": 0, "passo": 0, "tiro": 0} for nome in self.nomes
            },
            "jogador_atual": p.jogador_atual if p else None,
            "turno": dict(p.turno) if p else {"cerebro": 0, "passo": 0, "tiro": 0},
            "vencedor": p.vencedor if p else None,
            "eliminados": list(p.eliminados) if p else [],
            "resultado": self.resultado,
        }
        # O estado público contém apenas o necessário para desenhar a mesa.
        # O tubo, os dados pendentes e a semente pertencem ao servidor.
        if erro:
            estado["erro"] = erro
        return estado


class ServidorPartidas:
    def __init__(self, rng=random):
        self.salas = {}
        self.rng = rng

    def criar(self, nome):
        nome = self._nome(nome)
        codigo = secrets.token_urlsafe(5).upper()
        while codigo in self.salas:
            codigo = secrets.token_urlsafe(5).upper()
        sala = Sala(codigo, nome)
        self.salas[codigo] = sala
        return sala

    def entrar(self, codigo, nome):
        sala = self.salas.get(str(codigo).upper())
        if not sala:
            raise ErroAcao("sala não encontrada")
        nome = self._nome(nome)
        if nome in sala.nomes:
            raise ErroAcao("nome já está nesta sala")
        if len(sala.nomes) >= 8:
            raise ErroAcao("sala cheia: máximo de 8 jogadores")
        sala.nomes.append(nome)
        if len(sala.nomes) >= 2:
            if sala.partida is None:
                sala.partida = jogo.Partida(sala.nomes, random=self.rng)
                sala.partida.iniciar_turno(sala.partida.proximo_jogador())
            elif sala.jogadas == 0:
                # Recalcula a vez inicial usando todos os nomes que entraram
                # antes da primeira ação, sem inspecionar detalhes de Partida.
                partida = jogo.Partida(sala.nomes, random=self.rng)
                sala.partida = partida
                partida.iniciar_turno(partida.proximo_jogador())
            else:
                sala.partida.jogadores.append(nome)
                sala.partida.placar[nome] = {"cerebro": 0, "passo": 0, "tiro": 0}
        return sala

    def agir(self, sala, nome, acao):
        p = sala.partida
        if not p:
            raise ErroAcao("a partida ainda não começou")
        if nome != p.jogador_atual:
            raise ErroAcao("ação recusada: não é a vez de %s" % p.jogador_atual)
        if acao == "rolar":
            lancamento = p.lancar()
            sala.jogadas += 1
            sala.resultado = {
                chave: lancamento[chave]
                for chave in ("jogador", "faces", "cores", "turno")
            }
            status = p.estado_do_jogador(nome)
            if status == jogo.STATUS_ELIMINADO:
                p.eliminar_jogador(nome)
                self._avancar(sala)
            elif status == jogo.STATUS_VITORIA:
                p.finalizar_vitoria(nome)
        elif acao == "parar":
            p.parar_turno(nome)
            sala.jogadas += 1
            sala.resultado = None
            self._avancar(sala)
        else:
            raise ErroAcao("ação desconhecida: use rolar ou parar")
        return sala.estado()

    @staticmethod
    def _avancar(sala):
        p = sala.partida
        if p.vencedor:
            return
        proximo = p.proximo_jogador()
        if proximo is None:
            p.jogados.clear()
            proximo = p.proximo_jogador()
        if proximo:
            p.iniciar_turno(proximo)

    @staticmethod
    def _nome(nome):
        if not isinstance(nome, str) or not nome.strip():
            raise ErroAcao("informe um nome de jogador")
        nome = nome.strip()
        if len(nome) > 40:
            raise ErroAcao("nome deve ter até 40 caracteres")
        return nome


class ServidorHTTPWebSocket:
    """Servidor asyncio mínimo, sem dependências de rede de terceiros."""
    def __init__(self, host="127.0.0.1", port=8765, gerenciador=None):
        self.host, self.port = host, port
        self.gerenciador = gerenciador or ServidorPartidas()
        self._server = None

    async def iniciar(self):
        self._server = await asyncio.start_server(self._cliente, self.host, self.port)
        return self._server

    async def fechar(self):
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def _cliente(self, reader, writer):
        try:
            linha = await reader.readline()
            if not linha:
                return
            partes = linha.decode("ascii", "replace").split()
            headers = {}
            while True:
                linha = await reader.readline()
                if linha in (b"\r\n", b"\n", b""):
                    break
                chave, _, valor = linha.decode("latin1").partition(":")
                headers[chave.lower()] = valor.strip()
            if headers.get("upgrade", "").lower() == "websocket":
                await self._websocket(reader, writer, headers)
            elif len(partes) >= 2 and partes[1] == "/health":
                await self._resposta(writer, 200, {"status": "ok"})
            elif len(partes) >= 2 and partes[1] == "/rooms" and partes[0] == "POST":
                tamanho = min(int(headers.get("content-length", "0")), 4096)
                body = json.loads((await reader.readexactly(tamanho)).decode())
                sala = self.gerenciador.criar(body.get("nome"))
                await self._resposta(writer, 201, {"sala": sala.codigo, "estado": sala.estado()})
            else:
                await self._resposta(writer, 404, {"erro": "rota não encontrada"})
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            await self._resposta(writer, 400, {"erro": str(exc)})
        except (ConnectionError, asyncio.IncompleteReadError):
            pass
        finally:
            if not writer.is_closing():
                writer.close()
                try:
                    await writer.wait_closed()
                except ConnectionError:
                    pass

    async def _resposta(self, writer, status, payload):
        corpo = json.dumps(payload, ensure_ascii=False).encode()
        frase = {200: "OK", 201: "Created", 400: "Bad Request", 404: "Not Found"}[status]
        writer.write(("HTTP/1.1 %d %s\r\nContent-Type: application/json; charset=utf-8\r\n"
                      "Content-Length: %d\r\nConnection: close\r\n\r\n" %
                      (status, frase, len(corpo))).encode() + corpo)
        await writer.drain()

    async def _websocket(self, reader, writer, headers):
        chave = headers.get("sec-websocket-key")
        if not chave:
            return
        aceita = base64.b64encode(hashlib.sha1(
            (chave + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
        writer.write(("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\n"
                      "Connection: Upgrade\r\nSec-WebSocket-Accept: %s\r\n\r\n" % aceita).encode())
        await writer.drain()
        sala = nome = None
        try:
            while True:
                mensagem = await self._ler_frame(reader)
                if mensagem is None:
                    return
                try:
                    dados = json.loads(mensagem)
                    acao = dados.get("acao")
                    if sala is None:
                        if acao == "criar":
                            sala = self.gerenciador.criar(dados.get("nome"))
                            nome = sala.nomes[0]
                        elif acao == "entrar":
                            sala = self.gerenciador.entrar(dados.get("sala"), dados.get("nome"))
                            nome = sala.nomes[-1]
                        else:
                            raise ErroAcao("primeira ação deve ser criar ou entrar")
                        sala.clientes.add(writer)
                        await self._broadcast(sala)
                    else:
                        self.gerenciador.agir(sala, nome, acao)
                        await self._broadcast(sala)
                except (ErroAcao, ValueError, TypeError) as exc:
                    await self._enviar(writer, {"erro": str(exc), "estado": sala.estado() if sala else None})
        finally:
            if sala:
                sala.clientes.discard(writer)

    async def _broadcast(self, sala):
        payload = sala.estado()
        await asyncio.gather(*(self._enviar(c, payload) for c in tuple(sala.clientes)), return_exceptions=True)

    async def _enviar(self, writer, payload):
        dados = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
        tamanho = len(dados)
        if tamanho < 126:
            cabecalho = bytes((0x81, tamanho))
        elif tamanho < 65536:
            cabecalho = bytes((0x81, 126)) + struct.pack("!H", tamanho)
        else:
            cabecalho = bytes((0x81, 127)) + struct.pack("!Q", tamanho)
        writer.write(cabecalho + dados)
        await writer.drain()

    async def _ler_frame(self, reader):
        cab = await reader.readexactly(2)
        opcode, tamanho = cab[0] & 0x0F, cab[1] & 0x7F
        if opcode == 8:
            return None
        if tamanho == 126:
            tamanho = struct.unpack("!H", await reader.readexactly(2))[0]
        elif tamanho == 127:
            tamanho = struct.unpack("!Q", await reader.readexactly(8))[0]
        if tamanho > 65536:
            raise ValueError("mensagem muito grande")
        mascara = await reader.readexactly(4) if cab[1] & 0x80 else None
        dados = await reader.readexactly(tamanho)
        if mascara:
            dados = bytes(byte ^ mascara[i % 4] for i, byte in enumerate(dados))
        if opcode == 9:
            return "{}"  # ping: o estado corrente serve como resposta ao cliente
        return dados.decode("utf-8") if opcode == 1 else None


async def servir(host="127.0.0.1", port=8765):
    servidor = ServidorHTTPWebSocket(host, port)
    await servidor.iniciar()
    async with servidor._server:
        await servidor._server.serve_forever()


if __name__ == "__main__":
    asyncio.run(servir())
