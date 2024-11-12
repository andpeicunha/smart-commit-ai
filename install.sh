#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Instalando gerador de commits...${NC}"

# Perguntar qual shell o usuário usa
echo -e "${YELLOW}Qual shell você usa?${NC}"
echo -e "1) ${GREEN}Bash${NC}"
echo -e "2) ${GREEN}Zsh${NC}"
read -p "Escolha (1/2): " shell_choice

# Configurar o shell baseado na escolha
case $shell_choice in
    1)
        SHELL_RC="$HOME/.bashrc"
        SHELL_NAME="Bash"
        ;;
    2)
        SHELL_RC="$HOME/.zshrc"
        SHELL_NAME="Zsh"
        ;;
    *)
        echo -e "${RED}❌ Opção inválida. Por favor, escolha 1 para Bash ou 2 para Zsh.${NC}"
        exit 1
        ;;
esac

echo -e "${BLUE}🛠️  Configurando para $SHELL_NAME ($SHELL_RC)${NC}"

# Criar diretório de scripts se não existir
SCRIPTS_DIR="$HOME/scripts"
if [ ! -d "$SCRIPTS_DIR" ]; then
    echo -e "${BLUE}📁 Criando diretório $SCRIPTS_DIR...${NC}"
    mkdir -p "$SCRIPTS_DIR"
fi

# Download do arquivo Python diretamente do GitHub
COMMIT_GENERATOR="$SCRIPTS_DIR/commit-generator.py"
echo -e "${BLUE}📝 Baixando script em $COMMIT_GENERATOR...${NC}"

GITHUB_RAW_URL="https://raw.githubusercontent.com/andpeicunha/smart-commit-ai/master/commit-generator.py"

if ! curl -fsSL "$GITHUB_RAW_URL" -o "$COMMIT_GENERATOR"; then
    echo -e "${RED}❌ Erro ao baixar o script. Verifique sua conexão ou se o repositório está acessível.${NC}"
    exit 1
fi

# Tornar o script executável
chmod +x "$COMMIT_GENERATOR"

# Verificar se python3 está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não está instalado. Por favor, instale-o primeiro.${NC}"
    exit 1
fi

# Instalar dependências do Python
echo -e "${BLUE}📦 Instalando dependências Python...${NC}"
pip3 install g4f --quiet

# Remover alias antigo se existir
if [ -f "$SHELL_RC" ]; then
    sed -i '/alias gsc=/d' "$SHELL_RC"
else
    echo -e "${BLUE}📝 Criando arquivo $SHELL_RC...${NC}"
    touch "$SHELL_RC"
fi

# Adicionar novo alias
echo "alias gsc='python3 $COMMIT_GENERATOR'" >> "$SHELL_RC"

echo -e "${GREEN}✅ Instalação concluída!${NC}"
echo -e "${BLUE}ℹ️  Para começar a usar, recarregue seu terminal ou execute:${NC}"
echo -e "   source $SHELL_RC"
echo -e "${BLUE}ℹ️  Depois, use o comando${NC} gsc ${BLUE}dentro de um repositório git${NC}"
