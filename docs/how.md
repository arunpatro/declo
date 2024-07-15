---
title: How does Declo work?
---

The goal of declo is to manipulate Python objects with JavaScript syntax. We can do using three strategies, each of them have their own trade-offs:

## 1. Source to Source
Convert `js src => py src`. This can be kinda hard because of regex parsing etc, it will involve creating a custom grammar parser. This can be good at the start, but can quickly get complex, as and when we add more features. A simple way is:
```python
def arrow_func(js_code = "x => x + 1"):
    parts = js_code.replace(" ", "").split("=>")

    if len(parts) != 2:
        raise ValueError("Invalid arrow_func expression format")

    param, body = parts
    py_code = f"lambda {param}: {body}"
    code_obj = compile(py_code, "<string>", "eval")

    return eval(code_obj)
```



## 2. AST to AST
Convert `js ast => py ast`. It is easier to work with structured data. Coding the rules for the equivalence is relatively easier. We provide this api in `declo.ast.ast_js2py`. This can get a little verbose too:
```python
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
```

## 3. SRC to AST
Convert `js src => py ast`. End to End convertion would be the best, but is the most complex which requires a mix of S1 and S2. We could do this by patching the python grammar `Python.asdl` to support the new syntax. See: ... We don't have to recompile python to run this code, we just reuse the python pgen parser with our new `JsPython.asdl` to directly create the python objects. 