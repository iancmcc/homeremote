import time
import subprocess
import shelve
from contextlib import contextmanager


FILENAME = "/tmp/remote.db"


STATES=[0, # None
        1, # A/C
        2, # B/D
        3, # AB/CD
        ]

CLOSETAMP = "closetamp"
SPEAKERS_AB = "SPEAKERS_AB"
SPEAKERS_CD = "SPEAKERS_CD"

AB = SPEAKERS_AB
CD = SPEAKERS_CD

KEYS = {
    "ROOM2": "KEY_FRONT",
    "SPEAKERS_AB": "KEY_LEFT",
    "SPEAKERS_CD": "KEY_RIGHT",
}

IRSEND = "/usr/bin/irsend"


ROOM = [1]

@contextmanager
def config():
    db = shelve.open(FILENAME, writeback=True)
    try:
        yield db.setdefault(str(ROOM[0]), {})
    finally:
        db.close()


@contextmanager
def room2():
    send("ROOM2")
    ROOM[0] = 2
    yield
    send("ROOM2")
    ROOM[0] = 1


def set_speaker_state(speakers, state, initialstate=0):
    # First get the current state
    with config() as db:
        oldstate = db.setdefault(CLOSETAMP, {}).setdefault(speakers, initialstate)
        diff = state - oldstate
        # If positive, that's the number to do. If negative, we want 4-diff
        count = diff if diff >= 0 else 4 + diff
        send(speakers, remote=CLOSETAMP, count=count)
        # Store the new state
        db[CLOSETAMP][speakers] = state


def set_volume(vol=0, initialstate=0):
    with config() as db:
        old = db.setdefault(CLOSETAMP, {}).setdefault('VOLUME', initialstate)
        delta = vol - old
        if delta > 0:
            send("KEY_VOLUMEUP", count=delta)
        elif delta < 0:
            send("KEY_VOLUMEDOWN", count=-delta)
        db[CLOSETAMP]['VOLUME'] = vol


def send(key, remote="closetamp", count=1):
    tosend = KEYS.get(key, key)
    if tosend is not None:
        for i in range(count):
            subprocess.call([IRSEND, "SEND_ONCE", remote, tosend])
            time.sleep(0.01)


def power_on():
    send("KEY_POWER")


def power_off():
    send("KEY_POWER2")


def set_source_diningbathroom():
    send("KEY_CD")


def set_source_norababy():
    send("KEY_AUX")


class HomeState(object):

    def __init__(self):
        pass

