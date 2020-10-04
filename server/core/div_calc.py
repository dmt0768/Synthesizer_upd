from decimal import Decimal
from fractions import Fraction

def get_multiplier(fr_out: str, fr_in: str = '20000000', delta: float = 0.0001, des_error: float = 0.1, max_error: float = 30, divider_limit : float = 5):
    flag = True

    # des_error - желаемая ошибка
    # delta - шаг при подборе числа, большой -- плохо, маленький -- долго

    fr_in = Decimal(fr_in)  # Специальный класс для точного расчёта
    fr_out = Decimal(fr_out)

    res = Fraction(fr_out/fr_in).limit_denominator()  # Ищем наименьшую дробь

    num = res.numerator  # Промежеточные переменные
    den = res.denominator

    i = 1

    # Быстрый алгоритм, но грубый
    if (num > 2**20) or (den > 2**39):
        while (num > 2**20) or (den > 2**39):
            num = res.numerator / 2**i
            den = res.denominator / 2**i
            i += 0.1
    else:
        while (num < 2**20 - 1000) and (den < 2**39 - 1000):
            num = res.numerator * 2**i
            den = res.denominator * 2**i
            i += 0.1

    res = {'N1_HS': 4, 'N1_LS': 1, 'N2_HS': 4, 'N2_LS': 1, 'N3': 1}
    res['N2_LS'] = num / res['N2_HS']
    res['N3'] = den / res['N1_HS']

    temp = res.copy()

    while not (4.9 * 10**9 < (float(fr_in) * temp['N2_HS'] * temp['N2_LS'] / temp['N3']) <= 5.63 * 10**9):
        if temp['N1_HS'] == 11:
            temp['N1_HS'] = 4

            if temp['N1_LS'] == 1:
                temp['N1_LS'] += 1
            else:
                temp['N1_LS'] += 2

        temp['N1_HS'] += 1
        temp['N3'] = res['N3'] / (temp['N1_HS'] / 4) / temp['N1_LS']  # Тут мы окончательно определяем N1_LS, дальше работаем с с N3 и N2

        if temp['N3'] < 2:
            flag = 'PLL out frequency calculation failed!'
            break

    res = temp.copy()

    # Медленный алгоритм
    j = 1 + delta
    k = 1
    while (abs(float(fr_out) - float(fr_in) * res['N2_HS'] * round(res['N2_LS']) / (res['N1_HS'] * res['N1_LS'] * round(res['N3']))) > k * des_error) or (round(res['N2_LS']) % 2):
        res['N2_LS'] = temp['N2_LS'] / j
        res['N3'] = temp['N3'] / j
        j += delta
        if j > divider_limit:
            j = 1
            k *= 2
            res['N2_LS'] = temp['N2_LS']
            res['N3'] = temp['N3']
            if k * des_error > max_error:
                flag = 'Fine calculation failed!'
                break

    res = {'N1_HS': round(res['N1_HS']), 'N1_LS': round(res['N1_LS']), 'N2_HS': round(res['N2_HS']), 'N2_LS': round(res['N2_LS']), 'N3': round(res['N3'])}

    #  Финальная проверка делителей
    if flag:
        if not (4 <= res['N1_HS'] <= 11):
            flag = 'Divider test №1 failed!'
        if not (1 <= res['N1_LS'] <= 2**20) and ((res['N1_LS'] % 2 == 0) or res['N1_LS'] == 1):
            flag = 'Divider test №2 failed!'
        if not (4 <= res['N2_HS'] <= 11):
            flag = 'Divider test №3 failed!'
        if not ((2 <= res['N2_LS'] <= 2**20) and res['N2_LS'] % 2 == 0):
            flag = 'Divider test №4 failed!'
        if not (1 <= res['N3'] <= 2**19):
            flag = 'Divider test №5 failed!'

        #  Финальная проверка внутренних частот
        if not (2 * 10**3 < (float(fr_in) / res['N3']) < 2 * 10**6):
            flag = 'PLL in frequency test failed!'

        if not (4.85 * 10 ** 9 < (float(fr_in) * temp['N2_HS'] * temp['N2_LS'] / temp['N3']) <= 5.67 * 10 ** 9):
            flag = 'PLL out frequency test failed!'

    freq = float(fr_in) * res['N2_HS'] * res['N2_LS'] / (res['N1_HS'] * res['N1_LS'] * res['N3'])
    err = float(fr_out) - freq

    #  Подготовка к отправке
    #  Учтём, например, что 0 в регистре N1_HS означает -- 4 в делителе

    res['N1_HS'] = res['N1_HS'] - 4
    res['N1_LS'] = res['N1_LS'] - 1
    res['N2_HS'] = res['N2_HS'] - 4
    res['N2_LS'] = res['N2_LS'] - 1
    res['N3'] = res['N3'] - 1

    # Проверим наш код
    if __name__ == '__main__':
        print('N1_HS =', res['N1_HS'])
        print('N1_LS =', res['N1_LS'])
        print('N2_HS =', res['N2_HS'])
        print('N2_LS =', res['N2_LS'])
        print('N3 =', res['N3'])

        print('Заданная частота =', fr_out)
        print('Фактическая частота = ', freq)
        print('Отклонение', err)
        print('Для отладки, j =', j)
        print('Статус:', flag)

    return [res, {'freq':freq, 'err':err, 'status': flag}]

if __name__ == '__main__':
    get_multiplier('1'+'000'+'000')
