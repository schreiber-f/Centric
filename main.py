import subprocess
import sys


def main():
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "dashboard.py",
        ]
    )
    print("Started app")


if __name__ == "__main__":
    main()
