import matplotlib.pyplot as plot
import matplotlib.animation as animation
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
        self.thetas = []
        self.rs = []
        self.plot = 0
        self.number_new_infected = 0
        self.new_infected_indices = []
        self.mild_indices = []
        self.severe_indices = []
        self.death_indices = []
        self.animate = None
        self.animate2 = None

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

    def spread_virus(self, i):
        self.exposed_before = self.exposed_after
        if self.day % self.serial_interval == 0 and self.exposed_before < 3000:
            self.number_new_infected = round(self.r0 * self.total_number_infected)
            self.exposed_after += round(self.number_new_infected * 1.1)
            if self.exposed_after > 3000:
                self.number_new_infected = round((3000 - self.exposed_before) * 0.9)
                self.exposed_after = 3000
            self.number_currently_infected += self.number_new_infected
            self.total_number_infected += self.number_new_infected
            self.new_infected_indices = list(
                np.random.choice(range(self.exposed_before, self.exposed_after), self.number_new_infected,
                                 replace=False)
            )
            thetas = [self.thetas[i] for i in self.new_infected_indices]
            rs = [self.rs[i] for i in self.new_infected_indices]
            self.animate.event_source.stop()
            if len(self.new_infected_indices) > 24:
                size_list = round(len(self.new_infected_indices) / 24)
                theta_chunks = list(self.chunks(thetas, size_list))
                r_chunks = list(self.chunks(rs, size_list))
                self.animate2 = animation.FuncAnimation(
                    self.figure,
                    self.one_by_one,
                    interval=50,
                    frames=len(theta_chunks),
                    fargs=(theta_chunks, r_chunks, RED)
                )
            else:
                self.animate2 = animation.FuncAnimation(
                    self.figure,
                    self.one_by_one,
                    interval=50,
                    frames=len(thetas),
                    fargs=(thetas, rs, RED)
                )

            self.assign_symptoms()
        self.day += 1
        self.update_status()
        self.update_text()

    def one_by_one(self, i, thetas, rs, color):
        self.axes.scatter(thetas[i], rs[i], s=5, color=color)
        if i == len(thetas) - 1:
            self.animate2.event_source.stop()
            self.animate.event_source.start()

    @staticmethod
    def chunks(a_list, n):
        for i in range(0, len(a_list), n):
            yield a_list[i:i + n]

    def assign_symptoms(self):
        number_mild = round(self.percent_mild * self.number_new_infected)
        number_severe = round(self.percent_severe * self.number_new_infected)

        # choose a random subset of newly infected patients to have mild symptoms
        self.mild_indices = np.random.choice(
            self.new_infected_indices, number_mild, replace=False
        )

        # assign the rest of the patients severe symptoms, either resulting in recovery or death
        remaining_indices = [
            i for i in self.new_infected_indices if i not in self.mild_indices
        ]
        percent_severe_recovery = 1 - (self.fatality_rate / self.percent_severe)
        number_severe_recovery = round(percent_severe_recovery * number_severe)
        self.severe_indices = []
        self.death_indices = []
        if remaining_indices:
            self.severe_indices = np.random.choice(
                remaining_indices, number_severe_recovery, replace=False
            )
            self.death_indices = [
                i for i in remaining_indices if i not in self.severe_indices
            ]

        # assign recovery/death day
        low = self.day + self.mild_fast
        high = self.day + self.mild_slow
        for mild in self.mild_indices:
            recovery_day = np.random.randint(low, high)
            mild_theta = self.thetas[mild]
            mild_r = self.rs[mild]
            self.mild[recovery_day]["thetas"].append(mild_theta)
            self.mild[recovery_day]["rs"].append(mild_r)
        low = self.day + self.severe_fast
        high = self.day + self.severe_slow
        for recovery in self.severe_indices:
            recovery_day = np.random.randint(low, high)
            recovery_theta = self.thetas[recovery]
            recovery_r = self.rs[recovery]
            self.severe["recovery"][recovery_day]["thetas"].append(recovery_theta)
            self.severe["recovery"][recovery_day]["rs"].append(recovery_r)
        low = self.day + self.death_fast
        high = self.day + self.death_slow
        for death in self.death_indices:
            death_day = np.random.randint(low, high)
            death_theta = self.thetas[death]
            death_r = self.rs[death]
            self.severe["death"][death_day]["thetas"].append(death_theta)
            self.severe["death"][death_day]["rs"].append(death_r)

    def update_status(self):
        if self.day >= self.mild_fast:
            mild_thetas = self.mild[self.day]["thetas"]
            mild_rs = self.mild[self.day]["rs"]
            self.axes.scatter(mild_thetas, mild_rs, s=5, color=GREEN)
            self.number_recovered += len(mild_thetas)
            self.number_currently_infected -= len(mild_thetas)
        if self.day >= self.severe_fast:
            rec_thetas = self.severe["recovery"][self.day]["thetas"]
            rec_rs = self.severe["recovery"][self.day]["rs"]
            self.axes.scatter(rec_thetas, rec_rs, s=5, color=GREEN)
            self.number_recovered += len(rec_thetas)
            self.number_currently_infected -= len(rec_thetas)
        if self.day >= self.death_fast:
            death_thetas = self.severe["death"][self.day]["thetas"]
            death_rs = self.severe["death"][self.day]["rs"]
            self.axes.scatter(death_thetas, death_rs, s=5, color=BLACK)
            self.number_deaths += len(death_thetas)
            self.number_currently_infected -= len(death_thetas)

    def update_text(self):
        self.day_text.set_text("Day {}".format(self.day))
        self.infected_text.set_text("Infected: {}".format(self.number_currently_infected))
        self.death_text.set_text("\nDeaths: {}".format(self.number_deaths))
        self.recovered_text.set_text("\n\nRecovered: {}".format(self.number_recovered))

    def generator(self):
        while self.number_deaths + self.number_recovered < self.total_number_infected:
            yield

    def animation(self):
        self.animate = animation.FuncAnimation(
            self.figure,
            self.spread_virus,
            frames=self.generator,
            repeat=True,
            cache_frame_data=False
        )
        return self.animate


