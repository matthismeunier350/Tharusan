import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('mini_jeux_2')

#define le font
font = pygame.font.SysFont('Bauhaus 93', 60)

#defini les couleur 
white = (255, 255, 255)

#definition des variable de la game 
ground = 0
scroll_speed = 4
flying = False
game_over = False
mur_gap = 150
frequency = 1500 #millisecondes
last = pygame.time.get_ticks() - frequency
score = 0
pass_mur = False


# telecharge les images
bg = pygame.image.load('img/bg.jpg')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')


# fontion qui creer le texte sur le jeu 
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def reset():
	mur_group.empty()
	flappy.rect.x = 100
	flappy.rect.y = int(screen_height / 2)
	score = 0
	return score


class Oiseau(pygame.sprite.Sprite):

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = [] # liste pour mettre les images 
		self.index = 0
		self.counter = 0
		for num in range (1, 4):
			img = pygame.image.load(f"img/bird{num}.png")
			self.images.append(img) # met toute les image dans une liste 
		self.image = self.images[self.index]# creation d'une indextion des images selon leur ordre 
		self.rect = self.image.get_rect()# cree un rectangle autour des images 
		self.rect.center = [x, y]# coordonne du centre du rectangle 
		self.vel = 0
		self.clicked = False # variable appui

	def update(self):

		if flying == True: # fonction si vole est vrai 
			#gravity 
			self.vel += 0.5
			if self.vel > 8:
				self.vel = 8
			if self.rect.bottom < 768:
				self.rect.y += int(self.vel)

		if game_over == False: # si le joueur n'est pas mort
			#sauter 
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: # le saut est possible si 
				self.clicked = True
				self.vel = -10 # monte de dix
			if pygame.mouse.get_pressed()[0] == 0:
				self.clicked = False

			#animation 
			flap_cooldown = 5
			self.counter += 1
			
			if self.counter > flap_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images):
					self.index = 0
				self.image = self.images[self.index]


			#faire pivoter l’oiseau
			self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
		else:
			#fait tomber l'oiseau vers le sol 
			self.image = pygame.transform.rotate(self.images[self.index], -90)



class Mur(pygame.sprite.Sprite): # mur avec lequel il entre en collsion 

	def __init__(self, x, y, position):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/pipe.png")
		self.rect = self.image.get_rect()
		#La variable position détermine si le tuyau provient du bas ou du haut
		#la position 1 vient du haut, -1 vient du bas

		if position == 1:
			self.image = pygame.transform.flip(self.image, False, True)
			self.rect.bottomleft = [x, y - int(mur_gap / 2)]
		elif position == -1:
			self.rect.topleft = [x, y + int(mur_gap / 2)]


	def update(self):
		self.rect.x -= scroll_speed
		if self.rect.right < 0:
			self.kill()



class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

	def draw(self):
		action = False

		#prend la position de la souris
		position_souri = pygame.mouse.get_pos()

		#vérifier les conditions de la souris et de cliquer
		if self.rect.collidepoint(position_souri):
			if pygame.mouse.get_pressed()[0] == 1:
				action = True

		#dessine le bouton
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action



mur_group = pygame.sprite.Group()
oiseau_group = pygame.sprite.Group()

flappy = Oiseau(100, int(screen_height / 2))

oiseau_group.add(flappy)

# creer les bouton
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)


run = True
while run:

	clock.tick(fps)

	#dessine le font
	screen.blit(bg, (0,0))

	mur_group.draw(screen)
	oiseau_group.draw(screen)
	oiseau_group.update()

	#dessiner et deplacmeynt le font
	screen.blit(ground_img, (ground, 768))

	#verifie le score
	if len(mur_group) > 0:
		if oiseau_group.sprites()[0].rect.left > mur_group.sprites()[0].rect.left\
			and oiseau_group.sprites()[0].rect.right < mur_group.sprites()[0].rect.right\
			and pass_mur == False:
			pass_mur = True
		if pass_mur == True:
			if oiseau_group.sprites()[0].rect.left > mur_group.sprites()[0].rect.right:
				score += 1
				pass_mur = False
	draw_text(str(score), font, white, int(screen_width / 2), 20)


	#regarde si il y a une collsion 
	if pygame.sprite.groupcollide(oiseau_group, mur_group, False, False) or flappy.rect.top < 0:
		game_over = True
	
	if flappy.rect.bottom >= 768:
		game_over = True
		flying = False


	if flying == True and game_over == False:
		#genere les obstacle 
		temps = pygame.time.get_ticks()
		if temps - last > frequency:
			pipe_height = random.randint(-100, 100)
			btm_mur = Mur(screen_width, int(screen_height / 2) + pipe_height, -1)
			top_mur = Mur(screen_width, int(screen_height / 2) + pipe_height, 1)
			mur_group.add(btm_mur)
			mur_group.add(top_mur)
			last= temps

		mur_group.update()

		ground -= scroll_speed
		if abs(ground) > 35:
			ground= 0
	

	#veridie si il est mort et reset le jeu 
	if game_over == True:
		if button.draw():
			game_over = False 
			score = reset()


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
			flying = True

	pygame.display.update()

pygame.quit()
