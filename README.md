# GIIS DМДК XML Signer

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)](https://www.microsoft.com/windows)

Утилита для подписания XML-документов по стандарту XMLDSig с требованиями **ГИИС ДМДК** (Государственная информационная система мониторинга драгоценных металлов и драгоценных камней), используя **КриптоПро CSP**.

## Особенности

- ✅ Подписание XML-документов по стандарту **XMLDSig**
- ✅ Поддержка алгоритмов **ГОСТ Р 34.10-2012** и **ГОСТ Р 34.11-2012**
- ✅ Интеграция с **КриптоПро CSP** через COM-интерфейс
- ✅ Применение **Exclusive Canonicalization (ExcC14N)**
- ✅ Поддержка **SMEV-трансформации** для государственных систем
- ✅ GUI и CLI интерфейсы
- ✅ Standalone exe-файлы (без установки Python)
- ✅ Готов к использованию в производстве

## Безопасность

### VirusTotal Анализ
Standalone exe-файлы регулярно проверяются на VirusTotal для обеспечения безопасности:

[![VirusTotal Scan](https://img.shields.io/badge/VirusTotal-Clean-success)](https://www.virustotal.com/gui/file-analysis/YzI4NTVhMTJjNGJmYTEwOTg4ZGM4NjY5M2RjMjRiZTI6MTc1OTQwMjg0Nw==)

**Последний анализ:** GIIS-Signer-GUI.exe
- **Результат:** 0/72 антивирусов обнаружили угрозы
- **Детали:** [Просмотреть полный отчет](https://www.virustotal.com/gui/file-analysis/YzI4NTVhMTJjNGJmYTEwOTg4ZGM4NjY5M2RjMjRiZTI6MTc1OTQwMjg0Nw==)

Exe-файлы созданы с помощью PyInstaller и содержат:
- Весь код Python приложения
- Необходимые библиотеки и зависимости
- Python runtime

⚠️ **Важно:** Exe-файлы НЕ содержат и НЕ хранят закрытые ключи. Все криптографические операции выполняются через КриптоПро CSP с использованием сертификатов из хранилища Windows.

## Связанные репозитории

Проект использует следующие специализированные библиотеки для работы с ГОСТ криптографией:

- **[xmlcanon](https://github.com/imdeniil/xmlcanon)** - Реализация Exclusive XML Canonicalization (ExcC14N) для Python
- **[smev-transform](https://github.com/imdeniil/smev-transform)** - Реализация SMEV-трансформации для электронной подписи государственных документов
- **[giis-srv-selector](https://github.com/imdeniil/giis-srv-selector)** - Утилита для выбора сервера ГИИС ДМДК (тестовый/продуктовый)

Все библиотеки разработаны специально для обеспечения совместимости с требованиями ГИИС ДМДК и других государственных информационных систем РФ.

## Требования

### Системные требования
- **ОС**: Windows (из-за зависимости от КриптоПро CSP)
- **Python**: >= 3.8
- **КриптоПро CSP**: Установлен и настроен
- **КриптоПро ЭЦП Browser plug-in**: Установлен ([скачать](https://www.cryptopro.ru/products/cades/plugin))
- **Сертификат**: ГОСТ Р 34.10-2012 (256 бит) в хранилище сертификатов Windows

### Python-зависимости
- `pywin32>=305` - для работы с COM-интерфейсом КриптоПро
- `lxml>=4.9.0` - для обработки XML

## Установка

### 1. Установка КриптоПро CSP

Скачайте и установите [КриптоПро CSP](https://www.cryptopro.ru/products/csp/downloads) с официального сайта.

Также установите [КриптоПро ЭЦП Browser plug-in](https://www.cryptopro.ru/products/cades/plugin) для работы с COM-интерфейсом.

### 2. Установка Python и uv

Убедитесь, что у вас установлен Python 3.8 или выше.

Установите uv package manager:
```powershell
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Или используйте pip:
```bash
pip install uv
```

### 3. Установка утилиты

#### Вариант А: Из Git репозитория

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/giis-signer.git
cd giis-signer

# Создание виртуального окружения и установка зависимостей
uv venv
uv sync
uv pip install -e .
```

#### Вариант Б: Копирование папки на новый ПК

Если вы скопировали папку проекта на новый компьютер:

```bash
# Перейдите в папку проекта
cd путь\к\giis-signer

# Создайте виртуальное окружение
uv venv

# Установите зависимости из lockfile
uv sync

# Установите пакет в editable режиме для регистрации entry points
uv pip install -e .
```

**Запуск GUI приложения:**
```bash
# Вариант 1: Через entry point (рекомендуется)
.venv\Scripts\giis-signer-gui.exe

# Вариант 2: Через Python модуль
.venv\Scripts\python.exe -m giis_signer.gui.app
```

**Запуск CLI:**
```bash
# Вариант 1: Через entry point
.venv\Scripts\giis-signer.exe template.xml -t <thumbprint> -o signed.xml

# Вариант 2: Через Python модуль
.venv\Scripts\python.exe -m giis_signer.cli template.xml -t <thumbprint> -o signed.xml
```

## Использование

### GUI приложение (Рекомендуется)

Запустите GUI приложение:

```bash
giis-signer-gui
```

#### Возможности GUI:
- ✅ Интуитивно понятный интерфейс
- ✅ Двухпанельный режим: входной XML → подписанный XML
- ✅ Импорт/экспорт XML файлов
- ✅ Копирование результата в буфер обмена
- ✅ Выбор сертификата из списка с подробной информацией
- ✅ Автосохранение последнего выбранного сертификата
- ✅ Кнопки очистки полей (по отдельности и вместе)
- ✅ Поддержка темной и светлой темы
- ✅ Сохранение размера окна и последних директорий
- ✅ Авто-определение Element ID для подписания из XML
- ✅ Возможность ручной корректировки Element ID
- ✅ Кнопка обновления Element ID (активируется при ручном изменении)
- ✅ Неблокирующие toast-уведомления вместо модальных окон

### Командная строка

#### Базовый пример (Element ID определяется автоматически)

```bash
giis-signer template.xml -t c755d5b4b7e1554b632f0c989427eba47b176c3a -o signed.xml
```

**Примечание:** Element ID автоматически определяется из XML. Если не найден, используется "body".

#### Пример с указанием субъекта сертификата

```bash
giis-signer template.xml -s "CN=Иванов Иван Иванович" -o signed.xml
```

#### Пример с явным указанием Element ID

```bash
giis-signer input.xml -t <thumbprint> -e "requestBody" -o output.xml
```

#### Пример с кастомными параметрами

```bash
giis-signer input.xml -t <thumbprint> -e "RequestBody" -n "Signature" -o output.xml
```

### Параметры CLI

| Параметр | Описание | Обязательный |
|----------|----------|--------------|
| `input` | Путь к входному XML-файлу (SOAP-шаблон) | ✅ Да |
| `-o, --output` | Путь к выходному файлу (stdout если не указан) | ❌ Нет |
| `-t, --thumbprint` | Отпечаток сертификата (SHA1, HEX) | ⚠️ Один из `-t` или `-s` |
| `-s, --subject` | Имя субъекта сертификата | ⚠️ Один из `-t` или `-s` |
| `-e, --element-id` | ID элемента для подписания (авто-определение или `body`) | ❌ Нет |
| `-n, --signature-element` | Имя элемента для вставки подписи (по умолчанию: `CallerSignature`) | ❌ Нет |

### Использование как библиотеки

```python
from giis_signer import CryptoProSigner, XMLSigner

# Инициализация подписанта
signer = CryptoProSigner(thumbprint="c755d5b4b7e1554b632f0c989427eba47b176c3a")

# Поиск сертификата
certificate = signer.find_certificate()
print(f"Найден сертификат: {certificate.SubjectName}")

# Создание XML подписанта
xml_signer = XMLSigner(signer)

# Чтение XML-шаблона
with open("template.xml", "r", encoding="utf-8") as f:
    soap_xml = f.read()

# Подписание документа
signed_xml = xml_signer.sign_soap_request(
    soap_xml,
    element_id="body",
    signature_element_name="CallerSignature"
)

# Сохранение результата
with open("signed.xml", "w", encoding="utf-8") as f:
    f.write(signed_xml)
```

## Формат SOAP-документа

Входной XML-документ должен иметь следующую структуру:

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
- `id="body"` - элемент, который будет подписан (Element ID может быть любым)
- `<ns:CallerSignature>` - элемент, куда будет вставлена подпись

**Примечание:** В GUI приложении Element ID автоматически определяется из XML по паттерну `<ns:RequestData id="...">`. Значение можно изменить вручную перед подписанием.

## Алгоритм подписания

1. **Каноникализация ExcC14N** → применяется к элементу с `id="body"`
2. **SMEV-трансформация** → применяется к результату каноникализации
3. **Хеширование ГОСТ Р 34.11-2012** → вычисление дайджеста трансформированных данных
4. **Формирование SignedInfo** → создание метаданных подписи с DigestValue
5. **Каноникализация SignedInfo** → применение ExcC14N к SignedInfo
6. **Подписание** → создание подписи с помощью КриптоПро (ГОСТ Р 34.10-2012)
7. **Реверс подписи** → обязательное требование КриптоПро CSP
8. **Формирование Signature** → создание финальной XML-структуры с подписью

## Поддерживаемые алгоритмы

| Тип | Алгоритм | URI |
|-----|----------|-----|
| **Каноникализация** | Exclusive XML Canonicalization 1.0 | `http://www.w3.org/2001/10/xml-exc-c14n#` |
| **Трансформация** | SMEV Transform | `urn://smev-gov-ru/xmldsig/transform` |
| **Подпись** | ГОСТ Р 34.10-2012 (256 бит) | `urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102012-gostr34112012-256` |
| **Хеширование** | ГОСТ Р 34.11-2012 (256 бит) | `urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34112012-256` |

## Структура проекта

```
giis-signer/
├── giis_signer/               # Основной пакет
│   ├── __init__.py            # Экспорты модуля
│   ├── cli.py                 # CLI-интерфейс
│   ├── cryptopro_signer.py    # Интеграция с КриптоПро CSP
│   ├── xml_signer.py          # Формирование XMLDSig подписи
│   ├── diagnostics.py         # Утилиты диагностики
│   ├── exc_c14n_module/       # ExcC14N каноникализация
│   └── smev_transform/        # SMEV трансформация
├── examples/                  # Примеры шаблонов
│   ├── template.xml           # Базовый SOAP-шаблон
│   └── example_rq_1c.xml      # Пример запроса 1С
├── tests/                     # Тесты (пустая директория)
├── docs/                      # Документация
│   ├── DEVELOPMENT.md         # История разработки
│   ├── CRYPTOPRO_COM.md       # Документация COM-интерфейса
│   └── SMEV.md                # Описание SMEV-трансформации
├── pyproject.toml             # Конфигурация проекта
├── README.md                  # Этот файл
└── LICENSE                    # Лицензия MIT
```

## Отладка и диагностика

### Проверка доступности КриптоПро CSP

```bash
python -m giis_signer.diagnostics --check-cryptopro
```

Проверяет:
- Доступность COM-объектов КриптоПро
- Список доступных сертификатов в хранилище

### Диагностика подписи

```bash
# Краткая проверка
python -m giis_signer.diagnostics --check-signature signed.xml

# Полная диагностика
python -m giis_signer.diagnostics --check-signature signed.xml --full
```

Проверяет:
- Корректность структуры подписи
- Валидность DigestValue
- Соответствие требованиям ГИИС ДМДК

### Использование в коде

```python
from giis_signer import check_cryptopro_available, list_certificates, check_signature

# Проверка КриптоПро
if check_cryptopro_available():
    list_certificates()

# Проверка подписи
is_valid = check_signature("signed.xml", verbose=True)
```

## Известные особенности

### Критические требования

⚠️ **DigestValue** - ОБЯЗАТЕЛЬНО в формате Base64 (не HEX)
⚠️ **Реверс подписи** - ОБЯЗАТЕЛЕН для совместимости с КриптоПро
⚠️ **Порядок трансформаций** - ExcC14N → SMEV (не наоборот!)
⚠️ **Атрибут id** - использовать маленькие буквы: `id="body"` (не `Id` или `ID`)
⚠️ **Форматирование** - не изменяйте форматирование подписанного XML, это нарушит целостность

### Поиск отпечатка сертификата

**Windows:**
1. Откройте `certmgr.msc`
2. Перейдите в "Личные" → "Сертификаты"
3. Откройте нужный сертификат → вкладка "Состав"
4. Найдите поле "Отпечаток" и скопируйте значение
5. Удалите пробелы: `c7 55 d5 b4...` → `c755d5b4...`

**PowerShell:**
```powershell
Get-ChildItem Cert:\CurrentUser\My | Select-Object Subject, Thumbprint
```

## Устранение неполадок

### Ошибка: "Недопустимая строка с указанием класса"

**Причина:** КриптоПро CSP не установлен или COM-объекты не зарегистрированы.

**Решение:**
1. Убедитесь, что КриптоПро CSP установлен
2. Перезапустите компьютер после установки
3. Проверьте версию КриптоПро (требуется 4.0 или выше)

### Ошибка: "Сертификат не найден"

**Причина:** Неверный отпечаток или сертификат отсутствует в хранилище.

**Решение:**
1. Проверьте отпечаток (без пробелов, верхний регистр)
2. Убедитесь, что сертификат находится в хранилище "Личные"
3. Используйте `tests/test_com.py` для просмотра доступных сертификатов

### Ошибка ГИИС ДМДК: код -12 (нарушена целостность)

**Причина:** Проблема с каноникализацией SignedInfo.

**Решение:**
1. Убедитесь, что используется актуальная версия утилиты
2. Не изменяйте форматирование подписанного XML вручную
3. Проверьте соответствие шаблона требованиям ГИИС ДМДК

## Вклад в проект

Приветствуются любые улучшения проекта:

1. Форкните репозиторий
2. Создайте ветку для изменений (`git checkout -b feature/improvement`)
3. Зафиксируйте изменения (`git commit -am 'Add new feature'`)
4. Отправьте в репозиторий (`git push origin feature/improvement`)
5. Создайте Pull Request

## Лицензия

Проект распространяется под лицензией [MIT](LICENSE).

## Авторы

Проект разработан для работы с ГИИС ДМДК (Государственная информационная система мониторинга драгоценных металлов и драгоценных камней).

## Поддержка

При возникновении проблем:
1. Проверьте раздел [Устранение неполадок](#устранение-неполадок)
2. Изучите документацию в папке [docs/](docs/)
3. Создайте Issue в репозитории с подробным описанием проблемы

## Благодарности

- **КриптоПро** - за разработку КриптоПро CSP
- **SMEV** - за спецификацию SMEV-трансформации
- **Сообщество разработчиков** - за вклад в проект

---

**⚠️ Важно:** Утилита предназначена исключительно для легального использования в соответствии с законодательством Российской Федерации. Убедитесь, что у вас есть все необходимые права и лицензии на использование КриптоПро CSP и ГОСТ-сертификатов.
