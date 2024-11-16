from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

def evaluate_expression(expr):
    def parse_expr(tokens):
        value = parse_term(tokens)
        while tokens and tokens[0] in ('+', '-'):
            op = tokens.pop(0)
            if op == '+':
                value += parse_term(tokens)
            elif op == '-':
                value -= parse_term(tokens)
        return value

    def parse_term(tokens):
        value = parse_factor(tokens)
        while tokens and tokens[0] in ('*', '/'):
            op = tokens.pop(0)
            if op == '*':
                value *= parse_factor(tokens)
            elif op == '/':
                value /= parse_factor(tokens)
        return value

    def parse_factor(tokens):
        if tokens[0] == '(':
            tokens.pop(0)  # Remove '('
            value = parse_expr(tokens)
            tokens.pop(0)  # Remove ')'
            return value
        else:
            return float(tokens.pop(0))  # Convert number to float

    # Tokenizer: Split expression into tokens
    tokens = re.findall(r'\d+\.\d+|\d+|[+\-*/()]', expr)
    return parse_expr(tokens)

# Rutas de Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        expression = request.form['expression']
        result = evaluate_expression(expression)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
