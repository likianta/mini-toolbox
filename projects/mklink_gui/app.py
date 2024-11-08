import streamlit as st
import streamlit_canary as sc
from lk_utils import fs
from lk_utils.textwrap import dedent
from os.path import realpath

st.set_page_config('Make Link')

# _config = sc.session.init(
#     lambda: {
#         'recent_targets': []
#     }
# )


def main() -> None:
    with st.container(border=True):
        input_holder = st.empty()
        
        preset_dir_1 = r'C:/Likianta/workspace/dev_master_likianta'
        preset_dir_2 = r'C:/Likianta/workspace/com_jlsemi_likianta'
        preset = st.radio(
            'Quick select',
            sorted(
                (
                    f'{preset_dir_1}/aircontrol/airmise',
                    f'{preset_dir_1}/argsense-cli/argsense',
                    f'{preset_dir_1}/depsland',
                    f'{preset_dir_1}/lk-logger/lk_logger',
                    f'{preset_dir_1}/lk-utils/lk_utils',
                    f'{preset_dir_1}/mini-toolbox/projects/conflore/conflore',
                    f'{preset_dir_1}/mini-toolbox/projects/fake_typing/fake_typing',
                    f'{preset_dir_1}/pinkrain/pinkrain',
                    f'{preset_dir_1}/pyapp-window/pyapp_window',
                    f'{preset_dir_1}/pyportable-crypto/pyportable_crypto',
                    f'{preset_dir_1}/qmlease/qmlease',
                    f'{preset_dir_1}/streamlit-canary/streamlit_canary',
                    f'{preset_dir_2}/batch-dump-registers/batch_dump_registers',
                    f'{preset_dir_2}/debug-memory-ui/debug_memory_ui',
                    f'{preset_dir_2}/gaemei-test-database',
                    f'{preset_dir_2}/hummingbird-sdk-refactor/hummingbird',
                    f'{preset_dir_2}/omni-driver-kit/omni_driver_kit',
                    f'{preset_dir_2}/phy-driver-base',
                ),
                key=lambda x: x.rsplit('/', 1)[1],
            ),
            format_func=lambda x: x.rsplit('/', 1)[1]
        )
        
        with input_holder:
            path_i = st.text_input('Source', placeholder=preset)
            if path_i:
                path_i = fs.normpath(path_i)
                assert fs.exists(path_i)
            else:
                path_i = preset
    
    with st.container(border=True):
        path_o = st.text_input('Target')
        if path_o:
            path_o = fs.normpath(path_o)
            if fs.exists(path_o):
                if fs.islink(path_o):
                    if fs.normpath(realpath(path_o)) == path_i:
                        st.warning('Already linked')
                        return
                if fs.basename(path_o) != fs.basename(path_i):
                    path_o = '{}/{}'.format(path_o, fs.basename(path_i))
            else:
                assert fs.exists(fs.parent(path_o))
        else:
            return
    
    st.info(dedent(
        '''
        **Preview**
        
        :maple_leaf: :red[{}]

        :four_leaf_clover: :green[{}]
        '''.format(path_i, path_o)
    ))
    
    if sc.long_button('Make link', type='primary', disabled=fs.exists(path_o)):
        print('symlink: {} -> {}'.format(path_i, path_o), ':r2')
        fs.make_link(path_i, path_o)
        st.rerun()


if __name__ == '__main__':
    # strun 2009 projects/mklink_gui/app.py
    main()
