""" Lexer Class - Defines the CPL Language
    This class is implemented using the SLY package
    """
from sly import Lexer

class LexerCPQ(Lexer):
    tokens = {ID, NUM,INPUT, OUTPUT,IF, ELSE, SWITCH, CASE, DEFAULT,WHILE, BREAK,INT, FLOAT, CAST,RELOP, ADDOP, MULOP, OR, AND, NOT}
    literals = {'(', ')', '{', '}', ',', ':', ';', '='}
    ignore_comment = r'/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/'
    ignore = ' \t'

    @_(r'(\d*\.\d+)|(\d+\.\d*)',r'[0-9]+')
    def NUM(self, t):
        return t

    @_(r'cast<int>', r'cast<float>')
    def CAST(self, t):
        return t

    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'

    ID['break'] = BREAK
    ID['case'] = CASE
    ID['default'] = DEFAULT
    ID['else'] = ELSE
    ID['float'] = FLOAT
    ID['if'] = IF
    ID['input'] = INPUT
    ID['int'] = INT
    ID['output'] = OUTPUT
    ID['switch'] = SWITCH
    ID['while'] = WHILE


    @_(r'==', r'!=', r'>=', r'<=', r'<', r'>')
    def RELOP(self, t):
        return t

    @_(r'\+', r'\-')
    def ADDOP(self, t):
        return t

    @_(r'\*', r'\/')
    def MULOP(self, t):
        return t

    @_(r'[|]{2}')
    def OR(self, t):
        return t

    @_(r'&&')
    def AND(self, t):
        return t

    @_(r'!')
    def NOT(self, t):
        return t

    @_(r'\{')
    def lbrace(self, t):
        t.type = '{'
        return t

    @_(r'\}')
    def rbrace(self, t):
        t.type = '}'
        return t

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)


    def error(self, t):
        print("Lexical error at line %s, symbol='%s'" % (self.lineno, t.value[0]))
        self.index += 1

