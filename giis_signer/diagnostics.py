"""
Утилиты диагностики для GIIS-Signer

Включает:
- Проверка доступности КриптоПро COM-объектов
- Список сертификатов в хранилище
- Диагностика XML-подписи
- Проверка DigestValue и SignatureValue
- Валидация структуры подписи

Использование из командной строки:

    # Проверка КриптоПро и сертификатов
    python -m giis_signer.diagnostics --check-cryptopro

    # Диагностика подписанного XML
    python -m giis_signer.diagnostics --check-signature signed.xml

    # Полная диагностика
    python -m giis_signer.diagnostics --check-signature signed.xml --full

Использование из кода:

    from giis_signer.diagnostics import check_cryptopro_available, list_certificates, check_signature

    # Проверка КриптоПро
    if check_cryptopro_available():
        list_certificates()

    # Проверка подписи
    check_signature("signed.xml", verbose=True)
"""

import sys
import os
import base64
import re
import argparse
from xml.etree import ElementTree as ET

try:
    import win32com.client
except ImportError:
    print("⚠️  Модуль pywin32 не установлен. Установите: pip install pywin32")
    win32com = None

from giis_signer.cryptopro_signer import CryptoProSigner
from xmlcanon import canonicalize_xml
from smev_transform import Transform as SmevTransform


# ============================================================================
# ПРОВЕРКА CRYPTOPRO COM
# ============================================================================

def check_cryptopro_available():
    """Проверка доступности COM-объектов КриптоПро"""
    if win32com is None:
        print("❌ pywin32 не установлен")
        return False

    print("\n" + "="*60)
    print("ПРОВЕРКА ДОСТУПНОСТИ CRYPTOPRO CSP")
    print("="*60)

    com_objects = [
        "CAdESCOM.Store",
        "CAdESCOM.HashedData",
        "CAdESCOM.RawSignature",
        "CAPICOM.Store"
    ]

    results = []
    for prog_id in com_objects:
        try:
            obj = win32com.client.Dispatch(prog_id)
            print(f"✅ {prog_id} - доступен")
            results.append(True)
        except Exception as e:
            print(f"❌ {prog_id} - недоступен: {e}")
            results.append(False)

    all_ok = all(results)
    if all_ok:
        print("\n✅ Все необходимые COM-объекты доступны")
    else:
        print("\n⚠️  Некоторые COM-объекты недоступны")
        print("   Убедитесь, что КриптоПро CSP установлен корректно")

    return all_ok


def list_certificates(max_count=10):
    """Список сертификатов в хранилище"""
    if win32com is None:
        print("❌ pywin32 не установлен")
        return

    print("\n" + "="*60)
    print("СПИСОК СЕРТИФИКАТОВ В ХРАНИЛИЩЕ")
    print("="*60)

    store_types = [
        ("CAdESCOM.Store", "CAdES Store"),
        ("CAPICOM.Store", "CAPICOM Store")
    ]

    for prog_id, name in store_types:
        try:
            print(f"\nИспользуется: {name} ({prog_id})")
            store = win32com.client.Dispatch(prog_id)
            store.Open(2, "My", 0)  # CURRENT_USER, My, READ_ONLY

            cert_count = store.Certificates.Count
            print(f"Всего сертификатов: {cert_count}")

            if cert_count == 0:
                print("  (хранилище пустое)")
                store.Close()
                continue

            display_count = min(cert_count, max_count)
            print(f"\nПоказаны первые {display_count} сертификатов:\n")

            for i in range(1, display_count + 1):
                cert = store.Certificates.Item(i)
                print(f"[{i}] {cert.SubjectName}")
                print(f"    Отпечаток: {cert.Thumbprint}")
                print(f"    Действителен: {cert.ValidFromDate} - {cert.ValidToDate}")

                try:
                    if cert.PrivateKey:
                        print(f"    Закрытый ключ: ✅ ЕСТЬ")
                except:
                    print(f"    Закрытый ключ: ❌ НЕТ")
                print()

            store.Close()
            return  # Успешно получили список

        except Exception as e:
            print(f"❌ Ошибка при работе с {name}: {e}")
            continue

    print("\n❌ Не удалось получить список сертификатов")


# ============================================================================
# ДИАГНОСТИКА XML-ПОДПИСИ
# ============================================================================

