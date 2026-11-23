# Ensures tests can `import src...` the same way the app does, by adding the
# repo root to sys.path (pytest's default rootdir insertion is not enough
# here since we don't install the package).
