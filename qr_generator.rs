// qr_generator.rs - Генератор QR-кодов на Rust (CLI)
// Зависимости: qrcode, image, clap
use clap::{Arg, App};
use qrcode::QrCode;
use qrcode::EcLevel;
use image::{ImageBuffer, Rgb, ImageFormat};
use std::fs;
use std::path::Path;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let matches = App::new("QR Generator")
        .arg(Arg::with_name("data").short("d").long("data").takes_value(true).required(true).help("Данные для кодирования"))
        .arg(Arg::with_name("output").short("o").long("output").takes_value(true).help("Путь для сохранения (PNG)"))
        .arg(Arg::with_name("size").short("s").long("size").takes_value(true).default_value("300").help("Размер в пикселях"))
        .arg(Arg::with_name("color").short("c").long("color").takes_value(true).default_value("#000000").help("Цвет точек"))
        .arg(Arg::with_name("bg").short("b").long("bg").takes_value(true).default_value("#ffffff").help("Цвет фона"))
        .arg(Arg::with_name("error").short("e").long("error").takes_value(true).default_value("M").help("Уровень коррекции (L,M,Q,H)"))
        .arg(Arg::with_name("batch").long("batch").takes_value(true).help("JSON-файл со списком данных"))
        .arg(Arg::with_name("output-dir").long("output-dir").takes_value(true).default_value("qrs").help("Папка для массовой генерации"))
        .get_matches();

    let data = matches.value_of("data").unwrap();
    let size: u32 = matches.value_of("size").unwrap().parse()?;
    let color = hex_to_rgb(matches.value_of("color").unwrap());
    let bg = hex_to_rgb(matches.value_of("bg").unwrap());
    let ec_level = match matches.value_of("error").unwrap() {
        "L" => EcLevel::L,
        "Q" => EcLevel::Q,
        "H" => EcLevel::H,
        _ => EcLevel::M,
    };

    if let Some(batch_file) = matches.value_of("batch") {
        // Массовая генерация
        let content = fs::read_to_string(batch_file)?;
        let data_list: Vec<String> = serde_json::from_str(&content)?;
        let output_dir = matches.value_of("output-dir").unwrap();
        fs::create_dir_all(output_dir)?;
        for (i, d) in data_list.iter().enumerate() {
            let code = QrCode::with_error_correction_level(d, ec_level)?;
            let img = render_qr(&code, size, color, bg);
            let path = format!("{}/qr_{}.png", output_dir, i+1);
            img.save(&path)?;
            println!("Сгенерирован: {}", path);
        }
        return Ok(());
    }

    let code = QrCode::with_error_correction_level(data, ec_level)?;
    let img = render_qr(&code, size, color, bg);

    if let Some(output) = matches.value_of("output") {
        img.save(output)?;
        println!("QR-код сохранён в {}", output);
    } else {
        // Выводим PNG в stdout (base64)
        let mut buffer = Vec::new();
        img.write_to(&mut buffer, ImageFormat::Png)?;
        println!("data:image/png;base64,{}", base64::encode(&buffer));
    }
    Ok(())
}

fn hex_to_rgb(hex: &str) -> [u8; 3] {
    let hex = hex.trim_start_matches('#');
    if hex.len() == 6 {
        let r = u8::from_str_radix(&hex[0..2], 16).unwrap_or(0);
        let g = u8::from_str_radix(&hex[2..4], 16).unwrap_or(0);
        let b = u8::from_str_radix(&hex[4..6], 16).unwrap_or(0);
        [r, g, b]
    } else {
        [0, 0, 0]
    }
}

fn render_qr(code: &QrCode, size: u32, color: [u8; 3], bg: [u8; 3]) -> ImageBuffer<Rgb<u8>, Vec<u8>> {
    let modules = code.modules();
    let module_count = modules.size() as u32;
    let module_size = size / module_count;
    let actual_size = module_size * module_count;

    let mut img = ImageBuffer::new(actual_size, actual_size);
    for y in 0..module_count {
        for x in 0..module_count {
            let pixel = if modules[(x as usize, y as usize)] { color } else { bg };
            for dy in 0..module_size {
                for dx in 0..module_size {
                    img.put_pixel(x * module_size + dx, y * module_size + dy, Rgb(pixel));
                }
            }
        }
    }
    img
}
