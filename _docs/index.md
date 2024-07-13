# declo

`declo` aims to improve the ergonomics of functional programming syntax in python. It extends the JS syntax into python.

## Usage
1. Create lambdas with arrow notation
```python
import declo

add_one = declo.d_lambda("x => x + 1")
assert add_one(1) == 2 # True
```

2. Create named functions globally
```python
import declo

# this creates a function foo in the global name space. 
declo.run("let foo = x => x + 1")

assert foo(5) == 6
```

## Thoughts

1. Can we introduce synctatic sugar with pre-processing?
2. Can we dynamically create native objects using `ast`, `compile()` or `types.FunctionDef`?
3. What are the hard things - like closures?
4. How do we handle linting?
