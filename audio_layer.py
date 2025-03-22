import subprocess

def play_audio_file(path):
    subprocess.run(["ffplay", "-nodisp", "-autoexit", path])
