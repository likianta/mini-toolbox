import asyncio
import pinkrain as pr


_history = []


def main():
    with pr.daisy.MainPage():
        with pr.comp.Column():
            with pr.html.textarea(
                cls='textarea textarea-bordered',
                placeholder='Type something...'
            ) as area:
                _temp_text = ''
                
                @area.on_change
                def _(e):
                    print(e, ':v')
                    nonlocal _temp_text
                    _temp_text = e['value']
            
            with pr.daisy.Button('Submit') as btn:
                @btn.on_click
                def _():
                    nonlocal _temp_text
                    if _temp_text:
                        print(_temp_text)
                        _history.append(_temp_text)
                        _temp_text = ''
                        area.text = ''
                        # area.attrs['value'] = ''
                    else:
                        print(':v3', 'nothing to commit')
        # asyncio.create_task(_auto_refresh_area(pr.comp.Column()))


async def _auto_refresh_area(placeholder: pr.comp.Column):
    session_id = placeholder.id.plain.split('_')[1]
    local_pointer = 0
    while True:
        await asyncio.sleep(1)
        if local_pointer < len(_history):
            msg = _history[local_pointer]
            with placeholder:
                pr.html.div(msg)
            placeholder.html = placeholder.render(True)  # workaround
            print(local_pointer, len(_history), session_id, placeholder.html, ':vsil')
            # pr.sync(session_id)
            pr.sync()
            local_pointer += 1


if __name__ == '__main__':
    # pox projects/localnet_chatapp/app_pr.py
    pr.app.run(main, host='0.0.0.0', port=2017, debug=True)
