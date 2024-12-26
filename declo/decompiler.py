import ast
from typing import Any

class ListComprehensionTransformer(ast.NodeTransformer):
    def visit_ListComp(self, node: ast.ListComp) -> Any:
        """Transform list comprehensions to .map() calls when possible."""
        # Only handle simple list comprehensions with single for and no if conditions
        if len(node.generators) == 1 and not node.generators[0].ifs:
            comp = node.generators[0]
            # Create a lambda function
            lambda_node = ast.Lambda(
                args=ast.arguments(
                    posonlyargs=[],
                    args=[comp.target],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=node.elt
            )
            
            # Create a map call
            return ast.Call(
                func=ast.Attribute(
                    value=comp.iter,
                    attr='map',
                    ctx=ast.Load()
                ),
                args=[lambda_node],
                keywords=[]
            )
        return node

def compile_python_to_declo(code: str) -> str:
    """
    Convert Python code to Declo syntax, focusing on list comprehension patterns.
    Currently handles:
    - Simple list comprehensions to .map() calls
    """
    try:
        # Parse the code into an AST
        tree = ast.parse(code)
        
        # Transform the AST
        transformer = ListComprehensionTransformer()
        transformed_tree = transformer.visit(tree)
        ast.fix_missing_locations(transformed_tree)
        
        # Generate Python code from the transformed AST
        return ast.unparse(transformed_tree)
    except SyntaxError as e:
        raise SyntaxError(f"Invalid syntax in Python code: {str(e)}")
    except Exception as e:
        raise Exception(f"Error compiling Python code to Declo: {str(e)}") 