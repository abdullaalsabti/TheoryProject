from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List


class TokenType(Enum):
    IF = auto()
    THEN = auto()
    PASS = auto()
    FAIL = auto()
    
    GTE = auto()
    LTE = auto()
    
    IDENTIFIER = auto()
    NUMBER = auto()
    
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str = ""
    
    def __repr__(self):
        if self.value:
            return f"{self.type.name}({self.value})"
        return self.type.name


class Lexer:
    KEYWORDS = {
        "if": TokenType.IF,
        "then": TokenType.THEN,
        "pass": TokenType.PASS,
        "fail": TokenType.FAIL,
    }
    
    ALLOWED_IDENTIFIERS = {"score"}
    
    ALLOWED_NUMBERS = {"90"}
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.tokens: List[Token] = []
    
    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def advance(self):
        self.pos += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char().isspace():
            self.advance()
    
    def read_word(self) -> str:
        result = ""
        while self.current_char() and self.current_char().isalpha():
            result += self.current_char()
            self.advance()
        return result
    
    def read_number(self) -> str:
        result = ""
        while self.current_char() and self.current_char().isdigit():
            result += self.current_char()
            self.advance()
        return result
    
    def tokenize(self) -> List[Token]:
        while self.current_char() is not None:
            self.skip_whitespace()
            
            if self.current_char() is None:
                break
            
            char = self.current_char()
            
            if char == ">" and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == "=":
                self.tokens.append(Token(TokenType.GTE, ">="))
                self.advance()
                self.advance()
            elif char == "<" and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == "=":
                self.tokens.append(Token(TokenType.LTE, "<="))
                self.advance()
                self.advance()
            
            elif char.isalpha():
                word = self.read_word()
                
                if word.lower() in self.KEYWORDS:
                    self.tokens.append(Token(self.KEYWORDS[word.lower()], word))
                else:
                    if word not in self.ALLOWED_IDENTIFIERS:
                        raise SyntaxError(f"Invalid identifier '{word}'. Only 'score' is allowed.")
                    self.tokens.append(Token(TokenType.IDENTIFIER, word))
            
            elif char.isdigit():
                number = self.read_number()
                if number not in self.ALLOWED_NUMBERS:
                    raise SyntaxError(f"Invalid number '{number}'. Only 50 and 90 are allowed.")
                self.tokens.append(Token(TokenType.NUMBER, number))
            
            else:
                raise SyntaxError(f"Unexpected character: '{char}' at position {self.pos}")
        
        self.tokens.append(Token(TokenType.EOF))
        return self.tokens


if __name__ == "__main__":
    source = "if score >= 90 then pass"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    print("Tokens:", tokens)
