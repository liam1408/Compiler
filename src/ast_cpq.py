""" this file responsible for making the ast nodes
    each node has a function "gen" that generates the code
    with the help of the interpreter class.
"""
from interpreter import Interpreter,Success

AST = Interpreter()

class ASTNode(object):

    def gen(self):
        pass

class ProgramNode(ASTNode):
    def __init__(self, declarations, stmt_block):
        self.declarations = declarations
        self.stmt_block = stmt_block

    def gen(self):
        self.declarations.gen()
        stmt_labels = self.stmt_block.gen()
        return AST.handle_Program(stmt_labels, AST.insert_halt())

class DeclarationsNode(ASTNode):
    def __init__(self, declarations, declaration):
        self.left = declarations
        self.right = declaration

    def gen(self):
        self.left.gen()
        self.right.gen()

class EpsilonNode(ASTNode):
    def gen(self):
        return AST.handle_epsilon()

class DeclarationNode(ASTNode):
    def __init__(self, id_list, type_node, lineno):
        self.id_list = id_list
        self.type_node = type_node
        self.lineno = lineno

    def gen(self):
        self.id_list.gen()
        self.type_node.gen()

class IdListNode(ASTNode):
    def __init__(self, left, right, lineno):
        self.left = left
        self.right = right
        self.lineno = lineno

    def gen(self):
        self.left.gen()
        self.right.gen()

class TypeNode(ASTNode):
    def __init__(self, type_ ,lineno):
        self.type_ = type_
        self.lineno = lineno

    def gen(self):
        AST.declare_variables(self.type_)

class IdNode(ASTNode):
    def __init__(self, id_, lineno):
        self.id_ = id_
        self.lineno = lineno

    def gen(self):
        AST.load_variable(self.id_, self.lineno)
        return self.id_

class AssignmentNode(ASTNode):
    def __init__(self, id_, expression, lineno):
        self.id_ = id_
        self.expression = expression
        self.lineno = lineno

    def gen(self):
        return AST.handle_assignment(self.id_.gen(), self.expression.gen(), self.lineno)

class InputNode(ASTNode):
    def __init__(self, id_):
        self.id_ = id_

    def gen(self):
        return AST.handle_input(self.id_.gen())

class OutputNode(ASTNode):
    def __init__(self, expression, lineno):
        self.expression = expression
        self.lineno = lineno

    def gen(self):
        return AST.handle_output(self.expression.gen(), self.lineno)

class IfNode(ASTNode):
    def __init__(self, boolean_expr, true_stmt, false_stmt, lineno):
        self.boolean_expr = boolean_expr
        self.true_stmt = true_stmt
        self.false_stmt = false_stmt
        self.lineno = lineno

    def gen(self):
        bool_expr = self.boolean_expr.gen()
        true_line = AST.next_statement_line()
        true_body = self.true_stmt.gen()
        else_line = AST.create_else_jump()
        false_line = AST.next_statement_line()
        false_body = self.false_stmt.gen()
        return AST.handle_ifStatement(bool_expr, true_line, else_line, false_line, true_body, false_body)

class StmtBlockNode(ASTNode):
    def __init__(self, stmt):
        self.stmt = stmt

    def gen(self):
        return self.stmt.gen()

class WhileNode(ASTNode):
    def __init__(self, boolean_expr, stmt, lineno):
        self.boolean_expr = boolean_expr
        self.stmt = stmt
        self.lineno = lineno

    def gen(self):
        start_line = AST.start_while()
        bool_expr = self.boolean_expr.gen()
        stmt_line = AST.next_statement_line()
        stmt_body = self.stmt.gen()
        return AST.handle_whileStatement(bool_expr, start_line, stmt_line, stmt_body)

class SwitchNode(ASTNode):
    def __init__(self, expr, case_list, stmt_list, lineno):
        self.expr = expr
        self.case_list = case_list
        self.stmt_list = stmt_list
        self.lineno = lineno

    def gen(self):
        expr_ = self.expr.gen()
        AST.start_switch(expr_, self.lineno)
        case_ = self.case_list.gen()
        self.stmt_list.gen()
        nextline = AST.current_line()
        return AST.handle_switchStatement(case_, nextline)

class CaseListNode(ASTNode):
    def __init__(self, case_list, num, stmt_list, lineno):
        self.case_list = case_list
        self.num = num
        self.stmt_list = stmt_list
        self.lineno = lineno

    def gen(self):
        c1 = self.case_list.gen()
        else_label = AST.start_case(self.num, self.lineno)
        s1 = self.stmt_list.gen()
        nextline = AST.current_line()
        return AST.handle_caseList(c1, else_label, s1, nextline)

class BreakNode(ASTNode):
    def __init__(self, lineno):
        self.lineno = lineno

    def gen(self):
        return AST.handle_breakStatement(self.lineno)

class StatementListNode(ASTNode):
    def __init__(self, stmt_list, stmt):
        self.left = stmt_list
        self.right = stmt

    def gen(self):
        s1 = self.left.gen()
        stmt_line = AST.next_statement_line()
        s2 = self.right.gen()
        return AST.handle_statementList(s1, s2, stmt_line)

class BooleanExprNode(ASTNode):
    def __init__(self, operator, left, right, lineno):
        self.operator = operator
        self.left = left
        self.right = right
        self.lineno = lineno

    def gen(self):
        return AST.handle_booleanExpression(
            AST.next_statement_line(), self.operator,
            self.left.gen(), self.right.gen(), self.lineno
        )

class NotNode(ASTNode):
    def __init__(self, boolean_expr, lineno):
        self.boolean_expr = boolean_expr
        self.lineno = lineno

    def gen(self):
        return AST.handle_notExpression(self.boolean_expr.gen())

class RelopNode(ASTNode):
    def __init__(self, operator, left_expr, right_expr, lineno):
        self.operator = operator
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.lineno = lineno

    def gen(self):
        return AST.handle_relop(
            AST.next_statement_line(), self.operator,
            self.left_expr.gen(), self.right_expr.gen(), self.lineno
        )

class CastNode(ASTNode):
    def __init__(self, cast_type, expression, lineno):
        self.cast_type = cast_type
        self.expression = expression
        self.lineno = lineno

    def gen(self):
        return AST.handle_cast(self.cast_type, self.expression.gen(), self.lineno)

class OperationNode(ASTNode):
    def __init__(self, operator, left, right, lineno):
        self.operator = operator
        self.left = left
        self.right = right
        self.lineno = lineno

    def gen(self):
        return AST.handle_math_operation(
            self.operator, self.left.gen(), self.right.gen()
        )

class IdfactorNode(ASTNode):
    def __init__(self, value, lineno):
        self.value = value
        self.lineno = lineno

    def gen(self):
        AST.check_variable(self.value, self.lineno)
        return self.value

class NumfactorNode(ASTNode):
    def __init__(self, value, lineno):
        self.value = value
        self.lineno = lineno

    def gen(self):
        return self.value
