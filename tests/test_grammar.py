from grammar import Grammar


def test_evaluate():
    grammar = Grammar()

    query = "(3d1 + 5) * 2"
    expected = 16

    total, rolls = grammar.evaluate(query)

    print(total)
    print(rolls)

    assert total == expected
    assert ((sum(int(roll) for roll in rolls) + 5) * 2) == expected

    query = "3d1 + 2"
    expected = 5

    total, rolls = grammar.evaluate(query)

    assert total == expected
    assert (sum(int(roll) for roll in rolls) + 2) == expected


def test_get_calc():
    grammar = Grammar()

    try:
        grammar.get_calc('¬')
        assert False
    except:
        assert True
