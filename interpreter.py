from lexer import Lexer, Token
from parser import Parser

class Interpreter:
    def __init__(self, ast, debug_mode=False):
        self.ast = ast
        self.data_segment = [0] * 700  # Segment de données de 700 octets
        self.stack_segment = [0] * 500  # Segment de pile de 500 octets
        self.flags = {'ZF': 0, 'SF': 0, 'OF': 0}  # Flags d'état
        self.CO = 0  # Compteur ordinal
        self.registers = {'AX': 0, 'BX': 0, 'CX': 0, 'DX': 0}  # Registres
        self.variables = {}  # Dictionnaire pour stocker les variables
        self.variable_addresses = {}  # Dictionnaire pour stocker les adresses des variables
        self.current_address = 0  # Adresse actuelle pour le stockage des variables
        self.stack_pointer = 0  # Pointeur de pile
        self.debug_mode = debug_mode

    def debug(self, message):
        if self.debug_mode:
            print(f'DEBUG: {message}')

    def run(self):
        self.debug('Starting interpretation')
        self.parse_declarations()
        self.execute_instructions()
        self.debug('Finished interpretation')

    def parse_declarations(self):
        # Parcourir l'AST pour trouver les déclarations de variables et les initialiser
        for node in self.ast:
            if node['type'] == 'declaration':
                self.declare_variable(node)

    def declare_variable(self, node):
        # Initialiser les variables dans le segment de données
        var_name = node['name']
        var_type = node['var_type']
        if var_type == 'byte':
            self.variables[var_name] = 0  # Initialiser à 0
            self.variable_addresses[var_name] = self.current_address
            self.current_address += 1
        elif var_type.startswith('Array'):
            size = int(var_type.split('[')[1].split(']')[0])
            self.variables[var_name] = [0] * size  # Initialiser un tableau de la taille spécifiée
            self.variable_addresses[var_name] = self.current_address
            self.current_address += size
        self.debug(f'Declared variable {var_name} of type {var_type} at address {self.variable_addresses[var_name]}')

    def execute_instructions(self):
        # Parcourir l'AST pour exécuter les instructions
        while self.CO < len(self.ast):
            node = self.ast[self.CO]
            if node['type'] == 'instruction':
                self.execute_instruction(node)
            self.CO += 1

    def execute_instruction(self, node):
        command = node['command']
        operands = node['operands']
        if command == 'mov':
            self.mov(operands[0], operands[1])
        elif command == 'add':
            self.add(operands[0], operands[1])
        elif command == 'sub':
            self.sub(operands[0], operands[1])
        elif command == 'mult':
            self.mult(operands[0], operands[1])
        elif command == 'div':
            self.div(operands[0], operands[1])
        elif command == 'and':
            self.and_op(operands[0], operands[1])
        elif command == 'or':
            self.or_op(operands[0], operands[1])
        elif command == 'not':
            self.not_op(operands[0])
        elif command == 'jmp':
            self.jmp(operands[0])
        elif command == 'jz':
            self.jz(operands[0])
        elif command == 'js':
            self.js(operands[0])
        elif command == 'jo':
            self.jo(operands[0])
        elif command == 'input':
            self.input_op(operands[0])
        elif command == 'print':
            self.print_op(operands[0])
        elif command == 'halt':
            self.halt()
        elif command == 'push':
            self.push(operands[0])
        elif command == 'pop':
            self.pop(operands[0])
        elif command == 'isFull':
            self.isFull()
        elif command == 'call':
            self.call(operands[0])
        else:
            self.error(f'Unknown command {command}')

    def mov(self, dest, src):
        self.debug(f'Executing mov {dest}, {src}')
        self.variables[dest] = self.get_value(src)

    def add(self, dest, src):
        self.debug(f'Executing add {dest}, {src}')
        self.variables[dest] += self.get_value(src)
        self.update_flags(self.variables[dest])

    def sub(self, dest, src):
        self.debug(f'Executing sub {dest}, {src}')
        self.variables[dest] -= self.get_value(src)
        self.update_flags(self.variables[dest])

    def mult(self, dest, src):
        self.debug(f'Executing mult {dest}, {src}')
        self.variables[dest] *= self.get_value(src)
        self.update_flags(self.variables[dest])

    def div(self, dest, src):
        self.debug(f'Executing div {dest}, {src}')
        self.variables[dest] //= self.get_value(src)
        self.update_flags(self.variables[dest])

    def and_op(self, dest, src):
        self.debug(f'Executing and {dest}, {src}')
        self.variables[dest] &= self.get_value(src)
        self.update_flags(self.variables[dest])

    def or_op(self, dest, src):
        self.debug(f'Executing or {dest}, {src}')
        self.variables[dest] |= self.get_value(src)
        self.update_flags(self.variables[dest])

    def not_op(self, dest):
        self.debug(f'Executing not {dest}')
        self.variables[dest] = ~self.variables[dest]
        self.update_flags(self.variables[dest])

    def jmp(self, address):
        self.debug(f'Executing jmp {address}')
        self.CO = address - 1  # Adjust for the increment in execute_instructions

    def jz(self, address):
        self.debug(f'Executing jz {address}')
        if self.flags['ZF'] == 1:
            self.CO = address - 1  # Adjust for the increment in execute_instructions

    def js(self, address):
        self.debug(f'Executing js {address}')
        if self.flags['SF'] == 1:
            self.CO = address - 1  # Adjust for the increment in execute_instructions

    def jo(self, address):
        self.debug(f'Executing jo {address}')
        if self.flags['OF'] == 1:
            self.CO = address - 1  # Adjust for the increment in execute_instructions

    def input_op(self, dest):
        self.debug(f'Executing input {dest}')
        self.variables[dest] = int(input(f'Input value for {dest}: '))

    def print_op(self, src):
        self.debug(f'Executing print {src}')
        print(self.get_value(src))

    def halt(self):
        self.debug('Executing halt')
        exit()

    def push(self, src):
        self.debug(f'Executing push {src}')
        if self.stack_pointer >= len(self.stack_segment):
            self.error('Stack overflow')
        self.stack_segment[self.stack_pointer] = self.get_value(src)
        self.stack_pointer += 1

    def pop(self, dest):
        self.debug(f'Executing pop {dest}')
        if self.stack_pointer == 0:
            self.error('Stack underflow')
        self.stack_pointer -= 1
        self.variables[dest] = self.stack_segment[self.stack_pointer]

    def isFull(self):
        self.debug('Executing isFull')
        print(self.stack_pointer >= len(self.stack_segment))

    def call(self, function_name):
        self.debug(f'Executing call {function_name}')
        # Implementation of call depends on the function definitions

    def get_value(self, operand):
        if isinstance(operand, int) or operand.isdigit():
            return int(operand)
        elif '[' in operand and ']' in operand:
            var_name, index = operand.split('[')
            index = int(index[:-1])  # Remove the closing bracket
            return self.variables[var_name][index]
        elif operand in self.variables:
            return self.variables[operand]
        else:
            self.error(f'Unknown operand {operand}')

    def update_flags(self, result):
        self.flags['ZF'] = 1 if result == 0 else 0
        self.flags['SF'] = 1 if result >= 0 else 0
        self.flags['OF'] = 1 if result < -127 or result > 128 else 0

    def error(self, message):
        raise RuntimeError(message)

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
    interpreter = Interpreter(ast, debug_mode=True)
    interpreter.run()