import streamlit as st
import streamlit_canary as sc
from collections import deque
from lk_utils import fs
from lk_utils import dedent
from os.path import realpath

_data: dict  # {'preset': [str, ...], 'history': [str, ...]}
if not (_data := sc.session.get_data(2)):
    _data.update({
        'preset': tuple(sorted(
            fs.load(fs.xpath('preset.yaml')),
            key=lambda x: x.rsplit('/', 1)[1],
        )),
        'history': deque(maxlen=20),
    })


def main() -> None:
    with st.container(border=True):
        input_holder = st.empty()
        tabs = iter(st.tabs(('Quick select', 'History select')))
        with next(tabs):
            preset = st.radio(
                'Select from preset',
                _data['preset'],
                format_func=lambda x: x.rsplit('/', 1)[1]
            )
        with next(tabs):
            def shortify_path(path: str) -> str:
                segs = path.split('/')
                if len(segs) > 4:
                    return '{}/{}/.../{}/{}'.format(
                        segs[0], segs[1], segs[-2], segs[-1]
                    )
                else:
                    return path
            
            hist = st.radio(
                'Select from history',
                _data['history'],
                format_func=shortify_path
            )
        with input_holder:
            path_i = st.text_input('Source', placeholder=preset)
            if path_i:
                path_i = fs.normpath(path_i)
            else:
                path_i = preset
    
    with st.container(border=True):
        path_o = st.text_input('Target')
        if path_o:
            path_o = fs.normpath(path_o)
            if fs.exist(path_o):
                if fs.islink(path_o):
                    if fs.normpath(realpath(path_o)) == path_i:
                        st.success('Linked')
                        return
                if fs.basename(path_o) != fs.basename(path_i):
                    path_o = '{}/{}'.format(path_o, fs.basename(path_i))
            else:
                assert fs.exist(fs.parent(path_o))
        else:
            return
    
    st.info(dedent(
        '''
        **Preview**
        
        :maple_leaf: :red[{}]

        :four_leaf_clover: :green[{}]
        '''.format(path_i, path_o)
    ))
    
    if sc.long_button('Make link', type='primary', disabled=fs.exist(path_o)):
        assert fs.exist(path_i)
        print('symlink: {} -> {}'.format(path_i, path_o), ':r2')
        fs.make_link(path_i, path_o)
        st.rerun()


# def _quick_select():
#     input_holder = st.empty()
#     preset = st.radio(
#         'Quick select',
#         _data['preset'],
#         format_func=lambda x: x.rsplit('/', 1)[1]
#     )
#     with input_holder:
#         path_i = st.text_input('Source', placeholder=preset)
#         if path_i:
#             path_i = fs.normpath(path_i)
#             assert fs.exist(path_i)
#         else:
#             path_i = preset


if __name__ == '__main__':
    # strun 2009 projects/mklink_gui/app.py
    st.set_page_config('Make Link')
    main()
