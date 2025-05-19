
from pygame import*

win_width = 1000
win_height = 700

img_back1 = "images/Castle.jpg"
img_hero = "images/Potter.png"
img_enemy = "images/dark_lord.png"

display.set_caption("Hogwarts Combat")
window = display.set_mode((win_width,win_height))
background1 = transform.scale(image.load(img_back1),(win_width,win_height))

run = True

font.init()
font_health = font.Font("alagard-12px-unicode.ttf",40)

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, x, y, size_x, size_y, speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, image, x, y, size_x, size_y, speed,left_key,right_key,melee_attack_key,ranged_attack_key,hp,power):
        super().__init__(image, x, y, size_x, size_y, speed)
        self.left_key = left_key
        self.right_key = right_key
        self.melee_attack_key = melee_attack_key
        self.ranged_attack_key = ranged_attack_key
        self.hp = hp
        self.power = power

    def update(self, keys,*args, **kwargs):
        if keys[self.left_key]:
            self.rect.x -= self.speed
        if keys[self.right_key]:
            self.rect.x += self.speed

    def _attack(self, keys, other,attack_key,dist,power):
        if keys[attack_key]:
            if abs(self.rect.centerx - other.rect.centerx) < dist:
                other.hp -= power
                print("залишок хп", other.hp)

    def melee_attack(self,keys,other):
        self._attack(keys,other,self.melee_attack_key,100,self.power*2)


    def ranged_attack(self,keys,other):
        self._attack(keys,other,self.melee_attack_key,400,self.power)



harry = Player(img_hero,100,450,100,200,10,K_a,K_d,K_SPACE,K_LSHIFT,100,5)
lord = Player(img_enemy,400,450,100,200,10,K_LEFT,K_RIGHT,K_RCTRL,K_RSHIFT,100,10)


while run :
    events = event.get()
    for e in events:
        if e.type == QUIT:
            run = False
    keys = key.get_pressed()


    window.blit(background1,(0,0))
    harry.update(keys)
    harry.reset()
    harry.melee_attack(keys,lord)
    lord.update(keys)
    lord.reset()
    lord.melee_attack(keys,harry)

    text_health1 = font_health.render(f"Здоров'я:{harry.hp}",1,(255,255,255))
    window.blit(text_health1,(0,0))
    text_health2 = font_health.render(f"Здоров'я:{lord.hp}", 1, (255, 255, 255))
    window.blit(text_health2, (win_width-250, 0))

    display.update()
    time.delay(50)
