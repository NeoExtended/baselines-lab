import logging

import numpy as np
import tensorflow as tf
from stable_baselines.common import tf_util, tf_layers
from stable_baselines.common.buffers import ReplayBuffer
from stable_baselines.common.input import observation_input
from stable_baselines.common.running_mean_std import RunningMeanStd
from stable_baselines.common.vec_env import VecEnvWrapper


def small_convnet(x, activ = tf.nn.relu, **kwargs):
    layer_1 = activ(tf_layers.conv(x, 'c1', n_filters=32, filter_size=8, stride=4, init_scale=np.sqrt(2), **kwargs))
    layer_2 = activ(tf_layers.conv(layer_1, 'c2', n_filters=64, filter_size=4, stride=2, init_scale=np.sqrt(2), **kwargs))
    layer_3 = activ(tf_layers.conv(layer_2, 'c3', n_filters=64, filter_size=3, stride=1, init_scale=np.sqrt(2), **kwargs))
    layer_3 = tf_layers.conv_to_fc(layer_3)
    return tf_layers.linear(layer_3, 'fc1', n_hidden=512, init_scale=np.sqrt(2))


class CuriosityWrapper(VecEnvWrapper):

    def __init__(self, env, network: str = "cnn", intrinsic_reward_weight: float = 1.0, buffer_size: int = 65536, train_freq: int = 16384, gradient_steps: int = 4,
                 batch_size: int = 4096, learning_starts: int = 100, filter_end_of_episode: bool = True, filter_reward: bool = False, normalize_obs: bool = True,
                 gamma: float = 0.99, learning_rate: float = 0.0001):
        """

        :param env: (gym.Env) Environment to wrap.
        :param network: (str) Network type. Can be a "cnn" or a "mlp".
        :param intrinsic_reward_weight: (float) Weight for the intrinsic reward.
        :param buffer_size: (int) Size of the replay buffer for predictor training.
        :param train_freq: (int) Frequency of predictor training in steps.
        :param gradient_steps: (int) Number of optimization epochs.
        :param batch_size: (int) Number of samples to draw from the replay buffer per optimization epoch.
        :param learning_starts: (int) Number of steps to wait before training the predictor for the first time.
        :param filter_end_of_episode: (bool) Weather or not to filter end of episode signals (dones).
        :param filter_reward: (bool) Weather or not to filter extrinsic reward from the environment.
        :param normalize_obs: (bool) Weather or not to normalize and clip obs for the target/predictor network. Note that obs returned will be unaffected.
        :param gamma: (float) Reward discount factor for intrinsic reward normalization.
        :param learning_rate: (float) Learning rate for the Adam optimizer of the predictor network.
        """
        super().__init__(env)

        self.network_type = network
        self.buffer = ReplayBuffer(buffer_size)
        self.train_freq = train_freq
        self.gradient_steps = gradient_steps
        self.batch_size = batch_size
        self.learning_starts = learning_starts
        self.intrinsic_reward_weight = intrinsic_reward_weight
        self.filter_end_of_episode = filter_end_of_episode
        self.filter_extrinsic_reward = filter_reward
        self.clip_obs = 5
        self.norm_obs = normalize_obs
        self.gamma = gamma
        self.learning_rate = learning_rate

        self.epsilon = 1e-8
        self.int_rwd_rms = RunningMeanStd(shape=(), epsilon=self.epsilon)
        self.obs_rms = RunningMeanStd(shape=self.observation_space.shape)
        self.ret = np.zeros(self.num_envs) # discounted return

        self.updates = 0
        self.steps = 0
        self.last_action = None
        self.last_obs = None
        self.last_update = 0

        self._setup_model()

    def _setup_model(self):
        self.graph = tf.Graph()

        with self.graph.as_default():
            self.sess = tf_util.make_session(num_cpu=None, graph=self.graph)
            self.observation_ph, self.processed_obs = observation_input(self.venv.observation_space, scale=(self.network_type == "cnn"))

            with tf.variable_scope("target_model"):
                self.target_network = small_convnet(self.processed_obs, tf.nn.leaky_relu)
                #self.target_network = tf_layers.linear(self.target_network, "out", 512)

            with tf.variable_scope("predictor_model"):
                self.predictor_network = tf.nn.relu(small_convnet(self.processed_obs, tf.nn.leaky_relu))
                self.predictor_network = tf.nn.relu(tf_layers.linear(self.predictor_network, "fc2", 512))
                self.predictor_network = tf_layers.linear(self.predictor_network, "out", 512)

            with tf.name_scope("loss"):
                self.int_reward = tf.reduce_mean(tf.square(tf.stop_gradient(self.target_network) - self.predictor_network), axis=1)
                self.aux_loss = tf.reduce_mean(tf.square(tf.stop_gradient(self.target_network) - self.predictor_network))

            with tf.name_scope("train"):
                self.optimizer = tf.train.AdamOptimizer(self.learning_rate)
                self.training_op = self.optimizer.minimize(self.aux_loss)

            tf.global_variables_initializer().run(session=self.sess)

    def reset(self):
        obs = self.venv.reset()
        self.last_obs = obs
        return obs

    def step_async(self, actions):
        super().step_async(actions)
        self.last_action = actions
        self.steps += self.num_envs

    def step_wait(self):
        obs, rews, dones, infos = self.venv.step_wait()

        self.buffer.extend(self.last_obs, self.last_action, rews, obs, dones)

        if self.filter_extrinsic_reward:
            rews = np.zeros(rews.shape)
        if self.filter_end_of_episode:
            dones = np.zeros(dones.shape)

        self.obs_rms.update(obs)
        obs_n = self.normalize_obs(obs)

        target, predictor, loss = self.sess.run([self.target_network, self.predictor_network, self.int_reward], {self.observation_ph : obs_n})

        self.update_mean(loss)
        intrinsic_reward = np.array(loss) / np.sqrt(self.int_rwd_rms.var + self.epsilon)

        reward = np.squeeze(rews + self.intrinsic_reward_weight * intrinsic_reward)

        if self.steps > self.learning_starts and self.steps - self.last_update > self.train_freq:
            self.updates += 1
            self.last_update = self.steps
            self.learn()

        return obs, reward, dones, infos

    def close(self):
        VecEnvWrapper.close(self)

    def learn(self):
        total_loss = 0
        for _ in range(self.gradient_steps):
            obs_batch, act_batch, rews_batch, next_obs_batch, done_mask = self.buffer.sample(self.batch_size)
            obs_batch = self.normalize_obs(obs_batch)
            test = self.sess.run(self.aux_loss, {self.observation_ph : obs_batch})
            train, loss = self.sess.run([self.training_op, self.aux_loss], {self.observation_ph : obs_batch})
            total_loss += loss
        logging.info("Trained predictor. Avg loss: {}".format(total_loss / self.gradient_steps))

    def update_mean(self, reward):
        self.ret = self.gamma * self.ret + reward
        self.int_rwd_rms.update(self.ret)

    def normalize_obs(self, obs: np.ndarray) -> np.ndarray:
        """
        Normalize observations using observations statistics.
        Calling this method does not update statistics.
        """
        if self.norm_obs:
            obs = np.clip((obs - self.obs_rms.mean) / np.sqrt(self.obs_rms.var + self.epsilon),
                          -self.clip_obs,
                          self.clip_obs)
        return obs