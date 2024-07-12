# declo

A simple way to program declaratively in python.

## Usage
```python
from declo.tools import d_lambda

add_one = d_lambda("x => x + 1")
assert add_one(1) == 2 # True
```