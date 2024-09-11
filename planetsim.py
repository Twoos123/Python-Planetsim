import pygame
import math

pygame.init()

# Updated window size
WIDTH, HEIGHT = 2000, 1200
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulation")

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

FONT = pygame.font.SysFont("Arial", 14)  # Changed font to Arial

class Planet:
    AU = 149.6e6 * 1000
    G = 6.67428e-11
    TIMESTEP = 3600 * 24  # 1 day in seconds

    def __init__(self, x, y, radius, color, mass, name):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.name = name

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0
        self.selected = False

    def draw(self, win, scale, offset_x, offset_y):
        x = self.x * scale + WIDTH / 2 + offset_x
        y = self.y * scale + HEIGHT / 2 + offset_y

        # Draw the orbit path
        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                px, py = point
                px = px * scale + WIDTH / 2 + offset_x
                py = py * scale + HEIGHT / 2 + offset_y
                updated_points.append((px, py))

            pygame.draw.lines(win, self.color, False, updated_points, 2)

        # Draw the planet
        pygame.draw.circle(win, self.color, (int(x), int(y)), self.radius)

        # Draw distance to the sun for planets other than the sun
        if not self.sun:
            distance_text = FONT.render(f"{round(self.distance_to_sun / 1000, 1)} km", True, WHITE)
            win.blit(distance_text, (int(x - distance_text.get_width() / 2), int(y - distance_text.get_height() / 2)))
        
        # Draw name and additional info if planet is selected
        if self.selected:
            info_text = FONT.render(f"{self.name}: {round(self.distance_to_sun / 1000, 1)} km, Mass: {self.mass / 1e24:.2e} kg", True, WHITE)
            win.blit(info_text, (int(x - info_text.get_width() / 2), int(y - self.radius - 20)))


    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))


def main():
    run = True
    clock = pygame.time.Clock()

    # Create the sun with a smaller radius
    sun = Planet(0, 0, 20, YELLOW, 1.98892 * 10 ** 30, "Sun")
    sun.sun = True

    # Add all planets in the solar system with adjusted positions
    planets = [
        Planet(0.387 * Planet.AU, 0, 6, DARK_GREY, 3.30 * 10 ** 23, "Mercury"),
        Planet(0.723 * Planet.AU, 0, 12, WHITE, 4.8685 * 10 ** 24, "Venus"),
        Planet(1 * Planet.AU, 0, 16, BLUE, 5.9742 * 10 ** 24, "Earth"),
        Planet(1.524 * Planet.AU, 0, 12, RED, 6.39 * 10 ** 23, "Mars"),
        Planet(5.203 * Planet.AU, 0, 70, ORANGE, 1.898 * 10 ** 27, "Jupiter"),
        Planet(9.537 * Planet.AU, 0, 60, BROWN, 5.683 * 10 ** 26, "Saturn"),
        Planet(19.191 * Planet.AU, 0, 25, LIGHT_BLUE, 8.681 * 10 ** 25, "Uranus"),
        Planet(30.068 * Planet.AU, 0, 24, BLUE, 1.024 * 10 ** 26, "Neptune")
    ]

    # Set velocities for planets
    planets[0].y_vel = -47.4 * 1000  # Mercury
    planets[1].y_vel = -35.02 * 1000  # Venus
    planets[2].y_vel = 29.783 * 1000   # Earth
    planets[3].y_vel = 24.077 * 1000   # Mars
    planets[4].y_vel = 13.07 * 1000    # Jupiter
    planets[5].y_vel = 9.69 * 1000     # Saturn
    planets[6].y_vel = 6.81 * 1000     # Uranus
    planets[7].y_vel = 5.43 * 1000     # Neptune

    planets.append(sun)  # Add the sun last so it appears on top

    scale = 100 / Planet.AU  # Initial scale factor
    offset_x, offset_y = 0, 0
    selected_planet = None
    paused = False

    while run:
        clock.tick(60)
        WIN.fill(BLACK)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    scale *= 1.1  # Zoom in
                elif event.key == pygame.K_MINUS:
                    scale /= 1.1  # Zoom out
                elif event.key == pygame.K_p:  # Pause/Play
                    paused = not paused
                elif event.key == pygame.K_UP:
                    offset_y -= 10  # Move up (fixed direction)
                elif event.key == pygame.K_DOWN:
                    offset_y += 10  # Move down (fixed direction)
                elif event.key == pygame.K_LEFT:
                    offset_x += 10  # Move left (fixed direction)
                elif event.key == pygame.K_RIGHT:
                    offset_x -= 10  # Move right (fixed direction)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    mouse_x -= WIDTH / 2
                    mouse_y -= HEIGHT / 2
                    mouse_x /= scale
                    mouse_y /= scale
                    mouse_x -= offset_x
                    mouse_y -= offset_y

                    # Check if a planet is clicked
                    for planet in planets:
                        distance_x = mouse_x - planet.x
                        distance_y = mouse_y - planet.y
                        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)
                        if distance < planet.radius:
                            selected_planet = planet
                            planet.selected = True
                        else:
                            planet.selected = False

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    selected_planet = None

            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Scrolling up
                    scale *= 1.1  # Zoom in
                elif event.y < 0:  # Scrolling down
                    scale /= 1.1  # Zoom out

        # Update and draw planets
        for planet in planets:
            if not paused:
                planet.update_position(planets)
            planet.draw(WIN, scale, offset_x, offset_y)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
