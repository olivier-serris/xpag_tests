import os
import numpy as np
import gymnasium as gym
import mediapy as media
from typing import Callable
import joblib
import jax
from brax import envs
from brax.io import html
from IPython import display
from IPython.display import HTML
from PIL import Image, ImageDraw
import ipywidgets


def mujoco_notebook_replay(load_dir: str):
    """
    Episode replay for mujoco environments.
    """

    class DownloadButton(ipywidgets.Button):
        """Download button with dynamic content

        The content is generated using a callback when the button is clicked.
        """

        def __init__(self, contents: Callable[[], str], **kwargs):
            super(DownloadButton, self).__init__(**kwargs)
            self.contents = contents
            self.on_click(self.__on_click)

        def __on_click(self, b):
            descr = self.description
            filepath = self.contents(self)
            self.description = descr
            if filepath is not None:
                print(f"Saved to: {filepath}")

    env_name = str(
        np.loadtxt(os.path.join(load_dir, "episode", "env_name.txt"), dtype="str")
    )
    env_replay = gym.make(env_name, render_mode="rgb_array")
    env_replay.reset()
    qpos = np.load(os.path.join(load_dir, "episode", "qpos.npy"))
    qvel = np.load(os.path.join(load_dir, "episode", "qvel.npy"))

    img_dict = {}

    play = ipywidgets.Play(
        value=0,
        min=0,
        max=len(qpos) - 1,
        step=1,
        description="Press play",
        disabled=False,
    )

    def compute_image(step):
        env_replay.set_state(qpos[step], qvel[step])
        img_ = Image.fromarray(env_replay.render())
        ImageDraw.Draw(img_).text((0, 0), f"step: {step}", (255, 255, 255))
        return img_

    def display_sequence(slider_):
        def _show(step):
            if step in img_dict:
                return img_dict[step]
            else:
                img_dict[step] = compute_image(step)
                return img_dict[step]

        return ipywidgets.interact(_show, step=slider_)

    slider = ipywidgets.IntSlider(
        min=0,
        max=len(qpos) - 1,
        step=1,
        value=0,
        readout=True,
        layout=ipywidgets.Layout(width="400px"),
    )
    ipywidgets.jslink((play, "value"), (slider, "value"))
    display.display(ipywidgets.HBox([play]))
    display_sequence(slider)

    def create_gif(button):
        latest_percent = 0
        for step in range(len(qpos)):
            new_percent = min(int(step / len(qpos) * 100.0), 99)
            if new_percent > latest_percent:
                latest_percent = new_percent
                button.description = f"{latest_percent}%"
            if step not in img_dict:
                img_dict[step] = compute_image(step)
        button.description = "saving gif..."
        img_dict[0].save(
            os.path.join(load_dir, "episode", "episode.gif"),
            format="gif",
            append_images=[img_dict[k] for k in range(1, len(qpos))],
            save_all=True,
            duration=env_replay.model.opt.timestep * env_replay.frame_skip * len(qpos),
            loop=0,
        )
        return os.path.join(load_dir, "episode", "episode.gif")

    def create_mp4(button):
        latest_percent = 0
        for step in range(len(qpos)):
            new_percent = min(int(step / len(qpos) * 100.0), 99)
            if new_percent > latest_percent:
                latest_percent = new_percent
                button.description = f"{latest_percent}%"
            if step not in img_dict:
                img_dict[step] = compute_image(step)
        button.description = "generating mp4..."
        imgs = []
        for i in range(len(qpos)):
            imgs.append(np.array(img_dict[i]))
        media.show_video(
            imgs, fps=1.0 / (env_replay.model.opt.timestep * env_replay.frame_skip)
        )

    display.display(
        ipywidgets.widgets.HBox(
            (
                DownloadButton(contents=create_gif, description="Generate gif"),
                DownloadButton(contents=create_mp4, description="Generate mp4"),
            )
        )
    )


def brax_notebook_replay(load_dir: str):
    """
    Episode replay for brax environments.
    """
    env_name = str(
        np.loadtxt(os.path.join(load_dir, "episode", "env_name.txt"), dtype="str")
    )
    env = envs.create(env_name=env_name)
    with open(os.path.join(load_dir, "episode", "states.joblib"), "rb") as f:
        states = joblib.load(f)
    episode = [
        jax.tree_util.tree_map(lambda x: x.squeeze(axis=0), st.pipeline_state)
        for st in states
    ]
    display.display(HTML(html.render(env.sys.replace(dt=env.dt), episode)))
