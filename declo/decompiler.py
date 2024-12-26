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
            
            # Handle function calls in filter conditions
            if len(comp.ifs) == 1:
                filter_condition = comp.ifs[0]
                # If it's a comparison involving a function call
                if (isinstance(filter_condition, ast.Compare) and 
                    isinstance(filter_condition.left, ast.Call)):
                    # Ensure the function call is correctly represented
                    filter_condition = ast.Compare(
                        left=filter_condition.left,
                        ops=filter_condition.ops,
                        comparators=filter_condition.comparators
                    )
                else:
                    # Directly use the condition if it's not a comparison
                    filter_condition = filter_condition
            else:
                filter_condition = ast.BoolOp(
                    op=ast.And(),
                    values=comp.ifs
                )
            
            filter_arrow = self.create_arrow_function(comp.target, filter_condition)
            
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

class IdentityMapOptimizer(BaseTransformer):
    """Removes unnecessary identity mappings like .map(x => x)."""
    def visit_Call(self, node: ast.Call) -> Any:
        # First visit children
        node = self.generic_visit(node)
        
        # Check if this is a map call
        if (isinstance(node.func, ast.Attribute) and 
            node.func.attr == 'map' and 
            len(node.args) == 1):
            
            # Get the arrow function
            arrow_call = node.args[0]
            if (isinstance(arrow_call, ast.Call) and 
                isinstance(arrow_call.func, ast.Name) and 
                arrow_call.func.id == '__arrow__' and 
                len(arrow_call.args) == 2):
                
                arg_name = arrow_call.args[0].value
                body = arrow_call.args[1]
                
                # Check if it's an identity function (x => x)
                if (isinstance(body, ast.Name) and 
                    body.id == arg_name):
                    # Return the value being mapped over instead
                    return node.func.value
        
        return node

def compile_python_to_declo(code: str) -> str:
    """
    Convert Python code to Declo syntax.
    
    Currently supports:
    - Simple list comprehensions to .map() calls
    - List comprehensions with filters to .filter().map() chains
    - Lambda functions to arrow functions
    - Optimizes away unnecessary identity mappings (.map(x => x))
    
    Example:
        [x*x for x in nums] -> nums.map(x => x * x)
        [x for x in nums if x % 2 == 0] -> nums.filter(x => x % 2 == 0)
    """
    try:
        # Parse the code into an AST
        tree = ast.parse(code)
        
        # Apply transformations in sequence
        transformers = [
            MapTransformer(),
            FilterMapTransformer(),
            IdentityMapOptimizer(),
        ]
        
        for transformer in transformers:
            tree = transformer.visit(tree)
            ast.fix_missing_locations(tree)
        
        # Generate Python code from the transformed AST
        code = ast.unparse(tree)
        
        # Replace the __arrow__ function calls with arrow function syntax
        import re
        # First replace any remaining lambda functions with arrow syntax
        code = re.sub(r'lambda\s+(\w+)\s*:\s*([^,\n]+)', r'\1 => \2', code)
        # Then replace __arrow__ calls
        code = re.sub(r'__arrow__\([\'"](\w+)[\'"]\s*,\s*(.+?)\)', r'\1 => \2', code)
        return code
    except SyntaxError as e:
        raise SyntaxError(f"Invalid syntax in Python code: {str(e)}")
    except Exception as e:
        raise Exception(f"Error compiling Python code to Declo: {str(e)}") 