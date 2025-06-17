from argsense import cli
from datetime import datetime
from lk_logger import track
from time import sleep
from windows_toasts import Toast
from windows_toasts import WindowsToaster


@cli
def notify_me(
    clock: str, remark: str = 'Alarming at "{}"', advance: int = 0
) -> None:
    """
    params:
        clock: "<hh:mm>" format. e.g. "14:30".
            tip: both "09:30" and "9:30" are valid.
            both 12-hour and 24-hour are supported, it is auto detected. for -
            example, if you set "8:30" in the morning (before 8:30), the -
            target time will be 8:30 AM, if you set "8:30" in the afternoon, -
            will be 8:30 PM.
    """
    duration = _get_duration(clock) - advance
    assert duration > 0
    for _ in track(range(duration), 'Waiting for alarm...'):
        sleep(1)
    toaster = WindowsToaster('LK Alarm Clock')
    toast = Toast()
    toast.text_fields = [remark.format(clock)]
    toaster.show_toast(toast)


def _get_duration(target_time: str) -> int:
    now = datetime.now()
    hh, mm = map(int, target_time.split(':'))
    if now.hour > 12 > hh:
        hh += 12
    complete_target_time = now.replace(
        hour=hh, minute=mm, second=0, microsecond=0
    )
    duration = (complete_target_time - now).total_seconds()
    return round(duration)


if __name__ == '__main__':
    # pox projects/alarm_clock/alarm_clock.py -h
    cli.run(notify_me)
