# declopy/compiler.py

import ast
import re
import astor
from typing import Any

def preprocess_arrow_functions(code: str) -> str:
    """Convert arrow function syntax to __arrow__ function calls before parsing."""
    def process_arrow_function(arrow_part: str) -> str:
        pattern = r'(\w+)\s*=>\s*(.+)'
        match = re.match(pattern, arrow_part.strip())
        if match:
            arg, body = match.groups()
            return f'__arrow__("{arg}", {body})'
        return arrow_part
    
    # Process line by line
    lines = code.split('\n')
    processed_lines = []
    
    for line in lines:
        # If line contains arrow function
        if '=>' in line:
            # Find the arrow function within parentheses
            start = line.find('(', 0)
            while start != -1:
                # Find matching closing parenthesis
                depth = 1
                pos = start + 1
                while depth > 0 and pos < len(line):
                    if line[pos] == '(':
                        depth += 1
                    elif line[pos] == ')':
                        depth -= 1
                    pos += 1
                
                if depth == 0:
                    end = pos - 1
                    # Process only the arrow function part
                    before = line[:start + 1]
                    arrow_part = line[start + 1:end]
                    after = line[end:]
                    
                    # Replace arrow function if present
                    if '=>' in arrow_part:
                        arrow_part = process_arrow_function(arrow_part)
                        line = before + arrow_part + after
                        break
                    
                start = line.find('(', start + 1)
        
        processed_lines.append(line)
    
    return '\n'.join(processed_lines)

class ArrowTransformer(ast.NodeTransformer):
    """Transform __arrow__ function calls to lambda expressions."""
    def visit_Call(self, node: ast.Call) -> Any:
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
    """Transform map/filter operations to list comprehensions."""
    def visit_Call(self, node: ast.Call) -> Any:
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

class CleanupTransformer(ast.NodeTransformer):
    """Clean up the AST to generate cleaner code."""
    def visit_ListComp(self, node: ast.ListComp) -> Any:
        # Remove unnecessary parentheses from list comprehension elements
        if isinstance(node.elt, ast.BinOp):
            # Simplify binary operations like x * x
            node.elt.lineno = None
            node.elt.col_offset = None
        return node

def compile_declo_to_python(code: str) -> str:
    """
    Convert Declo syntax to valid Python using AST transformation.
    Handles list comprehensions, .map(), .filter(), and arrow functions.
    """
    try:
        # Preprocess arrow functions
        preprocessed_code = preprocess_arrow_functions(code)
        
        # Parse the code into an AST
        tree = ast.parse(preprocessed_code)
        
        # Transform arrow functions to lambda
        arrow_transformer = ArrowTransformer()
        tree = arrow_transformer.visit(tree)
        
        # Transform map/filter operations
        map_filter_transformer = MapFilterTransformer()
        tree = map_filter_transformer.visit(tree)
        
        # Clean up the AST
        cleanup_transformer = CleanupTransformer()
        transformed_tree = cleanup_transformer.visit(tree)
        ast.fix_missing_locations(transformed_tree)
        
        # Configure astor for cleaner output
        astor_options = {
            'indent_with': ' ' * 4,
            'add_line_information': False,
            'source_generator_class': astor.SourceGenerator
        }
        
        # Generate Python code using astor
        return astor.to_source(transformed_tree, **astor_options).strip()
    except SyntaxError as e:
        raise SyntaxError(f"Invalid syntax in Declo code: {str(e)}")
    except Exception as e:
        raise Exception(f"Error compiling Declo code: {str(e)}")
