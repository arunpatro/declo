---
title: Intro
---

# declo

`declo` aims to improve the ergonomics of functional programming syntax in python. It extends the JS syntax into python.

## Usage
1. Create lambdas with arrow notation
```python
import declo

add_one = declo.func("x => x + 1")
assert add_one(1) == 2 # True
```

2. Create named functions globally
```python
import declo

# this creates a function foo in the global name space. 
declo.run("let foo = x => x + 1")

assert foo(5) == 6
```

## Why declo?
It should be easy to customize our python sytanx. I find the JS Syntax for functional programming easier to work with, allowing me to write declartive code easily.

Declo is about DSLs that compile to python bytecode during runti


## FAQ
### How is declo different from `js2py`?
`js2py` is a js compiler written in python. It emits custom objects that help run JS objects inside python. `declo` is simpler and restrictive, and deals only with python objects.  

### How is declo different from `macro-py`?
TODO: I don't really understand `macro-py`.




## Thoughts

1. Can we introduce synctatic sugar with pre-processing?
2. What are the hard things - like closures?
3. How do we handle linting?



