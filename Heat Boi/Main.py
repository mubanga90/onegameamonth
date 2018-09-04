from scene import *
from threading import Timer
import random
import sound
import atexit
A = Action
s = 4
ground = 0

music = sound.Player('Reggea.wav')
music.number_of_loops = -1
music.play()

run_textures = []
for i in range(0, 8):
	run_textures.append(
		Texture('run/' + str(i) + '.png'))

jump_textures = []
for i in range(0, 8):
	jump_textures.append(
		Texture('jump/' + str(i) + '.png'))

fall_textures = []
for i in range(0, 8):
	fall_textures.append(
		Texture('fall/' + str(i) + '.png'))
		
bunny_textures = []
for i in range(0, 10):
	bunny_textures.append(
		Texture('bun/' + str(i) + '.png'))

class background(SpriteNode):
	def __init__(self, **kwargs):
		SpriteNode.__init__(self, 'bg/' + str(random.randint(0,4)) + '.png', **kwargs)
		self.z_position = -10

class bunny(SpriteNode):
	def __init__(self, **kwargs):
		self.step = 0
		self.burning = False
		self.done = False
		SpriteNode.__init__(self, 'bun/' + str(self.step) + '.png', **kwargs)

class Game (Scene):
	def setup(self):
		self.game_started = False
		self.game_ended = False
		self.background_color = '#ccf8ff'
		
		self.player = SpriteNode(run_textures[0])
		self.player.scale = 0.3
		self.player.anchor_point = (0.5, 0)
		self.player.position = (self.size.w/3, ground)
		self.add_child(self.player)
		
		self.screen = SpriteNode('start.png')
		self.screen.z_position = 100
		self.screen.scale = 0.58
		self.screen.position = (self.size.w/2, 206)
		self.add_child(self.screen)
		
		self.end_screen = SpriteNode('end.png')
		self.end_screen.z_position = 100
		self.end_screen.scale = 0.58
		self.end_screen.position = (self.size.w/2, 206)
		self.add_child(self.end_screen)
		
		score_font = ('Futura', 40)
		self.score_label = LabelNode('', score_font, parent=self)
		self.score_label.position = (self.size.w/2, self.size.h/2 - 50)
		self.score_label.z_position = 101
		
		self.start_screen()
		self.start_background()
		
		
	def update(self):
		if self.game_started:
			self.jump()
			self.player.position = (self.size.w/3, self.playerY)
			self.animation_stuff()
				
			if random.random() < 0.01:
				self.spawnBunny()
			self.checkCollision()
	
	def animation_stuff(self):
		if self.frames >= 3:
			if self.jumping:
				if self.jumpSpeed >= 0:
					self.player.texture = jump_textures[self.step]
				else:
					self.player.texture = fall_textures[self.step]
			else:
				self.player.texture = run_textures[self.step]
				
			if self.step < 7:
				self.step += 1
				if not self.jumping and self.step % 3 is 0:
					sound.play_effect('rpg:Footstep04', 0.4, 1.0 + 0.5 * self.step)
				for bun in self.bunnies:
					if bun.burning and bun.step < 9:
						bun.step += 1
						bun.texture = bunny_textures[bun.step]
			else:
				self.step = 0
			self.frames = 0
		else:
			self.frames += 1
	
	def touch_began(self, touch):
		if self.game_started:
			if not self.jumping:
				self.jumping = True
				self.boosting = True
				self.jumpSpeed = 14
				sound.play_effect('rpg:Footstep05', 0.5)
		elif not self.game_started and not self.game_ended:
			self.start_game()
		else:
			self.start_screen()
	
	def touch_ended(self, touch):
		self.end_boost()
	
	def end_boost(self):
		self.boosting = False
		self.jumpBoost = 0
	
	def jump(self):
		if self.boosting:
			if self.jumpBoost < 11:
				self.jumpSpeed += 1
				self.jumpBoost += 1
			else:
				self.end_boost()
		if self.jumping:
			self.playerY += self.jumpSpeed
			if self.playerY < ground:
				self.jumping = False
				self.playerY = ground
			self.jumpSpeed -= 1
	
	def spawnBunny(self):
		bun = bunny(parent=self)
		bun.scale = 0.4
		bun.position = (self.size.x * 2, 48)
		actions = [A.move_by(-self.size.x * 4, 0, s * 2), A.remove()]
		bun.run_action(A.sequence(actions))
		self.bunnies.append(bun)
				
	def start_background(self):
		bg = background(parent=self)
		bg.scale = 0.57
		bg.position = (40, 205)
		actions = [A.move_by(-self.size.x * 4, 0, s * 2), A.remove()]
		bg.run_action(A.sequence(actions))
		
		bg = background(parent=self)
		bg.scale = 0.57
		bg.position = (self.size.x + 20, 205)
		actions = [A.move_by(-self.size.x * 4, 0, s * 2), A.remove()]
		bg.run_action(A.sequence(actions))
		
		self.runBackground()
	
	def runBackground(self):
		bg = background(parent=self)
		bg.scale = 0.57
		bg.position = (self.size.x * 2, 205)
		actions = [A.move_by(-self.size.x * 4, 0, s * 2), A.remove()]
		bg.run_action(A.sequence(actions))
		Timer(s * 0.45 , self.runBackground).start()
	
	def checkCollision(self):
		for bun in self.bunnies:
			dist = abs(self.player.position - bun.position + (10, 40))
			if dist < 30 and not bun.burning:
				bun.burning = True
				sound.play_effect('rpg:HandleSmallLeather2', 1)
			if bun.position.x < 0 and not bun.done:
				bun.done = True
				if bun.burning:
					self.bunnies_burned += 1
				else:
					self.bunnies_jumped += 1
				
				print('bunnies jumped: ' + str(self.bunnies_jumped) + ', bunnies burnes: ' + str(self.bunnies_burned))
	
	def start_screen(self):
		self.screen.alpha = 1
		self.end_screen.alpha = 0
		self.score_label.text = ''
		self.game_ended = False
		
		
	def start_game(self):
		self.screen.alpha = 0
		self.step = 0
		self.frames = 0
		self.playerY = ground
		self.jumpSpeed = 16
		self.jumpBoost = 0
		self.boosting = False
		self.jumping = False
		self.bunnies = []
		self.spawnBunny()
		self.bunnies_jumped = 0
		self.bunnies_burned = 0
		self.game_started = True
		Timer(30, self.show_end_screen).start()
		
	def show_end_screen(self):
		self.game_ended = True
		self.game_started = False
		self.end_screen.alpha = 1
		self.screen.alpha = 0
		self.score_label.text = 'You jumped over ' + str(self.bunnies_jumped) + ' bunnies \n and burned ' + str(self.bunnies_burned) + ' bunnies!'

def exit_handler():
	music.stop()
	print('bye')

atexit.register(exit_handler)

if __name__ == '__main__':
	run(Game(), LANDSCAPE, show_fps = True)
