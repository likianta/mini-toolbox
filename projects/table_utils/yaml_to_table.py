from argsense import cli
from lk_utils import fs


@cli.cmd()
def yaml_to_excel(file_i: str, file_o: str = None) -> None:
    """
    params:
        file_i: a ".yaml" file.
        file_o:
            if not given, will be the same as file_i with ext changed to -
            ".xlsx".
    """
    if not file_o:
        file_o = fs.replace_ext(file_i, 'xlsx')
    assert file_i.endswith('.yaml') and file_o.endswith('.xlsx')
    
    data: dict = fs.load(file_i)
    
    # guess column names
    colnames = ['index', 'name']
    for v in data.values():
        for k in v.keys():
            if k not in colnames:
                colnames.append(k)
    
    # avoid name conflict
    if colnames.count('name') == 2:
        assert 'key' not in colnames
        colnames[1] = 'key'
        
    colnames = tuple(colnames)
    print(colnames, ':v2')
    
    rows = [colnames]
    for i, (k, v) in enumerate(data.items(), 1):
        rows.append((
            i,
            k,
            *[v.get(x, '') for x in colnames[2:]]
        ))
        
    fs.dump(rows, file_o)
    print(':tv4', 'done. see {}'.format(file_o))


if __name__ == '__main__':
    # pox projects/table_utils/yaml_to_table.py yaml_to_excel ...
    cli.run()
