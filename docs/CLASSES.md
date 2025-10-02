# Структура классов проекта GIIS Signer

Документ описывает все классы и их взаимосвязи в проекте.

## Основные классы

### 1. CryptoProSigner

**Файл:** `giis_signer/cryptopro_signer.py`

**Назначение:** Интеграция с КриптоПро CSP через COM-интерфейс для работы с электронной подписью.

**Основные методы:**
- `__init__(thumbprint: Optional[str], subject_name: Optional[str])` - инициализация с поиском по отпечатку или субъекту
- `find_certificate()` - поиск сертификата в хранилище Windows
- `compute_hash(data: bytes) -> str` - вычисление хеша ГОСТ Р 34.11-2012 (256 бит) в Base64
- `sign_data(data: bytes) -> str` - подписание данных с ГОСТ Р 34.10-2012 (256 бит)
- `get_certificate_base64() -> str` - экспорт сертификата в Base64
- `get_signature_algorithm_uri() -> str` - получение URI алгоритма подписи
- `get_digest_algorithm_uri() -> str` - получение URI алгоритма хеширования

**Константы:**
- `CAPICOM_CURRENT_USER_STORE = 2` - хранилище текущего пользователя
- `CAPICOM_STORE_OPEN_READ_ONLY = 0` - режим только для чтения
- `CAPICOM_MY_STORE = "My"` - личное хранилище
- `CAPICOM_CERTIFICATE_FIND_SHA1_HASH = 0` - поиск по SHA1
- `CAPICOM_CERTIFICATE_FIND_SUBJECT_NAME = 1` - поиск по субъекту
- `CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256 = 101` - ГОСТ хеш 256 бит
- `CADESCOM_BASE64_TO_BINARY = 1` - конвертация Base64 в бинарные данные

**Зависимости:**
- `win32com.client` - для работы с COM-объектами
- `base64` - для кодирования/декодирования Base64

**Исключения:**
- `CryptoProException` - базовое исключение при работе с КриптоПро

---

### 2. XMLSigner

**Файл:** `giis_signer/xml_signer.py`

**Назначение:** Формирование XML-подписи в формате XMLDSig с применением трансформаций ExcC14N и SMEV.

**Основные методы:**
- `__init__(signer: CryptoProSigner)` - инициализация с экземпляром CryptoProSigner
- `sign_element(xml_string: str, element_id: str) -> str` - подписание XML-элемента
- `sign_soap_request(soap_xml: str, element_id: str, signature_element_name: str) -> str` - полный цикл подписания SOAP
- `insert_signature_into_soap(soap_xml: str, signature_xml: str, signature_element_name: str) -> str` - вставка подписи в документ

**Вспомогательные методы:**
- `_find_element_by_id(root: ET.Element, element_id: str) -> Optional[ET.Element]` - поиск элемента по атрибуту id
- `_create_signed_info(reference_uri: str, digest_value: str, signature_method: str, digest_method: str, include_xmlns: bool) -> str` - создание элемента SignedInfo
- `_create_signature(signed_info: str, signature_value: str, certificate: str) -> str` - создание финального элемента Signature
- `_find_element_by_local_name(root: ET.Element, local_name: str) -> Optional[ET.Element]` - поиск по локальному имени без namespace

**Константы:**
- `DS_NAMESPACE = "http://www.w3.org/2000/09/xmldsig#"` - пространство имен XMLDSig

**Зависимости:**
- `xml.etree.ElementTree` - для парсинга XML
- `xmlcanon` - для ExcC14N каноникализации
- `smev_transform` - для SMEV-трансформации
- `CryptoProSigner` - для криптографических операций

**Исключения:**
- `XMLSignerException` - базовое исключение при формировании подписи

**Алгоритм подписания:**
1. Извлечение элемента по ID
2. ExcC14N каноникализация
3. SMEV-трансформация
4. Вычисление DigestValue (Base64)
5. Формирование SignedInfo с xmlns:ds
6. Каноникализация SignedInfo
7. Подписание SignedInfo
8. Реверс подписи
9. Формирование финальной структуры Signature
10. Вставка в SOAP

---

### 3. SignatureChecker

**Файл:** `giis_signer/diagnostics.py`

