"""
LEXER (Tokenizer)
-----------------
The lexer breaks input text into tokens (smallest meaningful units).
It recognizes: keywords, identifiers, numbers, letters, and operators.

Example: "if score >= 90 then grade is A"
Tokens:  [IF, IDENTIFIER(score), GTE, NUMBER(90), THEN, IDENTIFIER(grade), IS, LETTER(A)]
"""

from __future__ import annotations  # For Python 3.9 compatibility

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List


class TokenType(Enum):
    """All possible token types in our grammar."""
    # Keywords
    IF = auto()
    THEN = auto()
    ELSE = auto()
    IS = auto()
    
    # Operators
    GTE = auto()  # >=
    
    # Literals
    IDENTIFIER = auto()  # e.g., score, grade
    NUMBER = auto()      # e.g., 90, 80
    LETTER = auto()      # e.g., A, B, F
    
    # Special
    EOF = auto()  # End of file


@dataclass
class Token:
    """A token has a type and optionally a value."""
    type: TokenType
    value: str = ""
    
    def __repr__(self):
        if self.value:
            return f"{self.type.name}({self.value})"
        return self.type.name


class Lexer:
    """
    Converts source code string into a list of tokens.
    This is the first phase of compilation.
    """
    
    # Keywords mapping
    KEYWORDS = {
        "if": TokenType.IF,
        "then": TokenType.THEN,
        "else": TokenType.ELSE,
        "is": TokenType.IS,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0  # Current position in source
        self.tokens: List[Token] = []
    
    def current_char(self) -> Optional[str]:
        """Return current character or None if at end."""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def advance(self):
        """Move to next character."""
        self.pos += 1
    
    def skip_whitespace(self):
        """Skip spaces, tabs, newlines."""
        while self.current_char() and self.current_char().isspace():
            self.advance()
    
    def read_word(self) -> str:
        """Read a word (letters only)."""
        result = ""
        while self.current_char() and self.current_char().isalpha():
            result += self.current_char()
            self.advance()
        return result
    
    def read_number(self) -> str:
        """Read a number (digits only)."""
        result = ""
        while self.current_char() and self.current_char().isdigit():
            result += self.current_char()
            self.advance()
        return result
    
    def tokenize(self) -> List[Token]:
        """
        Main method: scan source and produce tokens.
        Returns list of tokens ending with EOF.
        """
        while self.current_char() is not None:
            self.skip_whitespace()
            
            if self.current_char() is None:
                break
            
            char = self.current_char()
            
            # Check for >= operator
            if char == ">" and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == "=":
                self.tokens.append(Token(TokenType.GTE, ">="))
                self.advance()
                self.advance()
            
            # Check for word (keyword, identifier, or single letter)
            elif char.isalpha():
                word = self.read_word()
                
                # Is it a keyword?
                if word.lower() in self.KEYWORDS:
                    self.tokens.append(Token(self.KEYWORDS[word.lower()], word))
                # Is it a single uppercase letter? (LETTER terminal)
                elif len(word) == 1 and word.isupper():
                    self.tokens.append(Token(TokenType.LETTER, word))
                # Otherwise it's an identifier
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, word))
            
            # Check for number
            elif char.isdigit():
                number = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, number))
            
            else:
                raise SyntaxError(f"Unexpected character: '{char}' at position {self.pos}")
        
        # Add end-of-file token
        self.tokens.append(Token(TokenType.EOF))
        return self.tokens


# Quick test
if __name__ == "__main__":
    source = "if score >= 90 then grade is A else grade is B"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    print("Tokens:", tokens)
