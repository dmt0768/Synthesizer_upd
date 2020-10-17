from decimal import Decimal
from fractions import Fraction

def get_multiplier(fr_out: str, fr_in: str = '20000000', delta: float = 0.0001, des_error: float = 0.1, max_error: float = 30, divider_limit : float = 5, cheat : int = 1):
    flag = True

    # des_error - желаемая ошибка
    # delta - шаг при подборе числа, большой -- плохо, маленький -- долго

    fr_in = Decimal(fr_in)  # Специальный класс для точного расчёта
    fr_out = Decimal(fr_out)

    res = Fraction(fr_out/fr_in).limit_denominator()  # Ищем наименьшую дробь (2 * 10**3 < float(fr_in) / (res.denominator * 2**i / res['N1_HS']) < 2 * 10**6)



    # Быстрый алгоритм, но грубый
    def fast_alg(num, den):
        i = 1
        if (num > cheat*2**20) or (den > cheat*2**39):
            while (num > cheat*2**20) or (den > cheat*2**39):
                num = res.numerator / 2**i
                den = res.denominator / 2**i
                i += 0.1
        else:
            while (num < cheat*2**20) and (den < cheat*2**39):

                num = res.numerator * 2**i
                den = res.denominator * 2**i
                i += 0.1
        return num, den

    temp = fast_alg(res.numerator, res.denominator)

    res = {'N1_HS': 4, 'N1_LS': 1, 'N2_HS': 4, 'N2_LS': 1, 'N3': 1}
    res['N2_LS'] = temp[0] / res['N2_HS']
    res['N3'] = temp[1] / res['N1_HS']


    def PLL_out_alg(dictionary):
        N1_HS = dictionary['N1_HS']
        N1_LS = dictionary['N1_LS']
        N2_HS = dictionary['N2_HS']
        N2_LS = dictionary['N2_LS']
        N3 = dictionary['N3']
        nonlocal flag
        const_N3 = N3
        while not (4.9 * 10**9 < (float(fr_in) * N2_HS *  N2_LS / N3) <= 5.63 * 10**9):
            if N1_HS == 11:
                N1_HS = 4

                if N1_LS == 1:
                    N1_LS += 1
                else:
                    N1_LS += 2

            N1_HS += 1
            N3 = const_N3 / (N1_HS / 4) / N1_LS  # Тут мы окончательно определяем N1_LS, дальше работаем с с N3 и N2

            if N3 < 2:
                flag = 'PLL out frequency calculation failed!'
                break
        return {'N1_HS': N1_HS, 'N1_LS': N1_LS, 'N2_HS': N2_HS, 'N2_LS': N2_LS, 'N3': N3}

    res = PLL_out_alg(res)
    temp = res.copy()

    def increase_N3_alg(dictionary):
        N1_HS = dictionary['N1_HS']
        N1_LS = dictionary['N1_LS']
        N2_HS = dictionary['N2_HS']
        N2_LS = dictionary['N2_LS']
        N3 = dictionary['N3']
        const_N3 = N3
        while (N3 * (N2_HS+1) / 4 < N2_LS) and (N2_HS <= 10) and (2 * 10**3 < (float(fr_in) / N3) < 2 * 10**6):
            N2_HS += 1
            N3 = const_N3 * N2_HS / 4
        return {'N1_HS': N1_HS, 'N1_LS': N1_LS, 'N2_HS': N2_HS, 'N2_LS': N2_LS, 'N3': N3}

    res = increase_N3_alg(res)
    temp = res.copy()
    freq = float(fr_in) * res['N2_HS'] * res['N2_LS'] / (res['N1_HS'] * res['N1_LS'] * res['N3'])
    print(float(fr_out) - freq)

    # Медленный алгоритм
    def slow_alg(dictionary):
        N1_HS = dictionary['N1_HS']
        N1_LS = dictionary['N1_LS']
        N2_HS = dictionary['N2_HS']
        N2_LS = dictionary['N2_LS']
        N3 = dictionary['N3']
        nonlocal flag
        const_N2_LS = N2_LS
        const_N3 = N3
        j = 1 + delta
        k = 1
        while (abs(float(fr_out) - float(fr_in) * N2_HS * round(N2_LS) / (N1_HS * N1_LS * round(N3))) > k * des_error) or (round(N2_LS) % 2):

            N2_LS = const_N2_LS / j
            N3 = const_N3 / j
            j += delta
            if j > divider_limit:
                j = 1
                k *= 2
                N2_LS = const_N2_LS
                N3 = const_N3
                if k * des_error > max_error:
                    flag = 'Fine calculation failed!'
                    break

        return {'N1_HS': N1_HS, 'N1_LS': N1_LS, 'N2_HS': N2_HS, 'N2_LS': N2_LS, 'N3': N3}


    if flag == True:
        res = slow_alg(res)

        res = {'N1_HS': round(res['N1_HS']), 'N1_LS': round(res['N1_LS']), 'N2_HS': round(res['N2_HS']), 'N2_LS': round(res['N2_LS']), 'N3': round(res['N3'])}

    #  Финальная проверка делителей

    if flag == True:
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
        print('Статус:', flag)

    return [res, {'freq':freq, 'err':err, 'status': flag}]

if __name__ == '__main__':
    get_multiplier('555'+'555'+'000')
