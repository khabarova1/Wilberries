"""Софт (скрипт), который будет выгружать видео-отзыв с маркетплейса."""

import os
import uuid
import time
import re
import subprocess
import keyboard
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def setup_driver():
    """Запускает/не запускает Chrome с настройками для перехвата сетевого трафика."""
    options = webdriver.ChromeOptions()
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    # Без открытия окна браузера
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = Service()
    return webdriver.Chrome(service=service, options=options)


def get_m3u8_url(driver, url):
    """Открывает или не открывает страницу и извлекает URL .m3u8
    из сетевых логов."""
    driver.get(url)
    time.sleep(25) # Потому что грузится долго!!!

    logs = driver.get_log("performance")
    for log in logs:
        if "m3u8" in log["message"]:
            match = re.search(r"https://[^\s]+?\.m3u8", log["message"])
            if match:
                return match.group(0)
    return None


def download_video(m3u8_url, output_file="downloads_wildberris"):
    """Скачивает видео из .m3u8 с помощью ffmpeg."""
    os.makedirs(output_file, exist_ok=True)
    filename = os.path.join(output_file, f"video_{uuid.uuid4()}.mp4")
    if m3u8_url:
        subprocess.run([
            "ffmpeg", "-headers", "User-Agent: Mozilla/5.0",
            "-i", m3u8_url, "-c", "copy", filename
        ])
        print(f"Видео сохранено как {filename}")
    else:
        print("Ошибка: m3u8 URL не найден.")


def start_download():
    """Функция для загрузки видео при нажатии F4."""
    url = "https://www.wildberries.ru/catalog/192186031/feedbacks?imtId=183532775&size=31%203642019"
    driver = setup_driver()
    try:
        print("Поиск .m3u8 URL...")
        m3u8_url = get_m3u8_url(driver, url)
        if m3u8_url:
            print(f"Найден .m3u8: {m3u8_url}")
            download_video(m3u8_url)
        else:
            print("❌ Ошибка: m3u8 URL не найден.")
    finally:
        driver.quit()


def main():
    print("Скрипт запущен. Нажмите F4 для загрузки видео...")
    keyboard.add_hotkey("F4",
                        start_download)
    keyboard.wait("esc")


if __name__ == "__main__":
    main()
