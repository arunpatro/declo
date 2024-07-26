from typing import Union
from pydantic import BaseModel, Field
import ast
import esprima

# Define Pydantic models for JavaScript AST nodes
class Identifier(BaseModel):
    type: str
    name: str | None = None

class Literal(BaseModel):
    type: str
    value: int | float | str | bool | None = None
    raw: str | None = None

class BinaryExpression(BaseModel):
    type: str
    left: "Identifier" | "Literal" | None = None
    operator: str | None = None
    right: "Identifier" | "Literal" | None = None

    class Config:
        arbitrary_types_allowed = True
        fields = {
            'left': {'discriminator': 'type'},
            'right': {'discriminator': 'type'},
        }

class ArrowFunctionExpression(BaseModel):
    type: str
    id: None = None
    expression: bool | None = None
    generator: bool | None = None
    async_: bool | None = Field(None, alias='async')
    params: list[Identifier] | None = None
    body: BinaryExpression | None = None

    class Config:
        arbitrary_types_allowed = True

class ExpressionStatement(BaseModel):
    type: str
    expression: ArrowFunctionExpression | None = None

class Program(BaseModel):
    type: str
    body: list[ExpressionStatement | ArrowFunctionExpression | BinaryExpression | Identifier | Literal] | None = None
    sourceType: str | None = None

Program.model_rebuild()

def parse_js(js_code) -> Program:
    js_ast_dict = esprima.parseScript(js_code).toDict()
    return Program(**js_ast_dict)


def ast_js2py(js_node: Program | ExpressionStatement | ArrowFunctionExpression | BinaryExpression | Identifier | Literal) -> ast.AST:
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

