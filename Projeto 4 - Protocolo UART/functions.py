def transformIntToBytes(number):
    return int(number).to_bytes(1, byteorder='big')

def transformBytesToInt(byte):
    return int.from_bytes(byte, byteorder='big')

def EOP():
    first = b'\xFF'
    second = b'\xAA'
    EOP = first + second + first + second
    return EOP

def numberOfPackages(size):
    completedPackages = int(size / 114)
    lastPayloadSize = size % 114

    if lastPayloadSize != 0:
        packages = completedPackages + 1
        last_payload = lastPayloadSize
    else:
        packages = division
        last_payload = 114

    print("O número total de pacotes é: {}". format(packages))
    print("O último payload tem tamanho: {} bytes \n". format(last_payload))

    return packages, last_payload

def buildHandshakeHeader(type_, id_, idServer_, totalOfPackages_, idFile_, lPayload):
    typeOfMessage   = transformIntToBytes(type_)
    idOfSensor      = transformIntToBytes(id_)
    idServer        = transformIntToBytes(idServer_)
    totalOfPackages = transformIntToBytes(totalOfPackages_)
    idFile          = transformIntToBytes(idFile_)
    lastPayloadSize = transformIntToBytes(lPayload)
    zero            = transformIntToBytes(0)

    header = typeOfMessage + idOfSensor + idServer + totalOfPackages + zero + idFile + zero * 2 + lastPayloadSize + zero

    # print("[HEADER]: ", header)

    if len(header) == 10:
        return header
    else:
        print("O header não está com tamanho correto. Fazer novamente")

def headerPackages(type_, totalOfPackages_, actualPackage_, tamPayload_):
    typeOfMessage   = transformIntToBytes(type_)
    totalOfPackages = transformIntToBytes(totalOfPackages_)
    actualPackage   = transformIntToBytes(actualPackage_)
    tamPayload      = transformIntToBytes(tamPayload_)
    zero            = transformIntToBytes(0)

    header = typeOfMessage + zero*2 + totalOfPackages + actualPackage + tamPayload + zero*4

    if len(header) == 10:
        return header

def headerConfirmation(type_, error_, lastReceived_):
    typeOfMessage   = transformIntToBytes(type_)
    lastReceived    = transformIntToBytes(lastReceived_)
    error           = transformIntToBytes(error_)
    zero            = transformIntToBytes(0)

    header = typeOfMessage + zero*5 + error + lastReceived + zero*2

    if len(header) == 10:
        return header

def seeError(header, endOP):
    error = False

    if len(header) != 10:
        print("[ERROR] Tamanho Header")
        error = True
    
    if endOP != EOP():
        print("[ERROR] EOP errado")
        error = True

    return error