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
squares = nums.map(lambda x: x * x)
```

```bash
declo compile list_comp.declo -o list_comp.py
```

```python
# File: list_comp.py
nums = [1, 2, 3, 4, 5]
squares = [x * x for x in nums]
```

### 2. Decompile 

```bash
declo decompile list_comp.py -o list_comp.declo
```

### 3. Run
```bash
declo run input_file.declo
declo run input_file.py
```
