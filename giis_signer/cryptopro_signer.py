"""
Модуль для работы с КриптоПро CSP через COM-интерфейс
Реализует подписание данных по ГОСТ Р 34.10-2012 с реверсом подписи
"""

import base64
import win32com.client
from typing import Optional


class CryptoProException(Exception):
    """Исключение при работе с КриптоПро"""
    pass


class CryptoProSigner:
    """
    Класс для подписания данных с использованием КриптоПро CSP
    """

    # Константы CAPICOM_STORE_LOCATION
    CAPICOM_CURRENT_USER_STORE = 2
    CAPICOM_LOCAL_MACHINE_STORE = 1

    # Константы CAPICOM_STORE_OPEN_MODE
    CAPICOM_STORE_OPEN_READ_ONLY = 0

    # Имена хранилищ
    CAPICOM_MY_STORE = "My"

    # Константы CAPICOM_CERTIFICATE_FIND_TYPE
    CAPICOM_CERTIFICATE_FIND_SHA1_HASH = 0
    CAPICOM_CERTIFICATE_FIND_SUBJECT_NAME = 1

    # Константы CADESCOM_HASH_ALGORITHM
    CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256 = 101
    CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_512 = 102

    # Константы CAPICOM_ENCODING_TYPE
    CAPICOM_ENCODE_BASE64 = 0

    # Константы CADESCOM_CONTENT_ENCODING_TYPE
    CADESCOM_BASE64_TO_BINARY = 1

    def __init__(self, thumbprint: Optional[str] = None, subject_name: Optional[str] = None):
        """
        Инициализация подписанта

        Args:
            thumbprint: Отпечаток сертификата (SHA1)
            subject_name: Имя субъекта сертификата
        """
        # Очищаем thumbprint от пробелов и приводим к верхнему регистру
        self.thumbprint = thumbprint.replace(" ", "").upper() if thumbprint else None
        self.subject_name = subject_name
        self.certificate = None
        self.hash_algorithm = self.CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256

    def find_certificate(self):
        """
        Поиск сертификата в хранилище

        Raises:
            CryptoProException: Если сертификат не найден
        """
        store = None
        try:
            # Пробуем разные варианты создания Store
            try:
                store = win32com.client.Dispatch("CAdESCOM.Store")
            except:
                try:
                    store = win32com.client.Dispatch("CAPICOM.Store")
                except:
                    raise CryptoProException("Не удалось создать объект Store. Проверьте установку КриптоПро CSP")

            # Открываем хранилище сертификатов
            store.Open(
                self.CAPICOM_CURRENT_USER_STORE,
                self.CAPICOM_MY_STORE,
                self.CAPICOM_STORE_OPEN_READ_ONLY
            )

            certificates = store.Certificates

            if self.thumbprint:
                # Поиск по отпечатку
                certificates = certificates.Find(
                    self.CAPICOM_CERTIFICATE_FIND_SHA1_HASH,
                    self.thumbprint,
                    False  # ValidOnly = False
                )
            elif self.subject_name:
                # Поиск по имени субъекта
                certificates = certificates.Find(
                    self.CAPICOM_CERTIFICATE_FIND_SUBJECT_NAME,
                    self.subject_name,
                    False
                )
            else:
                raise CryptoProException("Необходимо указать thumbprint или subject_name")

            if certificates.Count == 0:
                raise CryptoProException(f"Сертификат не найден. Отпечаток: {self.thumbprint}")

            # Берем первый найденный сертификат (индексация с 1)
            self.certificate = certificates.Item(1)

            if store:
                store.Close()

            return self.certificate

        except CryptoProException:
            raise
        except Exception as e:
            if store:
                try:
                    store.Close()
                except:
                    pass
            raise CryptoProException(f"Ошибка при поиске сертификата: {e}")

    def compute_hash(self, data: bytes) -> str:
        """
        Вычисление хеша по ГОСТ Р 34.11-2012

        Args:
            data: Данные для хеширования

        Returns:
            Base64-encoded хеш

        Raises:
            CryptoProException: Если произошла ошибка при хешировании
        """
        try:
            hasher = win32com.client.Dispatch("CAdESCOM.HashedData")
            hasher.Algorithm = self.hash_algorithm
            hasher.DataEncoding = self.CADESCOM_BASE64_TO_BINARY

            # Кодируем данные в base64 для передачи в КриптоПро
            data_base64 = base64.b64encode(data).decode('ascii')
            hasher.Hash(data_base64)

            # Получаем значение хеша (возвращается в HEX формате)
            hash_hex = hasher.Value

            # Конвертируем HEX в Base64
            hash_bytes = bytes.fromhex(hash_hex)
            hash_base64 = base64.b64encode(hash_bytes).decode('ascii')

            return hash_base64

        except Exception as e:
            raise CryptoProException(f"Ошибка при вычислении хеша: {e}")

    def sign_hash(self, hash_value: str) -> str:
        """
        Подписание хеша с реверсом подписи

        Args:
            hash_value: Base64-encoded хеш

        Returns:
            Base64-encoded подпись (с реверсом)

        Raises:
            CryptoProException: Если произошла ошибка при подписании
        """
        try:
            if not self.certificate:
                self.find_certificate()

            # Создаем объект для подписания хеша
            raw_signature = win32com.client.Dispatch("CAdESCOM.RawSignature")

            # Создаем HashedData объект с уже вычисленным хешем
            hasher = win32com.client.Dispatch("CAdESCOM.HashedData")
            hasher.Algorithm = self.hash_algorithm

            # Конвертируем Base64 хеш в HEX для SetHashValue
            hash_bytes = base64.b64decode(hash_value)
            hash_hex = hash_bytes.hex().upper()

            hasher.SetHashValue(hash_hex)

            # Подписываем хеш
            signature_hex = raw_signature.SignHash(hasher, self.certificate)

            # ВАЖНО: Реверсируем подпись (требование КриптоПро)
            # Конвертируем hex -> bytes -> реверс -> base64
            signature_bytes = bytes.fromhex(signature_hex)
            reversed_signature = signature_bytes[::-1]
            signature_base64 = base64.b64encode(reversed_signature).decode('ascii')

            return signature_base64

        except Exception as e:
            raise CryptoProException(f"Ошибка при подписании хеша: {e}")

    def sign_data(self, data: bytes) -> str:
        """
        Подписание данных (вычисление хеша + подписание)

        Args:
            data: Данные для подписания

        Returns:
            Base64-encoded подпись (с реверсом)

        Raises:
            CryptoProException: Если произошла ошибка при подписании
        """
        hash_value = self.compute_hash(data)
        return self.sign_hash(hash_value)

    def get_certificate_base64(self) -> str:
        """
        Получение сертификата в формате Base64

        Returns:
            Base64-encoded сертификат

        Raises:
            CryptoProException: Если произошла ошибка при получении сертификата
        """
        try:
            if not self.certificate:
                self.find_certificate()

            # Экспортируем сертификат в base64
            cert_base64 = self.certificate.Export(self.CAPICOM_ENCODE_BASE64)

            # Удаляем заголовки BEGIN/END CERTIFICATE если они есть
            cert_base64 = cert_base64.replace("-----BEGIN CERTIFICATE-----", "")
            cert_base64 = cert_base64.replace("-----END CERTIFICATE-----", "")
            cert_base64 = cert_base64.replace("\r", "").replace("\n", "").strip()

            return cert_base64

        except Exception as e:
            raise CryptoProException(f"Ошибка при получении сертификата: {e}")

    def get_signature_algorithm_uri(self) -> str:
        """
        Получение URI алгоритма подписи на основе сертификата

        Returns:
            URI алгоритма подписи
        """
        # Для ГОСТ Р 34.10-2012 256 бит
        return "urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102012-gostr34112012-256"

    def get_digest_algorithm_uri(self) -> str:
        """
        Получение URI алгоритма хеширования

        Returns:
            URI алгоритма хеширования
        """
        # Для ГОСТ Р 34.11-2012 256 бит
        return "urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34112012-256"