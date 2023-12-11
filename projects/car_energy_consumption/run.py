import re
import streamlit as st
import sys
from argsense import cli

from lk_utils import run_cmd_args
from lk_utils.textwrap import dedent
from lk_utils.time_utils import timestamp


@cli.cmd()
def run_st(port: int = 2020) -> None:
    run_cmd_args(
        (sys.executable, '-m', 'streamlit', 'run'),
        (__file__, 'setup-ui'),
        ('--browser.gatherUsageStats', 'false'),
        ('--server.headless', 'true'),
        ('--server.port', port),
        ignore_return=True,
        verbose=True,
    )


@cli.cmd('setup-ui')
def main() -> None:
    st.title('OraCat Car Energy Consumption Statistic')
    
    if 'init' not in st.session_state:
        st.session_state.init = True
        st.session_state.estm_start = 0
        st.session_state.percent_start = 0
        st.session_state.total_start = 0
    
    with st.expander('Quick input', False):
        text = st.text_area(
            'Shorthand record',
            placeholder='<estimated_mileage> <percentage> <total_mileage>'
        )
        if text and (m := re.search(r'(\d+) +(\d+) +(\d+)', text)):
            a, b, c = map(int, m.groups())
            st.session_state.estm_start = a
            st.session_state.percent_start = b
            st.session_state.total_start = c
    
    with st.expander('Starting status', True):
        c0, c1, c2 = st.columns(3)
        estm_start: int = c0.number_input(
            'Estimated battery mileage',
            min_value=0,
            max_value=500,
            value=st.session_state.estm_start,
            key='estm_start_input'
        )
        percent_start: int = c1.number_input(
            'Percentage',
            min_value=0,
            max_value=100,
            value=st.session_state.percent_start,
            key='percent_start_input'
        )
        total_start: int = c2.number_input(
            'Total mileage',
            value=st.session_state.total_start,
            key='total_start_input'
        )
    
    with st.expander('Ending status', True):
        c0, c1, c2 = st.columns(3)
        estm_end: int = c0.number_input(
            'Estimated battery mileage',
            min_value=0,
            max_value=500,
            key='estm_end_input'
        )
        percent_end: int = c1.number_input(
            'Percentage',
            min_value=0,
            max_value=100,
            key='percent_end_input'
        )
        total_end: int = c2.number_input(
            'Total mileage',
            min_value=0,
            max_value=total_start + 1000,
            # value=total_start,
            key='total_end_input'
        )
    
    if all((
        estm_start, percent_start, total_start,
        estm_end, percent_end, total_end
    )):
        if st.button('Save'):
            st.session_state.estm_start = estm_end
            st.session_state.percent_start = percent_end
            st.session_state.total_start = total_end
            st.rerun()
        else:
            st.session_state.estm_start = estm_start
            st.session_state.total_start = total_start
            
            if (
                (estm_start > estm_end > 0) and
                (percent_start > 0 and percent_end > 0) and
                (0 < total_start < total_end)
            ):
                template = dedent('''
                    ```
                    - 时间: {time}
                    - 表显:
                        - 开始时: {estm_start}km, {percent_start}% (满续航评估 {estm_full_start}km)
                        - 结束时: {estm_end}km, {percent_end}% (满续航评估 {estm_full_end}km)
                        - 消耗 {exp_cost}km
                    - 实际:
                        - 开始时里程: {total_start}km
                        - 结束时里程: {total_end}km
                        - 增长 {real_cost}km, 达成率 {diff_ratio}%
                    ```
                ''', join_sep='\\')
                
                # noinspection PyStringFormat
                st.markdown(template.format(
                    time='{}-{}-{} {}:{}'.format(
                        *(timestamp('y m d h').split(' ')),
                        _round_minute(int(timestamp('n'))),
                    ),
                    
                    estm_start=estm_start,
                    percent_start=percent_start,
                    estm_full_start=_estimate_full_mileage(
                        estm_start, percent_start),
                    
                    estm_end=estm_end,
                    percent_end=percent_end,
                    estm_full_end=_estimate_full_mileage(estm_end, percent_end),
                    exp_cost=(exp_cost := abs(estm_end - estm_start)),
                    
                    total_start=total_start,
                    total_end=total_end,
                    real_cost=(real_cost := abs(total_end - total_start)),
                    diff_ratio=round(real_cost / exp_cost * 100),
                ))


def _estimate_full_mileage(curr: int, percent: int) -> int:
    return round(curr / percent * 100)


def _round_minute(m: int) -> int:
    # e.g. 32 -> 30, 36 -> 35
    a, b = divmod(m, 10)
    if 0 <= b < 3:
        return a * 10
    elif 3 <= b < 7:
        return a * 10 + 5
    else:
        return a * 10 + 10


if __name__ == '__main__':
    # pox car_energy_consumption/run.py run-st
    cli.run()
