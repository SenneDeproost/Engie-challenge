class Powerplant:
    def __init__(self, name: str, type: str, efficiency: float, pmin: float, pmax: float):
        self.name = name
        self.type = type
        self.efficiency = efficiency
        self.pmin = pmin
        self.pmax = pmax

    def calculate_production(self, megas_fuel):
        return megas_fuel * self.efficiency

    def calculate_cost_per_mega(self, cost):
        return cost / self.efficiency




