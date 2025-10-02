
# КриптоПро CSP COM-объекты: Полная документация

## Основные COM-объекты

### 1. CAPICOM.Store / CAdESCOM.Store
**ProgID:** "CAPICOM.Store" или "CAdESCOM.Store"

**Методы:**
- Open(StoreLocation, StoreName, OpenMode) - Открывает хранилище сертификатов
- Close() - Закрывает хранилище

**Свойства:**
- Certificates - Коллекция сертификатов в хранилище

### 2. CAPICOM.Certificates / CAdESCOM.Certificates  
**Коллекция сертификатов**

**Методы:**
- Find(FindType, Criteria, ValidOnly) - Поиск сертификатов
- Item(Index) - Получить сертификат по индексу

**Свойства:**
- Count - Количество сертификатов в коллекции

### 3. CAPICOM.Certificate / CAdESCOM.Certificate
**Объект сертификата**

**Свойства:**
- SubjectName - Имя владельца сертификата
- Thumbprint - Отпечаток сертификата (SHA1 hash)
- ValidFromDate - Дата начала действия
- ValidToDate - Дата окончания действия
- PrivateKey - Закрытый ключ (если доступен)

**Методы:**
- Export(EncodingType) - Экспорт сертификата
- Load(FileName, Password, KeyStorageFlag, KeyLocation) - Загрузка сертификата из файла

### 4. CAdESCOM.HashedData / CAPICOM.HashedData
**ProgID:** "CAdESCOM.HashedData" или "CAPICOM.HashedData"

**Свойства:**
- Algorithm - Алгоритм хэширования
- DataEncoding - Кодировка входных данных  
- Value - Значение хэша (только для чтения)

**Методы:**
- Hash(Data) - Вычисление хэша от данных
- SetHashValue(HashValue) - Установка готового значения хэша

### 5. CAdESCOM.RawSignature
**ProgID:** "CAdESCOM.RawSignature"

**Методы:**
- SignHash(HashedData, Certificate) - Подписание хэша
  - Параметры:
    - HashedData: объект CAdESCOM.HashedData с вычисленным хэшем
    - Certificate: сертификат для подписания
  - Возвращает: подпись в шестнадцатеричном формате

### 6. CAdESCOM.CPSigner / CAPICOM.Signer
**ProgID:** "CAdESCOM.CPSigner" или "CAPICOM.Signer"

**Свойства:**
- Certificate - Сертификат для подписания
- Options - Параметры подписи
- TSAAddress - Адрес службы меток времени
- AuthenticatedAttributes2 - Коллекция аутентифицированных атрибутов


## Константы и перечисления

### 1. CAPICOM_STORE_LOCATION
Местоположение хранилища сертификатов:

```
CAPICOM_MEMORY_STORE = 0                    // Хранилище в памяти
CAPICOM_LOCAL_MACHINE_STORE = 1             // Локальное хранилище компьютера  
CAPICOM_CURRENT_USER_STORE = 2              // Хранилище текущего пользователя
CAPICOM_ACTIVE_DIRECTORY_USER_STORE = 3     // Хранилище Active Directory
CAPICOM_SMART_CARD_USER_STORE = 4           // Хранилище смарт-карты
```

### 2. CAPICOM_STORE_OPEN_MODE  
Режимы открытия хранилища:

```
CAPICOM_STORE_OPEN_READ_ONLY = 0           // Только для чтения
CAPICOM_STORE_OPEN_READ_WRITE = 1          // Чтение и запись
CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED = 2     // Максимальные разрешения
CAPICOM_STORE_OPEN_EXISTING_ONLY = 128     // Только существующие хранилища
CAPICOM_STORE_OPEN_INCLUDE_ARCHIVED = 256  // Включить архивные сертификаты
```

### 3. CAPICOM_CERTIFICATE_FIND_TYPE
Типы поиска сертификатов:

```
CAPICOM_CERTIFICATE_FIND_SHA1_HASH = 0         // По SHA1 отпечатку
CAPICOM_CERTIFICATE_FIND_SUBJECT_NAME = 1      // По имени владельца
CAPICOM_CERTIFICATE_FIND_ISSUER_NAME = 2       // По имени издателя
CAPICOM_CERTIFICATE_FIND_ROOT_NAME = 3         // По корневому имени
CAPICOM_CERTIFICATE_FIND_TEMPLATE_NAME = 4     // По имени шаблона
CAPICOM_CERTIFICATE_FIND_EXTENSION = 5         // По расширению
CAPICOM_CERTIFICATE_FIND_EXTENDED_PROPERTY = 6 // По расширенному свойству
CAPICOM_CERTIFICATE_FIND_APPLICATION_POLICY = 7// По политике приложения
CAPICOM_CERTIFICATE_FIND_CERTIFICATE_POLICY = 8// По политике сертификата
CAPICOM_CERTIFICATE_FIND_TIME_VALID = 9        // Действительные по времени
CAPICOM_CERTIFICATE_FIND_TIME_NOT_YET_VALID = 10// Еще не действительные
CAPICOM_CERTIFICATE_FIND_TIME_EXPIRED = 11     // Истекшие
CAPICOM_CERTIFICATE_FIND_KEY_USAGE = 12        // По использованию ключа
```

