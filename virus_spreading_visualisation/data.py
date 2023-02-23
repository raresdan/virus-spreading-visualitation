GREY = (0.78, 0.78, 0.78)  # uninfected patient
RED = (0.96, 0.15, 0.15)  # infected patient
GREEN = (0, 0.86, 0.03)  # recovered patient
BLACK = (0, 0, 0)  # dead patient

VIRUS_PARAMETERS = {
    "r0": 2.28,
    "incubation": 5,
    "percent_mild": 0.8,
    "mild_recovery": (7, 14),
    "percent_severe": 0.2,
    "severe_recovery": (21, 42),
    "severe_death": (14, 56),
    "fatality_rate": 0.034,
    "serial_interval": 7
}
