#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#####################################################
# Camada Física da Computação
# Carareto
# 11/08/2020
# Adaptação: William Silva
#####################################################

from enlace import *
import time
# Portas: python -m serial.tools.list_ports

# Porta
serialName = "COM3"

def main():
    try:
        # Nome da imagem que será salva quando for recebida
        imageW = "./img/imageRecebida.png"

        # Iniciando a conexão
        com_back = enlace(serialName)    
        com_back.enable()
        print("A porta {} esta conectada". format(com_back.fisica.name))

        # Pegando o tamanho da imagem, que passei primeiro
        recebido, nRx0 = com_back.getData(2)
        tamanho = int.from_bytes(recebido, byteorder='big')
        print("O valor recebido foi {}".format(tamanho))
        time.sleep(0.1)

        # Pegando a Imagem de fato
        rxBuffer, nRx = com_back.getData(tamanho)
        print("O nRx eh {}".format(nRx))

        # Salvar a imagem
        print("-"*30)
        print ("Salvando dados no arquivo:")
        print (" - {}".format(imageW))
        f = open(imageW, 'wb')
        f.write(rxBuffer)
        f.close()
        print("Imagem salva com sucesso!")

        # Enviando novamente para comparação
        print("-"*30)
        print("Antes de fechar a porta, vou enviar os dados de volta")        
        com_back.sendData((int(nRx)).to_bytes(2, byteorder='big'))

        # Desativando a porta
        com_back.disable()
        print("Porta desabilitada!")
    
    except:
        print("Recepcao Falhou")
        com_back.disable()

if __name__ == "__main__":
    main()
