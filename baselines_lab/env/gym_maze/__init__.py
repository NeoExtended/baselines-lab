from gym.envs.registration import register

from baselines_lab.env.gym_maze.maze_generators import BufferedRRTGenerator

register(id="Maze0122Discrete-v0",
         entry_point="baselines_lab.env.gym_maze.envs:MazeBase",
         max_episode_steps=5000,
         kwargs={'instance': '../mapdata/map0122.csv',
                 'goal': [96, 204],
                 'goal_range': 15,
                 'reward_generator': "goal"})

register(id="Maze0122Continuous-v0",
         entry_point="baselines_lab.env.gym_maze.envs:MazeBase",
         max_episode_steps=5000,
         kwargs={'instance': '../mapdata/map0122.csv',
                 'goal': [96, 204],
                 'goal_range': 15,
                 'reward_generator': "continuous"})

register(id="Maze0318Discrete-v0",
         entry_point="baselines_lab.env.gym_maze.envs:MazeBase",
         max_episode_steps=2000,
         kwargs={'instance': '../mapdata/map0318.csv',
                 'goal': [82, 80],
                 'goal_range': 10,
                 'reward_generator': "goal"})

register(id="Maze0318Continuous-v0",
         entry_point="baselines_lab.env.gym_maze.envs:MazeBase",
         max_episode_steps=2000,
         kwargs={'instance': '../mapdata/map0318.csv',
                 'goal': [82, 80],
                 'goal_range': 10,
                 'reward_generator': "continuous"})

register(id="Maze0318Continuous-v1",
         entry_point="baselines_lab.env.gym_maze.envs:MazeBase",
         max_episode_steps=2000,
         kwargs={'instance': '../mapdata/map0318.csv',
                 'goal': [82, 80],
                 'goal_range': 10,
                 'robot_count': -1,
                 'reward_generator': "goal"})

register(id="Maze0318Continuous-v2",
         entry_point="baselines_lab.env.gym_maze.envs:MazeBase",
         max_episode_steps=2000,
         kwargs={'instance': '../mapdata/map0318.csv',
                 'goal': None,
                 'goal_range': 10,
                 'reward_generator': "continuous"})

register(id="Maze0318Continuous-v3",
         entry_point="baselines_lab.env.gym_maze.envs:MazeBase",
         max_episode_steps=2000,
         kwargs={'instance': '../mapdata/map0318.csv',
                 'goal': None,
                 'goal_range': 10,
                 'robot_count': -1,
                 'reward_generator': "continuous"})

register(id="Maze0318Continuous-v4",
         entry_point="baselines_lab.env.gym_maze.envs:FuzzyMaze",
         max_episode_steps=2000,
         kwargs={'instance': '../mapdata/map0318.csv',
                 'goal': [82, 80],
                 'goal_range': 10,
                 'reward_generator': "continuous"})

register(id="Maze0518Discrete-v0",
         entry_point="baselines_lab.env.gym_maze.envs:MazeBase",
         max_episode_steps=2400,
         kwargs={'instance': '../mapdata/map0518.csv',
                 'goal': [60, 130],
                 'goal_range': 10,
                 'reward_generator': "goal"})

register(id="Maze0518Continuous-v0",
         entry_point="baselines_lab.env.gym_maze.envs:MazeBase",
         max_episode_steps=2400,
         kwargs={'instance': '../mapdata/map0518.csv',
                 'goal': [60, 130],
                 'goal_range': 10,
                 'reward_generator': "continuous"})

register(id="Maze0518Continuous-v2",
         entry_point="baselines_lab.env.gym_maze.envs:MazeBase",
         max_episode_steps=2400,
         kwargs={'instance': '../mapdata/map0518.csv',
                 'goal': None,
                 'goal_range': 10,
                 'reward_generator': "continuous"})

register(id="RandomMazeDiscrete-v0",
         entry_point="baselines_lab.env.gym_maze.envs:MazeBase",
         max_episode_steps=2000,
         kwargs={'instance': BufferedRRTGenerator,
                 'goal': None,
                 'goal_range': 10,
                 'reward_generator': "goal"})

register(id="PhysicalMaze0318Continuous-v0",
         entry_point="baselines_lab.env.gym_maze.envs:PhysicalMaze",
         max_episode_steps=2000,
         kwargs={'instance': '../mapdata/map0318.csv',
                 'goal': [82, 80],
                 'goal_range': 10,
                 'reward_generator': "continuous"})

register(id="VesselMaze01Continuous-v0",
         entry_point="baselines_lab.env.gym_maze.envs:MazeBase",
         max_episode_steps=2000,
         kwargs={'instance': '../mapdata/small_vessel.csv',
                 'goal': [95, 60],
                 'goal_range': 10,
                 'reward_generator': "continuous"})
