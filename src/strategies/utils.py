def iterations_back_till_condition(series, condition):
    count = 0
    for value in series[::-1]:
        # print(f'value: {value}')
        if condition(value):
            # print(f'Condition met at index {value}')
            break
        count += 1
    return count