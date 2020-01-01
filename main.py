from kivy.config import Config

Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '414')
Config.set('graphics', 'height', '736')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.label import Label
from time import strftime
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.animation import Animation
from kivy.clock import Clock
from random import randint
from kivy.core.audio import SoundLoader
from kivy.uix.progressbar import ProgressBar


class YouCount(App):
    def build(self):
        return ScreenManagerz()


class MyContent(FloatLayout):
    pass


class ScreenManagerz(ScreenManager):

    def __init__(self, *args, **kwargs):
        super(ScreenManagerz, self).__init__()

        self.sync()

        self.buzz_sound = SoundLoader.load('buzz.wav')
        self.level_up_sound = SoundLoader.load('lev.wav')
        self.correct_sound = SoundLoader.load('correct.ogg')
        self.wrong_sound = SoundLoader.load('wrong.ogg')
        self.main_sound = SoundLoader.load('main.ogg')
        self.main_sound.volume = 0.3
        self.main_sound.loop = True

    diff = ObjectProperty('baby')
    time = ObjectProperty('60')
    example = ObjectProperty('')
    anwser = ObjectProperty('')
    started = True
    minus_text = ObjectProperty('[color=ff3333]-10[/color]')

    true_false = ObjectProperty((.2, .2, .2))

    real_anwser = None
    best_record = ObjectProperty('0')

    main_sound = None
    wrong_sound = None
    correct_sound = None

    actions = ['-', '+', '*', '/']

    pos_gotov = ObjectProperty({'center_x': .5, 'center_y': .05})
    pos_otvet = ObjectProperty({'center_x': 2, 'center_y': .05})

    pos_skip = ObjectProperty({'center_x': -2, 'center_y': .5})
    pos_give_up = ObjectProperty({'center_x': 2, 'center_y': .5})

    pos_plus25 = ObjectProperty(({"center_x": -2, "center_y": .95}))
    pos_minus15 = ObjectProperty(({"center_x": -2, "center_y": .95}))
    score = ObjectProperty("0")

    pos_heart_gray_one = ObjectProperty({"center_x": -2,"center_y":.9})
    pos_heart_gray_two = ObjectProperty({"center_x": -2,"center_y":.9})
    pos_heart_gray_three = ObjectProperty({"center_x": -2,"center_y":.9})
    heart_counter = ObjectProperty(3)


    pbmax = ObjectProperty(0)
    pbvalue = ObjectProperty(0)

    level = ObjectProperty('0')

    last_level = None
    last_best = '0'

    def on_heart_counter(self, *args):
        if self.heart_counter == 3:
            self.pos_heart_gray_one = {"center_x": -2,"center_y":.9}
            self.pos_heart_gray_two = {"center_x": -2,"center_y":.9}
            self.pos_heart_gray_three = {"center_x": -2,"center_y":.9}
        elif self.heart_counter == 2:
            self.pos_heart_gray_one = {"center_x": -2,"center_y":.9}
            self.pos_heart_gray_two = {"center_x": -2,"center_y":.9}
            self.pos_heart_gray_three = {"center_x": .6,"center_y":.9}
        elif self.heart_counter == 1:
            self.pos_heart_gray_one = {"center_x": -2,"center_y":.9}
            self.pos_heart_gray_two = {"center_x": .5,"center_y":.9}
            self.pos_heart_gray_three = {"center_x": .6,"center_y":.9}
        elif self.heart_counter == 0:
            self.pos_heart_gray_one = {"center_x": .4,"center_y":.9}
            self.pos_heart_gray_two = {"center_x": .5,"center_y":.9}
            self.pos_heart_gray_three = {"center_x": .6,"center_y":.9}

    def sync(self):
        try:
            f = open("records.txt", "r+")
            rawread = f.read()
            f.close()
            if len(rawread) == 0:
                self.best_record = '0'
                self.last_best = '0'
            else:
                self.best_record = rawread
                self.last_best = rawread
        except:
            f = open("records.txt", "w+")
            f.close()

    def minus15getback(self, *args):
        self.pos_minus15 = ({"center_x": -2, "center_y": .95})
        cozy = Animation(opacity=1, duration=0.1)
        cozy.start(self.ids.minus)

    def minus15_ini(self, status, *args):
        if status:
            self.pos_minus15 = ({"center_x": .68, "center_y": .95})
            cozy = Animation(opacity=0, duration=1)
            cozy.start(self.ids.minus)
            Clock.schedule_once(self.minus15getback, 1)

    def plus25getback(self, *args):
        self.pos_plus25 = ({"center_x": -2, "center_y": .95})
        cozy = Animation(opacity=1, duration=0.1)
        cozy.start(self.ids.plus)

    def plus25_ini(self, status, *args):
        if status:
            self.pos_plus25 = ({"center_x": .68, "center_y": .95})
            cozy = Animation(opacity=0, duration=1)
            cozy.start(self.ids.plus)
            Clock.schedule_once(self.plus25getback, 1)

    def color_green_down(self, *args):
        to_change = self.true_false[1]

        to_change -= .1
        self.true_false = ((.2, to_change, .2))

        if self.true_false[1] <= .2:
            self.true_false = (.2, .2, .2)
            return
        else:
            Clock.schedule_once(self.color_green_down, 0.0001)

    def color_green_up(self, *args):
        to_change = self.true_false[1]

        to_change += .1
        self.true_false = ((.2, to_change, .2))

        if self.true_false[1] >= 1:
            return self.color_green_down()
        else:
            Clock.schedule_once(self.color_green_up, 0.0001)

    def color_red_down(self, *args):
        to_change = self.true_false[0]

        to_change -= .1
        self.true_false = ((to_change, .2, .2))

        if self.true_false[0] <= .2:
            return
        else:
            Clock.schedule_once(self.color_red_down, 0.0001)

    def color_red_up(self, *args):
        to_change = self.true_false[0]

        to_change += .1
        self.true_false = ((to_change, .2, .2))

        if self.true_false[0] >= 1:
            return self.color_red_down()
        else:
            Clock.schedule_once(self.color_red_up, 0.0001)

    def pb_up(self, *args):
        if int(self.time) > self.pbvalue:
            self.pbvalue += 1
        elif int(self.time) < self.pbvalue:
            self.pbvalue -= 1
        else:
            return

        if self.pbvalue == int(self.time):
            return
        else:
            Clock.schedule_once(self.pb_up, 0.0001)

    def ini_pb(self, *args):
        if int(self.score) >= 600:
            self.level = '3'
            self.pbmax = 1000
        elif int(self.score) >= 400:
            self.level = '2'
            self.pbmax = 600
        elif int(self.score) >= 250:
            self.level = '1'
            self.pbmax = 400
        elif int(self.score) >= 0:
            self.level = '0'
            self.pbmax = 250

        if self.pbvalue != int(self.score):
            Clock.schedule_once(self.pb_up, 0.0001)

    def return_level(self, *args):
        self.ids.level_verh.pos_hint = ({"center_x": -1, "center_y": .7})

    def go_away_level(self, *args):
        self.animation = Animation(pos_hint=({"center_x": 2, "center_y": .7}), duration=0.25)
        self.animation.start(self.ids.level_verh)
        Clock.schedule_once(self.return_level, 1)

    def on_level(self, *args):
        if self.level != "0":
            self.level_up_sound.play()
            self.animation = Animation(pos_hint=({"center_x": .5, "center_y": .7}), duration=0.25)
            self.animation.start(self.ids.level_verh)
            Clock.schedule_once(self.go_away_level, 2)

    def color(self, on):
        if on:
            Clock.schedule_once(self.color_red_up, 0.0001)
        else:
            Clock.schedule_once(self.color_green_up, 0.0001)

    def pre_skip_question(self):
        if self.heart_counter == 0:
            return
        else:
            self.skip_question()

    def skip_question(self):
        try:
            self.time = str(int(self.time) - 10)
            self.heart_counter -= 1
            self.ini_pb()
        except:
            return

        self.anwser = ''
        self.color(True)
        self.minus15_ini(True)

        return self.generate_question()

    def check_anwser(self):
        if self.anwser == '' or self.anwser == '-':
            return

        if int(self.real_anwser) != int(self.anwser):
            self.wrong_sound.play()
            try:
                self.time = str(int(self.time) - 10)
                self.ini_pb()
            except:
                return
            self.anwser = ''
            self.color(True)
            self.minus15_ini(True)
        else:
            self.correct_sound.play()
            self.time = str(int(self.time) + 25)
            if int(self.time) > int(self.score):
                self.score = self.time
            if int(self.score) > int(self.best_record):
                self.best_record = self.score

            self.ini_pb()

            self.anwser = ''
            self.color(False)
            self.plus25_ini(True)
            return self.generate_question()

    def generate_question(self):
        if self.diff == 'baby':
            first = randint(1, 99)
            second = randint(1, 99)
            action = self.actions[randint(0, 1)]

        elif self.diff == 'baby2':
            action = self.actions[randint(0, 2)]

            if action == '*':
                first = randint(1, 10)
                second = randint(1, 99)
            else:
                first = randint(-99, 99)
                second = randint(-99, 99)

        elif self.diff == 'baby3':
            action = self.actions[randint(0, 2)]

            if action == '*':
                first = randint(1, 99)
                second = randint(1, 99)
            else:
                first = randint(-999, 999)
                second = randint(-999, 999)

        elif self.diff == 'pro':
            first = randint(1, 99)
            second = randint(1, 99)
            action = '*'
        elif self.diff == 'legendary':
            first = randint(1, 999)
            second = randint(1, 999)
            action = self.actions[randint(0, 3)]

        self.example = '{}{}{}'.format(first, action, second)

        if action == '-':
            anwser = first - second
        elif action == '+':
            anwser = first + second
        elif action == '*':
            anwser = first * second
        elif action == '/':
            anwser = first / second

        self.real_anwser = str(anwser)

    def move_gui(self, status):
        if status:
            self.animation = Animation(pos_hint=({"center_x": -1, "center_y": .05}), duration=0.25)
            self.animation.start(self.ids.gotov)

            self.animation = Animation(pos_hint=({'center_x': .5, 'center_y': .05}), duration=0.25)
            self.animation.start(self.ids.otvet)

            #give_up_button + skip_button
            self.animation = Animation(pos_hint=({"center_x": .3,"center_y":.485}), duration=0.25)
            self.animation.start(self.ids.skip)

            self.animation = Animation(pos_hint=({'center_x': .7, 'center_y':.485}), duration=0.25)
            self.animation.start(self.ids.give_up)
        else:
            self.animation = Animation(pos_hint=({"center_x": .5, "center_y": .05}), duration=0.25)
            self.animation.start(self.ids.gotov)

            self.animation = Animation(pos_hint=({'center_x': -2, 'center_y': .05}), duration=0.25)
            self.animation.start(self.ids.otvet)

            #give_up_button + skip_button hide
            self.animation = Animation(pos_hint=({'center_x': -2, 'center_y': .5}), duration=0.25)
            self.animation.start(self.ids.skip)

            self.animation = Animation(pos_hint=({'center_x': 2, 'center_y': .5}), duration=0.25)
            self.animation.start(self.ids.give_up)


    def input(self, what):
        if what == 'CLS':
            self.anwser = ''
        elif what == '-' and '-' not in self.anwser:
            self.anwser = '-' + self.anwser
        elif what == '-' and '-' in self.anwser:
            self.anwser = self.anwser[1:]
        else:
            self.anwser = self.anwser + what

    def clock_down(self, *args):
        self.pb_up()
        if int(self.time) > 0:
            if self.started:

                if int(self.score) > 600:
                    self.diff = 'pro'
                elif int(self.score) > 400:
                    self.diff = 'baby3'
                elif int(self.score) > 250:
                    self.diff = 'baby2'
                elif int(self.score) > 0:
                    self.diff = 'baby'

                time = int(self.time)
                time -= 1
                self.time = str(time)
                Clock.schedule_once(self.clock_down, 1)
        else:
            self.buzz_sound.play()
            self.time = '0'
            self.main_sound.stop()
            Clock.schedule_once(self.reset, 2)

    def reset(self, *args):
        if int(self.best_record) > int(self.last_best):
            self.last_best = self.best_record
            save(int(self.best_record))

        self.level = "0"
        self.diff = 'baby'
        self.time = '60'
        self.example = ''
        self.anwser = ''
        self.started = True

        self.real_anwser = None
        self.heart_counter = 3

        self.score = '0'

        self.current = 'menu'

        self.move_gui(False)

    def start(self):
        self.main_sound.play()
        Clock.schedule_once(self.clock_down, 1)

    def change_diff(self, to):
        self.diff = to

    def leggo(self):
        self.current = 'count'


def save(number):
    print('I was initialized with {}'.format(number))
    f = open("records.txt", "w+")
    f.write(str(number))
    f.close()


if __name__ == "__main__":
    YouCount().run()
