# declopy/compiler.py

import ast
from typing import Any

class MapTransformer(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> Any:
        if (isinstance(node.func, ast.Attribute) and 
            isinstance(node.func.value, (ast.Name, ast.List, ast.ListComp)) and
            node.func.attr == 'map' and 
            len(node.args) == 1 and 
            isinstance(node.args[0], ast.Lambda)):
            
            lambda_node = node.args[0]
            return ast.ListComp(
                elt=lambda_node.body,
                generators=[
                    ast.comprehension(
                        target=lambda_node.args.args[0],
                        iter=node.func.value,
                        ifs=[],
                        is_async=0
                    )
                ]
            )
        return self.generic_visit(node)

def compile_declo_to_python(code: str) -> str:
    """
    Convert minimal Declo syntax to valid Python using AST transformation.
    Handles both native list comprehensions and .map(lambda x: expr).
    """
    try:
        # Parse the code into an AST
        tree = ast.parse(code)
        
        # Transform the AST
        transformer = MapTransformer()
        transformed_tree = transformer.visit(tree)
        ast.fix_missing_locations(transformed_tree)
        
        # Generate Python code from the transformed AST
        return ast.unparse(transformed_tree)
    except SyntaxError as e:
        raise SyntaxError(f"Invalid syntax in Declo code: {str(e)}")
    except Exception as e:
        raise Exception(f"Error compiling Declo code: {str(e)}")
