#!/usr/bin/env python3
"""
Script para criar credentials.json a partir das credenciais fornecidas.
Execute este script localmente para criar o arquivo credentials.json.

As credenciais podem ser fornecidas via:
1. Variáveis de ambiente (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
2. Input interativo quando o script é executado
"""

import json
import os

# Credenciais - serão solicitadas ao usuário ou lidas de variáveis de ambiente
def obter_credenciais():
    """Obtém credenciais do usuário ou variáveis de ambiente"""
    client_id = os.environ.get('GOOGLE_CLIENT_ID') or input("Digite o Client ID: ").strip()
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET') or input("Digite o Client Secret: ").strip()
    project_id = os.environ.get('GOOGLE_PROJECT_ID', 'escala-coroinhas-app')
    
    return {
        "web": {
            "client_id": client_id,
            "project_id": project_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": [
                "http://localhost:5000/oauth2callback",
                "http://localhost:3000/oauth2callback"
            ]
        }
    }

def criar_credentials():
    """Cria o arquivo credentials.json"""
    arquivo = "credentials.json"
    
    # Verificar se já existe
    if os.path.exists(arquivo):
        resposta = input(f"O arquivo {arquivo} já existe. Deseja sobrescrever? (s/N): ")
        if resposta.lower() != 's':
            print("Operação cancelada.")
            return
    
    # Obter credenciais
    credentials = obter_credenciais()
    
    # Obter URL da Vercel se fornecida
    vercel_url = input("Digite a URL da Vercel (ex: seu-app.vercel.app) ou pressione Enter para pular: ").strip()
    if vercel_url:
        if not vercel_url.startswith('http'):
            vercel_url = f"https://{vercel_url}"
        credentials["web"]["redirect_uris"].append(f"{vercel_url}/oauth2callback")
        print(f"URL da Vercel adicionada: {vercel_url}/oauth2callback")
    
    # Salvar arquivo
    try:
        with open(arquivo, 'w') as f:
            json.dump(credentials, f, indent=2)
        print(f"✅ Arquivo {arquivo} criado com sucesso!")
        print(f"📝 Redirect URIs configurados: {len(credentials['web']['redirect_uris'])}")
    except Exception as e:
        print(f"❌ Erro ao criar arquivo: {e}")

if __name__ == "__main__":
    criar_credentials()

