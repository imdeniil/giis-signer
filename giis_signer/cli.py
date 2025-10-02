"""
Главная утилита для подписания XML-документов в формате ГИИС ДМДК
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

from giis_signer.cryptopro_signer import CryptoProSigner, CryptoProException
from giis_signer.xml_signer import XMLSigner, XMLSignerException


def extract_element_id(xml_content: str) -> Optional[str]:
    """
    Извлекает element_id из XML по паттерну <ns:RequestData id="...">

    Args:
        xml_content: содержимое XML

    Returns:
        element_id или None если не найден
    """
    # Паттерн для поиска id в RequestData или любом другом элементе
    pattern = r'<[^>]*:RequestData[^>]+id\s*=\s*["\']([^"\']+)["\']'
    match = re.search(pattern, xml_content)

    if match:
        return match.group(1)

    # Если не нашли в RequestData, ищем любой элемент с id
    pattern_generic = r'id\s*=\s*["\']([^"\']+)["\']'
    match = re.search(pattern_generic, xml_content)

    if match:
        return match.group(1)

    return None

def main():
    """Главная функция утилиты"""
    parser = argparse.ArgumentParser(
        description='Утилита для подписания XML-документов по стандарту ГИИС ДМДК'
    )

    parser.add_argument(
        'input',
        type=str,
        help='Путь к входному XML-файлу (SOAP-шаблон)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Путь к выходному файлу (если не указан, выводится в stdout)'
    )

    parser.add_argument(
        '-t', '--thumbprint',
        type=str,
        help='Отпечаток сертификата (SHA1)'
    )

    parser.add_argument(
        '-s', '--subject',
        type=str,
        help='Имя субъекта сертификата'
    )

    parser.add_argument(
        '-e', '--element-id',
        type=str,
        default=None,
        help='ID элемента для подписания (по умолчанию: авто-определение из XML или "body")'
    )

    parser.add_argument(
        '-n', '--signature-element',
        type=str,
        default='CallerSignature',
        help='Имя элемента для вставки подписи (по умолчанию: CallerSignature)'
    )

    args = parser.parse_args()

    try:
        # Проверяем наличие сертификата
        if not args.thumbprint and not args.subject:
            print("Ошибка: Необходимо указать --thumbprint или --subject", file=sys.stderr)
            sys.exit(1)

        # Читаем входной файл
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Ошибка: Файл '{args.input}' не найден", file=sys.stderr)
            sys.exit(1)

        with open(input_path, 'r', encoding='utf-8') as f:
            soap_xml = f.read()

        print(f"Загружен XML-шаблон из {args.input}")

        # Определяем element_id
        element_id = args.element_id
        if not element_id:
            # Пробуем авто-определить
            element_id = extract_element_id(soap_xml)
            if element_id:
                print(f"Element ID определен автоматически: '{element_id}'")
            else:
                element_id = 'body'
                print(f"Element ID не найден, используется значение по умолчанию: '{element_id}'")
        else:
            print(f"Используется указанный Element ID: '{element_id}'")

        # Инициализируем подписанта
        print("Инициализация КриптоПро CSP...")
        signer = CryptoProSigner(
            thumbprint=args.thumbprint,
            subject_name=args.subject
        )

        if args.thumbprint:
            print(f"Поиск по отпечатку: {signer.thumbprint}")

        # Находим сертификат
        print("Поиск сертификата...")
        certificate = signer.find_certificate()
        print(f"Сертификат найден: {certificate.SubjectName}")
        print(f"Отпечаток: {certificate.Thumbprint}")

        # Создаем XML подписанта
        xml_signer = XMLSigner(signer)

        # Подписываем документ
        print(f"Подписание элемента с id='{element_id}'...")
        signed_xml = xml_signer.sign_soap_request(
            soap_xml,
            element_id=element_id,
            signature_element_name=args.signature_element
        )

        # Сохраняем результат
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(signed_xml)
            print(f"Подписанный документ сохранен в {args.output}")
        else:
            print("\n--- Подписанный XML ---")
            print(signed_xml)

        print("\nУспешно!")
        sys.exit(0)

    except CryptoProException as e:
        print(f"Ошибка КриптоПро: {e}", file=sys.stderr)
        sys.exit(1)
    except XMLSignerException as e:
        print(f"Ошибка подписания XML: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
