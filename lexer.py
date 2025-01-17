import re

# Define token types with regular expressions
TOKEN_TYPES = {
    'KEYWORD': r'\b(Var|Instructions|byte|Array|mov|add|sub|mult|div|and|or|not|jmp|jz|js|jo|input|print|halt|push|pop|isFull|call)\b',
    'IDENTIFIER': r'\b[a-zA-Z][a-zA-Z0-9_]*\b',
    'NUMBER': r'\b[+-]?[0-9]+\b',
    'OPERATOR': r'[+\-*/]',
    'PUNCTUATION': r'[,:;\[\]\(\)]',
    'WHITESPACE': r'\s+',
}

# Token class to represent each token
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f'Token({self.type}, {self.value})'

# Lexer class to tokenize the input code
class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.tokenize()

    def tokenize(self):
        code = self.code
        while code:
            match = None
            for token_type, pattern in TOKEN_TYPES.items():
                regex = re.compile(pattern)
                match = regex.match(code)
                if match:
                    value = match.group(0)
                    if token_type != 'WHITESPACE':  # Ignore whitespace
                        self.tokens.append(Token(token_type, value))
                    code = code[len(value):]  # Move to the next part of the code
                    break
            if not match:
                raise SyntaxError(f'Unexpected character: {code[0]}')
        self.tokens.append(Token('EOF', 'EOF'))  # End of file token

# Example usage
if __name__ == '__main__':
    code = '''
    Var x: byte, y: Array[10]
    Instructions
    1: mov x, 5;
    2: add x, y[0];
    3: print(x);
    4: halt;
    '''
    lexer = Lexer(code)
    for token in lexer.tokens:
        print(token)