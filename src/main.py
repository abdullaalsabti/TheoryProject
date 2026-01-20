from lexer import Lexer
from table_parser import build_parsing_table, print_parsing_table


def compile_with_validation(source: str) -> bool:
    print("\n" + "=" * 80)
    print("COMPILER - Theory of Computation")
    print("=" * 80)
    print(f"\nInput: {source}")
    
    print("\n" + "=" * 80)
    print("STEP 1: LL(1) PARSING TABLE")
    print("=" * 80)
    table = build_parsing_table()
    print_parsing_table(table)
    
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
    except SyntaxError as e:
        print(f"\n✗ LEXICAL ERROR: {e}")
        print("\n" + "=" * 80)
        print("COMPILATION FAILED - Invalid token in input")
        print("=" * 80)
        return False
    
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
    
    print("\n" + "=" * 80)
    print("✓ COMPILATION SUCCESSFUL!")
    print("=" * 80)
    print("\nThe input is valid and conforms to the grammar.")
    
    return True


def interactive_mode():
    print("\n" + "=" * 80)
    print("INTERACTIVE COMPILER")
    print("Theory of Computation - Grammar-Based Compiler")
    print("=" * 80)
    
    print("""
Minimal Grammar:
  S → if C then R
  C → IDENTIFIER >= NUMBER | IDENTIFIER <= NUMBER
  R → pass | fail

Where: S=Statement, C=Condition, R=Result

Valid inputs (ONLY these patterns are accepted):
  • if score >= 90 then pass
  • if score <= 90 then fail

Restrictions:
  - Only identifier: score
  - Only number: 90
  - Only operators: >=, <=
  - Only results: pass, fail

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
            source = "if score >= 90 then pass"
            print(f"Running example: {source}")
        
        if source.lower() == 'grammar':
            from grammar_analysis import analyze_grammar
            analyze_grammar()
            continue
        
        compile_with_validation(source)


def main():
    import sys
    
    if len(sys.argv) > 1:
        source = " ".join(sys.argv[1:])
        compile_with_validation(source)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
