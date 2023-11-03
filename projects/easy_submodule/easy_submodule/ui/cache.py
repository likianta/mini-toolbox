import atexit

import streamlit as st
from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads


def init_cache() -> None:
    st.session_state.cache = loads(_get_cache_file())


@atexit.register
def save_cache() -> None:
    dumps(dict(st.session_state.cache), _get_cache_file())


def _get_cache_file() -> str:
    if fs.exists(x := fs.xpath('../../_easy_submodule_cache.pkl')):
        # for project development
        cache_file = x
    else:
        cache_file = fs.xpath('./_cache.pkl')
        assert fs.exists(cache_file), cache_file
    return cache_file
