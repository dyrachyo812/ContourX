<div align="center">

# ContourX
### Превращаем любое фото в чистый чёрно-белый контур

![Python](https://img.shields.io/badge/Python-3.10+-a855f7?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-a855f7?style=for-the-badge)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-a855f7?style=for-the-badge&logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-a855f7?style=for-the-badge)

</div>

---

## Что это?

Десктопное приложение на Python, которое извлекает чёткий контур из любого изображения.
Удаляет все цвета, тени и текстуры — остаются только линии.

## Скриншот

> *(добавьте скриншот приложения сюда)*

## Быстрый старт

### Вариант 1 — двойной клик (только Windows)
Скачайте репозиторий и дважды щёлкните `start.bat`.
Всё остальное произойдёт автоматически.

### Вариант 2 — вручную
```bash
git clone https://github.com/ВАШ_НИК/contourx.git
cd contourx
pip install -r requirements.txt
python app.py
```

## Функции

- Загрузка любых форматов: JPG, PNG, BMP, TIFF, WEBP
- Два алгоритма: **Canny Edge Detection** и **Adaptive Threshold**
- Три настраиваемых параметра через ползунки
- Предпросмотр оригинала и результата в реальном времени
- Сохранение результата в PNG / JPEG
- Поддержка кириллических путей на Windows

## Технологии

| Библиотека | Назначение |
|---|---|
| CustomTkinter | Современный GUI |
| OpenCV | Обработка изображений |
| Pillow | Загрузка / сохранение файлов |
| NumPy | Работа с массивами пикселей |

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Лицензия

MIT — делайте что хотите.
