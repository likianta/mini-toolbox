import streamlit as st

from projects.file_renamer_pro import rename


def main() -> None:
    path = st.text_input('Input dirpath')
    if path:
        with st.spinner('renaming files...'):
            rename.main(path)


if __name__ == '__main__':
    # strun 3002 projects/file_renamer_pro/ui.py
    st.set_page_config(page_title='File Renamer Pro')
    main()
