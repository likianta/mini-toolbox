import streamlit as st


def main():
    st.title('LocalChat')
    if msg := st.text_area('Message'):
        print('\n' + msg.strip())


if __name__ == '__main__':
    # strun 2134 projects/local_chatapp/app.py
    main()
