import argparse
import os
import subprocess
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from codegen import CCodeGenerator

def compile_and_run(c_file):
    # Compile the C file
    output_exe = c_file.replace('.c', '.exe')
    compile_result = subprocess.run(['gcc', c_file, '-o', output_exe], 
                                  capture_output=True, 
                                  text=True)
    
    if compile_result.returncode != 0:
        print("C compilation failed:")
        print(compile_result.stderr)
        return False
    
    # Run the executable
    try:
        run_result = subprocess.run([f'./{output_exe}'], 
                                  capture_output=True, 
                                  text=True)
        print("\nProgram output:")
        print(run_result.stdout)
        return True
    except Exception as e:
        print(f"Error running program: {e}")
        return False
    finally:
        # Clean up
        try:
            os.remove(output_exe)
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description='Simple compiler')
    parser.add_argument('input', help='Input source file')
    parser.add_argument('-o', '--output', help='Output C file', default='output.c')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--run', action='store_true', help='Compile and run the program')
    args = parser.parse_args()
    
    try:
        # Read input file
        with open(args.input, 'r') as f:
            source = f.read()
        
        # Lexical analysis
        lexer = Lexer(source)
        if args.debug:
            print("Tokens:", lexer.tokens)
        
        # Parsing
        parser = Parser(lexer.tokens)
        ast = parser.parse()
        if args.debug:
            print("AST:", ast)
        
        # Semantic analysis
        analyzer = SemanticAnalyzer(ast)
        success, errors = analyzer.analyze()
        if not success:
            print("Semantic errors:")
            for error in errors:
                print(f"  {error}")
            return 1
        
        # Code generation
        generator = CCodeGenerator(ast)
        c_code = generator.generate()
        
        # Write output
        with open(args.output, 'w') as f:
            f.write(c_code)
            
        print(f"Successfully compiled to {args.output}")
        
        # Compile and run if requested
        if args.run:
            print("\nCompiling and running the program...")
            if not compile_and_run(args.output):
                return 1
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    exit(main()) 