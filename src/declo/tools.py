import ast
import re

def d_lambda(code):
    parts = code.replace(" ", "").split("=>")
    
    if len(parts) != 2:
        raise ValueError("Invalid lambda expression format")
    
    param, body = parts
    body = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*)', r'\1', body)
    lambda_str = f"lambda {param}: {body}"
    lambda_ast = ast.parse(lambda_str).body[0].value
    code_obj = compile(ast.Expression(lambda_ast), '<string>', 'eval')

    return eval(code_obj)

def d_map(code):
    """
    Parses code of the style 'x.map(fn)' and returns a function that maps the input to the output.
    """
    pattern = r'^(\w+)\.map\((.*?)\)$'
    match = re.match(pattern, code.strip())
    
    if not match:
        raise ValueError("Invalid map expression format")
    
    lis, fn = match.groups()
    return d_lambda(f"lambda {lis}: [{fn}(i) for i in {lis}]")