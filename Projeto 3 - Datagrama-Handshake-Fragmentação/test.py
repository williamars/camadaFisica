image = './img/image.png'
txbuffer = open(image, 'rb').read()

print(len(txbuffer[0:114]))
