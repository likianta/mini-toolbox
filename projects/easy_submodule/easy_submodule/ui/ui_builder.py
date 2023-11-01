# __package__ = 'easy_submodule.ui.ui_builder'

import datetime
import re
import typing as t

import streamlit as st  # noqa
from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads
from lk_utils import run_cmd_args

from ..lock import get_current_info
from ..profile import T
from ..profile import load_profile
from ..pull import pull_submodules


def _get_cache() -> dict:
    if 'cache' not in st.session_state:
        if fs.exists(x := fs.xpath('../../_easy_submodule_cache.pkl')):
            # for project development
            cache_file = x
        else:
            cache_file = fs.xpath('./_cache.pkl')
            assert fs.exists(cache_file), cache_file
        cache = loads(cache_file)
        st.session_state['cache'] = cache
    return st.session_state['cache']


# TODO
# @atexit.register
def _sync_cache(cache: dict) -> None:
    if fs.exists(x := fs.xpath('../../_easy_submodule_cache.pkl')):
        # for project development
        cache_file = x
    else:
        cache_file = fs.xpath('./_cache.pkl')
    dumps(dict(cache), cache_file)


def main() -> None:
    print(':d')
    st.title('Easy Submodule')
    new_item = add_new_project()
    cache = _get_cache()
    if new_item:
        cache.update(new_item)
        _sync_cache(cache)
    list_projects(cache)


def add_new_project() -> t.Optional[dict]:
    new_proj_path = st.text_input(
        'Add new project',
        help='Given a folder path to a project, will list all submodules '
             'inside it.'
    )
    if new_proj_path:
        return {
            (fs.dirname(new_proj_path), new_proj_path):
                analyze_project(new_proj_path)
        }


def analyze_project(path: str) -> t.Dict[str, str]:
    out = {}
    if fs.exists(x := f'{path}/.submodules.yaml'):
        print(x, ':v')
        profile = load_profile(x)
        for name, info in profile.items():
            # out[name] = analyze_project(info['path'])
            out[name] = info['path']
    else:
        st.warning('No ".submodules.yaml" found in this project.')
    return out


def list_projects(projects: t.Dict[t.Tuple[str, str], t.Dict[str, str]]) -> None:
    for (top_name, top_path), v0 in projects.items():
        # cols = st.columns(2)
        # sub_names = v0.keys()
        # for sub_name in v0.keys():
        #     pass
        with st.expander(top_name, True):
            # c0, c1 = st.columns(2)

            all_be_pulled = False
            if st.button(
                'Pull all submodules',
                type='primary',
                key=f'pull_btn_{top_name}'
            ):
                pull_submodules(f'{top_path}/.submodules.yaml')
                all_be_pulled = True
            if st.button('Refresh states'):
                all_be_pulled = False
            if st.button(':red[Delete this entry]'):
                continue
                
            for sub_name, path in v0.items():
                # c0.markdown(f'**{sub_name}**')
                # st.write(sub_name)
                author, time_delta, comment = _get_last_commit_info(path)
                st.markdown('''
                    - submodule: {name}
                        - author: {author}
                        - commit: {comment}
                        - since: {since}
                '''.format(
                    name=sub_name,
                    author=author,
                    comment=comment,
                    since=time_delta
                ))
                if st.button(f'Pull "{sub_name}"', disabled=all_be_pulled):
                    run_cmd_args('git', 'pull', verbose=True, cwd=path)


def _check_submodule(info: T.ProfileItem) -> bool:
    # ref: `./check.py`
    branch0, commit0 = get_current_info(info['path'])
    branch1, commit1 = info['branch'], info['commit']
    return branch0 == branch1 and commit0 == commit1


def _get_last_commit_info(cwd: str) -> t.Tuple[str, str, str]:
    # ref: https://stackoverflow.com/questions/7293008/display-last-git-commit-
    #   comment
    msg = run_cmd_args('git', 'log', '-1', cwd=cwd)
    print(fs.dirname(cwd), msg)
    """
    e.g.
        commit <hash> (HEAD -> master, ...)
        Author: <name> <email>
        Date  : Tue Oct 31 17:39:25 2023 +0800
        
            <comment>
    """
    lines = msg.splitlines()
    
    def get_author() -> str:
        return re.search(r'Author: (\w+)', lines[1]).group(1)
    
    def get_time_delta() -> str:
        print(':dv', lines[2])
        mon, day, hr, min_, sec, yr, tz = re.search(
            r'Date *: +\w+ (\w+) (\d+) (\d+):(\d+):(\d+) (\d+) (\+\d+)',
            lines[2]
        ).groups()
        # convert to datetime format
        dt = datetime.datetime(
            int(yr),
            datetime.datetime.strptime(mon, '%b').month,
            int(day),
            int(hr),
            int(min_),
            int(sec)
        )
        # calculate time delta
        delta = datetime.datetime.now() - dt
        # convert to str
        if (x := delta.days) > 0:
            return f'{x} days ago'
        else:
            s = delta.seconds
            if s > 3600:
                return f'{s // 3600} hours ago'
            elif s > 60:
                return f'{s // 60} minutes ago'
            elif s > 0:
                return f'{s} seconds ago'
            else:
                return 'just now'
    
    def get_comment() -> str:
        return lines[4].strip()
    
    return get_author(), get_time_delta(), get_comment()
