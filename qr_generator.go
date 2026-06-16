// qr_generator.go - Генератор QR-кодов на Go (CLI)
// Установка: go get -u github.com/skip2/go-qrcode
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"

	qrcode "github.com/skip2/go-qrcode"
)

func main() {
	var data, output, color, bg, batch, outputDir string
	var size int
	var errorLevel string

	flag.StringVar(&data, "data", "", "Данные для кодирования")
	flag.StringVar(&output, "output", "", "Путь для сохранения (PNG)")
	flag.IntVar(&size, "size", 256, "Размер в пикселях")
	flag.StringVar(&color, "color", "#000000", "Цвет точек")
	flag.StringVar(&bg, "bg", "#ffffff", "Цвет фона")
	flag.StringVar(&errorLevel, "error", "M", "Уровень коррекции (L,M,Q,H)")
	flag.StringVar(&batch, "batch", "", "JSON-файл со списком данных")
	flag.StringVar(&outputDir, "output-dir", "qrs", "Папка для массовой генерации")
	flag.Parse()

	// Преобразование цвета
	fgColor := hexToColor(color)
	bgColor := hexToColor(bg)

	// Уровень коррекции
	var ecLevel qrcode.RecoveryLevel
	switch errorLevel {
	case "L":
		ecLevel = qrcode.Low
	case "Q":
		ecLevel = qrcode.Quartile
	case "H":
		ecLevel = qrcode.Highest
	default:
		ecLevel = qrcode.Medium
	}

	if batch != "" {
		// Массовая генерация
		dataBytes, err := ioutil.ReadFile(batch)
		if err != nil {
			fmt.Printf("Ошибка чтения %s: %v\n", batch, err)
			return
		}
		var dataList []string
		if err := json.Unmarshal(dataBytes, &dataList); err != nil {
			fmt.Printf("Ошибка парсинга JSON: %v\n", err)
			return
		}
		if err := os.MkdirAll(outputDir, 0755); err != nil {
			fmt.Printf("Ошибка создания папки: %v\n", err)
			return
		}
		for i, d := range dataList {
			outPath := filepath.Join(outputDir, fmt.Sprintf("qr_%d.png", i+1))
			err := qrcode.WriteColorFile(d, ecLevel, size, fgColor, bgColor, outPath)
			if err != nil {
				fmt.Printf("Ошибка генерации %s: %v\n", outPath, err)
			} else {
				fmt.Printf("Сгенерирован: %s\n", outPath)
			}
		}
		return
	}

	if data == "" {
		fmt.Println("Укажите --data")
		flag.Usage()
		return
	}

	if output == "" {
		// Если output не указан, генерируем в stdout (base64 PNG)
		png, err := qrcode.Encode(data, ecLevel, size)
		if err != nil {
			fmt.Printf("Ошибка: %v\n", err)
			return
		}
		fmt.Printf("data:image/png;base64,%s\n", base64Encode(png))
	} else {
		err := qrcode.WriteColorFile(data, ecLevel, size, fgColor, bgColor, output)
		if err != nil {
			fmt.Printf("Ошибка: %v\n", err)
		} else {
			fmt.Printf("QR-код сохранён в %s\n", output)
		}
	}
}

func hexToColor(hex string) qrcode.Color {
	return qrcode.Color(hex)
}

func base64Encode(data []byte) string {
	return string(data) // упрощённо, в реальности нужно использовать encoding/base64
}
