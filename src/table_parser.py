"""
TABLE-DRIVEN LL(1) PARSER
-------------------------
This parser uses the LL(1) parsing table to validate input.
It shows each step of parsing and rejects invalid input with errors.

The parsing table is displayed during compilation.
"""

from typing import Dict, List, Set, Tuple, Optional
from lexer import Lexer, Token, TokenType


# ============================================================
# GRAMMAR DEFINITION
# ============================================================

EPSILON = "ε"

# Map token types to terminal symbols in grammar
TOKEN_TO_TERMINAL = {
    TokenType.IF: "if",
    TokenType.THEN: "then",
    TokenType.ELSE: "else",
    TokenType.IS: "is",
    TokenType.GTE: ">=",
    TokenType.IDENTIFIER: "IDENTIFIER",
    TokenType.NUMBER: "NUMBER",
    TokenType.LETTER: "LETTER",
    TokenType.EOF: "$",
}

# All terminals
TERMINALS = {"if", "then", "else", "is", ">=", "IDENTIFIER", "NUMBER", "LETTER", "$", EPSILON}

# Grammar productions (numbered for reference)
# Fixed: else can only follow an if statement
GRAMMAR = {
    "Program": [
        (1, ["StatementList"]),
    ],
    "StatementList": [
        (2, ["Statement", "StatementList'"]),
    ],
    "StatementList'": [
        (3, ["Statement", "StatementList'"]),
        (4, [EPSILON]),
    ],
    "Statement": [
        (5, ["IfStatement", "OptionalElse"]),  # if must be followed by optional else
    ],
    "IfStatement": [
        (6, ["if", "Condition", "then", "Assignment"]),
    ],
    "OptionalElse": [
        (7, ["else", "Assignment"]),  # else is optional after if
        (8, [EPSILON]),               # or nothing
    ],
    "Condition": [
        (9, ["IDENTIFIER", ">=", "NUMBER"]),
    ],
    "Assignment": [
        (10, ["IDENTIFIER", "is", "Value"]),
    ],
    "Value": [
        (11, ["LETTER"]),
    ],
}


def is_terminal(symbol: str) -> bool:
    return symbol in TERMINALS


def is_non_terminal(symbol: str) -> bool:
    return symbol in GRAMMAR


# ============================================================
# FIRST AND FOLLOW SETS - Computed from Production Rules
# ============================================================

def compute_first_sets() -> Dict[str, Set[str]]:
    """
    Compute FIRST sets for all non-terminals using the production rules.
    
    FIRST(X) = set of terminals that can begin strings derived from X
    
    Rules:
    1. If X is a terminal: FIRST(X) = {X}
    2. If X → ε is a production: add ε to FIRST(X)
    3. If X → Y₁Y₂...Yₖ is a production:
       - Add FIRST(Y₁) - {ε} to FIRST(X)
       - If ε ∈ FIRST(Y₁), add FIRST(Y₂) - {ε} to FIRST(X)
       - If ε ∈ FIRST(Y₁) and ε ∈ FIRST(Y₂), add FIRST(Y₃) - {ε}
       - Continue until we find Yᵢ where ε ∉ FIRST(Yᵢ)
       - If ε ∈ FIRST(Yᵢ) for all i, add ε to FIRST(X)
    """
    first: Dict[str, Set[str]] = {nt: set() for nt in GRAMMAR}
    
    # Also add FIRST for terminals (FIRST(a) = {a})
    for terminal in TERMINALS:
        first[terminal] = {terminal}
    
    # Iterate until no changes (fixed-point algorithm)
    changed = True
    while changed:
        changed = False
        
        for nt, productions in GRAMMAR.items():
            for rule_num, prod in productions:
                # Handle ε-production
                if prod == [EPSILON]:
                    if EPSILON not in first[nt]:
                        first[nt].add(EPSILON)
                        changed = True
                else:
                    # Process each symbol in production
                    all_have_epsilon = True
                    
                    for symbol in prod:
                        if is_terminal(symbol):
                            # Terminal: add it and stop
                            if symbol not in first[nt]:
                                first[nt].add(symbol)
                                changed = True
                            all_have_epsilon = False
                            break
                        else:
                            # Non-terminal: add FIRST(symbol) - {ε}
                            to_add = first.get(symbol, set()) - {EPSILON}
                            if not to_add.issubset(first[nt]):
                                first[nt].update(to_add)
                                changed = True
                            
                            # If symbol can't derive ε, stop
                            if EPSILON not in first.get(symbol, set()):
                                all_have_epsilon = False
                                break
                    
                    # If all symbols can derive ε, add ε
                    if all_have_epsilon:
                        if EPSILON not in first[nt]:
                            first[nt].add(EPSILON)
                            changed = True
    
    return first


