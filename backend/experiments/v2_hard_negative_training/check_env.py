for pkg in ["torch", "tensorflow", "scipy", "numpy", "sklearn", "librosa"]:
    try:
        m = __import__(pkg)
        print(f"{pkg}: {getattr(m, '__version__', 'installed')}")
    except ImportError:
        print(f"{pkg}: NOT INSTALLED")
