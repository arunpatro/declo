# declo

A simple way to program declaratively in python.

## Usage
1. Easily create lambdas
```python
from declo.tools import d_lambda

add_one = d_lambda("x => x + 1")
assert add_one(1) == 2 # True
```

2. Create named functions globally
```python
from declo.tools import run

# this creates a function foo in the global name space. 
run("let foo = x => x + 1")

assert foo(5) == 6
```

## Thoughts

1. Can we introduce synctatic sugar with pre-processing?
2. Can we dynamically create native objects using `ast`, `compile()` or `types.FunctionDef`?
3. What are the hard things - like closures?
4. How do we handle linting?
