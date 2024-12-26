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
    
    lines = code.split('\n')
    processed_lines = []
    
    for line in lines:
        while '=>' in line:
            start = line.find('(')
            replaced = False
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
                    before = line[:start + 1]
                    arrow_part = line[start + 1:end]
                    after = line[end:]
                    if '=>' in arrow_part:
                        arrow_part = process_arrow_function(arrow_part)
                        line = before + arrow_part + after
                        replaced = True
                        # Continue looking for more arrow functions in the same line
                        break
                start = line.find('(', start + 1)
            
            # If we didn't find a matching set of parentheses containing '=>', break the while
            if not replaced:
                break
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
                # If the underlying call is already a list comprehension, unify the if condition
                if isinstance(node.func.value, ast.ListComp):
                    listcomp = node.func.value
                    # Forward any existing elt from the list comp
                    # so we keep the top-level comprehension in one piece.
                    # Just add the new condition to the same generator.
                    listcomp.generators[0].ifs.append(lambda_node.body)
                    return listcomp

                # Regular filter operation
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
            # Remove parentheses by setting parenthesized to False
            if hasattr(node.elt, '_parenthesized'):
                node.elt._parenthesized = False
        return node

class CustomSourceGenerator(astor.SourceGenerator):
    """Custom source generator to handle list comprehension formatting."""

    # Helper method to stringify sub-AST nodes without calling self.to_source_string
    def _stringify_node(self, node: ast.AST) -> str:
        import io
        old_stream = self.stream
        buffer = io.StringIO()
        self.stream = buffer
        self.visit(node)
        self.stream = old_stream
        return buffer.getvalue()

    def visit_ListComp(self, node):
        self.write('[')
        self.visit(node.elt)
        for gen in node.generators:
            self.write(' for ')
            self.visit(gen.target)
            self.write(' in ')
            self.visit(gen.iter)
            for if_ in gen.ifs:
                self.write(' if ')
                self.visit(if_)
        self.write(']')

    def visit_BinOp(self, node):
        """Remove unnecessary parentheses for simple binops."""
        operator_map: dict[type[ast.operator], str] | None = {
            ast.Add: '+',
            ast.Sub: '-',
            ast.Mult: '*',
            ast.Div: '/',
            ast.Mod: '%',
            ast.Pow: '**',
            ast.FloorDiv: '//',
        }
        self.visit(node.left)
        self.write(' ')
        self.write(operator_map[type(node.op)])
        self.write(' ')
        self.visit(node.right)

    def visit_UnaryOp(self, node):
        """Print unary operations like -x without parentheses."""
        if isinstance(node.op, ast.USub):
            self.write('-')
        elif isinstance(node.op, ast.UAdd):
            self.write('+')
        self.visit(node.operand)

    def visit_Compare(self, node):
        """Print comparisons like x % 2 == 0 without extra parentheses."""
        cmp_ops: dict[type[ast.cmpop], str] | None = {
            ast.Eq: '==',
            ast.NotEq: '!=',
            ast.Lt: '<',
            ast.LtE: '<=',
            ast.Gt: '>',
            ast.GtE: '>=',
            ast.Is: 'is',
            ast.IsNot: 'is not',
            ast.In: 'in',
            ast.NotIn: 'not in',
        }
        self.visit(node.left)
        for op, comparator in zip(node.ops, node.comparators):
            self.write(' ')
            self.write(cmp_ops[type(op)])
            self.write(' ')
            self.visit(comparator)

    def visit_Dict(self, node):
        """
        Print dictionaries with quoted string keys and values,
        e.g. {'name': 'Alice'} not {name: Alice}.
        Avoid _stringify_node to prevent AttributeError from astor's code generator.
        """
        self.write('{')
        first = True
        for key, value in zip(node.keys, node.values):
            if not first:
                self.write(', ')
            else:
                first = False

            # Print key
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                self.write(f"'{key.value}'")
            else:
                self.visit(key)

            self.write(': ')

            # Print value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                self.write(f"'{value.value}'")
            else:
                self.visit(value)
        self.write('}')

    def visit_Constant(self, node):
        """
        Print string constants with quotes, numeric constants without parentheses.
        """
        if isinstance(node.value, str):
            self.write(f"'{node.value}'")
        else:
            self.write(str(node.value))

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
        tree = cleanup_transformer.visit(tree)
        
        # Configure astor for cleaner output
        astor_options = {
            'indent_with': ' ' * 4,
            'add_line_information': False,
            'source_generator_class': CustomSourceGenerator
        }
        
        # Generate Python code using astor
        return astor.to_source(tree, **astor_options).strip()
    except SyntaxError as e:
        raise SyntaxError(f"Invalid syntax in Declo code: {str(e)}")
    except Exception as e:
        raise Exception(f"Error compiling Declo code: {str(e)}")
