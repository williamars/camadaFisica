#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


from enlace import *
import time
#   python -m serial.tools.list_ports
serialName = "COM4"

size_header = 10
size_payload = 114 # no maximo
size_end_of_package = 4

def transform_to_bytes(number):
    return int(number).to_bytes(1, byteorder='big')

def transform_to_int(byte):
    return int.from_bytes(byte, byteorder='big')

def header_confirm_Handshake():
    type_ = transform_to_bytes(2)
    zero = transform_to_bytes(0)
    header = type_ + zero * 9
    # b'\x02\x00\x00\x00...
    return header

def EOP():
    zero = transform_to_bytes(0)
    eop = zero * size_end_of_package
    return eop

def see_error(header, eop):
    error = False

    if len(header) != size_header:
        print("Há um erro no tamanho do header")
        error = True
    if len(eop) != size_end_of_package:
        print("Há um erro no tamanho do EOP")
        error = True

    return error

def define_header(type_, package_actual, packages, size_payload):

    tipo = transform_to_bytes(type_)
    package_actual = transform_to_bytes(package_actual)
    number = transform_to_bytes(packages)
    zero = transform_to_bytes(0)

    if type_ == 4:
        header = tipo + zero*3 + number + package_actual + zero*4
        
    else:
        size = transform_to_bytes(size_payload)
        header = tipo + package_actual + number + size + zero*6

    return header

def send_something(type_, package, error):
    eop = EOP()
    # Tipo de confirmação Handshake
    if type_ == 2:
        header = header_confirm_Handshake()
        return header + eop

    elif type_ == 4:
        header = define_header(type_, package, error, 0)
        return header + eop


def main():
    try:
        com = enlace(serialName)
    
        com.enable()

        imageW = './img/thisIsCopia.png'
        
        print("Comunicação de Recepção aberta!")
        
        finish = False
        handshakeCame = False
        getAllPackages = False
        all_payloads = b''

        while not finish:    
            # Primeiramente, pegando o HANDSHAKE
            while not handshakeCame:
                header = com.rx.getNData(size_header)
                eop = com.rx.getNData(size_end_of_package)
                if transform_to_int(header[0:1]) == 1:
                    if see_error(header, eop):
                        print("Há um erro")
                    else:
                        qtde_packages = transform_to_int(header[2:3])
                        print("A quantidade de pacotes que receberei será {}".format(qtde_packages))
                        print("Está tudo certo, vou enviar a resposta do handshake!\n")
                        time.sleep(0.5)
                        com.sendData(send_something(2, 0, 0))
                        handshakeCame = True

            contador_package = 0
            tamanho_payload = 0
            while not getAllPackages:

                print("Agora, vou aguardar o pacote {} ". format(contador_package+1))
                # Comunicação dos pacotes
                header = com.rx.getNData(size_header)
                type_message = transform_to_int(header[0:1])
                actual_package = transform_to_int(header[1:2])
                size_payload = transform_to_int(header[3:4])

                # print(header)

                payload = com.rx.getNData(size_payload)
                eop = com.rx.getNData(size_end_of_package)
                print("Esperando 1 segundo...\n")
                time.sleep(1)
                

                if actual_package == (contador_package+1):
                    if type_message == 3:
                        time.sleep(0.1)
                        if see_error(header, eop):
                            print("Há um erro no header ou no EOP")
                            #Mandar uma mensagem avisando que deu errado, envia novamente, espera receber novamiente
                        all_payloads += payload
                        tamanho_payload = len(all_payloads)
                        

                    print("Recebi o pacote {}. Vou enviar a confirmação para o Client\n".format(actual_package))
                    com.sendData(send_something(4, contador_package, 1))
                    time.sleep(0.1)

                    if actual_package == qtde_packages:
                            print("\nEnviou todos. Finalizando comunicação!")
                            getAllPackages = True
                            finish = True

                    contador_package += 1
                else:
                    # print(tamanho_payload/114)
                    print("Deu erro nos pacotes. Esse não era o próximo. Por favor, mandar de novo o {}". format(int((tamanho_payload/114)+1)))
                    # print(send_something(4, (tamanho_payload/114)+1, 0))
                    com.sendData(send_something(4, int((tamanho_payload/114)+1), 0))
                    time.sleep(2)

        # print(all_payloads)

        print("-"*30)
        print ("Salvando dados no arquivo:")
        print (" - {}".format(imageW))
        f = open(imageW, 'wb')
        f.write(all_payloads)
        f.close()
        print("Imagem salva com sucesso!")
               
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com.disable()
    except Exception as ex:
        print(ex)
        com.disable()

# Só roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
