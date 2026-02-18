import datetime
import calendar
import random

def gera_senha(tamanho):
    """
    Função que gera uma senha de tamanho X
    :param tamanho: Tamanho da senha
    :return: Senha em texto
    """
    letras = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    caracteres = '!@#$%&-'
    digitos = '012345689'
    geral = letras + caracteres + digitos
    return "".join(random.choices(geral, k=tamanho))


def so_numeros(texto):
    """
    Função que retorna só os numeros de um texto
    :param texto:
    :return: texto somente com os numeros
    """
    return ''.join(caractere for caractere in texto if caractere.isdigit())


def dia_da_semana(dia):
    """
    Função que entrando uma dia da Semana 0 = segunda .... 7 domingo
    :param dia: 0 = segunda .... 7 domingo
    :return: texto de dia da semana
    """
    dias = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
    return dias[dia]

def datas_do_mes(ano: int, mes: int):
    """
    Função de retorna a data inicial e final do mês
    :param ano: Numero do ano com 4 digitos
    :param mes: Numero do mês de 1 a 12
    :return: Data Inicial e Final
    """
    # Primeiro dia do mês
    data_inicial = datetime.date(ano, mes, 1)
    # Último dia do mês (usando calendar.monthrange)
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_final = datetime.date(ano, mes, ultimo_dia)
    return data_inicial, data_final