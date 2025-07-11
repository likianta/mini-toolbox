import streamlit as st
import streamlit_canary as sc
from lk_utils import fs
from lk_utils import dedent
from os.path import realpath

if not (_data := sc.session.get_data(1)):
    dir1 = r'C:/Likianta/workspace/dev.master.likianta'
    dir2 = r'C:/Likianta/workspace/com.jlsemi.likianta'
    _data.update({
        'preset_dirs': tuple(sorted(
            (
                f'{dir1}/airmise/airmise',
                f'{dir1}/argsense-cli/argsense',
                f'{dir1}/depsland',
                f'{dir1}/lk-logger/lk_logger',
                f'{dir1}/lk-utils/lk_utils',
                f'{dir1}/mini-toolbox/projects/conflore/conflore',
                f'{dir1}/mini-toolbox/projects/fake_typing/fake_typing',
                f'{dir1}/pinkrain/pinkrain',
                f'{dir1}/pyapp-window/pyapp_window',
                f'{dir1}/pyportable-crypto/pyportable_crypto',
                f'{dir1}/python-tree-shaking/tree_shaking',
                f'{dir1}/qmlease/qmlease',
                f'{dir1}/remote-ipython/remote_ipython',
                f'{dir1}/streamlit-canary/streamlit_canary',
                f'{dir2}/batch-dump-registers/batch_dump_registers',
                f'{dir2}/debug-memory-ui/debug_memory_ui',
                f'{dir2}/gaemei-test-database',
                f'{dir2}/hummingbird-sdk-refactor/hummingbird',
                f'{dir2}/omni-driver-kit/omni_driver_kit',
                f'{dir2}/phy-driver-base',
            ),
            key=lambda x: x.rsplit('/', 1)[1],
        ))
    })


def main() -> None:
    with st.container(border=True):
        input_holder = st.empty()
        preset = st.radio(
            'Quick select',
            _data['preset_dirs'],
            format_func=lambda x: x.rsplit('/', 1)[1]
        )
        with input_holder:
            path_i = st.text_input('Source', placeholder=preset)
            if path_i:
                path_i = fs.normpath(path_i)
                assert fs.exist(path_i)
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
        print('symlink: {} -> {}'.format(path_i, path_o), ':r2')
        fs.make_link(path_i, path_o)
        st.rerun()


if __name__ == '__main__':
    # strun 2009 projects/mklink_gui/app.py
    st.set_page_config('Make Link')
    main()
