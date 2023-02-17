# Conflore

## Quick start

```py
from conflore import Conflore

conf = Conflore('config.pkl')

xxx = conf['xxx']
conf.bind('xxx', lambda : 'yyy')
conf.save()
```
