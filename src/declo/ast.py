from typing import Union, List, Optional

from pydantic import BaseModel, Field
import ast
import esprima

# Define Pydantic models for JavaScript AST nodes

class Identifier(BaseModel):
    type: str
    name: str

class Literal(BaseModel):
    type: str
    value: Union[int, float, str, bool, None] = None
    raw: str | None = None

class BinaryExpression(BaseModel):
    type: str
    left: Union["Identifier", "Literal", "BinaryExpression"]
    operator: str
    right: Union["Identifier", "Literal", "BinaryExpression"]

class BlockStatement(BaseModel):
    type: str
    body: List[Union["VariableDeclaration", "ReturnStatement", "ExpressionStatement"]]

class VariableDeclaration(BaseModel):
    type: str
    declarations: List["VariableDeclarator"]
    kind: str

class VariableDeclarator(BaseModel):
    type: str
    id: Identifier
    init: Union["ArrowFunctionExpression", BinaryExpression, Identifier, Literal]

class ReturnStatement(BaseModel):
    type: str
    argument: Union[BinaryExpression, Identifier, Literal]

class ArrowFunctionExpression(BaseModel):
    type: str
    expression: bool
    generator: bool
    async_: bool = Field(alias='async')
    params: List[Identifier]
    body: Union[BinaryExpression, BlockStatement]

class ExpressionStatement(BaseModel):
    type: str
    expression: ArrowFunctionExpression

class Program(BaseModel):
    type: str
    body: List[Union[VariableDeclaration, ExpressionStatement]]
    sourceType: str

Program.model_rebuild()


def parse_js(js_code) -> Program:
    js_ast_dict = esprima.parseScript(js_code).toDict()
    return Program(**js_ast_dict)


def ast_js2py(js_node: Program | ExpressionStatement | ArrowFunctionExpression | BinaryExpression | Identifier | Literal | BlockStatement | VariableDeclaration | VariableDeclarator | ReturnStatement, name:str=None) -> ast.AST:
    match js_node:
        case Program():
            return ast.Module(body=[ast_js2py(stmt) for stmt in js_node.body], type_ignores=[])
        case VariableDeclaration() if js_node.kind == 'const' and len(js_node.declarations) == 1:
            declarator = js_node.declarations[0]
            if isinstance(declarator.init, ArrowFunctionExpression):
                return ast_js2py(declarator.init, name=declarator.id.name)
        case ArrowFunctionExpression():
            function_name = name if name else '<lambda>'
            return ast.FunctionDef(
                name=function_name,
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg=param.name) for param in js_node.params],
                    kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
                ),
                body=[ast_js2py(stmt) for stmt in js_node.body.body] if isinstance(js_node.body, BlockStatement) else [ast.Return(value=ast_js2py(js_node.body))],
                decorator_list=[]
            )
        case BlockStatement():
            return [ast_js2py(stmt) for stmt in js_node.body]
        case VariableDeclaration():
            return ast.Assign(
                targets=[ast.Name(id=declarator.id.name, ctx=ast.Store()) for declarator in js_node.declarations],
                value=ast_js2py(js_node.declarations[0].init)
            )
        case ReturnStatement():
            return ast.Return(value=ast_js2py(js_node.argument))
        case BinaryExpression():
            op_map = {
                "+": ast.Add(),
                "-": ast.Sub(),
                "*": ast.Mult(),
                "/": ast.Div(),
                "**": ast.Pow(),
                "%": ast.Mod(),
                "<<": ast.LShift(),
                ">>": ast.RShift(),
                "|": ast.BitOr(),
                "^": ast.BitXor(),
                "&": ast.BitAnd(),
                "//": ast.FloorDiv()
            }
            return ast.BinOp(
                left=ast_js2py(js_node.left),
                op=op_map.get(js_node.operator, ast.Add()),
                right=ast_js2py(js_node.right)
            )
        case Identifier():
            print("Matched Identifier")
            return ast.Name(id=js_node.name, ctx=ast.Load())
        case Literal():
            print("Matched Literal")
            return ast.Constant(value=js_node.value)
        case ExpressionStatement():
            print("Matched ExpressionStatement")
            return ast.Expr(value=ast_js2py(js_node.expression))
        case _:
            print(f"Unsupported JS AST node type: {type(js_node).__name__}")
            raise ValueError(f"Unsupported JS AST node type: {type(js_node).__name__}")
