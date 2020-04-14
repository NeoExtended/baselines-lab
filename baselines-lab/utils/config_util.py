"""
Defines helper functions for reading and writing the lab config file
"""

import json
import logging
import os

import yaml

from utils import util


def get_config(config_file, args):
    """
    Reads the lab config from a given file and configures it for use with to the current lab mode.
    :param config_file: (str) Path to the config file.
    :param args: (dict) parsed args dict
    :return: (dict) The parsed config file as dictionary.
    """
    config = read_config(config_file)
    config = extend_meta_data(config)
    config = clean_config(config, args)
    return config


def clean_config(config, args):
    """
    Deletes or modifies keys from the config which are not compatible with the current lab mode.
    :param config: (dict) The config dictionary
    :param args: (dict) parsed args dict
    :return: (dict) The cleaned config dictionary
    """

    if args.lab_mode == 'enjoy':
        return _clean_enjoy_config(args, config)
    elif args.lab_mode == 'train':
        _clean_train_config(config)
    elif args.lab_mode == "search":
        _clean_search_config(config)

    return config


def _clean_search_config(config):
    resume = config['search'].get("resume", False)
    if resume and isinstance(resume, bool):
        from model.checkpoints import CheckpointManager
        path = CheckpointManager.get_latest_run(config['meta']['log_dir'])
        config['search']['resume'] = path
    return config


def _clean_train_config(config):
    # Allow fast loading of recently trained agents via "last" and "best" checkpoints
    if config['algorithm'].get('trained_agent', None):
        if config['algorithm']['trained_agent'] in ['best', 'last']:
            from model.checkpoints import CheckpointManager
            path = CheckpointManager.get_latest_run(config['meta']['log_dir'])
            set_checkpoints(config, path, config['algorithm']['trained_agent'])
    if config['algorithm']['name'] in ["dqn", "ddpg"]:
        if config['env'].get('n_envs', 1) > 1:
            logging.warning("Number of envs must be 1 for dqn and ddpg! Reducing n_envs to 1.")
            config['env']['n_envs'] = 1
    return config


def _clean_enjoy_config(args, config):
    # Do not change running averages in enjoy mode
    if 'normalize' in config['env']:
        if isinstance(config['env']['normalize'], bool):
            config['env'].pop('normalize')
            config['env']['normalize'] = {'training': False}
        else:
            config['env']['normalize']['training'] = False
    # Do not train curiosity networks in enjoy mode
    if 'curiosity' in config['env']:
        if isinstance(config['env']['curiosity'], bool):
            config['env'].pop('curiosity')
            config['env']['curiosity'] = {'training': False}
        else:
            config['env']['curiosity']['training'] = False
    # Find checkpoints
    if len(args.checkpoint_path) > 0:
        set_checkpoints(config, args.checkpoint_path, args.type)
    else:
        from model.checkpoints import CheckpointManager
        path = CheckpointManager.get_latest_run(config['meta']['log_dir'])
        set_checkpoints(config, path, args.type)
    # Reduce number of envs if there are too many
    if config['env']['n_envs'] > 32:
        config['env']['n_envs'] = 32
    if args.strict:
        config['env']['n_envs'] = 1
    return config


def set_checkpoints(config, path, type):
    from model.checkpoints import CheckpointManager
    normalization = 'normalize' in config['env']
    curiosity = 'curiosity' in config['env']

    checkpoint = CheckpointManager.get_checkpoint(path, type=type)
    config['algorithm']['trained_agent'] = CheckpointManager.get_file_path(checkpoint, "model")
    if normalization:
        config['env']['normalize']['trained_agent'] = CheckpointManager.get_file_path(checkpoint, "normalization")

    if curiosity:
        config['env']['curiosity']['trained_agent'] = CheckpointManager.get_file_path(checkpoint, "curiosity")


def read_config(config_file):
    """
    Reads a config file from disc. The file must follow JSON or YAML standard.
    :param config_file: (str) Path to the config file.
    :return: (dict) A dict with the contents of the file.
    """
    file = open(config_file, "r")
    ext = os.path.splitext(config_file)[-1]

    if ext == '.json':
        config = json.load(file)
    elif ext == '.yml':
        config = yaml.load(file)
    else:
        raise NotImplementedError("File format unknown")

    file.close()
    return config


def save_config(config, path):
    """
    Saves a given lab configuration to a file.
    :param config: (dict) The lab configuration.
    :param path: (str) Desired file location.
    """
    ext = os.path.splitext(path)[-1]
    file = open(path, "w")
    if ext == '.json':
        json.dump(config, file, indent=2, sort_keys=True)
    elif ext == '.yml':
        yaml.dump(config, file, indent=2)
    file.close()


def extend_meta_data(config):
    """
    Extends the meta-data dictionary of the file to save additional information at training time.
    :param config: (dict) The config dictionary.
    :return: (dict) The updated config dictionary.
    """
    extended_info = {
        "timestamp": util.get_timestamp(),
        "random_seed": None,
    }
    config['meta'].update(extended_info)
    return config
