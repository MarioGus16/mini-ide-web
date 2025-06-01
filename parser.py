import lexer

class ParserError(Exception):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"{message} (línea {line}, columna {column})")

def analyze(code):
    tokens, lex_errors = lexer.analyze(code)
    if lex_errors:
        errors = [{'line': e['line'], 'column': e['column'], 'message': f"Error léxico: '{e['value']}'"} for e in lex_errors]
        return errors, None

    # Verificar operador al inicio
    if tokens and tokens[0]['type'] in {'OP', 'ASIGNAR'}:
        errors = [{'line': tokens[0]['line'], 'column': tokens[0]['column'], 'message': "No se puede iniciar con un operador"}]
        return errors, None

    # Verificar paréntesis balanceados
    stack = []
    errors_parentesis = []
    
    for token in tokens:
        if token['type'] == 'PAR_IZQ':
            stack.append(token)
        elif token['type'] == 'PAR_DER':
            if not stack:  # Si encontramos un paréntesis derecho sin su correspondiente izquierdo
                errors_parentesis.append({
                    'line': token['line'],
                    'column': token['column'],
                    'message': "Se encontró un paréntesis de cierre ')' sin su correspondiente paréntesis de apertura '('"
                })
            else:
                stack.pop()

    # Si quedaron paréntesis sin cerrar
    for token in stack:
        errors_parentesis.append({
            'line': token['line'],
            'column': token['column'],
            'message': "El paréntesis de apertura '(' no tiene su correspondiente paréntesis de cierre ')'"
        })

    if errors_parentesis:
        return errors_parentesis, None

    index = 0
    errors = []
    lines = code.split('\n')
    current_line = 1
    processed_lines = set()

    def peek():
        return tokens[index] if index < len(tokens) else None

    def consume(expected_type=None):
        nonlocal index
        token = peek()
        if token and (expected_type is None or token['type'] == expected_type):
            index += 1
            return token
        return None

    def check_line_for_assignment(line_num, line_text):
        if line_num in processed_lines:
            return
        
        tokens_in_line = [t for t in tokens if t['line'] == line_num]
        if tokens_in_line:
            has_id = any(t['type'] == 'ID' for t in tokens_in_line)
            has_assign = any(t['type'] == 'ASIGNAR' for t in tokens_in_line)

            if has_id and not has_assign and not line_text.strip().startswith('//'):
                errors.append({
                    'line': line_num,
                    'column': 1,
                    'message': "Falta asignarle valor"
                })
                processed_lines.add(line_num)

    def parse_primary():
        token = peek()
        if token and token['type'] in {'ID', 'NUMERO'}:
            consume()
            return True
        elif token and token['type'] == 'PAR_IZQ':
            consume('PAR_IZQ')
            if parse_expr():
                if consume('PAR_DER'):
                    return True
                else:
                    errors.append({'line': token['line'], 'column': token['column'], 'message': "Falta paréntesis de cierre"})
                    return False
            else:
                errors.append({'line': token['line'], 'column': token['column'], 'message': "Expresión inválida"})
                return False
        return False

    def parse_expr():
        token = peek()
        if not token:
            return False

        # Verificar operador suelto
        if token['type'] in {'OP', 'ASIGNAR'}:
            next_token = tokens[index + 1] if index + 1 < len(tokens) else None
            if not next_token or next_token['type'] in {'OP', 'ASIGNAR'}:
                errors.append({
                    'line': token['line'],
                    'column': token['column'],
                    'message': "Operador suelto no permitido"
                })
                return False

        if token['type'] == 'ID':
            id_token = consume('ID')
            next_token = peek()
            
            if next_token and next_token['type'] == 'ASIGNAR':
                consume('ASIGNAR')
                if not parse_expr():
                    errors.append({
                        'line': id_token['line'],
                        'column': id_token['column'] + len(id_token['value']) + 1,
                        'message': "Falta valor después de '='"
                    })
                    return False
                return True
            elif next_token and next_token['type'] == 'OP':
                consume('ID')
                op_token = consume('OP')
                if not parse_primary():
                    errors.append({
                        'line': op_token['line'],
                        'column': op_token['column'],
                        'message': "Operador sin operando"
                    })
                    return False
                return True
            else:
                errors.append({
                    'line': id_token['line'],
                    'column': id_token['column'],
                    'message': "Falta asignarle valor"
                })
                return False
        
        return parse_primary()

    # Analizar el código
    while index < len(tokens):
        if not parse_expr():
            index += 1

    if errors:
        # Eliminar duplicados manteniendo el orden
        unique_errors = []
        seen = set()
        for error in errors:
            key = (error['line'], error['column'], error['message'])
            if key not in seen:
                seen.add(key)
                unique_errors.append(error)
        return unique_errors, None
    else:
        return None, ["Código sintácticamente válido"]
