class CompilerError(Exception):
    def __init__(self, error_type, message, line_number=None, column=None):
        self.error_type = error_type
        self.message = message
        self.line_number = line_number
        self.column = column

    def __str__(self):
        location = ""
        if self.line_number is not None:
            location = f" at line {self.line_number}"
            if self.column is not None:
                location += f", column {self.column}"
        return f"{self.error_type} Error{location}: {self.message}" 