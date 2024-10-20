from pyautogui import *
import pygetwindow as gw
import pyautogui
import time
import keyboard
import random
from pynput.mouse import Button, Controller
import numpy as np
import cv2
import win32gui
from PIL import ImageGrab

mouse = Controller()
time.sleep(0.5)

def click(x, y):
    mouse.position = (x, y + random.randint(1, 3))
    mouse.press(Button.left)
    mouse.release(Button.left)

def print_welcome():
    print("""
          Hellow_world
[!] | | TELEGRAM .https://t.me/Avtomatiza_B                  
[!] | | Добро пожаловать в автокликер для Blum.
[!] | | Для использования окна Telegram Desktop по умолчанию введите 1.
[!] | | Для указания другого окна введите 2.
""")

def print_pause_message(paused):
    if paused:
        print('[-] | Пауза активирована, нажмите "q" для продолжения.')
    else:
        print('[+] | Работа продолжается.')

def print_not_found_message(window_name):
    print(f"[-] | Окно - {window_name} не найдено!")

def print_found_message(window_name):
    print(f"[+] | Окно найдено - {window_name}\n[+] | Нажмите 'q' для паузы.")

def print_stop_message():
    print('[!] | Программа остановлена.')

def get_client_rect(hwnd):
    rect = win32gui.GetClientRect(hwnd)
    left, top = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
    right, bottom = win32gui.ClientToScreen(hwnd, (rect[2], rect[3]))
    return (left + 10, top + 10, right - 10, bottom - 10)

def is_play_button_visible(window, threshold=10):
    left, top, right, bottom = get_client_rect(window._hWnd)
    width = right - left
    height = bottom - top
    
    # Определяем область для поиска кнопки "Play"
    search_top = top + int(height * 0.80)  # 80% от высоты окна
    search_height = int(height * 0.10)     # 10% от высоты окна
    search_bottom = search_top + search_height
    
    screenshot = pyautogui.screenshot(region=(left, search_top, width, search_height))
    screenshot = np.array(screenshot)
    
    # Преобразуем скриншот в формат, используемый для анализа
    white_pixel_ratio, _, _ = analyze_search_area(screenshot)
    return white_pixel_ratio > threshold

def analyze_search_area(image, ignore_percent=0.1, search_percent=0.1):
    height, width, _ = image.shape
    ignore_height = int(height * ignore_percent)
    search_height = int(height * search_percent)
    search_top = height - ignore_height - search_height
    start_point = (0, search_top)
    end_point = (width, search_top + search_height)
    white_pixel_count = 0
    total_pixels = (end_point[0] - start_point[0]) * (end_point[1] - start_point[1])
    
    for x in range(start_point[0], end_point[0]):
        for y in range(start_point[1], end_point[1]):
            if np.array_equal(image[y, x], [255, 255, 255]):
                white_pixel_count += 1

    white_pixel_ratio = white_pixel_count / total_pixels * 100

    return white_pixel_ratio, white_pixel_count, total_pixels

print_welcome()

choice = input('\nВведите ваш выбор: ')

if choice == '1':
    window_name = "TelegramDesktop"
elif choice == '2':
    print('Пожалуйста, активируйте нужное окно и нажмите Enter.')
    while not keyboard.is_pressed('Enter'):
        time.sleep(0.1)
    active_window = gw.getActiveWindow()
    if active_window:
        window_name = active_window.title
    else:
        window_name = None
else:
    window_name = "TelegramDesktop"

if window_name is None:
    print_not_found_message("активное окно")
else:
    check = gw.getWindowsWithTitle(window_name)
    if not check:
        print_not_found_message(window_name)
    else:
        print_found_message(window_name)

telegram_window = check[0] if window_name is not None else None
paused = False

# Диапазоны цветов для зеленых и синих бактерий, а также для бомб
green_bacteria_range = ((104, 234, 21), (132, 255, 49))
blue_bacteria_range = ((88, 164, 174), (242, 255, 255))
bomb_range = ((50, 50, 50), (200, 200, 200))

def is_color_in_range(color, color_range):
    return all(color_range[0][i] <= color[i] <= color_range[1][i] for i in range(3))

# Получаем количество игр от пользователя
try:
    game_count = int(input('Введите количество игр для автокликера (оставьте пустым для бесконечного режима): '))
except ValueError:
    game_count = None

play_clicks = 0
counter = 0
wait_for_pause = False

while telegram_window:
    if keyboard.is_pressed('q'):
        paused = not paused
        print_pause_message(paused)
        time.sleep(0.2)

    if paused:
        continue

    window_rect = (
        telegram_window.left, telegram_window.top, telegram_window.width, telegram_window.height
    )

    if telegram_window != []:
        try:
            telegram_window.activate()
        except:
            telegram_window.minimize()
            telegram_window.restore()

    scrn = pyautogui.screenshot(region=(window_rect[0], window_rect[1], window_rect[2], window_rect[3]))

    width, height = scrn.size
    pixel_found = False

    for x in range(0, width, 20):
        for y in range(0, height, 20):
            r, g, b = scrn.getpixel((x, y))
            color = (r, g, b)

            if is_color_in_range(color, green_bacteria_range) or is_color_in_range(color, blue_bacteria_range):
                screen_x = window_rect[0] + x
                screen_y = window_rect[1] + y

                is_bomb = False
                try:
                    for bx in range(-5, 6):
                        for by in range(-5, 6):
                            br, bg, bb = scrn.getpixel((x + bx, y + by))
                            if is_color_in_range((br, bg, bb), bomb_range):
                                is_bomb = True
                                break
                        if is_bomb:
                            break
                except:
                    continue

                if not is_bomb:
                    click(screen_x + 4, screen_y)
                    time.sleep(0.001)
                    pixel_found = True
                    break

    counter += 1
    if counter >= 60:  # Проверка кнопки "Play" каждые 60 итераций
        counter = 0
        if is_play_button_visible(telegram_window):
            if wait_for_pause:
                paused = True
                print(f"[!] | Кнопка 'Play' появилась {play_clicks + 1} раз. Скрипт поставлен на паузу.")
                break
            else:
                left, top, right, bottom = get_client_rect(telegram_window._hWnd)
                click_x = left + (right - left) // 2
                click_y = top + int((bottom - top) * 0.85)
                click(click_x, click_y)
                play_clicks += 1
                print(f"[+] | Кнопка 'Play' найдена и нажата {play_clicks} раз(а).")
                if game_count is not None and play_clicks >= game_count:
                    print(f"[!] | Достигнуто заданное количество игр: {game_count}. Ожидание появления кнопки 'Play' для паузы.")
                    wait_for_pause = True

    if not pixel_found:
        time.sleep(0.1)

print_stop_message()
