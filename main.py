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
import json

# kill previous app instances that exposes port:5432 - only works in linux
close_process = subprocess.run('fuser -k 5432/tcp', shell=True)
server_process = subprocess.Popen('cd server && npm start', shell=True)


# create the root window
root = Tk()
root.title('Tkinter Open File Dialog')
root.resizable(False, False)

# create objects to package in the request
json_request_data = {}

# default values in the inputs
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
# stringify credential
json_string = json.dumps(json_object, indent=4)


# function runned when we want to select a certificate file
def select_file():
    # definition of the system window to select the file,
    # here we define the preset for the filetype
    filetypes = (
        ('archivos de intercambio de información personal', '*.pfx'),
        ('archivos de certificado', '*.cer'),
        ('All files', '*.*')
    )

    # contextual window to open a system file
    filename = fd.askopenfilename(
        title='Open a file',
        initialdir='./CERTIFICATES',
        filetypes=filetypes)

    # with the selected file (Certificate) we proceed to read and manage the data
    with open(filename, 'rb') as file:
        data = file.read()
        # we set the password in a variable
        password = '123456'.encode()
        # charge the certificate in a cryptography object
        pkcs12 = load_pkcs12(data, password)
        # obtaining key and certificate from pfx12 certificate
        # the only key format the gaia-X wizard understands is "PrivateFormat.PKCS8"
        # the ***Bytes variables have the public and private keys in readable format
        key = pkcs12.key
        cert = pkcs12.cert
        publicKey = key.public_key()
        publicBytes = publicKey.public_bytes(Encoding.PEM, PublicFormat.PKCS1)
        publicNumbers = publicKey.public_numbers()
        privateBytes = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())

        # reading the certificate chain to show in GUI
        message = cert.friendly_name 
        for i in pkcs12.additional_certs:
            message += ' \r' + pkcs12.additional_certs[i].friendly_name
        
        # Setting up the info 

        # we show into the button which charges the certificate
        # also enable the button that allows us to sign the document charged
        boton.config(text =  message)
        boton2.config(state="enabled")
        # make this following variables accesible from all application
        global input01
        global input02
        # showing the default values for the credential and the verification method
        # they are in a modifiable text frame, the user can change the values 
        # before proceed to sign 
        label01 = Label(frame1)
        label01.config(text="Verification Method")
        label02 = Label(frame1)
        label02.config(text="Content")
        input01 = Text(frame1)
        input02 = Text(frame1)
        input01.insert(INSERT, default_verification_method)
        input02.insert(INSERT, json_string)
        # we send the info to the interface
        label01.pack(anchor="n")
        input01.pack(anchor="n")
        label02.pack(anchor="n")
        input02.pack(anchor="n")

        # we call globally to the previously created variable json_request_data
        # to save the private key
        global json_request_data
        json_request_data= {'key':privateBytes.decode("utf-8")}

        

def call_server():
    # we will acceed and modify the following variable values
    # then we charge them globally
    global json_request_data
    global input01
    global input02

    # here we save the values of the text-boxes iin the request data 
    json_request_data['credential'] = input02.get("1.0",END)
    json_request_data['verification_method'] = input01.get("1.0",END)

    #we make the request to the server who signs the document
    # and save the response in a new variable
    response = requests.post("http://localhost:5432/",data=json_request_data)

    # we parse the obtained value to be able to read the info as a JSON object
    json_response = response.json()
    # to show the value in a text-box we need a readable format 
    formatted_json_response = json.dumps(json_response, indent=4)
    # then we set up the interface
    label03 = Label(frame2)
    label03.config(text="Signed Content")
    texto0 = Text(frame2)
    texto0.insert(INSERT, formatted_json_response)
    label03.pack(anchor="e", fill="both")
    texto0.pack(anchor="e", fill="both",expand=True)

    # we close the server instance
    close_process = subprocess.run('fuser -k 5432/tcp', shell=True)
    server_process.terminate()


# setting up the initial interface layout
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



# defining the closing behaviour
def on_closing():
    # in case the server is running we kill the process
    close_process = subprocess.run('fuser -k 5432/tcp', shell=True)
    server_process.terminate()
    root.destroy()

# setting the behaviour on close
root.protocol("WM_DELETE_WINDOW", on_closing)

# run the application
root.mainloop()