from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from core.models import Lines, Registers
from .div_calc2 import get_multiplier, get_secondary_get_multiplier

import time

debug_mode = False

status = ['OK']

if not debug_mode:
    import Adafruit_BBIO.SPI as SPI  # Библиотеку Adafruit_BBIO надо будет ещё
                                     # скачать через pip


# Настроим наш SPI

if not debug_mode:
    spi = SPI.SPI(1,0)  # Используем SPI 1 (он же SPI 0, нумерация с 1)
    spi.msh = 1000000  # По-умолчанию тут 16 000 000
    spi.mode = int('11', 2)
    spi.cshigh = False

set_adr = 0  # Команда на считывание адреса
set_write = int('01000000',2)  # Запись в регистр
set_inc_write = int('01100000',2)  # Запись с инкрементом адреса регистра
first_adr = 0  # Самый первый номер регистра


#_______________________________________ Functions-helpers
def is_integer(n):
    try:
        int(n)
        return True
    except ValueError:
        return False


def format_int(x):
    return format(x, '02x') + 'h'


def invert_int(x):
    return ~x&255


def make_ICAL():
    spi.writebytes([set_adr, 136])  # Установка очередного адреса
    spi.writebytes([set_write, 64])  # ICAL
#_______________________________________


def init():  # Запуск
    reg = Registers.objects.all()
    for i in reg:

        spi.writebytes([set_adr, i.id])  # Установка очередного адреса
        spi.writebytes([set_write, int(i.value[0:2], 16)])

    return

if not debug_mode:
    init()


def install_default(request):  # Сброс настроек в исходные
    content = Lines.objects.all()
    reg = Registers.objects.all()
    global status

    #  Запись во внешний вид интерфейса
    for i in content:
        i.input_freq = i.default_input_freq
        i.output_freq = i.default_output_freq
        i.status = i.default_status
        i.save()

    spi.writebytes([set_adr, 136])  # Установка очередного адреса
    spi.writebytes([set_write, 128]) # Reset
    status = ['Reset']

    time.sleep(1)

    #time.sleep(0.1)

    for i in reg:

        spi.writebytes([set_adr, i.id])  # Установка очередного адреса
        spi.writebytes([set_write,int(i.default_value[0:2], 16)])
        i.value = i.default_value
        i.save()

    status = ['Default: 1 MHz + ICAL']

    return render(request, 'core/Create_tmpl.html', {'Lines': content})


def show_main_page(request):  # Используется при загрузке страницы
    global status
    content = Lines.objects.all()
    status = ['OK']
    return render(request, 'core/Main_page.html', {'Lines':content})


def refresh_page(request):  # Обновляет меняющуюся часть страницы. Для ПОЛНОЙ перезагрузи страницы исп. show_main_page
    global status
    content = Lines.objects.all()
    status = ['OK']
    return render(request, 'core/Create_tmpl.html', {'Lines':content}) #redirect('show_main_page')

######################################## Functions-helpers


def helper_edit_line_write_regs(reg):
    for i in reg:
        spi.writebytes([set_adr, i])  # Установка очередного адреса
        spi.writebytes([set_write, reg[i]])


def helper_edit_line_write_bd(reg):
    for i in reg:
        j = Registers.objects.filter(id=i)[0]
        j.value = format_int(reg[i])
        j.save()


def helper_edit_line_get_N1_LS():
    step = 1  # 0 is 1, 1 is 2, 2 is 3. but 0 + step is 1
    reg = {}
    reg[25] = 0
    reg[26] = 0
    reg[27] = 0
    for i in reg:
        reg[i] = int(Registers.objects.filter(id=i)[0].value[:-1], 16)

    reg[26] = reg[26] << 8
    reg[25] = (reg[25] & 0xF) << 16

    return sum(reg.values()) + step
##########################################


