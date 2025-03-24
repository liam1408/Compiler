""" ParserCPQ Class - Defines the CPL Language Parser
    This class implements a parser for the CPL programming language using the SLY package
"""
import sys
from sly import Parser
from lexer_cpq import LexerCPQ
from ast_cpq import *


class ParserCPQ(Parser):
    tokens = LexerCPQ.tokens

    def __init__(self):
        pass

#Grammer for the programming language CPL#
    @_('declarations stmt_block')
    def program(self, p):
        return ProgramNode(p.declarations, p.stmt_block)

    @_('declarations declaration')
    def declarations(self, p):
        return DeclarationsNode(p.declarations, p.declaration)

    @_('epsilon')
    def declarations(self, p):
        return EpsilonNode()

    @_('idlist ":" type ";"')
    def declaration(self, p):
        return DeclarationNode(p.idlist, p.type, p.lineno)

    @_('INT', 'FLOAT')
    def type(self, p):
        return TypeNode(p[0], p.lineno)

    @_('idlist "," ID')
    def idlist(self, p):
        return IdListNode(p.idlist, IdNode(p.ID, p.lineno), p.lineno)

    @_('ID')
    def idlist(self, p):
        return IdNode(p.ID, p.lineno)

    @_('assignment_stmt', 'input_stmt', 'output_stmt', 'if_stmt', 'while_stmt', 'switch_stmt', 'break_stmt',
       'stmt_block')
    def stmt(self, p):
        return p[0]

    @_('ID "=" expression ";"')
    def assignment_stmt(self, p):
        return AssignmentNode(IdfactorNode(p.ID, p.lineno), p.expression, p.lineno)

    @_('INPUT "(" ID ")" ";"')
    def input_stmt(self, p):
        return InputNode(IdfactorNode(p.ID, p.lineno))

    @_('OUTPUT "(" expression ")" ";"')
    def output_stmt(self, p):
        return OutputNode(p.expression, p.lineno)

    @_('IF "(" boolexpr ")" stmt ELSE stmt')
    def if_stmt(self, p):
        return IfNode(p.boolexpr, p.stmt0, p.stmt1, p.lineno)

    @_('WHILE "(" boolexpr ")" stmt')
    def while_stmt(self, p):
        return WhileNode(p.boolexpr, p.stmt, p.lineno)

    @_('SWITCH "(" expression ")" "{" caselist default_clause "}"')
    def switch_stmt(self, p):
        return SwitchNode(p.expression, p.caselist, p.default_clause, p.lineno)

    @_('DEFAULT ":" stmtlist')
    def default_clause(self, p):
        return p.stmtlist

    @_('caselist CASE NUM ":" stmtlist')
    def caselist(self, p):
        return CaseListNode(p.caselist, p.NUM, p.stmtlist, p.lineno)

    @_('epsilon')
    def caselist(self, p):
        return EpsilonNode()

    @_('BREAK ";"')
    def break_stmt(self, p):
        return BreakNode(p.lineno)

    @_('"{" stmtlist "}"')
    def stmt_block(self, p):
        return p.stmtlist

    @_('stmtlist stmt')
    def stmtlist(self, p):
        return StatementListNode(p.stmtlist, p.stmt)

    @_('epsilon')
    def stmtlist(self, p):
        return EpsilonNode()

    @_('boolexpr OR boolterm')
    def boolexpr(self, p):
        return BooleanExprNode(p.OR, p.boolexpr, p.boolterm, p.lineno)

    @_('boolterm')
    def boolexpr(self, p):
        return p.boolterm

    @_('boolterm AND boolfactor')
    def boolterm(self, p):
        return BooleanExprNode(p.AND, p.boolterm, p.boolfactor, p.lineno)

    @_('boolfactor')
    def boolterm(self, p):
        return p.boolfactor

    @_('NOT "(" boolexpr ")"')
    def boolfactor(self, p):
        return NotNode(p.boolexpr, p.lineno)

    @_('expression RELOP expression')
    def boolfactor(self, p):
        return RelopNode(p.RELOP, p.expression0, p.expression1, p.lineno)

    @_('expression ADDOP term')
    def expression(self, p):
        return OperationNode(p.ADDOP, p.expression, p.term, p.lineno)

    @_('term')
    def expression(self, p):
        return p.term

    @_('term MULOP factor')
    def term(self, p):
        return OperationNode(p.MULOP, p.term, p.factor, p.lineno)

    @_('factor')
    def term(self, p):
        return p.factor

    @_('"(" expression ")"')
    def factor(self, p):
        return p.expression

    @_('CAST "(" expression ")"')
    def factor(self, p):
        return CastNode(p.CAST, p.expression, p.lineno)

    @_('ID')
    def factor(self, p):
        return IdfactorNode(p[0], p.lineno)

    @_('NUM')
    def factor(self, p):
        return NumfactorNode(p[0], p.lineno)

    @_('')
    def epsilon(self, p):
        return EpsilonNode()

    def error(self, p):
        print("Syntax error at line %s, token='%s'" % (p.lineno, p.type))
        Success.found_errors = 1
        errors = []
        while True:

            tok = next(self.tokens, None)
            if tok:
                errors.append(tok.type)
            if tok is None:
                break
            if tok or tok.type == ')' or tok.type == ';' or tok.type == '}':
                break
            self.errok()
        if tok:
            return tok