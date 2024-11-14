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

# Criar ambiente virtual
VENV_DIR="$HOME/.venv-gsc"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BLUE}📁 Criando ambiente virtual em $VENV_DIR...${NC}"
    python3 -m venv "$VENV_DIR"
fi

# Instalar dependências no ambiente virtual
echo -e "${BLUE}📦 Instalando dependências Python...${NC}"
"$VENV_DIR/bin/pip" install g4f --quiet

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

# Remover alias antigo se existir
if [ -f "$SHELL_RC" ]; then
    sed -i '/alias gsc=/d' "$SHELL_RC"
else
    echo -e "${BLUE}📝 Criando arquivo $SHELL_RC...${NC}"
    touch "$SHELL_RC"
fi

# Adicionar novo alias usando o Python do ambiente virtual
echo "alias gsc='$VENV_DIR/bin/python3 $COMMIT_GENERATOR'" >> "$SHELL_RC"

echo -e "${GREEN}✅ Instalação concluída!${NC}"
echo -e "${BLUE}ℹ️  Para começar a usar, recarregue seu terminal ou execute:${NC}"
echo -e "   source $SHELL_RC"
echo -e "${BLUE}ℹ️  Depois, use o comando${NC} gsc ${BLUE}dentro de um repositório git${NC}"
