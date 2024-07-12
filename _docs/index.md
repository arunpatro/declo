# declo

A simple way to program declaratively in python.

## Usage
```python
from declo.tools import d_lambda

add_one = d_lambda("x => x + 1")
assert add_one(1) == 2 # True
```

## Motivation

1. Many syntactic problems can be solved with a pre-processor
2. Next step is to compile aka ast parsing
3. Since types are not that big of a problem, we should concern ourselves with closure support.