### 4. CADESCOM_HASH_ALGORITHM
Алгоритмы хэширования:

```
CADESCOM_HASH_ALGORITHM_SHA1 = 0                         // SHA1
CADESCOM_HASH_ALGORITHM_MD2 = 1                          // MD2
CADESCOM_HASH_ALGORITHM_MD4 = 2                          // MD4
CADESCOM_HASH_ALGORITHM_MD5 = 3                          // MD5
CADESCOM_HASH_ALGORITHM_SHA_256 = 4                      // SHA-256
CADESCOM_HASH_ALGORITHM_SHA_384 = 5                      // SHA-384
CADESCOM_HASH_ALGORITHM_SHA_512 = 6                      // SHA-512

// ГОСТ алгоритмы (КриптоПро):
CADESCOM_HASH_ALGORITHM_CP_GOST_3411 = 100               // ГОСТ Р 34.11-94
CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256 = 101      // ГОСТ Р 34.11-2012 (256 бит)
CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_512 = 102      // ГОСТ Р 34.11-2012 (512 бит)
CADESCOM_HASH_ALGORITHM_CP_GOST_3411_HMAC = 110          // ГОСТ Р 34.11-94 HMAC
CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256_HMAC = 111 // ГОСТ Р 34.11-2012 (256) HMAC
CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_512_HMAC = 112 // ГОСТ Р 34.11-2012 (512) HMAC
```

### 5. CAPICOM_ENCODING_TYPE
Типы кодирования:

```
CAPICOM_ENCODE_ANY = -1        // Автоматическое определение (0xFFFFFFFF)
CAPICOM_ENCODE_BASE64 = 0      // Base64 кодирование
CAPICOM_ENCODE_BINARY = 1      // Двоичное представление
```

### 6. CADESCOM_CONTENT_ENCODING_TYPE
Кодирование содержимого для хэширования:

```
CADESCOM_BASE64_TO_BINARY = 1  // Преобразование Base64 в бинарные данные
CADESCOM_STRING_TO_UCS2LE = 0  // Строка в UCS2 Little Endian
```

### 7. Имена хранилищ сертификатов
Стандартные имена хранилищ:

```
"My" или "MY"         // Личные сертификаты
"Root"                // Доверенные корневые центры сертификации
"CA"                  // Промежуточные центры сертификации
"Trust"               // Доверенные издатели
"Disallowed"          // Недоверенные сертификаты
"TrustedPeople"       // Доверенные лица
"AddressBook"         // Адресная книга
```


## Примеры кода

### 1. Открытие хранилища и поиск сертификата (JavaScript/VBScript)

```javascript
// Константы
var CAPICOM_CURRENT_USER_STORE = 2;
var CAPICOM_MY_STORE = "My";
var CAPICOM_STORE_OPEN_READ_ONLY = 0;
var CAPICOM_CERTIFICATE_FIND_SHA1_HASH = 0;

// Открытие хранилища сертификатов
var oStore = new ActiveXObject("CAdESCOM.Store");
oStore.Open(CAPICOM_CURRENT_USER_STORE, CAPICOM_MY_STORE, CAPICOM_STORE_OPEN_READ_ONLY);

// Поиск сертификата по отпечатку
var thumbprint = "1234567890ABCDEF1234567890ABCDEF12345678"; // SHA1 отпечаток (40 символов)
var oCerts = oStore.Certificates.Find(CAPICOM_CERTIFICATE_FIND_SHA1_HASH, thumbprint, false);

if (oCerts.Count > 0) {
    var oCert = oCerts.Item(1); // Индексация начинается с 1
    console.log("Владелец: " + oCert.SubjectName);
    console.log("Действителен с: " + oCert.ValidFromDate);
    console.log("Действителен до: " + oCert.ValidToDate);
}

// Закрытие хранилища
oStore.Close();
```

### 2. Перебор всех сертификатов в хранилище

```javascript
var CAPICOM_CURRENT_USER_STORE = 2;
var CAPICOM_MY_STORE = "My";
var CAPICOM_STORE_OPEN_READ_ONLY = 0;

var oStore = new ActiveXObject("CAdESCOM.Store");
oStore.Open(CAPICOM_CURRENT_USER_STORE, CAPICOM_MY_STORE, CAPICOM_STORE_OPEN_READ_ONLY);

// Перебор всех сертификатов
for (var i = 1; i <= oStore.Certificates.Count; i++) {
    var cert = oStore.Certificates.Item(i);
    console.log("Сертификат " + i + ":");
    console.log("  Владелец: " + cert.SubjectName);
    console.log("  Отпечаток: " + cert.Thumbprint);
    console.log("  Период действия: " + cert.ValidFromDate + " - " + cert.ValidToDate);
}

oStore.Close();
```

