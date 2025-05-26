from pygame import *

win_width = 1000
win_height = 700

img_back1 = "images/Castle.jpg"
img_hero = "images/Potter.png"
img_enemy = "images/dark_lord.png"

display.set_caption("Hogwarts Combat")
window = display.set_mode((win_width, win_height))
background1 = transform.scale(image.load(img_back1), (win_width, win_height))

run = True

font.init()
font_health = font.Font("alagard-12px-unicode.ttf", 40)

mixer.init()
mixer.music.load("sounds/fon.wav")
mixer.music.play(-1)
melee_attack_sound = mixer.Sound("sounds/udar.wav")
ranged_attack_sound = mixer.Sound("sounds/bullet.wav")

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
    def __init__(self, image, x, y, size_x, size_y, speed, left_key, right_key,
                 melee_attack_key, ranged_attack_key, melee_attack_color, ranged_attack_color,
                 hp, power):
        super().__init__(image, x, y, size_x, size_y, speed)
        self.left_key = left_key
        self.right_key = right_key
        self.melee_attack_key = melee_attack_key
        self.ranged_attack_key = ranged_attack_key
        self.melee_attack_color = melee_attack_color
        self.ranged_attack_color = ranged_attack_color
        self.hp = hp
        self.power = power
        self.last_ranged_attack_time = 0
        self._ranged_cooldown = 500

        self.is_dead = False
        self.death_angle = 0
        self.fall_speed = 5

    @property
    def can_ranged_attack(self):
        return time.get_ticks() - self.last_ranged_attack_time >= self._ranged_cooldown

    def update(self, keys, *args, **kwargs):
        if self.is_dead:
            self.die()
            return
        if keys[self.left_key]:
            self.rect.x -= self.speed
        if keys[self.right_key]:
            self.rect.x += self.speed

    def _attack(self, other, attack_key, dist, power, color,sound):
        sound.play()
        if self.rect.centerx < other.rect.centerx:
            direction = 1
            start_x = self.rect.right
        else:
            direction = -1
            start_x = self.rect.left - 40

        spell = MagicSpell(start_x, self.rect.centery, direction, power, dist, color)
        spell_group.add(spell)
        self.last_ranged_attack_time = time.get_ticks()

    def melee_attack(self, other):
        self._attack(other, self.melee_attack_key, 100, self.power * 2, self.melee_attack_color,melee_attack_sound)


    def ranged_attack(self, other):
        self._attack(other, self.ranged_attack_key, 200, self.power, self.ranged_attack_color,ranged_attack_sound)

    def die(self):
        if self.death_angle < 90:  # обертання до 90 градусів
            self.death_angle += 5
            rotated_image = transform.rotate(self.image, self.death_angle)
            rotated_rect = rotated_image.get_rect(center=self.rect.center)
            window.blit(rotated_image, rotated_rect.topleft)
            self.rect.y += self.fall_speed
        else:
            # Після повного обертання — заморожуємо
            window.blit(transform.rotate(self.image, 90), self.rect.topleft)
            global finish
            finish = True

    def reset(self):
        if not self.is_dead:
            super().reset()


class MagicSpell(sprite.Sprite):
    def __init__(self, x, y, direction, power, dist, color=(0, 200, 255)):
        super().__init__()
        self.image = Surface((40, 10))
        self.image.fill(color)  # використовуй переданий колір
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.start_x = x  # зберігаємо стартову позицію
        self.speed = 10 * direction
        self.power = power
        self.direction = direction
        self.dist = dist  # радіус дії

    def update(self):
        self.rect.x += self.speed
        # Якщо вийшла за межі екрану або перевищила радіус дії
        if abs(self.rect.x - self.start_x) > self.dist or self.rect.right < 0 or self.rect.left > win_width:
            self.kill()

def start():
    global harry,lord,spell_group,finish
    harry = Player(img_hero, 100, 450, 100, 200, 10, K_a, K_d, K_SPACE, K_LSHIFT, (0, 247, 255), (107, 255, 206), 100, 5)  # TODO: додати кольори магії
    lord = Player(img_enemy, win_width-200, 450, 100, 200, 10, K_LEFT, K_RIGHT, K_RCTRL, K_RSHIFT, (255, 26, 72), (110, 67, 252), 100, 10)  # TODO: додати кольори магії
    spell_group = sprite.Group()
    finish = False
start()

while run:
    events = event.get()
    for e in events:
        if e.type == QUIT:
            run = False
        if e.type == KEYDOWN:
            if e.key == harry.melee_attack_key:
                harry.melee_attack(lord)
            if e.key == harry.ranged_attack_key:
                harry.ranged_attack(lord)
            if e.key == lord.melee_attack_key:
                lord.melee_attack(harry)
            if e.key == lord.ranged_attack_key:
                lord.ranged_attack(harry)
            if e.key == K_r:
                start()
    if not finish:
        keys = key.get_pressed()
        window.blit(background1, (0, 0))
        harry.update(keys)
        harry.reset()
        lord.update(keys)
        lord.reset()

        spell_group.update()
        spell_group.draw(window)

        for spell in spell_group:
            if spell.rect.colliderect(harry.rect):  # TODO: прибрати напрямок
                harry.hp -= spell.power
                spell.kill()
            elif spell.rect.colliderect(lord.rect):  # TODO: прибрати напрямок
                lord.hp -= spell.power
                spell.kill()

        text_health1 = font_health.render(f"Здоров'я:{harry.hp}", 1, (255, 255, 255))
        window.blit(text_health1, (0, 0))
        text_health2 = font_health.render(f"Здоров'я:{lord.hp}", 1, (255, 255, 255))
        window.blit(text_health2, (win_width - 250, 0))

        if harry.hp <= 0:
            harry.is_dead = True

            final_text = font_health.render("Гаррі Поттер помер😫",True,(255,0,0))
            window.blit(final_text,((win_width - final_text.get_rect().width) // 2, win_height // 2 - 50))
        if lord.hp <= 0:
            lord.is_dead = True

            final_text = font_health.render("Цей час настав!", True, (255, 0, 0))
            window.blit(final_text, ((win_width - final_text.get_rect().width) // 2, win_height // 2 - 50))


    display.update()
    time.delay(50)
