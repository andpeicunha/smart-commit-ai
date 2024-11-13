#!/usr/bin/env python3

import subprocess
from g4f.client import Client
from g4f.Provider import Blackbox
import textwrap
import sys
import os
import re
import argparse

# Dicionário com os diferentes estilos de mensagem
STYLES = {
    "padrao": {"description": "Estilo padrão, profissional e direto", "prompt_extra": ""},
    "ironico": {
        "description": "Mensagens com um toque de ironia e humor",
        "prompt_extra": """
        Adicione um toque de ironia e humor à mensagem, mas mantenha o formato profissional.
        Você pode usar trocadilhos leves e referências bem-humoradas, mas mantenha a mensagem compreensível.
        Exemplo de tom: "fix: remove bug que estava mais perdido que cego em tiroteio"
        """,
    },
    "epico": {
        "description": "Mensagens em estilo épico e dramático",
        "prompt_extra": """
        Escreva a mensagem como se fosse uma conquista épica ou uma grande saga.
        Use referências a filmes de aventura ou fantasia, mas mantenha o formato profissional.
        Exemplo de tom: "feat: forge the mighty user authentication system"
        """,
    },
    "nerd": {
        "description": "Mensagens com referências geek e tecnológicas",
        "prompt_extra": """
        Use referências a cultura geek, tecnologia, games, sci-fi e programação.
        Exemplo de tom: "feat: implement Order 66 in user permissions"
        """,
    },
    "poeta": {
        "description": "Mensagens em estilo poético e lírico",
        "prompt_extra": """
        Crie mensagens com um toque poético e lírico, mas mantendo a clareza.
        Use metáforas suaves e linguagem elegante.
        Exemplo de tom: "feat: let the database whisper its secrets through new API endpoints"
        """,
    },
}

# Novo dicionário com os tipos de commit e seus emojis
COMMIT_TYPES = {
    "feat": "✨",  # :sparkles:
    "fix": "🐛",  # :bug:
    "docs": "📚",  # :books:
    "style": "💎",  # :gem:
    "refactor": "🔨",  # :hammer:
    "perf": "🚀",  # :rocket:
    "test": "🚨",  # :rotating_light:
    "build": "📦",  # :package:
    "ci": "👷",  # :construction_worker:
    "chore": "🔧",  # :wrench:
}


def parse_arguments():
    parser = argparse.ArgumentParser(description="Gerador de mensagens de commit com diferentes estilos")

    for style in STYLES.keys():
        parser.add_argument(
            f"--{style}", action="store_const", const=style, dest="estilo", help=STYLES[style]["description"]
        )

    parser.add_argument("--list", action="store_true", help="Lista todos os estilos disponíveis")
    parser.add_argument("--accept", action="store_true", help="Aceita automaticamente a mensagem criada")

    args = parser.parse_args()

    if not args.estilo:
        args.estilo = "padrao"

    if args.list:
        print("\n🎨 Estilos disponíveis:")
        for style, info in STYLES.items():
            print(f"\n{style}: {info['description']}")
        sys.exit(0)

    return args


def get_git_diff():
    try:
        diff = subprocess.check_output(["git", "diff", "--cached"], universal_newlines=True)
        return diff
    except subprocess.CalledProcessError:
        return None


def get_recent_commits(num=3):
    try:
        commits = subprocess.check_output(["git", "log", f"-{num}", "--pretty=format:%B"], universal_newlines=True)
        return commits
    except subprocess.CalledProcessError:
        return None


def clean_blackbox_message(message):
    blackbox_pattern = r"Generated by BLACKBOX\.AI.*?\n"
    cleaned_message = re.sub(blackbox_pattern, "", message, flags=re.IGNORECASE)
    cleaned_message = cleaned_message.lstrip()

    # Adicionar emoji ao tipo de commit
    for commit_type, emoji in COMMIT_TYPES.items():
        pattern = f"^{commit_type}:"
        if re.match(pattern, cleaned_message):
            cleaned_message = f"{commit_type} {emoji}: {cleaned_message[len(commit_type)+1:].lstrip()}"
            break

    return cleaned_message


