"""
requirements:
    - keyboard
    - lk-logger >= 5.4.6
"""
import typing as t

import keyboard
import lk_logger
from keyboard import KeyboardEvent
from keyboard import _listener as os_listener  # noqa
from keyboard import _os_keyboard as os_keyboard  # noqa

lk_logger.setup(show_varnames=False)


def main():
    listener = Listener()
    listener.start_listening()
    keyboard.wait('esc')
    print('elegant exit')


def _intercept_capslock(key):
    print(key)
    pass


# noinspection PyMethodMayBeStatic
class Listener:
    store1: dict[str, int] = {}
    store2: list[str] = []
    _pressing = set()
    _hid = None  # hook id
    
    def start_listening(self):
        print('start listening', ':v2')
        self._hid = keyboard.hook(self.on_key, suppress=True)
    
    def _is_interceptable(self, key: str) -> bool:
        match key:
            case 'right shift':
                return True
            case 'caps lock':
                return True
            case _:
                return False
    
    def _is_storable(self, key: str) -> bool:
        match key:
            case 'right shift':
                return True
            case _:
                return False
    
    def on_key(self, key_evt: KeyboardEvent) -> None:
        """
        the trigger timing:
            by default: key-down triggers.
            some hesitant keys: key-up triggers.
        """
        # lk_logger.start_ipython({'key': key_evt})  # TEST
        key: str = key_evt.name
        
        if key == 'f8':
            self._exit()
            return
        
        if key_evt.event_type == 'down':
            if self.store2:
                for x in self.store2:
                    # self._send_key_code(key_evt.scan_code, True, False)
                    keyboard.send(x, True, False)
                self.store2.clear()
                self.store1.clear()
                
                print(':vs', key, '(down)')
                self._send_key_code(key_evt.scan_code, True, False)
                # keyboard.send(key, True, False)
                return
            
            if self._is_interceptable(key):
                self.store1[key] = len(self.store2)
                self.store2.append(key)
            else:
                print(':vs', key, '(down)')
                self._send_key_code(key_evt.scan_code, True, False)
                # keyboard.send(key, True, False)
        
        else:  # 'up'
            if key in self.store1:
                pos = self.store1[key]
                if pos == len(self.store2) - 1:
                    self._single_key_stroke(key)
                    self.store2.clear()
                    self.store1.clear()
                else:
                    raise Exception('unreachable case')
            
            else:
                print(':vs', key, '(up)')
                self._send_key_code(key_evt.scan_code, False, True)
                # keyboard.send(key, False, True)
    
    def _send_key_code(self, code: t.Any, press: bool, release: bool) -> None:
        """
        using this instead of `keyboard.send`, cause the latter has a bug in
        sending modifier keys.
        """
        os_listener.is_replaying = True
        if press:
            os_keyboard.press(code)
        if release:
            os_keyboard.release(code)
        os_listener.is_replaying = False
    
    def _single_key_stroke(self, key: str):
        match key:
            case 'right shift':
                print(':i', 'rshift -> underline')
                self._rshift_2_underline()
            case 'caps lock':
                print(':i', 'capslock -> ctrl + space')
                self._capslock_2_ctrl_space()
            case _:
                keyboard.send(key)
    
    # -------------------------------------------------------------------------
    # remapping
    
    def _rshift_2_underline(self):
        keyboard.send('shift + _')
    
    def _capslock_2_ctrl_space(self):
        keyboard.send('ctrl + space')
    
    # -------------------------------------------------------------------------
    
    def _exit(self):
        assert self._hid
        keyboard.unhook(self._hid)
        for key in self._pressing:
            keyboard.send(key, False, True)
        print('press esc to exit the program')


if __name__ == '__main__':
    main()
