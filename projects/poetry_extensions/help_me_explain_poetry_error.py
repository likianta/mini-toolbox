import lk_logger
import re
import streamlit as st

lk_logger.setup(quiet=True)
print(':d')


def main():
    text = st.text_area(
        'Paste your error info from terminal output to here',
        height=600,
    )
    if text:
        """
        e.g.
            Resolving dependencies... (17.2s)

            The current project's supported Python range (3.8.19) is not \
            compatible with some of the required packages Python requirement:
            - rpds-py requires Python >=3.9, so it will not be satisfied for \
            Python 3.8.19

            Because no versions of altair match !=5.4.1
            and altair (5.4.1) depends on jsonschema (>=3.0), every version of \
            altair requires jsonschema (>=3.0).
            And because no versions of jsonschema match >=3.0,<4.21.1 || \
            >4.21.1
            and jsonschema (4.21.1) depends on rpds-py (>=0.7.1), every \
            version of altair requires rpds-py (>=0.7.1).
            Because rpds-py (0.22.3) requires Python >=3.9
            and no versions of rpds-py match >=0.7.1,<0.22.3 || >0.22.3, \
            rpds-py is forbidden.
            Thus, altair is forbidden.
            So, because batch-dump-registers depends on altair (*), version \
            solving failed.

            * Check your dependencies Python requirement: The Python \
            requirement can be specified via the `python` or `markers` properties

            For rpds-py, a possible solution would be to set the `python` \
            property to "<empty>"

            https://python-poetry.org/docs/dependency-specification/ \
            #python-restricted-dependencies,
            https://python-poetry.org/docs/dependency-specification/ \
            #using-environment-markers
        """
        chain = []
        flag = 'INIT'
        temp = ''
        for line in text.splitlines():
            print(':v', line)
            match flag:
                case 'INIT':
                    if line.startswith('Because no versions of '):
                        temp = re.match(
                            r'Because no versions of ([-\w]+) match', line
                        ).group(1)
                        flag = 'START'
                case 'START':
                    if re.match(r' and [-\w]+ \([-.\w]+\) depends on ', line):
                        m = re.match(
                            r' and ([-\w]+) (\([.\w]+\)) depends on '
                            r'([-\w]+)', line
                        )
                        assert m.group(1) == temp
                        print(m.groups(), temp, ':v')
                        chain.append('{} {}'.format(m.group(1), m.group(2)))
                        temp = m.group(3)
                    elif line.startswith(' and no versions of '):
                        m = re.match(
                            r' and no versions of ([-\w]+) match', line
                        )
                        assert m.group(1) == temp, (m.group(1), temp)
                        chain.append(m.group(1))
                        flag = 'END'
                        break
        assert flag == 'END', (flag, chain, temp)
        
        st.info(
            ':skull: ' +
            '  :gray[<-]  '.join(f':red[**{x}**]' for x in reversed(chain))
        )


if __name__ == '__main__':
    # strun 3001 projects/poetry_extensions/help_me_explain_poetry_error.py
    main()
