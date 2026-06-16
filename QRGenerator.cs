// QRGenerator.cs - Генератор QR-кодов на C# (CLI + WinForms)
// Требует QRCoder: Install-Package QRCoder
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Windows.Forms;
using QRCoder;

namespace QRGenerator
{
    public class QRGenerator
    {
        // ========== ОСНОВНАЯ ЛОГИКА ==========
        public static Bitmap GenerateQR(string data, int size, Color color, Color bg,
                                        QRCodeGenerator.ECCLevel errorLevel, Image logo = null)
        {
            var qrGenerator = new QRCodeGenerator();
            var qrData = qrGenerator.CreateQrCode(data, errorLevel);
            var qrCode = new QRCode(qrData);
            Bitmap qrImage = qrCode.GetGraphic(20, color, bg, true);

            // Изменяем размер
            if (qrImage.Width != size)
            {
                var resized = new Bitmap(size, size);
                using (var g = Graphics.FromImage(resized))
                {
                    g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic;
                    g.DrawImage(qrImage, 0, 0, size, size);
                }
                qrImage = resized;
            }

            // Добавление логотипа
            if (logo != null)
            {
                int logoSize = size / 4;
                Image scaledLogo = logo.GetThumbnailImage(logoSize, logoSize, null, IntPtr.Zero);
                using (var g = Graphics.FromImage(qrImage))
                {
                    int x = (size - logoSize) / 2;
                    int y = (size - logoSize) / 2;
                    g.DrawImage(scaledLogo, x, y, logoSize, logoSize);
                }
            }
            return qrImage;
        }

