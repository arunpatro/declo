---
title: Features
---

Declo supports the following features:

1. Arrow Functions 

    ```js
    x => x + 1
    ```
    compiles to Lambdas
    ```python
    lambda x: x + 1
    ```

2. Named Functions

    ```js
    const foo = x => x + 1
    ```
    compiles to 
    ```python
    def foo(x):
        return x + 1
    ```

3. Braced Scopes and Blocks
    
    ```js
    const foo = x => {z = x + 1; y = z * 2; y}
    ```
    compiles to
    ```python
    def foo(x):
        z = x + 1
        y = z * 2
        return y
    ```

4. Map, Filter and Reduce

    ```js
    [1, 2, 3].map(x => x + 1)
    ```
    compiles to
    ```python
    list(map(lambda x: x + 1, [1, 2, 3]))
    ```


**Note:** We also accept any feature requests via Github Issues.