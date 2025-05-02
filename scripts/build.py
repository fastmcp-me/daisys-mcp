import platform
import subprocess
import sys


def run(cmd, shell=False):
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    subprocess.check_call(cmd, shell=shell)


def install_portaudio_linux():
    run(["sudo", "apt", "update"])
    run(
        [
            "sudo",
            "apt",
            "install",
            "-y",
            "libportaudio2",
            "libportaudiocpp0",
            "portaudio19-dev",
            "libjack-dev",
        ]
    )


def install_portaudio_macos():
    try:
        run(["brew", "--version"])
    except Exception:
        print("Homebrew not found. Installing it...")
        run(
            '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            shell=True,
        )
    run(["brew", "install", "portaudio"])


def install_portaudio_windows():
    # Nothing required – precompiled wheels include PortAudio.
    print("No PortAudio install needed on Windows.")


def main():
    os_name = platform.system()

    if os_name == "Linux":
        install_portaudio_linux()
    elif os_name == "Darwin":
        install_portaudio_macos()
    elif os_name == "Windows":
        install_portaudio_windows()
    else:
        print(f"Unsupported OS: {os_name}")
        sys.exit(1)

    print("✅ sounddevice installation complete.")


if __name__ == "__main__":
    main()
