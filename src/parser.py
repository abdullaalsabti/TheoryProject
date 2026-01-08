"""
PARSER (Syntax Analyzer)
------------------------
The parser checks if tokens follow the grammar rules and builds an AST.
AST = Abstract Syntax Tree, a tree representation of the program structure.

GRAMMAR RULES (Fixed - else can only follow if):
  <Program>       → <StatementList>
  <StatementList> → <Statement> <StatementList'>
  <StatementList'>→ <Statement> <StatementList'> | ε
  <Statement>     → <IfStatement> <OptionalElse>
  <IfStatement>   → if <Condition> then <Assignment>
  <OptionalElse>  → else <Assignment> | ε
  <Condition>     → IDENTIFIER >= NUMBER
  <Assignment>    → IDENTIFIER is <Value>
  <Value>         → LETTER
"""

from __future__ import annotations  # For Python 3.9 compatibility

from dataclasses import dataclass
from typing import Optional, List
from lexer import Lexer, Token, TokenType


# ============================================================
# AST NODE CLASSES
# Each class represents a node in the Abstract Syntax Tree
# ============================================================

@dataclass
class ValueNode:
    """Represents a LETTER value (e.g., A, B, F)."""
    letter: str


@dataclass
class ConditionNode:
    """Represents: IDENTIFIER >= NUMBER."""
    identifier: str
    number: int


@dataclass
class AssignmentNode:
    """Represents: IDENTIFIER is VALUE."""
    identifier: str
    value: ValueNode


@dataclass
class IfStatementNode:
    """Represents: if <Condition> then <Assignment> [else <Assignment>]."""
    condition: ConditionNode
    then_assignment: AssignmentNode
    else_assignment: Optional[AssignmentNode] = None  # Optional else part


@dataclass
class ProgramNode:
    """Root node containing all statements."""
    statements: list


# ============================================================
# PARSER CLASS
# Uses recursive descent parsing (one function per grammar rule)
# ============================================================

class Parser:
    """
    Recursive Descent Parser.
    Each grammar rule becomes a method that returns an AST node.
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0  # Current token position
    
    def current_token(self) -> Token:
        """Return current token."""
        return self.tokens[self.pos]
    
    def peek_token(self) -> Optional[Token]:
        """Look at next token without consuming."""
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None
    
    def consume(self, expected_type: TokenType) -> Token:
        """
        Consume current token if it matches expected type.
        Raises error if mismatch.
        """
        token = self.current_token()
        if token.type != expected_type:
            raise SyntaxError(
                f"Expected {expected_type.name}, got {token.type.name} at position {self.pos}"
            )
        self.pos += 1
        return token
    
    # --------------------------------------------------------
    # Grammar rule methods (one per production rule)
    # --------------------------------------------------------
    
    def parse(self) -> ProgramNode:
        """
        Entry point.
        <Program> → <StatementList>
        """
        statements = self.parse_statement_list()
        return ProgramNode(statements)
    
    def parse_statement_list(self) -> list:
        """
        <StatementList> → <Statement> <StatementList'>
        <StatementList'> → <Statement> <StatementList'> | ε
        
        Keep parsing statements until we hit EOF.
        """
        statements = []
        
        while self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            statements.append(stmt)
        
        return statements
    
    def parse_statement(self) -> IfStatementNode:
        """
        <Statement> → <IfStatement> <OptionalElse>
        
        A statement must start with 'if'. Else is optional after if.
        """
        token = self.current_token()
        
        if token.type == TokenType.IF:
            if_stmt = self.parse_if_statement()
            else_assignment = self.parse_optional_else()
            if_stmt.else_assignment = else_assignment
            return if_stmt
        else:
            raise SyntaxError(f"Expected 'if', got {token.type.name}. Statements must start with 'if'.")
    
    def parse_if_statement(self) -> IfStatementNode:
        """
        <IfStatement> → if <Condition> then <Assignment>
        """
        self.consume(TokenType.IF)           # Match 'if'
        condition = self.parse_condition()    # Parse condition
        self.consume(TokenType.THEN)          # Match 'then'
        assignment = self.parse_assignment()  # Parse assignment
        
        return IfStatementNode(condition, assignment)
    
    def parse_optional_else(self) -> Optional[AssignmentNode]:
        """
        <OptionalElse> → else <Assignment> | ε
        
        Returns the else assignment if present, None otherwise.
        """
        if self.current_token().type == TokenType.ELSE:
            self.consume(TokenType.ELSE)          # Match 'else'
            assignment = self.parse_assignment()  # Parse assignment
            return assignment
        
        # ε production - no else
        return None
    
    def parse_condition(self) -> ConditionNode:
        """
        <Condition> → IDENTIFIER >= NUMBER
        """
        id_token = self.consume(TokenType.IDENTIFIER)  # Match identifier
        self.consume(TokenType.GTE)                     # Match >=
        num_token = self.consume(TokenType.NUMBER)      # Match number
        
        return ConditionNode(id_token.value, int(num_token.value))
    
    def parse_assignment(self) -> AssignmentNode:
        """
        <Assignment> → IDENTIFIER is <Value>
        """
        id_token = self.consume(TokenType.IDENTIFIER)  # Match identifier
        self.consume(TokenType.IS)                      # Match 'is'
        value = self.parse_value()                      # Parse value
        
        return AssignmentNode(id_token.value, value)
    
    def parse_value(self) -> ValueNode:
        """
        <Value> → LETTER
        """
        letter_token = self.consume(TokenType.LETTER)  # Match letter
        return ValueNode(letter_token.value)


# Quick test
if __name__ == "__main__":
    source = "if score >= 90 then grade is A else grade is B"
    
    # Phase 1: Lexing
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    print("Tokens:", tokens)
    
    # Phase 2: Parsing
    parser = Parser(tokens)
    ast = parser.parse()
    print("\nAST:", ast)
