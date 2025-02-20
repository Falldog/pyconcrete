# Pyconcrete Test


## Testing Environment

Testing framework is `pytest`.

How to run the test?
```shell
$ pytest
```


Run test in docker, for testing different python version environment:
```shell
$ make test 3.10
```


## Testing Guideline
There 2 parts for pyconcrete testing:
1. `pyecli` encryption behavior
2. pyconcrete exe, executable behavior
3. pyconcrete hook import path behavior
4. pyconcrete decrypt .pye behavior

Avoid to pollute the testing environment, we avoid to change python default path_hook.
So pyconcrete test doesn't import pyconcret module during testing.

All of testcases will be executed by new process, such as `subprocess`. It will make sure the
testing environment clear and not be pollution.

For most of the general testing purpose. Put the testcases into `tests/exe_testcases/` to inspect the
process return code and stdout to make sure the code execute as expected result.
