# Smart Commit AI

Gerador inteligente de mensagens de commit usando IA para criar commits padronizados e descritivos.

## 🚀 Recursos

- Gera mensagens de commit baseadas no diff das alterações
- Segue convenções de commit (Conventional Commits)
- Suporta múltiplos tipos de commit (feat, fix, docs, etc)
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

## 🎯 Como usar

1. Faça suas alterações no código
2. Adicione as alterações ao stage do git (`git add .`)
3. Execute o comando:

```bash
gsc                # Estilo padrão
gsc --ironico     # Mensagem com toque de humor
gsc --nerd        # Referências geek
gsc --poeta       # Estilo poético
gsc --epico       # Tom épico
```

Para ver todos os estilos disponíveis:

```bash
gsc --list
```

> 💡 O comando `gsc` é um alias no seu shell, portanto NÃO precisa ter o git antes, basta executar dessa forma e ver a mágica acontecer!

4. O script irá analisar suas alterações e sugerir uma mensagem de commit
5. Confirme se deseja usar a mensagem sugerida

## 🎨 Estilos de Commit

Você pode personalizar o tom das suas mensagens de commit usando diferentes estilos:

- **Padrão**: Mensagens profissionais e diretas
- **Irônico**: Adiciona um toque de humor às mensagens
- **Nerd**: Usa referências da cultura geek e tech
- **Poeta**: Mensagens com um toque lírico e elegante
- **Épico**: Tom dramático e heroico

## 📝 Formato das mensagens

As mensagens seguem o padrão:

```
type: short end clear description (max 50 caracteres em inglês)

- Bullet points opcionais para mais detalhes (em Português)
- Máximo 2-3 bullets, cada um com máximo 100 caracteres
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

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🐛 Encontrou um bug?

Por favor, [abra uma issue](https://github.com/andpeicunha/smart-commit-ai/issues) descrevendo o problema encontrado.
