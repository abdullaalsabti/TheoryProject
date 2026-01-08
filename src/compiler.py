"""
COMPILER - Main Entry Point
----------------------------
A compiler has 3 main phases:
  1. LEXER:     Source code → Tokens
  2. PARSER:    Tokens → AST (Abstract Syntax Tree)
  3. CODEGEN:   AST → Target code

This file ties all phases together.
"""

from lexer import Lexer
from parser import Parser
from codegen import CodeGenerator


def compile_source(source: str) -> str:
    """
    Compile source code through all phases.
    
    Args:
        source: Input program in our custom language
        
    Returns:
        Generated Python code
    """
    print("=" * 50)
    print("COMPILATION PHASES")
    print("=" * 50)
    
    # --------------------------------------------------------
    # PHASE 1: LEXICAL ANALYSIS (Lexing)
    # Breaks source into tokens
    # --------------------------------------------------------
    print("\n[Phase 1] LEXER - Tokenizing...")
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    print(f"  Tokens: {tokens}")
    
    # --------------------------------------------------------
    # PHASE 2: SYNTAX ANALYSIS (Parsing)
    # Builds Abstract Syntax Tree from tokens
    # --------------------------------------------------------
    print("\n[Phase 2] PARSER - Building AST...")
    parser = Parser(tokens)
    ast = parser.parse()
    print(f"  AST: {ast}")
    
    # --------------------------------------------------------
    # PHASE 3: CODE GENERATION
    # Converts AST to target language (Python)
    # --------------------------------------------------------
    print("\n[Phase 3] CODEGEN - Generating Python...")
    codegen = CodeGenerator()
    output = codegen.generate(ast)
    
    return output


def main():
    """Run the compiler with example programs."""
    
    # Example 1: Simple if-else
    print("\n" + "=" * 50)
    print("EXAMPLE 1: Simple if-else")
    print("=" * 50)
    
    source1 = "if score >= 90 then grade is A else grade is B"
    print(f"\nSource: {source1}")
    
    output1 = compile_source(source1)
    print("\n" + "-" * 50)
    print("GENERATED CODE:")
    print("-" * 50)
    print(output1)
    
    # Example 2: Multiple conditions
    print("\n\n" + "=" * 50)
    print("EXAMPLE 2: Multiple conditions")
    print("=" * 50)
    
    source2 = """
    if score >= 90 then grade is A
    else grade is F
    if points >= 50 then result is P
    else result is F
    """
    print(f"\nSource: {source2.strip()}")
    
    output2 = compile_source(source2)
    print("\n" + "-" * 50)
    print("GENERATED CODE:")
    print("-" * 50)
    print(output2)


if __name__ == "__main__":
    main()
