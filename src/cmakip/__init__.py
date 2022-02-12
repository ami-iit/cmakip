def _is_editable() -> bool:

    import importlib.util
    import pathlib
    import site

    # Get the ModuleSpec of the package
    module_spec = importlib.util.find_spec(name="cmakip")

    # This can be None. If it's None, assume non-editable installation.
    if module_spec.origin is None:
        return False

    # Get the folder containing the 'teaching' package
    package_dir = str(pathlib.Path(module_spec.origin).parent.parent)

    # The installation is editable if the package dir is not in any {site|dist}-packages
    return package_dir not in site.getsitepackages()


def _configure_verbosity() -> None:
    pass


# Configure the package
_configure_verbosity()

# Delete private functions
del _is_editable
del _configure_verbosity
