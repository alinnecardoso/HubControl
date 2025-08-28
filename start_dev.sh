#!/bin/bash
# Garante que o script pare se algo der errado
set -e

# --- Configuração do Ambiente ---
# Garante que o processo do Uvicorn encontre as bibliotecas de sistema corretas.
# Esta variável é necessária em ambientes específicos como o NixOS.
export LD_LIBRARY_PATH=/nix/store/90yn7340r8yab8kxpb0p7y0c9j3snjam-gcc-13.2.0-lib/lib:$LD_LIBRARY_PATH

# --- Ativação do Ambiente Virtual ---
echo "Ativando o ambiente virtual..."
source venv/bin/activate

# --- Definição do PYTHONPATH ---
# Adiciona o diretório raiz do projeto ao PYTHONPATH.
# Isso permite importações absolutas consistentes a partir do nome da pasta raiz (backend).
echo "Definindo PYTHONPATH para o diretório do projeto..."
export PYTHONPATH=.

# --- Execução do Servidor ---
echo "Iniciando o servidor Uvicorn com auto-reload..."

# Com o PYTHONPATH definido para a raiz, o uvicorn pode localizar 'backend.main:app'.
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
