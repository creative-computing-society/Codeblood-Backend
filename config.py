_config = {"is_dev": True, "phase": "Phase 0"}


def set_config(is_dev, phase):
    global _config
    _config["is_dev"] = is_dev
    _config["phase"] = phase


def get_is_dev():
    global _config
    return _config["is_dev"]


def get_phase():
    global _config
    return _config["phase"]


DIFFICULTY_TO_POINTS = {
    "easy": 10,
    "medium": 30,
    "hard": 50,
}

PHASE_TO_BUNDLES = {
    "Phase 0": ["App", "Phase 0"],
    "Phase 1": ["App", "Phase 1"],
    "Phase 2": ["App", "Phase 2"],
    "Phase 3": ["App", "Phase 3"],
    "Phase 4": ["Phase 4"],
}
