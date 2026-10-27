# vaibify-conftest-loader: 1
"""Load vaibify's test-result marker plugin, when it is present.

Vaibify keeps this file identical in every version, so it is committed
once and never rewritten. The plugin it loads lives in
.vaibify/pytestPlugin/, a directory git ignores, which vaibify rewrites
as the plugin changes. After each pytest session the plugin writes the
JSON marker the vaibify dashboard reads. Without vaibify the plugin is
absent, this file does nothing, and the tests pass or fail on their own
merits. Do not edit or delete this file.
"""

from pathlib import Path as _Path


def _fpathLocateMarkerPlugin():
    """Return the plugin inside this repository, or None.

    The repository is the nearest ancestor holding .vaibify. A plugin
    that resolves outside it, through a symlink, is never loaded.
    """
    pathTests = _Path(__file__).resolve().parent
    for pathAncestor in pathTests.parents:
        if not (pathAncestor / ".vaibify").is_dir():
            continue
        pathPlugin = (
            pathAncestor / ".vaibify" / "pytestPlugin" / "markerPlugin.py")
        if not pathPlugin.is_file():
            return None
        try:
            pathPlugin.resolve().relative_to(pathAncestor)
        except ValueError:
            return None
        return pathPlugin
    return None


def _fnLoadMarkerPlugin():
    """Run the plugin as if it were this file, and expose its pytest hooks."""
    pathPlugin = _fpathLocateMarkerPlugin()
    if pathPlugin is None:
        return
    dictNamespace = {"__file__": __file__, "__name__": __name__}
    try:
        sSource = pathPlugin.read_text(encoding="utf-8")
        exec(compile(sSource, str(pathPlugin), "exec"), dictNamespace)
    except Exception as error:
        import warnings
        warnings.warn(
            "vaibify: the test-result marker plugin did not load ("
            + repr(error) + "); the tests still run, but this session "
            "writes no marker.")
        return
    for sName, fnHook in dictNamespace.items():
        if sName.startswith("pytest_"):
            globals()[sName] = fnHook


_fnLoadMarkerPlugin()
