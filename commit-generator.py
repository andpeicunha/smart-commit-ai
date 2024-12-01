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
        "description": "Mensagens com um toque poético e lírico",
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
    "editor": {"command": "code", "args": ["--wait"], "fallback": {"command": "nano", "args": []}},
    "shell_alias": "sca",
    "ai": {"provider": "FreeGpt", "model": "gemini-pro"},
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


VERSION = "1.0.0"


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
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"✨ Arquivo de configuração criado em {config_path}")
        print("Você pode editar este arquivo para personalizar o comportamento do gerador de commits.")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Gerador de mensagens de commit com diferentes estilos")
    for style in STYLES.keys():
        parser.add_argument(
            f"--{style}", action="store_const", const=style, dest="estilo", help=STYLES[style]["description"]
        )
    parser.add_argument("--list", "-L", action="store_true", help="Lista todos os estilos disponíveis")
    parser.add_argument("--accept", "-A", action="store_true", help="Aceita automaticamente a mensagem criada")
    parser.add_argument("--desc", "-D", action="store_true", help="Remove a descrição na mensagem")
    parser.add_argument("--version", "-v", action="store_true", help="Mostra a versão atual")

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
        return subprocess.check_output(["git", "diff", "--cached"], text=True, encoding="utf-8")
    except subprocess.CalledProcessError:
        return None

def get_recent_commits(num=3):
    try:
        return subprocess.check_output(["git", "log", f"-{num}", "--pretty=format:%B"], text=True, encoding="utf-8")
    except subprocess.CalledProcessError:
        return None


def clean_blackbox_message(message, args):
    # Split message into lines
    lines = message.strip().split("\n")

    # Find the first line that starts with a commit type
    commit_line_index = -1
    for i, line in enumerate(lines):
        if any(line.startswith(commit_type) for commit_type in COMMIT_TYPES.keys()):
            commit_line_index = i
            break

    # If no valid commit line found, return original message
    if commit_line_index == -1:
        return message

    # Get the commit message starting from the commit line
    filtered_lines = lines[commit_line_index:]

    # If --desc flag is not used, join all lines
    # If --desc flag is used, only take the first line
    if args.desc:
        filtered_message = filtered_lines[0]
    else:
        filtered_message = "\n".join(filtered_lines)

    # Add emoji to the commit type
    for commit_type, emoji in COMMIT_TYPES.items():
        pattern = f"^{commit_type}:"
        if re.match(pattern, filtered_message):
            filtered_message = f"{commit_type} {emoji}: {filtered_message[len(commit_type)+1:].lstrip()}"
            break

    return filtered_message.strip()


