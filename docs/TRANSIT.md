# GIIS-Signer - История разработки и технический контекст

## 📋 Содержание
- [Цель проекта](#цель-проекта)
- [Текущий статус](#текущий-статус)
- [Архитектура](#архитектура)
- [Решённые проблемы](#решённые-проблемы)
- [Известные ограничения](#известные-ограничения)
- [Критические технические детали](#критические-технические-детали)

## Цель проекта

Разработать **производственно-готовую** Python-утилиту для подписания XML-документов по стандарту **XMLDSig** с требованиями **ГИИС ДМДК** (Государственная информационная система мониторинга драгоценных металлов и драгоценных камней), используя **КриптоПро CSP**.

### Ключевые требования
- ✅ Подписание SOAP XML-документов с ГОСТ-алгоритмами
- ✅ Интеграция с КриптоПро CSP через COM-интерфейс
- ✅ Применение Exclusive Canonicalization (ExcC14N)
- ✅ Поддержка SMEV-трансформации
- ✅ Соответствие стандарту XMLDSig
- ✅ Простой CLI и программный API

## Текущий статус

### ✅ Релиз v1.0.0 (2025-10-01)

**Проект готов к использованию в производстве!**

Все критические проблемы решены:
- ✅ Подписание работает корректно
- ✅ ГИИС ДМДК принимает подписанные документы
- ✅ Подпись математически верна (проверено на dss.cryptopro.ru)
- ✅ Все трансформации работают корректно
- ✅ DigestValue в правильном формате (Base64)
- ✅ Структура соответствует требованиям ГИИС ДМДК

### Статус функций

| Функция | Статус | Примечание |
|---------|--------|------------|
| Поиск сертификатов | ✅ Работает | По thumbprint или subject |
| Вычисление хеша ГОСТ | ✅ Работает | ГОСТ Р 34.11-2012 (256 бит) |
| Подписание ГОСТ | ✅ Работает | ГОСТ Р 34.10-2012 (256 бит) |
| ExcC14N каноникализация | ✅ Работает | Exclusive Canonicalization 1.0 |
| SMEV-трансформация | ✅ Работает | urn://smev-gov-ru/xmldsig/transform |
| Формирование XMLDSig | ✅ Работает | Полная структура Signature |
| CLI-интерфейс | ✅ Работает | Удобный интерфейс командной строки |
| Программный API | ✅ Работает | Использование как библиотека |
| Отладочные утилиты | ✅ Работает | Полный набор инструментов |

## Архитектура

### Структура проекта

```
giis-signer/
├── giis_signer/                    # Основной пакет
│   ├── __init__.py                 # Публичный API
│   ├── cli.py                      # CLI-интерфейс (точка входа)
│   ├── cryptopro_signer.py         # Интеграция с КриптоПро CSP
│   ├── xml_signer.py               # Формирование XMLDSig подписи
│   ├── exc_c14n_module/            # ExcC14N каноникализация
│   │   └── transform.py
│   └── smev_transform/             # SMEV трансформация
│       └── transform.py
├── examples/                       # Примеры шаблонов
│   ├── template.xml                # Базовый SOAP-шаблон
│   └── example_rq_1c.xml           # Пример запроса из 1С
├── tests/                          # Тесты и отладка
│   ├── test_com.py                 # Проверка КриптоПро COM
│   ├── debug_tools.py              # Единый инструмент диагностики
│   ├── test_body_transform.py      # Тест трансформаций body
│   ├── test_smev_transform.py      # Тест SMEV-трансформации
│   └── verify_signaturevalue.py    # Проверка SignatureValue
├── docs/                           # Документация
│   ├── DEVELOPMENT.md              # Этот файл
│   ├── CRYPTOPRO_COM.md            # Документация COM-интерфейса
│   ├── SMEV.md                     # SMEV-трансформация
│   └── SMEV_TESTS.md               # Тесты SMEV
├── pyproject.toml                  # Конфигурация пакета
├── README.md                       # Основная документация
├── LICENSE                         # MIT License
└── .gitignore                      # Исключения Git
```

### Модули

#### 1. `cryptopro_signer.py`
**Назначение:** Интеграция с КриптоПро CSP через COM-интерфейс

**Класс:** `CryptoProSigner`

**Функционал:**
- Поиск сертификатов в хранилище Windows по thumbprint или subject
- Вычисление хеша ГОСТ Р 34.11-2012 (256 бит)
- Подписание хеша с ГОСТ Р 34.10-2012 (256 бит)
- Экспорт сертификата в Base64
- Конвертация HEX ↔ Base64

**Ключевые особенности:**
- Использует COM-объекты: `CAdESCOM.Store`, `CAdESCOM.HashedData`, `CAdESCOM.RawSignature`
- Автоматическая нормализация thumbprint (удаление пробелов, uppercase)
- **Реверс подписи:** `signature_bytes[::-1]` - критическое требование КриптоПро
- **Конвертация хеша:** КриптоПро возвращает HEX, для XMLDSig требуется Base64

**COM-константы:**
```python
CAPICOM_CURRENT_USER_STORE = 2
CAPICOM_STORE_OPEN_READ_ONLY = 0
CAPICOM_CERTIFICATE_FIND_SHA1_HASH = 0
CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256 = 101
CADESCOM_BASE64_TO_BINARY = 1
```

#### 2. `xml_signer.py`
**Назначение:** Формирование XML-подписи в формате XMLDSig

**Класс:** `XMLSigner`

**Алгоритм подписания:**
1. **Извлечение элемента** - поиск элемента с `id="body"` в SOAP
2. **ExcC14N каноникализация** - применение к элементу body
3. **SMEV-трансформация** - специфичная трансформация для госсистем
4. **Вычисление DigestValue** - хеш ГОСТ Р 34.11-2012 в Base64
5. **Формирование SignedInfo** - создание с метаданными (с xmlns:ds для каноникализации)
6. **Каноникализация SignedInfo** - применение ExcC14N
7. **Подписание SignedInfo** - создание подписи через КриптоПро
8. **Реверс подписи** - обязательная операция
9. **Формирование Signature** - финальная XML-структура (без xmlns:ds, т.к. наследуется)
10. **Вставка в SOAP** - текстовая замена для сохранения форматирования

**Структура подписи:**
```xml
<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Id="signature-xxx">
  <ds:SignedInfo>
    <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
    <ds:SignatureMethod Algorithm="urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102012-gostr34112012-256"/>
    <ds:Reference URI="#body">
      <ds:Transforms>
        <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
        <ds:Transform Algorithm="urn://smev-gov-ru/xmldsig/transform"/>
      </ds:Transforms>
      <ds:DigestMethod Algorithm="urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34112012-256"/>
      <ds:DigestValue>BASE64_HASH</ds:DigestValue>
    </ds:Reference>
  </ds:SignedInfo>
  <ds:SignatureValue>BASE64_SIGNATURE</ds:SignatureValue>
  <ds:KeyInfo>
    <ds:X509Data>
      <ds:X509Certificate>BASE64_CERT</ds:X509Certificate>
    </ds:X509Data>
  </ds:KeyInfo>
</ds:Signature>
```

#### 3. `cli.py` (ex-main.py)
**Назначение:** CLI-интерфейс для подписания документов

**Команда:** `giis-signer`

**Параметры:**
- `input` - путь к XML-шаблону (обязательный)
- `-o, --output` - путь к выходному файлу (опционально)
- `-t, --thumbprint` - отпечаток сертификата SHA1 (один из -t/-s обязателен)
- `-s, --subject` - имя субъекта сертификата (один из -t/-s обязателен)
- `-e, --element-id` - ID элемента для подписания (по умолчанию: `body`)
- `-n, --signature-element` - имя элемента для вставки подписи (по умолчанию: `CallerSignature`)

**Примеры:**
```bash
# Базовое использование
giis-signer template.xml -t c755d5b4b7e1554b632f0c989427eba47b176c3a -o signed.xml

# По имени субъекта
giis-signer template.xml -s "CN=Иванов Иван" -o signed.xml

# С кастомными параметрами
giis-signer input.xml -t <thumbprint> -e "RequestBody" -n "Signature" -o output.xml
```

#### 4. Вспомогательные модули

##### `exc_c14n_module/`
Реализация **Exclusive Canonicalization 1.0**
- Алгоритм: `http://www.w3.org/2001/10/xml-exc-c14n#`
- Используется для каноникализации элемента body и SignedInfo
- Критически важен для корректного вычисления хешей

##### `smev_transform/`
Реализация **SMEV-трансформации**
- Алгоритм: `urn://smev-gov-ru/xmldsig/transform`
- Специфичная трансформация для российских госсистем (СМЭВ)
- Применяется после ExcC14N перед хешированием

### Отладочные утилиты

#### `diagnostics.py`
Единый модуль диагностики в основном пакете
- **Проверка КриптоПро:** `python -m giis_signer.diagnostics --check-cryptopro`
- **Диагностика подписи:** `python -m giis_signer.diagnostics --check-signature signed.xml`
- **Полная диагностика:** `python -m giis_signer.diagnostics --check-signature signed.xml --full`

**Функции:**
- `check_cryptopro_available()` - проверка COM-объектов
- `list_certificates()` - список сертификатов
- `check_signature(xml_file, verbose)` - проверка XML-подписи
- `SignatureChecker` - класс для детальной проверки

**Доступен из кода:**
```python
from giis_signer import check_cryptopro_available, check_signature

if check_cryptopro_available():
    is_valid = check_signature("signed.xml", verbose=True)
```

## Решённые проблемы

### Проблема 1: Ошибка создания COM-объекта Store
**Дата:** Начало разработки
**Симптом:** `(-2147221005, 'Недопустимая строка с указанием класса', None, None)`

**Причина:** Неправильный ProgID или отсутствие регистрации COM-объектов

**Решение:**
1. Пробовать оба варианта: `CAdESCOM.Store` и `CAPICOM.Store`
2. Использовать правильные константы из документации КриптоПро
3. Проверить установку и версию КриптоПро CSP (требуется 4.0+)

### Проблема 2: Сертификат не найден
**Дата:** Начало разработки
**Симптом:** `Сертификат не найден` при правильном thumbprint

**Причины:**
- Thumbprint с пробелами или в неправильном регистре
- Неправильный параметр `ValidOnly` в методе `Find()`

**Решение:**
```python
# Нормализация thumbprint
self.thumbprint = thumbprint.replace(" ", "").upper() if thumbprint else None

# Правильный вызов Find
certificates = certificates.Find(
    CAPICOM_CERTIFICATE_FIND_SHA1_HASH,
    self.thumbprint,
    False  # ValidOnly = False (важно: не True или 0!)
)
```

### Проблема 3: ГИИС ДМДК код ошибки -2 (нет DigestValue)
**Дата:** Середина разработки
**Симптом:** DigestValue в HEX формате вместо Base64

**Причина:** КриптоПро возвращает хеш в HEX через свойство `HashedData.Value`

**Решение:**
```python
# Получаем хеш в HEX от КриптоПро
hash_hex = hasher.Value

# Конвертируем HEX → Base64 для XMLDSig
hash_bytes = bytes.fromhex(hash_hex)
hash_base64 = base64.b64encode(hash_bytes).decode('ascii')
```

**До:** `B5A6221E42BEB71B822BBCD3CC8140DE11EFF076D4B72FFF7456DCFB60169F73` (64 символа, HEX)
**После:** `taYiHkK+txuCK7zTzIFA3hHv8HbUty//dFbc+2AWn3M=` (44 символа, Base64) ✅

### Проблема 4: Самозакрывающиеся теги в SignedInfo
**Дата:** Середина разработки
**Симптом:** `<ds:CanonicalizationMethod ... />` вместо `<ds:CanonicalizationMethod...></ds:CanonicalizationMethod>`

**Причина:**
1. XML-шаблон содержал самозакрывающиеся теги
2. `ElementTree.tostring()` автоматически форматирует пустые элементы как self-closing

**Решение:**
1. **В шаблоне SignedInfo:** Использовать самозакрывающиеся теги БЕЗ ПРОБЕЛА перед `/>`:
```python
# Правильно (по эталону ГИИС ДМДК):
<ds:CanonicalizationMethod Algorithm="..."/>  # Без пробела!

# Неправильно:
<ds:CanonicalizationMethod Algorithm="..." />  # С пробелом
```

2. **При вставке подписи:** Использовать текстовую замену вместо парсинга:
```python
# НЕ использовать ElementTree (создаёт self-closing по-своему):
# signature_element = ET.fromstring(signature_xml)
# caller_signature.append(signature_element)

# Использовать regex-замену:
pattern = rf'<(\w+:)?{signature_element_name}(\s[^>]*)?>.*?</\1{signature_element_name}>'
result = re.sub(pattern, replace_func, soap_xml, flags=re.DOTALL)
```

### Проблема 5: Подписание хеша с неправильным форматом
**Дата:** Середина разработки
**Симптом:** Ошибка при вызове `SetHashValue()` с Base64

**Причина:** `SetHashValue()` ожидает HEX формат, а не Base64

**Решение:**
```python
# Для вставки в SignedInfo используем Base64:
digest_value_base64 = base64.b64encode(hash_bytes).decode('ascii')

# Для подписания конвертируем Base64 обратно в HEX:
hash_bytes = base64.b64decode(hash_value)
hash_hex = hash_bytes.hex().upper()
hasher.SetHashValue(hash_hex)
```

### Проблема 6: Форматирование нарушает подпись
**Дата:** 2025-10-01
**Симптом:** После добавления отступов в подпись ГИИС ДМДК возвращает ошибку

**Причина:** Любое изменение пробелов/переносов строк изменяет хеш элемента

**Решение:**
- **НЕ** форматировать подписанный XML
- Вставлять подпись как есть, без дополнительных отступов
- XML остаётся нечитаемым, но подпись валидна

**Статус:** ✅ Решено - форматирование отключено

## Известные ограничения

### 1. Форматирование XML
⚠️ **Подписанный XML нельзя переформатировать** - это нарушит целостность подписи.

Элемент `<ns:CallerSignature>` содержит подпись в одну строку:
```xml
<ns:CallerSignature><ds:Signature ...>...</ds:Signature></ns:CallerSignature>
```

Это некрасиво, но необходимо для сохранения валидности подписи.

### 2. Платформа
⚠️ **Только Windows** - из-за зависимости от КриптоПро CSP COM-интерфейса.

Нет планов по поддержке Linux/macOS, так как КриптоПро CSP доступен только на Windows.

### 3. Атрибут id vs Id
⚠️ **ОБЯЗАТЕЛЬНО использовать маленькую букву:** `id="body"` (не `Id` или `ID`)

ГИИС ДМДК строго требует `id` с маленькой буквы, хотя XMLDSig допускает разные варианты.

### 4. Реверс подписи
⚠️ **ОБЯЗАТЕЛЕН реверс подписи** - без него подпись не будет валидной.

КриптоПро CSP возвращает подпись в обратном порядке байт, это документированное поведение.

## Критические технические детали

### Порядок операций при подписании

```
1. Чтение SOAP XML
2. Извлечение элемента id="body"
3. ExcC14N каноникализация body
4. SMEV-трансформация
5. Хеш ГОСТ Р 34.11-2012 (256 бит)
6. DigestValue = Base64(hash)
7. Формирование SignedInfo (С xmlns:ds)
8. ExcC14N каноникализация SignedInfo
9. Хеш канонизированного SignedInfo
10. Подписание хеша через КриптоПро
11. Реверс подписи: signature[::-1]
12. SignatureValue = Base64(reversed_signature)
13. Формирование Signature (БЕЗ xmlns:ds в SignedInfo)
14. Вставка в CallerSignature (текстовая замена)
15. Сохранение результата
```

### Критические требования

| Требование | Значение | Последствия нарушения |
|------------|----------|----------------------|
| **DigestValue формат** | Base64 (не HEX!) | ГИИС ДМДК ошибка -2 |
| **Реверс подписи** | ОБЯЗАТЕЛЕН | Подпись невалидна |
| **Порядок трансформаций** | ExcC14N → SMEV | Неверный DigestValue |
| **Атрибут id** | Маленькая буква: `id="body"` | Элемент не найден |
| **xmlns:ds в SignedInfo** | Нужен для каноникализации, убирается в финале | Неверный хеш SignedInfo |
| **Самозакрывающиеся теги** | Формат `<tag/>` (без пробела) | Может нарушить каноникализацию |
| **Форматирование** | НЕ менять после подписания | Нарушает целостность |

### Алгоритмы и URI

| Операция | Алгоритм | URI |
|----------|----------|-----|
| **Каноникализация** | Exclusive C14N 1.0 | `http://www.w3.org/2001/10/xml-exc-c14n#` |
| **SMEV-трансформация** | SMEV Transform | `urn://smev-gov-ru/xmldsig/transform` |
| **Подпись** | ГОСТ Р 34.10-2012 (256 бит) | `urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102012-gostr34112012-256` |
| **Хеш** | ГОСТ Р 34.11-2012 (256 бит) | `urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34112012-256` |

### Формат SOAP-документа

**Входной шаблон:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ns="urn://xsd.dmdk.goznak.ru/exchange/3.0">
   <soapenv:Header/>
   <soapenv:Body>
      <ns:SendGetContractorRequest>
        <ns:CallerSignature></ns:CallerSignature>
        <ns:RequestData id="body">
           <ns:INN>7813252159</ns:INN>
        </ns:RequestData>
      </ns:SendGetContractorRequest>
   </soapenv:Body>
</soapenv:Envelope>
```

**Ключевые элементы:**
- `id="body"` - элемент, который подписывается
- `<ns:CallerSignature>` - элемент, куда вставляется подпись
- Namespace префиксы могут быть любыми (soapenv, ns, и т.д.)

## Зависимости

```toml
[project]
requires-python = ">=3.8"
dependencies = [
    "pywin32>=305",    # COM-интерфейс КриптоПро
    "lxml>=4.9.0",     # XML обработка
]
```

### Системные зависимости
- **Windows OS** (любая версия с поддержкой КриптоПро CSP)
- **КриптоПро CSP 4.0+** (с поддержкой ГОСТ Р 34.10-2012)
- **Сертификат ГОСТ Р 34.10-2012** (256 бит) в хранилище Windows

## Команды разработки

### Установка в режиме разработки
```bash
pip install -e .
```

### Проверка КриптоПро
```bash
python -m giis_signer.diagnostics --check-cryptopro
```

### Подписание документа
```bash
giis-signer examples/template.xml -t <thumbprint> -o signed.xml
```

### Диагностика подписи
```bash
# Краткая проверка
python -m giis_signer.diagnostics --check-signature signed.xml

# Полная диагностика
python -m giis_signer.diagnostics --check-signature signed.xml --full
```

## История версий

### v1.0.0 (2025-10-01)
- ✅ Первый стабильный релиз
- ✅ Проект переструктурирован как Python-пакет
- ✅ Полная документация (README.md)
- ✅ CLI-интерфейс через entry point
- ✅ Публичный API через `__init__.py`
- ✅ Примеры и тесты организованы
- ✅ MIT License
- ✅ Готов к публикации

### v0.1.0 (Начало разработки)
- ⚠️ Первая версия с основными функциями
- ⚠️ Проблемы с форматированием и COM
- ⚠️ Ошибки ГИИС ДМДК требовали исправления

---

**Последнее обновление:** 2025-10-01
**Версия:** 1.0.0
**Статус:** ✅ Production Ready - Все проблемы ГИИС ДМДК решены
