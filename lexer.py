import re

# regex patterns for different token types - kinda messy but works ok
TOKEN_TYPES = {
    'KEYWORD': r'\b(Var|Instructions|byte|Array|mov|add|sub|mult|div|and|or|not|jmp|jz|js|jo|input|print|halt|push|pop|isFull|call)\b',
    'IDENTIFIER': r'\b[a-zA-Z][a-zA-Z0-9_]*\b',
    'NUMBER': r'\b[+-]?[0-9]+\b',
    'OPERATOR': r'[+\-*/]',
    'PUNCTUATION': r'[,:;\[\]\(\)]',
    'WHITESPACE': r'\s+',  # spaces tabs etc
}

# stores info about each token we find
class Token:
    def __init__(self, type, value):
        self.type = type  # what kind of token
        self.value = value  # actual text

    def __repr__(self):
        return f'Token({self.type}, {self.value})'

# breaks down source code into tokens
# not perfect but does the job for our simple language
class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []  # gonna store all tokens here
        self.tokenize()  # do the actual work

    def tokenize(self):
        code = self.code
        while code:  # keep going till we process everything
            match = None
            # try each pattern until something matches
            for token_type, pattern in TOKEN_TYPES.items():
                regex = re.compile(pattern)
                match = regex.match(code)
                if match:
                    value = match.group(0)
                    # dont care about whitespace - skip it
                    if token_type != 'WHITESPACE':
                        self.tokens.append(Token(token_type, value))
                    code = code[len(value):]  # move forward in the code
                    break
            
            # uh oh - found something we dont understand
            if not match:
                raise SyntaxError(f'Weird character found: {code[0]}')
        
        # add special token to mark the end
        self.tokens.append(Token('EOF', 'EOF'))

# quick test to make sure it works
if __name__ == '__main__':
    code = '''
    Var x: byte, y: Array[10]
    Instructions
    1: mov x, 5;
    2: add x, y[0];  # add first element to x
    3: print(x);     # show result 
    4: halt;         # done!
    '''
    lexer = Lexer(code)
    for token in lexer.tokens:
        print(token)  # lets see what we got