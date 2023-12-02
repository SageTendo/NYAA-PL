class Node:
    def __init__(self, node_label):
        self.label = node_label

    def __repr__(self):
        return self.label.upper()

    def __str__(self):
        return f"{self.__repr__()}"

    def accept(self, visitor):
        print(f"Visiting {self.label}")
        return visitor.visit(self)


class ConditionalNode(Node):
    def __init__(self, expr, body=None, label="Conditional"):
        super().__init__(label)
        self.expr = expr
        self.body = body

    def __repr__(self):
        return f"{self.label.upper()}: {self.expr} {self.body}"


class ProgramNode(Node):
    def __init__(self):
        super().__init__("program")

        self.functions = []
        self.body = None
        self.eof = False

    def set_eof(self):
        self.eof = True

    def append_func(self, func):
        self.functions.append(func)

    def set_body(self, body):
        self.body = body

    def __repr__(self):
        functions = "[]"
        body = "[]"

        if self.functions:
            functions = self.functions
        if self.body:
            body = self.body
        return f"{self.label.upper()}: FUNC_DEF: {functions} {body}"


class FuncDefNode(Node):
    def __init__(self, identifier, args, body):
        super().__init__("func_def")
        self.identifier = identifier
        self.args = args
        self.body = body

    def __repr__(self):
        return f"{self.label.upper()}: {self.identifier}({self.args}) {self.body}"


class BodyNode(Node):
    def __init__(self):
        super().__init__("body")
        self.statements = []

    def append(self, statement):
        self.statements.append(statement)

    def __repr__(self):
        return f"{self.label.upper()}: {self.statements}"

    def __str__(self):
        return self.__repr__()


class PassNode(Node):
    def __init__(self):
        super().__init__("pass")


class BreakNode(Node):
    def __init__(self):
        super().__init__("break")


class ContinueNode(Node):
    def __init__(self):
        super().__init__("continue")


class ReturnNode(Node):
    def __init__(self):
        super().__init__("return")
        self.expr = None

    def set_expr(self, expr):
        self.expr = expr

    def __repr__(self):
        if self.expr:
            return f"{self.label.upper()}: {self.expr}"
        return super().__repr__()


class TryCatchNode(Node):
    def __init__(self, body, catch_body):
        super().__init__("try_catch")
        self.body = body
        self.catch_body = catch_body

    def __repr__(self):
        return f"{self.label.upper()}: [{self.body}] | Catch: [{self.catch_body}]"


class ArgsNode(Node):
    def __init__(self):
        super().__init__("args")
        self.children = []

    def append(self, argument):
        self.children.append(argument)

    def __repr__(self):
        return f"{self.label.upper()}: {self.children}"


class CallNode(Node):
    def __init__(self, identifier, args):
        super().__init__("call")
        self.left = identifier
        self.right = args

    def __repr__(self):
        return f"{self.label.upper()}: {self.left}({self.right})"


class InputNode(Node):
    def __init__(self, msg):
        super().__init__("input")
        self.message = msg

    def __repr__(self):
        return f"{self.label.upper()}: {self.message}"


class PrintNode(Node):
    def __init__(self, args):
        super().__init__("print")
        self.args = args

    def __repr__(self):
        return f"{self.label.upper()}: {self.args}"


class WhileNode(ConditionalNode):
    def __init__(self, expr, body):
        super().__init__(expr, body, "while")


class IfNode(ConditionalNode):
    def __init__(self, expr, body):
        super().__init__(expr, body, "if")

        self.else_if_statements = []
        self.else_body = None

    def append_else_if(self, statement):
        self.else_if_statements.append(statement)

    def set_else_body(self, body):
        self.else_body = body

    def __repr__(self):
        return (f"{self.label.upper()}: {self.expr} {self.body} |"
                f" ELIFS:{self.else_if_statements} |"
                f" ELSE: {self.else_body}")


class ElifNode(ConditionalNode):
    def __init__(self, expr, body):
        super().__init__(expr, body, "elif")


class ElseNode(ConditionalNode):
    def __init__(self, body):
        super().__init__(None, body, "else")


class AssignmentNode(Node):
    def __init__(self, left, right):
        super().__init__("assignment")
        self.left = left
        self.right = right

    def __repr__(self):
        return f"{self.label.upper()}: {self.left} = {self.right}"


class ExprNode(Node):
    def __init__(self):
        super().__init__("expr")

        self.left = None
        self.right = None
        self.op = None

    def __repr__(self):
        if self.op and self.right:
            return f"{self.label.upper()}: {self.left} {self.op} {self.right}"
        return f"{self.label.upper()}: {self.left}"

    def __str__(self):
        return self.__repr__()


class PostfixExprNode(Node):
    def __init__(self, left, op=None):
        super().__init__('postfix_expr')
        self.left = left
        self.op = op

    def __repr__(self):
        return f"{self.label.upper()}: ({self.left}) {self.op}"


class SimpleExprNode(Node):
    def __init__(self):
        super().__init__('simple_expr')
        self.left = None
        self.right = None
        self.op = None

    def __repr__(self):
        if self.op and self.right:
            return f"{self.label.upper()}: {self.left} {self.op} {self.right}"
        return f"{self.label.upper()}: {self.left}"


class TermNode(Node):
    def __init__(self):
        super().__init__('term')
        self.left = None
        self.right = None
        self.op = None

    def __repr__(self):
        if self.op and self.right:
            return f"{self.label.upper()}: {self.left} {self.op} {self.right}"
        return f"{self.label.upper()}: {self.left}"


class FactorNode(Node):
    def __init__(self, left, right=None):
        super().__init__("factor")
        self.left = left
        self.right = right

    def __repr__(self):
        if self.right:
            return f"{self.label.upper()}: {self.left} {self.right}"
        return f"{self.label.upper()}: {self.left}"


class IdentifierNode(Node):
    def __init__(self, token):
        super().__init__("identifier")
        self.value = token.value

    def __repr__(self):
        return f"{self.label.upper()}: {self.value}"


class NumericLiteralNode(Node):
    def __init__(self, token):
        super().__init__("numeric_literal")

        self.type = token.type
        self.value = token.value

    def __repr__(self):
        return f"{self.label.upper()}({self.type}): {self.value}"


class StringLiteralNode(Node):
    def __init__(self, token):
        super().__init__("string_literal")
        self.value = token.value

    def __repr__(self):
        return f"{self.label.upper()}: {self.value}"


class BooleanNode(Node):
    def __init__(self, token):
        super().__init__("boolean_literal")
        self.value = token.type

    def __repr__(self):
        return f"{self.label.upper()}: {self.value}"
