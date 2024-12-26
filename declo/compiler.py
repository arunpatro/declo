# declopy/compiler.py

import ast
import re
from typing import Any

def preprocess_arrow_functions(code: str) -> str:
    """Convert arrow function syntax to __arrow__ function calls before parsing."""
    # Match arrow functions like: x => x % 2
    pattern = r'(\w+)\s*=>\s*(.+)'
    
    def replace_arrow(match):
        arg, body = match.groups()
        return f'__arrow__("{arg}", {body})'
    
    return re.sub(pattern, replace_arrow, code)

class ArrowTransformer(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> Any:
        # Handle arrow function transformation
        if (isinstance(node.func, ast.Name) and 
            node.func.id == '__arrow__' and 
            len(node.args) == 2):
            return ast.Lambda(
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg=node.args[0].value)],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[]
                ),
                body=node.args[1]
            )
        return self.generic_visit(node)

class MapFilterTransformer(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Attribute) or not isinstance(node.func.value, (ast.Name, ast.List, ast.ListComp)):
            return self.generic_visit(node)
            
        # Transform map operation
        if node.func.attr == 'map' and len(node.args) == 1:
            if isinstance(node.args[0], ast.Lambda):
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
                
        # Transform filter operation
        elif node.func.attr == 'filter' and len(node.args) == 1:
            if isinstance(node.args[0], ast.Lambda):
                lambda_node = node.args[0]
                return ast.ListComp(
                    elt=ast.Name(id=lambda_node.args.args[0].arg, ctx=ast.Load()),
                    generators=[
                        ast.comprehension(
                            target=lambda_node.args.args[0],
                            iter=node.func.value,
                            ifs=[lambda_node.body],
                            is_async=0
                        )
                    ]
                )
                
        return self.generic_visit(node)

def compile_declo_to_python(code: str) -> str:
    """
    Convert minimal Declo syntax to valid Python using AST transformation.
    Handles both native list comprehensions, .map(lambda x: expr), and .filter(lambda x: expr).
    Also supports arrow function syntax (=>).
    """
    try:
        # Preprocess arrow functions
        preprocessed_code = preprocess_arrow_functions(code)
        
        # Parse the code into an AST
        tree = ast.parse(preprocessed_code)
        
        # First transform arrow functions to lambda
        arrow_transformer = ArrowTransformer()
        tree = arrow_transformer.visit(tree)
        
        # Then transform map/filter operations
        map_filter_transformer = MapFilterTransformer()
        transformed_tree = map_filter_transformer.visit(tree)
        ast.fix_missing_locations(transformed_tree)
        
        # Generate Python code from the transformed AST
        return ast.unparse(transformed_tree)
    except SyntaxError as e:
        raise SyntaxError(f"Invalid syntax in Declo code: {str(e)}")
    except Exception as e:
        raise Exception(f"Error compiling Declo code: {str(e)}")
