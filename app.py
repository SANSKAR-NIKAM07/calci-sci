from flask import Flask, render_template, request, jsonify
import ast
import operator
import math

app = Flask(__name__)

SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

SAFE_NAMES = {
    'pi': math.pi,
    'e': math.e,
    'tau': math.tau,
    'inf': math.inf,
    'nan': math.nan,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'sqrt': math.sqrt,
    'log': math.log,
    'log10': math.log10,
    'log2': math.log2,
    'exp': math.exp,
    'pow': pow,
    'abs': abs,
    'floor': math.floor,
    'ceil': math.ceil,
    'factorial': math.factorial,
    'degrees': math.degrees,
    'radians': math.radians,
}


def safe_eval(expr: str):
    expr = expr.strip()
    if not expr:
        raise ValueError('Empty expression')
    node = ast.parse(expr, mode='eval')

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op = SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError('Operator not allowed')
            return op(left, right)
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            op = SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError('Operator not allowed')
            return op(operand)
        if isinstance(node, ast.Call):
            func = node.func
            if not isinstance(func, ast.Name):
                raise ValueError('Invalid function call')
            func_name = func.id
            if func_name not in SAFE_NAMES:
                raise ValueError(f'Function {func_name} is not allowed')
            fn = SAFE_NAMES[func_name]
            args = [_eval(arg) for arg in node.args]
            return fn(*args)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):  # type: ignore[arg-type]
                return node.value
            raise ValueError('Invalid constant')
        if isinstance(node, ast.Name):
            if node.id in SAFE_NAMES:
                return SAFE_NAMES[node.id]
            raise ValueError(f'Unknown name: {node.id}')
        raise ValueError('Unsupported expression')

    return _eval(node)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json or {}
    expression = data.get('expression', '')
    try:
        result = safe_eval(expression)
        return jsonify({'result': str(result)})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 400


if __name__ == '__main__':
    app.run(debug=True)