### 3. Вычисление хэша данных

```javascript
// Константы
var CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256 = 101;
var CADESCOM_BASE64_TO_BINARY = 1;

// Создание объекта для хэширования
var oHashedData = new ActiveXObject("CAdESCOM.HashedData");

// Установка алгоритма хэширования
oHashedData.Algorithm = CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256;

// Установка кодировки входных данных
oHashedData.DataEncoding = CADESCOM_BASE64_TO_BINARY;

// Данные для хэширования (в Base64)
var dataToHash = btoa("Текст для хэширования"); // btoa() кодирует в Base64

// Вычисление хэша
oHashedData.Hash(dataToHash);

// Получение значения хэша
var hashValue = oHashedData.Value;
console.log("Хэш: " + hashValue);
```

### 4. Подписание хэша с помощью RawSignature

```javascript
// Предполагаем, что у нас уже есть:
// - oHashedData (объект с вычисленным хэшем)
// - oCert (сертификат для подписания)

// Создание объекта для подписания хэша
var oRawSignature = new ActiveXObject("CAdESCOM.RawSignature");

// Подписание хэша
var signatureHex = oRawSignature.SignHash(oHashedData, oCert);

console.log("Подпись (HEX): " + signatureHex);

// Преобразование в Base64 (при необходимости)
function hexToBase64(hexString) {
    var bytes = [];
    for (var i = 0; i < hexString.length; i += 2) {
        bytes.push(parseInt(hexString.substr(i, 2), 16));
    }
    return btoa(String.fromCharCode.apply(null, bytes));
}

var signatureBase64 = hexToBase64(signatureHex);
console.log("Подпись (Base64): " + signatureBase64);
```

### 5. Создание усовершенствованной подписи CAdES

```javascript
// Константы
var CAPICOM_CERTIFICATE_INCLUDE_WHOLE_CHAIN = 1;
var CADESCOM_CADES_BES = 1;
var CADESCOM_BASE64_TO_BINARY = 1;

// Данные для подписания
var contentToSign = "Документ для подписания";
var contentBase64 = btoa(contentToSign);

// Создание объекта для подписания
var oSigner = new ActiveXObject("CAdESCOM.CPSigner");
oSigner.Certificate = oCert; // Предполагаем, что сертификат уже выбран
oSigner.Options = CAPICOM_CERTIFICATE_INCLUDE_WHOLE_CHAIN;

// Добавление атрибута времени подписи
var oSigningTimeAttr = new ActiveXObject("CAdESCOM.CPAttribute");
oSigningTimeAttr.Name = 1; // CAPICOM_AUTHENTICATED_ATTRIBUTE_SIGNING_TIME
oSigningTimeAttr.Value = new Date();
oSigner.AuthenticatedAttributes2.Add(oSigningTimeAttr);

// Создание подписанных данных
var oSignedData = new ActiveXObject("CAdESCOM.CadesSignedData");
oSignedData.ContentEncoding = CADESCOM_BASE64_TO_BINARY;
oSignedData.Content = contentBase64;

// Создание подписи
var signature = oSignedData.SignCades(oSigner, CADESCOM_CADES_BES, false, 0);

console.log("CAdES подпись создана:");
console.log(signature);
```

### 6. Пример на C# с использованием Interop

```csharp
using CAdESCOM;
using CAPICOM;

// Константы
const int CAPICOM_CURRENT_USER_STORE = 2;
const int CAPICOM_STORE_OPEN_READ_ONLY = 0;
const int CAPICOM_CERTIFICATE_FIND_SHA1_HASH = 0;
const int CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256 = 101;

public void SignDocument(string documentText, string certificateThumbprint)
{
    try
    {
        // Открытие хранилища сертификатов
        var store = new StoreClass();
        store.Open(CAPICOM_STORE_LOCATION.CAPICOM_CURRENT_USER_STORE, 
                  "My", 
                  CAPICOM_STORE_OPEN_MODE.CAPICOM_STORE_OPEN_READ_ONLY);

        // Поиск сертификата
        var certificates = store.Certificates.Find(
            CAPICOM_CERTIFICATE_FIND_TYPE.CAPICOM_CERTIFICATE_FIND_SHA1_HASH,
            certificateThumbprint,
            false);

        if (certificates.Count == 0)
        {
            throw new Exception("Сертификат не найден");
        }

        var certificate = certificates.Item(1);

        // Создание хэша
        var hashedData = new HashedDataClass();
        hashedData.Algorithm = CADESCOM_HASH_ALGORITHM.CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256;
        hashedData.Hash(documentText);

        // Подписание хэша
        var rawSignature = new RawSignatureClass();
        var signature = rawSignature.SignHash(hashedData, certificate);

        Console.WriteLine($"Подпись: {signature}");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Ошибка: {ex.Message}");
    }
}
```

### 7. Пример на Python с использованием win32com

