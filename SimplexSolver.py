import numpy as np

# Based on https://medium.com/@jacob.d.moore1/coding-the-simplex-algorithm-from-scratch-using-python-and-numpy-93e3813e6e70

class SimplexSolver:

    def __init__(self):
        self.table = None

    def matrix(self, n_variables, n_constraints):
        return np.zeros((n_constraints + 1, n_variables + n_constraints + 2))

    def next_round_right_column(self, table):
        return min(table[:-1, -1]) < 0

    def next_round_bottom_row(self, table):
        l = len(table[:, 0])
        return min(table[l - 1, :-1]) < 0

    def find_negative_right_column(self, table):
        l = len(table[0, :])
        mi = min(table[:-1, l - 1])
        if mi <= 0:
            return np.where(table[:-1, l - 1] == mi)[0][0]
        else:
            return None

    def find_negative_botom_row(self, table):
        l = len(table[:, 0])
        mi = min(table[l - 1, :-1])
        if mi <= 0:
            return np.where(table[l - 1, :-1] == mi)[0][0]
        else:
            return None

    def locate_pivot_right_column(self, table):
        total = []
        row = table[self.find_negative_right_column(table), :-1]
        c = np.where(row == min(row))[0][0]
        column = table[:-1, c]
        for i, b in zip(column, table[:-1, -1]):
            if i ** 2 > 0 and b / i > 0:
                total.append(b / i)
            else:
                total.append(np.inf)
        index = total.index(min(total))
        return [index, c]

    def locate_pivot_bottom_row(self, table):
        if self.next_round_bottom_row(table):
            total = []
            n = self.find_negative_botom_row(table)
            for i, b in zip(table[:-1, n], table[:-1, -1]):
                if b / i > 0 and i ** 2 > 0:
                    total.append(b / i)
                else:
                    total.append(np.inf)
            index = total.index(min(total))
            return [index, n]

    def pivot_function(self, row, column, table):
        result = np.zeros((len(table[:, 0]), len(table[0, :])))
        pivot_right = table[row, :]
        if table[row, column] ** 2 > 0:
            r = pivot_right * (1 / table[row, column])
            for i in range(len(table[:, column])):
                k = table[i, :]
                c = table[i, column]
                if list(k) == list(pivot_right):
                    continue
                else:
                    result[i, :] = list(k - r * c)
            result[row, :] = list(r)
            return result

    def convert_equation(self, equation):
        if '≥' in equation:
            equation.pop(equation.index('≥'))
            equation = [float(i) * -1 for i in equation]
        elif '≤' in equation:
            equation.pop(equation.index('≤'))
        return equation

    def convert_min(self, table):
        table[-1, :-2] = [-1 * i for i in table[-1, :-2]]
        table[-1, -1] = -1 * table[-1, -1]
        return table

    def variable(self, table):
        var = len(table[0, :]) - len(table[:, 0]) - 1
        result = []
        for i in range(var):
            result.append('x' + str(i))
        return result

    def add_constrain(self, table):
        result = []
        for i in range(len(table[:, 0])):
            total = 0
            for j in table[i, :]:
                total += j ** 2
            if total == 0:
                result.append(total)
        return len(result) > 1

    def constrain(self, table, eq):
        if self.add_constrain(table):
            var = len(table[0, :]) - len(table[:, 0]) - 1
            j = 0
            while j < len(table[:, 0]):
                row_check = table[j, :]
                total = 0
                for i in row_check:
                    total += float(i ** 2)
                if total == 0:
                    row = row_check
                    break
                j += 1
            eq = self.convert_equation(eq)
            i = 0
            while i < len(eq) - 1:
                row[i] = eq[i]
                i += 1
            row[-1] = eq[-1]
            row[var + j] = 1

    def add_objective(self, table):
        lr = len(table[:, 0])
        result = []
        for i in range(lr):
            total = 0
            for j in table[i, :]:
                total += j ** 2
            if total == 0:
                result.append(total)
        return len(result) == 1

    def objective(self, table, equation):
        if self.add_objective(table):
            equation = [float(i) for i in equation]
            row = table[len(table[:, 0]) - 1, :]
            i = 0
            while i < len(equation) - 1:
                row[i] = equation[i] * -1
                i += 1
            row[-2] = 1
            row[-1] = equation[-1]

    def minimize(self, table):
        table = self.convert_min(table)
        # Do the pivot functions
        while self.next_round_right_column(table):
            table = self.pivot_function(self.locate_pivot_right_column(table)[0],
                                        self.locate_pivot_right_column(table)[1],
                                        table)
        while self.next_round_bottom_row(table):
            table = self.pivot_function(self.locate_pivot_bottom_row(table)[0],
                                        self.locate_pivot_bottom_row(table)[1],
                                        table)

        var = len(table[0, :]) - len(table[:, 0]) - 1
        val = {}
        for i in range(var):
            column = table[:, i]
            su = sum(column)
            ma = max(column)
            if su == ma:
                loc = np.where(column == ma)[0][0]
                val[self.variable(table)[i]] = table[loc, -1]
            else:
                val[self.variable(table)[i]] = 0
                val['min'] = table[-1, -1] * -1
        return val