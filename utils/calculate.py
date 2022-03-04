def format_output(result):
    expr_str = str(result)
    if '.' in expr_str:
        suffix = expr_str.split('.')[1]
        if len(suffix) > 2:
            return '%.2f' % result
        else:
            return str(result)
    else:
        return int(result)


def calc(string):
    if len(string.split()) <= 1:
        # no expression
        return '没有表达式'

    expression = ' '.join(string.split()[1:])
    try:
        result = eval(expression)
        result = format_output(result)
    except (SyntaxError, TypeError):
        # expression has error
        result = '表达式不正确'
    return result


if __name__ == '__main__':
    result = calc('计算 3/2')
    print(result)
