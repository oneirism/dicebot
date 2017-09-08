#!/usr/bin/env python3

# Third-Party
import dice

# Relative
import grammar
grammar = grammar.Grammar()


# Compiled Regexes
single_die_pattern = grammar.die_pattern
dice_notation_pattern = grammar.dice_notation_pattern


def is_single_die(string: str) -> bool:
    return single_die_pattern.match(string)


def is_dice_notation(string: str) -> bool:
    return dice_notation_pattern.match(string)


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


def init():
    if __name__ == '__main__':
        query = input()
        total, rolls = grammar.evaluate(query)
        print("Total: {0}\nRolls: {1}\n".format(total, rolls))


init()
