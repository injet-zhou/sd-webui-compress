import launch

deps = ['pyoxipng']

for dep in deps:
    if not launch.is_installed(dep):
        launch.run_pip(f"install {dep}", f"{dep}")