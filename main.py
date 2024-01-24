from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from cryptography import x509
from cryptography.hazmat.primitives.serialization import PublicFormat, NoEncryption, PrivateFormat, Encoding, BestAvailableEncryption, load_pem_private_key
from cryptography.hazmat.primitives.serialization.pkcs12 import load_pkcs12, PKCS12KeyAndCertificates, PKCS12Certificate
from cryptography.hazmat.primitives.asymmetric.rsa import  RSAPrivateKey, RSAPublicKey
import requests
import subprocess
# from pyld import jsonld
# from jose import jwt
import json


close_process = subprocess.run('fuser -k 5432/tcp', shell=True)
server_process = subprocess.Popen('cd server && npm start', shell=True)


# create the root window
root = Tk()
root.title('Tkinter Open File Dialog')
root.resizable(False, False)
# root.geometry('1024x1280')
# screen_width= root.winfo_screenwidth()               
# screen_height= root.winfo_screenheight()               
# root.geometry("%dx%d" % (screen_width, screen_height))
json_request_data = {}

default_verification_method = 'did:web:blablabla.com'
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
        initialdir='./CERTIFICATES',
        filetypes=filetypes)

    with open(filename, 'rb') as file:
        data = file.read()
        pkcs12 = load_pkcs12(data, '123456'.encode())
        key = pkcs12.key
        cert = pkcs12.cert
        publicKey = key.public_key()
        publicBytes = publicKey.public_bytes(Encoding.PEM, PublicFormat.PKCS1)
        publicNumbers = publicKey.public_numbers()
        privateBytes = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        message = cert.friendly_name 

        for i in pkcs12.additional_certs:
            message += ' \r' + pkcs12.additional_certs[i].friendly_name
        
        # boton2.pack(anchor="n", fill="both")
        boton.config(text =  message)
        boton2.config(state="enabled")
        global input01
        global input02
        label01 = Label(frame1)
        label01.config(text="Verification Method")
        label02 = Label(frame1)
        label02.config(text="Content")
        input01 = Text(frame1)
        input02 = Text(frame1)
        input01.insert(INSERT, default_verification_method)
        input02.insert(INSERT, json_string)


        # input01.config(height=24)
        # input02.config(height=400)

        label01.pack(anchor="n")
        input01.pack(anchor="n")
        label02.pack(anchor="n")
        input02.pack(anchor="n")

        
        request_data= {'key':privateBytes.decode("utf-8")}

        global json_request_data
        json_request_data = request_data
        
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

def call_server():
    global json_request_data
    global input01
    global input02
    json_request_data['credential'] = input02.get("1.0",END)
    json_request_data['verification_method'] = input01.get("1.0",END)
    response = requests.post("http://localhost:5432/",data=json_request_data)

    json_response = response.json()
    formatted_json_response = json.dumps(json_response, indent=4)
    # input01.pack_forget()
    # input02.pack_forget()
    label03 = Label(frame2)
    label03.config(text="Signed Content")
    texto0 = Text(frame2)
    texto0.insert(INSERT, formatted_json_response)
    # texto0.config(height = screen_height)
    label03.pack(anchor="e", fill="both")
    texto0.pack(anchor="e", fill="both",expand=True)
    # showinfo(
    #     title='JWS Signature',
    #     message= json_response['proof']['jws']
    # )
    close_process = subprocess.run('fuser -k 5432/tcp', shell=True)
    server_process.terminate()

frame0= Frame(root)
frame1 = Frame(root)
frame2 = Frame(root)

boton=ttk.Button(
    frame0,
    text='Escoge un certificado para firmar el documento',
    command=select_file
)
boton2=ttk.Button(frame0,
    text='Solicitud al servidor',
    command=call_server,
    state='disabled'
)


boton.pack(anchor="n",fill="both")
boton2.pack(anchor="n",fill="both")

frame0.pack(side="top",fill="both")
frame1.pack(side="left")
frame2.pack(side="right", fill="y", expand=True)

# input01 = Text(root)
# input02 = Text(root)
# input01.insert(INSERT, default_verification_method)
# input02.insert(INSERT, json_string)

# input01.config(height=24)
# input02.config(height=400)

# input01.pack(anchor="nw")
# input02.pack(anchor="nw")




def on_closing():

    close_process = subprocess.run('fuser -k 5432/tcp', shell=True)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)


# run the application
root.mainloop()