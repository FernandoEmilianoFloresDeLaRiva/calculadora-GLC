from flask import Flask, render_template, request, jsonify
from lark import Lark, Transformer, Tree, Token

app = Flask(__name__)

# Gramática libre de contexto
grammar = """
?start: expr
?expr: term
     | expr "+" term   -> add
     | expr "-" term   -> sub
?term: factor
     | term "*" factor -> mul
     | term "/" factor -> div
?factor: NUMBER        -> number
       | "(" expr ")"  -> parens
NUMBER: /\d+(\.\d+)?/
%ignore " "            // Ignorar espacios en blanco
"""

# Analizador de Lark
parser = Lark(grammar, start='start', parser='lalr')

# Transformer para evaluar las expresiones
class EvalTransformer(Transformer):
    def add(self, args):
        return args[0] + args[1]

    def sub(self, args):
        return args[0] - args[1]

    def mul(self, args):
        return args[0] * args[1]

    def div(self, args):
        if args[1] == 0:
            raise ValueError("División por cero")
        return args[0] / args[1]

    def number(self, args):
        return float(args[0])

    def parens(self, args):
        return args[0]

def tree_to_json(tree):
    if isinstance(tree, Token):
        return {"name": tree.value}  # Token como hoja
    elif isinstance(tree, Tree):
        return {
            "name": tree.data,  # Nodo
            "children": [tree_to_json(child) for child in tree.children]
        }
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        expression = request.form['expression']
        tree = parser.parse(expression)
        result = EvalTransformer().transform(tree)
        tree_json = tree_to_json(tree)
        return jsonify({'result': result, 'tree_json': tree_json})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
