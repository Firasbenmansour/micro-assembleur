import unittest
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from codegen import CCodeGenerator

class TestCompiler(unittest.TestCase):
    def test_simple_program(self):
        source = """
        Var x: byte, y: Array[10];
        mov x, 5;
        add x, y[0];
        print(x);
        halt;
        """
        
        # Test lexer
        lexer = Lexer(source)
        self.assertTrue(len(lexer.tokens) > 0)
        
        # Test parser
        parser = Parser(lexer.tokens)
        ast = parser.parse()
        self.assertTrue(len(ast) > 0)
        
        # Test semantic analyzer
        analyzer = SemanticAnalyzer(ast)
        success, errors = analyzer.analyze()
        self.assertTrue(success, f"Semantic errors: {errors}")
        
        # Test code generator
        generator = CCodeGenerator(ast)
        c_code = generator.generate()
        self.assertIn('int main', c_code)

if __name__ == '__main__':
    unittest.main() 