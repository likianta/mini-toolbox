def loads(file: str) -> dict:
    if file.endswith(('.json', '.json5')):
        from json import load as jload
        with open(file, 'r', encoding='utf-8') as f:
            return jload(f)
    elif file.endswith(('.yaml', '.yml')):
        from yaml import safe_load as yload  # noqa
        with open(file, 'r', encoding='utf-8') as f:
            return yload(f)
    elif file.endswith('.pkl'):
        from pickle import load as pload
        with open(file, 'rb') as f:
            return pload(f)
    else:
        raise Exception('unsupported file type', file)


def dumps(data: dict, file: str) -> None:
    if file.endswith(('.json', '.json5')):
        from json import dump as jdump
        with open(file, 'w', encoding='utf-8') as f:
            jdump(data, f, ensure_ascii=False, default=str, indent=4)
    elif file.endswith(('.yaml', '.yml')):
        from yaml import dump as ydump  # noqa
        with open(file, 'w', encoding='utf-8') as f:
            ydump(data, f, sort_keys=False)
    elif file.endswith('.pkl'):
        from pickle import dump as pdump
        with open(file, 'wb') as f:
            pdump(data, f)
    else:
        raise Exception('unsupported file type', file)