        // ========== CLI ==========
        static void Main(string[] args)
        {
            if (args.Length > 0 && args[0] == "--gui")
            {
                Application.EnableVisualStyles();
                Application.Run(new QRGeneratorGUI());
                return;
            }
            // CLI режим (упрощённый)
            try
            {
                string data = null, output = null, colorHex = "#000000", bgHex = "#ffffff", error = "M", logoPath = null;
                int size = 300;
                for (int i = 0; i < args.Length; i++)
                {
                    switch (args[i])
                    {
                        case "--data": data = args[++i]; break;
                        case "--output": output = args[++i]; break;
                        case "--size": size = int.Parse(args[++i]); break;
                        case "--color": colorHex = args[++i]; break;
                        case "--bg": bgHex = args[++i]; break;
                        case "--error": error = args[++i]; break;
                        case "--logo": logoPath = args[++i]; break;
                    }
                }
                if (string.IsNullOrEmpty(data))
                {
                    Console.WriteLine("Укажите --data");
                    return;
                }
                var color = ColorTranslator.FromHtml(colorHex);
                var bg = ColorTranslator.FromHtml(bgHex);
                var ecLevel = (QRCodeGenerator.ECCLevel)Enum.Parse(typeof(QRCodeGenerator.ECCLevel), error);
                Image logo = null;
                if (!string.IsNullOrEmpty(logoPath) && File.Exists(logoPath))
                {
                    logo = Image.FromFile(logoPath);
                }
                var img = GenerateQR(data, size, color, bg, ecLevel, logo);
                if (!string.IsNullOrEmpty(output))
                {
                    img.Save(output, ImageFormat.Png);
                    Console.WriteLine($"QR-код сохранён в {output}");
                }
                else
                {
                    Console.WriteLine("QR-код сгенерирован (сохраните через --output)");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Ошибка: {ex.Message}");
            }
        }

        // ========== GUI ==========
        public class QRGeneratorGUI : Form
        {
            private TextBox dataBox, colorBox, bgBox, logoBox;
            private NumericUpDown sizeUpDown;
            private ComboBox errorCombo;
            private PictureBox previewBox;
            private Bitmap lastImage;

            public QRGeneratorGUI()
            {
                Text = "Генератор QR-кодов";
                Size = new Size(600, 700);
                StartPosition = FormStartPosition.CenterScreen;

                var mainPanel = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 2, RowCount = 7, Padding = new Padding(10) };
                mainPanel.RowStyles.Add(new RowStyle(SizeType.AutoSize));
                mainPanel.RowStyles.Add(new RowStyle(SizeType.AutoSize));
                mainPanel.RowStyles.Add(new RowStyle(SizeType.AutoSize));
                mainPanel.RowStyles.Add(new RowStyle(SizeType.AutoSize));
                mainPanel.RowStyles.Add(new RowStyle(SizeType.AutoSize));
                mainPanel.RowStyles.Add(new RowStyle(SizeType.AutoSize));
                mainPanel.RowStyles.Add(new RowStyle(SizeType.Percent, 100));

                // Данные
                mainPanel.Controls.Add(new Label { Text = "Данные:", AutoSize = true }, 0, 0);
                dataBox = new TextBox { Multiline = true, Height = 60, Dock = DockStyle.Fill };
                mainPanel.Controls.Add(dataBox, 1, 0);

                // Размер
                mainPanel.Controls.Add(new Label { Text = "Размер:", AutoSize = true }, 0, 1);
                sizeUpDown = new NumericUpDown { Minimum = 100, Maximum = 1000, Value = 300, Increment = 10 };
                mainPanel.Controls.Add(sizeUpDown, 1, 1);

                // Цвета
                mainPanel.Controls.Add(new Label { Text = "Цвет точек:", AutoSize = true }, 0, 2);
                var colorPanel = new FlowLayoutPanel();
                colorBox = new TextBox { Text = "#000000", Width = 80 };
                var colorBtn = new Button { Text = "Выбрать", AutoSize = true };
                colorBtn.Click += (s, e) => ChooseColor(colorBox);
                colorPanel.Controls.Add(colorBox);
                colorPanel.Controls.Add(colorBtn);
                mainPanel.Controls.Add(colorPanel, 1, 2);

                mainPanel.Controls.Add(new Label { Text = "Цвет фона:", AutoSize = true }, 0, 3);
                var bgPanel = new FlowLayoutPanel();
                bgBox = new TextBox { Text = "#ffffff", Width = 80 };
                var bgBtn = new Button { Text = "Выбрать", AutoSize = true };
                bgBtn.Click += (s, e) => ChooseColor(bgBox);
                bgPanel.Controls.Add(bgBox);
                bgPanel.Controls.Add(bgBtn);
                mainPanel.Controls.Add(bgPanel, 1, 3);

                // Коррекция
                mainPanel.Controls.Add(new Label { Text = "Коррекция:", AutoSize = true }, 0, 4);
                errorCombo = new ComboBox { DropDownStyle = ComboBoxStyle.DropDownList, Items = { "L", "M", "Q", "H" }, SelectedIndex = 1 };
                mainPanel.Controls.Add(errorCombo, 1, 4);

                // Логотип
                mainPanel.Controls.Add(new Label { Text = "Логотип:", AutoSize = true }, 0, 5);
                var logoPanel = new FlowLayoutPanel();
                logoBox = new TextBox { Width = 150 };
                var logoBtn = new Button { Text = "Обзор...", AutoSize = true };
                logoBtn.Click += (s, e) => {
                    var ofd = new OpenFileDialog { Filter = "Image files|*.png;*.jpg;*.jpeg;*.gif" };
                    if (ofd.ShowDialog() == DialogResult.OK) logoBox.Text = ofd.FileName;
                };
                logoPanel.Controls.Add(logoBox);
                logoPanel.Controls.Add(logoBtn);
                mainPanel.Controls.Add(logoPanel, 1, 5);

                // Кнопки
                var btnPanel = new FlowLayoutPanel();
                var genBtn = new Button { Text = "Сгенерировать", AutoSize = true };
                genBtn.Click += (s, e) => Generate();
                btnPanel.Controls.Add(genBtn);
                var saveBtn = new Button { Text = "Сохранить...", AutoSize = true };
                saveBtn.Click += (s, e) => SaveImage();
                btnPanel.Controls.Add(saveBtn);
                mainPanel.Controls.Add(btnPanel, 1, 6);

                // Preview
                previewBox = new PictureBox { Dock = DockStyle.Fill, SizeMode = PictureBoxSizeMode.Zoom, BorderStyle = BorderStyle.FixedSingle, BackColor = Color.White };
                mainPanel.Controls.Add(previewBox, 0, 6);
                mainPanel.SetColumnSpan(previewBox, 2);

                Controls.Add(mainPanel);
            }

            private void ChooseColor(TextBox box)
            {
                var cd = new ColorDialog();
                if (cd.ShowDialog() == DialogResult.OK)
                {
                    box.Text = $"#{cd.Color.R:X2}{cd.Color.G:X2}{cd.Color.B:X2}";
                }
            }

            private void Generate()
            {
                try
                {
                    string data = dataBox.Text.Trim();
                    if (string.IsNullOrEmpty(data))
                    {
                        MessageBox.Show("Введите данные");
                        return;
                    }
                    int size = (int)sizeUpDown.Value;
                    var color = ColorTranslator.FromHtml(colorBox.Text);
                    var bg = ColorTranslator.FromHtml(bgBox.Text);
                    var error = (QRCodeGenerator.ECCLevel)Enum.Parse(typeof(QRCodeGenerator.ECCLevel), errorCombo.SelectedItem.ToString());
                    Image logo = null;
                    if (!string.IsNullOrEmpty(logoBox.Text) && File.Exists(logoBox.Text))
                    {
                        logo = Image.FromFile(logoBox.Text);
                    }
                    lastImage = GenerateQR(data, size, color, bg, error, logo);
                    previewBox.Image = lastImage;
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Ошибка: {ex.Message}");
                }
            }

            private void SaveImage()
            {
                if (lastImage == null)
                {
                    MessageBox.Show("Сначала сгенерируйте QR-код");
                    return;
                }
                var sfd = new SaveFileDialog { Filter = "PNG files|*.png", DefaultExt = "png" };
                if (sfd.ShowDialog() == DialogResult.OK)
                {
                    lastImage.Save(sfd.FileName, ImageFormat.Png);
                    MessageBox.Show("Сохранён");
                }
            }
        }
    }
}
