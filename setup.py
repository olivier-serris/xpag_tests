from setuptools import setup, find_packages

# Install with 'pip install -e .'

setup(
    name="xpag",
    version="0.1.0",
    author="Nicolas Perrin-Gilbert",
    description="xpag: Exploring Agents",
    url="https://github.com/perrin-isir/xpag",
    packages=find_packages(
        include=[
            "xpag",
            "xpag.*",
            "xpag.agents.*",
            "xpag.agents.jax.*",
            "xpag.buffers.*",
            "xpag.goalsetters.*",
            "xpag.plotting.*",
            "xpag.samplers.*",
            "xpag.tools.*",
            "envs",
            "envs.*",
            "envs.gym-gmazes.*",
            "envs.gym-gmazes.gym_gmazes.*",
        ]
    ),
    install_requires=[
        "psutil>=5.8.0",
        "numpy>=1.21.5",
        "matplotlib>=3.5.1",
        "joblib>=1.1.0",
        "gym>=0.22.0",
        "torch>=1.10.1",
        "mujoco_py>=2.1.2.14",
        "IPython>=8.0.1",
    ],
    license="LICENSE",
)
