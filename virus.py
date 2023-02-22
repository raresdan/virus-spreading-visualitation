import matplotlib.pyplot as plot
import numpy as np

from data import *


class Virus:
    def __init__(self, parameters):
        # plot creation
        self.figure = plot.figure()
        self.axes = self.figure.add_subplot(111, projection="polar")
        self.axes.grid(False)
        self.axes.set_xticklabels([])
        self.axes.set_yticklabels([])
        self.axes.set_ylim(0, 1)

        # annotations creation
        self.day_text = self.axes.annotate(
            "Day 0", xy=[np.pi / 2, 1], ha="center", va="bottom"
        )
        self.infected_text = self.axes.annotate(
            "Infected: 0", xy=[3 * np.pi / 2, 1], ha="center", va="top", color=RED
        )
        self.death_text = self.axes.annotate(
            "\nDeaths: 0", xy=[3 * np.pi / 2, 1], ha="center", va="top", color=BLACK
        )
        self.recovered_text = self.axes.annotate(
            "\n\nRecovered: 0", xy=[3 * np.pi / 2, 1], ha="center", va="top", color=GREEN
        )

        # member variables
        self.day = 0
        self.total_number_infected = 0
        self.number_currently_infected = 0
        self.number_recovered = 0
        self.number_deaths = 0
        self.r0 = parameters["r0"]
        self.percent_mild = parameters["percent_mild"]
        self.percent_severe = parameters["percent_severe"]
        self.fatality_rate = parameters["fatality_rate"]
        self.serial_interval = parameters["serial_interval"]
        self.mild_fast = parameters["incubation"] + parameters["mild_recovery"][0]
        self.mild_slow = parameters["incubation"] + parameters["mild_recovery"][1]
        self.severe_fast = parameters["incubation"] + parameters["severe_recovery"][0]
        self.severe_slow = parameters["incubation"] + parameters["severe_recovery"][1]
        self.death_fast = parameters["incubation"] + parameters["severe_death"][0]
        self.death_slow = parameters["incubation"] + parameters["severe_death"][1]
        self.mild = {i: {"thetas": [], "rs": []} for i in range(self.mild_fast, 365)}
        self.severe = {"recovery": {i: {"thetas": [], "rs": []} for i in range(self.severe_fast, 365)},
                       "death": {i: {"thetas": [], "rs": []} for i in range(self.death_fast, 365)}}
        self.exposed_before = 0
        self.exposed_after = 1
        self.thetas = 0
        self.rs = 0
        self.plot = 0

        self.initial_population()

    def initial_population(self):
        population = 3000
        self.number_currently_infected = 1
        self.total_number_infected = 1
        indices = np.arange(0, population) + 0.5
        self.thetas = np.pi * (1 + 5 ** 0.5) * indices
        self.rs = np.sqrt(indices / population)
        self.plot = self.axes.scatter(self.thetas, self.rs, s=5, color=GREY)

        # patient zero
        self.axes.scatter(self.thetas[0], self.rs[0], s=5, color=RED)
        self.mild[self.mild_fast]["thetas"].append(self.thetas[0])
        self.mild[self.mild_fast]["rs"].append(self.rs[0])
