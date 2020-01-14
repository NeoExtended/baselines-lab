from gym.envs.registration import register
from env.gym_maze.rewards import GoalRewardGenerator, ContinuousRewardGenerator

register(id="Maze0318Discrete-v0",
        entry_point="env.gym_maze.envs:MazeBase",
        max_episode_steps=2000,
        kwargs={'map_file':'../mapdata/map0318.csv', 'goal':[82, 80], 'goal_range':10, 'reward_generator': GoalRewardGenerator})

register(id="Maze0318Continuous-v0",
        entry_point="env.gym_maze.envs:MazeBase",
        max_episode_steps=2000,
        kwargs={'map_file':'../mapdata/map0318.csv', 'goal':[82, 80], 'goal_range':10, 'reward_generator': ContinuousRewardGenerator})