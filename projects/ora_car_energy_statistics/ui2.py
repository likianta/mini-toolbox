"""
simplified version.
"""
import streamlit as st

st.set_page_config('Ora Cat Mileage Estimation')


def main() -> None:
    tabs = st.tabs(('Calculation', 'Settings'))
    
    with tabs[1]:
        a = st.number_input(
            'Total battery capacity (kWh)',
            value=57.7,
            step=1.0,
        )
        b = st.number_input(
            'Estimated healthy level (%)',
            min_value=0,
            max_value=100,
            value=90,
            step=1,
        )
        c = st.number_input(
            'Reserved capacity (%)',
            min_value=0,
            max_value=100,
            value=10,
            step=1,
        )
    
    with tabs[0]:
        with st.expander('Overview', True):
            d = st.number_input(
                'Current percentage (%)',
                min_value=0,
                max_value=100,
                value=90,
                step=1,
            )
            e = st.number_input(
                'Current energy consumption (kWh/100km)',
                min_value=1.0,
                max_value=100.0,
                value=18.0,
                step=0.1,
            )
            if d <= c:
                st.warning('Energy too low!')
                return
            else:
                st.success(
                    'Estimated leftover range: {}km.\n\n'
                    'For each percent you can drive {}km.'
                    .format(
                        round((a * (b / 100)) / 100 * (d - c) / (e / 100)),
                        round((a * (b / 100)) / 100 * (100 - c) / (e / 100), 2),
                    )
                )
        
        with st.expander('Your destination', True):
            f = st.number_input(
                'The distance to your destination (km)',
                min_value=0,
                max_value=100,
                value=0,
                step=1,
            )
            if f > 0:
                g = d - round(f / ((a * (b / 100)) / 100 / (e / 100)))
                if g == d:
                    st.success(
                        'When you arrive at your destination, the bettery '
                        'percentage changes less than :green[1%].'
                    )
                elif g < 0:
                    st.error('You may run out of energy before arriving!')
                else:
                    st.success(
                        'When you arrive at your destination, the battery goes '
                        'down from :green[{}%] to :red[{}%].'
                        .format(d, g)
                    )


if __name__ == '__main__':
    # strun 2020 projects/ora_car_energy_statistics/ui2.py
    main()
