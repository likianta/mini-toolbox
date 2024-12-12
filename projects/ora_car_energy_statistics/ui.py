import json

import streamlit as st
import streamlit_canary as sc
from code_editor import code_editor
from lk_utils import fs

st.set_page_config('Ora Cat Car Energy Statistics')

_state = sc.session.init(
    lambda: {
        'dataset': fs.load(
            fs.xpath('_dataset.json'),
            default={
                '0000-00-00': {
                    'total_mileage'               : [],
                    'displayed_leftover_mileage'  : [],
                    'displayed_battery_percentage': [],
                    'energy_consumption'          : [],
                }
            }
        ),
        'current': '0000-00-00'
    },
    version=1
)


def main() -> None:
    current_dataset: dict[str, list] = _state['dataset'][_state['current']]
    
    with sc.card('New record'):
        a: int = st.number_input(
            'Total mileage', value=20000
        )
        b: int = st.number_input(
            'Displayed leftover mileage', value=500
        )
        c: int = st.number_input(
            'Displayed battery percentage', 0, 100, value=100
        )
        d: float = st.number_input(
            'Energy consumption', 8.0, 30.0, value=16.0
        )
        if sc.long_button('Submit'):
            current_dataset['total_mileage'].append(a)
            current_dataset['displayed_leftover_mileage'].append(b)
            current_dataset['displayed_battery_percentage'].append(c)
            current_dataset['energy_consumption'].append(d)
    
    place1 = st.empty()
    
    with st.expander('Revise dataset'):
        revise_dataset()
    
    if len(current_dataset['total_mileage']) <= 1:
        return
    
    def diff(key):
        return current_dataset[key][-1] - current_dataset[key][-2]
    
    e = diff('total_mileage')
    f = -diff('displayed_leftover_mileage')
    g = -diff('displayed_battery_percentage')
    
    with place1:
        st.table(
            ('Actual changed mileage', e),
            ('Display changed mileage', f),
            ('Display changed mileage (by percentage)', round(500 * (g / 100))),
            (
                'Objective estimated changed mileage',
                '{] (similarity to actual: {})'.format(
                    round(
                        x := 55 * (g / 100) /
                             current_dataset['energy_consumption'][-1]
                    ),
                    '{:.2%}'.format(x / e)
                )
            )
        )
        
        if current_dataset['displayed_battery_percentage'][-1] <= 10:
            st.warning('Very low energy level!')
        else:
            st.write('Objective estimated leftover mileage: {}'.format(
                round(
                    (55 * ((current_dataset['displayed_battery_percentage'][-1]
                            - 10) / 100)
                     ) / current_dataset['energy_consumption'][-1]
                )
            ))


def revise_dataset():
    data = code_editor(
        json.dumps(_state['dataset'], indent=4),
        lang='json',
        buttons=(
            {
                'name'        : 'update',
                'feather'     : 'Save',
                'primary'     : True,
                'hasText'     : False,
                'showWithIcon': True,
                'commands'    : ['submit'],
                'style'       : {'bottom': '0rem', 'right': '0.4rem'},
            },
        ),
        options={'wrap': True}
    )
    if data['type'] == 'submit':
        _state['dataset'] = json.loads(data['text'])
        st.rerun()
    
    if st.button('Save to local file'):
        fs.dump(_state['dataset'], fs.xpath('_dataset.json'))
        st.toast(':green[Successfully saved.]')


if __name__ == '__main__':
    # strun 2020 projects/ora_car_energy_statistics/ui.py
    main()
