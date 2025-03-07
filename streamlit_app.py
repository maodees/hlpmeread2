import qrtools

qr = qrtools.QR()
qr.decode("path_to_qrcode_image.png")

if qr.data:
    print(f"Decoded Data: {qr.data}")
else:
    print("No QR Code detected.")
