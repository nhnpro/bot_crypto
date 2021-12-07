from random import randint
import pyautogui as pag
from time import sleep, time
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
import sys
from notifiers import get_notifier
from datetime import datetime as dt
from skimage.metrics import structural_similarity
import cv2
from json import load


class Clicker(QThread):
    append_text = pyqtSignal(str)
    set_text = pyqtSignal(str)

    def __init__(self, refresh_minutes, re_enter_map):
        super(Clicker, self).__init__()
        self.refresh_minutes = int(refresh_minutes) * 60
        self.re_enter_map = int(re_enter_map) * 60
        self.current_time = '%H:%M'
        self.telegram = get_notifier('telegram')
        with open('Requirements.json') as file:
            data = load(file)
        self.username = data['user']
        self.telegram_chat_id = data['telegram chat id']
        self.telegram_token = data['telegram bot token']
        self.max_time_captcha = data['max time captcha']
        self.mouse_up_if_difference = data['mouse up if top difference more than']

    def run(self):
        while True:
            try:
                while True:
                    self.do_all_steps()
                    last_refresh_time = time()
                    while True:
                        if time() - last_refresh_time > self.refresh_minutes:
                            self.set_text.emit(
                                f'Refreshing page, because last refresh was in {self.refresh_minutes / 60} minutes')
                            break
                        last_remap_time = time()
                        while True:
                            if time() - last_refresh_time > self.refresh_minutes + randint(0, 300):
                                break
                            self.check_error()
                            self.check_new_map()
                            if time() - last_remap_time > self.re_enter_map + randint(-30, 30):
                                self.append_text.emit(f'{dt.now().strftime(self.current_time)} Re enter to the map')
                                self.back_from_map()
                                break
                            minutes_before_remap = last_remap_time + self.re_enter_map - time()
                            self.append_text.emit(f'{dt.now().strftime(self.current_time)} Next re enter to the map in '
                                               f'{round(minutes_before_remap / 60, 2)} minutes')
                            sleep(20)
            except:
                if self.telegram_token and self.telegram_chat_id:
                    self.telegram.notify(token=self.telegram_token, chat_id=self.telegram_chat_id,
                                     message=f'Error with bot {self.username}')
                pag.screenshot('FATAL ERROR.png')
                self.set_text.emit('FATAL ERROR')

    def do_all_steps(self):
        self.refresh_and_connect()
        self.go_to_heroes()
        self.clicks_to_work()
        self.exit_from_heroes()
        self.go_hunt_function()

    def refresh_and_connect(self):
        self.refresh_page()
        self.connect_wallet()
        self.apply_metamask()

    def check_captcha(self):
        robot = pag.locateCenterOnScreen('targets/Robot.png', confidence=0.95)
        if robot is None:
            self.append_text.emit(f'{dt.now().strftime(self.current_time)} Captcha is not detected')
            return False
        else:
            self.append_text.emit(f'{dt.now().strftime(self.current_time)} Captcha detected')
            return True

    def solve_captcha(self):
        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Trying solve captcha..')
        try:
            for i in range(1, 4):
                self.do_captcha()
                sleep(2)
                robot = pag.locateCenterOnScreen('targets/Robot.png', confidence=0.95)
                if robot is None:
                    return True
                if i == 3:
                    self.append_text.emit(f'{dt.now().strftime(self.current_time)} Ended attempts, refreshing..')
                    return False
        except:
            self.append_text.emit(f'{dt.now().strftime(self.current_time)} Error in captcha block')
            return False

    def do_captcha(self):
        slider = pag.locateCenterOnScreen('targets/Slider.png', confidence=0.95)
        robot = pag.locateCenterOnScreen('targets/Robot.png', confidence=0.95)
        x, y = robot
        slider_posx, slider_posy = slider
        slider_posx += randint(-7, 7)
        slider_posy += randint(-3, 3)
        pag.moveTo(slider_posx, slider_posy)
        pag.mouseDown()
        top_difference = 0
        default_pixel = 10
        start_time = time()
        while True:
            if time() - start_time > float(self.max_time_captcha):
                pag.moveTo(best_moment, slider_posy)
                sleep(1)
                pag.mouseUp()
                return
            pag.screenshot('temp/before.png', region=(x - 210, y + 30, 420, 300))
            before = cv2.imread('temp/before.png')
            pag.screenshot('temp/after.png', region=(x - 210, y + 30, 420, 300))
            after = cv2.imread('temp/after.png')
            before = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
            after = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)
            difference = structural_similarity(before, after, full=True)[0]
            if difference > top_difference:
                top_difference = difference
                best_moment = slider_posx
            if self.mouse_up_if_difference:
                if top_difference - difference > float(self.mouse_up_if_difference):
                    pag.moveTo(best_moment, slider_posy)
                    sleep(1)
                    pag.mouseUp()
                    return
            if difference > 0.98:
                default_pixel = 10
            if difference > 0.99:
                default_pixel = 1
            slider_posx += default_pixel
            pag.moveTo(slider_posx, slider_posy)

    def check_new_map(self):
        new_map = pag.locateCenterOnScreen('targets/New map.png', confidence=0.9)
        if new_map is not None:
            self.append_text.emit(f'{dt.now().strftime(self.current_time)} Go to new map')
            while True:
                pag.click(new_map[0] + randint(-80, 80), new_map[1] + randint(-25, 25))
                sleep(2)
                new_map = pag.locateCenterOnScreen('targets/New map.png', confidence=0.9)
                if new_map is None:
                    if self.check_captcha():
                        if self.solve_captcha():
                            sleep(2)
                            back_from_map = pag.locateCenterOnScreen('targets/Back from map.png', confidence=0.95)
                            if back_from_map is None:
                                return self.refresh_and_connect(), self.go_hunt_function()
                            return
                        return self.refresh_and_connect(), self.go_hunt_function()
                    return
        else:
            self.append_text.emit(f'{dt.now().strftime(self.current_time)} New map is not detected')

    def apply_metamask(self):
        if self.check_captcha():
            while True:
                if self.solve_captcha():
                    sleep(2)
                    apply_metamask = pag.locateCenterOnScreen('targets/Apply metamask.png', confidence=0.95)
                    if apply_metamask is not None:
                        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Captcha passed!')
                        pag.click(apply_metamask[0] + randint(-35, 35), apply_metamask[1] + randint(-20, 20))
                        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Apply from metamask clicked')
                        return
                    break
                else:
                    return self.refresh_and_connect()

        waiting_apply_metamask = 0
        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Waiting metamask button')
        while True:
            apply_metamask = pag.locateCenterOnScreen('targets/Apply metamask.png', confidence=0.95)
            if apply_metamask is None:
                waiting_apply_metamask += 1
                if waiting_apply_metamask == 30:
                    self.append_text.emit(f"{dt.now().strftime(self.current_time)} Didn't  see metamask button, refreshing")
                    return self.refresh_and_connect()
                sleep(1)
                continue
            pag.click(apply_metamask[0] + randint(-35,  35), apply_metamask[1] + randint(-20, 20))
            self.append_text.emit(f'{dt.now().strftime(self.current_time)} Apply from metamask clicked')
            sleep(3)
            break

    def check_error(self):
        ok_error_button = pag.locateCenterOnScreen('targets/Ok error.png', confidence=0.9)
        if ok_error_button is not None:
            self.append_text.emit(f'{dt.now().strftime(self.current_time)} Error detected, refreshing..')
            return self.refresh_and_connect(), self.go_hunt_function()
        else:
            self.append_text.emit(f'{dt.now().strftime(self.current_time)} No errors detected')

    def refresh_page(self):
        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Refreshing page..')
        bcrypto_tab = pag.locateCenterOnScreen('targets/BCrypto tab.png', confidence=0.9)
        pag.click(bcrypto_tab[0] + randint(-80, 80), bcrypto_tab[1] + randint(-4, 4))
        sleep(0.5)
        pag.press('f5')
        sleep(3)

    def connect_wallet(self):
        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Waiting connect button..')
        waiting_wallet_button = 0
        while True:
            connect_wallet = pag.locateCenterOnScreen('targets/Connect wallet.png', confidence=0.9)
            if connect_wallet is None:
                waiting_wallet_button += 1
                if waiting_wallet_button == 30:
                    self.append_text.emit(f"{dt.now().strftime(self.current_time)} Didn't  see connect button, refreshing")
                    return self.refresh_page(), self.connect_wallet()
                sleep(1)
                continue
            pag.click(connect_wallet[0] + randint(-120, 120), connect_wallet[1] + randint(-35, 35))
            self.append_text.emit(f'{dt.now().strftime(self.current_time)} Connect button clicked')
            break
        sleep(2)

    def go_to_heroes(self):
        waiting_heroes = 0
        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Waiting Heroes button')
        while True:
            heroes = pag.locateCenterOnScreen('targets/Heroes.png', confidence=0.95)
            if heroes is None:
                waiting_heroes += 1
                sleep(1)
                if waiting_heroes == 90:
                    self.append_text.emit(f"{dt.now().strftime(self.current_time)} Didn't see Heroes button, refreshing..")
                    return self.refresh_and_connect(), self.go_to_heroes()
                continue
            break
        waiting_heroes = 0
        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Go to Heroes')
        while True:
            pag.click(heroes[0] + randint(-15, 15), heroes[1] + randint(-20, 20))
            sleep(1)
            heroes = pag.locateCenterOnScreen('targets/Heroes.png', confidence=0.95)
            if heroes is None:
                break
            waiting_heroes += 1
            if waiting_heroes == 30:
                return self.refresh_and_connect(), self.go_to_heroes()

    def go_hunt_function(self):
        waiting_hunt = 0
        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Waiting Hunt button..')
        while True:
            go_hunt = pag.locateCenterOnScreen('targets/Go hunt.png', confidence=0.9)
            if go_hunt is None:
                waiting_hunt += 1
                sleep(1)
                if waiting_hunt == 90:
                    self.append_text.emit(f"{dt.now().strftime(self.current_time)} Didn't see Hunt button, refresh..")
                    return self.refresh_and_connect(), self.go_hunt_function()
                continue
            break
        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Go Hunt')
        waiting_hunt = 0
        while True:
            pag.click(go_hunt[0] + randint(-40, 40), go_hunt[1] + randint(-100, 100))
            sleep(1)
            go_hunt = pag.locateCenterOnScreen('targets/Go hunt.png', confidence=0.95)
            if go_hunt is None:
                break
            waiting_hunt += 1
            if waiting_hunt == 30:
                return self.refresh_and_connect(), self.go_hunt_function()

    def clicks_to_work(self):
        start_time = time()
        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Loading..')
        while True:
            if time() - start_time > 120:
                return self.refresh_and_connect(), self.go_to_heroes(), self.clicks_to_work()
            home_button = pag.locateCenterOnScreen('targets/Home button.png', confidence=0.95)
            if home_button is not None:
                break
            sleep(1)
        self.scroll()
        sleep(1)
        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Clicking..')
        while True:
            work_button = pag.locateCenterOnScreen('targets/Work button.png', confidence=0.96)
            if work_button is not None:
                if time() - start_time > 120:
                    pag.screenshot('ERROR IN HEROES.png')
                    return self.refresh_and_connect(), self.go_to_heroes(), self.clicks_to_work()
                pag.click(work_button[0] + randint(-15, 15), work_button[1] + randint(-10, 10))
                sleep(1)
                continue
            if time() - start_time > 120:
                pag.screenshot('ERROR IN HEROES.png')
                return self.refresh_and_connect(), self.go_to_heroes(), self.clicks_to_work()
            sleep(2)
            work_button = pag.locateCenterOnScreen('targets/Work button.png', confidence=0.96)
            if work_button is None:
                home_button = pag.locateCenterOnScreen('targets/Home button.png', confidence=0.95)
                if home_button is not None:
                    self.append_text.emit(f'{dt.now().strftime(self.current_time)} All Heroes is working!')
                    break

    def scroll(self):
        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Scrolling')
        for i in range(2):
            character = pag.locateCenterOnScreen('targets/Character.png', confidence=0.95)
            x, y = character
            pag.moveTo(x + randint(-100, 100), y + randint(365, 395))
            pag.dragTo(x + randint(-150, 150), y - randint(150, 180), 0.5, button='left')
            sleep(1)

    def exit_from_heroes(self):
        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Go to main menu..')
        quit_from_heroes = pag.locateCenterOnScreen('targets/Quit from heroes.png', confidence=0.9)
        if quit_from_heroes is None:
            self.append_text.emit('Something went wrong, refreshing..')
            return self.refresh_and_connect(), self.go_hunt_function()
        while True:
            pag.click(quit_from_heroes[0] + randint(-10, 10), quit_from_heroes[1] + randint(-10, 10))
            sleep(1)
            quit_from_heroes = pag.locateCenterOnScreen('targets/Quit from heroes.png', confidence=0.9)
            if quit_from_heroes is None:
                break

    def back_from_map(self):
        counter_back_from_map = 0
        back_from_map = pag.locateCenterOnScreen('targets/Back from map.png', confidence=0.95)
        if back_from_map is None:
            self.append_text.emit('Something went wrong, refreshing..')
            pag.screenshot('BACK FROM MAP ERROR.png')
            return self.refresh_and_connect(), self.go_hunt_function()
        self.append_text.emit(f'{dt.now().strftime(self.current_time)} Exit from map')
        while True:
            pag.click(back_from_map[0] + randint(-20, 20), back_from_map[1] + randint(-15, 15))
            sleep(1)
            back_from_map = pag.locateCenterOnScreen('targets/Back from map.png', confidence=0.95)
            if back_from_map is None:
                self.go_hunt_function()
                break
            counter_back_from_map += 1
            if counter_back_from_map == 30:
                return self.refresh_and_connect(), self.go_hunt_function()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(0, 0, 600, 500)
        self.setWindowTitle('Clicker')
        font = QtGui.QFont()
        font.setPointSize(15)
        self.re_enter_map = QtWidgets.QLineEdit(self)
        self.re_enter_map.setText('3')
        self.re_enter_map.setGeometry(500, 10, 40, 40)
        self.re_enter_map.setFont(font)
        self.refresh_time = QtWidgets.QLineEdit(self)
        self.refresh_time.setText('55')
        self.refresh_time.setGeometry(120, 10, 40, 40)
        self.refresh_time.setFont(font)
        self.start_button = QtWidgets.QPushButton(self)
        self.start_button.setText('Start')
        self.start_button.setFont(font)
        self.start_button.setGeometry(180, 10, 100, 40)

        font = QtGui.QFont()
        font.setPointSize(11)
        self.autograph = QtWidgets.QLabel(self)
        self.autograph.setGeometry(450, 450, 150, 40)
        self.autograph.setText('1B-NHNPRO')
        self.autograph.setFont(font)
        self.status = QtWidgets.QPlainTextEdit(self)
        self.status.setGeometry(10, 60, 580, 380)
        self.status.setReadOnly(True)
        self.status.setFont(font)

        font = QtGui.QFont()
        font.setPointSize(12)
        self.refresh_label = QtWidgets.QLabel(self)
        self.refresh_label.setText('Refresh in')
        self.refresh_label.setGeometry(5, 5, 100, 50)
        self.refresh_label.setFont(font)
        self.re_map_label = QtWidgets.QLabel(self)
        self.re_map_label.setText('ReMap in')
        self.re_map_label.setFont(font)
        self.re_map_label.setGeometry(400, 5, 100, 50)


        self.start_button.clicked.connect(self.function)

    def function(self):
        if self.start_button.text() == 'Start':
            self.start_button.setText('Stop')
            self.start_button.setStyleSheet('background-color: rgb(255, 69, 32)')
            self.worker = Clicker(self.refresh_time.text(), self.re_enter_map.text())
            self.worker.append_text.connect(lambda x: self.status.appendPlainText(x))
            self.worker.set_text.connect(lambda x: self.status.setPlainText(x))
            self.worker.start()
        else:
            self.start_button.setText('Start')
            self.start_button.setStyleSheet('background-color: light gray')
            self.worker.terminate()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
