import pygame
from pygame import *
import os

# Ініціалізація pygame
init()
mixer.init()
mixer.music.load("sounds/fon.wav")
mixer.music.play(-1)
melee_attack_sound = mixer.Sound("sounds/udar.wav")
ranged_attack_sound = mixer.Sound("sounds/bullet.wav")

# Константи
WIN_WIDTH = 1200
WIN_HEIGHT = 800
FPS = 60
GRAVITY = 0.8
JUMP_POWER = -16

# Налаштування вікна
screen = display.set_mode((WIN_WIDTH, WIN_HEIGHT))
display.set_caption("Mortal Kombat Arena")
clock = time.Clock()

# Шрифти
font.init()
font_large = font.Font(None, 72)
font_medium = font.Font(None, 48)
font_small = font.Font(None, 32)

# Стани гри
MENU = 0
GAME = 1
SHOP = 2
GAME_OVER = 3

# Налаштування платформи
PLATFORM_WIDTH = 1300
PLATFORM_HEIGHT = 100
PLATFORM_X = (WIN_WIDTH - PLATFORM_WIDTH) // 2
PLATFORM_Y = WIN_HEIGHT - 200


# Функція для завантаження зображень
def load_image(name, width=None, height=None):
    """Завантажує зображення, якщо файл не існує - створює кольорову заміну"""
    full_name = os.path.join('images', name)
    try:
        img = pygame.image.load(full_name)
        if width and height:
            img = transform.scale(img, (width, height))
        return img
    except:
        # Якщо файл не знайдено, створюємо кольорову заміну
        if width and height:
            replacement = Surface((width, height))
        else:
            replacement = Surface((100, 100))

        # Різні кольори для різних типів зображень
        if 'harry' in name.lower():
            if 'gold' in name.lower():
                replacement.fill((255, 215, 0))
            elif 'diamond' in name.lower():
                replacement.fill((185, 242, 255))
            elif 'fire' in name.lower():
                replacement.fill((255, 69, 0))
            else:
                replacement.fill((0, 100, 200))
        elif 'lord' in name.lower():
            if 'germiona' in name.lower():
                replacement.fill((128, 0, 128))
            elif 'ron' in name.lower():
                replacement.fill((0, 128, 0))
            elif 'severus' in name.lower():
                replacement.fill((255, 20, 147))
            else:
                replacement.fill((139, 0, 0))
        elif 'platform' in name.lower():
            replacement.fill((139, 69, 19))  # Коричневий для платформи
            # Додаємо текстуру каменю
            for i in range(0, width, 50):
                for j in range(0, height, 25):
                    draw.rect(replacement, (160, 82, 45), (i, j, 48, 23), 2)
        elif 'background' in name.lower():
            replacement.fill((135, 206, 235))
        elif 'menu_bg' in name.lower():
            replacement.fill((20, 20, 50))
        else:
            replacement.fill((128, 128, 128))

        # Додаємо простий контур
        if 'platform' not in name.lower():
            draw.rect(replacement, (255, 255, 255), replacement.get_rect(), 2)

        return replacement


class SkinData:
    def __init__(self):
        self.skins = {
            'harry': [
                {'name': 'Класичний Гаррі', 'unlocked': True, 'image': 'Potter.png'},
                {'name': 'Герміона', 'unlocked': True, 'image': 'germiona.png'},
                {'name': 'Рон', 'unlocked': True, 'image': 'ron.png'},
                {'name': 'Северус', 'unlocked': True, 'image': 'severus.png'}
            ],
            'lord': [
                {'name': 'Темний Лорд', 'unlocked': True, 'image': 'lord.png'},
                {'name': 'Фіолетовий Лорд', 'unlocked': True, 'image': 'oko.png'},
                {'name': 'Зелений Лорд', 'unlocked': True, 'image': 'damboldor.png'},
                {'name': 'Рожевий Лорд', 'unlocked': True, 'image': 'severus.png'}
            ]
        }
        self.selected_skins = {'harry': 0, 'lord': 0}
        self.coins = 50


skin_data = SkinData()

# Завантаження зображень
try:
    menu_bg = load_image('Castle.jpg', WIN_WIDTH, WIN_HEIGHT)
    game_bg = load_image('arena_background.jpg', WIN_WIDTH, WIN_HEIGHT)
    shop_bg = load_image('shop_bg.jpg', WIN_WIDTH, WIN_HEIGHT)
    platform_img = load_image('platform.png', PLATFORM_WIDTH, PLATFORM_HEIGHT)
