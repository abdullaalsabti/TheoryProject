from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List
from lexer import Lexer, Token, TokenType


@dataclass
class ResultNode:
    result: str


@dataclass
class ConditionNode:
    identifier: str
    operator: str
    number: int


@dataclass
class IfStatementNode:
    condition: ConditionNode
    result: ResultNode


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current_token(self) -> Token:
        return self.tokens[self.pos]
    
    def consume(self, expected_type: TokenType) -> Token:
        token = self.current_token()
        if token.type != expected_type:
            raise SyntaxError(
                f"Expected {expected_type.name}, got {token.type.name} at position {self.pos}"
            )
        self.pos += 1
        return token
    
    def parse(self) -> IfStatementNode:
        statement = self.parse_statement()
        if self.current_token().type != TokenType.EOF:
            raise SyntaxError(f"Unexpected token after statement: {self.current_token().type.name}")
        return statement
    
    def parse_statement(self) -> IfStatementNode:
        self.consume(TokenType.IF)
        condition = self.parse_condition()
        self.consume(TokenType.THEN)
        result = self.parse_result()
        
        return IfStatementNode(condition, result)
    
    def parse_condition(self) -> ConditionNode:
        id_token = self.consume(TokenType.IDENTIFIER)
        
        current = self.current_token()
        if current.type == TokenType.GTE:
            operator = ">="
            self.consume(TokenType.GTE)
        elif current.type == TokenType.LTE:
            operator = "<="
            self.consume(TokenType.LTE)
        else:
            raise SyntaxError(f"Expected >= or <=, got {current.type.name}")
        
        num_token = self.consume(TokenType.NUMBER)
        
        return ConditionNode(id_token.value, operator, int(num_token.value))
    
    def parse_result(self) -> ResultNode:
        current = self.current_token()
        if current.type == TokenType.PASS:
            self.consume(TokenType.PASS)
            return ResultNode("pass")
        elif current.type == TokenType.FAIL:
            self.consume(TokenType.FAIL)
            return ResultNode("fail")
        else:
            raise SyntaxError(f"Expected 'pass' or 'fail', got {current.type.name}")


if __name__ == "__main__":
    source = "if score >= 90 then pass"
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    print("Tokens:", tokens)
    
    parser = Parser(tokens)
    ast = parser.parse()
    print("\nAST:", ast)