**Назначение:** Проверка и диагностика XML-подписей.

**Основные методы:**
- `__init__(xml_file: str)` - инициализация с путем к XML-файлу
- `check(verbose: bool = False) -> bool` - проверка подписи
- `check_structure() -> bool` - проверка структуры подписи
- `check_digest() -> bool` - проверка DigestValue
- `extract_signature_info() -> dict` - извлечение информации о подписи

**Внутренние методы:**
- `_find_signature_element()` - поиск элемента ds:Signature
- `_extract_digest_value()` - извлечение DigestValue
- `_extract_reference_uri()` - извлечение URI ссылки
- `_find_signed_element()` - поиск подписанного элемента

**Зависимости:**
- `xml.etree.ElementTree` - для парсинга XML
- `xmlcanon` - для каноникализации
- `smev_transform` - для SMEV-трансформации

---

## Вспомогательные функции

### diagnostics.py

**Функции:**
- `check_cryptopro_available() -> bool` - проверка доступности КриптоПро CSP
- `list_certificates()` - вывод списка доступных сертификатов
- `check_signature(xml_file: str, verbose: bool = False) -> bool` - проверка XML-подписи

---

## CLI модуль

### cli.py

**Назначение:** Интерфейс командной строки для подписания XML-документов.

**Функции:**
- `extract_element_id(xml_content: str) -> Optional[str]` - извлечение Element ID из XML по паттерну
- `main()` - точка входа CLI приложения

**Параметры командной строки:**
- `input` - путь к входному XML-файлу
- `-o, --output` - путь к выходному файлу
- `-t, --thumbprint` - отпечаток сертификата
- `-s, --subject` - имя субъекта сертификата
- `-e, --element-id` - ID элемента для подписания (авто-определение или "body")
- `-n, --signature-element` - имя элемента для вставки подписи

**Логика авто-определения Element ID:**
1. Если `-e` не указан, пробуем извлечь из XML по паттерну `<ns:RequestData id="..."`
2. Если найден - используем его и выводим сообщение
3. Если не найден - используем дефолтное значение "body"
4. Если `-e` указан явно - используем указанное значение

**Зависимости:**
- `argparse` - для парсинга аргументов командной строки
- `re` - для извлечения Element ID
- `CryptoProSigner` - для подписания
- `XMLSigner` - для формирования XML-подписи

---

## GUI модуль

### 4. GIISSignerApp

**Файл:** `giis_signer/gui/app.py`

**Назначение:** Главное окно GUI приложения для подписания XML документов.

**Основные методы:**
- `__init__()` - инициализация приложения, создание интерфейса
- `_create_widgets()` - создание всех элементов интерфейса
- `_select_certificate()` - открытие диалога выбора сертификата
- `_load_last_certificate()` - загрузка последнего использованного сертификата
- `_extract_element_id(xml_content: str) -> Optional[str]` - извлечение Element ID из XML по паттерну
- `_on_element_id_changed(event=None)` - обработчик изменения поля Element ID (активирует кнопку обновления)
- `_refresh_element_id()` - обновление Element ID из XML по кнопке
- `_on_input_text_changed(event=None)` - обработчик изменения входного текста для авто-определения Element ID
- `_import_file()` - импорт XML файла
- `_export_file()` - экспорт подписанного XML
- `_copy_output()` - копирование результата в буфер обмена
- `_clear_input()` - очистка входного поля и Element ID
- `_clear_output()` - очистка выходного поля
- `_clear_all()` - очистка обоих полей
- `_sign_xml()` - подписание XML документа с использованием Element ID
- `_toggle_theme()` - переключение темы оформления
- `_on_closing()` - обработчик закрытия окна

**Компоненты интерфейса:**
- Заголовок с названием приложения
- Фрейм выбора сертификата
- Левая панель - входной XML:
  - Поле ввода Element ID (с авто-определением) + кнопка обновления 🔄
  - Текстовое поле для XML
  - Кнопки импорта/очистки
- Правая панель - подписанный XML (текстовое поле + кнопки экспорта/копирования/очистки)
- Нижняя панель - кнопки "Очистить всё" и "Подписать"