except:


    platform_img = load_image('platform.png', PLATFORM_WIDTH, PLATFORM_HEIGHT)


def create_character_image(width, height, character_type, skin_index):
    """Створює зображення персонажа з скіном"""
    skin_info = skin_data.skins[character_type][skin_index]
    image = load_image(skin_info['image'], width, height)
    return image


class Platform:
    def __init__(self, x, y, width, height):
        self.rect = Rect(x, y, width, height)
        self.image = platform_img

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class MagicSpell(sprite.Sprite):
    def __init__(self, x, y, direction, power, spell_range, character_type):
        sprite.Sprite.__init__(self)
        self.image = Surface((40, 20))

        # Різні кольори для різних персонажів
        if character_type == 'harry':
            self.image.fill((0, 191, 255))  # Блакитний
        else:
            self.image.fill((255, 0, 0))  # Червоний

        # Додаємо ефект свічення
        draw.ellipse(self.image, (255, 255, 255), (10, 5, 20, 10))

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.start_x = x
        self.speed = 15 * direction
        self.power = power
        self.range = spell_range
        self.character_type = character_type

    def update(self):
        self.rect.x += self.speed
        if abs(self.rect.x - self.start_x) > self.range or self.rect.right < 0 or self.rect.left > WIN_WIDTH:
            self.kill()


class Player(MagicSpell):
    def __init__(self, x, y, controls, character_type, max_hp=100, power=15):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 160
        self.speed = 8
        self.max_hp = max_hp
        self.hp = max_hp
        self.power = power
        self.controls = controls
        self.character_type = character_type

        # Фізика
        self.vel_y = 0
        self.on_ground = False
        self.can_jump = True

        # Стан
        self.is_dead = False
        self.death_angle = 0
        self.facing_right = True

        # Атаки
        self.last_ranged_attack = 0
        self.ranged_cooldown = 600
        self.last_melee_attack = 0
        self.melee_cooldown = 300

        # Анімація
        self.hit_animation = 0

    def get_image(self):
        skin_index = skin_data.selected_skins[self.character_type]
        return create_character_image(self.width, self.height, self.character_type, skin_index)

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

    def update(self, keys, platform):
        if self.is_dead:
            return

        # Горизонтальний рух
        if keys[self.controls['left']]:
            self.x -= self.speed
            self.facing_right = False
        if keys[self.controls['right']]:
            self.x += self.speed
            self.facing_right = True

        # Стрибок
        if keys[self.controls.get('jump', K_SPACE)] and self.on_ground and self.can_jump:
            self.vel_y = JUMP_POWER
            self.on_ground = False
            self.can_jump = False

        # Застосування гравітації
        self.vel_y += GRAVITY
        self.y += self.vel_y

        # Обмеження швидкості падіння
        if self.vel_y > 20:
            self.vel_y = 20

        # Перевірка колізії з платформою
        player_rect = self.get_rect()
        if player_rect.colliderect(platform.rect):
            if self.vel_y > 0:  # Падіння вниз
                self.y = platform.rect.top - self.height
                self.vel_y = 0
                self.on_ground = True
                self.can_jump = True

        # Перевірка падіння за межі екрану (смерть)
        if self.y > WIN_HEIGHT:
            self.take_damage(self.hp)  # Миттєва смерть

        # Обмеження горизонтального руху
        self.x = max(0, min(WIN_WIDTH - self.width, self.x))

        # Зменшення анімації удару
        if self.hit_animation > 0:
            self.hit_animation -= 1

        # Скидання можливості стрибка якщо клавішу відпустили
        if not keys[self.controls.get('jump', K_SPACE)]:
            self.can_jump = True

    def can_ranged_attack(self):
        return time.get_ticks() - self.last_ranged_attack >= self.ranged_cooldown

    def can_melee_attack(self):
        return time.get_ticks() - self.last_melee_attack >= self.melee_cooldown

    # У методі melee_attack класу Player (замінити існуючий метод):
    def melee_attack(self, other_player, spell_group):
        if not self.can_melee_attack():
            return

        # Перевірка дистанції для ближньої атаки
        distance = abs(self.x - other_player.x)
        if distance < 120:  # Дистанція ближньої атаки
            other_player.take_damage(self.power * 2)
            self.last_melee_attack = time.get_ticks()
            # Додати звук ближньої атаки
            melee_attack_sound.play()

    # У методі ranged_attack класу Player (замінити існуючий метод):
    def ranged_attack(self, spell_group):
        if not self.can_ranged_attack():
            return

        direction = 1 if self.facing_right else -1
        start_x = self.x + self.width if self.facing_right else self.x

        spell = MagicSpell(start_x, self.y + self.height // 2, direction, self.power, 400, self.character_type)
        spell_group.add(spell)
        self.last_ranged_attack = time.get_ticks()
        # Додати звук дальньої атаки
        ranged_attack_sound.play()

    def take_damage(self, damage):
        self.hp -= damage
        self.hit_animation = 10
        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True

    def draw(self, surface):
        if self.is_dead:
            if self.death_angle < 90:
                self.death_angle += 3
                rotated = transform.rotate(self.get_image(), self.death_angle)
                rect = rotated.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2 + self.death_angle))
                surface.blit(rotated, rect)
            else:
                rotated = transform.rotate(self.get_image(), 90)
                surface.blit(rotated, (self.x, self.y + 50))
        else:
            image = self.get_image()
            # Ефект удару - червоний відтінок
            if self.hit_animation > 0:
                red_surface = Surface((self.width, self.height))
                red_surface.fill((255, 0, 0))
                red_surface.set_alpha(100)
                image.blit(red_surface, (0, 0))
            surface.blit(image, (self.x, self.y))