```python
import win32com.client

# Константы
CAPICOM_CURRENT_USER_STORE = 2
CAPICOM_MY_STORE = "My"
CAPICOM_STORE_OPEN_READ_ONLY = 0
CAPICOM_CERTIFICATE_FIND_SHA1_HASH = 0
CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256 = 101

def find_certificate_by_thumbprint(thumbprint):
    # Создание объекта хранилища
    store = win32com.client.Dispatch("CAdESCOM.Store")

    try:
        # Открытие хранилища
        store.Open(CAPICOM_CURRENT_USER_STORE, CAPICOM_MY_STORE, CAPICOM_STORE_OPEN_READ_ONLY)

        # Поиск сертификата
        certificates = store.Certificates.Find(CAPICOM_CERTIFICATE_FIND_SHA1_HASH, thumbprint, False)

        if certificates.Count > 0:
            cert = certificates.Item(1)
            print(f"Найден сертификат: {cert.SubjectName}")
            print(f"Отпечаток: {cert.Thumbprint}")
            return cert
        else:
            print("Сертификат не найден")
            return None

    finally:
        store.Close()

def sign_hash(data_to_hash, certificate):
    # Создание объекта для хэширования
    hashed_data = win32com.client.Dispatch("CAdESCOM.HashedData")
    hashed_data.Algorithm = CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256
    hashed_data.Hash(data_to_hash)

    # Подписание хэша
    raw_signature = win32com.client.Dispatch("CAdESCOM.RawSignature")
    signature = raw_signature.SignHash(hashed_data, certificate)

    return signature

# Пример использования
if __name__ == "__main__":
    thumbprint = "1234567890ABCDEF1234567890ABCDEF12345678"
    cert = find_certificate_by_thumbprint(thumbprint)

    if cert:
        data = "Данные для подписания"
        signature = sign_hash(data, cert)
        print(f"Подпись: {signature}")
```

### 8. Пример обработки ошибок

```javascript
function safeSignOperation(documentText, thumbprint) {
    var oStore = null;

    try {
        // Инициализация
        oStore = new ActiveXObject("CAdESCOM.Store");
        oStore.Open(2, "My", 0);  // CURRENT_USER, My store, READ_ONLY

        // Поиск сертификата
        var certs = oStore.Certificates.Find(0, thumbprint, false); // SHA1_HASH find

        if (certs.Count === 0) {
            throw new Error("Сертификат с отпечатком " + thumbprint + " не найден");
        }

        var cert = certs.Item(1);

        // Проверка срока действия
        var now = new Date();
        var validFrom = new Date(cert.ValidFromDate);
        var validTo = new Date(cert.ValidToDate);

        if (now < validFrom || now > validTo) {
            throw new Error("Сертификат недействителен: срок действия истек или еще не наступил");
        }

        // Проверка наличия закрытого ключа
        if (!cert.PrivateKey) {
            throw new Error("У сертификата отсутствует закрытый ключ");
        }

        // Подписание документа
        var hashedData = new ActiveXObject("CAdESCOM.HashedData");
        hashedData.Algorithm = 101; // GOST 3411-2012 256
        hashedData.Hash(documentText);

        var rawSig = new ActiveXObject("CAdESCOM.RawSignature");
        var signature = rawSig.SignHash(hashedData, cert);

        return {
            success: true,
            signature: signature,
            certificate: {
                subject: cert.SubjectName,
                thumbprint: cert.Thumbprint,
                validFrom: cert.ValidFromDate,
                validTo: cert.ValidToDate
            }
        };

    } catch (error) {
        return {
            success: false,
            error: error.message,
            code: error.number
        };
    } finally {
        // Освобождение ресурсов
        if (oStore) {
            try {
                oStore.Close();
            } catch (e) {
                // Игнорируем ошибки при закрытии
            }
        }
    }
}

// Использование
var result = safeSignOperation("Документ для подписи", "A1B2C3D4E5F6...");
if (result.success) {
    console.log("Подпись успешно создана: " + result.signature);
} else {
    console.log("Ошибка: " + result.error);
}
```


# КриптоПро CSP COM-объекты: Расширенная документация

## Дополнительные константы

### CAPICOM_CERTIFICATE_INCLUDE_OPTION
Опции включения сертификатов в подпись:

```
CAPICOM_CERTIFICATE_INCLUDE_CHAIN_EXCEPT_ROOT = 0  // Цепочка без корневого сертификата
CAPICOM_CERTIFICATE_INCLUDE_WHOLE_CHAIN = 1        // Полная цепочка сертификатов  
CAPICOM_CERTIFICATE_INCLUDE_END_ENTITY_ONLY = 2    // Только конечный сертификат
```

### CADESCOM_CADES_TYPE
Типы усовершенствованной подписи CAdES:

