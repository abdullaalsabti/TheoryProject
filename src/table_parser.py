from typing import Dict, List, Set, Tuple, Optional
from lexer import Lexer, Token, TokenType


EPSILON = "ε"

TOKEN_TO_TERMINAL = {
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

TERMINALS = {"if", "then", "pass", "fail", ">=", "<=", "IDENTIFIER", "NUMBER", "$", EPSILON}

GRAMMAR = {
    "S": [
        (1, ["if", "C", "then", "R"]),
    ],
    "C": [
        (2, ["IDENTIFIER", ">=", "NUMBER"]),
        (3, ["IDENTIFIER", "<=", "NUMBER"]),
    ],
    "R": [
        (4, ["pass"]),
        (5, ["fail"]),
    ],
}


def is_terminal(symbol: str) -> bool:
    return symbol in TERMINALS


def is_non_terminal(symbol: str) -> bool:
    return symbol in GRAMMAR


def compute_first_sets() -> Dict[str, Set[str]]:
    first: Dict[str, Set[str]] = {nt: set() for nt in GRAMMAR}
    
    for terminal in TERMINALS:
        first[terminal] = {terminal}
    
    changed = True
    while changed:
        changed = False
        
        for nt, productions in GRAMMAR.items():
            for rule_num, prod in productions:
                if prod == [EPSILON]:
                    if EPSILON not in first[nt]:
                        first[nt].add(EPSILON)
                        changed = True
                else:
                    all_have_epsilon = True
                    
                    for symbol in prod:
                        if is_terminal(symbol):
                            if symbol not in first[nt]:
                                first[nt].add(symbol)
                                changed = True
                            all_have_epsilon = False
                            break
                        else:
                            to_add = first.get(symbol, set()) - {EPSILON}
                            if not to_add.issubset(first[nt]):
                                first[nt].update(to_add)
                                changed = True
                            
                            if EPSILON not in first.get(symbol, set()):
                                all_have_epsilon = False
                                break
                    
                    if all_have_epsilon:
                        if EPSILON not in first[nt]:
                            first[nt].add(EPSILON)
                            changed = True
    
    return first


def compute_follow_sets(first: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    follow: Dict[str, Set[str]] = {nt: set() for nt in GRAMMAR}
    
    follow["S"].add("$")
    
    changed = True
    while changed:
        changed = False
        
        for nt, productions in GRAMMAR.items():
            for rule_num, prod in productions:
                if prod == [EPSILON]:
                    continue
                
                for i, symbol in enumerate(prod):
                    if is_non_terminal(symbol):
                        beta = prod[i + 1:]
                        
                        if beta:
                            first_beta = compute_first_of_string(beta, first)
                            to_add = first_beta - {EPSILON}
                            
                            if not to_add.issubset(follow[symbol]):
                                follow[symbol].update(to_add)
                                changed = True
                            
                            if EPSILON in first_beta:
                                if not follow[nt].issubset(follow[symbol]):
                                    follow[symbol].update(follow[nt])
                                    changed = True
                        else:
                            if not follow[nt].issubset(follow[symbol]):
                                follow[symbol].update(follow[nt])
                                changed = True
    
    return follow


def compute_first_of_string(symbols: List[str], first: Dict[str, Set[str]]) -> Set[str]:
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
        print(f"  FIRST({nt}) = {{ {', '.join(sorted(first_set))} }}")
        
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
        
        if nt == "S":
            print(f"      ← Rule 1: Start symbol, so $ ∈ FOLLOW(S)")
        
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


FIRST_SETS = compute_first_sets()
FOLLOW_SETS = compute_follow_sets(FIRST_SETS)


def build_parsing_table() -> Dict[Tuple[str, str], Tuple[int, List[str], str]]:
    table = {}
    
    for nt, productions in GRAMMAR.items():
        for rule_num, prod in productions:
            if prod == [EPSILON]:
                first_alpha = {EPSILON}
            else:
                first_alpha = compute_first_of_string(prod, FIRST_SETS)
            
            for terminal in first_alpha - {EPSILON}:
                table[(nt, terminal)] = (rule_num, prod, "FIRST")
            
            if EPSILON in first_alpha:
                for terminal in FOLLOW_SETS.get(nt, set()):
                    table[(nt, terminal)] = (rule_num, prod, "FOLLOW")
    
    return table


def print_parsing_table(table: Dict):
    print("\n" + "=" * 80)
    print("LL(1) PARSING TABLE")
    print("=" * 80)
    print("\nMinimal Grammar:")
    print("  S → if C then R")
    print("  C → IDENTIFIER >= NUMBER | IDENTIFIER <= NUMBER")
    print("  R → pass | fail")
    print()
    
    terminals = ["if", "then", "pass", "fail", ">=", "<=", "IDENTIFIER", "NUMBER", "$"]
    non_terminals = list(GRAMMAR.keys())
    
    col_width = 16
    header = f"{'NT':<4}|"
    for t in terminals:
        header += f" {t:^{col_width}}|"
    print(header)
    print("-" * len(header))
    
    for nt in non_terminals:
        row = f"{nt:<4}|"
        for t in terminals:
            entry = table.get((nt, t))
            if entry:
                rule_num, prod, reason = entry
                prod_str = " ".join(prod) if prod != [EPSILON] else EPSILON
                
                short_prod = prod_str.replace("IDENTIFIER", "ID")
                short_prod = short_prod.replace("NUMBER", "NUM")
                
                cell = f"{rule_num}:{short_prod}"
                if len(cell) > col_width:
                    cell = cell[:col_width-1] + "…"
                row += f" {cell:<{col_width}}|"
            else:
                row += f" {'—':<{col_width}}|"
        print(row)
    
    print("-" * len(header))
    
    print("\nProduction Rules:")
    for nt, productions in GRAMMAR.items():
        for rule_num, prod in productions:
            prod_str = " ".join(prod) if prod != [EPSILON] else EPSILON
            print(f"  {rule_num}. {nt} → {prod_str}")


class TableDrivenParser:
    def __init__(self, tokens: List[Token], show_steps: bool = True):
        self.tokens = tokens
        self.pos = 0
        self.show_steps = show_steps
        self.table = build_parsing_table()
        self.stack = ["$", "S"]
        self.errors = []
    
    def current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF)
    
    def token_to_terminal(self, token: Token) -> str:
        return TOKEN_TO_TERMINAL.get(token.type, str(token.type))
    
    def parse(self) -> bool:
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
            
            stack_str = " ".join(reversed(self.stack))
            remaining_tokens = [self.token_to_terminal(t) for t in self.tokens[self.pos:]]
            input_str = " ".join(remaining_tokens[:5])
            if len(remaining_tokens) > 5:
                input_str += "..."
            
            if top == "$":
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
                entry = self.table.get((top, terminal))
                
                if entry:
                    rule_num, production, relationship = entry
                    prod_str = " ".join(production) if production != [EPSILON] else EPSILON
                    action = f"Apply {rule_num}: {top}→{prod_str}"
                    
                    if self.show_steps:
                        print(f"{step:<6}{stack_str:<40}{input_str:<20}{action:<30}")
                    
                    self.stack.pop()
                    if production != [EPSILON]:
                        for symbol in reversed(production):
                            self.stack.append(symbol)
                else:
                    expected = [t for (nt, t) in self.table.keys() if nt == top]
                    error_msg = f"Unexpected '{current.value}'"
                    if expected:
                        error_msg += f", expected one of: {', '.join(expected)}"
                    self.errors.append(error_msg)
                    if self.show_steps:
                        print(f"{step:<6}{stack_str:<40}{input_str:<20}{'✗ ERROR':<30}")
                    return False
            
            else:
                error_msg = f"Unknown symbol on stack: {top}"
                self.errors.append(error_msg)
                return False
        
        return False
    
    def get_errors(self) -> List[str]:
        return self.errors


def validate_and_parse(source: str, show_table: bool = True, show_steps: bool = True) -> bool:
    print("\n" + "=" * 80)
    print("INPUT VALIDATION")
    print("=" * 80)
    print(f"Source: {source}")
    
    if show_table:
        table = build_parsing_table()
        print_parsing_table(table)
    
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
    
    parser = TableDrivenParser(tokens, show_steps=show_steps)
    is_valid = parser.parse()
    
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


if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("TEST 1: VALID INPUT")
    print("#" * 80)
    validate_and_parse("if score >= 90 then pass")
    
    print("\n\n" + "#" * 80)
    print("TEST 2: INVALID INPUT (missing 'then')")
    print("#" * 80)
    validate_and_parse("if score >= 90 pass")
    
    print("\n\n" + "#" * 80)
    print("TEST 3: INVALID INPUT (invalid token)")
    print("#" * 80)
    validate_and_parse("if score >= 90 then succeed")
