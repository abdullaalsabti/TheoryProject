"""
COMPILER - Interactive Mode
---------------------------
Enter your code and see:
1. The LL(1) parsing table
2. Step-by-step parsing
3. Generated code (if valid) or error messages (if invalid)

Run: python src/main.py
"""

from lexer import Lexer
from parser import Parser
from codegen import CodeGenerator
from table_parser import validate_and_parse, build_parsing_table, print_parsing_table


def compile_with_validation(source: str) -> bool:
    """
    Compile source code with full validation.
    Shows parsing table and validates before generating code.
    """
    print("\n" + "=" * 80)
    print("COMPILER - Theory of Computation")
    print("=" * 80)
    print(f"\nInput: {source}")
    
    # Step 1: Show parsing table
    print("\n" + "=" * 80)
    print("STEP 1: LL(1) PARSING TABLE")
    print("=" * 80)
    table = build_parsing_table()
    print_parsing_table(table)
    
    # Step 2: Lexical Analysis (silent - just tokenize)
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
    except SyntaxError as e:
        print(f"\n✗ LEXICAL ERROR: {e}")
        print("\n" + "=" * 80)
        print("COMPILATION FAILED - Invalid token in input")
        print("=" * 80)
        return False
    
    # Step 2: Syntax Analysis using table-driven parser
    print("\n" + "=" * 80)
    print("STEP 2: SYNTAX ANALYSIS (Table-Driven Parsing)")
    print("=" * 80)
    
    from table_parser import TableDrivenParser
    table_parser = TableDrivenParser(tokens, show_steps=True)
    is_valid = table_parser.parse()
    
    if not is_valid:
        print("\n" + "=" * 80)
        print("✗ COMPILATION FAILED - Syntax errors:")
        print("=" * 80)
        for error in table_parser.get_errors():
            print(f"  • {error}")
        print("\nThe input does not conform to the grammar.")
        print("Please check your syntax and try again.")
        return False
    
    # Step 3: Code Generation (only if syntax is valid)
    print("\n" + "=" * 80)
    print("STEP 3: CODE GENERATION")
    print("=" * 80)
    
    # Re-tokenize for the recursive descent parser
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    codegen = CodeGenerator()
    output = codegen.generate(ast)
    
    print("\n✓ COMPILATION SUCCESSFUL!")
    print("\nGenerated Python Code:")
    print("-" * 40)
    print(output)
    print("-" * 40)
    
    return True


def interactive_mode():
    """Run compiler in interactive mode."""
    print("\n" + "=" * 80)
    print("INTERACTIVE COMPILER")
    print("Theory of Computation - Grammar-Based Compiler")
    print("=" * 80)
    
    print("""
Grammar Rules (else can only follow if):
  <Program>       → <StatementList>
  <StatementList> → <Statement> <StatementList'>
  <StatementList'>→ <Statement> <StatementList'> | ε
  <Statement>     → <IfStatement> <OptionalElse>
  <IfStatement>   → if <Condition> then <Assignment>
  <OptionalElse>  → else <Assignment> | ε
  <Condition>     → IDENTIFIER >= NUMBER
  <Assignment>    → IDENTIFIER is <Value>
  <Value>         → LETTER

Example valid inputs:
  • if score >= 90 then grade is A
  • if score >= 90 then grade is A else grade is B
  • if x >= 50 then result is P else result is F

Type 'quit' or 'exit' to stop.
Type 'example' to see a demo.
Type 'grammar' to run grammar analysis.
""")
    
    while True:
        print("\n" + "-" * 80)
        try:
            source = input("Enter your code (or 'quit'): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not source:
            continue
        
        if source.lower() in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break
        
        if source.lower() == 'example':
            source = "if score >= 90 then grade is A else grade is B"
            print(f"Running example: {source}")
        
        if source.lower() == 'grammar':
            from grammar_analysis import analyze_grammar
            analyze_grammar()
            continue
        
        compile_with_validation(source)


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1:
        # Command line argument provided
        source = " ".join(sys.argv[1:])
        compile_with_validation(source)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
