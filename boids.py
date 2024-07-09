import pygame
import pygame_gui
import random
import math

pygame.init()
pygame.display.set_caption('Boids Simulation')
width, height = 1400, 850
screen = pygame.display.set_mode((width, height))
manager = pygame_gui.UIManager((width, height))

# set up sliders
coherence_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 40), (200, 30)),
                                                          start_value=0.005,
                                                          value_range=(0, 0.1),
                                                          manager=manager)
separation_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 100), (200, 30)),
                                                           start_value=0.05,
                                                           value_range=(0, 0.1),
                                                           manager=manager)
alignment_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 160), (200, 30)),
                                                          start_value=0.05,
                                                          value_range=(0, 0.1),
                                                          manager=manager)
visual_range_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((10, 220), (200, 30)),
                                                             start_value=75,
                                                             value_range=(20, 150),
                                                             manager=manager)

# set up labels
coherence_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, 40), (100, 30)),
                                              text="Coherence",
                                              manager=manager)
separation_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, 100), (100, 30)),
                                               text="Separation",
                                               manager=manager)
alignment_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, 160), (100, 30)),
                                              text="Alignment",
                                              manager=manager)
visual_range_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, 220), (100, 30)),
                                                 text="Visual Range",
                                                 manager=manager)

num_boids = 100

boids = []

# initialize the boids
def init_boids():
    for _ in range(num_boids):
        boids.append({
            'x': random.random() * width,
            'y': random.random() * height,
            'dx': random.random() * 10 - 5,
            'dy': random.random() * 10 - 5,
            'history': [],
        })

# calculate distance between two boids
def distance(boid1, boid2):
    return math.sqrt((boid1['x'] - boid2['x']) ** 2 + (boid1['y'] - boid2['y']) ** 2)

# constrain a boid to within the window
def keep_within_bounds(boid):
    margin = 200
    turn_factor = 1

    if boid['x'] < margin:
        boid['dx'] += turn_factor
    if boid['x'] > width - margin:
        boid['dx'] -= turn_factor
    if boid['y'] < margin:
        boid['dy'] += turn_factor
    if boid['y'] > height - margin:
        boid['dy'] -= turn_factor

# fly towards the center of mass
def fly_towards_center(boid, coherence_factor, visual_range):
    centerX, centerY = 0, 0
    num_neighbors = 0

    for other_boid in boids:
        if distance(boid, other_boid) < visual_range:
            centerX += other_boid['x']
            centerY += other_boid['y']
            num_neighbors += 1

    if num_neighbors:
        centerX /= num_neighbors
        centerY /= num_neighbors
        boid['dx'] += (centerX - boid['x']) * coherence_factor
        boid['dy'] += (centerY - boid['y']) * coherence_factor

# avoid other boids that are close
def avoid_others(boid, separation_factor, visual_range):
    min_distance = 10
    moveX, moveY = 0, 0

    for other_boid in boids:
        if other_boid != boid:
            if distance(boid, other_boid) < visual_range:
                moveX += boid['x'] - other_boid['x']
                moveY += boid['y'] - other_boid['y']

    boid['dx'] += moveX * separation_factor
    boid['dy'] += moveY * separation_factor

# match velocity with nearby boids
def match_velocity(boid, alignment_factor, visual_range):
    avgDX, avgDY = 0, 0
    num_neighbors = 0

    for other_boid in boids:
        if distance(boid, other_boid) < visual_range:
            avgDX += other_boid['dx']
            avgDY += other_boid['dy']
            num_neighbors += 1

    if num_neighbors:
        avgDX /= num_neighbors
        avgDY /= num_neighbors
        boid['dx'] += (avgDX - boid['dx']) * alignment_factor
        boid['dy'] += (avgDY - boid['dy']) * alignment_factor

# limit the speed
def limit_speed(boid):
    speed_limit = 15
    speed = math.sqrt(boid['dx'] ** 2 + boid['dy'] ** 2)

    if speed > speed_limit:
        boid['dx'] = (boid['dx'] / speed) * speed_limit
        boid['dy'] = (boid['dy'] / speed) * speed_limit

DRAW_TRAIL = True

def draw_boid(screen, boid):
    angle = math.atan2(boid['dy'], boid['dx'])
    points = [
        (boid['x'], boid['y']),
        (boid['x'] - 15 * math.cos(angle - math.pi / 6), boid['y'] - 15 * math.sin(angle - math.pi / 6)),
        (boid['x'] - 15 * math.cos(angle + math.pi / 6), boid['y'] - 15 * math.sin(angle + math.pi / 6))
    ]
    pygame.draw.polygon(screen, (85, 140, 244), points)

    if DRAW_TRAIL:
        if len(boid['history']) > 1:
            pygame.draw.lines(screen, (85, 140, 244, 102), False, boid['history'], 1)

# main animation loop
def animation_loop():
    global width, height
    clock = pygame.time.Clock()
    running = True

    while running:
        time_delta = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.process_events(event)

        manager.update(time_delta)

        screen.fill((0, 0, 0))

        coherence_factor = coherence_slider.get_current_value()
        separation_factor = separation_slider.get_current_value()
        alignment_factor = alignment_slider.get_current_value()
        visual_range = visual_range_slider.get_current_value()

        for boid in boids:
            fly_towards_center(boid, coherence_factor, visual_range)
            avoid_others(boid, separation_factor, visual_range)
            match_velocity(boid, alignment_factor, visual_range)
            limit_speed(boid)
            keep_within_bounds(boid)

            boid['x'] += boid['dx']
            boid['y'] += boid['dy']
            boid['history'].append((boid['x'], boid['y']))
            boid['history'] = boid['history'][-50:]

            draw_boid(screen, boid)

        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    init_boids()
    animation_loop()