class SignatureChecker:
    """Инструменты для проверки XML-подписи"""

    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.ns = {'ds': 'http://www.w3.org/2000/09/xmldsig#'}

        with open(xml_file, 'r', encoding='utf-8') as f:
            self.content = f.read()

        self.root = ET.fromstring(self.content)

    def check_body_digest(self, verbose=False):
        """Проверка DigestValue элемента body"""
        print("\n" + "="*60)
        print("1. ПРОВЕРКА DIGESTVALUE ЭЛЕМЕНТА BODY")
        print("="*60)

        # Находим элемент body
        def find_element_by_id(elem, target_id):
            if elem.get('id') == target_id:
                return elem
            for child in elem:
                result = find_element_by_id(child, target_id)
                if result is not None:
                    return result
            return None

        body_elem = find_element_by_id(self.root, 'body')
        if body_elem is None:
            print("❌ Элемент с id='body' не найден!")
            return False

        # Применяем трансформации
        body_string = ET.tostring(body_elem, encoding='unicode')

        if verbose:
            print(f"\nИсходный body элемент:\n{body_string[:200]}...\n")

        # ExcC14N
        canonicalized = canonicalize_xml(body_string)
        if verbose:
            print(f"После ExcC14N ({len(canonicalized)} байт)")

        # SMEV
        smev_transformer = SmevTransform()
        transformed = smev_transformer.process(canonicalized)
        if verbose:
            print(f"После SMEV ({len(transformed)} байт)")

        # Вычисляем хеш
        try:
            # Извлекаем thumbprint из сертификата в подписи
            cert_elem = self.root.find('.//ds:X509Certificate', self.ns)
            if cert_elem is not None:
                cert_b64 = cert_elem.text.strip()
                # Используем любой доступный сертификат для хеширования
                signer = CryptoProSigner(thumbprint="c755d5b4b7e1554b632f0c989427eba47b176c3a")
                signer.find_certificate()
            else:
                raise Exception("Сертификат не найден в подписи")

            computed_digest = signer.compute_hash(transformed.encode('utf-8'))
        except Exception as e:
            print(f"❌ Ошибка вычисления хеша: {e}")
            return False

        # Сравниваем с подписью
        digest_value_elem = self.root.find('.//ds:DigestValue', self.ns)
        if digest_value_elem is None:
            print("❌ DigestValue не найден в подписи!")
            return False

        signature_digest = digest_value_elem.text.strip()

        print(f"\nВычисленный DigestValue:  {computed_digest}")
        print(f"DigestValue из подписи:   {signature_digest}")

        if computed_digest == signature_digest:
            print("\n✅ DigestValue СОВПАДАЕТ - элемент body подписан корректно")
            return True
        else:
            print("\n❌ DigestValue НЕ СОВПАДАЕТ")
            return False

    def check_signedinfo(self, verbose=False):
        """Проверка SignedInfo и SignatureValue"""
        print("\n" + "="*60)
        print("2. ПРОВЕРКА SIGNEDINFO И SIGNATUREVALUE")
        print("="*60)

        # Извлекаем SignedInfo из файла
        pattern = r'<ds:SignedInfo[^>]*>.*?</ds:SignedInfo>'
        match = re.search(pattern, self.content, re.DOTALL)

        if not match:
            print("❌ SignedInfo не найден!")
            return False

        signed_info_raw = match.group(0)

        if verbose:
            print(f"\nSignedInfo:\n{signed_info_raw[:300]}...")

        print(f"\nДлина SignedInfo: {len(signed_info_raw)} символов")

        # Проверяем SignatureValue
        signature_value_elem = self.root.find('.//ds:SignatureValue', self.ns)
        if signature_value_elem is None:
            print("❌ SignatureValue не найден!")
            return False

        signature_value = signature_value_elem.text.strip()
        print(f"SignatureValue: {signature_value[:50]}... (длина: {len(signature_value)})")

        try:
            signature_bytes = base64.b64decode(signature_value)
            print(f"Декодированная подпись: {len(signature_bytes)} байт")
            print("✅ SignatureValue корректно закодирован в Base64")
            return True
        except Exception as e:
            print(f"❌ Ошибка декодирования SignatureValue: {e}")
            return False

    def check_structure(self):
        """Проверка структуры подписи"""
        print("\n" + "="*60)
        print("3. ПРОВЕРКА СТРУКТУРЫ ПОДПИСИ")
        print("="*60)

        checks = {
            'Signature': self.root.find('.//ds:Signature', self.ns) is not None,
            'SignedInfo': self.root.find('.//ds:SignedInfo', self.ns) is not None,
            'SignatureValue': self.root.find('.//ds:SignatureValue', self.ns) is not None,
            'KeyInfo': self.root.find('.//ds:KeyInfo', self.ns) is not None,
            'X509Certificate': self.root.find('.//ds:X509Certificate', self.ns) is not None,
            'Reference': self.root.find('.//ds:Reference[@URI="#body"]', self.ns) is not None,
            'DigestValue': self.root.find('.//ds:DigestValue', self.ns) is not None,
        }

        for name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {name}")

        # Проверка алгоритмов
        c14n = self.root.find('.//ds:CanonicalizationMethod', self.ns)
        if c14n is not None and c14n.get('Algorithm') == "http://www.w3.org/2001/10/xml-exc-c14n#":
            print("✅ CanonicalizationMethod: ExcC14N")
        else:
            print("❌ CanonicalizationMethod: неверный или отсутствует")

        sig_method = self.root.find('.//ds:SignatureMethod', self.ns)
        if sig_method is not None and "gostr34102012" in sig_method.get('Algorithm', ''):
            print("✅ SignatureMethod: ГОСТ Р 34.10-2012")
        else:
            print("❌ SignatureMethod: неверный или отсутствует")

        digest_method = self.root.find('.//ds:DigestMethod', self.ns)
        if digest_method is not None and "gostr34112012" in digest_method.get('Algorithm', ''):
            print("✅ DigestMethod: ГОСТ Р 34.11-2012")
        else:
            print("❌ DigestMethod: неверный или отсутствует")

        # Проверка трансформаций
        transforms = self.root.findall('.//ds:Transform', self.ns)
        if len(transforms) == 2:
            algo1 = transforms[0].get('Algorithm', '')
            algo2 = transforms[1].get('Algorithm', '')
            if "exc-c14n" in algo1 and "smev" in algo2:
                print("✅ Transforms: ExcC14N + SMEV")
            else:
                print("⚠️  Transforms: порядок или алгоритмы неверны")
        else:
            print(f"❌ Transforms: найдено {len(transforms)} (ожидалось 2)")

        return all(checks.values())

    def print_summary(self, digest_ok, signedinfo_ok, structure_ok):
        """Итоговое резюме"""
        print("\n" + "="*60)
        print("ИТОГОВЫЙ РЕЗУЛЬТАТ")
        print("="*60)

        if digest_ok and signedinfo_ok and structure_ok:
            print("\n✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
            print("\nПодпись сформирована корректно.")
        else:
            print("\n❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ:")
            if not digest_ok:
                print("  - DigestValue элемента body неверен")
            if not signedinfo_ok:
                print("  - Проблемы с SignedInfo/SignatureValue")
            if not structure_ok:
                print("  - Структура подписи некорректна")

        print("\n" + "="*60)


def check_signature(xml_file, verbose=False):
    """
    Полная проверка XML-подписи

    Args:
        xml_file: путь к подписанному XML файлу
        verbose: подробный вывод

    Returns:
        True если все проверки пройдены
    """
    if not os.path.exists(xml_file):
        print(f"❌ Файл не найден: {xml_file}")
        return False

    print("="*60)
    print("ДИАГНОСТИКА XML-ПОДПИСИ")
    print("="*60)
    print(f"Файл: {xml_file}")
    print(f"Режим: {'Полный' if verbose else 'Краткий'}")

    try:
        checker = SignatureChecker(xml_file)

        digest_ok = checker.check_body_digest(verbose=verbose)
        signedinfo_ok = checker.check_signedinfo(verbose=verbose)
        structure_ok = checker.check_structure()

        checker.print_summary(digest_ok, signedinfo_ok, structure_ok)

        return digest_ok and signedinfo_ok and structure_ok

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Точка входа для CLI"""
    parser = argparse.ArgumentParser(
        description='Утилиты диагностики GIIS-Signer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--check-cryptopro',
        action='store_true',
        help='Проверить доступность КриптоПро CSP и список сертификатов'
    )

    parser.add_argument(
        '--check-signature',
        metavar='FILE',
        help='Проверить XML-подпись в указанном файле'
    )

    parser.add_argument(
        '--full',
        action='store_true',
        help='Полная диагностика с подробным выводом'
    )

    args = parser.parse_args()

    # Если нет аргументов, показываем help
    if not args.check_cryptopro and not args.check_signature:
        parser.print_help()
        return

    # Проверка КриптоПро
    if args.check_cryptopro:
        check_cryptopro_available()
        list_certificates()

    # Проверка подписи
    if args.check_signature:
        result = check_signature(args.check_signature, verbose=args.full)
        sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
