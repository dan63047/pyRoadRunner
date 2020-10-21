import pygame
import random

WIN_SIZE_X = 600
WIN_SIZE_Y = 800
FRAMERATE = 60


class Player:
    def __init__(self):
        self.fuel = 100
        self.screen_speed = 3
        self.odometer = 0
        self.speed = 0
        self.stable = True
        self.destroyed = False
        self.color = (255, 0, 0)
        self.size = [20, 40]
        self.coords = [200, 500]
        self.consumption = 1.5
        self.score = 0

    def get_currect_color(self):
        if self.destroyed:
            return self.color[0] / 6, self.color[1] / 6, self.color[2] / 6
        else:
            return self.color

    def draw(self):
        pygame.draw.rect(win, self.get_currect_color(), (player.coords, player.size))

    def respawn(self):
        self.coords = [200, 500]
        self.fuel -= 5
        self.score -= 200

    def is_engine_on(self):
        if self.fuel <= 0:
            self.fuel = 0
            return False
        else:
            self.fuel -= self.consumption / FRAMERATE
            return True


class EnemyCar:
    def __init__(self, x=None, odo=None, spd=None):
        if x is None:
            self.x = 210
        else:
            self.x = x
        if odo is None:
            self.odometer = 0
        else:
            self.odometer = odo
        if spd is None:
            self.speed = 0
        else:
            self.speed = spd
        self.size = [20, 40]
        self.color = (100, 100, 100)
        self.y = 0

    def draw(self):
        self.y = (-self.odometer * road.get_scale() + player.odometer * road.get_scale()) + WIN_SIZE_Y / 2
        if WIN_SIZE_Y > self.y > -50:
            pygame.draw.rect(win, self.color, ([self.x, self.y], self.size))

    def collision_with_player(self):
        if self.x - player.size[0] < player.coords[0] < self.x + self.size[0] and self.y - player.size[1] < player.coords[1] < self.y + self.size[1]:
            return True
        else:
            return False

    def respawn(self):
        self.odometer += random.randint(5, 15) / 10
        self.speed = random.randint(100, 350)
        self.x = random.randint(road.left, road.right + EnemyCar().size[0])


class EnemyOnStart(EnemyCar):
    def __init__(self, x=None, odo=None):
        super().__init__(x, odo)
        self.speed = 600
        self.size = [20, 40]
        self.color = (0, 0, 255)
        self.y = 0


class Canister:
    def __init__(self, x=None, m=None, v=None):
        if x is None:
            self.x = 210
        else:
            self.x = x
        if m is None:
            self.road_milestone = 0.50
        else:
            self.road_milestone = m
        if v is None:
            self.volume = 15
        else:
            self.volume = v
        self.y = 0

    def draw(self):
        self.y = (-self.road_milestone * road.get_scale() + player.odometer * road.get_scale()) + WIN_SIZE_Y / 2
        if WIN_SIZE_Y > self.y > -50:
            pygame.draw.circle(win, (0, 255, 0), (self.x, int(self.y)), 5)

    def respawn(self):
        self.road_milestone += random.randint(5, 20) / 10
        self.x = random.randint(road.left, road.right)

    def collision_with_player(self):
        if self.x - player.size[0] < player.coords[0] < self.x + player.size[0] and self.y - player.size[1] < player.coords[1] < self.y + player.size[1]:
            return True
        else:
            return False


class Road:
    def __init__(self):
        self.left = 70
        self.right = 300
        self.__scale = 10000

    def draw(self):
        pygame.draw.rect(win, (255, 255, 255), (self.left, 0, self.right, WIN_SIZE_Y), 2)

    def get_scale(self):
        return self.__scale


