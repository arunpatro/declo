# declopy/compiler.py

import ast
import re
from typing import Any

def preprocess_arrow_functions(code: str) -> str:
    """Convert arrow function syntax to __arrow__ function calls before parsing."""
    # Match arrow functions like: x => x % 2 or x => x.upper()
    pattern = r'(\w+)\s*=>\s*([^.]+(?:\.[^.]+)*)'
    
    def replace_arrow(match):
        arg, body = match.groups()
        return f'__arrow__("{arg}", {body})'
    
    # Process line by line to handle chained operations
    lines = code.split('\n')
    processed_lines = []
    
    for line in lines:
        # If line contains chained operations, process each arrow function
        if '=>' in line and ('map' in line or 'filter' in line):
            parts = line.split('.')
            current = []
            for part in parts:
                if '=>' in part:
                    # Find the method name (map/filter) and combine with previous parts
                    method = part.split('(')[0].strip()
                    if method in ['map', 'filter']:
                        if current:
                            part = '.'.join(current) + '.' + part
                            current = []
                    part = re.sub(pattern, replace_arrow, part)
                current.append(part)
            line = '.'.join(current)
        processed_lines.append(line)
    
    return '\n'.join(processed_lines)

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
        # First visit children to handle nested operations
        node = self.generic_visit(node)
        
        if not isinstance(node.func, ast.Attribute):
            return node
            
        # Transform map operation
        if node.func.attr == 'map' and len(node.args) == 1:
            if isinstance(node.args[0], ast.Lambda):
                lambda_node = node.args[0]
                
                # Check if this is a chained operation (map after filter)
                if (isinstance(node.func.value, ast.ListComp) and 
                    len(node.func.value.generators) == 1 and 
                    node.func.value.generators[0].ifs):
                    # This is a filter().map() chain, combine them
                    return ast.ListComp(
                        elt=lambda_node.body,
                        generators=[
                            ast.comprehension(
                                target=lambda_node.args.args[0],
                                iter=node.func.value.generators[0].iter,
                                ifs=node.func.value.generators[0].ifs,
                                is_async=0
                            )
                        ]
                    )
                
                # Handle method calls in the lambda body
                if isinstance(lambda_node.body, ast.Call) and isinstance(lambda_node.body.func, ast.Attribute):
                    # This is a method call like x.upper()
                    return ast.ListComp(
                        elt=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id=lambda_node.args.args[0].arg, ctx=ast.Load()),
                                attr=lambda_node.body.func.attr,
                                ctx=ast.Load()
                            ),
                            args=lambda_node.body.args,
                            keywords=lambda_node.body.keywords
                        ),
                        generators=[
                            ast.comprehension(
                                target=lambda_node.args.args[0],
                                iter=node.func.value,
                                ifs=[],
                                is_async=0
                            )
                        ]
                    )
                else:
                    # Regular map operation
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
                
        return node

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
