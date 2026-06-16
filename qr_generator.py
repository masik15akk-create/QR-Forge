"""
qr_generator.py - Генератор QR-кодов на Python (CLI + Tkinter GUI)
Поддерживает: настройку цвета, размера, вставку логотипа, массовую генерацию.
"""
import argparse
import os
import sys
import json
from pathlib import Path
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw
import io
import base64

# ========== ОСНОВНАЯ ЛОГИКА ==========
class QRGenerator:
    def __init__(self, data, output=None, size=300, color="#000000", bg="#ffffff",
                 error_correction="M", logo=None, version=1, box_size=10, border=4):
        self.data = data
        self.output = output
        self.size = size
        self.color = color
        self.bg = bg
        self.error_correction = error_correction
        self.logo = logo
        self.version = version
        self.box_size = box_size
        self.border = border

    def generate(self):
        # Уровень коррекции ошибок
        ec_level = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H
        }.get(self.error_correction.upper(), qrcode.constants.ERROR_CORRECT_M)

        # Создаём QR-код
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=ec_level,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(self.data)
        qr.make(fit=True)

        # Создаём изображение
        if self.logo and Path(self.logo).exists():
            # Используем стилизованное изображение с логотипом
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                color_mask=SolidFillColorMask(
                    back_color=Image.new('RGB', (1,1), self.bg).getpixel((0,0)),
                    front_color=Image.new('RGB', (1,1), self.color).getpixel((0,0))
                )
            )
            # Вставляем логотип
            logo_img = Image.open(self.logo).convert("RGBA")
            # Изменяем размер логотипа (не более 30% от размера QR)
            qr_size = img.size[0]
            logo_size = int(qr_size * 0.25)
            logo_img.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

            # Вычисляем позицию для вставки в центр
            pos = ((qr_size - logo_img.size[0]) // 2, (qr_size - logo_img.size[1]) // 2)
            img.paste(logo_img, pos, logo_img)
        else:
            # Обычное изображение
            img = qr.make_image(fill_color=self.color, back_color=self.bg)

        # Изменяем размер если нужно
        if img.size[0] != self.size:
            img = img.resize((self.size, self.size), Image.Resampling.LANCZOS)

        return img

    def save(self, img):
        if self.output:
            img.save(self.output)
            return self.output
        # Если выход не указан, возвращаем base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    @staticmethod
    def generate_batch(data_list, output_dir, **kwargs):
        """Массовая генерация QR-кодов из списка данных"""
        os.makedirs(output_dir, exist_ok=True)
        results = []
        for i, data in enumerate(data_list):
            gen = QRGenerator(data, **kwargs)
            img = gen.generate()
            output_path = Path(output_dir) / f"qr_{i+1}.png"
            img.save(output_path)
            results.append(str(output_path))
        return results

# ========== CLI ==========
def cli():
    parser = argparse.ArgumentParser(description="Генератор QR-кодов")
    parser.add_argument("--data", required=True, help="Данные для кодирования")
    parser.add_argument("--output", "-o", help="Путь для сохранения (PNG)")
    parser.add_argument("--size", type=int, default=300, help="Размер в пикселях")
    parser.add_argument("--color", default="#000000", help="Цвет точек")
    parser.add_argument("--bg", default="#ffffff", help="Цвет фона")
    parser.add_argument("--error", default="M", choices=["L","M","Q","H"], help="Уровень коррекции")
    parser.add_argument("--logo", help="Путь к логотипу (PNG с прозрачностью)")
    parser.add_argument("--version", type=int, default=1, help="Версия QR (1-40)")
    parser.add_argument("--batch", help="JSON-файл со списком данных для массовой генерации")
    parser.add_argument("--output-dir", default="qrs", help="Папка для массовой генерации")
    args = parser.parse_args()

    if args.batch:
        # Массовая генерация
        with open(args.batch, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        results = QRGenerator.generate_batch(
            data_list, args.output_dir,
            size=args.size, color=args.color, bg=args.bg,
            error_correction=args.error, logo=args.logo
        )
        print(f"Сгенерировано {len(results)} QR-кодов в {args.output_dir}")
        for r in results:
            print(f"  {r}")
        return

    gen = QRGenerator(
        data=args.data,
        output=args.output,
        size=args.size,
        color=args.color,
        bg=args.bg,
        error_correction=args.error,
        logo=args.logo,
        version=args.version
    )
    img = gen.generate()
    if args.output:
        gen.save(img)
        print(f"QR-код сохранён в {args.output}")
    else:
        # Выводим base64
        b64 = gen.save(img)
        print(f"data:image/png;base64,{b64}")

# ========== GUI ==========
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, colorchooser
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

if GUI_AVAILABLE:
    class QRGeneratorGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("Генератор QR-кодов")
            self.root.geometry("600x700")
            self.root.resizable(True, True)

            self.logo_path = None
            self.create_widgets()

        def create_widgets(self):
            # Данные
            tk.Label(self.root, text="Данные для кодирования:").pack(pady=5)
            self.data_entry = tk.Text(self.root, height=4, width=60)
            self.data_entry.pack(pady=5)

            # Параметры
            param_frame = tk.Frame(self.root)
            param_frame.pack(pady=10)

            # Размер
            tk.Label(param_frame, text="Размер:").grid(row=0, column=0, padx=5)
            self.size_var = tk.IntVar(value=300)
            tk.Spinbox(param_frame, from_=100, to=1000, textvariable=self.size_var, width=8).grid(row=0, column=1, padx=5)

            # Цвета
            tk.Label(param_frame, text="Цвет точек:").grid(row=0, column=2, padx=5)
            self.color_var = tk.StringVar(value="#000000")
            tk.Entry(param_frame, textvariable=self.color_var, width=10).grid(row=0, column=3, padx=5)
            tk.Button(param_frame, text="Выбрать", command=lambda: self.choose_color("color")).grid(row=0, column=4)

            tk.Label(param_frame, text="Цвет фона:").grid(row=1, column=0, padx=5)
            self.bg_var = tk.StringVar(value="#ffffff")
            tk.Entry(param_frame, textvariable=self.bg_var, width=10).grid(row=1, column=1, padx=5)
            tk.Button(param_frame, text="Выбрать", command=lambda: self.choose_color("bg")).grid(row=1, column=2)

            # Уровень коррекции
            tk.Label(param_frame, text="Коррекция:").grid(row=1, column=3, padx=5)
            self.error_var = tk.StringVar(value="M")
            ttk.Combobox(param_frame, textvariable=self.error_var, values=["L","M","Q","H"], width=5).grid(row=1, column=4)

            # Логотип
            tk.Label(param_frame, text="Логотип:").grid(row=2, column=0, padx=5)
            self.logo_label = tk.Label(param_frame, text="Не выбран", fg="gray")
            self.logo_label.grid(row=2, column=1, columnspan=2, padx=5)
            tk.Button(param_frame, text="Обзор...", command=self.browse_logo).grid(row=2, column=3, padx=5)

            # Кнопки
            btn_frame = tk.Frame(self.root)
            btn_frame.pack(pady=10)
            tk.Button(btn_frame, text="Сгенерировать", command=self.generate, bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Сохранить...", command=self.save, bg="#2ecc71", fg="white").pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Очистить", command=self.clear).pack(side=tk.LEFT, padx=5)

            # Предпросмотр
            self.preview_label = tk.Label(self.root, text="Предпросмотр", bg="white", width=40, height=20)
            self.preview_label.pack(pady=10)

        def choose_color(self, target):
            color = colorchooser.askcolor()[1]
            if color:
                if target == "color":
                    self.color_var.set(color)
                else:
                    self.bg_var.set(color)

        def browse_logo(self):
            path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
            if path:
                self.logo_path = path
                self.logo_label.config(text=Path(path).name, fg="green")

        def generate(self):
            data = self.data_entry.get("1.0", tk.END).strip()
            if not data:
                messagebox.showerror("Ошибка", "Введите данные")
                return
            try:
                gen = QRGenerator(
                    data=data,
                    size=self.size_var.get(),
                    color=self.color_var.get(),
                    bg=self.bg_var.get(),
                    error_correction=self.error_var.get(),
                    logo=self.logo_path
                )
                img = gen.generate()
                # Отображаем в preview
                from PIL import ImageTk
                # Масштабируем для предпросмотра
                preview_size = 300
                img.thumbnail((preview_size, preview_size), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                self.preview_label.config(image=tk_img, text="")
                self.preview_label.image = tk_img
                self.last_img = img
                self.last_gen = gen
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        def save(self):
            if not hasattr(self, 'last_img'):
                messagebox.showwarning("Нет данных", "Сначала сгенерируйте QR-код")
                return
            path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if path:
                self.last_img.save(path)
                messagebox.showinfo("Сохранено", f"Сохранён в {path}")

        def clear(self):
            self.data_entry.delete("1.0", tk.END)
            self.preview_label.config(image="", text="Предпросмотр")
            self.logo_path = None
            self.logo_label.config(text="Не выбран", fg="gray")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli()
    elif GUI_AVAILABLE:
        root = tk.Tk()
        app = QRGeneratorGUI(root)
        root.mainloop()
    else:
        print("Tkinter не установлен. Используйте CLI с параметрами.")
