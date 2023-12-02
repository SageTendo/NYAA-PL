class Node:
    def __init__(self, node_label):
        self.label = node_label

    def __repr__(self):
        return self.label

    def __str__(self):
        return f"{self.__repr__()}"


class ConditionalNode(Node):
    def __init__(self, expr, body=None, label="Conditional"):
        super().__init__(label)
        self.expr = expr
        self.body = body

    def __repr__(self):
        return f"{self.label}: {self.expr} {self.body}"


class ProgramNode(Node):
    def __init__(self):
        super().__init__("Program")

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
        return f"{self.label}: FuncDefs: {functions} {body}"


class FuncDefNode(Node):
    def __init__(self, identifier, args, body):
        super().__init__("FuncDef")
        self.identifier = identifier
        self.args = args
        self.body = body

    def __repr__(self):
        return f"{self.label}: {self.identifier}({self.args}) {self.body}"


class BodyNode(Node):
    def __init__(self):
        super().__init__("Body")
        self.statements = []

    def append(self, statement):
        self.statements.append(statement)

    def __repr__(self):
        return f"{self.label}: {self.statements}"

    def __str__(self):
        return self.__repr__()


class PassNode(Node):
    def __init__(self):
        super().__init__("Pass")


class BreakNode(Node):
    def __init__(self):
        super().__init__("Break")


class ContinueNode(Node):
    def __init__(self):
        super().__init__("Continue")


class ReturnNode(Node):
    def __init__(self):
        super().__init__("Return")
        self.expr = None

    def set_expr(self, expr):
        self.expr = expr

    def __repr__(self):
        if self.expr:
            return f"{self.label}: {self.expr}"
        return f"{self.label}"


class TryCatchNode(Node):
    def __init__(self, body, catch_body):
        super().__init__("TryCatch")
        self.body = body
        self.catch_body = catch_body

    def __repr__(self):
        return f"{self.label}: {self.body} | Catch: [{self.catch_body}]"


class ArgsNode(Node):
    def __init__(self):
        super().__init__("args")
        self.children = []

    def append(self, argument):
        self.children.append(argument)

    def __repr__(self):
        return f"{self.label}: {self.children}"


class CallNode(Node):
    def __init__(self, identifier, args):
        super().__init__("call")
        self.left = identifier
        self.right = args

    def __repr__(self):
        return f"{self.label}: {self.left}({self.right})"


class InputNode(Node):
    def __init__(self, msg):
        super().__init__("input")
        self.message = msg

    def __repr__(self):
        return f"{self.label}: {self.message}"


class PrintNode(Node):
    def __init__(self, args):
        super().__init__("print")
        self.args = args

    def __repr__(self):
        return f"{self.label}: {self.args}"


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
        return f"{self.label}: {self.expr} {self.body} | Elifs:{self.else_if_statements} | Else: {self.else_body}"


class ElifNode(ConditionalNode):
    def __init__(self, expr, body):
        super().__init__(expr, body, "elif")


class ElseNode(ConditionalNode):
    def __init__(self, body):
        super().__init__(None, body, "else")


class AssignmentNode(Node):
    def __init__(self, left, right):
        super().__init__("Assignment")
        self.left = left
        self.right = right

    def __repr__(self):
        return f"{self.label}: {self.left} = {self.right}"


class ExprNode(Node):
    def __init__(self, left, right=None, op=None):
        super().__init__("Expr")

        self.left = left
        self.right = right
        self.op = op

    def __repr__(self):
        if self.op and self.right:
            return f"{self.label}: {self.left} {self.op} {self.right}"
        return f"{self.label}: {self.left}"

    def __str__(self):
        return self.__repr__()


class PostfixExprNode(Node):
    def __init__(self, left, op=None):
        super().__init__('PostfixExpr')
        self.left = left
        self.op = op

    def __repr__(self):
        return f"{self.label}: ({self.left}) {self.op}"


class SimpleExprNode(Node):
    def __init__(self):
        super().__init__('SimpleExpr')
        self.children = []

    def append(self, expr):
        self.children.append(expr)

    def __repr__(self):
        return f"{self.label}: {self.children}"


class TermNode(Node):
    def __init__(self):
        super().__init__('Term')
        self.children = []

    def append(self, term):
        self.children.append(term)

    def __repr__(self):
        return f"{self.label}: {self.children}"


class FactorNode(Node):
    def __init__(self, left, right=None):
        super().__init__("Factor")
        self.left = left
        self.right = right

    def __repr__(self):
        if self.right:
            return f"{self.label}: {self.left} {self.right}"
        return f"{self.label}: {self.left}"


class IdentifierNode(Node):
    def __init__(self, token):
        super().__init__("Identifier")
        self.value = token.value

    def __repr__(self):
        return f"{self.label}: {self.value}"


class NumericLiteralNode(Node):
    def __init__(self, token):
        super().__init__("NumericLiteral")

        self.type = token.type
        self.value = token.value

    def __repr__(self):
        return f"{self.label}({self.type}): {self.value}"


class StringLiteralNode(Node):
    def __init__(self, token):
        super().__init__("StringLiteral")
        self.value = token.value

    def __repr__(self):
        return f"{self.label}: {self.value}"


class BooleanOpNode(Node):
    def __init__(self, token):
        super().__init__("BooleanLiteral")
        self.value = token.type

    def __repr__(self):
        return f"{self.label}: {self.value}"


class OperatorNode(Node):
    def __init__(self, label, value):
        super().__init__(label)
        self.value = value

    def __repr__(self):
        if self.value is None:
            return f"{self.label}: None"
        return f"{self.label}: {self.value}"


class NegationNode(OperatorNode):
    def __init__(self):
        super().__init__("Negation", "-")


class NotNode(OperatorNode):
    def __init__(self):
        super().__init__("Complement", "not")


class AddOpNode(OperatorNode):
    def __init__(self, value):
        super().__init__("AddOP", value)


class MulOpNode(OperatorNode):
    def __init__(self, value):
        super().__init__("MulOp", value)


class RelOpNode(OperatorNode):
    def __init__(self, value):
        super().__init__("RelOp", value)
