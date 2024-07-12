from declo.tools import converter

def test_converter():
    code = "y => y + 1"
    func = converter(code)
    assert func(5) == 6