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
from kivy.lang import Builder

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

		self.correct_sound = SoundLoader.load('correct.ogg')
		self.wrong_sound = SoundLoader.load('wrong.ogg')
		self.main_sound = SoundLoader.load('main.ogg')
		self.main_sound.volume = 0.7
		self.main_sound.loop = True
	
	diff = ObjectProperty('baby')
	time = ObjectProperty('60')
	example = ObjectProperty('')
	anwser = ObjectProperty('')
	started = True

	true_false = ObjectProperty((.2, .2, .2))

	real_anwser = None
	best_record = ObjectProperty('0')

	main_sound = None
	wrong_sound = None
	correct_sound = None

	actions = ['-','+','*','/']

	pos_gotov = ObjectProperty({'center_x': .5, 'center_y': .05})
	pos_otvet = ObjectProperty({'center_x': 2, 'center_y': .05})

	pos_plus25 = ObjectProperty(({"center_x": -2,"center_y":.95}))
	pos_minus15 = ObjectProperty(({"center_x": -2,"center_y":.95}))
	score = ObjectProperty("0")

	pbmax = ObjectProperty(0)
	pbvalue = ObjectProperty(0)

	level = ObjectProperty('0')


	def minus15getback(self, *args):
		self.pos_minus15 = ({"center_x": -2,"center_y":.95})
		cozy = Animation(opacity=1, duration=0.1)
		cozy.start(self.ids.minus)

	def minus15_ini(self, status, *args):
		if status:
			self.pos_minus15 = ({"center_x": .68,"center_y":.95})
			cozy = Animation(opacity=0, duration=1)
			cozy.start(self.ids.minus)
			Clock.schedule_once(self.minus15getback, 1)

	def plus25getback(self, *args):
		self.pos_plus25 = ({"center_x": -2,"center_y":.95})
		cozy = Animation(opacity=1, duration=0.1)
		cozy.start(self.ids.plus)

	def plus25_ini(self, status, *args):
		if status:
			self.pos_plus25 = ({"center_x": .68,"center_y":.95})
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
		self.pbvalue += 1

		if self.pbvalue == int(self.score):
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

	def color(self, on):
		if on:
			Clock.schedule_once(self.color_red_up, 0.0001)
		else:
			Clock.schedule_once(self.color_green_up, 0.0001)

	def check_anwser(self):
		if self.anwser == '' or self.anwser == '-':
			return

		if int(self.real_anwser) != int(self.anwser):
			self.wrong_sound.play()
			try:
				self.time = str(int(self.time)-15)
			except:
				return
			self.anwser = ''
			self.color(True)
			self.minus15_ini(True)
		else:
			self.correct_sound.play()
			self.time = str(int(self.time)+25)
			self.ini_pb(self)
			if int(self.time) > int(self.score):
				self.score = self.time
			if int(self.score) > int(self.best_record):
				self.best_record = self.score

			self.anwser = ''
			self.color(False)
			self.plus25_ini(True)
			return self.generate_question()

	def generate_question(self):
		if self.diff == 'baby':
			first = randint(1,99)
			second = randint(1,99)
			action = self.actions[randint(0,1)]

		elif self.diff == 'baby2':
			action = self.actions[randint(0,2)]

			if action == '*':
				first = randint(1,10)
				second = randint(1,99)
			else:
				first = randint(-99,99)
				second = randint(-99,99)

		elif self.diff == 'baby3':
			action = self.actions[randint(0,2)]

			if action == '*':
				first = randint(1,99)
				second = randint(1,99)
			else:
				first = randint(-999,999)
				second = randint(-999,999)

		elif self.diff == 'pro':
			first = randint(1,99)
			second = randint(1,99)
			action = '*'
		elif self.diff == 'legendary':
			first = randint(1,999)
			second = randint(1,999)
			action = self.actions[randint(0,3)]


		self.example = '{}{}{}'.format(first, action, second)



		if action == '-':
			anwser = first-second
		elif action == '+':
			anwser = first+second
		elif action == '*':
			anwser = first*second
		elif action == '/':
			anwser = first/second

		self.real_anwser = str(anwser)



	def move_gui(self, status):
		if status:
			self.animation = Animation(pos_hint=({"center_x": -1,"center_y": .05}), duration=0.25)
			self.animation.start(self.ids.gotov)

			self.animation = Animation(pos_hint=({'center_x': .5, 'center_y': .05}), duration=0.25)
			self.animation.start(self.ids.otvet)
		else:
			self.animation = Animation(pos_hint=({"center_x": .5,"center_y": .05}), duration=0.25)
			self.animation.start(self.ids.gotov)

			self.animation = Animation(pos_hint=({'center_x': -2, 'center_y': .05}), duration=0.25)
			self.animation.start(self.ids.otvet)



	def input(self, what):
		if what == 'CLS':
			self.anwser = ''
		elif what == '-':
			self.anwser = '-' + self.anwser
		else:
			self.anwser = self.anwser + what

	def clock_down(self, *args):
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
			self.time = 'LOSER'
			self.main_sound.stop()
			Clock.schedule_once(self.reset, 2)

	def reset(self, *args):
		self.diff = 'baby'
		self.time = '60'
		self.example = ''
		self.anwser = ''
		self.started = True

		self.real_anwser = None

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


