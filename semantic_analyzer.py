class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.variables = {}  # keeps track of declared vars
        self.errors = []     # collect any errors we find
        
    def analyze(self):
        self.check_declarations()
        self.check_instructions()
        return len(self.errors) == 0, self.errors
    
    def check_declarations(self):
        # look for duplicate variables and invalid types
        for node in self.ast:
            if node['type'] == 'declaration':
                var_name = node['name']
                if var_name in self.variables:
                    self.errors.append(f"Variable {var_name} already declared")
                self.variables[var_name] = node['var_type']
    
    def check_instructions(self):
        # make sure all instructions are valid
        for node in self.ast:
            if node['type'] == 'instruction':
                self.check_instruction(node)
    
    def check_instruction(self, node):
        command = node['command']
        operands = node['operands']
        
        # figure out what kind of instruction it is and check it
        if command in ['add', 'sub', 'mult', 'div', 'and', 'or']:
            self.check_arithmetic_operation(command, operands)
        elif command == 'mov':
            self.check_assignment(operands)
        elif command == 'not':
            self.check_unary_operation(operands)
        elif command in ['jmp', 'jz', 'js', 'jo']:
            self.check_jump(operands)
        elif command == 'print':
            self.check_print(operands)
        elif command == 'input':
            self.check_input(operands)
        elif command in ['push', 'pop']:
            self.check_stack_operation(command, operands)
    
    def check_arithmetic_operation(self, op, operands):
        if len(operands) != 2:
            self.errors.append(f"{op} requires exactly 2 operands")
            return
        
        dest, src = operands
        if dest not in self.variables:
            self.errors.append(f"Variable undefined {dest}")
        self.check_operand(src)
    
    def check_assignment(self, operands):
        if len(operands) != 2:
            self.errors.append("Assignment requires exactly 2 operands")
            return
        
        dest, src = operands
        # Handle array assignment
        if '[' in str(dest) and ']' in str(dest):
            var_name = str(dest).split('[')[0]
            if var_name not in self.variables:
                self.errors.append(f"Array undefined {var_name}")
            elif not self.variables[var_name].startswith('Array'):
                self.errors.append(f"{var_name} is not an array")
        elif dest not in self.variables:
            self.errors.append(f"Variable undefined {dest}")
        
        self.check_operand(src)
    
    def check_operand(self, operand):
        if isinstance(operand, int) or str(operand).isdigit():
            # Check if number is in valid range for byte
            value = int(operand)
            if value < -128 or value > 127:
                self.errors.append(f"Value {value} out of byte range")
        elif '[' in str(operand) and ']' in str(operand):
            # Check array access
            var_name = str(operand).split('[')[0]
            index = str(operand).split('[')[1].split(']')[0]
            if var_name not in self.variables:
                self.errors.append(f"Array undefined {var_name}")
            elif not self.variables[var_name].startswith('Array'):
                self.errors.append(f"{var_name} is not an array")
            try:
                idx = int(index)
                size = int(self.variables[var_name].split('[')[1].split(']')[0])
                if idx < 0 or idx >= size:
                    self.errors.append(f"Array index {idx} out of bounds for {var_name}")
            except ValueError:
                self.errors.append(f"Invalid array index {index}")
        elif operand not in self.variables:
            self.errors.append(f"Variable undefined {operand}") 
    
    def check_unary_operation(self, operands):
        if len(operands) != 1:
            self.errors.append("Unary operation requires exactly 1 operand")
            return
        
        if operands[0] not in self.variables:
            self.errors.append(f"Variable undefined {operands[0]}")
    
    def check_jump(self, operands):
        if len(operands) != 1:
            self.errors.append("Jump requires exactly 1 operand")
            return
        
        try:
            label = int(operands[0])
            if label < 0:
                self.errors.append(f"Invalid jump label {label}")
        except ValueError:
            self.errors.append(f"Jump label must be a number, got {operands[0]}")
    
    def check_print(self, operands):
        if len(operands) != 1:
            self.errors.append("Print requires exactly 1 operand")
            return
        
        self.check_operand(operands[0])
    
    def check_input(self, operands):
        if len(operands) != 1:
            self.errors.append("Input requires exactly 1 operand")
            return
        
        if operands[0] not in self.variables:
            self.errors.append(f"Variable undefined {operands[0]}")
    
    def check_stack_operation(self, op, operands):
        if len(operands) != 1:
            self.errors.append(f"Stack operation {op} requires exactly 1 operand")
            return
        
        if op == 'pop':
            if operands[0] not in self.variables:
                self.errors.append(f"Variable undefined {operands[0]}")
        else:  # push
            self.check_operand(operands[0]) 