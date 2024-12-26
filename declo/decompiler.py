import ast
import re
import astor
from typing import Any

class BaseTransformer(ast.NodeTransformer):
    """Base class for all transformers."""
    def create_arrow_function(self, target_node: ast.AST, body_node: ast.AST) -> ast.Call:
        """Helper to create an arrow function node."""
        if isinstance(target_node, ast.Name):
            arg_name = target_node.id
        elif isinstance(target_node, ast.arg):
            arg_name = target_node.arg
        else:
            raise ValueError(f"Unsupported target node type: {type(target_node)}")
            
        return ast.Call(
            func=ast.Name(id='__arrow__', ctx=ast.Load()),
            args=[
                ast.Constant(value=arg_name),
                body_node
            ],
            keywords=[]
        )

class ListComprehensionTransformer(BaseTransformer):
    """Transform list comprehensions to map/filter chains."""
    def visit_ListComp(self, node: ast.ListComp) -> Any:
        if len(node.generators) != 1:
            return node
        
        comp = node.generators[0]
        target = comp.target
        iter_expr = comp.iter
        conditions = comp.ifs
        
        # Simple map: [x * 2 for x in nums]
        if not conditions:
            map_arrow = self.create_arrow_function(target, node.elt)
            return ast.Call(
                func=ast.Attribute(
                    value=iter_expr,
                    attr='map',
                    ctx=ast.Load()
                ),
                args=[map_arrow],
                keywords=[]
            )
        
        # Filter with map: [x * 2 for x in nums if x > 0]
        filter_condition = conditions[0] if len(conditions) == 1 else ast.BoolOp(
            op=ast.And(),
            values=conditions
        )
        
        filter_arrow = self.create_arrow_function(target, filter_condition)
        filter_call = ast.Call(
            func=ast.Attribute(
                value=iter_expr,
                attr='filter',
                ctx=ast.Load()
            ),
            args=[filter_arrow],
            keywords=[]
        )
        
        # If the element is just the target variable, we only need filter
        if isinstance(node.elt, ast.Name) and node.elt.id == target.id:
            return filter_call
        
        # Otherwise, chain map after filter
        map_arrow = self.create_arrow_function(target, node.elt)
        return ast.Call(
            func=ast.Attribute(
                value=filter_call,
                attr='map',
                ctx=ast.Load()
            ),
            args=[map_arrow],
            keywords=[]
        )

class LambdaTransformer(BaseTransformer):
    """Transform lambda functions to arrow functions."""
    def visit_Lambda(self, node: ast.Lambda) -> Any:
        if len(node.args.args) != 1:
            return node
        
        return self.create_arrow_function(node.args.args[0], node.body)

def compile_python_to_declo(code: str) -> str:
    """
    Convert Python code to Declo syntax.
    
    Supports:
    - List comprehensions to .map() and .filter() chains
    - Lambda functions to arrow functions
    - Complex chained operations
    
    Example:
        [x*x for x in nums] -> nums.map(x => x * x)
        [x for x in nums if x > 0] -> nums.filter(x => x > 0)
        [x*x for x in nums if x > 0] -> nums.filter(x => x > 0).map(x => x * x)
    """
    try:
        # Parse the code into an AST
        tree = ast.parse(code)
        
        # Apply transformations in sequence
        transformers = [
            ListComprehensionTransformer(),
            LambdaTransformer(),
        ]
        
        for transformer in transformers:
            tree = transformer.visit(tree)
            ast.fix_missing_locations(tree)
        
        # Generate Python code using astor
        code = astor.to_source(tree)
        
        # Replace __arrow__ calls with arrow function syntax
        code = re.sub(r'__arrow__\([\'"](\w+)[\'"]\s*,\s*(.+?)\)', r'\1 => \2', code)
        return code.strip()
    except SyntaxError as e:
        raise SyntaxError(f"Invalid syntax in Python code: {str(e)}")
    except Exception as e:
        raise Exception(f"Error compiling Python code to Declo: {str(e)}") 