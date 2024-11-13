#!/usr/bin/env python3

import subprocess
from g4f.client import Client
from g4f.Provider import Blackbox
import textwrap
import sys
import os
import re
import argparse
import json
from pathlib import Path

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

COMMIT_TYPES = {
    "feat": "✨",
    "fix": "🐛",
    "docs": "📚",
    "style": "💎",
    "refactor": "🔨",
    "perf": "🚀",
    "test": "🚨",
    "build": "📦",
    "ci": "👷",
    "chore": "🔧",
}

DEFAULT_CONFIG = {
    "commit_message": {"max_length": 50, "language": "en-US"},
    "description": {
        "format": "bullets",
        "max_bullets": 3,
        "max_bullet_length": 100,
        "max_paragraph_length": 300,
        "language": "pt-BR",
    },
    "shell_alias": "sca",
}

LANGUAGE_INSTRUCTIONS = {
    "en-US": {
        "commit": "Write the commit message in English",
        "desc_bullets": "Write bullet points in English",
        "desc_paragraph": "Write a detailed description in English as a paragraph. Do not use bullet points and write in a linear fashion, mentioning the specific files that were changed",
    },
    "pt-BR": {
        "commit": "Escreva a mensagem de commit em Português Brasil",
        "desc_bullets": "Escreva os bullet points em Português Brasil",
        "desc_paragraph": "Escreva uma descrição detalhada usando uma estrutura de parágrafos no idioma Português Brasil. Não use bullets e escreva de forma linear, sem parecer tópicos, especificando inclusive em qual arquivo foi feita a alteração",
    },
}


def load_config():
    config = DEFAULT_CONFIG.copy()
    config_paths = [Path.cwd() / ".gscrc", Path.home() / ".gscrc"]

    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path) as f:
                    user_config = json.load(f)
                    deep_update(config, user_config)
                break
            except json.JSONDecodeError:
                print(f"⚠️  Erro ao ler arquivo de configuração {config_path}. Usando configurações padrão.")

    return config


def deep_update(target, source):
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            deep_update(target[key], value)
        else:
            target[key] = value


def create_default_config():
    config_path = Path.home() / ".gscrc"
    if not config_path.exists():
        with open(config_path, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"✨ Arquivo de configuração criado em {config_path}")
        print("Você pode editar este arquivo para personalizar o comportamento do gerador de commits.")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Gerador de mensagens de commit com diferentes estilos")
    for style in STYLES.keys():
        parser.add_argument(
            f"--{style}", action="store_const", const=style, dest="estilo", help=STYLES[style]["description"]
        )
    parser.add_argument("--list", action="store_true", help="Lista todos os estilos disponíveis")
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
        return subprocess.check_output(["git", "diff", "--cached"], universal_newlines=True)
    except subprocess.CalledProcessError:
        return None


def get_recent_commits(num=3):
    try:
        return subprocess.check_output(["git", "log", f"-{num}", "--pretty=format:%B"], universal_newlines=True)
    except subprocess.CalledProcessError:
        return None


def clean_blackbox_message(message):
    message = re.sub(r"Generated by BLACKBOX\.AI.*?\n", "", message, flags=re.IGNORECASE).lstrip()
    for commit_type, emoji in COMMIT_TYPES.items():
        pattern = f"^{commit_type}:"
        if re.match(pattern, message):
            message = f"{commit_type} {emoji}: {message[len(commit_type)+1:].lstrip()}"
            break
    return message


def generate_description_format(config):
    desc_format = config["description"]["format"]
    if desc_format == "bullets":
        return f"""
        Formato da descrição:
        - Máximo {config['description']['max_bullets']} bullets
        - Cada bullet com máximo {config['description']['max_bullet_length']} caracteres"""
    else:
        return f"""
        Formato da descrição:
        - Descrição em formato de parágrafo
        - Máximo {config['description']['max_paragraph_length']} caracteres no total
        - Use quebras de linha entre parágrafos para melhor legibilidade"""


def generate_commit_message(diff, recent_commits, style, config):
    style_info = STYLES[style]
    commit_types_examples = "\n".join([f"- {type} {emoji}: descrição" for type, emoji in COMMIT_TYPES.items()])

    commit_lang = config["commit_message"]["language"]
    desc_lang = config["description"]["language"]
    desc_format = config["description"]["format"]
    desc_instructions = LANGUAGE_INSTRUCTIONS[desc_lang][
        "desc_bullets" if desc_format == "bullets" else "desc_paragraph"
    ]

    format_instructions = generate_description_format(config)

    prompt = textwrap.dedent(
        f"""
        Você é um especialista em Git. 
        Analise o diff e crie uma mensagem de commit seguindo RIGOROSAMENTE estas regras:

        Primeira linha (título do commit):
        - type: short and clear description (max {config['commit_message']['max_length']} caracteres)
        - {LANGUAGE_INSTRUCTIONS[commit_lang]['commit']}

        Tipos permitidos com seus emojis:
        {commit_types_examples}

        Descrição detalhada:
        {desc_instructions}

        {format_instructions}

        Regras gerais:
        1. Use verbos no imperativo
        2. Não termine com ponto
        3. Seja específico mas conciso
        4. Se tiver vários arquivos, mencione cada um e suas alterações
        5. Use APENAS os tipos listados acima
        6. NÃO inclua o emoji na mensagem, ele será adicionado automaticamente
        7. SEMPRE siga o formato de descrição especificado (bullets ou parágrafos)
        8. SEMPRE use o idioma especificado para cada parte

        Estilo adicional:
        {style_info['prompt_extra']}

        Retorne APENAS a mensagem, sem explicações ou aspas.

        Referência de commits recentes do repo:
        {recent_commits}

        Alterações (diff):
        {diff}
        """
    )

    try:
        client = Client()
        response = client.chat.completions.create(
            model="claude-3.5-sonnet",
            provider=Blackbox,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Recent commits:\n{recent_commits}"},
                {"role": "user", "content": f"Changes:\n{diff}"},
            ],
        )
        return clean_blackbox_message(response.choices[0].message.content.strip())
    except Exception as primary_error:
        print(f"Erro ao gerar mensagem: {str(primary_error)}")
        print("\nTentando provider alternativo...")
        try:
            from g4f.Provider import Bing

            response = client.chat.completions.create(
                model="gpt-4",
                provider=Bing,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Recent commits:\n{recent_commits}"},
                    {"role": "user", "content": f"Changes:\n{diff}"},
                ],
            )
            return clean_blackbox_message(response.choices[0].message.content.strip())
        except Exception as e:
            print(f"Erro no provider alternativo: {str(e)}")
            return None


def main():
    config = load_config()
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
    commit_msg = generate_commit_message(diff, recent_commits, args.estilo, config)

    if commit_msg:
        print("\n📝 Sugestão de mensagem:\n")
        print(commit_msg)
        response = input("\nDeseja usar esta mensagem? [Y/n] ").strip().lower()

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
    create_default_config()
    main()
