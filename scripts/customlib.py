import pygame, os
from pygame.locals import *
from pygame import gfxdraw


# RESOURCES AND PYGAME

def resourcePath(path: str) -> str: # Private
    return os.path.join(os.path.dirname(__file__), "..", "resources", path)

def loadImage(imagePath: str) -> pygame.Surface:
    return pygame.image.load(resourcePath("images/" + imagePath)).convert_alpha()

def loadFont(fontPath: str, size: int) -> pygame.font.Font:
    return pygame.font.Font(resourcePath("fonts/" + fontPath), size)

def loadFile(txtPath: str, options: str):
    return open(resourcePath("texts/" + txtPath), options)


def blitCenter(surface: pygame.Surface, image: pygame.Surface, center: tuple) -> None:
    surface.blit(image, (int(center[0] - image.get_width() / 2), int(center[1] - image.get_height() / 2)))

def blitSurfaceCenter(surface: pygame.Surface, image: pygame.Surface, offset: tuple = (0, 0)) -> None:
    surface.blit(image, mulVector(subVector(surface.get_size(), image.get_size()), 0.5))

def blitSurfaceCenterX(surface: pygame.Surface, image: pygame.Surface, x: int, offset: int = 0) -> None:
    surface.blit(image, (x, (surface.get_height() - image.get_height()) / 2 + offset))

def blitRectCenter(surface: pygame.Surface, image: pygame.Surface, rect: tuple, offset: tuple = (0, 0)) -> None:
    surface.blit(image, addVector(addVector(mulVector(subVector(rect[2:4], image.get_size()), 0.5), rect[0:2]), offset))

def drawRectCenter(surface: pygame.Surface, color: tuple, center: tuple, size: tuple) -> None:
    pygame.draw.rect(surface, color, addVector(center, mulVector(size, -0.5)) + size)

def drawCircle(surface: pygame.Surface, center: tuple, radius: int, color: tuple) -> None:
    gfxdraw.aacircle(surface, center[0], center[1], radius, color)
    gfxdraw.filled_circle(surface, center[0], center[1], radius, color)

def drawRoundRectTopLeft(surface: pygame.Surface, topLeft: tuple, size: tuple, radius: int, color: tuple) -> None:
    drawCircle(surface, (topLeft[0] + radius + 1, topLeft[1] + radius), radius, color)
    drawCircle(surface, (topLeft[0] + size[0] - radius - 2, topLeft[1] + radius), radius, color)
    drawCircle(surface, (topLeft[0] + radius + 1, topLeft[1] + size[1] - radius - 1), radius, color)
    drawCircle(surface, (topLeft[0] + size[0] - radius - 2, topLeft[1] + size[1] - radius - 1), radius, color)
    pygame.draw.rect(surface, color, (topLeft[0], topLeft[1] + radius, size[0], size[1] - 2 * radius))
    pygame.draw.rect(surface, color, (topLeft[0] + radius, topLeft[1], size[0] - 2 * radius, size[1]))

def drawRoundRectCenter(surface: pygame.Surface, center: tuple, size: tuple, radius: int, color: tuple) -> None:
    drawRoundRectTopLeft(surface, addVector(center, mulVector(size, -0.5)), size, radius, color)

def drawShrunkenRect(surface: pygame.Surface, color: tuple, rect: tuple, border: int) -> None:
    pygame.draw.rect(surface, color, (rect[0] + border, rect[1] + border, rect[2] - border * 2, rect[3] - border * 2))

def blitCircle(surface: pygame.Surface, center: tuple, radius: int, color: tuple, alpha: int = 255) -> None:
    s = pygame.Surface(radius * 2 - 1, radius * 2 - 1, SRCALPHA).convert_alpha()
    drawCircle(s, unitVector(2, radius - 1), radius, color)
    s.set_alpha(alpha)
    blitCenter(surface, s, center)

def blitRoundRectTopLeft(surface: pygame.Surface, topLeft: tuple, size: tuple, radius: int, color: tuple, alpha: int = 255) -> None:
    s = pygame.Surface(size, SRCALPHA).convert_alpha()
    drawRoundRectTopLeft(s, (0, 0), size, radius, color)
    s.set_alpha(alpha)
    surface.blit(s, topLeft)

def blitRoundRectCenter(surface: pygame.Surface, center: tuple, size: tuple, radius: int, color: tuple, alpha: int = 255) -> None:
    blitRoundRectTopLeft(surface, addVector(center, mulVector(size, -0.5)), size, radius, color, alpha)

def fontSurface(font: pygame.font.Font, text: str, color: tuple, alpha: int = 255) -> pygame.Surface:
    s = font.render(text, True, color).convert_alpha()
    s.set_alpha(alpha)
    return s

# MATH

def unitVector(size: int, scalar: float) -> tuple:
    return tuple([scalar for i in range(size)])

def addVector(v1: tuple, v2: tuple) -> tuple:
    return tuple([v1[i] + v2[i] for i in range(len(v1))])

def subVector(v1: tuple, v2: tuple) -> tuple:
    return tuple([v1[i] - v2[i] for i in range(len(v1))])

def mulVector(vector: tuple, scalar: float) -> tuple:
    return tuple([comp * scalar for comp in vector])

def intVector(v: tuple) -> tuple:
    return tuple([int(comp) for comp in v])

def roundVector(v: tuple) -> tuple:
    return tuple([round(comp) for comp in v])

def lerpVector(current: tuple, target: tuple, factor: float) -> tuple:
    return tuple([current[i] + (target[i] - current[i]) * factor for i in range(len(current))])


def pointInRectCenter(center: tuple, size: tuple, point: tuple) -> bool:
    return abs(point[0] - center[0]) <= size[0] / 2 and abs(point[1] - center[1]) <= size[1] / 2

def pointInRectTopLeft(topLeft: tuple, size: tuple, point: tuple) -> bool:
    return point[0] >= topLeft[0] and point[1] >= topLeft[1] and point[0] <= topLeft[0] + size[0] and point[1] <= topLeft[1] + size[1]


# COLOR

def colorMultiply(color: tuple, factor: float) -> tuple:
    return tuple([comp * factor for comp in color])

def colorLighten(color: tuple, factor: float) -> tuple:
    return tuple([comp + (255 - comp) * factor for comp in color])


# OTHER

def flatten(l: list) -> list:
    return [x for xs in l for x in xs]