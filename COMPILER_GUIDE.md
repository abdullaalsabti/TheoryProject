# Compiler Output Explanation Guide

## Overview

This compiler processes your input through 5 phases based on Theory of Computation principles. Here's what each output section means:

---

## STEP 1: LL(1) PARSING TABLE

### What is it?

The parsing table is the "brain" of the compiler. It tells the parser which grammar rule to apply based on:

- **Current non-terminal** (what we're trying to parse)
- **Current input token** (what we're looking at)

### How to read it:

```
Non-Terminal      | if          | then        | else        | ...
------------------|-------------|-------------|-------------|----
Program           | 1:StatementL| —           | —           | ...
Statement         | 5:IfStatemen| —           | 6:ElseState | ...
```

- **Row**: Non-terminal symbol (like Program, Statement)
- **Column**: Terminal symbol (like if, then, else)
- **Cell**: Rule number and production to use
- **—**: Empty cell means syntax error if this combination occurs

### Example:

- Cell `(Statement, if)` = `5:IfStatement`
- Meaning: "When parsing Statement and seeing 'if', use rule 5: Statement → IfStatement"

### Why it matters:

This table proves your grammar is **LL(1)** (can be parsed left-to-right with 1 lookahead token).
If any cell has multiple entries, the grammar is ambiguous!

---

## STEP 2: LEXICAL ANALYSIS (Tokenization)

### What is it?

The **lexer** breaks your input text into meaningful chunks called **tokens**.

### Example:

Input: `if score >= 90 then grade is A`

Tokens:

```
1. IF(if)              ← Keyword
2. IDENTIFIER(score)   ← Variable name
3. GTE(>=)             ← Operator
4. NUMBER(90)          ← Numeric literal
5. THEN(then)          ← Keyword
6. IDENTIFIER(grade)   ← Variable name
7. IS(is)              ← Keyword
8. LETTER(A)           ← Single letter value
9. EOF                 ← End of input
```

### Token Types:

- **Keywords**: `if`, `then`, `else`, `is` (reserved words)
- **Operators**: `>=` (comparison)
- **IDENTIFIER**: Variable names like `score`, `grade`
- **NUMBER**: Numeric values like `90`, `80`
- **LETTER**: Single uppercase letters like `A`, `B`, `F`
- **EOF**: End of file marker

### Why it matters:

If you have an invalid character (like `@` or `#`), you'll get a **LEXICAL ERROR** here.
The lexer ensures every character is recognized.

---

## STEP 3: SYNTAX ANALYSIS (Table-Driven Parsing)

### What is it?

The **parser** checks if your tokens follow the grammar rules using the parsing table.
It uses a **stack** and processes tokens one by one.

### How to read the parsing steps:

```
Step  Stack                    Input               Action
------|------------------------|-------------------|------------------
1     $ Program                if score >= 90...  Apply 1: Program→StatementList
2     $ StatementList          if score >= 90...  Apply 2: StatementList→Statement...
3     $ StatementList' Statement if score >= 90... Apply 5: Statement→IfStatement
...
```

### Columns explained:

- **Step**: Sequential step number
- **Stack**: What the parser is currently working on (read right to left)
- **Input**: Remaining tokens to process
- **Action**: What the parser does:
  - `Apply X: A→B` = Use grammar rule X to expand A into B
  - `Match 'X'` = Current token matches expected terminal, consume it
  - `✓ ACCEPT` = Input is valid!
  - `✗ ERROR` = Syntax error found

### Example walkthrough:

1. Start with `Program` on stack
2. Look at input token `if`
3. Check table: `(Program, if)` → use rule 1
4. Replace `Program` with `StatementList`
5. Continue until stack is empty and input is consumed

### Why it matters:

This is where **SYNTAX ERRORS** are caught. If your code doesn't follow grammar rules,
you'll see exactly where and why it failed.

---

## STEP 4: BUILDING ABSTRACT SYNTAX TREE (AST)

### What is it?

The **AST** is a tree structure representing your program's meaning (not just syntax).

### Example:

Input: `if score >= 90 then grade is A`

AST:

```
ProgramNode(
  statements=[
    IfStatementNode(
      condition=ConditionNode(identifier='score', number=90),
      assignment=AssignmentNode(identifier='grade', value=ValueNode(letter='A'))
    )
  ]
)
```

### Node types:

- **ProgramNode**: Root of the tree (entire program)
- **IfStatementNode**: Represents an if-statement
- **ConditionNode**: Represents a condition (e.g., `score >= 90`)
- **AssignmentNode**: Represents an assignment (e.g., `grade is A`)
- **ValueNode**: Represents a value (e.g., `A`)

### Why it matters:

The AST removes unnecessary syntax details (like keywords) and keeps only the semantic meaning.
This makes code generation easier.

---

## STEP 5: CODE GENERATION

### What is it?

The **code generator** walks the AST and produces target code (Python in our case).

### Example:

Input: `if score >= 90 then grade is A else grade is B`

Generated Python:

```python
if score >= 90:
    grade = "A"
else:
    grade = "B"
```

### Translation:

- `if <Condition> then <Assignment>` → `if <condition>: <assignment>`
- `else <Assignment>` → `else: <assignment>`
- `IDENTIFIER is LETTER` → `identifier = "letter"`
- `IDENTIFIER >= NUMBER` → `identifier >= number`

### Why it matters:

This is the final output! If compilation succeeds, you get executable Python code.

---

## Error Messages Explained

### ✗ LEXICAL ERROR

**What**: Invalid character in input
**Example**: `if score @ 90` (@ is not recognized)
**Fix**: Use only valid characters (letters, numbers, keywords, >=)

### ✗ SYNTAX ERROR

**What**: Tokens don't follow grammar rules
**Examples**:

- `if score >= 90 grade is A` (missing `then`)
- `if score = 90 then grade is A` (should be `>=` not `=`)
  **Fix**: Check grammar rules and ensure proper keyword order

### ✗ Expected 'X', got 'Y'

**What**: Parser expected token X but found Y
**Example**: Expected 'then', got 'grade'
**Fix**: Add the missing keyword

---

## Success Message

### ✓ COMPILATION SUCCESSFUL!

Your input is valid and has been compiled to Python code!

---

## Quick Reference: Theory of Computation Concepts

### 1. Grammar

A set of rules defining valid syntax:

```
<Program> → <StatementList>
<Statement> → <IfStatement> | <ElseStatement>
```

### 2. Terminals vs Non-Terminals

- **Terminals**: Actual tokens in code (`if`, `then`, `>=`, `90`)
- **Non-Terminals**: Abstract categories (`<Statement>`, `<Condition>`)

### 3. Left Recursion

When a rule refers to itself on the left:

```
A → Aα  (BAD - causes infinite loop in recursive descent)
A → αA  (GOOD - right recursion is fine)
```

### 4. Left Factoring

Removing common prefixes to make grammar LL(1):

```
Before: A → αβ | αγ  (ambiguous)
After:  A → αA'
        A'→ β | γ    (unambiguous)
```

### 5. FIRST Set

Terminals that can start a non-terminal:

```
FIRST(IfStatement) = {if}
FIRST(Statement) = {if, else}
```

### 6. FOLLOW Set

Terminals that can come after a non-terminal:

```
FOLLOW(Condition) = {then}
FOLLOW(Assignment) = {if, else, $}
```

### 7. LL(1) Parser

- **L**: Scans input Left-to-right
- **L**: Produces Leftmost derivation
- **(1)**: Uses 1 lookahead token

---

## Common Questions

### Q: Why does the parsing table have empty cells?

**A**: Those combinations are invalid syntax. If the parser encounters them, it's a syntax error.

### Q: What's the difference between lexer and parser?

**A**:

- **Lexer**: Recognizes individual words (tokens)
- **Parser**: Checks if words form valid sentences (grammar)

### Q: Why do we need an AST?

**A**: The AST removes syntax noise and represents program meaning, making code generation easier.

### Q: What if I get "Expected X, got Y"?

**A**: You're missing a required keyword or have tokens in wrong order. Check the grammar rules.

### Q: Can I add new keywords?

**A**: Yes! You'd need to:

1. Add token type to lexer
2. Add terminal to grammar
3. Update FIRST/FOLLOW sets
4. Rebuild parsing table

---

## Running the Compiler

### Interactive mode:

```bash
python src/main.py
```

### Command line:

```bash
python src/main.py "if score >= 90 then grade is A"
```

### Run grammar analysis:

```bash
python src/grammar_analysis.py
```

### Test table-driven parser:

```bash
python src/table_parser.py
```

---

## Valid Input Examples

```
✓ if score >= 90 then grade is A
✓ if score >= 90 then grade is A else grade is B
✓ if x >= 50 then result is P else result is F
✓ if points >= 100 then status is A if bonus >= 10 then extra is Y
```

## Invalid Input Examples

```
✗ if score = 90 then grade is A        (use >= not =)
✗ if score >= 90 grade is A            (missing 'then')
✗ if score >= 90 then grade = A        (use 'is' not =)
✗ if score >= 90 then grade is ABC     (use single letter)
✗ score >= 90                          (must start with 'if')
```

---

**Created by**: Theory of Computation Compiler Project
**Grammar Type**: LL(1) Context-Free Grammar
**Target Language**: Python
