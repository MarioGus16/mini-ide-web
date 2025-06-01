from flask import Flask, render_template, request, jsonify
import lexer
import parser
import turing

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze/lexical', methods=['POST'])
def analyze_lexical():
    data = request.get_json()
    code = data.get('code', '')
    tokens, errors = lexer.analyze(code)
    errors_msgs = [f"Error léxico: '{e['value']}' en línea {e['line']}, columna {e['column']}" for e in errors]
    return jsonify({'tokens': tokens, 'errors': errors_msgs})

@app.route('/analyze/syntactic', methods=['POST'])
def analyze_syntactic():
    data = request.get_json()
    code = data.get('code', '')
    errors, success = parser.analyze(code)
    if errors:
        return jsonify({'errors': errors})
    else:
        return jsonify({'success': success[0] if success else None})

@app.route('/analyze/turing', methods=['POST'])
def analyze_turing():
    data = request.get_json()
    code = data.get('code', '').strip()

    if any(c not in ['1', '0'] for c in code):
        return jsonify({'errors': ["La cinta solo puede contener los caracteres '1' y '0'."]})

    machine = turing.TuringMachine(code)
    accepted, final_tape, message, history = machine.run()

    if isinstance(message, dict):
        # Es un mensaje de error con información de línea y columna
        return jsonify({
            'turing_result': accepted,
            'final_tape': final_tape,
            'final_state': message['text'],
            'errors': [{
                'line': message['line'],
                'column': message['column'],
                'message': message['text']
            }],
            'steps': history
        })
    else:
        # Es un mensaje de aceptación
        return jsonify({
            'turing_result': accepted,
            'final_tape': final_tape,
            'final_state': message,
            'errors': [],
            'steps': history
        })

if __name__ == '__main__':
    app.run(debug=True)