**Логика авто-определения Element ID:**
1. При импорте файла или изменении текста ищется паттерн `<ns:RequestData id="..."`
2. Если найден - автоматически заполняется поле Element ID
3. Кнопка обновления 🔄 неактивна (серая)
4. При ручном изменении поля Element ID:
   - Если новое значение совпадает с Element ID из XML → кнопка остается неактивной (серая)
   - Если новое значение отличается → кнопка активируется (зеленая)
5. При нажатии на кнопку - Element ID обновляется из XML, кнопка снова становится неактивной
6. При очистке/импорте - кнопка деактивируется
7. При подписании используется значение из поля или дефолтное "body"

**Зависимости:**
- `customtkinter` - для GUI компонентов
- `CryptoProSigner`, `XMLSigner` - для подписания
- `CertificateDialog` - для выбора сертификата
- `CertificateManager` - для работы с сертификатами
- `Config` - для сохранения настроек

---

### 5. CertificateDialog

**Файл:** `giis_signer/gui/certificate_dialog.py`

**Назначение:** Диалоговое окно для выбора сертификата из списка.

**Основные методы:**
- `__init__(parent, certificate_manager)` - инициализация диалога
- `_create_widgets()` - создание элементов интерфейса
- `_load_certificates()` - загрузка списка сертификатов
- `_add_certificate_item(cert)` - добавление элемента сертификата в список
- `_on_certificate_selected(cert)` - обработчик выбора сертификата
- `_refresh_certificates()` - обновление списка сертификатов
- `_on_select()` - обработчик кнопки "Выбрать"
- `_on_cancel()` - обработчик кнопки "Отмена"
- `get_selected_certificate()` - получение выбранного сертификата

**Компоненты интерфейса:**
- Заголовок диалога
- Скроллируемый список сертификатов (радиокнопки)
- Текстовое поле с подробной информацией о выбранном сертификате
- Кнопки "Обновить", "Выбрать", "Отмена"

**Зависимости:**
- `customtkinter` - для GUI компонентов
- `CertificateManager` - для получения списка сертификатов

---

### 6. CertificateManager

**Файл:** `giis_signer/gui/certificate_manager.py`

**Назначение:** Управление сертификатами для GUI приложения.

**Основные методы:**
- `__init__()` - инициализация менеджера
- `get_certificates(refresh: bool = False) -> List[CertificateInfo]` - получение списка сертификатов
- `find_certificate_by_thumbprint(thumbprint: str) -> Optional[CertificateInfo]` - поиск сертификата по отпечатку
- `_format_date(date_value) -> str` - форматирование даты
- `_check_validity(cert) -> bool` - проверка действительности сертификата

**Константы:**
- `CAPICOM_CURRENT_USER_STORE = 2`
- `CAPICOM_STORE_OPEN_READ_ONLY = 0`
- `CAPICOM_MY_STORE = "My"`

**Зависимости:**
- `win32com.client` - для работы с COM-объектами
- `CertificateInfo` - dataclass для хранения информации о сертификате

---

### 7. CertificateInfo (dataclass)

**Файл:** `giis_signer/gui/certificate_manager.py`

**Назначение:** Хранение информации о сертификате.

**Поля:**
- `thumbprint: str` - отпечаток сертификата
- `subject_name: str` - имя субъекта
- `issuer_name: str` - имя издателя
- `valid_from: str` - дата начала действия
- `valid_to: str` - дата окончания действия
- `serial_number: str` - серийный номер
- `is_valid: bool` - флаг действительности

**Основные методы:**
- `get_display_name() -> str` - получение отображаемого имени (CN + последние 8 символов thumbprint)
- `get_tooltip() -> str` - получение подсказки с полной информацией
- `_extract_cn(subject: str) -> str` - извлечение CN из subject строки

---

### 8. Toast и ToastManager

**Файл:** `giis_signer/gui/toast.py`

**Назначение:** Система неблокирующих уведомлений в стиле push-notifications.

#### Toast (класс)

**Методы:**
- `__init__(parent, message: str, duration: int, type: Literal["success", "info", "warning", "error"])` - создание уведомления
- `show(x: int, y: int)` - показать в указанной позиции
- `hide()` - скрыть уведомление

**Типы уведомлений:**
- `success` - зеленое (✅) - успешные операции
- `info` - синее (ℹ️) - информационные сообщения
- `warning` - желтое (⚠️) - предупреждения
- `error` - красное (❌) - ошибки

