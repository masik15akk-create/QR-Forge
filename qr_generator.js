// qr_generator.js - Генератор QR-кодов на JavaScript (Node.js CLI + браузер)
// Для Node.js: npm install qrcode commander
// Для браузера: используйте библиотеку qrcodejs или встроенный код.

// ========== CLI (Node.js) ==========
if (typeof require !== 'undefined' && require.main === module) {
    const QRCode = require('qrcode');
    const fs = require('fs');
    const path = require('path');
    const { program } = require('commander');

    program
        .option('-d, --data <text>', 'Данные для кодирования')
        .option('-o, --output <path>', 'Путь для сохранения (PNG)')
        .option('-s, --size <number>', 'Размер в пикселях', parseInt, 300)
        .option('-c, --color <color>', 'Цвет точек', '#000000')
        .option('-b, --bg <color>', 'Цвет фона', '#ffffff')
        .option('-e, --error <level>', 'Уровень коррекции (L,M,Q,H)', 'M')
        .option('--logo <path>', 'Путь к логотипу (PNG)')
        .option('--batch <path>', 'JSON-файл со списком данных для массовой генерации')
        .option('--output-dir <path>', 'Папка для массовой генерации', 'qrs')
        .parse(process.argv);

    const opts = program.opts();

    if (opts.batch) {
        // Массовая генерация
        const dataList = JSON.parse(fs.readFileSync(opts.batch, 'utf8'));
        if (!fs.existsSync(opts.outputDir)) fs.mkdirSync(opts.outputDir, { recursive: true });
        dataList.forEach((data, i) => {
            const output = path.join(opts.outputDir, `qr_${i+1}.png`);
            QRCode.toFile(output, data, {
                width: opts.size,
                color: { dark: opts.color, light: opts.bg },
                errorCorrectionLevel: opts.error
            }, (err) => {
                if (err) console.error(err);
                else console.log(`Сгенерирован: ${output}`);
            });
        });
        return;
    }

    if (!opts.data) {
        console.error('Укажите --data');
        process.exit(1);
    }

    const options = {
        width: opts.size,
        color: { dark: opts.color, light: opts.bg },
        errorCorrectionLevel: opts.error
    };

    if (opts.output) {
        QRCode.toFile(opts.output, opts.data, options, (err) => {
            if (err) console.error(err);
            else console.log(`QR-код сохранён в ${opts.output}`);
        });
    } else {
        QRCode.toString(opts.data, { type: 'svg', ...options }, (err, svg) => {
            if (err) console.error(err);
            else console.log(svg);
        });
    }
}

// ========== Браузерная версия ==========
if (typeof window !== 'undefined') {
    // Используем библиотеку qrcodejs для браузера
    // Подключите: <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    window.generateQR = function(data, size, color, bg) {
        const container = document.getElementById('qr-container');
        container.innerHTML = '';
        new QRCode(container, {
            text: data,
            width: size || 256,
            height: size || 256,
            colorDark: color || '#000000',
            colorLight: bg || '#ffffff',
            correctLevel: QRCode.CorrectLevel.M
        });
    };
}
