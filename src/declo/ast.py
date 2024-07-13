from typing import List, Optional, Union
from pydantic import BaseModel, Field
import ast

# Define Pydantic models for JavaScript AST nodes
class Identifier(BaseModel):
    type: str
    name: str

class Literal(BaseModel):
    type: str
    value: Union[int, float, str, bool, None]
    raw: str

class BinaryExpression(BaseModel):
    type: str
    left: Union["Identifier", "Literal"]
    operator: str
    right: Union["Identifier", "Literal"]

class ArrowFunctionExpression(BaseModel):
    type: str
    id: Optional[None]
    expression: bool
    generator: bool
    async_: bool = Field(..., alias='async')
    params: List[Identifier]
    body: BinaryExpression

class ExpressionStatement(BaseModel):
    type: str
    expression: ArrowFunctionExpression

class Program(BaseModel):
    type: str
    body: List[Union[ExpressionStatement, ArrowFunctionExpression, BinaryExpression, Identifier, Literal]]
    sourceType: str

Program.model_rebuild()


def ast_js2py(js_node: Union[Program, ExpressionStatement, ArrowFunctionExpression, BinaryExpression, Identifier, Literal]) -> ast.AST:
    if isinstance(js_node, Program):
        return ast.Module(body=[ast_js2py(stmt) for stmt in js_node.body], type_ignores=[])
    elif isinstance(js_node, ExpressionStatement):
        return ast.Expr(value=ast_js2py(js_node.expression))
    elif isinstance(js_node, ArrowFunctionExpression):
        return ast.Lambda(
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg=param.name, annotation=None, type_comment=None) for param in js_node.params],
                vararg=None,
                kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
            ),
            body=ast_js2py(js_node.body)
        )
    elif isinstance(js_node, BinaryExpression):
        return ast.BinOp(
            left=ast_js2py(js_node.left),
            op=ast.Add() if js_node.operator == "+" else None,  # Extend this for other operators
            right=ast_js2py(js_node.right)
        )
    elif isinstance(js_node, Identifier):
        return ast.Name(id=js_node.name, ctx=ast.Load())
    elif isinstance(js_node, Literal):
        return ast.Constant(value=js_node.value, kind=None)
    else:
        raise ValueError(f"Unsupported JS AST node type: {js_node.__class__.__name__}")


def parse_js_ast_dict(js_ast_dict):
    return Program(**js_ast_dict)