class MenuButton:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), hover_color=(150, 150, 150)):
        self.rect = Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        draw.rect(surface, color, self.rect)
        draw.rect(surface, (255, 255, 255), self.rect, 3)

        text_surface = font_medium.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos, mouse_clicked):
        return self.rect.collidepoint(mouse_pos) and mouse_clicked


class GameState:
    def __init__(self):
        self.state = MENU
        self.platform = Platform(PLATFORM_X, PLATFORM_Y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        self.reset_game()

        # Створення кнопок меню
        button_width = 300
        button_height = 60
        button_x = WIN_WIDTH // 2 - button_width // 2

        self.menu_buttons = {
            'start': MenuButton(button_x, 300, button_width, button_height, "ПОЧАТИ ГРУ"),
            'shop': MenuButton(button_x, 390, button_width, button_height, "МАГАЗИН СКІНІВ"),
            'exit': MenuButton(button_x, 480, button_width, button_height, "ВИХІД")
        }

    def reset_game(self):
        # Створення гравців на платформі
        harry_controls = {
            'left': K_a,
            'right': K_d,
            'melee': K_s,
            'ranged': K_w,
            'jump': K_SPACE
        }

        lord_controls = {
            'left': K_LEFT,
            'right': K_RIGHT,
            'melee': K_DOWN,
            'ranged': K_UP,
            'jump': K_RSHIFT
        }

        # Розміщуємо персонажів на платформі
        self.harry = Player(PLATFORM_X + 150, PLATFORM_Y - 160, harry_controls, 'harry', 100, 20)
        self.lord = Player(PLATFORM_X + PLATFORM_WIDTH - 300, PLATFORM_Y - 160, lord_controls, 'lord', 100, 25)
        self.spell_group = sprite.Group()
        self.winner = None

    def handle_menu_events(self, events, mouse_pos, mouse_clicked):
        for button_name, button in self.menu_buttons.items():
            button.update(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                if button_name == 'start':
                    self.state = GAME
                    self.reset_game()
                elif button_name == 'shop':
                    self.state = SHOP
                elif button_name == 'exit':
                    return False

        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    self.state = GAME
                    self.reset_game()
                elif event.key == K_s:
                    self.state = SHOP
                elif event.key == K_ESCAPE:
                    return False
        return True

    def handle_shop_events(self, events):
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_BACKSPACE:
                    self.state = MENU
                elif event.key == K_q:  # Змінити скін Гаррі
                    self.change_skin('harry')
                elif event.key == K_e:  # Змінити скін Лорда
                    self.change_skin('lord')
        return True

    def change_skin(self, character):
        skins = skin_data.skins[character]
        current = skin_data.selected_skins[character]

        # Знайти наступний скін (всі скіни тепер безкоштовні)
        next_index = (current + 1) % len(skins)
        skin_data.selected_skins[character] = next_index

    def handle_game_events(self, events):
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.state = MENU
                elif event.key == K_r and (self.harry.is_dead or self.lord.is_dead):
                    self.reset_game()
                elif event.key == self.harry.controls['melee']:
                    self.harry.melee_attack(self.lord, self.spell_group)
                elif event.key == self.harry.controls['ranged']:
                    self.harry.ranged_attack(self.spell_group)
                elif event.key == self.lord.controls['melee']:
                    self.lord.melee_attack(self.harry, self.spell_group)
                elif event.key == self.lord.controls['ranged']:
                    self.lord.ranged_attack(self.spell_group)
        return True

    def update_game(self, keys):
        if not self.harry.is_dead and not self.lord.is_dead:
            self.harry.update(keys, self.platform)
            self.lord.update(keys, self.platform)

            # Оновлення заклинань
            self.spell_group.update()

            # Перевірка колізій заклинань
            for spell in self.spell_group:
                if spell.rect.colliderect(self.harry.get_rect()) and spell.character_type != 'harry':
                    self.harry.take_damage(spell.power)
                    spell.kill()
                elif spell.rect.colliderect(self.lord.get_rect()) and spell.character_type != 'lord':
                    self.lord.take_damage(spell.power)
                    spell.kill()

            # Перевірка переможця
            if self.harry.is_dead:
                self.winner = "Темний Лорд переміг!"
                skin_data.coins += 20
            elif self.lord.is_dead:
                self.winner = "Гаррі Поттер переміг!"
                skin_data.coins += 20

    def draw_menu(self):
        screen.blit(menu_bg, (0, 0))

        # Заголовок з ефектом
        title = font_large.render("Hogwarts Kombat", True, (255, 215, 0))
        title_shadow = font_large.render("Hogwarts Kombat", True, (139, 0, 0))
        screen.blit(title_shadow, (WIN_WIDTH // 2 - title.get_width() // 2 + 3, 103))
        screen.blit(title, (WIN_WIDTH // 2 - title.get_width() // 2, 100))

        subtitle = font_medium.render("ARENA", True, (255, 255, 255))
        screen.blit(subtitle, (WIN_WIDTH // 2 - subtitle.get_width() // 2, 180))

        # Малювання кнопок
        for button in self.menu_buttons.values():
            button.draw(screen)


        # Інструкції
        instruction_text = font_small.render(
            "Також можна використовувати клавіші: ENTER - гра, S - магазин, ESC - вихід", True, (200, 200, 200))
        screen.blit(instruction_text, (WIN_WIDTH // 2 - instruction_text.get_width() // 2, 650))

    def draw_shop(self):
        screen.blit(shop_bg, (0, 0))

        title = font_large.render("МАГАЗИН СКІНІВ", True, (255, 255, 255))
        title_shadow = font_large.render("МАГАЗИН СКІНІВ", True, (139, 0, 139))
        screen.blit(title_shadow, (WIN_WIDTH // 2 - title.get_width() // 2 + 2, 52))
        screen.blit(title, (WIN_WIDTH // 2 - title.get_width() // 2, 50))


        # Скіни Гаррі з превью
        harry_title = font_medium.render("ГАРРІ ПОТТЕР:", True, (255, 255, 255))
        screen.blit(harry_title, (100, 200))

        for i, skin in enumerate(skin_data.skins['harry']):
            y_pos = 250 + i * 60
            selected = "►" if skin_data.selected_skins['harry'] == i else "  "
            text = font_small.render(f"{selected} {skin['name']}", True, (255, 255, 255))
            screen.blit(text, (120, y_pos))

            # Превью скіна
            preview = create_character_image(40, 80, 'harry', i)
            screen.blit(preview, (350, y_pos - 10))

        # Скіни Лорда з превью
        lord_title = font_medium.render("ТЕМНИЙ ЛОРД:", True, (255, 255, 255))
        screen.blit(lord_title, (600, 200))

        for i, skin in enumerate(skin_data.skins['lord']):
            y_pos = 250 + i * 60
            selected = "►" if skin_data.selected_skins['lord'] == i else "  "
            text = font_small.render(f"{selected} {skin['name']}", True, (255, 255, 255))
            screen.blit(text, (620, y_pos))

            # Превью скіна
            preview = create_character_image(40, 80, 'lord', i)
            screen.blit(preview, (850, y_pos - 10))

        # Інструкції
        instructions = [
            "Q - Змінити скін Гаррі",
            "E - Змінити скін Лорда",
            "ESC - Повернутися в меню"
        ]

        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            screen.blit(text, (100, 550 + i * 30))

    def draw_game(self):
        screen.blit(game_bg, (0, 0))

        # Малювання платформи
        self.platform.draw(screen)

        # Малювання персонажів
        self.harry.draw(screen)
        self.lord.draw(screen)

        # Малювання заклинань
        self.spell_group.draw(screen)

        # UI з покращеним дизайном
        # Здоров'я Гаррі
        harry_hp_text = font_medium.render(f"Гаррі: {self.harry.hp}/100", True, (255, 255, 255))
        screen.blit(harry_hp_text, (50, 50))

        # Смуга здоров'я Гаррі з рамкою
        draw.rect(screen, (255, 255, 255), (48, 88, 204, 24), 2)
        draw.rect(screen, (255, 0, 0), (50, 90, 200, 20))
        draw.rect(screen, (0, 255, 0), (50, 90, int(200 * self.harry.hp / 100), 20))

        # Здоров'я Лорда
        lord_hp_text = font_medium.render(f"Лорд: {self.lord.hp}/100", True, (255, 255, 255))
        screen.blit(lord_hp_text, (WIN_WIDTH - 250, 50))

        # Смуга здоров'я Лорда з рамкою
        draw.rect(screen, (255, 255, 255), (WIN_WIDTH - 252, 88, 204, 24), 2)
        draw.rect(screen, (255, 0, 0), (WIN_WIDTH - 250, 90, 200, 20))
        draw.rect(screen, (0, 255, 0), (WIN_WIDTH - 250, 90, int(200 * self.lord.hp / 100), 20))

        # Керування в красивій рамці
        control_bg = Surface((WIN_WIDTH - 100, 100))
        control_bg.fill((0, 0, 0))
        control_bg.set_alpha(150)
        screen.blit(control_bg, (50, WIN_HEIGHT - 150))

        controls_text = [
            "Гаррі: A/D - рух, S - ближня атака, W - дальня атака, ПРОБІЛ - стрибок",
            "Лорд: ←/→ - рух, ↓ - ближня атака, ↑ - дальня атака, R.SHIFT - стрибок"
        ]

        for i, text in enumerate(controls_text):
            rendered = font_small.render(text, True, (255, 255, 255))
            screen.blit(rendered, (60, WIN_HEIGHT - 140 + i * 25))


        # Повідомлення про переможця з ефектом
        if self.winner:
            # Фон для повідомлення
            winner_bg = Surface((600, 150))
            winner_bg.fill((0, 0, 0))
            winner_bg.set_alpha(200)
            screen.blit(winner_bg, (WIN_WIDTH // 2 - 300, WIN_HEIGHT // 2 - 75))

            winner_text = font_large.render(self.winner, True, (255, 215, 0))
            winner_shadow = font_large.render(self.winner, True, (139, 0, 0))
            screen.blit(winner_shadow, (WIN_WIDTH // 2 - winner_text.get_width() // 2 + 2, WIN_HEIGHT // 2 - 48))
            screen.blit(winner_text, (WIN_WIDTH // 2 - winner_text.get_width() // 2, WIN_HEIGHT // 2 - 50))

            restart_text = font_medium.render("R - ПЕРЕЗАПУСК, ESC - МЕНЮ", True, (255, 255, 255))
            screen.blit(restart_text, (WIN_WIDTH // 2 - restart_text.get_width() // 2, WIN_HEIGHT // 2 + 20))


# Основний цикл гри
def main():
    game_state = GameState()
    running = True

    while running:
        mouse_pos = mouse.get_pos()
        mouse_clicked = False

        events = event.get()
        for e in events:
            if e.type == QUIT:
                running = False
            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 1:  # Ліва кнопка миші
                    mouse_clicked = True

        keys = key.get_pressed()

        if game_state.state == MENU:
            running = game_state.handle_menu_events(events, mouse_pos, mouse_clicked)
            game_state.draw_menu()
        elif game_state.state == SHOP:
            game_state.handle_shop_events(events)
            game_state.draw_shop()
        elif game_state.state == GAME:
            game_state.handle_game_events(events)
            game_state.update_game(keys)
            game_state.draw_game()

        display.flip()
        clock.tick(FPS)

    quit()


if __name__ == "__main__":
    main()