pygame.init()
pygame.font.init()
hat_font = pygame.font.Font("Curse_Casual_Cyrillic.ttf", 30)
small_hat_font = pygame.font.Font("Curse_Casual_Cyrillic.ttf", 10)
win = pygame.display.set_mode((WIN_SIZE_X, WIN_SIZE_Y))
clock = pygame.time.Clock()
pygame.display.set_caption("dan63047 RoadRunner")
road = Road()
player = Player()
enemy = [EnemyCar(random.randint(road.left, road.right+EnemyCar().size[0]), random.randint(0, 150)/100, random.randint(100, 350)) for i in range(150)]
enemy.append(EnemyOnStart())
bonuses = [Canister(random.randint(road.left, road.right), random.randint(0, 200)/100, random.randint(5, 15)) for i in range(3)]


def draw():
    win.fill((25, 25, 25))
    player.draw()
    road.draw()
    for e in enemy:
        e.draw()
    for b in bonuses:
        b.draw()
    if player.fuel > 20:
        fuel_color = (255, 255, 255)
    else:
        fuel_color = (255, 0, 0)
    win.blit(hat_font.render(f"SCORE: {player.score:.{0}f}", 1, (255, 255, 255)), (400, 50))
    win.blit(hat_font.render(f"FUEL: {player.fuel:.{0}f}", 1, fuel_color), (400, WIN_SIZE_Y-50))
    win.blit(hat_font.render(f"SPD: {player.speed:.{0}f} km/h", 1, (255, 255, 255)), (400, WIN_SIZE_Y-75))
    win.blit(hat_font.render(f"ODO: {player.odometer:.{2}f} km", 1, (255, 255, 255)), (400, WIN_SIZE_Y-100))
    win.blit(small_hat_font.render(f"p x: {player.coords[0]}; y: {player.coords[1]}", 1, (255, 255, 255)), (0, 25))
    win.blit(small_hat_font.render(str(clock), 1, (255, 255, 255)), (0, 15))
    win.blit(small_hat_font.render(f"enemys: {len(enemy)}", 1, (255, 255, 255)), (0, 35))
    pygame.display.update()


def gameplay_loop():
    end = False
    respawn_sec = 3
    frames_until_respawn = FRAMERATE * respawn_sec
    while not end:
        clock.tick(FRAMERATE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end = True
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            end = True

        accelerating = False
        if not player.destroyed:
            if player.speed > 0:
                if keys[pygame.K_LEFT] and player.coords[0]-player.screen_speed > road.left:
                    player.coords[0] -= player.screen_speed
                if keys[pygame.K_RIGHT] and player.coords[0]+player.screen_speed < road.left+road.right-player.size[0]:
                    player.coords[0] += player.screen_speed
            if player.is_engine_on():
                if keys[pygame.K_UP] and player.coords[1] - player.screen_speed > 0 and not player.destroyed:
                    player.coords[1] -= player.screen_speed
                if keys[pygame.K_DOWN] and player.coords[1] + player.screen_speed < WIN_SIZE_Y - player.size[1] and not player.destroyed:
                    player.coords[1] += player.screen_speed
                if keys[pygame.K_SPACE]:
                    accelerating = True
            if accelerating:
                if player.speed < 400:
                    player.speed += 3
            else:
                if player.speed > 0:
                    player.speed -= 3
            player.odometer += (player.speed/3600)/FRAMERATE
            player.score += player.speed/(FRAMERATE*10)

        for e in enemy:
            e.odometer += (e.speed/3600)/FRAMERATE
            if WIN_SIZE_Y+200 < e.y:
                e.respawn()
            if isinstance(e, EnemyOnStart) and e.y < -200:
                enemy.remove(e)
            if e.collision_with_player():
                player.destroyed = True

        for b in bonuses:
            if b.collision_with_player():
                player.fuel += b.volume
                player.score += 500
                b.respawn()
            if WIN_SIZE_Y+200 < b.y:
                b.respawn()

        if player.destroyed:
            player.speed = 0
            frames_until_respawn -= 1
            if frames_until_respawn == 0:
                player.destroyed = False
                frames_until_respawn = FRAMERATE*respawn_sec
                player.respawn()

        draw()


if __name__ == "__main__":
    gameplay_loop()
    pygame.quit()