```
CADESCOM_CADES_DEFAULT = 0         // По умолчанию
CADESCOM_CADES_BES = 1             // CAdES-BES (Basic Electronic Signature)
CADESCOM_CADES_T = 0x5             // CAdES-T (с отметкой времени)
CADESCOM_CADES_X_LONG_TYPE_1 = 0x5D // CAdES-X Long Type 1
```

### CAPICOM_AUTHENTICATED_ATTRIBUTE
Аутентифицированные атрибуты:

```
CAPICOM_AUTHENTICATED_ATTRIBUTE_SIGNING_TIME = 0      // Время подписи
CAPICOM_AUTHENTICATED_ATTRIBUTE_DOCUMENT_NAME = 1     // Имя документа
CAPICOM_AUTHENTICATED_ATTRIBUTE_DOCUMENT_DESCRIPTION = 2 // Описание документа
```

### CADESCOM_CONTENT_ENCODING_TYPE
Дополнительные типы кодирования содержимого:

```
CADESCOM_STRING_TO_UCS2LE = 0     // Строка в UCS2 Little Endian
CADESCOM_BASE64_TO_BINARY = 1     // Base64 в бинарные данные
```

## Расширенные примеры кода

### 1. Полный пример создания усовершенствованной подписи с атрибутами

```javascript
function createAdvancedSignature(documentText, certificateThumbprint) {
    try {
        // Константы
        var CAPICOM_CURRENT_USER_STORE = 2;
        var CAPICOM_MY_STORE = "My";
        var CAPICOM_STORE_OPEN_READ_ONLY = 0;
        var CAPICOM_CERTIFICATE_FIND_SHA1_HASH = 0;
        var CAPICOM_CERTIFICATE_INCLUDE_WHOLE_CHAIN = 1;
        var CADESCOM_CADES_BES = 1;
        var CADESCOM_BASE64_TO_BINARY = 1;
        var CAPICOM_AUTHENTICATED_ATTRIBUTE_SIGNING_TIME = 0;
        var CAPICOM_AUTHENTICATED_ATTRIBUTE_DOCUMENT_NAME = 1;

        // Открытие хранилища сертификатов
        var oStore = new ActiveXObject("CAdESCOM.Store");
        oStore.Open(CAPICOM_CURRENT_USER_STORE, CAPICOM_MY_STORE, CAPICOM_STORE_OPEN_READ_ONLY);

        // Поиск сертификата по отпечатку
        var oCerts = oStore.Certificates.Find(
            CAPICOM_CERTIFICATE_FIND_SHA1_HASH, 
            certificateThumbprint, 
            false
        );

        if (oCerts.Count === 0) {
            throw new Error("Сертификат не найден");
        }

        var oCert = oCerts.Item(1);

        // Создание объекта для подписания
        var oSigner = new ActiveXObject("CAdESCOM.CPSigner");
        oSigner.Certificate = oCert;
        oSigner.Options = CAPICOM_CERTIFICATE_INCLUDE_WHOLE_CHAIN;

        // Установка адреса службы меток времени (опционально)
        // oSigner.TSAAddress = "http://cryptopro.ru/tsp/";

        // Добавление атрибута времени подписи
        var oSigningTimeAttr = new ActiveXObject("CAdESCOM.CPAttribute");
        oSigningTimeAttr.Name = CAPICOM_AUTHENTICATED_ATTRIBUTE_SIGNING_TIME;
        oSigningTimeAttr.Value = new Date();
        oSigner.AuthenticatedAttributes2.Add(oSigningTimeAttr);

        // Добавление атрибута имени документа
        var oDocumentNameAttr = new ActiveXObject("CAdESCOM.CPAttribute");
        oDocumentNameAttr.Name = CAPICOM_AUTHENTICATED_ATTRIBUTE_DOCUMENT_NAME;
        oDocumentNameAttr.Value = "Важный документ";
        oSigner.AuthenticatedAttributes2.Add(oDocumentNameAttr);

        // Подготовка данных для подписи
        var contentBase64 = btoa(unescape(encodeURIComponent(documentText)));

        // Создание подписанных данных
        var oSignedData = new ActiveXObject("CAdESCOM.CadesSignedData");
        oSignedData.ContentEncoding = CADESCOM_BASE64_TO_BINARY;
        oSignedData.Content = contentBase64;

        // Создание подписи
        var sSignedMessage = oSignedData.SignCades(
            oSigner,
            CADESCOM_CADES_BES,    // Тип подписи
            false,                  // Не отсоединенная подпись
            0                      // Кодирование по умолчанию
        );

        // Закрытие хранилища
        oStore.Close();

        return {
            success: true,
            signature: sSignedMessage,
            certificateInfo: {
                subject: oCert.SubjectName,
                issuer: oCert.IssuerName,
                thumbprint: oCert.Thumbprint,
                validFrom: oCert.ValidFromDate,
                validTo: oCert.ValidToDate
            }
        };

    } catch (error) {
        return {
            success: false,
            error: error.message,
            errorCode: error.number
        };
    }
}

// Использование
var result = createAdvancedSignature(
    "Текст документа для подписания",
    "A1B2C3D4E5F6789012345678901234567890ABCD" // SHA1 отпечаток
);

if (result.success) {
    console.log("Подпись создана успешно");
    console.log("Подписано сертификатом:", result.certificateInfo.subject);
    // Можно сохранить result.signature
} else {
    console.log("Ошибка:", result.error);
}
```

