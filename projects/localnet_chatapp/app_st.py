import asyncio
import streamlit as st
import time
# from collections import deque
from functools import partial
from lk_utils import new_thread
# from streamlit_server_state import server_state
# from streamlit_server_state import server_state_lock


def main():
    history = _get_history()
    
    # with st.container(border=True):
    text = st.text_area(
        'Type something',
        value='',
        height=200,
        key='main_input'
    )
        
    cols = st.columns(3)
    with cols[0]:
        st.button(
            'Commit', 
            on_click=partial(_commit, history, text), 
            # disabled=not text,
            use_container_width=True
        )
        # if st.button('Commit', disabled=not text):
        #     history.insert(0, text)
        #     # if 'main_input' in st.session_state:
        #     st.session_state['main_input'] = ''
        #     # st.rerun()
    with cols[1]:
        if st.button('Refresh', use_container_width=True):
            pass
    with cols[2]:
        if st.button('Clear', use_container_width=True):
            history.clear()
    
    for x in history[:100]:
        st.code(x, language='plaintext', wrap_lines=True)
    # if msg := st.chat_input('Type something...'):
    #     # history.insert(0, msg)
    #     history.append(msg)
    # for msg in history[-100:]:
    #     st.chat_message('user').write(msg)
    # asyncio.run(_update_chat_zone(st.empty(), history))
    # _update_chat_zone_2(st.empty(), history)


def _commit(history, text):
    if not text:
        print('no text to commit')
        return
    history.insert(0, text)
    st.session_state['main_input'] = ''


@new_thread(singleton=True)
def _update_chat_zone_2(placeholder, history):
    # history = _get_history()
    while True:
        time.sleep(0.1)
        with placeholder:
            for msg in history[-100:]:
                st.chat_message('user').write(msg)


async def _update_chat_zone(placeholder, history):
    # history = _get_history()
    # old_len = 0
    while True:
        await asyncio.sleep(0.1)
        # print(len(history), ':iv')
        with placeholder:
            with st.container():
                for msg in history[-100:]:
                    st.chat_message('user').write(msg)
                    # st.code(msg, language='plaintext')
        # new_len = len(history)
        # if new_len != old_len:
        #     with placeholder:
        #         for msg in history[-100:]:
        #             st.chat_message('user').write(msg)
        #     old_len = new_len


@st.cache_resource
def _get_history():
    # return deque()
    return []


if __name__ == '__main__':
    # strun 2017 projects/localnet_chatapp/app_st.py
    main()
