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
    return eop

def define_header(type_, package_actual, packages, size_payload):
    tipo = transform_to_bytes(type_)
    package_actual = transform_to_bytes(package_actual)
    number = transform_to_bytes(packages)
    size = transform_to_bytes(size_payload)
    zero = transform_to_bytes(0)

    header = tipo + package_actual + number + size + zero*6

    return header



def main():
    try:
        com = enlace(serialName)
    
        com.enable()

        print("Comunicação de Envio aberta!\n")
        
        #txBuffer = imagem em bytes!
        image = './img/image.png'

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

        # tempo = time.time()
        while not init_completed:
            # tempo2 = time.time() -> tem que fazer algo com o tempo que não consegui (5 segundos)

            # 1º envio: HANDSHAKE
            hand_header = headerHandshake(packages)
            com.sendData(hand_header + eop_data)
            time.sleep(0.1)

            # Aguardando a confirmação do cliente
            confirmation_header_handshake = com.rx.getNData(size_header)
            confirmation_eop_handshake = com.rx.getNData(size_end_of_package)

            if see_error(confirmation_header_handshake, confirmation_eop_handshake):
                print("Há um erro na comunicação inicial")
                init_completed = False
            else:
                if transform_to_int(confirmation_header_handshake[0:1]) == 2:
                    print("Server autorizou. Começar a transmissão!")
                    init_completed = True
        
        send_all_packages = False
        last = False
        index_data1 = 0
        index_data2 = index_data1 + size_payload
        number_package = 1
        while not send_all_packages:
            time.sleep(2)
            print("Enviando o pacote {}...".format(number_package))
            if number_package == packages:
                last = True

            if not last:
                data = txBuffer[index_data1 : index_data2]
                header = define_header(3, number_package, packages, size_payload)
                com.sendData(header + data + eop_data)
                time.sleep(0.1)
                print("Enviei o pacote {0} com header {1}\n".format(number_package, header))

            else:
                data = txBuffer[index_data1 : index_data1+last_payload]
                header = define_header(3, number_package, packages, last_payload)
                com.sendData(header + data + eop_data)
                time.sleep(0.1)
                print("Enviei o último pacote, com header {}\.".format(header))
                send_all_packages = True
     
            index_data1 += size_payload
            number_package += 1
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com.disable()
    except:
        print("ops! :-\\")
        com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
