# cmakip

When working on virtual environments, Python projects can be installed with a single command invocation, for example `pip install --no-deps .` . 
Instead for CMake/C++ projects it is necessary to manually run `mkdir build && cd build && cmake -DCMAKE_INSTALL_PREFIX=...` .

`cmakip` is a command line tool to simplify this step, i.e. the compilation and installation of C++/CMake projects when working on environments such as [conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html) or [Python's virtual environments](https://docs.python.org/3/library/venv.html), similarly to what `pip` permits to do with Python projects. 


## Installation

First of all, make sure that you are in a conda environment or a Python virtual environment, then you can install `cmakip` as:

~~~bash
pip install --no-deps git+https://github.com/ami-iit/cmakip
~~~

## Usage

### Installation from a directory

`cmakip` can permit to quickly install a project in a directory, for example:

~~~bash
cd ~
git clone https://github.com/fmtlib/fmt
cd fmt
cmakip install .
~~~

This automatically creates a `build_cmakip` directory in the source folder and then installs it in the appropriate location:

| Operating System |  Environment Type  |  CMAKE_INSTALL_PREFIX   |   
|:----------------:|:------------------:|:-----------------------:|
| Linux&macOS      |  Conda             | ${CONDA_PREFIX}         |
| Windows          |  Conda             | ${CONDA_PREFIX}\Library |
| Linux&macOS      |  Python venv       | ${VIRTUAL_ENV}          |
| Windows          |  Python venv       | Not Supported           |

A project installed like that can be uninstalled like:
~~~
cd ~/fmt
cmakip uninstall .
~~~

### Installation from a repo

`cmakip` can also be used to install CMake libraries from a repo:
 
~~~bash
cmake install git+https://github.com/fmtlib/fmt
~~~

This automatically clone the repo in `${CONDA_PREFIX}\src` or `${VIRTUAL_ENV}\src`, and then installs it.

A library installed like this can be uninstalled simply specifying the repo name:

~~~bash
cmakip uninstall fmt
~~~

## FAQs

### Does cmakip resolve dependencies?

No. In a sense, it is kind of equivalent to `pip install --no-deps`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License

[BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html)
