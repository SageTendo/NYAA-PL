import json


class Node:
    def __init__(self, node_label):
        self.label = node_label

    def accept(self, visitor):
        return visitor.visit(self)

    def to_json(self):
        node_map = self.__dict__.copy()
        for k, v in node_map.items():
            if v is None:
                node_map[k] = "null"
            if v is True:
                node_map[k] = "true"
            if v is False:
                node_map[k] = "false"

            if isinstance(v, list):
                node_map[k] = []
                for item in v:
                    node_map[k].append(item.to_json())

            if isinstance(v, dict):
                node_map[k] = {}
                for key, value in v.items():
                    node_map[k][key] = value.to_json()

            if isinstance(v, Node):
                node_map[k] = v.to_json()
        return node_map

    def encode_json(self):
        return json.dumps(self.to_json(), indent=2)


class ConditionalNode(Node):
    def __init__(self, expr, body=None, label="Conditional"):
        super().__init__(label)
        self.expr = expr
        self.body = body


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


class FuncDefNode(Node):
    def __init__(self, identifier, args, body):
        super().__init__("func_def")
        self.identifier = identifier
        self.args = args
        self.body = body


class BodyNode(Node):
    def __init__(self):
        super().__init__("body")
        self.statements = []

    def append(self, statement):
        self.statements.append(statement)


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


class TryCatchNode(Node):
    def __init__(self, body, catch_body):
        super().__init__("try_catch")
        self.body = body
        self.catch_body = catch_body


class ArgsNode(Node):
    def __init__(self):
        super().__init__("args")
        self.children = []

    def append(self, argument):
        self.children.append(argument)


class CallNode(Node):
    def __init__(self, identifier, args):
        super().__init__("call")
        self.identifier = identifier
        self.args = args


class InputNode(Node):
    def __init__(self, msg=None):
        super().__init__("input")
        self.message = msg if msg else ""


class PrintNode(Node):
    def __init__(self, args):
        super().__init__("print")
        self.args = args


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


class ExprNode(Node):
    def __init__(self):
        super().__init__("expr")

        self.left = None
        self.right = None
        self.op = None


class PostfixExprNode(Node):
    def __init__(self, left, op=None):
        super().__init__('postfix_expr')
        self.left = left
        self.op = op


class SimpleExprNode(Node):
    def __init__(self):
        super().__init__('simple_expr')
        self.left = None
        self.right = None
        self.op = None


class TermNode(Node):
    def __init__(self):
        super().__init__('term')
        self.left = None
        self.right = None
        self.op = None


class FactorNode(Node):
    def __init__(self, left, right=None):
        super().__init__("factor")
        self.left = left
        self.right = right


class IdentifierNode(Node):
    def __init__(self, token):
        super().__init__("identifier")
        self.value = token.value


class NumericLiteralNode(Node):
    def __init__(self, token):
        super().__init__("numeric_literal")

        self.type = token.type
        self.value = token.value

    def to_json(self):
        return {
            "type": str(self.type),
            "value": str(self.value)
        }


class StringLiteralNode(Node):
    def __init__(self, token):
        super().__init__("string_literal")
        self.value = token.value


class BooleanNode(Node):
    def __init__(self, token):
        super().__init__("boolean_literal")
        self.value = token.type

    def to_json(self):
        return {
            "value": str(self.value)
        }


class OperatorNode(Node):
    def __init__(self, value):
        super().__init__("operator")
        self.value = value
