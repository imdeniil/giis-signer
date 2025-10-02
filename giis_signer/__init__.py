"""

Утилита для подписания XML-документов по стандарту XMLDSig
с требованиями ГИИС ДМДК, используя КриптоПро CSP.
"""

__version__ = "1.0.0"
__author__ = "GIIS Signer Contributors"
__license__ = "MIT"

from giis_signer.cryptopro_signer import CryptoProSigner, CryptoProException
from giis_signer.xml_signer import XMLSigner, XMLSignerException
from giis_signer.diagnostics import (
    check_cryptopro_available,
    list_certificates,
    check_signature,
    SignatureChecker
)

__all__ = [
    "CryptoProSigner",
    "CryptoProException",
    "XMLSigner",
    "XMLSignerException",
    "check_cryptopro_available",
    "list_certificates",
    "check_signature",
    "SignatureChecker",
]
