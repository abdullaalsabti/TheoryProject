"""
GRAMMAR ANALYSIS
Shows FIRST and FOLLOW sets for the grammar
"""

from typing import Dict, Set


# Simple grammar
GRAMMAR = {
    "S": [["if", "C", "then", "R"]],
    "C": [["IDENTIFIER", ">=", "NUMBER"], ["IDENTIFIER", "<=", "NUMBER"]],
    "R": [["pass"], ["fail"]],
}


def compute_first_sets() -> Dict[str, Set[str]]:
    """
    FIRST(X) = What tokens can START when parsing X
    """
    return {
        "S": {"if"},
        "C": {"IDENTIFIER"},
        "R": {"pass", "fail"},
    }


def compute_follow_sets() -> Dict[str, Set[str]]:
    """
    FOLLOW(X) = What tokens can come AFTER X
    """
    return {
        "S": {"$"},
        "C": {"then"},
        "R": {"$"},
    }


def print_grammar():
    """Print the grammar rules"""
    print("\n" + "=" * 60)
    print("GRAMMAR RULES")
    print("=" * 60)
    
    print("\nProductions:")
    print("  S → if C then R")
    print("  C → IDENTIFIER >= NUMBER | IDENTIFIER <= NUMBER")
    print("  R → pass | fail")
    
    print("\nMeaning:")
    print("  S = Statement (complete if-then)")
    print("  C = Condition (score >= 90 or score <= 90)")
    print("  R = Result (pass or fail)")


def print_first_follow():
    """Print FIRST and FOLLOW sets"""
    print("\n" + "=" * 60)
    print("FIRST SETS")
    print("=" * 60)
    print("\nFIRST(X) = What tokens can START when parsing X")
    print()
    
    first = compute_first_sets()
    for nt, tokens in sorted(first.items()):
        print(f"  FIRST({nt}) = {{ {', '.join(sorted(tokens))} }}")
        if nt == "S":
            print(f"      → S always starts with 'if'")
        elif nt == "C":
            print(f"      → C always starts with IDENTIFIER")
        elif nt == "R":
            print(f"      → R can start with 'pass' OR 'fail'")
    
    print("\n" + "=" * 60)
    print("FOLLOW SETS")
    print("=" * 60)
    print("\nFOLLOW(X) = What tokens can come AFTER X")
    print()
    
    follow = compute_follow_sets()
    for nt, tokens in sorted(follow.items()):
        print(f"  FOLLOW({nt}) = {{ {', '.join(sorted(tokens))} }}")
        if nt == "S":
            print(f"      → After S comes end of input ($)")
        elif nt == "C":
            print(f"      → After C comes 'then'")
        elif nt == "R":
            print(f"      → After R comes end of input ($)")


def print_parsing_table():
    """Print the parsing table"""
    print("\n" + "=" * 60)
    print("LL(1) PARSING TABLE")
    print("=" * 60)
    print("\nHow to use: Table[Non-Terminal, Token] = Which rule to apply")
    print()
    
    print(f"{'NT':<4}| {'if':<15} {'then':<15} {'pass':<15} {'fail':<15} {'ID':<15}")
    print("-" * 80)
    print(f"{'S':<4}| {'S→if C then R':<15} {'—':<15} {'—':<15} {'—':<15} {'—':<15}")
    print(f"{'C':<4}| {'—':<15} {'—':<15} {'—':<15} {'—':<15} {'C→ID>=NUM':<15}")
    print(f"{'R':<4}| {'—':<15} {'—':<15} {'R→pass':<15} {'R→fail':<15} {'—':<15}")
    
    print("\nExplanation:")
    print("  • When parsing S and see 'if' → Use rule: S → if C then R")
    print("  • When parsing C and see 'IDENTIFIER' → Use rule: C → IDENTIFIER >= NUMBER")
    print("  • When parsing R and see 'pass' → Use rule: R → pass")
    print("  • When parsing R and see 'fail' → Use rule: R → fail")


def analyze_grammar():
    """Run complete grammar analysis"""
    print("\n" + "=" * 60)
    print("GRAMMAR ANALYSIS")
    print("=" * 60)
    
    print_grammar()
    print_first_follow()
    print_parsing_table()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
This grammar is LL(1) which means:
  • L = Scan input Left-to-right
  • L = Build Leftmost derivation
  • (1) = Use only 1 token lookahead

The grammar is simple and unambiguous!
""")


if __name__ == "__main__":
    analyze_grammar()
