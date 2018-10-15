# Candidate Models for Brain-Score: Which Artificial Neural Network is most Brain-Like?

Candidate models to evaluate on brain measurements, i.e. neural and behavioral recordings.
Brain recordings are packaged in [Brain-Score](https://github.com/dicarlolab/brain-score).


## Quick setup

Recommended for most users. Use as a library.

```
# PyTorch -- current version has trouble when installed through pip. Install by hand, e.g. use the following for Python3.6-cpu or conda.
pip install http://download.pytorch.org/whl/cpu/torch-0.4.1-cp36-cp36m-linux_x86_64.whl
pip install torchvision
# Brain-Score and Candidate-Models (this framework)
pip install --process-dependency-links git+https://github.com/dicarlolab/brain-score
pip install --process-dependency-links git+https://github.com/dicarlolab/candidate_models
```

To contribute code to this framework, see the [Development Setup](#development-setup).


## Usage
```bash
PYTHONPATH=. python candidate_models --model alexnet
```

During first-time use, ImageNet validation images (9.8 GB) will be downloaded, so give it a couple of minutes.

See the [examples](examples/) for more elaborate examples.


### Environment variables
Environment variables are prefixed with `CM_`.

| Variable               | Description                                                  |
|------------------------|--------------------------------------------------------------|
| CM_HOME                | path to framework root                                       |
| CM_IMAGENET_PATH       | path to ImageNet file containing the validation image set    |
| CM_TSLIM_WEIGHTS_DIR   | path to stored weights for TensorFlow/research/slim models   |


## Development setup

Only necessary if you plan to change code.

1. Clone the Git repository to wherever you keep repositories:
    * `cd ~/dev`
    * `git clone git@github.com:dicarlolab/candidate_models.git`
3. Create and activate a Conda environment with relevant packages:
    * `conda env create -f environment.yml`
    * `conda activate candidate-models`


## Troubleshooting
<details>
<summary>Could not find a version that satisfies the requirement brain-score</summary>

pip has trouble when dependency links are private repositories (as is the case now for brain-score).
To circumvent, install brain-score by hand before installing candidate_models:
`pip install --process-dependency-links git+https://github.com/dicarlolab/brain-score`.
</details>

<details>
<summary>Could not find a version that satisfies the requirement tensorflow</summary>

TensorFlow doesn't always catch up with newer Python versions.
For instance, if you have Python 3.7 (check with `python -V`), TensorFlow might only work up to Python 3.6.
If you're using conda, it usually installs the very newest version of Python.
To fix, downgrade python: `conda install python=3.6`.
</details>

<details>
<summary>Failed to build pytorch</summary>

Some versions of PyTorch cannot be installed via pip (e.g. CPU).
Instead, you need to build pytorch from their provided wheel.
Check [the website](https://pytorch.org/) for installation instructions, right now they are (e.g. for Linux, Python 3.6, no CUDA):
`pip install http://download.pytorch.org/whl/cpu/torch-0.4.1-cp36-cp36m-linux_x86_64.whl &&
pip install torchvision`.
Or just use conda, e.g., for CPU: `conda install pytorch-cpu torchvision-cpu -c pytorch`
</details>

<details>
<summary>No module named `nets` / `preprocessing`</summary>
You probably haven't installed TensorFlow/research/slim.
Follow the instructions [here](https://github.com/tensorflow/models/tree/master/research/slim#Install).
</details>

<details>
<summary>ImportError: cannot import name '_obtain_input_shape'</summary>

keras_squeezenet unfortunately does not run with keras > 2.2.0.
To fix, `pip install keras==2.2.0`.
</details>

<details>
<summary>tensorflow.python.framework.errors_impl.FailedPreconditionError: Error while reading resource variable</summary>

If this happened when running a keras model, your tensorflow and keras versions are probably incompatible.
See the setup.py for which versions are supported.
</details>
