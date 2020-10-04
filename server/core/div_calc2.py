from decimal import Decimal
from fractions import Fraction

def get_multiplier(fr_out: str, fr_in: str = '20000000', delta: float = 0.0001, des_error: float = 0.1, max_error: float = 20, divider_limit : float = 10):
    flag = True
    res = {'N1_HS':4, 'N1_LS':1, 'N2_HS':4, 'N2_LS':1, 'N3':1}
    # des_error - желаемая ошибка
    # delta - шаг при подборе числа, большой -- плохо, маленький -- долго

    fr_in = Decimal(fr_in)  # Специальный класс для точного расчёта
    fr_out = Decimal(fr_out)

    res = Fraction(fr_out/fr_in).limit_denominator()  # Ищем наименьшую дробь
    #print('Результат 1:', res)

    num = res.numerator  # Промежеточные переменные
    den = res.denominator

    i = 1
    j = 1 + delta  # Счётчики

    # Быстрый алгоритм, но грубый

    while (num > 2**20) or (den > 2**39):
        num = res.numerator / i
        den = res.denominator / i
        i += 1

    if den > 2**20:
        print('Algorithm needs to be more advanced')

    res = {'N1_HS': 1, 'N1_LS': 1, 'N2_HS': 1, 'N2_LS': num, 'N3': den}

    num1 = num  # Ещё одни промежуточные переменные
    den1 = den

    # Медленный алгоритм
    temp = 1
    while abs(fr_out - fr_in * round(num)/(round(den))) > temp * des_error:
        num = num1 / j
        den = den1 / j
        j += delta
        if j > divider_limit:
            j = 1
            temp += 1
            num = num1
            den = den1
            if temp * des_error > max_error:
                print('Calculation failed!')
                flag = False
                break

    res = {'N1_HS': 1, 'N1_LS': 1, 'N2_HS': 1, 'N2_LS': num, 'N3': den}

    temp = res.copy()


    while not (4.85 * 10**9 < (float(fr_in) * temp['N2_HS'] * temp['N2_LS'] / temp['N3']) <= 5.67 * 10**9):

        temp['N1_LS'] += 1
        temp['N3'] = res['N3'] / temp['N1_LS']

    res = {'N1_HS': 4, 'N1_LS': temp['N1_LS'], 'N2_HS': 4, 'N2_LS': round(num), 'N3': round(temp['N3'])}

    freq = float(fr_in) * res['N2_HS'] * res['N2_LS'] / (res['N1_HS'] * res['N1_LS'] * res['N3'])
    err = float(fr_out) - freq
    # Проверим наш код
    if __name__ == '__main__':
        print('N1_HS =', res['N1_HS'])
        print('N1_LS =', res['N1_LS'])
        print('N2_HS =', res['N2_HS'])
        print('N2_LS =', res['N2_LS'])
        print('N3 =', res['N3'])
        freq = float(fr_in) * res['N2_HS'] * res['N2_LS'] / (res['N1_HS'] * res['N1_LS'] * res['N3'])
        print('Заданная частота =', fr_out)
        print('Фактическая частота = ', freq)
        print('Отклонение', err)
        print('Для отладки, j =', j)



    return [res, {'freq':freq, 'err':err, 'status': flag}]


if __name__ == '__main__':
    get_multiplier('600'+'342'+'200')
    '''
    for i in range(3*10**6,10**7):
        a = get_multiplier(str(i))
        print(i, a[1]['err'])
        if abs(a[1]['err']) >= 20:
            break
    '''