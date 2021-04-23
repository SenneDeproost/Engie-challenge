from Powerplant import Powerplant
from copy import deepcopy
import numpy as np
from SimplexSolver import SimplexSolver

translations= {
    "gasfired": "gas", "gas(euro/MWh)": "gas",
    "turbojet": "kerosine", "kerosine(euro/MWh)": "kerosine",
    "co2(euro/ton)": "co2",
    "wind(%)": "wind"
}

source_to_cost = {
    "wind": "wind(%)",
    "kerosine": "kerosine(euro/MWh)",
    "gas": "gas(euro/MWh)"
}

type_to_source = {
    "windturbine": "wind",
    "gasfired": "gas",
    "turbojet": "kerosine"
}


costs_per_type = {
    "gas": ["gas", "co2"],
    "kerosine": ["kerosine", "co2"],
    "wind": []
}

zero_costs = ["wind"]

class CommitmentController:
    def __init__(self, data):
        self.data = data
        self.load = data['load']
        self.fuels = data['fuels']
        self.powerplants = []
        for plant in data['powerplants']:
            self.powerplants.append(Powerplant(
              plant['name'],
              plant['type'],
              plant['efficiency'],
              plant['pmin'],
              plant['pmax']
            ))



    def calculate_commitment(self):
        solver = SimplexSolver()
        n_variables = len(self.powerplants) - 2
        n_constraints = n_variables*2
        n_objectives = 1
        n_lines = n_constraints + n_objectives
        mat = solver.matrix(n_variables, n_lines)
        zero_cost_production = 0
        for i in range(len(self.powerplants)):
            plant = self.powerplants[i]
            _low = [0] * (n_variables + 2)
            _up = [0] * (n_variables + 2)
            cost = type_to_source[plant.type]
            if cost in zero_costs:
                zero_cost_production += (plant.pmax * (self.fuels[source_to_cost[cost]]/100))
            else:
                # Lowbound
                _low[i] = 1
                _low[-2] = '≥'
                _low[-1] = plant.pmin
                # Upbound
                _up[i] = 1
                _up[-2] = '≤'
                _up[-1] = plant.pmax
                # Add constraints
                solver.constrain(mat, _low)
                solver.constrain(mat, _up)


        # Add constraint for total production
        _low = [1] * (n_variables + 2)
        _up = [1] * (n_variables + 2)

        _low[-2] = '≥'
        _low[-1] = self.load - zero_cost_production
        # Upbound
        _up[-2] = '≤'
        _up[-1] = self.load - zero_cost_production
        # Add bounds to
        solver.constrain(mat, _low)
        solver.constrain(mat, _up)

        # Define objective
        ratios = []
        for plant in self.powerplants:
            cost = type_to_source[plant.type]
            if cost in zero_costs:
                ratios.append(0)
            else:
                ratios.append(plant.calculate_cost_per_mega(self.fuels[source_to_cost[cost]]))

        solver.objective(mat, ratios)

        # Solve the minimization task
        result = solver.minimize(mat)
        vals = list(result.values())
        commitment = []
        for i in range(n_variables):
            commitment.append({"name": self.powerplants[i].name, "p": round(vals[i], 2)})
        for i in range(n_variables, n_variables + 2):
            plant = self.powerplants[i]
            cost = type_to_source[plant.type]
            commitment.append({"name": plant.name, "p": round(plant.pmax*(self.fuels[source_to_cost[cost]]/100), 1)})
        return commitment
