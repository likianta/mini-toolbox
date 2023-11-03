"""
notice: this module should only be called in streamlit running session. -
see its only usage at `./ui_builder.py : main`.
"""
import atexit

import streamlit as st  # noqa
from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads


# def is_running_in_streamlit() -> bool:
#     try:
#         from streamlit.script_run_context import get_script_run_ctx  # noqa
#     except ModuleNotFoundError:
#         return False
#     else:
#         return bool(get_script_run_ctx())


def init_cache() -> None:
    print('init cache')
    st.session_state.cache = loads(_get_cache_file())


# @atexit.register  # FIXME: atexit not worked in Popen?
def save_cache() -> None:
    print('save cache', st.session_state.cache, ':l')
    dumps(dict(st.session_state.cache), _get_cache_file())


def _get_cache_file() -> str:
    if fs.exists(x := fs.xpath('../../_easy_submodule_cache.pkl')):
        # for project development
        cache_file = x
    else:
        cache_file = fs.xpath('./_cache.pkl')
        assert fs.exists(cache_file), cache_file
    return cache_file


# if is_running_in_streamlit():
#     print('init streamlit cache')
#     init_cache()
#     atexit.register(save_cache)
