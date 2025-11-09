import os
import textwrap
import yaml
from babel.dates import format_datetime
from datetime import datetime


# --- CONFIGURATION ---

TEMPLATE_PATH        = '../html-templates/base.html'
CONTENT_DIR          = '../html-content'
EXTRA_HEAD_DIR       = '../html-extra-head/'
EXTRA_SCRIPTS_DIR    = '../html-extra-scripts/'
OUTPUT_DIR           = '../_site'
TRANSLATIONS_PATH    = 'translations.yml'
ALTERNATE_LINKS_PATH = 'alternate-links.yml'


# --- READ FILES ---

def read_translations():
    with open(TRANSLATIONS_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def read_alternate_links():
    with open(ALTERNATE_LINKS_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def read_template():
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def read_content(content_path):
    with open(content_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_extra_head(extra_head_path):
    if os.path.isfile(extra_head_path):
        with open(extra_head_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return ''

def read_extra_scripts(extra_scripts_path):
    if os.path.isfile(extra_scripts_path):
        with open(extra_scripts_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return ''


# --- EXTRACT INFO ---

def get_last_modified(file_path, lang):
    timestamp = os.path.getmtime(file_path)
    date = datetime.fromtimestamp(timestamp)
    if lang == 'en':
        #date_human = date.strftime('%d/%m/%Y at %Hh%M')
        date_human = format_datetime(date, "MMMM d, y 'at' h:mm a", locale=lang)
    if lang == 'fr':
        #date_human = date.strftime('%d/%m/%Y à %Hh%M')
        date_human = format_datetime(date, "'le' d MMMM y 'à' HH'h'mm", locale=lang)
    date_machine = date.isoformat(timespec='minutes')
    return date_human, date_machine

def get_lang_and_filename(path):
    """Déduit la langue (fr/en) et le nom de fichier à partir du chemin complet."""
    parts = os.path.normpath(path).split(os.sep)
    if len(parts) >= 3:
        lang = parts[-2]
        filename = os.path.basename(path)
        return lang, filename
    exit(1)

# --- BUILD PAGE ---

def build_page(template, content_path, translations, alternate_links):
    # Reading content
    content = read_content(content_path)
    # Indente le contenu pour qu'il soit bien aligné dans le template
    content = textwrap.indent(content, '      ')
    
    # Extract info from path
    lang, filename = get_lang_and_filename(content_path)

    # Reading extra head (if exists)
    extra_head = read_extra_head(EXTRA_HEAD_DIR + f'{lang}/' + filename)
    # Indente l'extra head pour qu'il soit bien aligné dans le template
    extra_head = textwrap.indent(extra_head, '      ')

    # Reading extra scripts (if exists)
    extra_scripts = read_extra_scripts(EXTRA_SCRIPTS_DIR + f'{lang}/' + filename)
    # Indente l'extra scripts pour qu'il soit bien aligné dans le template
    extra_scripts = textwrap.indent(extra_scripts, '    ')

    # Initialize the final page to the html template
    page = template

    # Injecting alternate links
    if lang == 'fr':
        page = page.replace('{{ alternate_link_en }}', alternate_links['fr'][filename])
        page = page.replace('{{ alternate_link_fr }}', filename)
    if lang == 'en':
        page = page.replace('{{ alternate_link_en }}', filename)
        page = page.replace('{{ alternate_link_fr }}', alternate_links['en'][filename])
    # Injecting extra head
    page = page.replace('{{ extra_head }}', extra_head)
    # Injecting static language-dependent text according to the .yaml file
    page = page.replace('{{ lang }}', lang)
    for key, value in translations[lang].items():
        placeholder = f"{{{{ {key} }}}}"   # --> produit une vraie chaîne "{{ key }}"
        page = page.replace(placeholder, value)
    # Completing with the content
    page = page.replace('{{ content }}', content)
    # Updating last modified
    last_modified_human, last_modified_machine = get_last_modified(content_path, lang)
    page = (
        page
        .replace('{{ last_modified_machine }}', last_modified_machine)
        .replace('{{ last_modified_human }}', last_modified_human)
    )
    # Injecting extra scirpt
    page = page.replace('{{ extra_scripts }}', extra_scripts)
    
    return page

def write_output(output_path, html):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


# --- MAIN ---

def main():
    template = read_template()
    translations = read_translations()
    alternate_links = read_alternate_links()

    for root, _, files in os.walk(CONTENT_DIR):
        for file in files:
            if not file.endswith('.html'):
                continue
            content_path = os.path.join(root, file)
            relative_path = os.path.relpath(content_path, CONTENT_DIR)
            output_path = os.path.join(OUTPUT_DIR, relative_path)
            
            html = build_page(template, content_path, translations, alternate_links)
            write_output(output_path, html)
            print(f"Fichier '{output_path}' généré avec succès")

if __name__ == '__main__':
    main()
