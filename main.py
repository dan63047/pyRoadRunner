import pygame
import random
import locale
import datetime
import json
from string import Template

WIN_SIZE_X = 600
WIN_SIZE_Y = 800
FRAMERATE = 60


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    hours += d["D"]*24
    d["H"] = locale.format_string('%d', hours, grouping=True)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


class GameObject:
    def __init__(self, **args):
        if 'size' not in args:
            self.size = [20, 40]
        else:
            self.size = args['size']
        if 'x' not in args:
            self.x = 100
        else:
            self.x = args['x']
        if 'y' not in args:
            self.y = 100
        else:
            self.y = args['y']
        if 'texture' not in args:
            self.texture = pygame.image.load("textures/Player.png")
        else:
            self.texture = pygame.image.load(args['texture'])


class Player(GameObject):
    def __init__(self):
        super().__init__(size=[32, 64], x=200, y=500, texture="textures/Player.png")
        self.fuel = 100
        self.screen_speed = 3
        self.odometer = 0
        self.speed = 0
        self.stable = True
        self.destroyed = False
        self.color = (255, 0, 0)
        self.consumption = 1.5
        self.score = 0

    def draw(self):
        if self.destroyed:
            pygame.draw.rect(game.win, (43, 0, 0), (self.x, self.y, self.size[0], self.size[1]))
        else:
            game.win.blit(self.texture, (self.x, self.y))

    def respawn(self):
        self.x = 200
        self.y = 500
        game.incriment("score", -200)

    def is_engine_on(self):
        if self.fuel <= 0:
            self.fuel = 0
            return False
        else:
            game.incriment("fuel", self.consumption / FRAMERATE)
            return True


class EnemyCar(GameObject):
    def __init__(self, x=None, odo=None, spd=None, **args):
        if x is None:
            x = 210
        super().__init__(x=x, y=0, size=[32, 64], texture="textures/EnemyCar.png")
        if odo is None:
            self.odometer = 0
        else:
            self.odometer = odo
        if spd is None:
            self.speed = 0
        else:
            self.speed = spd
        self.color = (100, 100, 100)
        self.y = 0

    def draw(self):
        self.y = (-self.odometer * game.road.get_scale() + game.player.odometer * game.road.get_scale()) + WIN_SIZE_Y / 2
        if WIN_SIZE_Y > self.y > -50:
            game.win.blit(self.texture, (self.x, self.y))

    def collision_with_player(self):
        if self.x - game.player.size[0] < game.player.x < self.x + self.size[0] and self.y - game.player.size[1] < game.player.y < self.y + self.size[1]:
            return True
        else:
            return False

    def respawn(self):
        self.odometer += random.randint(5, 15) / 10
        self.speed = random.randint(100, 350)
        self.x = random.randint(game.road.left, game.road.right + EnemyCar().size[0])


class EnemyOnStart(EnemyCar):
    def __init__(self, x=None, odo=None):
        super().__init__(x, odo)
        self.speed = 600
        self.size = [20, 40]
        self.color = (0, 0, 255)
        self.y = 0


class Canister(GameObject):
    def __init__(self, x=None, m=None, v=None):
        if x is None:
            x = 210
        super().__init__(x=x, y=0)
        if m is None:
            self.road_milestone = 0.50
        else:
            self.road_milestone = m
        if v is None:
            self.volume = 15
        else:
            self.volume = v

    def draw(self):
        self.y = (-self.road_milestone * game.road.get_scale() + game.player.odometer * game.road.get_scale()) + WIN_SIZE_Y / 2
        if WIN_SIZE_Y > self.y > -50:
            pygame.draw.circle(game.win, (0, 255, 0), (self.x, int(self.y)), 5)

    def respawn(self):
        self.road_milestone += random.randint(5, 20) / 10
        self.x = random.randint(game.road.left, game.road.right)

    def collision_with_player(self):
        if self.x - game.player.size[0] < game.player.x < self.x + game.player.size[0] and self.y - game.player.size[1] < game.player.y < self.y + game.player.size[1]:
            return True
        else:
            return False


class Road:
    def __init__(self):
        self.left = 70
        self.right = 300
        self.__scale = 10000

    def draw(self):
        pygame.draw.rect(game.win, (255, 255, 255), (self.left, 0, self.right, WIN_SIZE_Y), 2)

    def get_scale(self):
        return self.__scale