**Параметры:**
- `duration` - длительность отображения в миллисекундах (по умолчанию 3000)
- `message` - текст уведомления
- `type` - тип уведомления

#### ToastManager (класс)

**Методы:**
- `__init__(parent)` - инициализация менеджера
- `show(message: str, type: str, duration: int)` - показать уведомление
- `success(message: str, duration: int = 3000)` - показать success-уведомление
- `info(message: str, duration: int = 3000)` - показать info-уведомление
- `warning(message: str, duration: int = 3000)` - показать warning-уведомление
- `error(message: str, duration: int = 3000)` - показать error-уведомление

**Цветовая схема:**
- `success` - яркий зеленый (#28a745) с белым текстом
- `info` - яркий голубой (#17a2b8) с белым текстом
- `warning` - яркий желтый (#ffc107) с темным текстом (#212529)
- `error` - яркий красный (#dc3545) с белым текстом

**Особенности:**
- Уведомления появляются в правом верхнем углу
- При наличии нескольких уведомлений они выстраиваются вертикально (сверху вниз)
- Максимум 3 уведомления одновременно
- Новое уведомление появляется сверху, старое исчезает снизу
- Автоматическое удаление после истечения времени
- Неблокирующие - не требуют подтверждения пользователя
- Автоматическое перепозиционирование при удалении

---

### 9. Config

**Файл:** `giis_signer/gui/config.py`

**Назначение:** Управление конфигурацией GUI приложения.

**Основные методы:**
- `__init__(app_name: str = "giis-signer")` - инициализация конфигурации
- `load()` - загрузка конфигурации из файла
- `save()` - сохранение конфигурации в файл
- `get(key: str, default: Any = None) -> Any` - получение значения по ключу
- `set(key: str, value: Any)` - установка значения
- `get_last_certificate_thumbprint() -> Optional[str]`
- `set_last_certificate_thumbprint(thumbprint: str)`
- `get_window_geometry() -> Optional[str]`
- `set_window_geometry(geometry: str)`
- `get_theme() -> str`
- `set_theme(theme: str)`
- `get_last_input_dir() -> Optional[str]`
- `set_last_input_dir(directory: str)`
- `get_last_output_dir() -> Optional[str]`
- `set_last_output_dir(directory: str)`
- `clear()` - очистка всей конфигурации

**Расположение файла конфигурации:**
- Windows: `%APPDATA%/giis-signer/config.json`
- Linux/macOS: `~/.config/giis-signer/config.json`

**Зависимости:**
- `json` - для сериализации конфигурации
- `pathlib.Path` - для работы с путями

---

## Исключения

### CryptoProException
**Базовый класс:** `Exception`
**Модуль:** `cryptopro_signer.py`
**Назначение:** Ошибки при работе с КриптоПро CSP

### XMLSignerException
**Базовый класс:** `Exception`
**Модуль:** `xml_signer.py`
**Назначение:** Ошибки при формировании XML-подписи

---

## Диаграмма зависимостей

```
cli.py
  └── CryptoProSigner (cryptopro_signer.py)
  └── XMLSigner (xml_signer.py)
        ├── CryptoProSigner
        ├── xmlcanon (внешняя библиотека)
        └── smev_transform (внешний пакет)

diagnostics.py
  ├── SignatureChecker
  │     ├── xmlcanon
  │     └── smev_transform
  └── CryptoProSigner (для проверки КриптоПро)

__init__.py
  ├── CryptoProSigner
  ├── XMLSigner
  └── diagnostics (все функции)
```

---

## Внешние зависимости

### Библиотеки Python
- `pywin32>=305` - для работы с COM-интерфейсом Windows
- `lxml>=4.9.0` - для обработки XML
- `xmlcanon>=1.0.0` - для ExcC14N каноникализации
- `smev-transform>=2.0.0` - для SMEV-трансформации

### Системные зависимости
- **КриптоПро CSP 4.0+** - для криптографических операций с ГОСТ
- **Windows OS** - из-за зависимости от COM-интерфейса КриптоПро

---

**Последнее обновление:** 2025-10-01
**Версия проекта:** 1.0.0
