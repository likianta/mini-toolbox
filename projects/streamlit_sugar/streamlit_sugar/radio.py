import typing as t
import streamlit as st


def radio_idx(
    label: str,
    options: t.Tuple[str, ...],
    index: int = 0,
    horizontal: bool = True,
) -> int:
    options = dict(enumerate(options))
    # FIXME: can keys be int type?
    return st.radio(
        label,
        options.keys(),
        format_func=lambda x: options[x],
        horizontal=horizontal,
        index=index,
    )


def radio_key(
    label: str,
    options: t.Dict[str, str],
    index: int = 0,
    horizontal: bool = True,
    **kwargs
) -> str:
    return st.radio(
        label,
        options.keys(),
        format_func=lambda x: options[x],
        horizontal=horizontal,
        index=index,
        **kwargs
    )