def compute_follow_sets(first: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    """
    Compute FOLLOW sets for all non-terminals using the production rules.
    
    FOLLOW(A) = set of terminals that can appear immediately after A
    
    Rules:
    1. Add $ to FOLLOW(Start Symbol)
    2. If A → αBβ: add FIRST(β) - {ε} to FOLLOW(B)
    3. If A → αB or (A → αBβ and ε ∈ FIRST(β)):
       add FOLLOW(A) to FOLLOW(B)
    """
    follow: Dict[str, Set[str]] = {nt: set() for nt in GRAMMAR}
    
    # Rule 1: Add $ to FOLLOW(Start Symbol)
    follow["Program"].add("$")
    
    # Iterate until no changes (fixed-point algorithm)
    changed = True
    while changed:
        changed = False
        
        for nt, productions in GRAMMAR.items():
            for rule_num, prod in productions:
                if prod == [EPSILON]:
                    continue
                
                for i, symbol in enumerate(prod):
                    if is_non_terminal(symbol):
                        # Get β (everything after symbol)
                        beta = prod[i + 1:]
                        
                        if beta:
                            # Rule 2: Add FIRST(β) - {ε} to FOLLOW(symbol)
                            first_beta = compute_first_of_string(beta, first)
                            to_add = first_beta - {EPSILON}
                            
                            if not to_add.issubset(follow[symbol]):
                                follow[symbol].update(to_add)
                                changed = True
                            
                            # Rule 3: If ε ∈ FIRST(β), add FOLLOW(A) to FOLLOW(B)
                            if EPSILON in first_beta:
                                if not follow[nt].issubset(follow[symbol]):
                                    follow[symbol].update(follow[nt])
                                    changed = True
                        else:
                            # Rule 3: B is at end of production, add FOLLOW(A)
                            if not follow[nt].issubset(follow[symbol]):
                                follow[symbol].update(follow[nt])
                                changed = True
    
    return follow


def compute_first_of_string(symbols: List[str], first: Dict[str, Set[str]]) -> Set[str]:
    """Compute FIRST set for a string of symbols."""
    result = set()
    
    all_have_epsilon = True
    for symbol in symbols:
        if is_terminal(symbol):
            result.add(symbol)
            all_have_epsilon = False
            break
        else:
            result.update(first.get(symbol, set()) - {EPSILON})
            if EPSILON not in first.get(symbol, set()):
                all_have_epsilon = False
                break
    
    if all_have_epsilon:
        result.add(EPSILON)
    
    return result


def print_first_follow_sets(first: Dict[str, Set[str]], follow: Dict[str, Set[str]]):
    """Print FIRST and FOLLOW sets with derivation explanation."""
    print("\n" + "=" * 80)
    print("FIRST SETS (computed from production rules)")
    print("=" * 80)
    print("\nRules used:")
    print("  1. If X is terminal: FIRST(X) = {X}")
    print("  2. If X → ε: add ε to FIRST(X)")
    print("  3. If X → Y₁Y₂...Yₖ: add FIRST(Y₁)-{ε}, then FIRST(Y₂)-{ε} if ε∈FIRST(Y₁), etc.")
    print()
    
    for nt in GRAMMAR.keys():
        first_set = first.get(nt, set())
        # Show which production rules contribute to FIRST
        print(f"  FIRST({nt}) = {{ {', '.join(sorted(first_set))} }}")
        
        # Explain derivation
        for rule_num, prod in GRAMMAR[nt]:
            prod_str = " ".join(prod) if prod != [EPSILON] else EPSILON
            if prod == [EPSILON]:
                print(f"      ← Rule {rule_num}: {nt} → {prod_str} contributes: ε")
            elif is_terminal(prod[0]):
                print(f"      ← Rule {rule_num}: {nt} → {prod_str} contributes: {prod[0]} (direct)")
            else:
                contrib = first.get(prod[0], set()) - {EPSILON}
                print(f"      ← Rule {rule_num}: {nt} → {prod_str} contributes: {{{', '.join(sorted(contrib))}}} via FIRST({prod[0]})")
    
    print("\n" + "=" * 80)
    print("FOLLOW SETS (computed from production rules)")
    print("=" * 80)
    print("\nRules used:")
    print("  1. Add $ to FOLLOW(Start Symbol)")
    print("  2. If A → αBβ: add FIRST(β)-{ε} to FOLLOW(B)")
    print("  3. If A → αB or ε∈FIRST(β): add FOLLOW(A) to FOLLOW(B)")
    print()
    
    for nt in GRAMMAR.keys():
        follow_set = follow.get(nt, set())
        print(f"  FOLLOW({nt}) = {{ {', '.join(sorted(follow_set))} }}")
        
        # Explain where FOLLOW comes from
        if nt == "Program":
            print(f"      ← Rule 1: Start symbol, so $ ∈ FOLLOW(Program)")
        
        # Find productions where this non-terminal appears
        for other_nt, productions in GRAMMAR.items():
            for rule_num, prod in productions:
                if prod == [EPSILON]:
                    continue
                for i, symbol in enumerate(prod):
                    if symbol == nt:
                        beta = prod[i + 1:]
                        prod_str = " ".join(prod)
                        if beta:
                            first_beta = compute_first_of_string(beta, first)
                            contrib = first_beta - {EPSILON}
                            if contrib:
                                print(f"      ← Rule {rule_num}: {other_nt} → {prod_str}")
                                print(f"         FIRST({' '.join(beta)}) - {{ε}} = {{{', '.join(sorted(contrib))}}}")
                            if EPSILON in first_beta:
                                print(f"      ← Rule {rule_num}: {other_nt} → {prod_str}")
                                print(f"         ε ∈ FIRST({' '.join(beta)}), so add FOLLOW({other_nt})")
                        else:
                            print(f"      ← Rule {rule_num}: {other_nt} → {prod_str}")
                            print(f"         {nt} at end, so add FOLLOW({other_nt})")


# Compute FIRST and FOLLOW sets
FIRST_SETS = compute_first_sets()
FOLLOW_SETS = compute_follow_sets(FIRST_SETS)


# ============================================================
# LL(1) PARSING TABLE - Built from FIRST and FOLLOW sets
# ============================================================

def build_parsing_table() -> Dict[Tuple[str, str], Tuple[int, List[str], str]]:
    """
    Build the LL(1) parsing table using FIRST and FOLLOW sets.
    
    Algorithm:
    For each production A → α:
      1. For each terminal 'a' in FIRST(α):
         Add A → α to M[A, a]
      2. If ε ∈ FIRST(α):
         For each terminal 'b' in FOLLOW(A):
         Add A → α to M[A, b]
    
    Returns: dict mapping (NonTerminal, Terminal) -> (rule_number, production, reason)
    - reason: "FIRST" or "FOLLOW" indicating why entry was added
    """
    table = {}
    
    for nt, productions in GRAMMAR.items():
        for rule_num, prod in productions:
            # Compute FIRST(α) for this production
            if prod == [EPSILON]:
                first_alpha = {EPSILON}
            else:
                first_alpha = compute_first_of_string(prod, FIRST_SETS)
            
            # Rule 1: For each terminal 'a' in FIRST(α), add to M[A, a]
            for terminal in first_alpha - {EPSILON}:
                table[(nt, terminal)] = (rule_num, prod, "FIRST")
            
            # Rule 2: If ε ∈ FIRST(α), for each 'b' in FOLLOW(A), add to M[A, b]
            if EPSILON in first_alpha:
                for terminal in FOLLOW_SETS.get(nt, set()):
                    table[(nt, terminal)] = (rule_num, prod, "FOLLOW")
    
    return table


def print_parsing_table(table: Dict):
    """
    Display the parsing table showing production rules.
    """
    print("\n" + "=" * 120)
    print("LL(1) PARSING TABLE")
    print("=" * 120)
    print("\nTable Construction Rules:")
    print("  For each production A → α:")
    print("    1. For each terminal 'a' in FIRST(α): add A → α to M[A, a]")
    print("    2. If ε ∈ FIRST(α): for each 'b' in FOLLOW(A): add A → α to M[A, b]")
    print()
    
    # Get all terminals used (excluding epsilon)
    terminals = ["if", "then", "else", "is", ">=", "IDENTIFIER", "NUMBER", "LETTER", "$"]
    non_terminals = list(GRAMMAR.keys())
    
    # Print header
    col_width = 22
    header = f"{'Non-Terminal':<16}|"
    for t in terminals:
        header += f" {t:^{col_width}}|"
    print(header)
    print("-" * len(header))
    
    # Print each row
    for nt in non_terminals:
        row = f"{nt:<16}|"
        for t in terminals:
            entry = table.get((nt, t))
            if entry:
                rule_num, prod, reason = entry
                prod_str = " ".join(prod) if prod != [EPSILON] else EPSILON
                
                # Shorten non-terminal names for display
                short_prod = prod_str.replace("StatementList", "SL")
                short_prod = short_prod.replace("Statement", "St")
                short_prod = short_prod.replace("IfStatement", "IfSt")
                short_prod = short_prod.replace("OptionalElse", "OptEl")
                short_prod = short_prod.replace("Condition", "Cond")
                short_prod = short_prod.replace("Assignment", "Asgn")
                short_prod = short_prod.replace("IDENTIFIER", "ID")
                short_prod = short_prod.replace("NUMBER", "NUM")
                short_prod = short_prod.replace("LETTER", "LET")
                
                # Format: NT → prod
                cell = f"{nt}→{short_prod}"
                if len(cell) > col_width:
                    cell = cell[:col_width-1] + "…"
                row += f" {cell:<{col_width}}|"
            else:
                row += f" {'(empty)':<{col_width}}|"
        print(row)
    
    print("-" * len(header))
    
    # Print full production rules
    print("\n" + "=" * 80)
    print("PRODUCTION RULES")
    print("=" * 80)
    for nt, productions in GRAMMAR.items():
        for rule_num, prod in productions:
            prod_str = " ".join(prod) if prod != [EPSILON] else EPSILON
            print(f"  Rule {rule_num}: {nt} → {prod_str}")


# ============================================================
# TABLE-DRIVEN PARSER
# ============================================================

class TableDrivenParser:
    """
    LL(1) table-driven parser.
    Uses a stack and parsing table to validate input.
    Shows each parsing step.
    """
    
    def __init__(self, tokens: List[Token], show_steps: bool = True):
        self.tokens = tokens
        self.pos = 0
        self.show_steps = show_steps
        self.table = build_parsing_table()
        self.stack = ["$", "Program"]  # Start with $ and start symbol
        self.errors = []
    
    def current_token(self) -> Token:
        """Get current input token."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF)
    
    def token_to_terminal(self, token: Token) -> str:
        """Convert token to grammar terminal."""
        return TOKEN_TO_TERMINAL.get(token.type, str(token.type))
    
    def parse(self) -> bool:
        """
        Parse the input using table-driven method.
        Returns True if input is valid, False otherwise.
        """
        if self.show_steps:
            print("\n" + "=" * 80)
            print("PARSING STEPS")
            print("=" * 80)
            print(f"{'Step':<6}{'Stack':<40}{'Input':<20}{'Action':<30}")
            print("-" * 96)
        
        step = 0
        
        while self.stack:
            step += 1
            top = self.stack[-1]
            current = self.current_token()
            terminal = self.token_to_terminal(current)
            
            # Format stack and input for display
            stack_str = " ".join(reversed(self.stack))
            remaining_tokens = [self.token_to_terminal(t) for t in self.tokens[self.pos:]]
            input_str = " ".join(remaining_tokens[:5])
            if len(remaining_tokens) > 5:
                input_str += "..."
            
            if top == "$":
                # End of stack
                if terminal == "$":
                    if self.show_steps:
                        print(f"{step:<6}{stack_str:<40}{input_str:<20}{'✓ ACCEPT':<30}")
                    return True
                else:
                    error_msg = f"Unexpected token '{current.value}' at end"
                    self.errors.append(error_msg)
                    if self.show_steps:
                        print(f"{step:<6}{stack_str:<40}{input_str:<20}{'✗ ERROR: ' + error_msg:<30}")
                    return False
            
            elif is_terminal(top):
                # Terminal on stack - must match input
                if top == terminal:
                    action = f"Match '{top}'"
                    self.stack.pop()
                    self.pos += 1
                    if self.show_steps:
                        print(f"{step:<6}{stack_str:<40}{input_str:<20}{action:<30}")
                else:
                    error_msg = f"Expected '{top}', got '{current.value}'"
                    self.errors.append(error_msg)
                    if self.show_steps:
                        print(f"{step:<6}{stack_str:<40}{input_str:<20}{'✗ ERROR: ' + error_msg:<30}")
                    return False
            
            elif is_non_terminal(top):
                # Non-terminal - look up in parsing table
                entry = self.table.get((top, terminal))
                
                if entry:
                    rule_num, production, relationship = entry
                    prod_str = " ".join(production) if production != [EPSILON] else EPSILON
                    action = f"Apply {rule_num}: {top}→{prod_str}"
                    
                    if self.show_steps:
                        print(f"{step:<6}{stack_str:<40}{input_str:<20}{action:<30}")
                    
                    # Pop non-terminal and push production in reverse
                    self.stack.pop()
                    if production != [EPSILON]:
                        for symbol in reversed(production):
                            self.stack.append(symbol)
                else:
                    # No entry in table - syntax error
                    expected = [t for (nt, t) in self.table.keys() if nt == top]
                    error_msg = f"Unexpected '{current.value}'"
                    if expected:
                        error_msg += f", expected one of: {', '.join(expected)}"
                    self.errors.append(error_msg)
                    if self.show_steps:
                        print(f"{step:<6}{stack_str:<40}{input_str:<20}{'✗ ERROR':<30}")
                    return False
            
            else:
                # Unknown symbol
                error_msg = f"Unknown symbol on stack: {top}"
                self.errors.append(error_msg)
                return False
        
        return False
    
    def get_errors(self) -> List[str]:
        """Return list of parsing errors."""
        return self.errors


# ============================================================
# MAIN VALIDATION FUNCTION
# ============================================================

def validate_and_parse(source: str, show_table: bool = True, show_steps: bool = True) -> bool:
    """
    Validate source code against the grammar.
    Shows parsing table and steps.
    Returns True if valid, False otherwise.
    """
    print("\n" + "=" * 80)
    print("INPUT VALIDATION")
    print("=" * 80)
    print(f"Source: {source}")
    
    # Show parsing table
    if show_table:
        table = build_parsing_table()
        print_parsing_table(table)
    
    # Lexical analysis
    print("\n" + "=" * 80)
    print("LEXICAL ANALYSIS")
    print("=" * 80)
    
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        print("Tokens:", [str(t) for t in tokens])
    except SyntaxError as e:
        print(f"✗ LEXICAL ERROR: {e}")
        return False
    
    # Syntactic analysis using table-driven parser
    parser = TableDrivenParser(tokens, show_steps=show_steps)
    is_valid = parser.parse()
    
    # Result
    print("\n" + "=" * 80)
    print("RESULT")
    print("=" * 80)
    
    if is_valid:
        print("✓ INPUT ACCEPTED - The input conforms to the grammar!")
        return True
    else:
        print("✗ INPUT REJECTED - Syntax errors found:")
        for error in parser.get_errors():
            print(f"  • {error}")
        return False


# Quick test
if __name__ == "__main__":
    # Valid input
    print("\n" + "#" * 80)
    print("TEST 1: VALID INPUT")
    print("#" * 80)
    validate_and_parse("if score >= 90 then grade is A else grade is B")
    
    # Invalid input - missing 'then'
    print("\n\n" + "#" * 80)
    print("TEST 2: INVALID INPUT (missing 'then')")
    print("#" * 80)
    validate_and_parse("if score >= 90 grade is A")
    
    # Invalid input - wrong keyword
    print("\n\n" + "#" * 80)
    print("TEST 3: INVALID INPUT (invalid token)")
    print("#" * 80)
    validate_and_parse("if score >= 90 then grade = A")
