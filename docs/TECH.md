# Технический стек и архитектурные принципы GIIS Signer

## Архитектурные принципы

### 1. Модульность
Проект разделен на независимые модули с четкими границами ответственности:
- **cryptopro_signer.py** - взаимодействие с КриптоПро CSP
- **xml_signer.py** - формирование XMLDSig подписи
- **cli.py** - пользовательский интерфейс
- **diagnostics.py** - диагностика и проверка

### 2. Разделение ответственности
Каждый модуль отвечает за одну конкретную задачу:
- Криптография изолирована в CryptoProSigner
- XML-обработка изолирована в XMLSigner
- CLI логика отделена от бизнес-логики

### 3. Зависимость от абстракций
- XMLSigner зависит от интерфейса CryptoProSigner
- Минимальная связанность между модулями
- Легкая замена компонентов при необходимости

### 4. Обработка ошибок
- Каждый модуль определяет собственные исключения
- CryptoProException для ошибок криптографии
- XMLSignerException для ошибок XML-обработки
- Четкие сообщения об ошибках для пользователя

### 5. Принцип единственной ответственности (SRP)
- Класс выполняет одну задачу
- Методы делают одно действие
- Минимум side-effects

## Технологический стек

### Язык программирования
- **Python 3.8+**
  - Современные возможности типизации (typing)
  - f-strings для форматирования
  - Поддержка type hints

### Операционная система
- **Windows** (обязательно)
  - Зависимость от КриптоПро CSP COM-интерфейса
  - Win32 API через pywin32

### Менеджер пакетов
- **uv** (основной)
  - Быстрый менеджер пакетов на Rust
  - Современный lockfile (uv.lock)
  - Поддержка виртуальных окружений
- **pip** (альтернативный)
  - Для совместимости со стандартными инструментами

### Build система
- **setuptools + pyproject.toml**
  - Современный формат конфигурации (PEP 518/621)
  - Declarative конфигурация
  - Entry points для CLI команд

## Основные зависимости

### Runtime зависимости

#### pywin32 >= 305
**Назначение:** Работа с COM-интерфейсом Windows
- Доступ к КриптоПро CSP через COM
- Работа с сертификатами Windows
- Вызов криптографических функций

**Использование:**
```python
import win32com.client
store = win32com.client.Dispatch("CAdESCOM.Store")
```

#### lxml >= 4.9.0
**Назначение:** Обработка XML документов
- Парсинг XML
- XPath запросы
- Namespace management

**Использование:**
```python
from lxml import etree
root = etree.fromstring(xml_string)
```

#### xmlcanon >= 1.0.0
**Назначение:** Exclusive Canonicalization (ExcC14N)
- Каноникализация XML согласно W3C стандарту
- Используется для подготовки данных к подписанию

**Использование:**
```python
from xmlcanon import canonicalize_xml
canonical = canonicalize_xml(xml_string)
```

#### smev-transform >= 2.0.0
**Назначение:** SMEV-трансформация для госсистем
- Полная реализация 9-шагового алгоритма СМЭВ
- Соответствие спецификации СМЭВ 3.5.0.27
- Декодирование текста и атрибутов

**Использование:**
```python
from smev_transform import Transform
transformer = Transform()
transformed = transformer.process(xml_string)
```

### Development зависимости

#### pytest >= 7.0.0
**Назначение:** Фреймворк для тестирования
- Unit тесты
- Integration тесты
- Fixtures и параметризация

#### black >= 22.0.0
**Назначение:** Автоматическое форматирование кода
- Единый стиль кода
- PEP 8 compliance
- Настройки в pyproject.toml

#### flake8 >= 4.0.0
**Назначение:** Линтинг и проверка стиля
- Обнаружение ошибок кода
- PEP 8 проверки
- Сложность кода

#### mypy >= 0.950
**Назначение:** Статическая типизация
- Проверка type hints
- Обнаружение ошибок типов
- Улучшение качества кода

## Системные зависимости

### КриптоПро CSP 4.0+
**Назначение:** Криптография по ГОСТ стандартам
- ГОСТ Р 34.10-2012 (256 бит) - подпись
- ГОСТ Р 34.11-2012 (256 бит) - хеширование
- COM-интерфейс для интеграции

**Компоненты:**
- CAdESCOM.Store - хранилище сертификатов
- CAdESCOM.HashedData - вычисление хешей
- CAdESCOM.RawSignature - создание подписи

### Сертификаты
**Требования:**
- Алгоритм: ГОСТ Р 34.10-2012 (256 бит)
- Расположение: Хранилище "Личные" текущего пользователя
- Формат: X.509 с поддержкой ГОСТ

## Стандарты и спецификации

### XMLDSig
**Спецификация:** W3C XML Signature Syntax and Processing
- URI: http://www.w3.org/2000/09/xmldsig#
- Используется для структуры подписи

### Exclusive Canonicalization (ExcC14N)
**Спецификация:** W3C Canonical XML 1.0
- URI: http://www.w3.org/2001/10/xml-exc-c14n#
- Применяется к body и SignedInfo

### SMEV Transform
**Спецификация:** СМЭВ 3.5.0.27
- URI: urn://smev-gov-ru/xmldsig/transform
- 9-шаговая трансформация для госсистем

### ГОСТ стандарты
**ГОСТ Р 34.10-2012 (256 бит)**
- URI: urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102012-gostr34112012-256
- Алгоритм электронной подписи

**ГОСТ Р 34.11-2012 (256 бит)**
- URI: urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34112012-256
- Алгоритм хеширования

## Правила стилизации кода

### Python стиль

