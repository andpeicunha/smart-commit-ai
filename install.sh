#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para mostrar o uso do script
show_usage() {
    echo -e "${BLUE}Uso:${NC} $0 -s <shell>"
    echo -e "  -s: Especifique seu shell (${GREEN}bash${NC} ou ${GREEN}zsh${NC})"
    echo
    echo -e "Exemplo:"
    echo -e "  ${YELLOW}./install.sh -s bash${NC}"
    echo -e "  ${YELLOW}./install.sh -s zsh${NC}"
    exit 1
}

# Processar argumentos da linha de comando
while getopts "s:" opt; do
    case $opt in
        s)
            shell_type=$OPTARG
            ;;
        *)
            show_usage
            ;;
    esac
done

# Verificar se o shell foi especificado
if [ -z "$shell_type" ]; then
    echo -e "${RED}❌ Por favor, especifique o tipo de shell usando -s${NC}"
    show_usage
fi

# Configurar o shell baseado no parâmetro
case $shell_type in
    bash)
        SHELL_RC="$HOME/.bashrc"
        SHELL_NAME="Bash"
        ;;
    zsh)
        SHELL_RC="$HOME/.zshrc"
        SHELL_NAME="Zsh"
        ;;
    *)
        echo -e "${RED}❌ Shell inválido. Use 'bash' ou 'zsh'${NC}"
        show_usage
        ;;
esac

echo -e "${BLUE}📦 Instalando gerador de commits...${NC}"
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
