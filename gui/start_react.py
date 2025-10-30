import subprocess
import os

def start_react():
    os.chdir("/home/salah/doorLockGui/gui")
    env = os.environ.copy()
    env["NODE_ENV"] = "development"
    env["CI"] = "false"
    subprocess.run(["npm", "start"], env=env, check=True)


if __name__ == "__main__":
    start_react()