def edit_line(request):  # Отправка данный в синтезатор

    global status
    #print('\n\n\n\n\n' + str(request.GET) + '\n\n\n\n\n')
    edit = Lines.objects.filter(id=int(request.GET['edit']))[0]
    temp = request.GET
    line = int(request.GET['edit'])

    if (is_integer(temp['input_freq']) != True) or (is_integer(temp['output_freq']) != True):
        edit.status = 'Ошибка ввода'
        edit.save()

    else:
        edit.input_freq = int(temp['input_freq'])
        edit.output_freq = int(temp['output_freq'])
        edit.status = 'Активно'
        edit.save()

    if line == 1:  # Main channel
        res = get_multiplier(temp['output_freq'], temp['input_freq'])
        reg = {}
        if res[1]['status']:
            reg[25] = 0
            reg[26] = 0
            reg[27] = 0
            reg[25] |= res[0]['N1_HS'] << 5
            reg[25] |= int(format(res[0]['N1_LS'], '020b')[0:4], 2)
            reg[26] |= int(format(res[0]['N1_LS'], '020b')[4:12], 2)
            reg[27] |= int(format(res[0]['N1_LS'], '020b')[12:], 2)

            reg[40] = 0
            reg[41] = 0
            reg[42] = 0
            reg[40] |= res[0]['N2_HS'] << 5
            reg[40] |= int(format(res[0]['N2_LS'], '020b')[0:4], 2)
            reg[41] |= int(format(res[0]['N2_LS'], '020b')[4:12], 2)
            reg[42] |= int(format(res[0]['N2_LS'], '020b')[12:], 2)

            reg[43] = 0
            reg[44] = 0
            reg[45] = 0
            reg[43] |= int(format(res[0]['N3'], '019b')[0:3], 2)
            reg[44] |= int(format(res[0]['N3'], '019b')[3:11], 2)
            reg[45] |= int(format(res[0]['N3'], '019b')[11:], 2)

            helper_edit_line_write_regs(reg)
            make_ICAL()
            helper_edit_line_write_bd(reg)

            status = res

        else:
            status = 'Failed'

    else:
        res = get_secondary_get_multiplier(main_fr_out=Lines.objects.filter(id=1)[0].output_freq,
                                           sec_fr_out=edit.output_freq,
                                           main_N1_LS=helper_edit_line_get_N1_LS())
        reg = {}
        if res[1]['status']:
            reg[25 + 3 * (line - 1)] = 0
            reg[26 + 3 * (line - 1)] = 0
            reg[27 + 3 * (line - 1)] = 0
            reg[25 + 3 * (line - 1)] |= int(format(res[0]['N1_LS'], '020b')[0:4], 2)
            reg[26 + 3 * (line - 1)] |= int(format(res[0]['N1_LS'], '020b')[4:12], 2)
            reg[27 + 3 * (line - 1)] |= int(format(res[0]['N1_LS'], '020b')[12:], 2)

            helper_edit_line_write_regs(reg)
            make_ICAL()
            helper_edit_line_write_bd(reg)

            status = res
        else:
            status = 'Failed'

    content = Lines.objects.all()
    return render(request, 'core/Create_tmpl.html', {'Lines':content})


def stop_line(request):  # Подача 0 на выход синтезатора
    stopped = Lines.objects.filter(id=int(request.GET['stop']))[0]
    stopped.status = 'Остановлено'
    stopped.save()
    content = Lines.objects.all()
    return render(request, 'core/Create_tmpl.html', {'Lines':content}) #redirect('show_main_page')


def AJAX_test(request):  # Вывод сообщений

    return HttpResponse(str(status))


def turn_on(request):  # Регистр включения-выключения выходного делителя
    content = Lines.objects.filter(id=int(request.GET['edit']))[0]
    temp = int(Registers.objects.filter(id=10)[0].value[:2], 16)
    #print(temp)
    if request.GET['turn_on'] == 'true':
        content.turn_on = 1
    else:
        content.turn_on = 0
    #print(content.turn_on)
    content.save()
    if content.turn_on == 0:
        one = 1 << (int(request.GET['edit'])-1)
        #print(one)
        temp |= one
        #print(temp)

        reg = Registers.objects.filter(id=10)[0]
        reg.value = format_int(temp)
        reg.save()
    else:
        zero = invert_int(1 << (int(request.GET['edit'])-1))
        #print(zero)
        temp &= zero
        #print(temp)

        reg = Registers.objects.filter(id=10)[0]
        reg.value = format_int(temp)
        reg.save()
    #print(temp)
    spi.writebytes([set_adr, 10])  # адрес DSBL5_REG
    spi.writebytes([set_write, temp])
    return HttpResponse()
