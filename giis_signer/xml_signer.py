"""
Модуль для формирования XML-подписи в формате XMLDSig
с поддержкой требований ГИИС ДМДК
"""

import uuid
from xml.etree import ElementTree as ET
from typing import Optional

from xmlcanon import canonicalize_xml
from smev_transform import Transform as SmevTransform
from giis_signer.cryptopro_signer import CryptoProSigner, CryptoProException


class XMLSignerException(Exception):
    """Исключение при формировании XML-подписи"""
    pass


class XMLSigner:
    """
    Класс для создания XML-подписи в формате XMLDSig
    с применением трансформаций ExcC14N и SMEV
    """

    DS_NAMESPACE = "http://www.w3.org/2000/09/xmldsig#"

    def __init__(self, signer: CryptoProSigner):
        """
        Инициализация подписанта XML

        Args:
            signer: Экземпляр CryptoProSigner для работы с сертификатом
        """
        self.signer = signer

    def sign_element(self, xml_string: str, element_id: str) -> str:
        """
        Подписывает XML-элемент и возвращает структуру ds:Signature

        Args:
            xml_string: Исходный XML-документ
            element_id: ID элемента, который нужно подписать

        Returns:
            XML-подпись в формате ds:Signature

        Raises:
            XMLSignerException: Если произошла ошибка при подписании
        """
        try:
            # Парсим XML
            root = ET.fromstring(xml_string)

            # Находим элемент для подписания по ID
            element_to_sign = self._find_element_by_id(root, element_id)
            if element_to_sign is None:
                raise XMLSignerException(f"Элемент с id='{element_id}' не найден")

            # Конвертируем элемент в строку
            element_string = ET.tostring(element_to_sign, encoding='unicode')

            # Шаг 1: Применяем ExcC14N каноникализацию
            canonicalized = canonicalize_xml(element_string)

            # Шаг 2: Применяем SMEV-трансформацию
            smev_transformer = SmevTransform()
            transformed = smev_transformer.process(canonicalized)

            # Шаг 3: Вычисляем дайджест
            digest_value = self.signer.compute_hash(transformed.encode('utf-8'))

            # Отладка: проверяем дайджест
            if not digest_value or len(digest_value) == 0:
                raise XMLSignerException("DigestValue пустой!")
            print(f"DEBUG: DigestValue = {digest_value[:50]}... (длина: {len(digest_value)})")

            # Шаг 4: Формируем SignedInfo С xmlns:ds для каноникализации
            signed_info_with_ns = self._create_signed_info(
                element_id,
                digest_value,
                self.signer.get_signature_algorithm_uri(),
                self.signer.get_digest_algorithm_uri(),
                include_xmlns=True  # С xmlns для каноникализации
            )

            # Шаг 5: Каноникализируем SignedInfo (с xmlns:ds)
            signed_info_canonicalized = canonicalize_xml(signed_info_with_ns)

            # Шаг 6: Подписываем SignedInfo
            signature_value = self.signer.sign_data(signed_info_canonicalized.encode('utf-8'))

            # Шаг 7: Формируем SignedInfo БЕЗ xmlns:ds для вставки в финальный XML
            # (т.к. xmlns:ds будет унаследован от родительского ds:Signature)
            signed_info_without_ns = self._create_signed_info(
                element_id,
                digest_value,
                self.signer.get_signature_algorithm_uri(),
                self.signer.get_digest_algorithm_uri(),
                include_xmlns=False  # Без xmlns для финального XML
            )

            # Шаг 8: Получаем сертификат
            certificate_base64 = self.signer.get_certificate_base64()

            # Шаг 9: Формируем финальную структуру Signature с SignedInfo БЕЗ xmlns:ds
            signature_xml = self._create_signature(
                signed_info_without_ns,
                signature_value,
                certificate_base64
            )

            return signature_xml

        except CryptoProException as e:
            raise XMLSignerException(f"Ошибка КриптоПро: {e}")
        except Exception as e:
            raise XMLSignerException(f"Ошибка при подписании: {e}")

    def _find_element_by_id(self, root: ET.Element, element_id: str) -> Optional[ET.Element]:
        """
        Рекурсивный поиск элемента по атрибуту id

        Args:
            root: Корневой элемент для поиска
            element_id: Значение атрибута id

        Returns:
            Найденный элемент или None
        """
        # Проверяем текущий элемент
        if root.get('id') == element_id or root.get('Id') == element_id or root.get('ID') == element_id:
            return root

        # Рекурсивно ищем в дочерних элементах
        for child in root:
            result = self._find_element_by_id(child, element_id)
            if result is not None:
                return result

        return None

    def _create_signed_info(self, reference_uri: str, digest_value: str,
                           signature_method: str, digest_method: str,
                           include_xmlns: bool = True) -> str:
        """
        Создает элемент SignedInfo

        Args:
            reference_uri: URI ссылки на подписываемый элемент
            digest_value: Значение дайджеста (base64)
            signature_method: URI алгоритма подписи
            digest_method: URI алгоритма хеширования
            include_xmlns: Включать ли xmlns:ds декларацию

        Returns:
            XML-строка с элементом SignedInfo
        """
        xmlns_attr = f' xmlns:ds="{self.DS_NAMESPACE}"' if include_xmlns else ''

        # ВАЖНО: ГИИС ДМДК использует самозакрывающиеся теги БЕЗ ПРОБЕЛА перед />
        # Формат: <tag/> (НЕ <tag />)
        # Проверено по эталону respons.xml от ГИИС ДМДК
        signed_info = f'''<ds:SignedInfo{xmlns_attr}>
  <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
  <ds:SignatureMethod Algorithm="{signature_method}"/>
  <ds:Reference URI="#{reference_uri}">
    <ds:Transforms>
      <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
      <ds:Transform Algorithm="urn://smev-gov-ru/xmldsig/transform"/>
    </ds:Transforms>
    <ds:DigestMethod Algorithm="{digest_method}"/>
    <ds:DigestValue>{digest_value}</ds:DigestValue>
  </ds:Reference>
</ds:SignedInfo>'''

        return signed_info

    def _create_signature(self, signed_info: str, signature_value: str,
                         certificate: str) -> str:
        """
        Создает финальный элемент Signature

        Args:
            signed_info: XML-строка SignedInfo
            signature_value: Значение подписи (base64)
            certificate: Сертификат (base64)

        Returns:
            XML-строка с полным элементом Signature
        """
        import re

        # Генерируем уникальный ID для подписи
        signature_id = f"signature-{uuid.uuid4()}"

        # Убираем XML declaration из signed_info если есть
        signed_info_clean = signed_info.strip()
        if signed_info_clean.startswith('<?xml'):
            # Находим конец XML declaration
            end_pos = signed_info_clean.find('?>') + 2
            signed_info_clean = signed_info_clean[end_pos:].strip()

        # SignedInfo уже БЕЗ xmlns:ds (если include_xmlns=False),
        # т.к. он унаследует его от родительского ds:Signature

        signature = f'''<ds:Signature xmlns:ds="{self.DS_NAMESPACE}" Id="{signature_id}">
  {signed_info_clean}
  <ds:SignatureValue>{signature_value}</ds:SignatureValue>
  <ds:KeyInfo>
    <ds:X509Data>
      <ds:X509Certificate>{certificate}</ds:X509Certificate>
    </ds:X509Data>
  </ds:KeyInfo>
</ds:Signature>'''

        return signature

    def insert_signature_into_soap(self, soap_xml: str, signature_xml: str,
                                   signature_element_name: str = "CallerSignature") -> str:
        """
        Вставляет подпись в SOAP-документ используя текстовую замену
        для сохранения точного форматирования XML

        Args:
            soap_xml: Исходный SOAP XML
            signature_xml: XML-подпись для вставки
            signature_element_name: Имя элемента, куда вставить подпись

        Returns:
            SOAP XML с вставленной подписью

        Raises:
            XMLSignerException: Если элемент для вставки не найден
        """
        try:
            import re

            # Ищем элемент CallerSignature с любым namespace префиксом
            # Паттерн: <prefix:CallerSignature>...</prefix:CallerSignature> или <prefix:CallerSignature />
            pattern = rf'<(\w+:)?{signature_element_name}(\s[^>]*)?>.*?</\1{signature_element_name}>'
            pattern_selfclose = rf'<(\w+:)?{signature_element_name}(\s[^>]*)?/>'

            # Проверяем наличие элемента
            if not re.search(pattern, soap_xml, re.DOTALL) and not re.search(pattern_selfclose, soap_xml):
                raise XMLSignerException(f"Элемент '{signature_element_name}' не найден")

            # Заменяем содержимое, сохраняя prefix
            def replace_func(match):
                prefix = match.group(1) or ''
                return f'<{prefix}{signature_element_name}>{signature_xml}</{prefix}{signature_element_name}>'

            # Пробуем оба паттерна
            result = re.sub(pattern, replace_func, soap_xml, flags=re.DOTALL)
            if result == soap_xml:  # Если не заменили, пробуем самозакрывающийся
                result = re.sub(pattern_selfclose, replace_func, soap_xml)

            return result

        except XMLSignerException:
            raise
        except Exception as e:
            raise XMLSignerException(f"Ошибка при вставке подписи: {e}")

    def _find_element_by_local_name(self, root: ET.Element, local_name: str) -> Optional[ET.Element]:
        """
        Рекурсивный поиск элемента по локальному имени (без учета namespace)

        Args:
            root: Корневой элемент для поиска
            local_name: Локальное имя элемента

        Returns:
            Найденный элемент или None
        """
        # Получаем локальное имя текущего элемента
        tag = root.tag
        if '}' in tag:
            current_local_name = tag.split('}')[1]
        else:
            current_local_name = tag

        # Проверяем текущий элемент
        if current_local_name == local_name:
            return root

        # Рекурсивно ищем в дочерних элементах
        for child in root:
            result = self._find_element_by_local_name(child, local_name)
            if result is not None:
                return result

        return None

    def sign_soap_request(self, soap_xml: str, element_id: str = "body",
                         signature_element_name: str = "CallerSignature") -> str:
        """
        Полный цикл подписания SOAP-запроса

        Args:
            soap_xml: SOAP XML для подписания
            element_id: ID элемента для подписания
            signature_element_name: Имя элемента для вставки подписи

        Returns:
            Подписанный SOAP XML

        Raises:
            XMLSignerException: Если произошла ошибка
        """
        # Создаем подпись
        signature = self.sign_element(soap_xml, element_id)

        # Вставляем подпись в SOAP
        signed_soap = self.insert_signature_into_soap(
            soap_xml,
            signature,
            signature_element_name
        )

        return signed_soap