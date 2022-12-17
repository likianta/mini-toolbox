## tests_of_concept

The demo code for proof of concept. 

Run it by: 

```shell
py -m compatipy show-ast cases/tests_of_concept/<xxx.py>
```

Observe and analyse its output, think about how to use it in `compatipy/type_annotations_checker.py`.

## assert_succeeded

Below files are asserted to be succeeded.

Run it by:

```shell
# check all
py -m compatipy check-py38 cases/assert_succeeded

# check one
py -m compatipy check-py38 cases/assert_succeeded/<xxx.py>
```

Make sure all output get passed. Otherwise fix `compatipy` tool.

## assert_failed

Below files are asserted to be failed.

Run it by:

```shell
# check all
py -m compatipy check-py38 cases/assert_failed

# check one
py -m compatipy check-py38 cases/assert_failed/<xxx.py>
```
