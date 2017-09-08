import re
from typing import Callable

import dice


class Grammar():
    operators = {
        # addition
        '+' : {
            'calc' : lambda a,b: a + b,
            'prec': 0 },
        # subtraction
        '-' : {
            'calc' : lambda a,b: a - b,
            'prec': 0 },
        # division
        '/' : {
            'calc' : lambda a,b: a / b,
            'prec' : 1 },
        # multiplication
        '*' : {
            'calc' : lambda a,b: a * b,
            'prec' : 1 },
        # dice
        'd' : {
            'calc' : lambda a,b: dice.roll('{}d{}'.format(a, b)),
            'prec' : 2 },
    }


    def __init__(self):
        # Numbers and brackets
        token_characters = '\d()'

        # Plus supported operators
        for operator in self.operators:
            token_characters += operator

        self.die_pattern = re.compile('^(\d)?(d\d+)$')
        self.operator_pattern = re.compile('[{0}]'.format(token_characters))
        self.dice_notation_pattern = re.compile('^(((\d+)|((\d+)?(d\d+)))([{0}](?!$))?){{1,}}$'.format(token_characters))


    def apply_operator(self, operators: list, values: list, rolls: list):
        operator = operators.pop()
        right = values.pop()
        left = values.pop()

        calc = self.get_calc(operator)

        result = calc(left, right)

	# We track rolls for better output at the end.
        if operator == 'd':
            rolls.append(result)
            values.append(sum(result))
        else:
            values.append(result)


    def evaluate(self, expression: str) -> (int, list):
        tokens = self.get_tokens(expression)

        operators = []
        rolls = []
        values = []

        # Convert to postfix, applying operators where precedence allows
        for token in tokens:
            # Raw numbers go straight into values.
            if self.is_number(token):
                values.append(int(token))
            # Track opening brackets so we can work back later.
            elif token == '(':
                operators.append(token)
            # When we reach a closing bracket, we work back to the opening.
            elif token == ')':
                top = self.peek(operators)
                while top is not None and top != '(':
                    self.apply_operator(operators, values, rolls)
                    top = self.peek(operators)
                operators.pop()
            else:
                top = self.peek(operators)
                while top is not None and top not in "()" and self.greater_precedence(top, token):
                    self.apply_operator(operators, values, rolls)
                    top = self.peek(operators)
                operators.append(token)

        # Apply the remaining operators.
        while self.peek(operators) is not None:
            self.apply_operator(operators, values, rolls)

        # Return the final result along with a list of roll lists from 'd' operators
        return sum(values), rolls


    def get_calc(self, operator: str) -> Callable[[int, int], int]:
        if operator in self.operators:
            return self.operators[operator]['calc']
        return None


    def get_tokens(self, expression: str) -> list:
        return re.findall(self.operator_pattern, expression)


    def greater_precedence(self, op1: str, op2: str) -> bool:
        return self.operators[op1]['prec'] > self.operators[op2]['prec']


    def is_number(self, string: str) -> bool:
        try:
            int(string)
            return True
        except ValueError:
            return False


    def peek(self, stack: list) -> list:
        return stack[-1] if stack else None
