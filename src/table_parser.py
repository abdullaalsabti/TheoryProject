"""
SIMPLE TABLE-DRIVEN PARSER
With FIRST and FOLLOW sets explained simply
"""

from typing import Dict, List, Set, Tuple
from lexer import Token, TokenType


# Grammar rules
GRAMMAR = {
    "S": [(1, ["if", "C", "then", "R"])],
    "C": [(2, ["IDENTIFIER", ">=", "NUMBER"]), (3, ["IDENTIFIER", "<=", "NUMBER"])],
    "R": [(4, ["pass"]), (5, ["fail"])],
}

# Token to terminal mapping
TOKEN_MAP = {
    TokenType.IF: "if",
    TokenType.THEN: "then",
    TokenType.PASS: "pass",
    TokenType.FAIL: "fail",
    TokenType.GTE: ">=",
    TokenType.LTE: "<=",
    TokenType.IDENTIFIER: "IDENTIFIER",
    TokenType.NUMBER: "NUMBER",
    TokenType.EOF: "$",
}


def compute_first_sets() -> Dict[str, Set[str]]:
    """
    FIRST(X) = What tokens can START when parsing X
    
    Simple rules:
    - FIRST(S) = {if} because S starts with "if"
    - FIRST(C) = {IDENTIFIER} because C starts with IDENTIFIER
    - FIRST(R) = {pass, fail} because R can be pass OR fail
    """
    return {
        "S": {"if"},
        "C": {"IDENTIFIER"},
        "R": {"pass", "fail"},
    }


def compute_follow_sets() -> Dict[str, Set[str]]:
    """
    FOLLOW(X) = What tokens can come AFTER X
    
    Simple rules:
    - FOLLOW(S) = {$} because S is the whole program, $ comes after
    - FOLLOW(C) = {then} because after C comes "then"
    - FOLLOW(R) = {$} because R is at the end
    """
    return {
        "S": {"$"},
        "C": {"then"},
        "R": {"$"},
    }


def build_parsing_table() -> Dict[Tuple[str, str], Tuple[int, List[str]]]:
    """
    Build parsing table using FIRST and FOLLOW
    
    Rule: For each production A → α
    - If token 't' is in FIRST(α), put the rule in table[A, t]
    
    Example:
    - S → if C then R, FIRST = {if}, so table[S, if] = this rule
    - R → pass, FIRST = {pass}, so table[R, pass] = this rule
    """
    table = {}
    
    # Rule 1: S → if C then R (starts with "if")
    table[("S", "if")] = (1, ["if", "C", "then", "R"])
    
    # Rule 2: C → IDENTIFIER >= NUMBER (starts with IDENTIFIER)
    table[("C", "IDENTIFIER")] = (2, ["IDENTIFIER", ">=", "NUMBER"])
    
    # Rule 3: C → IDENTIFIER <= NUMBER (also starts with IDENTIFIER)
    # We'll handle this specially in the parser
    
    # Rule 4: R → pass (starts with "pass")
    table[("R", "pass")] = (4, ["pass"])
    
    # Rule 5: R → fail (starts with "fail")
    table[("R", "fail")] = (5, ["fail"])
    
    return table


def print_parsing_table(table):
    """Print the parsing table nicely"""
    print("\nGrammar:")
    print("  S → if C then R")
    print("  C → IDENTIFIER >= NUMBER | IDENTIFIER <= NUMBER")
    print("  R → pass | fail")
    print()
    
    print("FIRST Sets (what can START each rule):")
    first = compute_first_sets()
    for nt, tokens in first.items():
        print(f"  FIRST({nt}) = {{{', '.join(tokens)}}}")
    print()
    
    print("FOLLOW Sets (what can come AFTER each rule):")
    follow = compute_follow_sets()
    for nt, tokens in follow.items():
        print(f"  FOLLOW({nt}) = {{{', '.join(tokens)}}}")
    print()
    
    print("Parsing Table:")
    print(f"{'NT':<4}| {'if':<15} {'then':<15} {'pass':<15} {'fail':<15} {'ID':<15}")
    print("-" * 80)
    print(f"{'S':<4}| {'1:if C then R':<15} {'—':<15} {'—':<15} {'—':<15} {'—':<15}")
    print(f"{'C':<4}| {'—':<15} {'—':<15} {'—':<15} {'—':<15} {'2:ID>=NUM':<15}")
    print(f"{'R':<4}| {'—':<15} {'—':<15} {'4:pass':<15} {'5:fail':<15} {'—':<15}")
    print()
    
    print("Production Rules:")
    for nt, productions in GRAMMAR.items():
        for rule_num, prod in productions:
            print(f"  {rule_num}. {nt} → {' '.join(prod)}")