#### PEP 8
Следуем стандарту PEP 8 с модификациями:
```python
# Длина строки: 100 символов (настроено в black)
line-length = 100

# Отступы: 4 пробела
def function():
    pass

# Импорты: группировка
import standard_library
import third_party
from .local_module import Class
```

#### Type hints
Используем type hints везде где возможно:
```python
def compute_hash(self, data: bytes) -> str:
    """Вычисление хеша с аннотацией типов"""
    pass

from typing import Optional
def find_certificate(self, thumbprint: Optional[str] = None):
    pass
```

#### Docstrings
Используем Google style docstrings:
```python
def method(arg1: str, arg2: int) -> bool:
    """
    Краткое описание метода.

    Args:
        arg1: Описание первого аргумента
        arg2: Описание второго аргумента

    Returns:
        Описание возвращаемого значения

    Raises:
        ExceptionType: Когда возникает исключение
    """
    pass
```

#### Naming conventions
```python
# Классы: PascalCase
class CryptoProSigner:
    pass

# Функции и методы: snake_case
def compute_hash():
    pass

# Константы: UPPER_CASE
CAPICOM_CURRENT_USER_STORE = 2

# Приватные методы: _leading_underscore
def _internal_method():
    pass
```

### XML стиль

#### Namespace префиксы
```xml
<!-- Используем короткие осмысленные префиксы -->
<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
<ns:RequestData xmlns:ns="urn://xsd.dmdk.goznak.ru/exchange/3.0">
```

#### Атрибут id
```xml
<!-- Всегда используем маленькую букву -->
<ns:RequestData id="body">  <!-- Правильно -->
<ns:RequestData Id="body">  <!-- Неправильно -->
```

#### Самозакрывающиеся теги
```xml
<!-- Без пробела перед /> -->
<ds:CanonicalizationMethod Algorithm="..."/>  <!-- Правильно -->
<ds:CanonicalizationMethod Algorithm="..." /> <!-- Неправильно -->
```

### Git commit стиль

#### Формат сообщений
```
<тип>: <краткое описание>

<подробное описание при необходимости>
```

#### Типы коммитов
- `feat:` - новая функциональность
- `fix:` - исправление бага
- `docs:` - изменения документации
- `refactor:` - рефакторинг кода
- `test:` - добавление тестов
- `chore:` - рутинные задачи (обновление зависимостей и т.д.)

#### Примеры
```
feat: добавлена поддержка поиска сертификата по subject name

fix: исправлена проблема с DigestValue в HEX формате
Конвертируем HEX -> Base64 для соответствия XMLDSig стандарту

docs: обновлена документация по установке КриптоПро CSP
```

## Инструменты разработки

### Форматирование
```bash
# Автоформатирование с black
black giis_signer/

# С настройками из pyproject.toml
black --config pyproject.toml giis_signer/
```

### Линтинг
```bash
# Проверка с flake8
flake8 giis_signer/

# Игнорирование определенных правил
flake8 --ignore=E501,W503 giis_signer/
```

### Типизация
```bash
# Проверка типов с mypy
mypy giis_signer/

# С настройками из pyproject.toml
mypy --config-file pyproject.toml giis_signer/
```

### Тестирование
```bash
# Запуск всех тестов
pytest

# С покрытием кода
pytest --cov=giis_signer --cov-report=html

# Конкретный тест
pytest tests/test_cryptopro.py -v
```

## Конфигурация инструментов

### black (pyproject.toml)
```toml
[tool.black]
line-length = 100
target-version = ['py38']
```

### mypy (pyproject.toml)
```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
```

### pytest (pyproject.toml)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
```

## Рекомендации по разработке

### 1. Работа с виртуальным окружением
```bash
# Создание окружения
uv venv

# Активация (Windows)
.venv\Scripts\activate

# Синхронизация зависимостей
uv sync
```

### 2. Установка в режиме разработки
```bash
# С uv
uv pip install -e ".[dev]"

# С pip
pip install -e ".[dev]"
```

### 3. Порядок работы над изменениями
1. Создать ветку: `git checkout -b feature/my-feature`
2. Внести изменения в код
3. Запустить тесты: `pytest`
4. Проверить форматирование: `black giis_signer/`
5. Проверить типы: `mypy giis_signer/`
6. Обновить документацию (если необходимо)
7. Закоммитить: `git commit -m "feat: описание изменений"`
8. Создать PR

### 4. Обновление зависимостей
```bash
# Обновление lockfile
uv lock --upgrade

# Синхронизация с новыми версиями
uv sync
```

### 5. Создание релиза
```bash
# Обновить версию в pyproject.toml
# Обновить CHANGELOG.md

# Сборка дистрибутива
uv build

# Публикация на PyPI (если планируется)
uv publish
```

## Производительность

### Оптимизации
1. **Кэширование сертификатов** - сертификат загружается один раз
2. **Минимум парсинга XML** - используем текстовые замены где возможно
3. **Ленивая инициализация** - COM-объекты создаются по требованию

### Профилирование
```bash
# Профилирование с cProfile
python -m cProfile -o output.prof main.py

# Анализ результатов
python -m pstats output.prof
```

## Безопасность

### Обработка секретов
- Никогда не логировать приватные ключи
- Не выводить полное содержимое сертификатов
- Безопасное хранение отпечатков сертификатов

### Валидация входных данных
- Проверка форматов XML
- Валидация отпечатков сертификатов
- Проверка путей к файлам

### Обработка ошибок
- Не раскрывать внутренние детали в сообщениях об ошибках
- Логировать ошибки для отладки
- Предоставлять понятные сообщения пользователю

---

**Последнее обновление:** 2025-10-01
**Версия проекта:** 1.0.0
