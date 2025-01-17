from lexer import Lexer, Token

class Parser:
    def __init__(self, tokens, debug_mode=False):
        self.tokens = tokens
        self.current_token = None
        self.debug_mode = debug_mode
        self.ast = []
        self.next_token()

    def debug(self, message):
        if self.debug_mode:
            print(f'DEBUG: {message}')

    def next_token(self):
        if self.tokens:
            self.current_token = self.tokens.pop(0)
        else:
            self.current_token = Token('EOF', 'EOF')
        self.debug(f'Next token: {self.current_token}')

    def parse(self):
        self.debug('Starting parse')
        self.programme()
        self.debug('Finished parse')
        return self.ast

    def programme(self):
        self.debug('Parsing programme')
        self.declaration()
        self.liste_instructions()

    def declaration(self):
        self.debug('Parsing declaration')
        self.match('KEYWORD', 'Var')
        self.liste_declarations()
        self.match('PUNCTUATION', ';')

    def liste_declarations(self):
        self.debug('Parsing liste_declarations')
        self.declaration_variable()
        while self.current_token.type == 'PUNCTUATION' and self.current_token.value == ',':
            self.next_token()
            self.declaration_variable()

    def declaration_variable(self):
        self.debug('Parsing declaration_variable')
        var_name = self.current_token.value
        self.match('IDENTIFIER')
        self.match('PUNCTUATION', ':')
        var_type = self.type()
        self.ast.append({'type': 'declaration', 'name': var_name, 'var_type': var_type})

    def type(self):
        self.debug('Parsing type')
        if self.current_token.type == 'KEYWORD' and self.current_token.value == 'byte':
            var_type = 'byte'
            self.next_token()
        elif self.current_token.type == 'KEYWORD' and self.current_token.value == 'Array':
            self.next_token()
            self.match('PUNCTUATION', '[')
            size = self.current_token.value
            self.match('NUMBER')
            self.match('PUNCTUATION', ']')
            var_type = f'Array[{size}]'
        else:
            self.error('Expected type')
        return var_type

    def liste_instructions(self):
        self.debug('Parsing liste_instructions')
        while self.current_token.type == 'KEYWORD':
            self.instruction()

    def instruction(self):
        self.debug('Parsing instruction')
        command = self.current_token.value
        self.commande()
        self.match('PUNCTUATION', ';')
        self.ast.append({'type': 'instruction', 'command': command, 'operands': self.operands})

    def commande(self):
        self.debug(f'Parsing commande: {self.current_token.value}')
        if self.current_token.type == 'KEYWORD':
            command = self.current_token.value
            self.next_token()
            self.operands = []
            if command in ['mov', 'add', 'sub', 'mult', 'div', 'and', 'or']:
                self.operands.append(self.operande())
                self.match('PUNCTUATION', ',')
                self.operands.append(self.operande())
            elif command == 'not':
                self.operands.append(self.operande())
            elif command in ['jmp', 'jz', 'js', 'jo']:
                self.operands.append(self.current_token.value)
                self.match('NUMBER')
            elif command in ['input', 'print']:
                self.match('PUNCTUATION', '(')
                self.operands.append(self.operande())
                self.match('PUNCTUATION', ')')
            elif command == 'halt':
                pass
            elif command in ['push', 'pop']:
                self.operands.append(self.operande())
            elif command == 'isFull':
                pass
            elif command == 'call':
                self.operands.append(self.current_token.value)
                self.match('IDENTIFIER')
            else:
                self.error('Unknown command')
        else:
            self.error('Expected command')

    def operande(self):
        self.debug('Parsing operande')
        if self.current_token.type == 'IDENTIFIER':
            operand = self.current_token.value
            self.next_token()
            if self.current_token.type == 'PUNCTUATION' and self.current_token.value == '[':
                self.next_token()
                index = self.current_token.value
                self.match('NUMBER')
                self.match('PUNCTUATION', ']')
                operand = f'{operand}[{index}]'
        elif self.current_token.type == 'NUMBER':
            operand = self.current_token.value
            self.next_token()
        else:
            self.error('Expected operand')
        return operand

    def match(self, type, value=None):
        self.debug(f'Matching {type} {value}')
        if self.current_token.type == type and (value is None or self.current_token.value == value):
            self.next_token()
        else:
            self.error(f'Expected {type} {value}')

    def error(self, message):
        raise SyntaxError(f'{message} at {self.current_token}')

# Example usage
if __name__ == '__main__':
    code = '''
    Var x: byte, y: Array[10];
    mov x, 5;
    add x, y[0];
    print(x);
    halt;
    '''
    lexer = Lexer(code)
    parser = Parser(lexer.tokens, debug_mode=True)
    ast = parser.parse()
    print('AST:', ast)
    print('Parsing completed successfully')