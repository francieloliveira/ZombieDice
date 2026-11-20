"""Testes das ações autoritativas do servidor, sem navegador."""

import os
import asyncio
import base64
import hashlib
import json
import random
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from servidor import ErroAcao, ServidorHTTPWebSocket, ServidorPartidas


class TestServidorPartidas(unittest.TestCase):
    def setUp(self):
        self.servidor = ServidorPartidas(rng=random.Random(23))
        self.sala = self.servidor.criar("Ana")
        self.servidor.entrar(self.sala.codigo, "Beto")
        self.servidor.entrar(self.sala.codigo, "Caio")

    def test_estado_completo_tem_tres_jogadores_e_placar(self):
        estado = self.sala.estado()
        self.assertEqual(estado["jogadores"], ["Ana", "Beto", "Caio"])
        self.assertIn(estado["jogador_atual"], estado["jogadores"])
        self.assertEqual(set(estado["placar"]), set(estado["jogadores"]))
        self.assertNotIn("copo", estado)
        self.assertNotIn("rng", estado)
        self.assertNotIn("dados_passo", estado)

    def test_jogador_fora_da_vez_e_recusado_sem_mudar_estado(self):
        atual = self.sala.partida.jogador_atual
        outro = next(nome for nome in self.sala.nomes if nome != atual)
        antes = self.sala.estado()
        with self.assertRaisesRegex(ErroAcao, "não é a vez"):
            self.servidor.agir(self.sala, outro, "rolar")
        self.assertEqual(self.sala.estado(), antes)

    def test_acao_valida_atualiza_estado_serializavel(self):
        atual = self.sala.partida.jogador_atual
        estado = self.servidor.agir(self.sala, atual, "rolar")
        self.assertEqual(estado["resultado"]["jogador"], atual)
        self.assertEqual(len(estado["resultado"]["faces"]), 3)
        self.assertEqual(len(estado["resultado"]["cores"]), 3)
        self.assertEqual(len(estado["placar"]), 3)


class TestServidorWebSocket(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = ServidorHTTPWebSocket(port=0, gerenciador=ServidorPartidas(rng=random.Random(23)))
        self.server = await self.app.iniciar()
        self.port = self.server.sockets[0].getsockname()[1]
        self.clientes = []

    async def asyncTearDown(self):
        for reader, writer in self.clientes:
            writer.close()
            await writer.wait_closed()
        await self.app.fechar()

    async def conectar(self):
        reader, writer = await asyncio.open_connection("127.0.0.1", self.port)
        chave = base64.b64encode(os.urandom(16)).decode()
        writer.write(("GET / HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\n"
                      "Connection: Upgrade\r\nSec-WebSocket-Version: 13\r\n"
                      "Sec-WebSocket-Key: %s\r\n\r\n" % chave).encode())
        await writer.drain()
        resposta = await reader.readuntil(b"\r\n\r\n")
        self.assertIn(b"101 Switching Protocols", resposta)
        esperado = base64.b64encode(hashlib.sha1(
            (chave + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest())
        self.assertIn(esperado, resposta)
        self.clientes.append((reader, writer))
        return reader, writer

    async def enviar(self, writer, payload):
        dados = json.dumps(payload).encode()
        mascara = os.urandom(4)
        if len(dados) < 126:
            cab = bytes((0x81, 0x80 | len(dados)))
        else:
            cab = bytes((0x81, 0x80 | 126)) + struct.pack("!H", len(dados))
        writer.write(cab + mascara + bytes(b ^ mascara[i % 4] for i, b in enumerate(dados)))
        await writer.drain()

    async def receber(self, reader):
        cab = await asyncio.wait_for(reader.readexactly(2), 2)
        tamanho = cab[1] & 0x7f
        if tamanho == 126:
            tamanho = struct.unpack("!H", await reader.readexactly(2))[0]
        dados = await asyncio.wait_for(reader.readexactly(tamanho), 2)
        return json.loads(dados)

    async def test_tres_jogadores_recebem_estado_comum_e_recusa_pela_rede(self):
        r1, w1 = await self.conectar()
        await self.enviar(w1, {"acao": "criar", "nome": "Ana"})
        estado = await self.receber(r1)
        codigo = estado["sala"]

        r2, w2 = await self.conectar()
        await self.enviar(w2, {"acao": "entrar", "sala": codigo, "nome": "Beto"})
        await self.receber(r1)
        await self.receber(r2)

        r3, w3 = await self.conectar()
        await self.enviar(w3, {"acao": "entrar", "sala": codigo, "nome": "Caio"})
        estados = [await self.receber(r) for r in (r1, r2, r3)]
        self.assertEqual([e["jogadores"] for e in estados], [["Ana", "Beto", "Caio"]] * 3)
        atual = estados[0]["jogador_atual"]
        por_nome = {"Ana": (r1, w1), "Beto": (r2, w2), "Caio": (r3, w3)}

        await self.enviar(por_nome[atual][1], {"acao": "rolar"})
        apos_rolar = [await self.receber(r) for r in (r1, r2, r3)]
        self.assertEqual(apos_rolar[0], apos_rolar[1])
        self.assertEqual(apos_rolar[1], apos_rolar[2])
        self.assertEqual(len(apos_rolar[0]["resultado"]["faces"]), 3)

        fora = next(nome for nome in por_nome if nome != apos_rolar[0]["jogador_atual"])
        await self.enviar(por_nome[fora][1], {"acao": "parar"})
        resposta = await self.receber(por_nome[fora][0])
        self.assertIn("não é a vez", resposta["erro"])
        self.assertEqual(resposta["estado"], apos_rolar[0])


if __name__ == "__main__":
    unittest.main()
