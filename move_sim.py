import pygame
import numpy as np
from random import randint

yellow = (153, 153, 0)
blue = (0, 0, 255)
grey = (224, 224, 224)


class Sim:

    def __init__(self, sim_width, sim_height):
        pygame.display.set_caption('MoveSim')
        self.sim_width = sim_width
        self.sim_height = sim_height
        self.simDisplay = pygame.display.set_mode((sim_width, sim_height))
        self.simDisplay.fill(grey)
        self.walls = Walls(self)
        self.frame_rate = pygame.time.Clock()
        self.update_screen()

    @staticmethod
    def update_screen():
        pygame.display.flip()

    def refresh_screen(self, num_frames=45):
        """ Refreshes entire screen. Places the background walls as well as sets the frame rate. """
        self.clock_tick(num_frames)
        self.simDisplay = pygame.display.set_mode((self.sim_width, self.sim_height))
        self.simDisplay.fill(grey)
        self.walls = Walls(self)
        self.update_screen()

    def clock_tick(self, num_frames):
        self.frame_rate.tick(num_frames)


class Walls:

    def __init__(self, sim):
        self.num_walls = 20
        self.rectangle = [None for _ in range(self.num_walls)]
        self.setup(sim)

    def setup(self, sim):
        """ Sets up the wall boundaries and draws them in the sim display.

            Will place each wall in one list to be used later.
        """
        x = sim.sim_width
        y = sim.sim_height
        n = 4 * 20  # Just used to save space in defining walls
        for i in range(0, 4):
            self.rectangle[i*4] = pygame.draw.rect(sim.simDisplay, yellow, (0, i*20 + (i+1)*((y-n)/5), x/5.4, 20))
            self.rectangle[i*4+1] = pygame.draw.rect(sim.simDisplay, yellow, (x-(x/5.4), i*20+(i+1)*((y-n)/5), x/5.4, 20))
            self.rectangle[i*4+2] = pygame.draw.rect(sim.simDisplay, yellow, (i*20+(i+1)*((x-n)/5), 0, 20, y/5.4))
            self.rectangle[i*4+3] = pygame.draw.rect(sim.simDisplay, yellow, (i*20+(i+1)*((x-n)/5), y-(y/5.4), 20, y/5.4))

        # The four outer walls that cannot be seen but outline the perimeter
        self.rectangle[16] = pygame.draw.rect(sim.simDisplay, yellow, (0, 0, x, 0))
        self.rectangle[17] = pygame.draw.rect(sim.simDisplay, yellow, (0, 0, 0, y))
        self.rectangle[18] = pygame.draw.rect(sim.simDisplay, yellow, (x, 0, 0, y))
        self.rectangle[19] = pygame.draw.rect(sim.simDisplay, yellow, (0, y, x, 0))


