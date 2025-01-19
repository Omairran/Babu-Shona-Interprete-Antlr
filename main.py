import sys
from antlr4 import *
from generated.BabuShonaLexer import BabuShonaLexer
from generated.BabuShonaParser import BabuShonaParser
from generated.BabuShonaVisitor import BabuShonaVisitor


class BabuShonaInterpreter(BabuShonaVisitor):
    def __init__(self):
        self.variables = {}

    def visitPrintStmt(self, ctx):
        expr = ctx.expr()
        result = self.visit(expr)
        print(result)
        return None

    def visitVarDecl(self, ctx):
        var_name = ctx.IDENTIFIER().getText()
        expr = ctx.expr()
        value = self.visit(expr)
        self.variables[var_name] = value
        return None

    def visitInputStmt(self, ctx):
        var_name = ctx.IDENTIFIER().getText()
        user_input = input(f"{var_name} (True/False/Number/String): ")
        if user_input == "True":
            self.variables[var_name] = True
        elif user_input == "False":
            self.variables[var_name] = False
        elif user_input.isdigit():
            self.variables[var_name] = int(user_input)
        else:
            self.variables[var_name] = user_input
        return None

    def visitIfStmt(self, ctx):
        condition = self.visit(ctx.expr())
        if self.is_truthy(condition):
            self.visit(ctx.block())
            return None

        for elseIf in ctx.elseIfStmt():
            condition = self.visit(elseIf.expr())
            if self.is_truthy(condition):
                self.visit(elseIf.block())
                return None

        if ctx.elseStmt():
            self.visit(ctx.elseStmt().block())
        return None

    def visitForLoopStmt(self, ctx):
        loop_var = ctx.IDENTIFIER().getText()
        start = self.visit(ctx.expr(0))
        end = self.visit(ctx.expr(1))
        step = self.visit(ctx.expr(2)) if ctx.expr(2) else 1

        self.variables[loop_var] = start
        while self.variables[loop_var] < end:
            self.visit(ctx.block())
            self.variables[loop_var] += step

        del self.variables[loop_var]
        return None

    def is_truthy(self, value):
        if isinstance(value, (int, float)) and value == 0:
            return False
        elif value == "" or value is False:
            return False
        return True

    def visitArithmeticExpr(self, ctx):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        operator = ctx.getChild(1).getText()

        if operator == "+":
            return float(left) + float(right)
        elif operator == "-":
            return float(left) - float(right)
        elif operator == "*":
            return float(left) * float(right)
        elif operator == "/":
            return float(left) / float(right)
        return None

    def visitComparisonExpr(self, ctx):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        operator = ctx.getChild(1).getText()

        if operator == "<":
            return left < right
        elif operator == "<=":
            return left <= right
        elif operator == ">":
            return left > right
        elif operator == ">=":
            return left >= right
        elif operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        return None

    def visitLogicalExpr(self, ctx):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        operator = ctx.getChild(1).getText()

        if operator == "and":
            return left and right
        elif operator == "or":
            return left or right
        return None

    def visitNotExpr(self, ctx):
        expr = self.visit(ctx.expr())
        return not expr

    def visitIntExpr(self, ctx):
        return int(ctx.INT().getText())

    def visitStringExpr(self, ctx):
        return ctx.STRING().getText().strip('"')

    def visitBooleanExpr(self, ctx):
        return ctx.getText() == "True"

    def visitVariableExpr(self, ctx):
        var_name = ctx.IDENTIFIER().getText()
        if var_name in self.variables:
            return self.variables[var_name]
        else:
            raise ValueError(f"Variable '{var_name}' is not defined.")

    def visitParenthesesExpr(self, ctx):
        return self.visit(ctx.expr())


def execute_babu_script(file_path):
    try:
        with open(file_path, "r") as file:
            script = file.read()

        input_stream = InputStream(script)
        lexer = BabuShonaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = BabuShonaParser(token_stream)

        tree = parser.script()

        interpreter = BabuShonaInterpreter()
        interpreter.visit(tree)
    except Exception as e:
        print(f"Error executing script: {e}")


if __name__ == "__main__":
    # Ensure the script path is provided as a command-line argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        execute_babu_script(file_path)
    else:
        print("Error: No file path provided. Please provide a path to a .babu script.")
        sys.exit(1)