def get_editor_command(config):
    """Determina o comando do editor a ser usado"""
    editor_config = config.get("editor", DEFAULT_CONFIG["editor"])

    # Tenta o editor configurado
    command = editor_config["command"]
    args = editor_config.get("args", [])

    # Verifica se o comando principal está disponível
    try:
        subprocess.run([command, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return command, args
    except (subprocess.SubprocessError, FileNotFoundError):
        # Se o comando principal falhar, tenta o fallback
        fallback = editor_config.get("fallback", {"command": "vim", "args": []})
        try:
            subprocess.run([fallback["command"], "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return fallback["command"], fallback.get("args", [])
        except (subprocess.SubprocessError, FileNotFoundError):
            # Se também falhar, tenta variáveis de ambiente
            env_editor = os.getenv("VISUAL") or os.getenv("EDITOR") or "vim"
            return env_editor, []


def edit_message(message, config):
    """Abre a mensagem no editor configurado para edição"""
    tmp_file = os.path.expanduser("~/.git_commit_msg_tmp")
    editor_command, editor_args = get_editor_command(config)

    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write(message)

        # Monta o comando completo
        cmd = [editor_command] + editor_args + [tmp_file]
        print(f"🖊️  Abrindo com: {' '.join(cmd)}")

        # Executa o editor
        process = subprocess.run(cmd, check=True)

        if process.returncode == 0:
            with open(tmp_file, "r") as f:
                edited_message = f.read().strip()
            return edited_message
        return None
    except subprocess.CalledProcessError:
        print(f"❌ Erro ao abrir o editor {editor_command}")
        print("💡 Você pode configurar outro editor no arquivo .gscrc")
        return None
    except Exception as e:
        print(f"❌ Erro ao editar a mensagem: {str(e)}")
        return None
    finally:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)


def format_commit_message(message):
    """
    Format the commit message with proper spacing and line breaks.
    Expects format: type emoji: title\n\ndescription
    """
    # Split into title and description
    parts = message.split("\n", 1)
    title = parts[0].strip()
    description = parts[1].strip() if len(parts) > 1 else ""

    # Format title - ensure proper spacing around emoji
    title_parts = title.split(":", 1)
    if len(title_parts) == 2:
        type_and_emoji = title_parts[0].strip()
        title_text = title_parts[1].strip()

        # Ensure space between type and emoji
        type_emoji = " ".join(type_and_emoji.split())

        title = f"{type_emoji}: {title_text}"

    # Format description - normalize spacing and line breaks
    if description:
        # Convert runs of whitespace to single spaces
        description = " ".join(description.split())

        # Add proper line breaks for bullet points
        if "-" in description:
            description = description.replace(" - ", "\n- ")
            if not description.startswith("-"):
                description = f"\n{description}"

        # Wrap long lines
        if not description.startswith("-"):
            description = textwrap.fill(description, width=80)

    # Combine title and description
    final_message = title
    if description:
        final_message = f"{title}\n\n{description}"

    return final_message


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


def generate_commit_message(diff, recent_commits, style, config, args):
    style_info = STYLES[style]
    commit_types_examples = "\n".join([f"- {type} {emoji}: descrição" for type, emoji in COMMIT_TYPES.items()])

    commit_lang = config["commit_message"]["language"]
    desc_lang = config["description"]["language"]
    desc_format = config["description"]["format"]
    desc_instructions = LANGUAGE_INSTRUCTIONS[desc_lang][
        "desc_bullets" if desc_format == "bullets" else "desc_paragraph"
    ]

    if args.desc:
        desc_instructions = ""
        format_instructions = ""
    else:
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
        {"" if args.desc else f'''
        Descrição detalhada:
        {desc_instructions}
        {format_instructions}
        '''}
        Regras gerais:
        1. Use verbos no imperativo
        2. Para o descritivo sempre use o imperativo no passado, por exemplo, adicionei, inseri, coloquei
        3. Não termine com ponto
        4. Seja específico mas conciso
        5. Se tiver vários arquivos, mencione cada um e suas alterações
        6. Use APENAS os tipos listados acima
        7. NÃO inclua o emoji na mensagem, ele será adicionado automaticamente
        8. SEMPRE siga o formato de descrição especificado (bullets ou parágrafos)
        9. SEMPRE use o idioma especificado para cada parte

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
        provider_name = config["ai"].get("provider", "FreeGpt")
        model = config["ai"].get("model", "gemini-pro")
        print(f"🧠 Usando provedor de IA: {provider_name}, modelo: {model}")

        try:
            provider_module = __import__("g4f.Provider", fromlist=[provider_name])
            provider_class = getattr(provider_module, provider_name)
        except (ImportError, AttributeError) as e:
            print(f"⚠️  Erro ao carregar o provedor {provider_name}. Usando FreeGpt como fallback.")
            from g4f.Provider import FreeGpt
            provider_class = FreeGpt

        response = client.chat.completions.create(
            model=model,
            provider=provider_class,
            messages=[{"role": "system", "content": prompt}],
        )

        raw_message = response.choices[0].message.content.strip()
        return clean_blackbox_message(raw_message, args)

    except Exception as e:
        print(f"❌ Erro no provider ou na geração da mensagem: {str(e)}")
        return None


def main():
    if "--version" in sys.argv:
        print(f"Smart Commit AI v{VERSION}")
        sys.exit(0)

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
    commit_msg = generate_commit_message(diff, recent_commits, args.estilo, config, args)

    if commit_msg:
        while True:
            print("\n📝 Sugestão de mensagem:\n")
            print(commit_msg)

            if args.accept:
                print("\n💣 Aceitando automáticamente a mensagem de commit!")
                response = "y"
            else:
                try:
                    response = input("\n🤔 Deseja usar esta mensagem? [Y/n/e] ").strip().lower()
                except KeyboardInterrupt:
                    print("\nOperação cancelada pelo usuário.")
                    sys.exit(0)

            if response in ["y", "yes", ""]:
                tmp_file = os.path.expanduser("~/.git_commit_msg_tmp")
                with open(tmp_file, "w", encoding="utf-8") as f:
                    f.write(commit_msg)
                try:
                    subprocess.run(["git", "commit", "-F", tmp_file], check=True)
                    print("✅ Commit realizado com sucesso!")
                except subprocess.CalledProcessError:
                    print("❌ Erro ao realizar o commit")
                finally:
                    os.remove(tmp_file)
                break
            elif response == "e":
                print("\n📝 Abrindo mensagem para edição...")
                edited_msg = edit_message(commit_msg, config)
                if edited_msg:
                    print("\n📝 Mensagem editada:\n")
                    print(edited_msg)
                    commit_msg = edited_msg
                    continue
                else:
                    print("❌ Falha ao editar a mensagem")
                    sys.exit(1)
            elif response in ["n", "no"]:
                print("❌ Commit cancelado")
                sys.exit(0)
            else:
                print("⚠️  Opção inválida. Use Y para confirmar, n para cancelar ou e para editar.")
    else:
        print("❌ Não foi possível gerar a mensagem")
        sys.exit(1)


if __name__ == "__main__":
    create_default_config()
    main()