### 2. Создание отсоединенной подписи для API

```javascript
function createDetachedSignature(data, certificateThumbprint) {
    try {
        var CAPICOM_CURRENT_USER_STORE = 2;
        var CAPICOM_MY_STORE = "My";
        var CAPICOM_STORE_OPEN_READ_ONLY = 0;
        var CAPICOM_CERTIFICATE_FIND_SHA1_HASH = 0;
        var CAPICOM_CERTIFICATE_INCLUDE_WHOLE_CHAIN = 1;
        var CADESCOM_CADES_BES = 1;
        var CADESCOM_BASE64_TO_BINARY = 1;

        // Поиск сертификата
        var oStore = new ActiveXObject("CAdESCOM.Store");
        oStore.Open(CAPICOM_CURRENT_USER_STORE, CAPICOM_MY_STORE, CAPICOM_STORE_OPEN_READ_ONLY);

        var oCerts = oStore.Certificates.Find(CAPICOM_CERTIFICATE_FIND_SHA1_HASH, certificateThumbprint, false);
        if (oCerts.Count === 0) {
            throw new Error("Сертификат не найден");
        }
        var oCert = oCerts.Item(1);

        // Настройка подписанта
        var oSigner = new ActiveXObject("CAdESCOM.CPSigner");
        oSigner.Certificate = oCert;
        oSigner.Options = CAPICOM_CERTIFICATE_INCLUDE_WHOLE_CHAIN;

        // Добавление атрибута времени подписи
        var oSigningTimeAttr = new ActiveXObject("CAdESCOM.CPAttribute");
        oSigningTimeAttr.Name = 0; // CAPICOM_AUTHENTICATED_ATTRIBUTE_SIGNING_TIME
        oSigningTimeAttr.Value = new Date();
        oSigner.AuthenticatedAttributes2.Add(oSigningTimeAttr);

        // Подготовка данных (JSON без пробелов для API)
        var jsonData = JSON.stringify(data, null, 0); // Без форматирования
        var contentBase64 = btoa(unescape(encodeURIComponent(jsonData)));

        // Создание подписанных данных
        var oSignedData = new ActiveXObject("CAdESCOM.CadesSignedData");
        oSignedData.ContentEncoding = CADESCOM_BASE64_TO_BINARY;
        oSignedData.Content = contentBase64;

        // Создание отсоединенной подписи
        var detachedSignature = oSignedData.SignCades(
            oSigner,
            CADESCOM_CADES_BES,    // Тип подписи
            true,                   // Отсоединенная подпись
            0                      // Кодирование Base64
        );

        // Очистка переносов строк для HTTP заголовков
        detachedSignature = detachedSignature.replace(/
?
|
/g, '');

        oStore.Close();

        return {
            data: jsonData,          // Оригинальные данные
            signature: detachedSignature,  // Отсоединенная подпись
            certificate: oCert.Export(0)   // Сертификат в Base64
        };

    } catch (error) {
        throw new Error("Ошибка создания подписи: " + error.message);
    }
}

// Пример для API Честный знак
var apiData = {
    "productGroup": "lp",
    "attributes": {
        "releaseMethodType": "PRODUCTION",
        "createMethodType": "SELF_MADE"
    },
    "products": [
        // массив продуктов
    ]
};

try {
    var signResult = createDetachedSignature(apiData, "YOUR_CERT_THUMBPRINT");

    // Отправка запроса с подписью
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "https://api.example.com/endpoint");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("X-Signature", signResult.signature); // Отсоединенная подпись в заголовке
    xhr.send(signResult.data); // Оригинальные данные в теле запроса

} catch (error) {
    console.error("Ошибка:", error.message);
}
```

### 3. Проверка подписи

```javascript
function verifySignature(signedData, isDetached, originalData) {
    try {
        var CADESCOM_CADES_BES = 1;

        var oSignedData = new ActiveXObject("CAdESCOM.CadesSignedData");

        if (isDetached && originalData) {
            // Для отсоединенной подписи нужно установить оригинальные данные
            var contentBase64 = btoa(unescape(encodeURIComponent(originalData)));
            oSignedData.ContentEncoding = 1; // CADESCOM_BASE64_TO_BINARY
            oSignedData.Content = contentBase64;
        }

        // Проверка подписи
        oSignedData.VerifyCades(signedData, CADESCOM_CADES_BES, isDetached);

        // Получение информации о подписантах
        var signers = [];
        for (var i = 1; i <= oSignedData.Signers.Count; i++) {
            var signer = oSignedData.Signers.Item(i);
            var cert = signer.Certificate;

            signers.push({
                subjectName: cert.SubjectName,
                issuerName: cert.IssuerName,
                thumbprint: cert.Thumbprint,
                validFrom: cert.ValidFromDate,
                validTo: cert.ValidToDate,
                signingTime: signer.SigningTime || null
            });
        }

        return {
            valid: true,
            signers: signers,
            content: isDetached ? originalData : oSignedData.Content
        };

    } catch (error) {
        return {
            valid: false,
            error: error.message,
            errorCode: error.number
        };
    }
}

// Пример использования
var verifyResult = verifySignature(
    signatureData,    // Base64 подпись
    true,            // Отсоединенная подпись
    originalData     // Оригинальные данные
);

if (verifyResult.valid) {
    console.log("Подпись действительна");
    verifyResult.signers.forEach(function(signer, index) {
        console.log("Подписант " + (index + 1) + ":", signer.subjectName);
    });
} else {
    console.log("Подпись недействительна:", verifyResult.error);
}
```

