class TuringMachine:
    def __init__(self, tape):
        self.tape = list(tape)
        self.accepted = False
        self.message = ""
        self.error_line = 1
        self.error_column = 1

    def validate_binary(self, input_str):
        for i, c in enumerate(input_str):
            if c not in ['0', '1']:
                self.error_line = 1
                self.error_column = i + 1
                return False
        return True

    def run(self):
        input_str = ''.join(self.tape)
        
        # Validar que solo contenga 1s y 0s
        if not self.validate_binary(input_str):
            self.accepted = False
            self.message = {
                'text': "ERROR LÉXICO: La cadena solo puede contener símbolos del alfabeto Σ = {0,1}",
                'line': self.error_line,
                'column': self.error_column
            }
            return self.accepted, input_str, self.message, []

        # Validar que la longitud sea par
        if len(self.tape) % 2 != 0:
            self.accepted = False
            self.message = {
                'text': "ERROR SINTÁCTICO: La longitud de la cadena debe ser par (secuencias de '10')",
                'line': 1,
                'column': len(self.tape)
            }
            return self.accepted, input_str, self.message, []

        # Validar que termine en 0
        if self.tape[-1] != '0':
            self.accepted = False
            self.message = {
                'text': "ERROR SINTÁCTICO: La cadena debe terminar con el símbolo '0'",
                'line': 1,
                'column': len(self.tape)
            }
            return self.accepted, input_str, self.message, []

        # Validar que sean pares de 10
        for i in range(0, len(self.tape), 2):
            if self.tape[i] != '1' or self.tape[i+1] != '0':
                self.accepted = False
                self.message = {
                    'text': "ERROR SINTÁCTICO: La cadena debe estar formada por secuencias del par ordenado (1,0)",
                    'line': 1,
                    'column': i + 1
                }
                return self.accepted, input_str, self.message, []

        self.accepted = True
        self.message = "ACEPTADO"
        return self.accepted, input_str, self.message, []
