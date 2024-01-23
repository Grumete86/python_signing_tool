import { useEffect, useState } from 'react'
import { os } from '@neutralinojs/lib'
import './App.css';
import { VDocument } from './models/document.ts'
import { CompactSign, importPKCS8 } from 'jose'
import { canonize, JsonLdDocument } from 'jsonld'
import { staticDocumentLoader } from './utils/static-document-loader.ts'
import {
  Box,
  BoxProps,
  Drawer,
  DrawerContent,
  Flex,
  FlexProps,
  Icon,
  IconButton,
  Link,
  useColorModeValue,
  useDisclosure,
  VStack
} from '@chakra-ui/react'

// Import filesystem namespace
import { filesystem } from "@neutralinojs/lib"
import React from 'react';

function App() {
  const [json, setJson] = useState()
  // Log current directory or error after component is mounted
  useEffect(() => {
    filesystem.readDirectory('./').then((data) => {
      console.log(data)
    }).catch((err) => {
      console.log(err)
    })
  }, [])

  const signVerifiableCredential = async (pemPrivateKey: string, verifiableCredential: any, verificationMethod: string): Promise<VDocument> => {
    // Step 1: Import key from the PEM format
    const rsaPrivateKey = await importPKCS8(pemPrivateKey, 'PS256')
    // Step 2: Compute the hash of the normalized verifiable credential
    const credentialNormalized = await normalize(verifiableCredential)
    const credentialHashed = await hash(credentialNormalized)
    const credentialEncoded = new TextEncoder().encode(credentialHashed)
  
    // Step 3: Sign
    const credentialJws = await new CompactSign(credentialEncoded).setProtectedHeader({ alg: 'PS256', b64: false, crit: ['b64'] }).sign(rsaPrivateKey)
  
    // Step 4: Add the signature to the verifiable credential
    return {
      ...verifiableCredential,
      proof: {
        type: 'JsonWebSignature2020',
        created: new Date().toISOString(),
        proofPurpose: 'assertionMethod',
        verificationMethod: verificationMethod,
        jws: credentialJws
      }
    }
  }
  
  async function normalize(payload: JsonLdDocument) {
    return await canonize(payload, {
      algorithm: 'URDNA2015',
      format: 'application/n-quads',
      documentLoader: staticDocumentLoader
    })
  }
  
  function hash(payload: string) {
    return computePayloadHash(payload)
  }
  
  async function computePayloadHash(payload: string) {
    const encoder = new TextEncoder()
    const data = encoder.encode(payload)
    const digestBuffer = await crypto.subtle.digest('SHA-256', data)
    const digestArray = new Uint8Array(digestBuffer)
    return Array.from(digestArray)
      .map(b => b.toString(16).padStart(2, '0'))
      .join('')
  }
  
  async function handleClick(){
    await os.getEnvs().then(envs => {
      os.showNotification('ENVS', envs.toString())
    })
  }

  return (
    <div className="App">
      My Neutralinojs App
      <button onClick={handleClick}>Click</button>
    </div>
  );
}

export default App;