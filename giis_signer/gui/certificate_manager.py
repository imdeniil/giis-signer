"""
Модуль для работы с сертификатами в GUI приложении
Расширяет функционал CryptoProSigner для GUI
"""

import win32com.client
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class CertificateInfo:
    """Информация о сертификате для отображения в GUI"""
    thumbprint: str
    subject_name: str
    issuer_name: str
    valid_from: str
    valid_to: str
    serial_number: str
    is_valid: bool

    def get_display_name(self) -> str:
        """Получить отображаемое имя сертификата"""
        # Извлекаем CN из subject
        cn = self._extract_cn(self.subject_name)
        # Добавляем последние 8 символов thumbprint для различия
        short_thumb = self.thumbprint[-8:].upper()
        return f"{cn} (...{short_thumb})"

    def get_tooltip(self) -> str:
        """Получить подсказку с полной информацией"""
        return (
            f"Субъект: {self.subject_name}\n"
            f"Издатель: {self.issuer_name}\n"
            f"Отпечаток: {self.thumbprint}\n"
            f"Серийный номер: {self.serial_number}\n"
            f"Действителен с: {self.valid_from}\n"
            f"Действителен до: {self.valid_to}\n"
            f"Статус: {'Действителен' if self.is_valid else 'Недействителен'}"
        )

    @staticmethod
    def _extract_cn(subject: str) -> str:
        """Извлечь CN (Common Name) из subject строки"""
        parts = subject.split(',')
        for part in parts:
            part = part.strip()
            if part.startswith('CN='):
                return part[3:].strip()
        return subject


class CertificateManager:
    """
    Менеджер сертификатов для GUI приложения
    Предоставляет список сертификатов с подробной информацией
    """

    # Константы CAPICOM
    CAPICOM_CURRENT_USER_STORE = 2
    CAPICOM_STORE_OPEN_READ_ONLY = 0
    CAPICOM_MY_STORE = "My"

    def __init__(self):
        """Инициализация менеджера"""
        self._certificates_cache: Optional[List[CertificateInfo]] = None

    def get_certificates(self, refresh: bool = False) -> List[CertificateInfo]:
        """
        Получить список всех сертификатов из хранилища

        Args:
            refresh: Обновить кэш сертификатов

        Returns:
            Список объектов CertificateInfo

        Raises:
            Exception: Если не удалось получить доступ к хранилищу
        """
        logger.info(f"Запрос списка сертификатов (refresh={refresh})")

        if self._certificates_cache is not None and not refresh:
            logger.info(f"Возврат кэшированных сертификатов: {len(self._certificates_cache)} шт.")
            return self._certificates_cache

        certificates_info = []
        store = None

        try:
            # Пробуем создать Store - сначала CAdESCOM, потом CAPICOM
            store_created = False
            last_error = None

            for store_name in ["CAdESCOM.Store", "CAPICOM.Store"]:
                try:
                    logger.debug(f"Попытка создать COM-объект: {store_name}")
                    store = win32com.client.Dispatch(store_name)
                    store_created = True
                    logger.info(f"COM-объект успешно создан: {store_name}")
                    break
                except Exception as e:
                    logger.warning(f"Не удалось создать {store_name}: {e}")
                    last_error = e
                    continue

            if not store_created:
                error_msg = f"Не удалось создать COM-объект Store. Убедитесь, что установлен КриптоПро ЭЦП Browser plug-in. Ошибка: {last_error}"
                logger.error(error_msg)
                raise Exception(error_msg)

            # Открываем хранилище
            logger.debug("Открытие хранилища сертификатов...")
            store.Open(
                self.CAPICOM_CURRENT_USER_STORE,
                self.CAPICOM_MY_STORE,
                self.CAPICOM_STORE_OPEN_READ_ONLY
            )
            logger.info("Хранилище сертификатов успешно открыто")

            certificates = store.Certificates
            cert_count = certificates.Count if certificates else 0
            logger.info(f"Найдено сертификатов в хранилище: {cert_count}")

            if certificates is None or certificates.Count == 0:
                logger.warning("Хранилище сертификатов пусто")
                # Возвращаем пустой список, но без ошибки
                self._certificates_cache = []
                return []

            # Перебираем все сертификаты
            for i in range(1, certificates.Count + 1):
                cert = certificates.Item(i)

                try:
                    # Получаем информацию о сертификате
                    cert_info = CertificateInfo(
                        thumbprint=cert.Thumbprint.replace(" ", "").upper(),
                        subject_name=cert.SubjectName,
                        issuer_name=cert.IssuerName,
                        valid_from=self._format_date(cert.ValidFromDate),
                        valid_to=self._format_date(cert.ValidToDate),
                        serial_number=cert.SerialNumber,
                        is_valid=self._check_validity(cert)
                    )
                    certificates_info.append(cert_info)
                    logger.debug(f"Сертификат #{i} обработан: {cert_info.subject_name}")
                except Exception as e:
                    # Пропускаем сертификаты с ошибками, но не прерываем процесс
                    logger.warning(f"Ошибка при обработке сертификата #{i}: {e}")
                    continue

            logger.info(f"Успешно обработано сертификатов: {len(certificates_info)}")

        except Exception as e:
            logger.error(f"Ошибка при доступе к хранилищу сертификатов: {e}", exc_info=True)
            raise Exception(f"Не удалось получить доступ к хранилищу сертификатов: {e}")

        finally:
            if store is not None:
                try:
                    store.Close()
                except:
                    pass

        # Сортируем: сначала действительные, потом по имени
        certificates_info.sort(key=lambda x: (not x.is_valid, x.subject_name))

        # Кэшируем результат
        self._certificates_cache = certificates_info

        return certificates_info

    def find_certificate_by_thumbprint(self, thumbprint: str) -> Optional[CertificateInfo]:
        """
        Найти сертификат по отпечатку

        Args:
            thumbprint: Отпечаток сертификата

        Returns:
            CertificateInfo или None если не найден
        """
        thumbprint_clean = thumbprint.replace(" ", "").upper()
        certificates = self.get_certificates()

        for cert in certificates:
            if cert.thumbprint == thumbprint_clean:
                return cert

        return None

    def _format_date(self, date_value) -> str:
        """Форматировать дату для отображения"""
        try:
            if isinstance(date_value, str):
                return date_value
            # Преобразуем в datetime если это COM-дата
            if hasattr(date_value, 'year'):
                return f"{date_value.day:02d}.{date_value.month:02d}.{date_value.year}"
            return str(date_value)
        except:
            return "Неизвестно"

    def _check_validity(self, cert) -> bool:
        """Проверить действительность сертификата"""
        try:
            # Проверяем срок действия
            now = datetime.now()
            valid_from = cert.ValidFromDate
            valid_to = cert.ValidToDate

            # Преобразуем в datetime если нужно
            if hasattr(valid_from, 'year'):
                valid_from_dt = datetime(valid_from.year, valid_from.month, valid_from.day)
            else:
                return True  # Не можем проверить, считаем действительным

            if hasattr(valid_to, 'year'):
                valid_to_dt = datetime(valid_to.year, valid_to.month, valid_to.day)
            else:
                return True

            return valid_from_dt <= now <= valid_to_dt

        except:
            return True  # В случае ошибки считаем действительным
