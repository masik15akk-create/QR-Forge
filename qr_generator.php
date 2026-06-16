<?php
// qr_generator.php - Генератор QR-кодов на PHP (CLI + веб)
// Требует библиотеку phpqrcode: https://sourceforge.net/projects/phpqrcode/
// Для CLI: php qr_generator.php --data="Hello" --output=qr.png

if (php_sapi_name() === 'cli') {
    // CLI режим
    $options = getopt("", ["data:", "output:", "size:", "color:", "bg:", "error:", "batch:", "output-dir:"]);
    $data = $options['data'] ?? null;
    $output = $options['output'] ?? null;
    $size = isset($options['size']) ? (int)$options['size'] : 300;
    $color = $options['color'] ?? '#000000';
    $bg = $options['bg'] ?? '#ffffff';
    $error = $options['error'] ?? 'M';
    $batch = $options['batch'] ?? null;
    $outputDir = $options['output-dir'] ?? 'qrs';

    require_once 'phpqrcode/qrlib.php';

    if ($batch) {
        // Массовая генерация
        $dataList = json_decode(file_get_contents($batch), true);
        if (!is_dir($outputDir)) mkdir($outputDir, 0755, true);
        foreach ($dataList as $i => $d) {
            $path = $outputDir . '/qr_' . ($i+1) . '.png';
            QRcode::png($d, $path, $error, $size/100, 2);
            echo "Сгенерирован: $path\n";
        }
        exit;
    }

    if (!$data) {
        echo "Укажите --data\n";
        exit(1);
    }

    if ($output) {
        QRcode::png($data, $output, $error, $size/100, 2);
        echo "QR-код сохранён в $output\n";
    } else {
        // Выводим в stdout (base64)
        ob_start();
        QRcode::png($data, null, $error, $size/100, 2);
        $png = ob_get_clean();
        echo "data:image/png;base64," . base64_encode($png) . "\n";
    }
    exit;
}

// ========== ВЕБ-ИНТЕРФЕЙС ==========
?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Генератор QR-кодов (PHP)</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f4f7fb; margin: 40px; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        label { display: inline-block; width: 120px; }
        input, select, textarea { margin: 8px 0; padding: 6px; width: 100%; box-sizing: border-box; }
        button { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        .qr-result { margin-top: 20px; text-align: center; }
        img { max-width: 100%; }
    </style>
</head>
<body>
<div class="container">
    <h1>📱 Генератор QR-кодов</h1>
    <form method="GET">
        <label>Данные:</label>
        <textarea name="data" rows="3"><?= isset($_GET['data']) ? htmlspecialchars($_GET['data']) : 'https://github.com' ?></textarea>
        <label>Размер:</label>
        <input type="number" name="size" value="<?= isset($_GET['size']) ? $_GET['size'] : 300 ?>" min="100" max="1000">
        <label>Цвет точек:</label>
        <input type="color" name="color" value="<?= isset($_GET['color']) ? $_GET['color'] : '#000000' ?>">
        <label>Цвет фона:</label>
        <input type="color" name="bg" value="<?= isset($_GET['bg']) ? $_GET['bg'] : '#ffffff' ?>">
        <label>Коррекция:</label>
        <select name="error">
            <option value="L" <?= isset($_GET['error']) && $_GET['error']=='L' ? 'selected' : '' ?>>L</option>
            <option value="M" <?= !isset($_GET['error']) || $_GET['error']=='M' ? 'selected' : '' ?>>M</option>
            <option value="Q" <?= isset($_GET['error']) && $_GET['error']=='Q' ? 'selected' : '' ?>>Q</option>
            <option value="H" <?= isset($_GET['error']) && $_GET['error']=='H' ? 'selected' : '' ?>>H</option>
        </select>
        <button type="submit">Сгенерировать</button>
    </form>
    <?php
    if (isset($_GET['data']) && !empty($_GET['data'])) {
        require_once 'phpqrcode/qrlib.php';
        $data = $_GET['data'];
        $size = isset($_GET['size']) ? (int)$_GET['size'] : 300;
        $color = $_GET['color'] ?? '#000000';
        $bg = $_GET['bg'] ?? '#ffffff';
        $error = $_GET['error'] ?? 'M';

        // Генерируем QR-код во временный файл
        $tempFile = tempnam(sys_get_temp_dir(), 'qr') . '.png';
        QRcode::png($data, $tempFile, $error, $size/100, 2);

        // Перекрашиваем (phpqrcode не поддерживает цвета, используем GD)
        $im = imagecreatefrompng($tempFile);
        $w = imagesx($im);
        $h = imagesy($im);
        $newIm = imagecreatetruecolor($w, $h);

        // Цвета
        list($r, $g, $b) = sscanf($bg, "#%02x%02x%02x");
        $bgColor = imagecolorallocate($newIm, $r, $g, $b);
        imagefill($newIm, 0, 0, $bgColor);

        list($r, $g, $b) = sscanf($color, "#%02x%02x%02x");
        $fgColor = imagecolorallocate($newIm, $r, $g, $b);

        for ($x = 0; $x < $w; $x++) {
            for ($y = 0; $y < $h; $y++) {
                $pixel = imagecolorat($im, $x, $y);
                $rgb = imagecolorsforindex($im, $pixel);
                if ($rgb['red'] < 128 && $rgb['green'] < 128 && $rgb['blue'] < 128) {
                    imagesetpixel($newIm, $x, $y, $fgColor);
                }
            }
        }
        imagedestroy($im);

        // Вывод
        ob_start();
        imagepng($newIm);
        $png = ob_get_clean();
        imagedestroy($newIm);
        unlink($tempFile);

        echo '<div class="qr-result">';
        echo '<img src="data:image/png;base64,' . base64_encode($png) . '" alt="QR-код">';
        echo '<br><a href="data:image/png;base64,' . base64_encode($png) . '" download="qr.png">Скачать PNG</a>';
        echo '</div>';
    }
    ?>
</div>
</body>
</html>
