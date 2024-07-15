import ast
import re

def arrow_func(code):
    parts = code.replace(" ", "").split("=>")
    
    if len(parts) != 2:
        raise ValueError("Invalid lambda expression format")
    
    param, body = parts
    lambda_str = f"lambda {param}: {body}"
    lambda_ast = ast.parse(lambda_str).body[0].value
    code_obj = compile(ast.Expression(lambda_ast), '<string>', 'eval')

    return eval(code_obj)


def run(dsl_input):
    # Regular expression to match the DSL pattern
    pattern = r"let (\w+) = (\w+) => (.+)"
    match = re.match(pattern, dsl_input.strip())
    
    if match:
        func_name = match.group(1)
        param = match.group(2)
        body = match.group(3)
        
        # Create a code object for the function body
        exec(f"def {func_name}({param}):\n    return {body}", globals())
    else:
        raise ValueError("Invalid DSL input")

# def d_map(code):
#     """
#     Parses code of the style 'x.map(fn)' and returns a function that maps the input to the output.
#     """
#     pattern = r'^(\w+)\.map\((.*?)\)$'
#     match = re.match(pattern, code.strip())
    
#     if not match:
#         raise ValueError("Invalid map expression format")
    
#     lis, fn = match.groups()
#     return d_lambda(f"lambda {lis}: [{fn}(i) for i in {lis}]")