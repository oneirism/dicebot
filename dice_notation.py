import re

import dice

op_details = {
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
        # exponentiation
        '^' : {
            'calc' : lambda a,b: a ** b,
            'prec' : 3 },
        # modulus
        '%' : {
            'calc' : lambda a,b: a % b,
            'prec': 4 },
        # max
        '$' : {
            'calc' : max,
            'prec' : 5 },
        # min
        '&': {
            'calc' : min,
            'prec' : 5 },
        # dice
        'd' : {
            'calc' : lambda a,b: dice.roll("{}d{}".format(a, b)),
            'prec' : 6 },
}


op_pattern = '()'
for operator in op_details:
    op_pattern += operator


dice_notation_pattern = re.compile('^(\d+(d\d+)?([{0}](?!$))?){{1,}}$'.format(op_pattern))
single_dice_notation_pattern = re.compile('^\d+d\d+$')


def is_valid_dice_notation(string: str) -> bool:
    return dice_notation_pattern.match(string)


def is_valid_single_dice_notation(string: str) -> bool:
    return single_dice_notation_pattern.match(string)


def is_number(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        return False


def peek(stack: list) -> list:
    return stack[-1] if stack else None


def apply_operator(operators: list, values: list, rolls: list):
    operator = operators.pop()
    right = values.pop()
    left = values.pop()

    if operator in op_details:
        calc = op_details[operator]['calc']
        result = calc(left, right)

        if isinstance(result, list):
            rolls.append(result)
            values.append(sum(result))
        else:
            values.append(result)


def greater_precedence(op1: str, op2: str) -> bool:
    return op_details[op1]['prec'] > op_details[op2]['prec']


def handicap(handicap_type: str, expression: str) -> (int, list):
    rolls = []
    rolls.append(dice.roll(expression))
    rolls.append(dice.roll(expression))

    total = -1
    if handicap_type == 'advantage':
        total = max(rolls)
    elif handicap_type == 'disadvantage':
        total = min(rolls)
    return int(total), rolls


def evaluate(expression: str) -> (int, list):
    tokens = re.findall("[{0}]|\d+".format(op_pattern), expression)

    rolls = []
    values = []
    operators = []
    for token in tokens:
        if is_number(token):
            values.append(int(token))
        elif token == '(':
            operators.append(token)
        elif token == ')':
            top = peek(operators)
            while top is not None and top != '(':
                apply_operator(operators, values, rolls)
                top = peek(operators)
            operators.pop() # Discard the '('
        else:
            # Operator
            top = peek(operators)
            while top is not None and top not in "()" and greater_precedence(top, token):
                apply_operator(operators, values, rolls)
                top = peek(operators)
            operators.append(token)
    while peek(operators) is not None:
        apply_operator(operators, values, rolls)

    return sum(values), rolls


def init():
    if __name__ == '__main__':
        query = input()
        total, rolls = evaluate(query)
        print("Total: {0}\nRolls: {1}\n".format(total, rolls))


init()
