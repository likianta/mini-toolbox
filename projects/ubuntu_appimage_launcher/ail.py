"""
add an Appimage to the launcher pad.
"""
import os.path
import re

import cairosvg
import lk_logger
from argsense import cli
from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads
from lk_utils import run_cmd_args

lk_logger.setup(quiet=True, show_funcname=False, show_varnames=True)


@cli.cmd()
def main(app_path: str) -> None:  # DELETE
    """
    https://askubuntu.com/questions/1311600/
    """
    assert app_path.endswith('.Appimage'), 'not an Appimage file!'
    app_path = fs.abspath(app_path)
    app_name = fs.basename(app_path)
    
    # mount records
    mlist = run_cmd_args('mount', shell=True, verbose=True).splitlines()
    # print(mlist, app_name, ':lv')
    
    mnames = {}
    for line in mlist:
        # e.g.: 'qq-3.1.2.Appimage on /tmp/.mount_qq-3.1sco4jk type fuse.qq \
        # -3.1.2.Appimage (ro,nosuid,nodev,relatime,user_id=1000,group_id=1000)'
        segs = line.split()
        mnames[segs[0]] = segs[2]
    # mnames = tuple(line.split()[0] for line in mlist)
    print(mnames, ':lv')
    
    # get the tmp path
    if app_name not in mnames:
        print('app not mounted! please make sure you have launched it.', ':v4')
        return
    tmp_path = mnames[app_name]
    
    # find the icon
    if x := tuple(f.path for f in fs.find_files(tmp_path, '.png')):
        assert len(x) == 1, ('multiple icons found!', x)
        icon_path = x[0]
    else:
        print('no icon found!', tmp_path, ':v4')
        return
    
    # find the desktop file
    icon_name = fs.basename(icon_path, False)
    if fs.exists(x := f'{tmp_path}/{icon_name}.desktop'):
        desktop_path = x
    else:  # FIXME: maybe we need to fallback to query `*.desktop` file.
        print('the expected desktop file not exist!', x, ':v4')
        return
    
    # dump icon
    home_dir = os.path.expanduser('~')
    fs.copy_file(
        icon_path,
        x := '{}/.local/share/icons/{}'.format(
            home_dir, fs.basename(icon_path)
        ),
        True,
    )
    icon_path = fs.abspath(x)
    
    # dump desktop file
    content = loads(desktop_path, 'plain')
    content = (
        content.replace(
            'Exec=',
            'Exec={}/{} '.format(
                fs.dirname(app_path),
                fs.basename(app_path, False),
            ),
        ).replace(
            'TryExec=',
            'TryExec={}/{} '.format(
                fs.dirname(app_path),
                fs.basename(app_path, False),
            ),
        )
        # .replace(
        #     'Icon=',
        #     'Icon={} '.format(
        #         fs.basename(icon_path, False),
        #     ),
        # )
    )
    content = re.sub(
        r'Icon=.*',
        'Icon={}'.format(fs.basename(icon_path, False)),
        content,
    )
    dumps(
        content,
        x := '{}/.local/share/applications/{}'.format(
            home_dir, fs.basename(desktop_path)
        ),
        'plain',
    )
    desktop_path = fs.abspath(x)
    
    print(
        'app successfully added to launcher pad',
        app_path,
        icon_path,
        desktop_path,
        ':tv2l',
    )


@cli.cmd()
def create_desktop(
    app_path: str,
    app_name: str,
    icon_name: str = None,
    show_terminal: bool = False,
    check_running: bool = True,
) -> None:
    """
    ref:
        how to create desktop file: https://askubuntu.com/questions/1403802/
        replacing system icons: https://www.solvetechnow.com/post/how-to \
        -change-app-icon-in-ubuntu
        custom icons: https://github.com/vinceliuice/WhiteSur-icon-theme
    
    kwargs:
        check_running (-r):
    """
    if check_running and _is_mounted(fs.basename(app_path)):
        print(
            'app is running, please consider closing it first! '
            'otherwise you may have to kill the process in system monitor '
            'manually.',
            ':v3',
        )
        if input('continue? [y/N] ') not in ('y', 'Y'): return
    
    home_dir = os.path.expanduser('~')
    icon_root = '{}/.local/share/icons'.format(home_dir)
    if icon_name:
        assert icon_name.endswith(('.png', '.svg'))
        if os.path.isabs(icon_name):
            icon_path = icon_name
            if icon_path.startswith(icon_root):
                icon_name = fs.relpath(icon_path, icon_root)
            else:
                fs.copy_file(
                    icon_name,
                    y := '{}/{}'.format(icon_root, x := fs.basename(icon_name)),
                    True,
                )
                icon_name = x
                icon_path = y
        else:
            icon_path = '{}/{}'.format(icon_root, icon_name)
        if icon_name.endswith('.svg'):
            icon_path = _convert_svg_to_png(icon_path)
            icon_name = icon_name.replace('.svg', '.png')
        assert fs.exists(icon_path)
    del icon_root
    
    output = [
        '[Desktop Entry]',
        'Name={}'.format(app_name),
        'Exec={} %f'.format(fs.abspath(app_path)),
        icon_name and 'Icon={}'.format(icon_name.removesuffix('.png')),
        'Terminal={}'.format('true' if show_terminal else 'false'),
        'Type=Application',
    ]
    output = '\n'.join(filter(None, output))
    dumps(
        output,
        desktop_path := '{}/.local/share/applications/{}.desktop'.format(
            home_dir, app_name.lower().replace(' ', '-').replace('_', '-')
        ),
    )
    print(desktop_path, ':tv2')


@cli.cmd('convert-icon')
def _convert_svg_to_png(svg_path: str, png_path: str = None) -> str:
    if png_path is None:
        png_path = svg_path.replace('.svg', '.png')
    cairosvg.svg2png(url=svg_path, write_to=png_path)
    return png_path


def _is_mounted(appimage_name: str) -> bool:
    mlist = run_cmd_args('mount', shell=True, verbose=True).splitlines()
    mnames = tuple(line.split()[0] for line in mlist)
    return appimage_name in mnames


if __name__ == '__main__':
    # pox projects/ubuntu_appimage_launcher/ail.py -h
    # pox projects/ubuntu_appimage_launcher/ail.py create-desktop $appimage \
    #   $appname
    # pox projects/ubuntu_appimage_launcher/ail.py create-desktop \
    #   /home/likianta/Desktop/apps /clash/clash-verge-1.3.5.AppImage \
    #   'Clash Verge' /home/likianta/.local /share/icons/whitesur-apps \
    #   /akonadiconsole.svg -R
    # pox projects/ubuntu_appimage_launcher/ail.py convert-icon $svg_path
    cli.run()