Builder.load_string("""
#:import NoTransition kivy.uix.screenmanager.NoTransition


<ScreenManagerz>:
	transition: NoTransition()
	id: mana

	Screen:
		name: 'menu'
		FloatLayout:
			canvas:
				Color: 
					rgb: .9, .2, .2
				Rectangle:
					source: 'back.png'
					size: self.size
					pos: self.pos

			Label:
				text: 'YOU COUNT!'
				halign: 'center'
				valign: "middle"
				text_size: self.size
				size_hint: ( 1, .15)
				font_size: sp(60)
				pos_hint:{"center_x": .5,"center_y":.92}

			Label:
				text: root.best_record
				halign: 'center'
				valign: "middle"
				text_size: self.size
				size_hint: ( 1, .15)
				font_size: sp(60)
				pos_hint:{"center_x": .2,"center_y":.54}

			Label:
				text: 'Лучший счет:'
				halign: 'center'
				valign: "middle"
				text_size: self.size
				size_hint: ( 1, .15)
				font_size: sp(20)
				pos_hint:{"center_x": .2,"center_y":.6}

			Button:
				pos_hint: {'center_x': .5, 'center_y': .2}
				border: 0,0,0,0
				size_hint: (.4, .15)
				background_normal: 'geek.jpg'
				on_press: root.leggo()


			Label:
				text: 'ЖМИ НА БОТАНА ЧТОБЫ НАЧАТЬ'
				halign: 'center'
				valign: "middle"
				text_size: self.size
				size_hint: ( 1, .15)
				font_size: sp(25)
				pos_hint:{"center_x": .5,"center_y":.1}

	Screen:
		name: 'count'
		FloatLayout:
			canvas:
				Color: 
					rgb: .2, .2, .2
				Rectangle:
					source: 'back.png'
					size: self.size
					pos: self.pos

			Label:
				canvas.before:
					Color: 
						rgb: .7, .2, .2
					Rectangle:
						source: 'back.png'
						size: self.size
						pos: self.pos
				font_size: sp(50)
				text: root.example
				size_hint: ( 1, .15)
				pos_hint:{"center_x": .5,"center_y":.8}

			Label:
				canvas.before: 
					Color: 
						rgb: root.true_false
					Rectangle: 
						pos: self.pos 
						size: self.size

				text: root.time
				halign: 'center'
				valign: "middle"
				text_size: self.size
				size_hint: ( 1, .15)
				font_size: sp(40)
				pos_hint:{"center_x": .5,"center_y":.95}

			Label:
				canvas.before:
					Color: 
						rgb: .4, .2, .5
					Rectangle:
						source: 'back.png'
						size: self.size
						pos: self.pos
				text: root.anwser
				size_hint: ( 1, .15)
				font_size: sp(50)
				pos_hint:{"center_x": .5,"center_y":.6}

			Label:
				id: plus
				text: '[color=00ff56]+25[/color]'
				halign: 'center'
				valign: "middle"
				text_size: self.size
				size_hint: ( .2, .1)
				font_size: sp(40)
				pos_hint: root.pos_plus25
				markup: True

			Label:
				text: root.score
				halign: 'center'
				valign: "middle"
				text_size: self.size
				size_hint: ( 1, .15)
				font_size: sp(40)
				pos_hint:{"center_x": .1,"center_y":.95}

			Label:
				text: root.level
				halign: 'center'
				valign: "middle"
				text_size: self.size
				size_hint: ( 1, .15)
				font_size: sp(40)
				pos_hint:{"center_x": .9,"center_y":.95}

			Label:
				text: 'score'
				halign: 'center'
				valign: "middle"
				text_size: self.size
				size_hint: ( 1, .15)
				font_size: sp(30)
				pos_hint:{"center_x": .1,"center_y":.9}

			Label:
				text: 'level'
				halign: 'center'
				valign: "middle"
				text_size: self.size
				size_hint: ( 1, .15)
				font_size: sp(30)
				pos_hint:{"center_x": .9,"center_y":.9}

			Label:
				id: minus
				text: '[color=ff3333]-15[/color]'
				halign: 'center'
				valign: "middle"
				text_size: self.size
				size_hint: ( .2, .1)
				font_size: sp(40)
				pos_hint: root.pos_minus15
				markup: True

			Button:
				id: gotov
				pos_hint: root.pos_gotov
				text: 'Я готов!!!'
				size_hint: (.7, .05)
				on_press: root.ini_pb()
				on_press: root.generate_question()
				on_press: root.move_gui('True')
				on_press: root.start()

			Button:
				id: otvet
				pos_hint: root.pos_otvet
				text: 'Ответ'
				size_hint: (.9, .09)
				on_press: root.check_anwser()

			ProgressBar:
				max: root.pbmax
				value: root.pbvalue
				size_hint: (.7, .05)
				pos_hint:{"center_x": .5,"center_y":.7}
			

			GridLayout:
				cols: 3
				size_hint_y: .4
				size_hint_x: .8
				pos_hint: {'center_x': .5, 'center_y': .3}
				canvas.before: 
					Color: 
						rgb: 0, .8, 0 
					Rectangle: 
						pos: self.pos 
						size: self.size
				Button:
					text: "1"
					font_size: sp(35)
					on_press: root.input('1')

				Button:
					text: "2"
					font_size: sp(35)
					on_press: root.input('2')
				Button:
					text: "3"
					font_size: sp(35)
					on_press: root.input('3')
				Button:
					text: "4"
					font_size: sp(35)
					on_press: root.input('4')
				Button:
					text: "5"
					font_size: sp(35)
					on_press: root.input('5')
				Button:
					text: "6"
					font_size: sp(35)
					on_press: root.input('6')
				Button:
					text: "7"
					font_size: sp(35)
					on_press: root.input('7')
				Button:
					text: "8"
					font_size: sp(35)
					on_press: root.input('8')
				Button:
					text: "9"
					font_size: sp(35)
					on_press: root.input('9')
				Button:
					text: "CLS"
					font_size: sp(35)
					on_press: root.input('CLS')
				Button:
					text: "0"
					font_size: sp(35)
					on_press: root.input('0')
				Button:
					text: "-"
					font_size: sp(35)
					on_press: root.input('-')


	""")



if __name__ == "__main__":
	YouCount().run()
