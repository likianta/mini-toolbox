from argsense import cli
from lk_utils.filesniff import normpath


@cli.cmd()
def md2md(file_i, file_o=''):
    from . import md_2_md
    file_i = normpath(file_i)
    file_o = normpath(file_o) if file_o else file_i[:-3] + '.b64.md'
    return md_2_md(file_i, file_o)


@cli.cmd()
def md2html(file_i, file_o=''):
    from . import md_2_html
    file_i = normpath(file_i)
    file_o = normpath(file_o) if file_o else file_i[:-3] + '.b64.html'
    return md_2_html(file_i, file_o)


@cli.cmd()
def html2html(file_i, file_o: str = '') -> str:
    from . import html_2_html
    file_i = normpath(file_i)
    file_o = normpath(file_o) if file_o else file_i[:-5] + '.b64.html'
    return html_2_html(file_i, file_o)


if __name__ == '__main__':
    # pox -m projects.markdown_image_base64.md_img_b64 -h
    # pox -m projects.markdown_image_base64.md_img_b64 md2html ...
    cli.run()
