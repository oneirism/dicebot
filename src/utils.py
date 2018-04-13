import dice


def format_response(title, result):
    response = '<i>{0}</i>\n'.format(title)

    rolls = print_sub(result)

    response += '<b>Results:</b>\n'
    if isinstance(rolls, str):
        response += '\t\t{0}\n'.format(rolls)
    else:
        for roll in rolls:
            if isinstance(roll, str):
                response += '\t\t{0}\n'.format(roll)
            else:
                response += '\t\t{0}\n'.format(roll[0])

    if isinstance(result.result, list):
        total = sum(result.result)
    else:
        total = result.result

    response += '<b>Total</b>: {0}'.format(total)

    return response

def print_op(element):
    lines = []

    for _, e in enumerate(element.original_operands):
        newlines = print_sub(e)
        if newlines is not None:
            lines.append(newlines)

    return lines

def print_sub(element, **kwargs):
    if not hasattr(element, 'result'):
        element.evaluate_cached(**kwargs)

    if isinstance(element, dice.elements.Operator):
        return print_op(element)

    elif isinstance(element, dice.elements.Dice):
        return '{}: {}'.format(element, element.result)

    return None