### 4. Работа с хэшированием и низкоуровневой подписью

```javascript
function signHashDirectly(dataToHash, certificateThumbprint, hashAlgorithm) {
    try {
        // Константы
        var CAPICOM_CURRENT_USER_STORE = 2;
        var CAPICOM_MY_STORE = "My";
        var CAPICOM_STORE_OPEN_READ_ONLY = 0;
        var CAPICOM_CERTIFICATE_FIND_SHA1_HASH = 0;
        var CADESCOM_BASE64_TO_BINARY = 1;

        // Алгоритм хэширования (по умолчанию ГОСТ Р 34.11-2012 256)
        hashAlgorithm = hashAlgorithm || 101; // CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256

        // Поиск сертификата
        var oStore = new ActiveXObject("CAdESCOM.Store");
        oStore.Open(CAPICOM_CURRENT_USER_STORE, CAPICOM_MY_STORE, CAPICOM_STORE_OPEN_READ_ONLY);

        var oCerts = oStore.Certificates.Find(CAPICOM_CERTIFICATE_FIND_SHA1_HASH, certificateThumbprint, false);
        if (oCerts.Count === 0) {
            throw new Error("Сертификат не найден");
        }
        var oCert = oCerts.Item(1);

        // Создание хэша
        var oHashedData = new ActiveXObject("CAdESCOM.HashedData");
        oHashedData.Algorithm = hashAlgorithm;
        oHashedData.DataEncoding = CADESCOM_BASE64_TO_BINARY;

        // Если данные уже в Base64, используем их напрямую
        // Иначе кодируем
        var dataBase64;
        if (typeof dataToHash === 'string' && isBase64(dataToHash)) {
            dataBase64 = dataToHash;
        } else {
            dataBase64 = btoa(unescape(encodeURIComponent(dataToHash)));
        }

        oHashedData.Hash(dataBase64);

        // Получение значения хэша
        var hashValue = oHashedData.Value;
        console.log("Хэш:", hashValue);

        // Подписание хэша
        var oRawSignature = new ActiveXObject("CAdESCOM.RawSignature");
        var signatureHex = oRawSignature.SignHash(oHashedData, oCert);

        oStore.Close();

        return {
            hash: hashValue,
            signature: signatureHex,
            signatureBase64: hexToBase64(signatureHex)
        };

    } catch (error) {
        throw new Error("Ошибка подписания хэша: " + error.message);
    }
}

// Вспомогательные функции
function isBase64(str) {
    try {
        return btoa(atob(str)) === str;
    } catch (err) {
        return false;
    }
}

function hexToBase64(hexString) {
    var bytes = [];
    for (var i = 0; i < hexString.length; i += 2) {
        bytes.push(parseInt(hexString.substr(i, 2), 16));
    }
    var binary = String.fromCharCode.apply(null, bytes);
    return btoa(binary);
}

// Пример использования
try {
    var hashSignResult = signHashDirectly(
        "Данные для хэширования и подписания",
        "YOUR_CERT_THUMBPRINT",
        101 // ГОСТ Р 34.11-2012 256
    );

    console.log("Хэш:", hashSignResult.hash);
    console.log("Подпись (HEX):", hashSignResult.signature);
    console.log("Подпись (Base64):", hashSignResult.signatureBase64);

} catch (error) {
    console.error("Ошибка:", error.message);
}
```

### 5. Универсальная функция выбора сертификата

