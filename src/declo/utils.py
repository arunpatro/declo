
import ast
import json

def node_to_dict(node: ast.AST | list | any):
    """Recursively convert an AST node to a dictionary."""
    if isinstance(node, ast.AST):
        fields = {name: node_to_dict(value) for name, value in ast.iter_fields(node)}
        return {'type': node.__class__.__name__, **fields}
    elif isinstance(node, list):
        return [node_to_dict(item) for item in node]
    return node

def ast_to_json(code):
    """Parse code and return the AST as a JSON string."""
    parsed_ast = ast.parse(code)
    ast_dict = node_to_dict(parsed_ast)
    return json.dumps(ast_dict, indent=2)