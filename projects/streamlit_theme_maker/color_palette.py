from lk_utils import fs


def generate_toml_files():
    """
    doc: see `./readme.md`.
    """
    palette = fs.load(fs.xpath('catppuccin_palette.json'))
    for theme_name in ('latte', 'frappe', 'macchiato', 'mocha'):
        item = palette[theme_name]
        colors1 = {k: v['hex'] for k, v in item['colors'].items()}
        colors2 = {k: v['normal']['hex'] for k, v in item['ansiColors'].items()}
        
        # simple
        st_theme = {
            'base'                    : 'dark' if item['dark'] else 'light',
            'backgroundColor'         : colors1['base'],
            'secondaryBackgroundColor': colors1['crust'],
            # # this is subjective
            # # 'primaryColor'            : colors1['blue'],
            # workaround note:
            #   streamlit doesn't render `st.button(..., type='primary')`
            #   well in dark themes if we use `colors1['blue']`, because the
            #   button background color in inactive is too shallow with its
            #   button text. so we harden the primary color for dark themes to
            #   solve this.
            'primaryColor'            :
                '#3d7ce4' if item['dark'] else colors1['blue'],
            'textColor'               : colors1['text'],
        }
        fs.dump(
            {'theme': st_theme},
            fs.xpath('themes/simple/catppuccin-{}.toml'.format(theme_name))
        )
        
        st_theme.update({
            'redColor'           : colors2['red'],
            'orangeColor'        : colors1['peach'],
            'yellowColor'        : colors2['yellow'],
            'blueColor'          : colors2['blue'],
            'greenColor'         : colors2['green'],
            'violetColor'        : colors1['mauve'],
            'grayColor'          : colors1['overlay1'],
            'linkColor'          : colors1['blue'],
            'linkUnderline'      : True,
            'codeBackgroundColor': colors1['crust'],
            'borderColor'        : colors1['overlay0'],
            'showWidgetBorder'   : False,
            'showSidebarBorder'  : False,  # edit?
        })
        fs.dump(
            {'theme': st_theme},
            fs.xpath('themes/detailed/catppuccin-{}.toml'.format(theme_name))
        )


if __name__ == '__main__':
    generate_toml_files()