```javascript
function selectCertificate(filterOptions) {
    try {
        var CAPICOM_CURRENT_USER_STORE = 2;
        var CAPICOM_MY_STORE = "My";
        var CAPICOM_STORE_OPEN_READ_ONLY = 0;

        var oStore = new ActiveXObject("CAdESCOM.Store");
        oStore.Open(CAPICOM_CURRENT_USER_STORE, CAPICOM_MY_STORE, CAPICOM_STORE_OPEN_READ_ONLY);

        var certificates = [];
        var now = new Date();

        // Перебор всех сертификатов
        for (var i = 1; i <= oStore.Certificates.Count; i++) {
            var cert = oStore.Certificates.Item(i);

            // Проверка срока действия
            var validFrom = new Date(cert.ValidFromDate);
            var validTo = new Date(cert.ValidToDate);
            var isValid = (now >= validFrom && now <= validTo);

            // Проверка наличия закрытого ключа
            var hasPrivateKey = false;
            try {
                hasPrivateKey = !!cert.PrivateKey;
            } catch (e) {
                // Если ошибка доступа к PrivateKey, считаем что ключа нет
            }

            var certInfo = {
                index: i,
                certificate: cert,
                subjectName: cert.SubjectName,
                issuerName: cert.IssuerName,
                thumbprint: cert.Thumbprint,
                serialNumber: cert.SerialNumber,
                validFrom: cert.ValidFromDate,
                validTo: cert.ValidToDate,
                isValid: isValid,
                hasPrivateKey: hasPrivateKey,
                isExpired: now > validTo,
                isNotYetValid: now < validFrom
            };

            // Применение фильтров
            var passesFilter = true;

            if (filterOptions) {
                if (filterOptions.validOnly && !isValid) passesFilter = false;
                if (filterOptions.withPrivateKeyOnly && !hasPrivateKey) passesFilter = false;
                if (filterOptions.subjectContains && 
                    cert.SubjectName.toLowerCase().indexOf(filterOptions.subjectContains.toLowerCase()) === -1) {
                    passesFilter = false;
                }
                if (filterOptions.issuerContains && 
                    cert.IssuerName.toLowerCase().indexOf(filterOptions.issuerContains.toLowerCase()) === -1) {
                    passesFilter = false;
                }
            }

            if (passesFilter) {
                certificates.push(certInfo);
            }
        }

        oStore.Close();

        // Сортировка: сначала действительные, потом по дате окончания
        certificates.sort(function(a, b) {
            if (a.isValid && !b.isValid) return -1;
            if (!a.isValid && b.isValid) return 1;

            var dateA = new Date(a.validTo);
            var dateB = new Date(b.validTo);
            return dateB - dateA; // Сначала с более поздней датой окончания
        });

        return certificates;

    } catch (error) {
        throw new Error("Ошибка получения списка сертификатов: " + error.message);
    }
}

// Пример использования
try {
    var certs = selectCertificate({
        validOnly: true,              // Только действительные
        withPrivateKeyOnly: true,     // Только с закрытым ключом
        subjectContains: "ООО",       // В субъекте содержится "ООО"
        // issuerContains: "Тест"     // В издателе содержится "Тест"
    });

    if (certs.length === 0) {
        console.log("Подходящие сертификаты не найдены");
    } else {
        console.log("Найдено сертификатов:", certs.length);

        certs.forEach(function(cert, index) {
            console.log((index + 1) + ". " + cert.subjectName);
            console.log("   Отпечаток: " + cert.thumbprint);
            console.log("   Действителен: " + cert.validFrom + " - " + cert.validTo);
            console.log("   Статус: " + (cert.isValid ? "Действительный" : "Недействительный"));
            console.log("   Закрытый ключ: " + (cert.hasPrivateKey ? "Есть" : "Отсутствует"));
            console.log("");
        });

        // Автоматический выбор первого подходящего сертификата
        var selectedCert = certs[0].certificate;
        console.log("Выбран сертификат:", selectedCert.SubjectName);
    }

} catch (error) {
    console.error("Ошибка:", error.message);
}
```

## Коды ошибок и их обработка

### Часто встречающиеся ошибки:

```
0x80880251 - CAPICOM_E_SIGNER_NOT_FOUND - Подписант не найден в подписанном сообщении
0x80880250 - CAPICOM_E_SIGNER_NOT_INITIALIZED - Подписант не инициализирован
0x80880230 - CAPICOM_E_STORE_NOT_OPENED - Хранилище не открыто
0x80880210 - CAPICOM_E_CERTIFICATE_NOT_INITIALIZED - Сертификат не инициализирован
0x80880211 - CAPICOM_E_CERTIFICATE_NO_PRIVATE_KEY - У сертификата нет закрытого ключа
```

### Функция обработки ошибок:

```javascript
function handleCryptoError(error) {
    var errorCode = error.number || error.code;
    var errorMessages = {
        0x80880251: "Подписант не найден в подписанном сообщении",
        0x80880250: "Подписант не инициализирован", 
        0x80880230: "Хранилище сертификатов не открыто",
        0x80880210: "Сертификат не инициализирован",
        0x80880211: "У сертификата отсутствует закрытый ключ",
        0x80880220: "Цепочка сертификатов не построена",
        0x80880231: "Хранилище сертификатов пустое",
        0x80880270: "Недопустимый алгоритм",
        0x80880280: "Объект EnvelopedData не инициализирован"
    };

    var message = errorMessages[errorCode] || error.message || "Неизвестная ошибка";

    return {
        code: errorCode,
        message: message,
        originalError: error
    };
}
```