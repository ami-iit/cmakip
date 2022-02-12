import argparse
import os
import sys
import platform
import shutil
import subprocess

from typing import Dict, Iterable, Iterator, List, Optional, Sequence, TextIO, Type, Tuple, Union

cmakip_build_type = "Release"


class CmdLineParser:
    def __init__(self):

        self.parser = argparse.ArgumentParser(description="Automatically build a CMake project in a conda or venv environment.")

        self.parser.add_argument('command', type=str, nargs=1,
                    help='Command to execute (supported commands: install).')

        self.parser.add_argument('path', type=str, nargs=1,
                    help='Local source path or remote url.')

    def parse(self) -> Tuple[argparse.Namespace, List]:

        return self.parser.parse_known_args(args=sys.argv[1:])


def run_command(args, cwd):
    full_command = " ".join(args)
    print(f"--- cmakip executing command: {full_command}")
    subprocess.run(args, cwd=cwd)

def get_install_prefix():
    """
    Get install prefix, based on the specified environment variables.
    
    On Linux and macOS, both Python's virtualenv and conda environments are supported.
    On Windows, only conda environments are supported.
    """

    if "CONDA_PREFIX" in os.environ:
        if (platform.system() == "Windows"):
            return os.path.join(os.environ["CONDA_PREFIX"],"Library")
        else:
            return os.environ["CONDA_PREFIX"]

    if "VIRTUAL_ENV" in os.environ:
        if (platform.system() == "Windows"):
            raise RuntimeError(f"Python virtual env detected, but cmakip on Windows only supports conda environments.")
        else:
            return os.environ["VIRTUAL_ENV"]

    # If we are not in a python virtual einvroment neither a conda prefix, raise an error
    raise RuntimeError(f"Faiure: no conda environment or pythin virtual environemtn detected. cmakip needs to be run in an environment.")

def get_source_directory(project_name):
    """
    Get source directory 
    """

    if "CONDA_PREFIX" in os.environ:
        return os.path.join(os.environ["CONDA_PREFIX"],"src",project_name)

    if "VIRTUAL_ENV" in os.environ:
        return os.path.join(os.environ["VIRTUAL_ENV"],"src",project_name)


    # If we are not in a python virtual einvroment neither a conda prefix, raise an error
    raise RuntimeError(f"Faiure: no conda environment or pythin virtual environemtn detected. cmakip needs to be run in an environment.")



def do_install(build_directory, install_prefix):
    run_command(["cmake",f"-DCMAKE_BUILD_TYPE={cmakip_build_type}", f"-DCMAKE_INSTALL_PREFIX={install_prefix}", ".."], cwd=build_directory)
    # Build
    run_command(["cmake","--build",".","--config",cmakip_build_type], cwd=build_directory)
    # Install
    run_command(["cmake","--install",".","--config",cmakip_build_type], cwd=build_directory)
    print("--- cmakip: install successfully completed")

def do_uninstall(build_directory, install_prefix):
    # Check if CMakeLists.txt exists in the specified path
    install_manifest_candidate_name = os.path.join(build_directory, "install_manifest.txt")
    if(not os.path.isfile(install_manifest_candidate_name)):
        raise RuntimeError(f"Fail during uninstall project was never installed as no install_manifest.txt is found.")
    
    # Get list of installed files
    install_manifest = open(install_manifest_candidate_name, "r")
    files_to_uninstall = install_manifest.readlines()
    for file_to_uninstall in files_to_uninstall:
        print(f"--- cmakip: Remove {file_to_uninstall.strip()}")
        os.remove(file_to_uninstall.strip())

    install_manifest.close()
    print("--- cmakip: uninstall successfully completed")


def main(cli_args: Sequence[str], prog: Optional[str] = None) -> None:  # noqa: C901
    """
    Parse the CLI arguments and invoke the build process.
    :param cli_args: CLI arguments
    :param prog: Program name to show in help text
    """
    args, extra_args = CmdLineParser().parse()

    # Detect the command
    if (args.command[0] != "install" and args.command[0] != "uninstall"):
        raise RuntimeError("Only the install and uninstall commands are supported.")

    # Detect if argument is local path or remote url
    is_local_path = True
    if ("://" in args.path[0]):
        is_local_path = False

    # Get install path (also checks and raise error if we are not in a support env)
    install_prefix = get_install_prefix()

    if is_local_path:
        src_path = args.path[0]
        if(args.command[0] == "install"):
            if(not os.path.isdir(src_path)):
                raise RuntimeError(f"Source path {src_path} is not a directory on this system.")
        if(args.command[0] == "uninstall"):
            if(not os.path.isdir(src_path)):
                project_name = src_path
                src_path = get_source_directory(project_name)
    else:
        if args.command[0] == "install":
            # TODO: investigate if in some way we can recycle pip parser for these urls
            full_path = args.path[0]

            if (not "git+" in full_path):
                raise RuntimeError(f"Remote specifier {full_path} does not contain git+, only git is currently supported.")

            # Split across @ 
            full_path_split = full_path.split("@")

            if (len(full_path_split) >= 3):
                raise RuntimeError(f"Too many @ in f{full_path}.")

            # TODO: move this logic somewhere where we can test it
            # Detect if git repo is the first argument or second
            if ("git+" in full_path_split[0]):
                project_name = None
                repo_url = full_path_split[0].strip()[4:]
                if len(full_path_split) == 2:
                    repo_tag = full_path_split[1]
                else:
                    repo_tag = None
            elif("git+" in full_path_split[1]):
                project_name = full_path_split[0].strip()
                repo_url = full_path_split[1].strip()[4:]
                if len(full_path_split) == 3:
                    repo_tag = full_path_split[2]
                else:
                    repo_tag = None

            # TODO: Remove anything that comes after # in repo_url
            if project_name is None:
                project_name = repo_url.split("/")[-1]

            # Now clone the repo
            src_path = get_source_directory(project_name)

            # Delete it if it already exists
            if (os.path.exists(src_path)):
                print(f"--- cmakip: found directory {src_path}, removing it before cloning in it.")
                shutil.rmtree(src_path)

            # Clone the repo
            run_command(["git","clone", repo_url, src_path], cwd=os.getcwd())

            # If a specific tag is given, run checkout
            if repo_tag is not None:
                run_command(["git","checkout", repo_tag], cwd=src_path)
        
        elif args.command[0] == "uninstall":
            project_name = args.path[0]
            src_path = get_source_directory(project_name)


    # Check if CMakeLists.txt exists in the specified path
    cmakelists_candidate_name = os.path.join(src_path, "CMakeLists.txt")
    if(not os.path.isfile(cmakelists_candidate_name)):
        raise RuntimeError(f"Local path {src_path} is not a CMake project as it does not contain a CMakeLists.txt file.")

    # If it does not exist, create build directory
    build_directory = os.path.join(src_path, "build_cmakip")
    if (not os.path.isdir(build_directory)):
        os.mkdir(build_directory)
    
    # TODO: Check if cmake exists to give a resonable error if it does not
    if (args.command[0] == "install"):
        do_install(build_directory, install_prefix)

    if (args.command[0] == "uninstall"):
        do_uninstall(build_directory, install_prefix)

    exit(0)

def entrypoint() -> None:
    main(sys.argv[1:])

if __name__ == '__main__':  # pragma: no cover
    main(sys.argv[1:], 'python -m build')
