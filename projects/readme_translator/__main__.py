"""
prerequisites:
    1. gcloud auth
        scoop install gcloud
        gcloud init
            when asked to pick a project, choose the one starts with -
            'halogen...'
        gcloud auth list
        gcloud auth application-default login
    2. add 'config.yaml'
        project_id: halogen-...
        api_secret_key: ...
"""

import re
from uuid import uuid4

import lk_logger
from argsense import cli
from google.cloud import translate_v3 as google_trans
from lk_utils import fs
from markdown2 import markdown as md_2_html
from markdownify import markdownify as html_2_md  # html -> markdown


@cli.cmd()
def translate_readme_file(file_i: str, file_o: str = None) -> None:
    """
    translate readme.md from chinese to english.
    params:
        file_o:
            if not given, the output file will be named as '<input_name>.en.md'.
    devnote:
        since google cloud translation accepts html and plain text, but not -
        markdown, we need to firstly convert markdown to html, then translate, -
        finally convert html back to markdown.
    """
    if not file_o:
        file_o = fs.replace_ext(file_i, 'en.md')
    html_content, (code_blocks, placeholder_id) = (
        convert_md_to_html(fs.load(file_i))
    )
    html_content = translate_html(html_content)
    md_content = convert_html_to_md(html_content, code_blocks, placeholder_id)
    fs.dump(md_content, file_o)
    print(':r2', 'file size changed: {} -> {}'.format(
        fs.filesize(file_i, str), fs.filesize(file_o, str)
    ))
    print(':tv4', 'done', file_o)


def convert_md_to_html(md_content: str) -> tuple[str, tuple[list, str]]:
    md_without_code, code_blocks, placeholder_id = (
        _extract_code_blocks(md_content)
    )
    html_content = md_2_html(md_without_code)
    # bury placeholder_id into html tags, so that google won't translate it.
    html_content = html_content.replace(
        placeholder_id, '<!-- {} -->'.format(placeholder_id)
    )
    return html_content, (code_blocks, placeholder_id)


def _extract_code_blocks(md_content: str) -> tuple[str, list, str]:
    # untranslated placeholder
    placeholder_id = str(uuid4().int)  # generates a unique identifier
    pattern = re.compile(r'(```.*?```)', re.DOTALL)
    code_blocks = pattern.findall(md_content)
    text_without_code = pattern.sub(placeholder_id, md_content)
    return text_without_code, code_blocks, placeholder_id


def translate_html(html_content: str) -> str:
    """
    translate html content from chinese to english.
    https://cloud.google.com/translate/docs/advanced/translating-text-v3
        ?hl=zh-cn
    """
    cfg = fs.load(fs.xpath('config.yaml'))
    client = google_trans.TranslationServiceClient()
    with lk_logger.spinner('translating...'):
        response = client.translate_text(
            contents=[html_content],
            mime_type='text/html',
            parent='projects/{}/locations/global'.format(cfg['project_id']),
            source_language_code='zh-CN',
            target_language_code='en-US',
        )
    return response.translations[0].translated_text


def convert_html_to_md(
    html_content: str, code_blocks: list, placeholder_id
) -> str:
    print('<!-- {} -->'.format(placeholder_id) in html_content, ':v')
    html_content = html_content.replace(
        '<!-- {} -->'.format(placeholder_id), placeholder_id
    )
    md_without_code = html_2_md(
        html_content,
        heading_style='ATX',
        bullets='-',
        escape_underscores=False,
    )
    
    _i = -1
    
    def _insert_code_blocks(_):
        nonlocal _i
        _i += 1
        return code_blocks[_i]
    
    md_content = re.sub(
        placeholder_id,
        _insert_code_blocks,
        md_without_code,
    )
    return md_content


if __name__ == '__main__':
    # pox -m projects.readme_translator -h
    # pox -m projects.readme_translator translate-readme-file -h
    cli.run()
