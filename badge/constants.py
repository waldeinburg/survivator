import math

DEBUG=False

HERO_WIDTH = 9
HERO_HEIGHT = 9
HERO_SIZE = 9
HERO_RADIUS = HERO_SIZE / 2

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 160

INFO_HEIGHT = 11

PLAY_WIDTH = SCREEN_WIDTH
PLAY_HEIGHT = SCREEN_HEIGHT - INFO_HEIGHT

HERO_EXPLODE_WIDTH = 21
HERO_EXPLODE_HEIGHT = 21

SHIELD_WIDTH = 17
SHIELD_DEPTH = 9

ROCKET_SIZE = 7
ROCKET_WIDTH = ROCKET_SIZE
ROCKET_HEIGHT = ROCKET_SIZE

FIREWALL_BITMAP_HEIGHT = 20
FIREWALL_DEPTH = 15
FIREWALL_HOR_TILES = 5
FIREWALL_VER_TILES = 4
FIREWALL_HOR_TILE_SIZE = FIREWALL_BITMAP_HEIGHT // FIREWALL_HOR_TILES
FIREWALL_VER_TILE_SIZE = FIREWALL_BITMAP_HEIGHT // FIREWALL_VER_TILES
FIREWALL_HOR_SIZE = math.ceil(PLAY_WIDTH / FIREWALL_HOR_TILE_SIZE)
FIREWALL_VER_SIZE = math.ceil(PLAY_HEIGHT / FIREWALL_VER_TILE_SIZE)

WEAPON_SIZE = 25
WEAPON_RADIUS = WEAPON_SIZE / 2
WEAPON_WIDTH = WEAPON_SIZE
WEAPON_HEIGHT = WEAPON_SIZE

# Factor based on feeling. Is this really some crude application of intertia physics?
# TODO: Brush up 20+ year old physics/math and do this properly. It could improve the feeling of the steering.`
PHYSICS_SCALE = 0.01

# Screen width is 28 mm, resolution 128, i.e.:
PX_PER_M = 4571
