from typing import List, Optional
from ..scanner import Token, Tokens
from ..util import SyntaxParsingError
from .ast import Node


class Parser:

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.index = 0
        self.length = len(tokens)
        self.ast = None

    def peek(self) -> Optional[Token]:

        if self.index < self.length:
            return self.tokens[self.index]
        else:
            return None

    def advance(self) -> Optional[Token]:
        
        if self.index < self.length:
            token = self.tokens[self.index]
            self.index += 1
            return token
        else:
            return None

    def parse(self):
        
        self.parse_program()

    def expect(self, expected: Tokens) -> Token:

        token = self.advance()
        if token.type == expected:
            return token
        else:
            raise SyntaxParsingError(expected, token)

    def parse_program(self):
        

        expected = [Tokens.FLOATDCL, Tokens.INTDCL, Tokens.ID, Tokens.PRINT,
                    Tokens.END]
        if self.peek().type in expected:
            self.parse_declarations()
            self.parse_statements()
            self.expect(Tokens.END)
        else:
            raise SyntaxParsingError(expected, self.peek())

    def parse_declarations(self):
        
        expected_declarations = [Tokens.FLOATDCL, Tokens.INTDCL]
        expected_lambdas = [Tokens.ID, Tokens.PRINT, Tokens.END]
        union_expected = expected_declarations + expected_lambdas

        if self.peek().type not in union_expected:
            raise SyntaxParsingError(union_expected, self.peek())

        if self.peek().type in expected_declarations:
            self.parse_declaration()
            self.parse_declarations()
        elif self.peek().type in expected_lambdas:
            pass

    def parse_declaration(self):
        
        if self.peek().type == Tokens.FLOATDCL:
            declaration = self.expect(Tokens.FLOATDCL)
            id_ = self.expect(Tokens.ID)
        elif self.peek().type == Tokens.INTDCL:
            declaration = self.expect(Tokens.INTDCL)
            id_ = self.expect(Tokens.ID)
        else:
            raise SyntaxParsingError([Tokens.FLOATDCL, Tokens.INTDCL],
                                     self.peek())
        self.ast.root.add_child(declaration.type, id_)

    def parse_statements(self):
        
        if self.peek().type in [Tokens.ID, Tokens.PRINT]:
            self.parse_statement()
            self.parse_statements()
        elif self.peek().type == Tokens.END:
            pass
        else:
            raise SyntaxParsingError([Tokens.ID, Tokens.PRINT, Tokens.END],
                                     self.peek())

    def parse_statement(self) -> Optional[Node]:
        
        if self.peek().type == Tokens.ID:
            id_ = self.expect(Tokens.ID)
            assign = self.expect(Tokens.ASSIGN)
            value = self.parse_value()
            statement = self.ast.root.add_child(assign.type)
            statement.add_child(id_.type, id_.value)

            expression = self.parse_expression(statement, value)
            if expression:
                pass 
            else:
                statement.add_child(value.type, value.value)
            return statement
        elif self.peek().type == Tokens.PRINT:
            print_ = self.expect(Tokens.PRINT)
            id_ = self.expect(Tokens.ID)
            return self.ast.root.add_child(print_.type, id_.value)
        else:
            raise SyntaxParsingError

    def parse_value(self):

        if self.peek().type == Tokens.ID:
            value = self.expect(Tokens.ID)
        elif self.peek().type == Tokens.INUM:
            value = self.expect(Tokens.INUM)
        elif self.peek().type == Tokens.FNUM:
            value = self.expect(Tokens.FNUM)
        else:
            raise SyntaxParsingError([Tokens.ID, Tokens.FNUM, Tokens.INUM],
                                     self.peek())
        return value

    def parse_expression(self, node: Optional[Node] = None,
                         value: Optional[Token] = None):

        if self.peek().type == Tokens.PLUS:
            token = self.expect(Tokens.PLUS).type
        elif self.peek().type == Tokens.MINUS:
            token = self.expect(Tokens.MINUS).type
        elif self.peek().type in [Tokens.ID, Tokens.PRINT, Tokens.END]:
            return
        else:
            raise SyntaxParsingError([Tokens.PLUS, Tokens.MINUS, Tokens.ID,
                                      Tokens.PRINT, Tokens.END],
                                     self.peek())
        operation = self.ast.root.add_child(token) if not node \
            else node.add_child(token)
        operation.add_child(value.type, value.value)
        value = self.parse_value()
        node = operation.add_child(value.type, value.value)
        self.parse_expression(node)
        return operation
