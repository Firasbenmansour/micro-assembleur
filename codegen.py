import os
import sys

# Print current directory and files
print("Current directory:", os.getcwd())
print("Files in directory:", os.listdir())

try:
    from lexer import Lexer, Token
    from parser import Parser
except ImportError as e:
    print("Import error:", e)
    sys.exit(1)

class CCodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.variables = {}  # Track variable types
        self.indent_level = 0
        self.output = []
        self.labels = set()  # Track used labels
        self.current_instruction = 0  # Track instruction numbers for labels
        
    def indent(self):
        return "    " * self.indent_level
    
    def generate(self):
        # Add standard includes and main function header
        self.output = [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <stdint.h>",
            "",
            "// Flags",
            "int8_t ZF = 0, SF = 0, OF = 0;",
            "",
            "// Stack implementation",
            "#define STACK_SIZE 500",
            "int8_t stack[STACK_SIZE];",
            "int stack_pointer = 0;",
            "",
            "void push(int8_t value) {",
            "    if (stack_pointer >= STACK_SIZE) {",
            "        printf(\"Stack overflow\\n\");",
            "        exit(1);",
            "    }",
            "    stack[stack_pointer++] = value;",
            "}",
            "",
            "int8_t pop(void) {",
            "    if (stack_pointer <= 0) {",
            "        printf(\"Stack underflow\\n\");",
            "        exit(1);",
            "    }",
            "    return stack[--stack_pointer];",
            "}",
            "",
            "void update_flags(int value) {",
            "    ZF = (value == 0);",
            "    SF = (value < 0);",
            "    OF = (value < -127 || value > 128);",
            "}",
            "",
            "int main(void) {",
        ]
        self.indent_level = 1
        
        # Process declarations
        self.process_declarations()
        self.output.append("")
        
        # Process instructions
        self.process_instructions()
        
        # Add return statement and closing brace
        self.output.extend([
            "",
            "    return 0;",
            "}",
        ])
        
        return "\n".join(self.output)
    
    def process_declarations(self):
        for node in self.ast:
            if node['type'] == 'declaration':
                self.declare_variable(node)
    
    def declare_variable(self, node):
        var_name = node['name']
        var_type = node['var_type']
        
        if var_type == 'byte':
            self.variables[var_name] = 'byte'
            self.output.append(f"{self.indent()}int8_t {var_name} = 0;")
        elif var_type.startswith('Array'):
            size = int(var_type.split('[')[1].split(']')[0])
            self.variables[var_name] = ('array', size)
            self.output.append(f"{self.indent()}int8_t {var_name}[{size}] = {{0}};")
    
    def process_instructions(self):
        # First pass - collect all jump labels
        for node in self.ast:
            if node['type'] == 'instruction':
                if node['command'] in ['jmp', 'jz', 'js', 'jo']:
                    self.labels.add(int(node['operands'][0]))
        
        # Second pass - generate code with labels
        for node in self.ast:
            if node['type'] == 'instruction':
                if self.current_instruction in self.labels:
                    self.output.append(f"label_{self.current_instruction}:")
                self.generate_instruction(node)
                self.current_instruction += 1
    
    def generate_instruction(self, node):
        command = node['command']
        operands = node['operands']
        
        if command == 'mov':
            self.output.append(f"{self.indent()}{operands[0]} = {operands[1]};")
            
        elif command in ['add', 'sub', 'mult', 'div']:
            ops = {
                'add': '+',
                'sub': '-',
                'mult': '*',
                'div': '/'
            }
            op = ops[command]
            self.output.extend([
                f"{self.indent()}{operands[0]} {op}= {operands[1]};",
                f"{self.indent()}update_flags({operands[0]});"
            ])
            
        elif command in ['and', 'or']:
            op = '&' if command == 'and' else '|'
            self.output.extend([
                f"{self.indent()}{operands[0]} {op}= {operands[1]};",
                f"{self.indent()}update_flags({operands[0]});"
            ])
            
        elif command == 'not':
            self.output.extend([
                f"{self.indent()}{operands[0]} = ~{operands[0]};",
                f"{self.indent()}update_flags({operands[0]});"
            ])
            
        elif command == 'print':
            self.output.append(f"{self.indent()}printf(\"%d\\n\", {operands[0]});")
            
        elif command == 'input':
            self.output.append(
                f"{self.indent()}printf(\"Input value for {operands[0]}: \");"
                f"\n{self.indent()}scanf(\"%hhd\", &{operands[0]});"
            )
            
        elif command == 'push':
            self.output.append(f"{self.indent()}push({operands[0]});")
            
        elif command == 'pop':
            self.output.append(f"{self.indent()}{operands[0]} = pop();")
            
        elif command == 'isFull':
            self.output.append(
                f"{self.indent()}printf(\"%d\\n\", stack_pointer >= STACK_SIZE);"
            )
            
        elif command == 'halt':
            self.output.append(f"{self.indent()}exit(0);")
            
        elif command in ['jmp', 'jz', 'js', 'jo']:
            label = f"label_{operands[0]}"
            condition = {
                'jmp': '',
                'jz': 'if (ZF)',
                'js': 'if (SF)',
                'jo': 'if (OF)'
            }[command]
            if condition:
                self.output.append(f"{self.indent()}{condition} goto {label};")
            else:
                self.output.append(f"{self.indent()}goto {label};")

def generate_c_code(ast):
    generator = CCodeGenerator(ast)
    return generator.generate()

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
    parser = Parser(lexer.tokens)
    ast = parser.parse()
    c_code = generate_c_code(ast)
    print(c_code) 