def generate_commit_message(diff, recent_commits, style="padrao"):
    style_info = STYLES[style]
    style_prompt = style_info["prompt_extra"]

    # Criar string com exemplos de tipos de commit e seus emojis
    commit_types_examples = "\n".join([f"- {type} {emoji}: descrição" for type, emoji in COMMIT_TYPES.items()])

    PROMPT = textwrap.dedent(
        f"""
        Você é um especialista em Git. 
        Analise o diff e crie uma mensagem de commit
        Siga essas regras:

        Formato:
        type: short end clear description (max 50 caracteres em inglês)

        Tipos permitidos com seus emojis:
        {commit_types_examples}

        - Bullet points opcionais para mais detalhes (se necessário e sempre em Português Brasil)
        - Máximo 2-3 bullets, cada um com máximo 100 caracteres

        Regras:
        1. Use verbos no imperativo
        2. Não termine com ponto
        3. Seja específico mas conciso
        4. Se tiver vários arquivos, foque na mudança principal
        5. Use APENAS os tipos listados acima
        6. NÃO inclua o emoji na mensagem, ele será adicionado automaticamente

        {style_prompt}

        Retorne APENAS a mensagem, sem explicações ou aspas.

        Referência de commits recentes do repo:
        {recent_commits}

        Alterações (diff):
        {diff}
        """
    )

    try:
        client = Client()
        providers = [Blackbox]
        last_error = None

        for provider in providers:
            try:
                response = client.chat.completions.create(
                    model="claude-3.5-sonnet",
                    provider=provider,
                    messages=[
                        {"role": "system", "content": PROMPT},
                        {"role": "user", "content": f"Recent commits:\n{recent_commits}"},
                        {"role": "user", "content": f"Changes:\n{diff}"},
                    ],
                )
                message = response.choices[0].message.content.strip()
                return clean_blackbox_message(message)
            except Exception as e:
                last_error = e
                continue

        if last_error:
            raise last_error

    except Exception as e:
        print(f"Erro ao gerar mensagem: {str(e)}")
        print("\nTentando provider alternativo...")

        try:
            from g4f.Provider import Bing

            response = client.chat.completions.create(
                model="gpt-4",
                provider=Bing,
                messages=[
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": f"Recent commits:\n{recent_commits}"},
                    {"role": "user", "content": f"Changes:\n{diff}"},
                ],
            )
            message = response.choices[0].message.content.strip()
            return clean_blackbox_message(message)
        except Exception as e:
            print(f"Erro no provider alternativo: {str(e)}")
            return None


def main():
    args = parse_arguments()

    if args.estilo != "padrao":
        print(f"🎨 Usando estilo: {args.estilo}")
    print("🔍 Analisando alterações...")

    diff = get_git_diff()
    if not diff:
        print("❌ Não existem mudanças staged para commit")
        sys.exit(1)

    recent_commits = get_recent_commits()

    print("💭 Gerando sugestão de commit...")
    commit_msg = generate_commit_message(diff, recent_commits, args.estilo)

    if commit_msg:
        print("\n📝 Sugestão de mensagem:\n")
        print(commit_msg)

        if args.accept:
            print("\n💣 Aceitando automáticamente a mensagem de commit!")
            response = "y"
        else:
            try:
                response = input("\n🤔 Deseja usar esta mensagem? [Y/n] ").strip().lower()
            except KeyboardInterrupt:
                print("\nOperação cancelada pelo usuário.")
                response = 'n'


        if response in ["y", "yes", ""]:
            tmp_file = os.path.expanduser("~/.git_commit_msg_tmp")
            with open(tmp_file, "w") as f:
                f.write(commit_msg)

            try:
                subprocess.run(["git", "commit", "-F", tmp_file], check=True)
                print("✅ Commit realizado com sucesso!")
            except subprocess.CalledProcessError:
                print("❌ Erro ao realizar o commit")

            os.remove(tmp_file)
        else:
            print("❌ Commit cancelado")
    else:
        print("❌ Não foi possível gerar a mensagem")
        sys.exit(1)


if __name__ == "__main__":
    main()
