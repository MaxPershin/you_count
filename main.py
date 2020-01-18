import requests
from pusher import Pusher
import pysher

import json

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

class NumberGenerator():

    def __init__(self, seed_number):
        import random as rand
        self.rand = rand
        self.rand.seed(seed_number)

    def get_number(self):
        print(self.rand.randint(1, 999))


class Engine():

    def __init__(self, name, room, cls):
        self.cls = cls
        self.user = name
        self.chatroom = room
        self.known_users = []
        self.get_keys()

    def start_engine(self):
        self.pusher = Pusher(app_id=self.PUSHER_APP_ID, key=self.PUSHER_APP_KEY, secret=self.PUSHER_APP_SECRET,
                             cluster=self.PUSHER_APP_CLUSTER)
        self.clientPusher = pysher.Pusher(self.PUSHER_APP_KEY, self.PUSHER_APP_CLUSTER)
        self.clientPusher.connection.bind('pusher:connection_established', self.connectHandler)
        self.clientPusher.connect()

    def prepare_to_game(self):
        print('READY TO PLAY', self.chatroom, self.known_users)

    def agreed_handshake(self, by_who):
        self.seed_number = randint(0, 100000)
        #send seed number!!!
        message = '$connect%{}$'.format(by_who)
        self.pusher.trigger(self.chatroom, u'newmessage', {'user': self.user, 'message': message, 'service': True})
        self.cls.start_popup.dismiss()
        self.cls.connected(self.user, by_who)

    def close_chatroom(self):
        self.clientPusher.unsubscribe('search_room')

    def connectHandler(self, data):
        self.channel = self.clientPusher.subscribe(self.chatroom)
        self.channel.bind('newmessage', self.got_message)
        # saying hi to chatroom
        message = '$im_in$'
        self.pusher.trigger(self.chatroom, u'newmessage', {'user': self.user, 'message': message, 'service': True})

    def call_player(self, button):
        message = '$i_call%{}$'.format(button.text)
        self.pusher.trigger(self.chatroom, u'newmessage', {'user': self.user, 'message': message, 'service': True})

    def i_called(self, by_who):
        self.cls.handshake_popup(by_who)

    def check_if_service(self, message):

        if message['service'] == False:
            return False

        if message['user'] == self.user:
            return True
        else:
            if message['message'] == '$im_in$' and message['user'] not in self.known_users:
                self.known_users.append(message['user'])
                other_user = message['user']
                self.cls.ids.griddy.add_widget(Button(text=other_user, on_press=lambda x: self.call_player(x)))
                message = '$im_in$'
                self.pusher.trigger(self.chatroom, u'newmessage', {'user': self.user, 'message': message, 'service': True})
                return True

            if message['message'] == '$im_in$' and message['user'] in self.known_users:
                return True

            if message['message'] == '$i_call%{}$'.format(self.user):
                self.i_called(message['user'])
                return True

            if message['message'] == '$connect%{}$'.format(self.user):
                self.cls.connected(self.user, message['user'])
                return True

            return False

    def got_message(self, message):
        message = json.loads(message)

        if not self.check_if_service(message):
            print(message)

    def send_message(self, message):
        
        try:
            self.pusher.trigger(self.chatroom, u'newmessage', {'user': self.user, 'message': message, 'service': False})
            
        except Exception as e:
            print(e)
            

    def get_keys(self):
        #with open("auth_key.json", "r") as f:
        #   keys = json.load(f)

        #self.auth_key = keys['auth_key']
        #self.url = keys['url']

        #self.PUSHER_APP_ID = keys['PUSHER_APP_ID']
        #self.PUSHER_APP_KEY = keys['PUSHER_APP_KEY']
        #self.PUSHER_APP_SECRET = keys['PUSHER_APP_SECRET']
        #self.PUSHER_APP_CLUSTER = keys['PUSHER_APP_CLUSTER']

        self.PUSHER_APP_ID = '853308'
        self.PUSHER_APP_KEY = "a7d3caa6f11e8e40b649"
        self.PUSHER_APP_SECRET = "9618775036978ef089a7"
        self.PUSHER_APP_CLUSTER = 'eu'


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
        self.records_sound = SoundLoader.load('records.ogg')
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
    score_copy = ObjectProperty("0")

    pos_heart_gray_one = ObjectProperty({"center_x": -2,"center_y":.9})
    pos_heart_gray_two = ObjectProperty({"center_x": -2,"center_y":.9})
    pos_heart_gray_three = ObjectProperty({"center_x": -2,"center_y":.9})
    heart_counter = ObjectProperty(3)


    pbmax = ObjectProperty(0)
    pbvalue = ObjectProperty(0)

    level = ObjectProperty('0')

    last_level = None
    last_best = '0'

    champs = ObjectProperty('None')

    url = 'https://chatone-39de9.firebaseio.com/records.json'
    auth_key = '45uG9hhwkc6A5EQcyxtlxGMzWlHlbzZnopejiwxK'

    def final_stage_ready(self):
        generator = NumberGenerator()
        generator.get_number()

    def heal(self, amount):
        self.ids.health.value += amount
        if self.ids.health.value > 100:
            self.ids.health.value = 100

    def got_hit(self, amount):
        self.ids.health.value -= amount
        if self.ids.health.value <= 0:
            print('DEAD')

    def connected(self, user, opponent):
        channel = '{}{}'.format(user, opponent)
        self.c.close_chatroom()
        self.c = Engine(user, channel, self)
        self.c.start_engine()
        self.current = 'duel'
        self.c.prepare_to_game()

    def dismiss_handshake_popup(self):
        self.start_popup.dismiss()

    def handshake_popup(self, by_who):
        self.layout = FloatLayout(size=(self.width, self.height))
        txt = 'Вас приглашает в игру {}'.format(by_who)
        self.lbl = Label(text=txt, font_size="20sp",
                         pos_hint={"center_x": .5, "center_y": .86})
        self.button1 = Button(text='Нет', size_hint_y=None, size_hint_x=None,
                              height=0.06 * self.height, width=0.5 * self.width, font_size="25sp",
                              pos_hint={"center_x": .5, "center_y": .42}, halign='center',
                              valign="middle", on_press=lambda x: self.dismiss_handshake_popup())
        self.button2 = Button(text='Да', size_hint_y=None, size_hint_x=None,
                              height=0.06 * self.height, width=0.5 * self.width, font_size="25sp",
                              pos_hint={"center_x": .5, "center_y": .18}, halign='center',
                              valign="middle", on_press=lambda x: self.c.agreed_handshake(by_who))

        self.layout.add_widget(self.button1)
        self.layout.add_widget(self.button2)
        self.layout.add_widget(self.lbl)

        self.start_popup = Popup(title='Manage Ean',
                                      content=self.layout,
                                      size_hint=(.8, .35))

        self.start_popup.open()

    def find_opponent(self):
        self.c = Engine(self.ids.internet_user_name.text, 'search_room', self)
        self.c.start_engine()


    def popup(self, title, text):
        popup = Popup(title=title,
                      content=Label(text=text),
                      size_hint=(0.65, 0.25))
        popup.open()

    def load_records(self):
        self.records_sound.play()
        request = requests.get(self.url + "?auth=" + self.auth_key)
        anwser = request.json()

        dicti = {k: v for k, v in sorted(anwser.items(), reverse=True, key=lambda item: int(item[1]))}

        sentence = ''
        counter = 0

        for each in dicti:
            counter += 1
            if counter > 10:
                break
            sentence += '{}. {} - {}\n'.format(counter, each, dicti[each])

        self.champs = sentence

    def send_record(self):

        request = requests.get(self.url + "?auth=" + self.auth_key)
        anwser = request.json()
                        
        min_num = min([int(anwser[each]) for each in anwser])

        if int(self.score_copy) > min_num or len(anwser) < 10:
            sent = '{' + '"{}"'.format(self.ids.user_name.text) + ': ' + '"{}"'.format(self.score_copy) + '}'
            days_of_life = json.loads(sent)
            requests.patch(url=self.url, json=days_of_life)
            self.ids.saved_label.pos_hint = {"center_x": .5,"center_y":.23}
        else:
            self.ids.cant_save_label.pos_hint = {"center_x": .5,"center_y":.23}

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

    def clean_end_pics(self):
        self.ids.end_500.pos_hint = {"center_x": -5,"center_y":.6}
        self.ids.end_400.pos_hint = {"center_x": -5,"center_y":.6}
        self.ids.end_300.pos_hint = {"center_x": -5,"center_y":.6}
        self.ids.end_200.pos_hint = {"center_x": -5,"center_y":.6}
        self.ids.user_name.text = ''
        self.ids.cant_save_label.pos_hint = {"center_x": -5,"center_y":.23}
        self.ids.saved_label.pos_hint = {"center_x": -5,"center_y":.23}

    def prepare_results(self):
        if int(self.score_copy) >= 500:
            self.ids.end_500.pos_hint = {"center_x": .5,"center_y":.6}
        elif int(self.score_copy) >= 400:
            self.ids.end_400.pos_hint = {"center_x": .5,"center_y":.6}
        elif int(self.score_copy) >= 300:
            self.ids.end_300.pos_hint = {"center_x": .5,"center_y":.6}
        else:
            self.ids.end_200.pos_hint = {"center_x": .5,"center_y":.6}

        self.current = 'results'

    def reset(self, *args):
        self.score_copy = self.score
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

        self.prepare_results()

        self.move_gui(False)

    def start(self):
        self.main_sound.play()
        Clock.schedule_once(self.clock_down, 1)

    def change_diff(self, to):
        self.diff = to

    def leggo(self):
        self.current = 'count'


def save(number):
    f = open("records.txt", "w+")
    f.write(str(number))
    f.close()


if __name__ == "__main__":
    YouCount().run()
