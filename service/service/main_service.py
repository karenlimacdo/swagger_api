from logging import log
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
        
        #df_response = pd.DataFrame(response_predicts, columns=1)
        df_response['predict'] = response_predicts

        df_response = df_response.drop(columns=['textoMensagem'])

        response = {
                     "listaRespostas": json.loads(df_response.to_json(
                                                                            orient='records', force_ascii=False))}

        return response


    def calcular(self, texts):
        """
        Pega o modelo carregado e aplica em texts
        """
        logger.debug('Iniciando as operações...')

        response = []
        op = []
        d = deque(texts)

        # enquanto a fila não estiver vazia
        while (len(d)>=1):
            # text é igual ao primeiro da fila
            text = d[0]
            # se text é inteiro
            if(str(text).isdigit()):
                # se a fila possui apenas uma variável
                if(len(d)==1):
                    # se a lista de operandos está vazia, chegamos ao
                    # resultado final, caso contrário, temos um número
                    # errado de operandos
                    if(len(op)==0):
                        response.append(text)
                        return response
                    else:
                        response.append(mensagens.ERROR_OP)
                        return response
                # caso contrário, insere na lista de operandos
                else:
                    op.append(int(text))
                    response.append(text)
                    d.popleft()
            # se text é float
            elif(str(text).replace('.','',1).isdigit()):
                if(len(d)==1):
                    if(len(op)==0):
                        response.append(text)
                        return response
                    else:
                        response.append(mensagens.ERROR_OP)
                        return response
                else:
                    op.append(float(text))
                    response.append(text)
                    d.popleft()
            # se text não é inteiro nem float, é um operador ou
            # símbolo não suportado
            else:
                if(text=="*" or text=="multiplicar"):
                    if(len(op)==2):
                        d.popleft()
                        res = op[0]*op[1]
                        d.appendleft(str(res))
                        if(len(d)>1):
                            response.append(text)
                        op = []
                    else:
                        response.append(mensagens.ERROR_OP)
                        return response
                elif(text=="+" or text=="somar"):
                    if(len(op)==2):
                        d.popleft()
                        res = op[0]+op[1]
                        d.appendleft(str(res))
                        op = []
                    else:
                        response.append(mensagens.ERROR_OP)
                        return response
                elif(text=="-" or text=="subtrair"):
                    if(len(op)==2):
                        d.popleft()
                        res = op[0]-op[1]
                        d.appendleft(str(res))
                        op = []
                    else:
                        response.append(mensagens.ERROR_OP)
                        return response
                elif(text=="/" or text=="dividir"):
                    if(len(op)==2):
                        d.popleft()
                        res = op[0]/op[1]
                        d.appendleft(str(res))
                        op = []
                    else:
                        response.append(mensagens.ERROR_OP)
                        return response
                elif(text=="ˆ" or text=="potenciação"):
                    if(len(op)==1):
                        d.popleft()
                        res = op[0]*op[0]
                        d.appendleft(str(res))
                        op = []
                    else:
                        response.append(mensagens.ERROR_OP)
                        return response
                elif(text=="%" or text=="módulo"):
                    if(len(op)==2):
                        d.popleft()
                        res = op[0]%op[1]
                        d.appendleft(str(res))
                        op = []
                    else:
                        d.popleft()
                        response.append(mensagens.ERROR_OP)
                        return response
                else:
                    d.popleft()
                    response.append(mensagens.ERROR_OP)
                    return response    
        
        if(len(d)==0 and len(op)>=1):
            response.append(mensagens.ERROR_OP)

        return response
