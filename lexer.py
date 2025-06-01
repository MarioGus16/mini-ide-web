import re

TOKEN_SPECIFICATION = [
    ('NUMERO',   r'\d+(\.\d*)?'),     # Números enteros o decimales
    ('ID',       r'[a-zA-Z_]\w*'),    # Identificadores
    ('ASIGNAR',  r'='),               # Asignación
    ('OP',       r'[+\-*/<>]'),       # Operadores
    ('PAR_IZQ',  r'\('),              # Paréntesis izquierdo
    ('PAR_DER',  r'\)'),              # Paréntesis derecho
    ('ESPACIO',  r'[ \t]+'),          # Espacios y tabulaciones (ignorar)
    ('SALTO',    r'\n'),              # Saltos de línea (para contar líneas)
]

token_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPECIFICATION)
get_token = re.compile(token_regex).match

def analyze(code):
    line_num = 1
    line_start = 0
    pos = 0
    tokens = []
    errors = []

    while pos < len(code):
        mo = get_token(code, pos)
        if mo:
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'SALTO':
                line_num += 1
                line_start = mo.end()
            elif kind == 'ESPACIO':
                pass
            else:
                column = pos - line_start + 1
                tokens.append({'type': kind, 'value': value, 'line': line_num, 'column': column})
            pos = mo.end()
        else:
            column = pos - line_start + 1
            errors.append({'value': code[pos], 'line': line_num, 'column': column})
            pos += 1

    return tokens, errors
