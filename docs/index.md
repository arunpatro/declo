---
title: Introduction
---

# declo
`declo` aims to improve the ergonomics of functional programming syntax in python. It extends the JS syntax into python.


## Why declo?
It should be easy to customize our python sytanx. I find the JS Syntax for functional programming easier to work with, allowing me to write declarative code easily.

Declo is about DSLs that compile to python bytecode during runtime. 


## Usage
1. Create lambdas with arrow notation
```python
import declo

add_one = declo.arrow_func("x => x + 1")
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
1. How much can we acheive synctatic sugars with pre-processing?
2. What are the hard things - like closures?
3. How do we handle linting, since the commands are in strings?
