import time
import json
from loguru import logger
from service.constants import mensagens
import pandas as pd
from collections import deque


class CalcService():

    def __init__(self):
        logger.debug(mensagens.INICIO_LOAD_CALC)
        self.load_calc()

    def load_calc(self):
        """"
        Carrega a calculadora
        """

        logger.debug(mensagens.FIM_LOAD_CALC)

    def is_number(value):
        try:
            float(value)
        except ValueError:
            return False
        return True

    def executar_rest(self, texts):
        response = {}

        logger.debug(mensagens.INICIO_OP)
        start_time = time.time()

        response_predicts = self.calcular(texts['textoMensagem'])

        logger.debug(mensagens.FIM_OP)
        logger.debug(f"Fim de todas as operações em {time.time()-start_time}")

        df_response = pd.DataFrame(texts, columns=['textoMensagem'])

        df_response['predict'] = response_predicts

        df_response = df_response.drop(columns=['textoMensagem'])

        response = {
                     "listaRespostas": json.loads(df_response.to_json(
                                                                            orient='records', force_ascii=False))}

        return response

    # Calculadora pós-fixa de números inteiros e de ponto flutuante, realiza as seguinte operações
    #   - Multiplicação (digitar * ou multiplicar)
    #   - Soma (digitar + ou somar)
    #   - Subtração (digitar - ou subtrair)
    #   - Divisão (digitar / ou dividir)
    #   - Potenciação (digitar ˆ ou potenciacao)
    #   - Módulo (digitar % ou modulo)
    # Exemplos para teste:
        # infixa                                  | pós-fixa                | resultado
        # 5 * ( ( ( 9 + 8 ) * ( 4 * 6 ) ) + 7 )   | 5 9 8 + 4 6 * * 7 + *   | 2075
        # 5 * ( ( ( 9 - 8 ) * ( 4 * 6 ) ) + 7 )   | 5 9 8 - 4 6 * * 7 + *   | 155
        # 5 * ( ( ( 9 + 8 ) * ( 4 ˆ 6 ) ) + 7 )   | 5 9 8 + 4 6 ˆ * 7 + *   | 348195
        # 5 * ( ( ( 9 / 0 ) * ( 4 * 6 ) ) + 7 )   | 5 9 0 / 4 6 * * 7 + *   | divisão por zero
        # 5 * ( ( ( 10 % 2 ) * ( 4 * 6 ) ) + 7 )  | 5 10 2 % 4 6 * * 7 + *  | 35
        # 5 * ( ( ( 10 9 + 8 ) * ( 4 * 6 ) ) + 7 )| 5 10 9 8 + 4 6 * * 7 + *| número errado de operandos
        # 5 * ( ( ( + 8 ) * ( 4 * 6 ) ) + 7 )     | 5 8 + 4 6 * * 7 + *     | número errado de operandos
        # 5.5 * ( ( ( 9 + 8 ) * ( 4 * 6 ) ) + 7 ) | 5.5 9 8 + 4 6 * * 7 + * | 2282.5
        # "5 9 8 + 4 6 * * 7 + *", "5 9 8 - 4 6 * * 7 + *", "5 9 8 + 4 6 ˆ * 7 + *", "5 9 0 / 4 6 * * 7 + *", "5 10 2 % 4 6 * * 7 + *", "5 10 9 8 + 4 6 * * 7 + *", "5 8 + 4 6 * * 7 + *", "5.5 9 8 + 4 6 * * 7 + *"
        # "5 9 8 somar 4 6 * * 7 + *", "5 9 8 subtrair 4 6 multiplicar * 7 + *", "5 9 8 + 4 6 potenciacao * 7 + *", "5 9 0 / 4 6 * * 7 + *", "5 10 2 modulo 4 6 * * 7 + *", "5 10 9 8 + 4 6 * * 7 + *", "5 8 + 4 6 * * 7 + *", "5.5 9 8 + 4 6 * * 7 + *"
    def calcular(self, texts):
        """
        Pega o modelo carregado e aplica em texts
        """
        logger.debug('Iniciando as operações...')

        response = []
        op = []
        for form in texts:
            op = form.split(' ')
            d = deque()
            err = False

            for text in op:
                # se text é inteiro
                if(str(text).isdigit()):
                    logger.debug(text)
                    d.append(int(text))
                # se text é float
                elif(str(text).replace('.', '', 1).isdigit()):
                    logger.debug(text)
                    d.append(float(text))
                else:
                    if(len(d) >= 2):
                        if(text == "*" or text == "multiplicar"):
                            res = d.pop()*d.pop()
                            d.append(res)
                        elif(text == "+" or text == "somar"):
                            res = d.pop()+d.pop()
                            d.append(res)
                        elif(text == "-" or text == "subtrair"):
                            op2 = d.pop()
                            op1 = d.pop()
                            res = op1-op2
                            d.append(res)
                        elif(text == "/" or text == "dividir"):
                            op2 = d.pop()
                            op1 = d.pop()
                            if(op2 == 0):
                                err = True
                                break
                            else:
                                res = op1/op2
                                d.append(res)
                        elif(text == "ˆ" or text == "potenciacao"):
                            op2 = d.pop()
                            op1 = d.pop()
                            res = op1**op2
                            d.append(res)
                        elif(text == "%" or text == "modulo"):
                            op2 = d.pop()
                            op1 = d.pop()
                            if(op2 == 0):
                                err = True
                                break
                            else:
                                res = op1 % op2
                                d.append(res)
                        else:
                            err = True
                            break
                    else:
                        err = True
                        break

            # se a pilha não tem somente o resultado como elemnto, há um número errado
            # de operadores ou operandos então o erro é reportado
            if(len(d) != 1 or err):
                response.append(mensagens.ERROR_OP)
            else:
                response.append(d.pop())

        return response
