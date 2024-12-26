# declopy/compiler.py

import re

def compile_declo_to_python(code: str) -> str:
    """
    Convert minimal Declo syntax to valid Python.
    For now, only handle .map(lambda x: expr).
    """
    lines = code.split('\n')
    output_lines = []

    # Regex to match lines like:
    #   nums.map(lambda x: x**2)
    map_pattern = re.compile(
        r'^(\s*)([A-Za-z_]\w*)\.map\(lambda\s+([A-Za-z_]\w*):\s*(.+)\)(\s*)$'
    )
    
    for line in lines:
        line_stripped = line.strip()
        
        if '.map(' in line_stripped:
            match = map_pattern.match(line)
            if match:
                indent, list_var, param, expr, trailing_space = match.groups()
                # Convert to list comprehension
                transformed = f"{indent}[{expr} for {param} in {list_var}]{trailing_space}"
                output_lines.append(transformed)
            else:
                # If it doesn't match exactly, keep the original line
                output_lines.append(line)
        else:
            output_lines.append(line)
    
    return '\n'.join(output_lines)
