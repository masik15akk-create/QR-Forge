// QRGenerator.java - Генератор QR-кодов на Java (CLI + Swing GUI)
// Требует ZXing: https://github.com/zxing/zxing/releases
import com.google.zxing.*;
import com.google.zxing.client.j2se.MatrixToImageWriter;
import com.google.zxing.common.BitMatrix;
import com.google.zxing.qrcode.QRCodeWriter;
import com.google.zxing.qrcode.decoder.ErrorCorrectionLevel;

import javax.imageio.ImageIO;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import java.util.List;

public class QRGenerator {
    // ========== ОСНОВНАЯ ЛОГИКА ==========
    public static BufferedImage generateQR(String data, int size, String colorHex, String bgHex,
                                           String errorLevel, String logoPath) throws WriterException, IOException {
        Map<EncodeHintType, Object> hints = new HashMap<>();
        hints.put(EncodeHintType.ERROR_CORRECTION, ErrorCorrectionLevel.valueOf(errorLevel));
        hints.put(EncodeHintType.MARGIN, 1);

        QRCodeWriter writer = new QRCodeWriter();
        BitMatrix matrix = writer.encode(data, BarcodeFormat.QR_CODE, size, size, hints);

        BufferedImage image = MatrixToImageWriter.toBufferedImage(matrix);
        // Перекрашиваем в нужные цвета
        BufferedImage colored = new BufferedImage(size, size, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = colored.createGraphics();
        g.setColor(Color.decode(bgHex));
        g.fillRect(0, 0, size, size);
        g.setColor(Color.decode(colorHex));
        for (int x = 0; x < size; x++) {
            for (int y = 0; y < size; y++) {
                if (matrix.get(x, y)) {
                    g.fillRect(x, y, 1, 1);
                }
            }
        }
        g.dispose();

        // Добавление логотипа
        if (logoPath != null && !logoPath.isEmpty()) {
            try {
                BufferedImage logo = ImageIO.read(new File(logoPath));
                int logoSize = size / 4;
                Image scaledLogo = logo.getScaledInstance(logoSize, logoSize, Image.SCALE_SMOOTH);
                int x = (size - logoSize) / 2;
                int y = (size - logoSize) / 2;
                g = colored.createGraphics();
                g.drawImage(scaledLogo, x, y, null);
                g.dispose();
            } catch (IOException e) {
                System.err.println("Не удалось загрузить логотип: " + e.getMessage());
            }
        }
        return colored;
    }

    public static void saveImage(BufferedImage img, String path) throws IOException {
        ImageIO.write(img, "png", new File(path));
    }

    // ========== CLI ==========
    public static void main(String[] args) {
        if (args.length > 0 && args[0].equals("--gui")) {
            SwingUtilities.invokeLater(() -> new QRGeneratorGUI().setVisible(true));
            return;
        }
        // CLI режим (упрощённый)
        try {
            String data = null, output = null, color = "#000000", bg = "#ffffff", error = "M", logo = null;
            int size = 300;
            for (int i = 0; i < args.length; i++) {
                switch (args[i]) {
                    case "--data": data = args[++i]; break;
                    case "--output": output = args[++i]; break;
                    case "--size": size = Integer.parseInt(args[++i]); break;
                    case "--color": color = args[++i]; break;
                    case "--bg": bg = args[++i]; break;
                    case "--error": error = args[++i]; break;
                    case "--logo": logo = args[++i]; break;
                }
            }
            if (data == null) {
                System.err.println("Укажите --data");
                return;
            }
            BufferedImage img = generateQR(data, size, color, bg, error, logo);
            if (output != null) {
                saveImage(img, output);
                System.out.println("QR-код сохранён в " + output);
            } else {
                // Выводим base64 (упрощённо)
                System.out.println("Сгенерирован QR-код (сохраните через --output)");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // ========== GUI ==========
    static class QRGeneratorGUI extends JFrame {
        private JTextArea dataArea;
        private JSpinner sizeSpinner;
        private JTextField colorField, bgField, logoField;
        private JComboBox<String> errorCombo;
        private JLabel previewLabel;
        private BufferedImage lastImage;

        public QRGeneratorGUI() {
            setTitle("Генератор QR-кодов");
            setSize(600, 700);
            setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            setLayout(new BorderLayout(10, 10));

            JPanel topPanel = new JPanel(new GridBagLayout());
            GridBagConstraints gbc = new GridBagConstraints();
            gbc.insets = new Insets(5, 5, 5, 5);
            gbc.fill = GridBagConstraints.HORIZONTAL;

            gbc.gridx = 0; gbc.gridy = 0;
            topPanel.add(new JLabel("Данные:"), gbc);
            gbc.gridx = 1; gbc.gridwidth = 3;
            dataArea = new JTextArea(4, 30);
            topPanel.add(new JScrollPane(dataArea), gbc);

            gbc.gridy = 1; gbc.gridwidth = 1;
            gbc.gridx = 0;
            topPanel.add(new JLabel("Размер:"), gbc);
            gbc.gridx = 1;
            sizeSpinner = new JSpinner(new SpinnerNumberModel(300, 100, 1000, 10));
            topPanel.add(sizeSpinner, gbc);

            gbc.gridx = 2;
            topPanel.add(new JLabel("Коррекция:"), gbc);
            gbc.gridx = 3;
            errorCombo = new JComboBox<>(new String[]{"L", "M", "Q", "H"});
            topPanel.add(errorCombo, gbc);

            gbc.gridy = 2; gbc.gridx = 0;
            topPanel.add(new JLabel("Цвет точек:"), gbc);
            gbc.gridx = 1;
            colorField = new JTextField("#000000", 8);
            topPanel.add(colorField, gbc);
            JButton colorBtn = new JButton("Выбрать");
            colorBtn.addActionListener(e -> chooseColor(colorField));
            gbc.gridx = 2;
            topPanel.add(colorBtn, gbc);

            gbc.gridx = 3;
            topPanel.add(new JLabel("Цвет фона:"), gbc);
            gbc.gridx = 4;
            bgField = new JTextField("#ffffff", 8);
            topPanel.add(bgField, gbc);
            JButton bgBtn = new JButton("Выбрать");
            bgBtn.addActionListener(e -> chooseColor(bgField));
            gbc.gridx = 5;
            topPanel.add(bgBtn, gbc);

            gbc.gridy = 3; gbc.gridx = 0;
            topPanel.add(new JLabel("Логотип:"), gbc);
            gbc.gridx = 1; gbc.gridwidth = 2;
            logoField = new JTextField(15);
            topPanel.add(logoField, gbc);
            JButton logoBtn = new JButton("Обзор...");
            logoBtn.addActionListener(e -> {
                JFileChooser fc = new JFileChooser();
                if (fc.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
                    logoField.setText(fc.getSelectedFile().getAbsolutePath());
                }
            });
            gbc.gridx = 3;
            topPanel.add(logoBtn, gbc);

            add(topPanel, BorderLayout.NORTH);

            JButton generateBtn = new JButton("Сгенерировать");
            generateBtn.addActionListener(e -> generate());
            add(generateBtn, BorderLayout.CENTER);

            previewLabel = new JLabel("Предпросмотр", SwingConstants.CENTER);
            previewLabel.setPreferredSize(new Dimension(300, 300));
            previewLabel.setBorder(BorderFactory.createLineBorder(Color.GRAY));
            add(previewLabel, BorderLayout.SOUTH);

            JPanel btnPanel = new JPanel();
            JButton saveBtn = new JButton("Сохранить...");
            saveBtn.addActionListener(e -> saveImage());
            btnPanel.add(saveBtn);
            add(btnPanel, BorderLayout.AFTER_LAST_LINE);
        }

        private void chooseColor(JTextField field) {
            Color c = JColorChooser.showDialog(this, "Выберите цвет", Color.decode(field.getText()));
            if (c != null) {
                field.setText(String.format("#%02x%02x%02x", c.getRed(), c.getGreen(), c.getBlue()));
            }
        }

        private void generate() {
            try {
                String data = dataArea.getText().trim();
                if (data.isEmpty()) {
                    JOptionPane.showMessageDialog(this, "Введите данные");
                    return;
                }
                int size = (Integer) sizeSpinner.getValue();
                String color = colorField.getText();
                String bg = bgField.getText();
                String error = (String) errorCombo.getSelectedItem();
                String logo = logoField.getText().trim();
                if (logo.isEmpty()) logo = null;

                lastImage = generateQR(data, size, color, bg, error, logo);
                ImageIcon icon = new ImageIcon(lastImage.getScaledInstance(300, 300, Image.SCALE_SMOOTH));
                previewLabel.setIcon(icon);
                previewLabel.setText("");
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Ошибка: " + ex.getMessage());
            }
        }

        private void saveImage() {
            if (lastImage == null) {
                JOptionPane.showMessageDialog(this, "Сначала сгенерируйте QR-код");
                return;
            }
            JFileChooser fc = new JFileChooser();
            fc.setSelectedFile(new File("qr.png"));
            if (fc.showSaveDialog(this) == JFileChooser.APPROVE_OPTION) {
                try {
                    ImageIO.write(lastImage, "png", fc.getSelectedFile());
                    JOptionPane.showMessageDialog(this, "Сохранён");
                } catch (IOException ex) {
                    JOptionPane.showMessageDialog(this, "Ошибка: " + ex.getMessage());
                }
            }
        }
    }
}
