"""
CODE GENERATOR
--------------
The code generator walks the AST and produces target code.
We'll generate Python code as output.

Example:
  Input:  "if score >= 90 then grade is A else grade is B"
  Output: Python if-else statement
"""

from parser import (
    ProgramNode,
    IfStatementNode,
    ConditionNode,
    AssignmentNode,
    ValueNode,
)


class CodeGenerator:
    """
    Traverses the AST and generates Python code.
    Uses the Visitor pattern - one method per node type.
    """
    
    def __init__(self):
        self.indent_level = 0  # Track indentation
    
    def indent(self) -> str:
        """Return current indentation as spaces."""
        return "    " * self.indent_level
    
    def generate(self, node) -> str:
        """
        Main entry point.
        Dispatches to appropriate method based on node type.
        """
        method_name = f"gen_{type(node).__name__}"
        method = getattr(self, method_name, None)
        
        if method is None:
            raise NotImplementedError(f"No generator for {type(node).__name__}")
        
        return method(node)
    
    # --------------------------------------------------------
    # Generator methods (one per AST node type)
    # --------------------------------------------------------
    
    def gen_ProgramNode(self, node: ProgramNode) -> str:
        """
        Generate code for entire program.
        Each statement is an if with optional else.
        """
        lines = []
        
        for stmt in node.statements:
            lines.append(self.generate(stmt))
        
        return "\n".join(lines)
    
    def gen_IfStatementNode(self, node: IfStatementNode) -> str:
        """
        Generate: if <condition>:
                      <assignment>
                  [else:
                      <assignment>]
        """
        condition = self.generate(node.condition)
        
        self.indent_level += 1
        then_assignment = self.indent() + self.generate(node.then_assignment)
        self.indent_level -= 1
        
        result = f"if {condition}:\n{then_assignment}"
        
        # Add else part if present
        if node.else_assignment is not None:
            self.indent_level += 1
            else_assignment = self.indent() + self.generate(node.else_assignment)
            self.indent_level -= 1
            result += f"\nelse:\n{else_assignment}"
        
        return result
    
    def gen_ConditionNode(self, node: ConditionNode) -> str:
        """
        Generate: identifier >= number
        """
        return f"{node.identifier} >= {node.number}"
    
    def gen_AssignmentNode(self, node: AssignmentNode) -> str:
        """
        Generate: identifier = "value"
        """
        value = self.generate(node.value)
        return f'{node.identifier} = "{value}"'
    
    def gen_ValueNode(self, node: ValueNode) -> str:
        """
        Generate: letter (as string)
        """
        return node.letter


# Quick test
if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    
    source = "if score >= 90 then grade is A else grade is B"
    
    # Phase 1: Lexing
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    # Phase 2: Parsing
    parser = Parser(tokens)
    ast = parser.parse()
    
    # Phase 3: Code Generation
    codegen = CodeGenerator()
    output = codegen.generate(ast)
    
    print("Generated Python code:")
    print("-" * 30)
    print(output)
