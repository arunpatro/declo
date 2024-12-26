# Declo

```bash
pip install git+https://github.com/arunpatro/declo
```

Declo is a Python dialect that brings JavaScript-like functional programming patterns to Python, making functional code more concise and readable.

## Why?

I wanted to bring the excellent ergonomics of map, filter, chaining of functional transformations to python. We already have that in pandas, torch, so why not extend this to the rest of the language?


## Usage
### 1. Compile Declo code to Python

```python
# File: list_comp.declo
nums = [1, 2, 3, 4, 5]
squares = nums.map(x => x * x)
evens = nums.filter(x => x % 2 == 0)
```

```bash
declo compile list_comp.declo
```

```python
# File: list_comp.py
nums = [1, 2, 3, 4, 5]
squares = [x * x for x in nums]
evens = [x for x in nums if x % 2 == 0]
```

### 2. Decompile 

```bash
declo decompile list_comp.py
```

### 3. Run
```bash
declo run input_file.declo
declo run input_file.py
```
