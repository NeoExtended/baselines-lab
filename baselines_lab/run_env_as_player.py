import time

import keyboard
from stable_baselines.common import make_vec_env

from baselines_lab.env.gym_maze.envs import MazeBase  # noqa # pylint: disable=unused-import

env = make_vec_env("Maze0318Continuous-v0", n_envs=1)
obs = env.reset()

for i in range(1000):
    env.render(mode="human")
    action = 0
    while True:
        up = keyboard.is_pressed("up")
        down = keyboard.is_pressed("down")
        left = keyboard.is_pressed("left")
        right = keyboard.is_pressed("right")

        if up or down or left or right:
            break

        time.sleep(0.001)
    if up:
        action = 6
    if down:
        action = 2
    if left:
        action = 4
    if right:
        action = 0

    obs, rewards, dones, info = env.step([action])
    #print(rewards)