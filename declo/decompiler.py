import ast
from typing import Any

class BaseTransformer(ast.NodeTransformer):
    """Base class for all transformers."""
    def create_arrow_function(self, target_node, body_node):
        """Helper to create an arrow function node."""
        # Extract the argument name from the target node
        if isinstance(target_node, ast.Name):
            arg_name = target_node.id
        else:
            arg_name = ''
            
        return ast.Call(
            func=ast.Name(id='__arrow__', ctx=ast.Load()),
            args=[
                ast.Constant(value=arg_name),
                body_node
            ],
            keywords=[]
        )

class MapTransformer(BaseTransformer):
    """Transforms simple list comprehensions to .map() calls."""
    def visit_ListComp(self, node: ast.ListComp) -> Any:
        # Only handle simple list comprehensions with single for and no conditions
        if len(node.generators) == 1 and not node.generators[0].ifs:
            comp = node.generators[0]
            map_arrow = self.create_arrow_function(comp.target, node.elt)
            return ast.Call(
                func=ast.Attribute(
                    value=comp.iter,
                    attr='map',
                    ctx=ast.Load()
                ),
                args=[map_arrow],
                keywords=[]
            )
        return node

class FilterMapTransformer(BaseTransformer):
    """Transforms filtered list comprehensions to .filter().map() chains."""
    def visit_ListComp(self, node: ast.ListComp) -> Any:
        # Only handle list comprehensions with single for and filter conditions
        if len(node.generators) == 1 and node.generators[0].ifs:
            comp = node.generators[0]
            
            # Create arrow functions for both filter and map
            map_arrow = self.create_arrow_function(comp.target, node.elt)
            filter_arrow = self.create_arrow_function(
                comp.target,
                comp.ifs[0] if len(comp.ifs) == 1 else ast.BoolOp(
                    op=ast.And(),
                    values=comp.ifs
                )
            )
            
            # Create a filter().map() chain
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=comp.iter,
                            attr='filter',
                            ctx=ast.Load()
                        ),
                        args=[filter_arrow],
                        keywords=[]
                    ),
                    attr='map',
                    ctx=ast.Load()
                ),
                args=[map_arrow],
                keywords=[]
            )
        return node

def compile_python_to_declo(code: str) -> str:
    """
    Convert Python code to Declo syntax.
    
    Currently supports:
    - Simple list comprehensions to .map() calls
    - List comprehensions with filters to .filter().map() chains
    - Lambda functions to arrow functions
    
    Example:
        [x*x for x in nums] -> nums.map(x => x * x)
        [x for x in nums if x % 2 == 0] -> nums.filter(x => x % 2 == 0).map(x => x)
    """
    try:
        # Parse the code into an AST
        tree = ast.parse(code)
        
        # Apply transformations in sequence
        transformers = [
            MapTransformer(),
            FilterMapTransformer(),
        ]
        
        for transformer in transformers:
            tree = transformer.visit(tree)
            ast.fix_missing_locations(tree)
        
        # Generate Python code from the transformed AST
        code = ast.unparse(tree)
        
        # Replace the __arrow__ function calls with arrow function syntax
        import re
        code = re.sub(r'__arrow__\([\'"](\w+)[\'"]\s*,\s*(.+?)\)', r'\1 => \2', code)
        return code
    except SyntaxError as e:
        raise SyntaxError(f"Invalid syntax in Python code: {str(e)}")
    except Exception as e:
        raise Exception(f"Error compiling Python code to Declo: {str(e)}") 