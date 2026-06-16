QR Forge — Генератор QR-кодов на 7 языках
QR Forge — это коллекция из семи независимых реализаций генератора QR-кодов, каждая из которых работает на своём языке программирования. Проект создан для демонстрации кроссплатформенного подхода к одной задаче, а также для предоставления удобного инструмента для создания QR-кодов с расширенными возможностями.

✨ Уникальные возможности (общие для всех версий)
🎨 Кастомизация дизайна: выбор цвета фона и точек, добавление логотипа в центр

📐 Гибкие настройки: размер QR-кода, уровень коррекции ошибок (L, M, Q, H)

📁 Множество форматов вывода: PNG, SVG, EPS, PDF (в зависимости от реализации)

🖼️ Вставка логотипа (в большинстве версий)

💾 Сохранение на диск или получение в виде base64/data URL

🌐 Поддержка разных типов данных: текст, URL, контакты (vCard), Wi-Fi, email, SMS, геолокация

⚡ Массовая генерация — создание нескольких QR-кодов из списка данных

🖥️ Интерфейсы:

Командная строка (CLI) с богатыми опциями

Графический интерфейс (GUI) в Python и C#

Веб-интерфейс в JavaScript и PHP

📋 Сравнение языков и интерфейсов
Язык	Интерфейс	Библиотека	Логотип	SVG	Массовая генерация	GUI
Python	CLI + Tkinter GUI	qrcode + Pillow	✅	✅	✅	✅
JavaScript	CLI (Node.js) + Веб	qrcode (npm)	✅	✅	✅	✅ (браузер)
Go	CLI	go-qrcode	❌ (только PNG)	❌	✅	❌
Rust	CLI	qrcode (crate)	❌	❌	✅	❌
Java	CLI + Swing GUI	ZXing + java.awt	✅	❌	✅	✅
C#	CLI + WinForms	QRCoder	✅	❌	✅	✅
PHP	CLI + Веб	phpqrcode	❌	❌	✅	✅ (веб)
🚀 Быстрый старт
Общее для всех версий
Во всех реализациях используются проверенные библиотеки для генерации QR-кодов. Установка зависимостей описана ниже.

Python
bash
pip install qrcode[pil] pillow
python qr_generator.py --data "Hello, World!" --output qr.png --color "#ff0000" --bg "#ffffff" --size 300
JavaScript (Node.js)
bash
npm install qrcode
node qr_generator.js --data "Hello, World!" --output qr.png --color "#ff0000"
Для браузерной версии откройте index.html.

Go
bash
go get -u github.com/skip2/go-qrcode
go run qr_generator.go -data "Hello, World!" -output qr.png -size 256
Rust
bash
cargo add qrcode
cargo run -- --data "Hello, World!" --output qr.png --size 300
Java
bash
# Скачайте ZXing: https://github.com/zxing/zxing/releases
javac -cp ".:zxing-core-3.5.3.jar:zxing-javase-3.5.3.jar" QRGenerator.java
java -cp ".:zxing-core-3.5.3.jar:zxing-javase-3.5.3.jar" QRGenerator
C#
bash
# Установите QRCoder через NuGet: Install-Package QRCoder
csc /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:QRCoder.dll QRGenerator.cs
QRGenerator.exe
PHP
bash
# Скачайте phpqrcode: https://sourceforge.net/projects/phpqrcode/
php -S localhost:8000
# Откройте http://localhost:8000/qr_generator.php?data=Hello
🧪 Примеры использования
Сгенерировать QR-код для URL:
bash
python qr_generator.py --data "https://github.com" --output github.png --size 400
Сгенерировать QR-код с логотипом (Python):
bash
python qr_generator.py --data "https://example.com" --logo logo.png --output branded.png
Сгенерировать QR-код для Wi-Fi (Python):
bash
python qr_generator.py --wifi "MyWiFi" --password "secret" --output wifi.png
Массовая генерация (Go):
bash
go run qr_generator.go --batch data.txt --output-dir ./qrs/
🛠️ Расширение и кастомизация
В каждой версии вы можете легко изменить:

Цвета точек и фона

Размер QR-кода

Уровень коррекции ошибок

Добавить свой логотип (в поддерживаемых версиях)

Изменить формат вывода (PNG, SVG, EPS)

Подробные инструкции по расширению приведены в комментариях внутри кода.

📜 Лицензия
MIT — используйте и модифицируйте свободно.