class Ball:

    def __init__(self, sim, ball_size=12, move_limit=25, ball_speed=(2, 2), ball_start=(500, 500)):
        self.x_change, self.y_change = ball_speed[0], ball_speed[1]
        self.x = ball_start[0]
        self.y = ball_start[1]
        self.new_x, self.new_y = self.x, self.y
        self.circle = None
        self.ball_size = ball_size
        self.move_counter = 0
        self.move_limit = move_limit
        self.x_dir, self.y_dir = 0, 0
        self.dir = ((0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1))
        self.first_time = True
        self.index = None
        self.draw(sim)

    def draw(self, sim):
        """ Draws the ball on the sim display background, then refreshes the ball to update its position. """
        self.circle = pygame.draw.circle(sim.simDisplay, blue, (self.new_x, self.new_y), self.ball_size)
        self.refresh_ball()

    def update_position(self):
        self.x = self.new_x
        self.y = self.new_y

    def refresh_ball(self):
        pygame.display.update(self.circle)

    def random_gen(self):
        """ First time, will randomly generate a direction in either 8 places.

        After that, will only randomly generate direction within the space and nearest direction on either side.

                                            (0, -1)
                                    (-1, -1)       (1, -1)
                                 (-1, 0)               (1, 0)
                                    (-1, 1)        (1, 1)
                                            (0, 1)
        """
        if self.first_time:
            self.index = randint(0, 7)
            self.x_dir = self.dir[self.index][0]
            self.y_dir = self.dir[self.index][1]
            self.first_time = False
        else:
            rand = randint(-1, 1)
            self.index = self.index+rand
            if self.index > 7:
                self.index = self.index - len(self.dir)
            elif self.index < 0:
                self.index = self.index + len(self.dir)

            self.x_dir = self.dir[self.index][0]
            self.y_dir = self.dir[self.index][1]

    def analyze_move_counter(self):
        """ If move counter reaches the move limit, then it will reset"""
        self.move_counter = self.move_counter + 1

        if self.move_counter == self.move_limit:
            self.move_counter = 0

    def analyze_direction(self, direct_hit=False, angle_x=False, angle_y=False):
        """ Analyzes direction once collision is detected"""
        if direct_hit:
            self.x_dir = self.x_dir * -1
            self.y_dir = self.y_dir * -1
            self.index = self.index + 4
        elif self.x_dir == self.y_dir and angle_x:
            self.x_dir = self.x_dir * -1
            self.index = self.index + 2
        elif self.x_dir != self.y_dir and angle_x:
            self.x_dir = self.x_dir * -1
            self.index = self.index - 2
        elif self.x_dir == self.y_dir and angle_y:
            self.y_dir = self.y_dir * -1
            self.index = self.index - 2
        elif self.x_dir != self.y_dir and angle_y:
            self.y_dir = self.y_dir * -1
            self.index = self.index + 2

    def check_collision_walls(self, sim):
        """ Will check if ball object has detected collision with any wall surface by looping through each wall"""
        for r in sim.walls.rectangle:
            if r.collidepoint(self.circle.midleft) or r.collidepoint(self.circle.midtop) or \
                    r.collidepoint(self.circle.midright) or r.collidepoint(self.circle.midbottom) or \
                    r.collidepoint(self.circle.topright) or r.collidepoint(self.circle.topleft)or \
                    r.collidepoint(self.circle.bottomright) or r.collidepoint(self.circle.bottomleft):

                # check if wall hit dead on
                if self.x_dir == 0 or self.y_dir == 0:
                    self.analyze_direction(direct_hit=True)

                # if wall hit on angle in x direction
                elif (self.x_dir == -1 and r.collidepoint(self.circle.midleft)) or \
                        (self.x_dir == 1 and r.collidepoint(self.circle.midright)):
                    self.analyze_direction(angle_x=True)

                # if wall hit on angle in y direction
                elif (self.y_dir == -1 and r.collidepoint(self.circle.midtop)) or \
                        (self.y_dir == 1 and r.collidepoint(self.circle.midbottom)):
                    self.analyze_direction(angle_y=True)

                # if wall hit on corner
                elif (r.collidepoint(self.circle.topright) and self.y_dir == -1) or \
                        (r.collidepoint(self.circle.topleft) and self.y_dir == -1) or \
                        (r.collidepoint(self.circle.bottomright) and self.y_dir == 1) or \
                        (r.collidepoint(self.circle.bottomleft) and self.y_dir == 1):
                    self.analyze_direction(direct_hit=True)

                # if collision detected, start move counter over again
                self.move_counter = 0
                return True

    def move(self, sim):
        """ Will define the move based off of direction in x and y. Will move by a step of x/y change. """

        # if no collision detected and all moves are complete/first move, start random gen
        if not self.check_collision_walls(sim) and self.move_counter == 0:
            self.random_gen()

        if self.x_dir == 1:
            self.new_x = self.x + self.x_change
        elif self.x_dir == -1:
            self.new_x = self.x - self.x_change

        if self.y_dir == 1:
            self.new_y = self.y + self.y_change
        elif self.y_dir == -1:
            self.new_y = self.y - self.y_change

        self.analyze_move_counter()
        self.draw(sim)
        self.update_position()


class Run:

    def __init__(self, width=1000, height=1000):
        pygame.init()
        self.sim = Sim(width, height)
        self.sim_time = True
        self.ball_list = []

    def ball_setup(self, num_balls=4):
        for _ in range(num_balls):
            self.ball_list.append(Ball(self.sim))

    def run_sim(self):
        while self.sim_time:
            self.sim.refresh_screen()
            for i in range(len(self.ball_list)):
                self.ball_list[i].move(self.sim)


game1 = Run()
game1.ball_setup(25)
game1.run_sim()


