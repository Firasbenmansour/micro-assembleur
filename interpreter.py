from lexer import Lexer, Token
from parser import Parser

class Interpreter:
    def __init__(self, ast, debug_mode=False):
        self.ast = ast
        self.data_segment = [0] * 700  # 700 bytes for data storage
        self.stack_segment = [0] * 500  # stack memory - 500 bytes should be enough
        self.flags = {'ZF': 0, 'SF': 0, 'OF': 0}  # status flags for cmp etc
        self.CO = 0  # keeps track of current instruction
        self.registers = {'AX': 0, 'BX': 0, 'CX': 0, 'DX': 0}  # basic registers
        self.variables = {}  # store our variables here
        self.variable_addresses = {}  # remember where each var is stored
        self.current_address = 0  # next free memory slot
        self.stack_pointer = 0  # points to top of stack
        self.debug_mode = debug_mode

    def debug(self, message):
        if self.debug_mode:
            print(f'DEBUG: {message}')

    def run(self):
        self.debug('Starting interpretation')
        self.parse_declarations()
        self.execute_instructions()
        self.debug('All done!')

    def parse_declarations(self):
        # first pass - handle all the variable declarations
        for node in self.ast:
            if node['type'] == 'declaration':
                self.declare_variable(node)

    def declare_variable(self, node):
        # setup memory for a new variable
        var_name = node['name']
        var_type = node['var_type']
        if var_type == 'byte':
            self.variables[var_name] = 0  # start at zero
            self.variable_addresses[var_name] = self.current_address
            self.current_address += 1
        elif var_type.startswith('Array'):
            size = int(var_type.split('[')[1].split(']')[0])
            self.variables[var_name] = [0] * size  # zero out the array
            self.variable_addresses[var_name] = self.current_address
            self.current_address += size
        self.debug(f'Setup var {var_name} ({var_type}) at addr {self.variable_addresses[var_name]}')
        if self.current_address >= len(self.data_segment):
            self.error('Oops - ran out of memory!')

    def execute_instructions(self):
        # run through all instructions one by one
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
        result = self.variables[dest] + self.get_value(src)
        self.variables[dest] = self.validate_byte_value(result, 'add')
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
        value = self.get_value(src)
        if value < -128 or value > 127:
            self.error(f'Value {value} out of range for byte')
        self.stack_segment[self.stack_pointer] = value
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
            index = int(index[:-1])
            if index < 0 or index >= len(self.variables[var_name]):
                self.error(f'Array index {index} out of bounds for {var_name}')
            return self.variables[var_name][index]
        elif operand in self.variables:
            return self.variables[operand]
        else:
            self.error(f'Unknown operand {operand}')

    def update_flags(self, result):
        self.flags['ZF'] = 1 if result == 0 else 0
        self.flags['SF'] = 1 if result < 0 else 0
        self.flags['OF'] = 1 if result < -127 or result > 128 else 0

    def error(self, message):
        raise RuntimeError(f'Error at instruction {self.CO}: {message}')

    def validate_byte_value(self, value, operation):
        if value < -128 or value > 127:
            self.error(f'Result of {operation} ({value}) out of range for byte')
        return value

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