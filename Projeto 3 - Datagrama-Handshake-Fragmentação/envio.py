#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################

'''
HEADER:

0: Tipo de mensagem (1 - handshake | 2 - confirmação handshake | 3 - envio de pacote | 4 - confirmação pacote | 5 - finalizar)
1: Número do Pacote
2: Quantidade de pacotes
3: Tamanho do Payload
4: Confirmação -> deu certo 1, deu errado 0
5: Qual pacote deu erro? -> 0, se não deu
6: 0
7: 0
8: 0
9: 0

'''


from enlace import *
import time
import random

import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

#   python -m serial.tools.list_ports
serialName = "COM3"                  # Windows(variacao de)

# Definição do número de bytes de cada uma das partes do datagrama
size_header = 10
size_payload = 114 # no maximo
size_end_of_package = 4


def number_of_packages(size):
    division = int(size / size_payload)
    rest = size % size_payload

    if rest != 0:
        packages = division + 1
        last_payload = rest
    else:
        packages = division
        last_payload = 114

    return packages, last_payload

def transform_to_bytes(number):
    return int(number).to_bytes(1, byteorder='big')

def transform_to_int(byte):
    return int.from_bytes(byte, byteorder='big')

def headerHandshake(packages):
    qtde_packages = transform_to_bytes(packages)
    type_ = transform_to_bytes(1)
    zero = transform_to_bytes(0)
    header = type_ + zero + qtde_packages + zero * 7
    return header

def see_error(header, eop):
    error = False

    if len(header) != size_header:
        print("Há um erro no tamanho do header")
        error = True
    if len(eop) != size_end_of_package:
        print("Há um erro no tamanho do EOP")
        error = True

    return error

def EOP():
    zero = transform_to_bytes(0)
    eop = zero * size_end_of_package
    # b'\x00\x00\x00\x00'
    return eop

def define_header(type_, package_actual, packages, size_payload):
    tipo = transform_to_bytes(type_)
    package_actual = transform_to_bytes(package_actual)
    number = transform_to_bytes(packages)
    size = transform_to_bytes(size_payload)
    zero = transform_to_bytes(0)

    header = tipo + package_actual + number + size + zero*6
    # print("\n o header que enviarei é:", header)

    return header


def main():
    one = False
    try:
        com = enlace(serialName)
    
        com.enable()

        print("Comunicação de Envio aberta!\n")
        
        Tk().withdraw()
        image = askopenfilename() 

        #txBuffer = imagem em bytes!
        # image = './img/teste1.png'

        txBuffer =  open(image, 'rb').read()
        print("Imagem transformada com sucesso!\n")
        time.sleep(0.1)

        size_txBuffer = len(txBuffer)
        print("O arquivo a ser enviado possui {} bytes\n".format(size_txBuffer))

        packages, last_payload = number_of_packages(size_txBuffer) 

        print("O número de pacotes do arquivo a ser enviado é {}".format(packages))
        print("O último payload tem tamanho: {} bytes\n".format(last_payload))     

        eop_data = EOP()
        init_completed = False

        while not init_completed:

            # 1º envio: HANDSHAKE
            print("Para começar, vou enviar o Handshake!")
            hand_header = headerHandshake(packages)
            com.sendData(hand_header + eop_data)
            time.sleep(0.1)

            # Aguardando a confirmação do cliente
            confirmation_header_handshake = com.rx.getNData(size_header)
            while confirmation_header_handshake == b'\x00':
                try_again = input("Servidor inativo. Tentar novamente? S/N: ")
                if try_again == "S":
                    print("Ok, vamos tentar novamente. Enviando handshake...\n")
                    hand_header = headerHandshake(packages)
                    com.sendData(hand_header + eop_data)
                    time.sleep(0.1)
                    confirmation_header_handshake = com.rx.getNData(size_header)
                else:
                    print("Ok, finalizando comunicação.")
                    com.disable()
                    exit()

            confirmation_eop_handshake = com.rx.getNData(size_end_of_package)

            if see_error(confirmation_header_handshake, confirmation_eop_handshake):
                print("Há um erro na comunicação inicial")
                init_completed = False
            else:
                if transform_to_int(confirmation_header_handshake[0:1]) == 2:
                    print("Server autorizou. Começar a transmissão!")
                    init_completed = True
        
        last_again = False
        send_all_packages = False
        last = False
        index_data1 = 0
        number_package = 1
        while not send_all_packages:
            # print(index_data1)
            time.sleep(0.01)
            print("Enviando o pacote {}...\n".format(number_package))
            time.sleep(2)
            if number_package == packages:
                last = True

            if not last:
                data = txBuffer[index_data1 : index_data1+size_payload]
                header = define_header(3, number_package, packages, size_payload)
                com.sendData(header + data + eop_data)
                time.sleep(0.1)

            else:
                data = txBuffer[index_data1 : index_data1+last_payload]
                header = define_header(3, number_package, packages, last_payload)     
                if not one:  
                    com.sendData(header + data + b'\xFF' + eop_data)
                    one = True
                else: 
                    com.sendData(header + data + eop_data)
                    if transform_to_int(ans_head[4:5]) == 1:
                        send_all_packages = True
                time.sleep(0.1)

                ans_head = com.rx.getNData(size_header)
                while ans_head == b'\x00':
                    ans_head = com.rx.getNData(size_header)
                ans_payload = com.rx.getNData(0)
                ans_eop = com.rx.getNData(size_end_of_package)

                print("Enviei o último pacote {}. Agora vou esperar". format(number_package))
                ans_head = com.rx.getNData(size_header)
                while ans_head == b'\x00':
                    ans_head = com.rx.getNData(size_header)
                ans_payload = com.rx.getNData(0)
                ans_eop = com.rx.getNData(size_end_of_package)

                if transform_to_int(ans_head[4:5]) == 0:
                    last_again = True
                else:
                    send_all_packages = True

            print("Enviei o pacote {}. Agora vou esperar\n". format(number_package))
            if last_again == False:
                ans_head = com.rx.getNData(size_header)
                while ans_head == b'\x00':
                    ans_head = com.rx.getNData(size_header)
                ans_payload = com.rx.getNData(0)
                ans_eop = com.rx.getNData(size_end_of_package)

            if see_error(ans_head, ans_eop):
                print(ans_head)
                print(ans_eop)
                print("Deu erro no EOP")
            
            else:
                # print("header: ", ans_head)
                # print("eop: ", ans_eop)
                if transform_to_int(ans_head[4:5]) == 1:
                    print("Hm, houve um erro. Vou enviar o pacote novamente")
                    new = transform_to_int(ans_head[5:6])
                    number_package = new+1
                    if number_package == 3:
                        number_package -= 1
                    print(number_package)

                else:
                    print("Enviou certo. Próximo\n")
                    index_data1 += size_payload
                    new = transform_to_int(ans_head[5:6])
                    number_package = new + 1
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com.disable()
    except Exception as ex:
        print(ex)
        print("bye! ;)")
        com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