class GameWindow:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font("19471.ttf", 30)
        self.small_font = pygame.font.Font("19471.ttf", 14)
        self.win = pygame.display.set_mode((WIN_SIZE_X, WIN_SIZE_Y))
        self.clock = pygame.time.Clock()
        self.state = "main_menu"
        try:
            with open("r.r", "r") as jsn:
                self.stats = json.load(jsn)
        except:
            self.stats = {"hi_score": 0, "hi_odo": 0, "total_score": 0, "total_odo": 0, "total_fuel_burned": 0, "times_played": 0, "gameplay_time": 0, "crashes": 0, "canisters_picked_up": 0}
        self.game_over = False
        pygame.display.set_caption("dan63047 RoadRunner")

    def incriment(self, thing, number):
        if thing == "score":
            self.player.score += number
            self.stats['total_score'] += number
        elif thing == "fuel":
            self.player.fuel -= number
            game.stats['total_fuel_burned'] += number
        elif thing == "odo":
            self.player.odometer += number
            self.stats['total_odo'] += number


    def create_session(self):
        self.road = Road()
        self.player = Player()
        self.enemy = [EnemyCar(random.randint(self.road.left, self.road.right+EnemyCar().size[0]), random.randint(0, 150)/100, random.randint(100, 350)) for i in range(150)]
        self.enemy.append(EnemyOnStart())
        self.bonuses = [Canister(random.randint(self.road.left, self.road.right), random.randint(0, 200)/100, random.randint(5, 15)) for i in range(3)]
        self.respawn_sec = 3
        self.frames_until_respawn = FRAMERATE * self.respawn_sec
        self.stats["times_played"] += 1

    def main_menu_draw(self):
        self.win.fill((25, 25, 25))
        big_font = pygame.font.Font("19471.ttf", 60)
        self.win.blit(big_font.render("py Road Runner", 1, (255, 255, 255)), (WIN_SIZE_X/2-150, 50))
        self.win.blit(self.font.render("[N] Start", 1, (255, 255, 255)), (200, 200))
        self.win.blit(self.font.render("[B] Settings", 1, (255, 255, 255)), (200, 230))
        self.win.blit(self.font.render("[Esc] Exit", 1, (255, 255, 255)), (200, 260))
        self.win.blit(self.font.render("Stats:", 1, (255, 255, 255)), (100, 350))
        self.win.blit(self.font.render(f"Top score: {locale.format_string('%d', self.stats['hi_score'], grouping=True)}", 1, (255, 255, 255)), (100, 375))
        self.win.blit(self.font.render(f"Top ODO: {locale.format_string('%.2f', self.stats['hi_odo'], grouping=True)} km", 1, (255, 255, 255)), (100, 400))
        self.win.blit(self.font.render(f"Times played: {locale.format_string('%d', self.stats['times_played'], grouping=True)}", 1, (255, 255, 255)), (100, 425))
        self.win.blit(self.font.render(f"Time played: {strfdelta(datetime.timedelta(seconds=self.stats['gameplay_time']), '%H:%M:%S')}", 1, (255, 255, 255)), (100, 450))
        self.win.blit(self.font.render(f"Total score: {locale.format_string('%d', self.stats['total_score'], grouping=True)}", 1, (255, 255, 255)), (100, 475))
        self.win.blit(self.font.render(f"Total ODO: {locale.format_string('%.2f', self.stats['total_odo'], grouping=True)} km", 1, (255, 255, 255)), (100, 500))
        self.win.blit(self.font.render(f"Fuel burned: {locale.format_string('%d', self.stats['total_fuel_burned'], grouping=True)}", 1, (255, 255, 255)), (100, 525))
        self.win.blit(self.font.render(f"Crashes: {locale.format_string('%d', self.stats['crashes'], grouping=True)}", 1, (255, 255, 255)), (100, 550))
        self.win.blit(self.font.render(f"Canisters picked: {locale.format_string('%d', self.stats['canisters_picked_up'], grouping=True)}", 1, (255, 255, 255)), (100, 575))
        pygame.display.update()

    def gameplay_draw(self):
        self.win.fill((25, 25, 25))
        self.player.draw()
        self.road.draw()
        for e in self.enemy:
            e.draw()
        for b in self.bonuses:
            b.draw()
        if self.player.fuel > 20:
            fuel_color = (255, 255, 255)
        else:
            fuel_color = (255, 0, 0)
        self.win.blit(self.font.render(f"SCORE: {locale.format_string('%d', self.player.score, grouping=True)}", 1, (255, 255, 255)), (400, 50))
        self.win.blit(self.small_font.render(f"HI-SCORE: {locale.format_string('%d', self.stats['hi_score'], grouping=True)}", 1, (255, 255, 255)), (400, 75))
        self.win.blit(self.font.render(f"FUEL: {self.player.fuel:.{0}f}", 1, fuel_color), (400, WIN_SIZE_Y - 50))
        self.win.blit(self.font.render(f"SPD: {self.player.speed:.{0}f} km/h", 1, (255, 255, 255)), (400, WIN_SIZE_Y - 75))
        self.win.blit(self.font.render(f"ODO: {self.player.odometer:.{2}f} km", 1, (255, 255, 255)), (400, WIN_SIZE_Y - 100))
        self.win.blit(self.small_font.render(f"FPS: {self.clock.get_fps():{1}f}", 1, (255, 255, 255)), (0, 15))
        self.win.blit(self.small_font.render(f"{self.clock.get_time()} ms", 1, (255, 255, 255)), (0, 35))
        if self.game_over:
            self.win.blit(self.font.render(f"GAME OVER", 1, (255, 255, 255)), (400, 175))
            self.win.blit(self.font.render(f"[N] New game", 1, (255, 255, 255)), (400, 200))
            self.win.blit(self.font.render(f"[M] To main menu", 1, (255, 255, 255)), (400, 200))
        pygame.display.update()

    def gameplay_loop(self):
        accelerating = False
        keys = pygame.key.get_pressed()
        engine_on = self.player.is_engine_on()
        if self.player.speed > 0 and not self.player.destroyed:
            if keys[pygame.K_LEFT] and self.player.x-self.player.screen_speed > self.road.left:
                self.player.x -= self.player.screen_speed
            if keys[pygame.K_RIGHT] and self.player.x+self.player.screen_speed < self.road.left+self.road.right-self.player.size[0]:
                self.player.x += self.player.screen_speed
        if engine_on and not self.player.destroyed:
            if keys[pygame.K_UP] and self.player.y - self.player.screen_speed > 0:
                self.player.y -= self.player.screen_speed
            if keys[pygame.K_DOWN] and self.player.y + self.player.screen_speed < WIN_SIZE_Y - self.player.size[1]:
                self.player.y += self.player.screen_speed
            if keys[pygame.K_SPACE]:
                accelerating = True
        if accelerating and not self.player.destroyed:
            if self.player.speed < 400:
                self.player.speed += 3
        else:
            if self.player.speed > 0:
                self.player.speed -= 3
        self.incriment("score", self.player.speed/(FRAMERATE*10))
        self.incriment("odo", (self.player.speed/3600)/FRAMERATE)
        if self.player.score > self.stats['hi_score']:
            self.stats['hi_score'] = self.player.score
        if self.player.odometer > self.stats['hi_odo']:
            self.stats['hi_odo'] = self.player.odometer

        for e in self.enemy:
            e.odometer += (e.speed/3600)/FRAMERATE
            if WIN_SIZE_Y+200 < e.y:
                e.respawn()
            if isinstance(e, EnemyOnStart) and e.y < -200:
                self.enemy.remove(e)
            if e.collision_with_player():
                if not self.player.destroyed:
                    self.stats['crashes'] += 1
                self.player.destroyed = True

        for b in self.bonuses:
            if b.collision_with_player():
                self.player.fuel += b.volume
                self.incriment("score", 500)
                self.stats['canisters_picked_up'] += 1
                b.respawn()
            if WIN_SIZE_Y+200 < b.y:
                b.respawn()

        if self.player.destroyed:
            self.player.speed = 0
            self.frames_until_respawn -= 1
            if self.frames_until_respawn == 0:
                self.player.destroyed = False
                self.frames_until_respawn = FRAMERATE*self.respawn_sec
                self.player.respawn()

        if not engine_on and self.player.speed <= 0:
            self.game_over = True
            if keys[pygame.K_m]:
                self.state = "main_menu"
            if keys[pygame.K_n]:
                self.state = "create_session"
        else:
            self.stats['gameplay_time'] += self.clock.get_time()/1000

        self.gameplay_draw()

    def main_loop(self):
        need = True
        while need:
            self.clock.tick(FRAMERATE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    need = False
            keys = pygame.key.get_pressed()

            if keys[pygame.K_ESCAPE]:
                need = False
                self.main_menu_draw()
            if self.state == "main_menu":
                self.main_menu_draw()
                if keys[pygame.K_n]:
                    self.state = "create_session"
            elif self.state == "create_session":
                self.game_over = False
                self.create_session()
                self.state = "gameplay"
            elif self.state == "gameplay":
                self.gameplay_loop()
            with open("r.r", "w") as jsn:
                json.dump(self.stats, jsn)


if __name__ == "__main__":
    locale.setlocale(locale.LC_NUMERIC, ('ru_RU', 'UTF-8'))
    game = GameWindow()
    game.main_loop()
    pygame.quit()
