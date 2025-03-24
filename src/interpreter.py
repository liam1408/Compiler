
from collections import OrderedDict

class Success:
    found_errors = 0

class Command:
    def __init__(self, opcode='', arg1='', arg2='', arg3=''):
        self.opcode = opcode
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def __repr__(self):
        return f"< {self.opcode} {self.arg1} {self.arg2} {self.arg3}>"


class Interpreter:
    def __init__(self):
        self.commands = []
        self.switch_names = '$0' , '$1'
        self.labels = {}
        self.table = OrderedDict()
        self.nesting = 0
        self.count = 0


    def add_nest(self):
        self.nesting += 1

    def remove_nest(self):
        self.nesting -= 1

    def in_nest(self):
        return self.nesting > 0

    def load(self, name):
        """ Adds a variable to table if not already in table. """
        if name not in self.table:
            self.table[name] = ''
            return True
        else:
            return False

    def assign_type(self, typing):
        """ adds the type of the variables into the table"""
        for var in reversed(list(self.table.keys())):
            if self.table[var] == '':
                self.table[var] = typing
            else:
                break

    def in_table(self, var):
        """ checks if the variable is in the table"""
        return var in self.table

    def get_type(self, var):
        """ returns the type of variable """
        if '.' in var:
            return 'float'
        elif self.in_table(var):
            return self.table[var]
        else:
            return 'int'

    def generate_temp_variable(self):
        """ generates t values starts from 2 """
        temp_name = f't{self.count+1}'
        self.count += 1
        return temp_name


    def compile_commands(self):
        compiled = []
        for command in self.commands:
            if command.opcode in ('JMPZ', 'JUMP'):
                command.arg1 = self.labels.get(command.arg1, command.arg1)
            compiled.append(f"{command.opcode} {command.arg1} {command.arg2} {command.arg3}")
        return compiled

    def current_line(self):
        """ returns the current line """
        return len(self.commands) + 1

    def next_statement_line(self):
        """returns the next statement line"""
        return self.assign_label(self.current_line())

    def create_else_jump(self):
        """ creates a JUMP command"""
        else_label = self.assign_label(self.current_line())
        self.commands.append(Command('JUMP', else_label))
        return else_label

    def insert_halt(self):
        """ insert halt at the end """
        self.commands.append(Command('HALT'))
        return self.current_line() - 1

    def start_case(self, var, lineno):
        """ interpreters the case within the switch by doing the check with the switch stmt and the case value,
        with IEQL to check if equal , and JMPZ to exit if not equal"""
        if self.get_type(var) != 'int':
            print(f"error at line {lineno}, illegal type 'float' in case, variable='{var}'")
            Success.found_errors = 1
        pair = self.switch_names
        self.commands.append(Command('IEQL', pair[0], pair[1], var))
        case_label = self.assign_label(self.current_line())
        self.commands.append(Command('JMPZ', case_label, pair[0]))
        return case_label

    def start_while(self):
        """ starting the while interpretation """
        self.add_nest()
        return self.next_statement_line()

    def start_switch(self, var, lineno):
        """ starting the switch interpretation, getting the switch names t0 t1 to use for the cases checks
         also checks if the value in the case is a int value
         """
        self.add_nest()
        if self.get_type(var) != 'int':
            print(f"error at line {lineno} illegal type 'float' in case, variable='{var}'")
            Success.found_errors = 1
        pair = self.switch_names
        self.commands.append(Command('IASN', pair[1], var))

    def assign_label(self, lineno):
        """ assign labels for the lines """
        self.labels[lineno] = lineno
        return lineno

    def back_patching(self, label_list, target):
        """ backpatching for the labels """
        for label in label_list:
            self.labels[label] = target

    def handle_cast(self, cast_type, var, lineno):
        """ handles the cast<> , checks if the casting is legal"""
        original_type = self.get_type(var)
        target_type = 'float' if 'float' in cast_type else 'int'
        if original_type == target_type:
            print(f"error at line {lineno}, casting from '{target_type}' to '{original_type}', variable='{var}'")
        result_var = self.generate_temp_variable()
        opcode = 'ITOR' if target_type == 'float' else 'RTOI'
        self.commands.append(Command(opcode, result_var, var))
        return result_var

    def handle_epsilon(self):
        """ handles the epsilon , returns empty """
        return []

    def handle_assignment(self, target, source, lineno):
        """ handles variable assignments """
        target_type = self.get_type(target)
        source_type = self.get_type(source)

        if target_type == '':
            self.table[target] = source_type

        if self.get_type(target) == 'int' and self.get_type(source) == 'float':
            print(f"error at line {lineno}, can't assign 'float' to 'int'")
            Success.found_errors = 1
        opcode = 'RASN' if target_type == 'float' else 'IASN'
        self.commands.append(Command(opcode, target, source))
        return []

    def handle_math_operation(self, operator, left_var, right_var):
        """ handles math operation , checks if the value of the operation should be float
            then appends the right command into the Command struct"""
        left_type = self.get_type(left_var)
        right_type = self.get_type(right_var)
        result_type = 'float' if left_type == 'float' or right_type == 'float' else 'int'
        type_index = 0 if result_type == 'float' else 1
        opcodes = {
            '+': ['RADD', 'IADD'],
            '-': ['RSUB', 'ISUB'],
            '*': ['RMLT', 'IMLT'],
            '/': ['RDIV', 'IDIV']
        }
        result = self.generate_temp_variable()
        self.commands.append(Command(opcodes[operator][type_index], result, left_var, right_var))
        return result

    def handle_relop(self, jump_line, operator, left_var, right_var, lineno):
        """ handles relop operation , checks if the value of the operation should be float
                then appends the right command into the Command struct"""
        var1, var2, result_type = self.handle_numeric(left_var, right_var, lineno)
        type_index = 0 if result_type == 'float' else 1
        opcodes = {
            '==': ['REQL', 'IEQL'],
            '!=': ['RNQL', 'INQL'],
            '<': ['RLSS', 'ILSS'],
            '>': ['RGRT', 'IGRT'],
            '>=': ['RLSS', 'ILSS'],
            '<=': ['RGRT', 'IGRT']
        }
        result = self.generate_temp_variable()
        self.commands.append(Command(opcodes[operator][type_index], result, var1, var2))
        if operator in ('>=', '<='):
            self.commands.append(Command('ISUB', result, '1', result))
        self.commands.append(Command('JMPZ', jump_line, result))
        true_label = self.assign_label(self.current_line())
        return [[true_label], [jump_line]]

    def handle_output(self, var, lineno):
        """Outputs a variable or a number, checking if a variable has been declared."""

        if isinstance(var, str) and var.isdigit():
            var = int(var)
        elif isinstance(var, str):
            try:
                var = float(var)
            except ValueError:
                pass

        if isinstance(var, (int, float)):
            opcode = 'RPRT' if isinstance(var, float) else 'IPRT'
            self.commands.append(Command(opcode, var))
            return []

        # If not a number, check if it's a declared variable
        if not self.in_table(var):
            print(f"error at line {lineno}, undeclared variable {var}")
            Success.found_errors = 1
            return []

        # Get the correct opcode based on variable type
        opcode = 'RPRT' if self.get_type(var) == 'float' else 'IPRT'
        self.commands.append(Command(opcode, var))
        return []

    def handle_input(self, var):
        """ Handles input for a variable. """
        var_type = self.get_type(var)
        opcode = 'RINP' if var_type == 'float' else 'IINP'
        self.commands.append(Command(opcode, var))
        return []


    def handle_numeric(self, var1, var2, lineno):
        """ handles the number casting to match the expected type in the result """
        type1 = self.get_type(var1)
        type2 = self.get_type(var2)
        result_type = 'float' if type1 == 'float' or type2 == 'float' else 'int'
        new_var1 = var1
        new_var2 = var2
        if result_type == 'float':
            if type1 == 'int':
                new_var1 = self.handle_cast('float', var1, lineno)
            if type2 == 'int':
                new_var2 = self.handle_cast('float', var2, lineno)
        return new_var1, new_var2, result_type

    def load_variable(self, var, lineno):
        """ loads variable if already loaded prints error """
        if not self.load(var):
            print(f"error at line {lineno}, multiple declarations of {var}")
            Success.found_errors = 1

    def declare_variables(self, type_spec):
        """ assign variables their declared type. """
        self.assign_type(type_spec)

    def check_variable(self, var, lineno):
        if not self.in_table(var):
            print(f"error at line {lineno}, undeclared variable '{var}'")
            Success.found_errors = 1

    def handle_booleanExpression(self, jump_line, operator, left_expr, right_expr, lineno):
        """ handles boolean expressions and/or interpretation """
        if operator == '&&':
            self.back_patching(left_expr[0], jump_line)
            true_list = right_expr[0]
            false_list = left_expr[1] + right_expr[1]
        elif operator == '||':
            self.back_patching(left_expr[1], jump_line)
            true_list = left_expr[0] + right_expr[0]
            false_list = right_expr[1]
        else:
            true_list = false_list = []
        return [true_list, false_list]

    def handle_notExpression(self, boolean_expr):
        """ handles not expression """
        return [boolean_expr[1], boolean_expr[0]]

    def handle_Program(self, entry_labels, halt_line):
        self.back_patching(entry_labels, halt_line)
        return self.compile_commands()

    def handle_statementList(self, first_list, second_list, statement_line):
        self.back_patching(first_list, statement_line)
        return second_list

    def handle_ifStatement(self, bool_expr, true_line, else_line, false_line, true_stmt, false_stmt):
        self.back_patching(bool_expr[0], true_line)
        self.back_patching(bool_expr[1], false_line)
        return true_stmt + false_stmt + [else_line]

    def handle_whileStatement(self, bool_expr, while_start, stmt_line, stmt_body):
        self.back_patching(stmt_body, while_start)
        self.back_patching(bool_expr[0], stmt_line)
        start_label = self.assign_label(self.current_line())
        self.labels[start_label] = while_start
        self.commands.append(Command('JUMP', start_label))
        self.remove_nest()
        return bool_expr[1]

    def handle_caseList(self, case_list, else_label, stmt_list, next_line):
        self.back_patching([else_label], next_line + 1)
        true_label = self.assign_label(self.current_line())
        self.commands.append(Command('JUMP', true_label))
        exits = case_list + [true_label]
        return exits

    def handle_switchStatement(self, case_list, next_line):
        self.back_patching(case_list, next_line)
        self.remove_nest()
        return []

    def handle_breakStatement(self, lineno):
        if not self.in_nest():
            print("error at line %s, illegal 'break;' out of if/while scope" % (lineno))
            Success.found_errors = 1
        return []
