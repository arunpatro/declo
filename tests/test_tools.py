# from declo.tools import converter
import json
from declo.ast import parse_js, ast_js2py
# def test_converter():
#     code = "y => y + 1"
#     func = converter(code)
#     assert func(5) == 6

import pytest
import ast

@pytest.fixture
def test_bench():
    with open("tests/test_bench.json", "r") as f:
        return json.load(f)
    
def test_test_bench(test_bench):
    test_cases = test_bench["testCases"]

    for test_case in test_cases:
        print(f"Testing topic: {test_case['topic']}")
        for case in test_case["cases"]:
            js_code = case["js"]
            js_ast = parse_js(js_code)
            python_code = case["python"]
            _python_ast = ast.dump(ast.parse(python_code), indent=4)
            
            # pred 
            python_ast = ast_js2py(js_ast)
            python_ast = ast.dump(python_ast, indent=4)
            print(f"JS AST: {js_ast}")
            print(f"_Python AST: {_python_ast}")
            print(f"Python AST: {python_ast}")
            assert _python_ast == python_ast