from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from cryptography import x509
from cryptography.hazmat.primitives.serialization import PublicFormat, NoEncryption, PrivateFormat, Encoding, BestAvailableEncryption, load_pem_private_key
from cryptography.hazmat.primitives.serialization.pkcs12 import load_pkcs12, PKCS12KeyAndCertificates, PKCS12Certificate
from cryptography.hazmat.primitives.asymmetric.rsa import  RSAPrivateKey, RSAPublicKey
# from pyld import jsonld
# from jose import jwt
import json


# create the root window
root = Tk()
root.title('Tkinter Open File Dialog')
root.resizable(False, False)
root.geometry('1280x1024')



json_object = {
    "@context": [
        "https://www.w3.org/2018/credentials/v1",
        "https://w3id.org/security/suites/jws-2020/v1",
        "https://registry.lab.gaia-x.eu/development/api/trusted-shape-registry/v1/shapes/jsonld/trustframework#"
    ],
    "type": [
        "VerifiableCredential"
    ],
    "id": "https://arlabdevelopments.com/.well-known/ArsysParticipant.json",
    "issuer": "did:web:arlabdevelopments.com",
    "issuanceDate": "2023-12-11T09:00:00.000Z",
    "credentialSubject": {
        "gx:legalName": "Arsys Internet, S.L.U.",
        "gx:headquarterAddress": {
        "gx:countrySubdivisionCode": "ES-RI"
        },
        "gx:legalRegistrationNumber": {
        "id": "https://arlabdevelopments.com/.well-known/legalRegistrationNumberVC.json"
        },
        "gx:legalAddress": {
        "gx:countrySubdivisionCode": "ES-RI"
        },
        "type": "gx:LegalParticipant",
        "gx-terms-and-conditions:gaiaxTermsAndConditions": "70c1d713215f95191a11d38fe2341faed27d19e083917bc8732ca4fea4976700",
        "id": "https://arlabdevelopments.com/.well-known/ArsysParticipant.json"
    }
}

json_string = json.dumps(json_object, indent=4)
def select_file():
    filetypes = (
        ('archivos de intercambio de información personal', '*.pfx'),
        ('archivos de certificado', '*.cer'),
        ('All files', '*.*')
    )

    filename = fd.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)

    with open(filename, 'rb') as file:
        data = file.read()
        pkcs12 = load_pkcs12(data, '123456'.encode())
        key = pkcs12.key
        cert = pkcs12.cert
        publicKey = key.public_key()
        publicBytes = publicKey.public_bytes(Encoding.PEM, PublicFormat.PKCS1)
        publicNumbers = publicKey.public_numbers()
        privateBytes = key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption())
        message = cert.friendly_name 

        for i in pkcs12.additional_certs:
            message += ' \r' + pkcs12.additional_certs[i].friendly_name
        
        
        texto0.config(text =  message)
        texto1.config(text = publicBytes)
        texto2.config(text = privateBytes)
        # RSA_Private_Key = jwt.importPKCS8(privateBytes, 'PS256')
        

    # cert = x509.load_pem_x509_certificate(ca_cert)
    # key = load_pem_private_key(ca_key, None)
    # p12 = pkcs12.serialize_key_and_certificates(
    #     b"friendlyname", key, cert, None, BestAvailableEncryption(b"password")
    # )

    # showinfo(
    #     title='Selected File',
    #     message= privateBytes
    # )

boton=ttk.Button(
    root,
    text='Escoge un certificado para firmar el documento',
    command=select_file
)
boton.pack(anchor="n", fill="both")
texto0 = ttk.Label(root, text='')
texto0.pack(anchor="n", fill="both", expand=True)
texto1 = ttk.Label(root, text='')
texto1.pack(anchor="n", fill="both", expand=True)
texto2 = ttk.Label(root, text='')
texto2.pack(anchor="n", fill="both", expand=True)














# run the application
root.mainloop()