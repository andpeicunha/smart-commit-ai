# Smart Commit AI

Gerador inteligente de mensagens de commit usando IA para criar commits padronizados e descritivos.

## 🚀 Recursos

- Não precisa de Key de nenhum IA
- Roda 100% local
- Gera mensagens de commit baseadas no diff das alterações
- Segue convenções de commit (Conventional Commits)
- Suporta múltiplos tipos de commit (feat, fix, docs, etc) com emojis
- Analisa o contexto do projeto para gerar mensagens mais relevantes
- Integração fácil com seu fluxo de trabalho git
- Diferentes estilos de mensagem para tornar seus commits mais divertidos

## 📋 Pré-requisitos

- Python 3.x
- Git
- Terminal Bash ou Zsh
- Para utilizar, dependerá de uma conexão de internet

## Importante!

O resultado do comando `git diff` e `git log` será enviado para um serviço que fará a análise deste conteúdo para gerar a mensagens!

## 💻 Instalação

1. Baixe o script de instalação:

```bash
curl -fsSL https://raw.githubusercontent.com/andpeicunha/smart-commit-ai/master/install.sh -o install.sh
```

2. Torne o script executável e faça a instalação:

```bash
chmod +x install.sh && ./install.sh
```

_Ele vai perguntar qual shell você usa, se o Bash ou ZSH, basta seguir as instruções._

3. Após a instalação, você pode remover o script:

```bash
rm install.sh
```

## ⚙️ Configuração

O **Smart Commit AI** pode ser personalizado através do arquivo `.gscrc`. Na primeira execução, um arquivo de configuração padrão será criado em seu diretório home.

<!-- Você pode criar também um arquivo `.gscrc` específico para cada projeto. -->

Exemplo de configuração:

```json
{
  "commit_message": {
    "max_length": 50,
    "language": "en-US"
  },
  "description": {
    "format": "bullets",
    "max_bullets": 3,
    "max_bullet_length": 100,
    "max_paragraph_length": 300,
    "language": "pt-BR"
  },
  "editor": {
    "command": "code",
    "args": ["--wait"],
    "fallback": {
      "command": "vim",
      "args": []
    }
  },
  "shell_alias": "sca"
}
```

<br/>

### Opções de configuração:

- **commit_message**: Configurações da primeira linha do commit

  - `max_length`: Tamanho máximo da mensagem
  - `language`: Idioma ("en-US" ou "pt-BR")

- **description**: Configurações da descrição detalhada

  - `format`: Formato da descrição ("bullets" ou "paragraph")
  - `max_bullets`: Número máximo de bullets
  - `max_bullet_length`: Tamanho máximo de cada bullet
  - `max_paragraph_length`: Tamanho máximo do parágrafo
  - `language`: Idioma ("en-US" ou "pt-BR")

- **editor**: Configurações do editor para edição de mensagens
  - `command`: Comando do editor (ex: "code", "vim", "nano")
  - `args`: Argumentos adicionais do editor
  - `fallback`: Editor alternativo caso o principal falhe

<br/>

## 🎯 Como usar

**1.** Faça suas alterações no código

**2.** Adicione as alterações ao stage do git usando `git add .`

**3.** Execute o comando:

```bash
gsc               # Estilo padrão
gsc --ironico     # Mensagem com toque de humor
gsc --nerd        # Referências geek
gsc --poeta       # Estilo poético
gsc --epico       # Tom épico
```

Para ver todos os estilos disponíveis:

```bash
gsc --list
# também pode usar a forma abreviada
gsc -L
```

Para aceitar automaticamente a mensagem de commit

```bash
gsc --accept
# também pode usar a forma abreviada
gsc -A
```

Para não gerar a descrição

```bash
gsc --desc
# também pode usar a forma abreviada
gsc -D
```

> 💡 O comando `gsc` é um alias no seu shell, portanto NÃO precisa ter o git antes, basta executar dessa forma e ver a mágica acontecer!

4. O script irá analisar suas alterações e vai sugerir uma mensagem de commit

5. Você pode:
   - Pressionar `ENTER` ou digitar `Y` para aceitar a mensagem
   - Digitar `n` para cancelar
   - Digitar `e` para editar a mensagem no seu editor configurado

## 🎨 Estilos de Commit

Você pode personalizar o tom das suas mensagens de commit usando diferentes estilos:

- **Padrão**: Mensagens profissionais e diretas [**default**]
- **Irônico**: Adiciona um toque de humor às mensagens
- **Nerd**: Usa referências da cultura geek e tech
- **Poeta**: Mensagens com um toque elegante
- **Épico**: Tom dramático e heroico

<br/>

## 📝 Formato das mensagens

As mensagens seguem o padrão:

```bash
type: short end clear description (max 50 caracteres, idioma configurável)

# Formato bullets:
- Bullet points para mais detalhes (idioma configurável)
- Número e tamanho dos bullets configuráveis

# Formato parágrafo:
Descrição detalhada em formato de parágrafo, mencionando os arquivos alterados e mudanças específicas. O tamanho máximo e idioma são configuráveis através do arquivo .gscrc.
```

### Tipos de commit suportados:

- `feat`: nova funcionalidade
- `fix`: correção de bug
- `docs`: documentação
- `style`: formatação, ponto-e-vírgula, etc
- `refactor`: refatoração de código
- `test`: adição/modificação de testes
- `chore`: build, configs, etc
- `perf`: melhorias de performance

## 🤝 Contribuindo

Contribuições são sempre bem-vindas! Sinta-se à vontade para:

1. Fazer um fork do projeto
2. Criar uma branch para sua feature
3. Fazer suas alterações
4. Enviar um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 🐛 Encontrou um bug?

Por favor, [abra uma issue](https://github.com/andpeicunha/smart-commit-ai/issues) descrevendo o problema encontrado.
