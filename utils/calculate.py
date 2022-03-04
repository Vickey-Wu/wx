def calc(string):
    if len(string.split()) <= 1:
        # no expression
        return '没有表达式'

    expression = ' '.join(string.split()[1:])
    try:
        result = eval(expression)
    except (SyntaxError, TypeError):
        # expression has error
        result = '表达式不正确'
    return str(result)


if __name__ == '__main__':
    result = calc('计算 1+2')
    print(result)
