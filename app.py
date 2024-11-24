from flask import Flask, render_template, request, jsonify
from lark import Lark, Transformer, Tree, Token
import ply.lex as lex

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

# Lexer con PLY
tokens = ('NUMERO', 'SUMA', 'RESTA', 'MULTIPLICACION', 'DIVISION')

t_SUMA = r'\+'
t_RESTA = r'-'
t_MULTIPLICACION = r'\*'
t_DIVISION = r'/'

def t_NUMERO(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

t_ignore = ' \t'

def t_error(t):
    raise SyntaxError(f"Illegal character '{t.value[0]}' at position {t.lexpos}")

lexer = lex.lex()

def analyze_tokens(expression):
    lexer.input(expression)
    total_numbers = 0
    total_operators = 0
    tokens_list = []

    for token in lexer:
        tokens_list.append({'type': token.type, 'value': token.value})
        if token.type == 'NUMERO':
            total_numbers += 1
        elif token.type in ('SUMA', 'RESTA', 'MULTIPLICACION', 'DIVISION'):
            total_operators += 1

    return {
        'total_numbers': total_numbers,
        'total_operators': total_operators,
        'tokens_list': tokens_list
    }

def tree_to_json(tree):
    rename_map = {
        "add": "+",
        "sub": "-",
        "mul": "*",
        "div": "/",
        "number": "n"
    }
    if isinstance(tree, Token):
        return {"name": tree.value}  # Token como hoja
    elif isinstance(tree, Tree):
        node_name = rename_map.get(tree.data, tree.data)
        return {
            "name": node_name,
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
        token_analysis = analyze_tokens(expression)
        return jsonify({
            'result': result, 
            'tree_json': tree_json, 
            'total_numbers': token_analysis['total_numbers'],
            'total_operators': token_analysis['total_operators'],
            'tokens_list': token_analysis['tokens_list']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