class TableDrivenParser:
    """Simple parser using the parsing table"""
    
    def __init__(self, tokens: List[Token], show_steps: bool = True):
        self.tokens = tokens
        self.pos = 0
        self.show_steps = show_steps
        self.table = build_parsing_table()
        self.stack = ["$", "S"]  # Start with end marker and start symbol
        self.errors = []
    
    def current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF)
    
    def token_to_terminal(self, token: Token) -> str:
        return TOKEN_MAP.get(token.type, str(token.type))
    
    def parse(self) -> bool:
        """Parse using the table"""
        if self.show_steps:
            print(f"\n{'Step':<6}{'Stack':<30}{'Input':<25}{'Action':<30}")
            print("-" * 91)
        
        step = 0
        while self.stack:
            step += 1
            top = self.stack[-1]
            current = self.current_token()
            terminal = self.token_to_terminal(current)
            
            # Format for display
            stack_str = " ".join(reversed(self.stack))
            input_tokens = [self.token_to_terminal(t) for t in self.tokens[self.pos:]]
            input_str = " ".join(input_tokens[:4])
            if len(input_tokens) > 4:
                input_str += "..."
            
            # Case 1: End of stack
            if top == "$":
                if terminal == "$":
                    if self.show_steps:
                        print(f"{step:<6}{stack_str:<30}{input_str:<25}{'✓ ACCEPT':<30}")
                    return True
                else:
                    self.errors.append(f"Unexpected token '{current.value}'")
                    return False
            
            # Case 2: Terminal on stack - must match input
            elif top in ["if", "then", "pass", "fail", ">=", "<=", "IDENTIFIER", "NUMBER"]:
                if top == terminal:
                    if self.show_steps:
                        print(f"{step:<6}{stack_str:<30}{input_str:<25}{'Match ' + top:<30}")
                    self.stack.pop()
                    self.pos += 1
                else:
                    self.errors.append(f"Expected '{top}', got '{current.value}'")
                    return False
            
            # Case 3: Non-terminal on stack - look up in table
            elif top in ["S", "C", "R"]:
                # Special case: C can be >= or <=, check next token
                if top == "C" and terminal == "IDENTIFIER":
                    next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                    if next_token and next_token.type == TokenType.LTE:
                        rule_num, production = 3, ["IDENTIFIER", "<=", "NUMBER"]
                    else:
                        rule_num, production = 2, ["IDENTIFIER", ">=", "NUMBER"]
                    
                    if self.show_steps:
                        prod_str = " ".join(production)
                        print(f"{step:<6}{stack_str:<30}{input_str:<25}{f'Apply {rule_num}: {top}→{prod_str}':<30}")
                    
                    self.stack.pop()
                    for symbol in reversed(production):
                        self.stack.append(symbol)
                else:
                    # Look up in table
                    entry = self.table.get((top, terminal))
                    if entry:
                        rule_num, production = entry
                        if self.show_steps:
                            prod_str = " ".join(production)
                            print(f"{step:<6}{stack_str:<30}{input_str:<25}{f'Apply {rule_num}: {top}→{prod_str}':<30}")
                        
                        self.stack.pop()
                        for symbol in reversed(production):
                            self.stack.append(symbol)
                    else:
                        self.errors.append(f"Unexpected '{current.value}'")
                        return False
            else:
                self.errors.append(f"Unknown symbol: {top}")
                return False
        
        return False
    
    def get_errors(self) -> List[str]:
        return self.errors


if __name__ == "__main__":
    from lexer import Lexer
    
    print("=" * 80)
    print("TEST: if score >= 90 then pass")
    print("=" * 80)
    
    lexer = Lexer("if score >= 90 then pass")
    tokens = lexer.tokenize()
    
    table = build_parsing_table()
    print_parsing_table(table)
    
    parser = TableDrivenParser(tokens)
    result = parser.parse()
    
    print(f"\nResult: {'✓ VALID' if result else '✗ INVALID'}")
