import pygame, random

EXIT = False
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
        self.engine_on = True
        self.score = 0

    def get_currect_color(self):
        if self.destroyed:
            return self.color[0] / 6, self.color[1] / 6, self.color[2] / 6
        else:
            return self.color


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


class Road:
    def __init__(self):
        self.left = 70
        self.right = 300


pygame.init()
pygame.font.init()
hat_font = pygame.font.Font("Curse_Casual_Cyrillic.ttf", 30)
small_hat_font = pygame.font.Font("Curse_Casual_Cyrillic.ttf", 10)
win = pygame.display.set_mode((WIN_SIZE_X, WIN_SIZE_Y))
clock = pygame.time.Clock()
pygame.display.set_caption("dan63047 RoadRunner")
road = Road()
player = Player()
respawn_sec = 3
frames_until_respawn = FRAMERATE*respawn_sec
enemy = [EnemyCar(random.randint(road.left, road.right+EnemyCar().size[0]), random.randint(0, 150)/100, random.randint(100, 350)) for i in range(150)]
b = [Canister(random.randint(road.left, road.right), random.randint(0, 200)/100, random.randint(5, 15)) for i in range(3)]


def draw():
    win.fill((25, 25, 25))
    pygame.draw.rect(win, (255, 255, 255), (road.left, 0, road.right, WIN_SIZE_Y), 2)
    pygame.draw.rect(win, player.get_currect_color(), (player.coords, player.size))
    rendered = 0
    scale = 10000
    center_y = WIN_SIZE_Y / 2
    for e in enemy:
        enemy_y = (-e.odometer*scale + player.odometer*scale)+center_y
        e.y = enemy_y
        if WIN_SIZE_Y > enemy_y > -50:
            rendered += 1
            pygame.draw.rect(win, e.color, ([e.x, enemy_y], e.size))
    for v in b:
        bonus_y = (-v.road_milestone*scale + player.odometer*scale)+center_y
        v.y = bonus_y
        if WIN_SIZE_Y > bonus_y > -50:
            rendered += 1
            pygame.draw.circle(win, (0, 255, 0), (v.x, int(v.y)), 5)
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
    win.blit(small_hat_font.render(f"rendered: {rendered}", 1, (255, 255, 255)), (0, 35))
    pygame.display.update()


while not EXIT:
    clock.tick(FRAMERATE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            EXIT = True
    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        EXIT = True

    if not player.destroyed:
        if player.speed > 0:
            if keys[pygame.K_LEFT] and player.coords[0]-player.screen_speed > road.left:
                player.coords[0] -= player.screen_speed
            if keys[pygame.K_RIGHT] and player.coords[0]+player.screen_speed < road.left+road.right-player.size[0]:
                player.coords[0] += player.screen_speed
        if keys[pygame.K_SPACE] and player.engine_on:
            if player.speed < 400:
                player.speed += 3
        else:
            if player.speed > 0:
                player.speed -= 3
        player.odometer += (player.speed/3600)/FRAMERATE
        player.score += player.speed/(FRAMERATE*10)

    for e in enemy:
        e.odometer += (e.speed/3600)/FRAMERATE
        if e.x-player.size[0] < player.coords[0] < e.x+e.size[0] and e.y-player.size[1] < player.coords[1] < e.y+e.size[1]:
            player.destroyed = True
        if e.y > WIN_SIZE_Y+200:
            e.odometer += random.randint(5, 15)/10
            e.speed = random.randint(100, 350)
            e.x = random.randint(road.left, road.right+EnemyCar().size[0])

    for v in b:
        if v.x-player.size[0] < player.coords[0] < v.x+player.size[0] and v.y-player.size[1] < player.coords[1] < v.y+player.size[1]:
            player.fuel += 15
            player.engine_on = True
            player.score += 500
            v.road_milestone += random.randint(5, 20)/10
            v.x = random.randint(road.left, road.right)
        if v.y > WIN_SIZE_Y+200:
            v.road_milestone += random.randint(5, 20)/10
            v.x = random.randint(road.left, road.right)

    if player.destroyed:
        player.speed = 0
        frames_until_respawn -= 1
        if frames_until_respawn == 0:
            player.destroyed = False
            frames_until_respawn = FRAMERATE*respawn_sec
            player.coords = [200, 500]
            player.fuel -= 5
            player.score -= 200

    draw()
    if player.engine_on:
        if keys[pygame.K_UP] and player.coords[1] - player.screen_speed > 0 and not player.destroyed:
            player.coords[1] -= player.screen_speed
        if keys[pygame.K_DOWN] and player.coords[1] + player.screen_speed < WIN_SIZE_Y - player.size[1] and not player.destroyed:
            player.coords[1] += player.screen_speed
        player.fuel -= player.consumption/FRAMERATE
    if player.fuel < 0.1:
        player.fuel = 0
        player.engine_on = False

pygame.quit()
