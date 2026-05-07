#!/usr/bin/env python3
import os
import sys
import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class Element:
    symbol: str
    name: str
    atomic_mass: float
    atomic_number: int

class ConsoleColors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    @staticmethod
    def gradient_text(text: str, start_r: int, start_g: int, start_b: int, end_r: int, end_g: int, end_b: int) -> str:
        result = []
        length = len(text)
        for i, char in enumerate(text):
            ratio = i / length if length > 1 else 0
            r = int(start_r + (end_r - start_r) * ratio)
            g = int(start_g + (end_g - start_g) * ratio)
            b = int(start_b + (end_b - start_b) * ratio)
            result.append(f'\033[38;2;{r};{g};{b}m{char}')
        result.append(ConsoleColors.RESET)
        return ''.join(result)

class ChemicalCalculator:
    def __init__(self):
        self.elements = self._init_elements()
        self.formulas = self._init_formulas()
        self.history = []
        self.constants = {'R': 0.0821, 'R_si': 8.314, 'NA': 6.022e23, 'Faraday': 96485}

    def _init_elements(self) -> Dict[str, Element]:
        return {
            'H': Element('H', 'Hydrogen', 1.008, 1), 'He': Element('He', 'Helium', 4.0026, 2),
            'Li': Element('Li', 'Lithium', 6.94, 3), 'Be': Element('Be', 'Beryllium', 9.012, 4),
            'B': Element('B', 'Boron', 10.81, 5), 'C': Element('C', 'Carbon', 12.011, 6),
            'N': Element('N', 'Nitrogen', 14.007, 7), 'O': Element('O', 'Oxygen', 15.999, 8),
            'F': Element('F', 'Fluorine', 18.998, 9), 'Ne': Element('Ne', 'Neon', 20.180, 10),
            'Na': Element('Na', 'Sodium', 22.990, 11), 'Mg': Element('Mg', 'Magnesium', 24.305, 12),
            'Al': Element('Al', 'Aluminium', 26.982, 13), 'Si': Element('Si', 'Silicon', 28.086, 14),
            'P': Element('P', 'Phosphorus', 30.974, 15), 'S': Element('S', 'Sulfur', 32.06, 16),
            'Cl': Element('Cl', 'Chlorine', 35.45, 17), 'Ar': Element('Ar', 'Argon', 39.95, 18),
            'K': Element('K', 'Potassium', 39.098, 19), 'Ca': Element('Ca', 'Calcium', 40.078, 20),
            'Fe': Element('Fe', 'Iron', 55.845, 26), 'Cu': Element('Cu', 'Copper', 63.546, 29),
            'Zn': Element('Zn', 'Zinc', 65.38, 30), 'Ag': Element('Ag', 'Silver', 107.87, 47),
            'Au': Element('Au', 'Gold', 196.97, 79), 'Pb': Element('Pb', 'Lead', 207.2, 82),
            'Br': Element('Br', 'Bromine', 79.904, 35), 'I': Element('I', 'Iodine', 126.90, 53),
            'Mn': Element('Mn', 'Manganese', 54.938, 25), 'Cr': Element('Cr', 'Chromium', 51.996, 24),
            'Ni': Element('Ni', 'Nickel', 58.693, 28), 'Sn': Element('Sn', 'Tin', 118.71, 50),
            'Hg': Element('Hg', 'Mercury', 200.59, 80), 'Pt': Element('Pt', 'Platinum', 195.08, 78),
        }

    def _init_formulas(self) -> Dict[str, Dict]:
        base = {
            'H2O': {'name': 'Water', 'composition': {'H': 2, 'O': 1}, 'type': 'molecular'},
            'CO2': {'name': 'Carbon Dioxide', 'composition': {'C': 1, 'O': 2}, 'type': 'molecular'},
            'CH4': {'name': 'Methane', 'composition': {'C': 1, 'H': 4}, 'type': 'molecular'},
            'NH3': {'name': 'Ammonia', 'composition': {'N': 1, 'H': 3}, 'type': 'molecular'},
            'NaCl': {'name': 'Sodium Chloride', 'composition': {'Na': 1, 'Cl': 1}, 'type': 'ionic'},
            'C6H12O6': {'name': 'Glucose', 'composition': {'C': 6, 'H': 12, 'O': 6}, 'type': 'organic'},
            'H2SO4': {'name': 'Sulfuric Acid', 'composition': {'H': 2, 'S': 1, 'O': 4}, 'type': 'acid'},
            'HCl': {'name': 'Hydrochloric Acid', 'composition': {'H': 1, 'Cl': 1}, 'type': 'acid'},
            'HNO3': {'name': 'Nitric Acid', 'composition': {'H': 1, 'N': 1, 'O': 3}, 'type': 'acid'},
            'CH3COOH': {'name': 'Acetic Acid', 'composition': {'C': 2, 'H': 4, 'O': 2}, 'type': 'acid'},
            'NaOH': {'name': 'Sodium Hydroxide', 'composition': {'Na': 1, 'O': 1, 'H': 1}, 'type': 'base'},
            'C2H5OH': {'name': 'Ethanol', 'composition': {'C': 2, 'H': 6, 'O': 1}, 'type': 'alcohol'},
            'C3H8': {'name': 'Propane', 'composition': {'C': 3, 'H': 8}, 'type': 'hydrocarbon'},
            'C4H10': {'name': 'Butane', 'composition': {'C': 4, 'H': 10}, 'type': 'hydrocarbon'},
            'C8H18': {'name': 'Octane', 'composition': {'C': 8, 'H': 18}, 'type': 'hydrocarbon'},
            'C2H4': {'name': 'Ethene', 'composition': {'C': 2, 'H': 4}, 'type': 'hydrocarbon'},
            'C2H2': {'name': 'Ethyne', 'composition': {'C': 2, 'H': 2}, 'type': 'hydrocarbon'},
            'C6H6': {'name': 'Benzene', 'composition': {'C': 6, 'H': 6}, 'type': 'aromatic'},
            'CH3OH': {'name': 'Methanol', 'composition': {'C': 1, 'H': 4, 'O': 1}, 'type': 'alcohol'},
            'H2O2': {'name': 'Hydrogen Peroxide', 'composition': {'H': 2, 'O': 2}, 'type': 'peroxide'},
            'SO2': {'name': 'Sulfur Dioxide', 'composition': {'S': 1, 'O': 2}, 'type': 'oxide'},
            'SO3': {'name': 'Sulfur Trioxide', 'composition': {'S': 1, 'O': 3}, 'type': 'oxide'},
            'NO': {'name': 'Nitric Oxide', 'composition': {'N': 1, 'O': 1}, 'type': 'oxide'},
            'NO2': {'name': 'Nitrogen Dioxide', 'composition': {'N': 1, 'O': 2}, 'type': 'oxide'},
            'N2O': {'name': 'Nitrous Oxide', 'composition': {'N': 2, 'O': 1}, 'type': 'oxide'},
            'CO': {'name': 'Carbon Monoxide', 'composition': {'C': 1, 'O': 1}, 'type': 'oxide'},
            'CaCO3': {'name': 'Calcium Carbonate', 'composition': {'Ca': 1, 'C': 1, 'O': 3}, 'type': 'salt'},
            'Na2CO3': {'name': 'Sodium Carbonate', 'composition': {'Na': 2, 'C': 1, 'O': 3}, 'type': 'salt'},
            'NaHCO3': {'name': 'Sodium Bicarbonate', 'composition': {'Na': 1, 'H': 1, 'C': 1, 'O': 3}, 'type': 'salt'},
            'KMnO4': {'name': 'Potassium Permanganate', 'composition': {'K': 1, 'Mn': 1, 'O': 4}, 'type': 'oxidizer'},
            'K2Cr2O7': {'name': 'Potassium Dichromate', 'composition': {'K': 2, 'Cr': 2, 'O': 7}, 'type': 'oxidizer'},
            'Fe2O3': {'name': 'Iron(III) Oxide', 'composition': {'Fe': 2, 'O': 3}, 'type': 'oxide'},
            'Al2O3': {'name': 'Aluminium Oxide', 'composition': {'Al': 2, 'O': 3}, 'type': 'oxide'},
            'SiO2': {'name': 'Silicon Dioxide', 'composition': {'Si': 1, 'O': 2}, 'type': 'mineral'},
            'MgO': {'name': 'Magnesium Oxide', 'composition': {'Mg': 1, 'O': 1}, 'type': 'oxide'},
            'CaO': {'name': 'Calcium Oxide', 'composition': {'Ca': 1, 'O': 1}, 'type': 'oxide'},
            'ZnO': {'name': 'Zinc Oxide', 'composition': {'Zn': 1, 'O': 1}, 'type': 'oxide'},
            'CuO': {'name': 'Copper(II) Oxide', 'composition': {'Cu': 1, 'O': 1}, 'type': 'oxide'},
            'CuSO4': {'name': 'Copper Sulfate', 'composition': {'Cu': 1, 'S': 1, 'O': 4}, 'type': 'salt'},
            'AgNO3': {'name': 'Silver Nitrate', 'composition': {'Ag': 1, 'N': 1, 'O': 3}, 'type': 'salt'},
            'BaSO4': {'name': 'Barium Sulfate', 'composition': {'Ba': 1, 'S': 1, 'O': 4}, 'type': 'salt'},
            'Ca(OH)2': {'name': 'Calcium Hydroxide', 'composition': {'Ca': 1, 'O': 2, 'H': 2}, 'type': 'base'},
            'NH4Cl': {'name': 'Ammonium Chloride', 'composition': {'N': 1, 'H': 4, 'Cl': 1}, 'type': 'salt'},
            '(NH4)2SO4': {'name': 'Ammonium Sulfate', 'composition': {'N': 2, 'H': 8, 'S': 1, 'O': 4}, 'type': 'fertilizer'},
            'KNO3': {'name': 'Potassium Nitrate', 'composition': {'K': 1, 'N': 1, 'O': 3}, 'type': 'fertilizer'},
            'MgSO4': {'name': 'Magnesium Sulfate', 'composition': {'Mg': 1, 'S': 1, 'O': 4}, 'type': 'salt'},
            'FeSO4': {'name': 'Iron(II) Sulfate', 'composition': {'Fe': 1, 'S': 1, 'O': 4}, 'type': 'salt'},
            'ZnSO4': {'name': 'Zinc Sulfate', 'composition': {'Zn': 1, 'S': 1, 'O': 4}, 'type': 'salt'},
            'Na2SO4': {'name': 'Sodium Sulfate', 'composition': {'Na': 2, 'S': 1, 'O': 4}, 'type': 'salt'},
            'KCl': {'name': 'Potassium Chloride', 'composition': {'K': 1, 'Cl': 1}, 'type': 'salt'},
            'MgCl2': {'name': 'Magnesium Chloride', 'composition': {'Mg': 1, 'Cl': 2}, 'type': 'salt'},
            'CaCl2': {'name': 'Calcium Chloride', 'composition': {'Ca': 1, 'Cl': 2}, 'type': 'salt'},
            'AlCl3': {'name': 'Aluminium Chloride', 'composition': {'Al': 1, 'Cl': 3}, 'type': 'salt'},
            'FeCl3': {'name': 'Iron(III) Chloride', 'composition': {'Fe': 1, 'Cl': 3}, 'type': 'salt'},
            'CCl4': {'name': 'Carbon Tetrachloride', 'composition': {'C': 1, 'Cl': 4}, 'type': 'organic'},
            'C6H5OH': {'name': 'Phenol', 'composition': {'C': 6, 'H': 6, 'O': 1}, 'type': 'organic'},
            'Pb(NO3)2': {'name': 'Lead(II) Nitrate', 'composition': {'Pb': 1, 'N': 2, 'O': 6}, 'type': 'salt'},
            'Na3PO4': {'name': 'Sodium Phosphate', 'composition': {'Na': 3, 'P': 1, 'O': 4}, 'type': 'salt'},
            'Ca3(PO4)2': {'name': 'Calcium Phosphate', 'composition': {'Ca': 3, 'P': 2, 'O': 8}, 'type': 'mineral'},
        }
        additional = {
            'CH3Cl': {'name': 'Chloromethane', 'composition': {'C': 1, 'H': 3, 'Cl': 1}, 'type': 'organic'},
            'CH2Cl2': {'name': 'Dichloromethane', 'composition': {'C': 1, 'H': 2, 'Cl': 2}, 'type': 'organic'},
            'CHCl3': {'name': 'Chloroform', 'composition': {'C': 1, 'H': 1, 'Cl': 3}, 'type': 'organic'},
            'C2H3Cl': {'name': 'Vinyl Chloride', 'composition': {'C': 2, 'H': 3, 'Cl': 1}, 'type': 'organic'},
            'C6H4Cl2': {'name': 'Dichlorobenzene', 'composition': {'C': 6, 'H': 4, 'Cl': 2}, 'type': 'organic'},
            'C2H4Cl2': {'name': 'Dichloroethane', 'composition': {'C': 2, 'H': 4, 'Cl': 2}, 'type': 'organic'},
            'C2H5Cl': {'name': 'Chloroethane', 'composition': {'C': 2, 'H': 5, 'Cl': 1}, 'type': 'organic'},
            'C3H6O': {'name': 'Acetone', 'composition': {'C': 3, 'H': 6, 'O': 1}, 'type': 'ketone'},
            'P2O5': {'name': 'Phosphorus Pentoxide', 'composition': {'P': 2, 'O': 5}, 'type': 'oxide'},
            'Fe3O4': {'name': 'Magnetite', 'composition': {'Fe': 3, 'O': 4}, 'type': 'mineral'},
            'Na2S2O3': {'name': 'Sodium Thiosulfate', 'composition': {'Na': 2, 'S': 2, 'O': 3}, 'type': 'salt'},
            'C6H4(OH)2': {'name': 'Hydroquinone', 'composition': {'C': 6, 'H': 6, 'O': 2}, 'type': 'organic'},
            'Br2': {'name': 'Bromine', 'composition': {'Br': 2}, 'type': 'elemental'},
            'I2': {'name': 'Iodine', 'composition': {'I': 2}, 'type': 'elemental'},
            'Cl2': {'name': 'Chlorine', 'composition': {'Cl': 2}, 'type': 'elemental'},
            'F2': {'name': 'Fluorine', 'composition': {'F': 2}, 'type': 'elemental'},
            'O2': {'name': 'Oxygen', 'composition': {'O': 2}, 'type': 'elemental'},
            'N2': {'name': 'Nitrogen', 'composition': {'N': 2}, 'type': 'elemental'},
            'H2': {'name': 'Hydrogen', 'composition': {'H': 2}, 'type': 'elemental'},
            'O3': {'name': 'Ozone', 'composition': {'O': 3}, 'type': 'elemental'},
        }
        base.update(additional)
        return base

    def calculate_molar_mass(self, formula: str) -> float:
        mass = 0.0
        i = 0
        while i < len(formula):
            if formula[i] == '(':
                j = i + 1
                depth = 1
                while j < len(formula) and depth > 0:
                    if formula[j] == '(':
                        depth += 1
                    elif formula[j] == ')':
                        depth -= 1
                    j += 1
                sub_formula = formula[i+1:j-1]
                sub_mass = self.calculate_molar_mass(sub_formula)
                i = j
                num = 0
                while i < len(formula) and formula[i].isdigit():
                    num = num * 10 + int(formula[i])
                    i += 1
                if num == 0:
                    num = 1
                mass += sub_mass * num
            elif formula[i].isupper():
                symbol = formula[i]
                i += 1
                if i < len(formula) and formula[i].islower():
                    symbol += formula[i]
                    i += 1
                num = 0
                while i < len(formula) and formula[i].isdigit():
                    num = num * 10 + int(formula[i])
                    i += 1
                if num == 0:
                    num = 1
                if symbol in self.elements:
                    mass += self.elements[symbol].atomic_mass * num
        return round(mass, 3)

    def moles_to_mass(self, moles: float, molar_mass: float) -> float:
        return moles * molar_mass

    def mass_to_moles(self, mass: float, molar_mass: float) -> float:
        return mass / molar_mass

    def concentration(self, moles: float, volume_liters: float) -> float:
        return moles / volume_liters

    def dilution(self, c1: float, v1: float, c2: float) -> float:
        return (c1 * v1) / c2

    def ideal_gas_law(self, P: float = None, V: float = None, n: float = None, T: float = None) -> Dict:
        R = 0.0821
        if P is None:
            return {'P': (n * R * T) / V}
        elif V is None:
            return {'V': (n * R * T) / P}
        elif n is None:
            return {'n': (P * V) / (R * T)}
        elif T is None:
            return {'T': (P * V) / (n * R)}
        return {}

    def freezing_point_depression(self, Kf: float, m: float) -> float:
        return Kf * m

    def boiling_point_elevation(self, Kb: float, m: float) -> float:
        return Kb * m

    def osmotic_pressure(self, M: float, T: float, R: float = 0.0821) -> float:
        return M * R * T

    def ph_calculation(self, H_concentration: float) -> float:
        return -math.log10(H_concentration)

    def poh_calculation(self, OH_concentration: float) -> float:
        return -math.log10(OH_concentration)

    def ph_to_h(self, ph: float) -> float:
        return 10 ** (-ph)

    def enthalpy_change(self, products: float, reactants: float) -> float:
        return products - reactants

    def gibbs_free_energy(self, delta_H: float, delta_S: float, T: float) -> float:
        return delta_H - T * delta_S

    def entropy_change(self, q_rev: float, T: float) -> float:
        return q_rev / T

    def arrhenius(self, A: float, Ea: float, T: float, R: float = 8.314) -> float:
        return A * math.exp(-Ea / (R * T))

    def equilibrium_constant(self, delta_G: float, T: float, R: float = 8.314) -> float:
        return math.exp(-delta_G / (R * T))

    def nernst_equation(self, E0: float, n: float, Q: float, T: float = 298, R: float = 8.314, F: float = 96485) -> float:
        return E0 - (R * T / (n * F)) * math.log(Q)

    def beer_lambert(self, A: float, epsilon: float, l: float) -> float:
        return A / (epsilon * l)

    def rate_law(self, k: float, concentrations: List[float], orders: List[int]) -> float:
        rate = k
        for conc, order in zip(concentrations, orders):
            rate *= conc ** order
        return rate

    def half_life_first_order(self, k: float) -> float:
        return math.log(2) / k

    def half_life_second_order(self, k: float, A0: float) -> float:
        return 1 / (k * A0)

    def activation_energy(self, k1: float, k2: float, T1: float, T2: float, R: float = 8.314) -> float:
        return R * (T1 * T2 / (T2 - T1)) * math.log(k2 / k1)

    def van_der_waals(self, P: float, V: float, n: float, T: float, a: float, b: float, R: float = 0.0821) -> Dict:
        try:
            P_calc = (n * R * T) / (V - n * b) - a * (n / V) ** 2
            V_calc = None
            return {'P': P_calc, 'V': V_calc}
        except:
            return {'error': 'Van der Waals calculation failed'}

    def quantum_yield(self, photons_absorbed: float, molecules_reacted: float) -> float:
        return molecules_reacted / photons_absorbed if photons_absorbed > 0 else 0

    def debye_huckel(self, I: float, z: float, A: float = 0.509) -> float:
        return -A * z * z * math.sqrt(I)

    def molecular_weight_distribution(self, weights: List[float], abundances: List[float]) -> float:
        total = sum(abundances)
        if total == 0:
            return 0
        return sum(w * a for w, a in zip(weights, abundances)) / total

    def radius_hydration(self, z: float, r_ion: float, epsilon: float = 78.4) -> float:
        return r_ion + (z * z * 0.5) / (epsilon)

    def diffusion_coefficient(self, kT: float, eta: float, r: float) -> float:
        return kT / (6 * math.pi * eta * r)

    def stokes_einstein(self, D: float, T: float, eta: float, k: float = 1.38e-23) -> float:
        return (k * T) / (6 * math.pi * eta * D)

    def molar_conductivity(self, lambda_inf: float, concentration: float, K: float) -> float:
        return lambda_inf - K * math.sqrt(concentration)

    def electrochemical_potential(self, mu0: float, z: float, F: float, phi: float, R: float, T: float, concentration: float) -> float:
        return mu0 + R * T * math.log(concentration) + z * F * phi

class ChemistryApp:
    def __init__(self):
        self.calc = ChemicalCalculator()
        self.running = True
        self.commands = {
            'help': self.show_help, 'mass': self.calc_molar_mass, 'mol2mass': self.moles_to_mass_cmd,
            'mass2mol': self.mass_to_moles_cmd, 'conc': self.concentration_cmd, 'dilute': self.dilution_cmd,
            'gas': self.gas_law_cmd, 'ph': self.ph_cmd, 'poh': self.poh_cmd, 'freeze': self.freeze_point_cmd,
            'boil': self.boil_point_cmd, 'osmotic': self.osmotic_pressure_cmd, 'enthalpy': self.enthalpy_cmd,
            'gibbs': self.gibbs_cmd, 'entropy': self.entropy_cmd, 'list': self.list_formulas,
            'info': self.compound_info, 'neofetch': self.show_neofetch, 'clear': self.clear_screen,
            'exit': self.exit_app, 'quit': self.exit_app, 'arrhenius': self.arrhenius_cmd,
            'nernst': self.nernst_cmd, 'half': self.half_life_cmd, 'beer': self.beer_cmd,
            'eqconst': self.eq_const_cmd, 'history': self.show_history, 'elements': self.list_elements,
            'convert': self.convert_units, 'balance': self.balance_equation, 'ph2h': self.ph_to_h_cmd,
        }

    def print_banner(self):
        banner = "  _____ _                  _      _____      _            _       _\n"
        banner += " / ____| |                | |    / ____|    | |          | |     | |\n"
        banner += "| |    | |__   ___  _ __  | |_  | |     __ _| |_ ___  ___| | __ _| |_ ___ _ __\n"
        banner += "| |    | '_ \\ / _ \\| '_ \\ | __| | |    / _` | __/ _ \\/ __| |/ _` | __/ _ \\ '__|\n"
        banner += "| |____| | | | (_) | | | || |_  | |___| (_| | ||  __/ (__| | (_| | ||  __/ |\n"
        banner += " \\_____|_| |_|\\___/|_| |_| \\__|  \\_____\\__,_|\\__\\___|\\___|_|\\__,_|\\__\\___|_|\n"
        print(ConsoleColors.gradient_text(banner, 0, 255, 255, 255, 0, 255))

    def show_menu(self):
        formulas_list = list(self.calc.formulas.keys())
        print(f"\n{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}")
        print(f"{ConsoleColors.BOLD}{ConsoleColors.YELLOW} CHEMICAL FORMULAS DATABASE ({len(formulas_list)} formulas){ConsoleColors.RESET}")
        print(f"{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}\n")
        cols = 5
        for i in range(0, len(formulas_list), cols):
            row = formulas_list[i:i+cols]
            row_str = []
            for formula in row:
                info = self.calc.formulas[formula]
                type_color = {'molecular': ConsoleColors.GREEN, 'ionic': ConsoleColors.BLUE,
                              'organic': ConsoleColors.MAGENTA, 'acid': ConsoleColors.RED,
                              'base': ConsoleColors.CYAN, 'oxide': ConsoleColors.YELLOW,
                              'salt': ConsoleColors.WHITE, 'alcohol': ConsoleColors.MAGENTA,
                              'hydrocarbon': ConsoleColors.CYAN, 'aromatic': ConsoleColors.YELLOW,
                              'ketone': ConsoleColors.BLUE, 'peroxide': ConsoleColors.RED,
                              'mineral': ConsoleColors.GREEN, 'fertilizer': ConsoleColors.YELLOW,
                              'oxidizer': ConsoleColors.RED, 'elemental': ConsoleColors.WHITE}.get(info['type'], ConsoleColors.WHITE)
                row_str.append(f"{type_color}{formula:<12}{ConsoleColors.RESET}")
            print('  '.join(row_str))
        print(f"\n{ConsoleColors.CYAN}{'-'*80}{ConsoleColors.RESET}")
        print(f"{ConsoleColors.BOLD}{ConsoleColors.GREEN} COMMANDS:{ConsoleColors.RESET}")
        print(f"  {ConsoleColors.YELLOW}/help{ConsoleColors.RESET} - Show all commands")
        print(f"  {ConsoleColors.YELLOW}/list{ConsoleColors.RESET} - List all formulas")
        print(f"  {ConsoleColors.YELLOW}/mass <formula>{ConsoleColors.RESET} - Calculate molar mass")
        print(f"  {ConsoleColors.YELLOW}/info <formula>{ConsoleColors.RESET} - Get compound info")
        print(f"  {ConsoleColors.YELLOW}/neofetch{ConsoleColors.RESET} - Show system info")
        print(f"  {ConsoleColors.YELLOW}/clear{ConsoleColors.RESET} - Clear screen")
        print(f"  {ConsoleColors.YELLOW}/exit{ConsoleColors.RESET} - Exit program")

    def show_help(self, args=None):
        help_text = f"""
{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}
{ConsoleColors.BOLD}{ConsoleColors.YELLOW} CHEMISTRY CALCULATOR HELP v2.0{ConsoleColors.RESET}
{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}

{ConsoleColors.BOLD}{ConsoleColors.GREEN} MASS CALCULATIONS:{ConsoleColors.RESET}
  {ConsoleColors.CYAN}/mass <formula>{ConsoleColors.RESET}           - Calculate molar mass
  {ConsoleColors.CYAN}/mol2mass <moles> <formula>{ConsoleColors.RESET} - Convert moles to mass
  {ConsoleColors.CYAN}/mass2mol <mass> <formula>{ConsoleColors.RESET} - Convert mass to moles

{ConsoleColors.BOLD}{ConsoleColors.GREEN} SOLUTION CHEMISTRY:{ConsoleColors.RESET}
  {ConsoleColors.CYAN}/conc <moles> <volume_L>{ConsoleColors.RESET}    - Concentration (M)
  {ConsoleColors.CYAN}/dilute <C1> <V1> <C2>{ConsoleColors.RESET}      - Dilution volume
  {ConsoleColors.CYAN}/ph <H+>{ConsoleColors.RESET}                   - pH from [H+]
  {ConsoleColors.CYAN}/poh <OH->{ConsoleColors.RESET}                 - pOH from [OH-]
  {ConsoleColors.CYAN}/ph2h <pH>{ConsoleColors.RESET}                 - [H+] from pH

{ConsoleColors.BOLD}{ConsoleColors.GREEN} THERMODYNAMICS:{ConsoleColors.RESET}
  {ConsoleColors.CYAN}/freeze <Kf> <molality>{ConsoleColors.RESET}     - Freezing point depression
  {ConsoleColors.CYAN}/boil <Kb> <molality>{ConsoleColors.RESET}       - Boiling point elevation
  {ConsoleColors.CYAN}/osmotic <M> <T>{ConsoleColors.RESET}            - Osmotic pressure
  {ConsoleColors.CYAN}/enthalpy <H_prod> <H_react>{ConsoleColors.RESET} - Enthalpy change
  {ConsoleColors.CYAN}/gibbs <dH> <dS> <T>{ConsoleColors.RESET}        - Gibbs free energy
  {ConsoleColors.CYAN}/entropy <Q_rev> <T>{ConsoleColors.RESET}        - Entropy change

{ConsoleColors.BOLD}{ConsoleColors.GREEN} REACTION KINETICS:{ConsoleColors.RESET}
  {ConsoleColors.CYAN}/arrhenius <A> <Ea> <T>{ConsoleColors.RESET}     - Rate constant
  {ConsoleColors.CYAN}/half <k> <order> <A0>{ConsoleColors.RESET}      - Half-life
  {ConsoleColors.CYAN}/eqconst <dG> <T>{ConsoleColors.RESET}          - Equilibrium constant

{ConsoleColors.BOLD}{ConsoleColors.GREEN} ELECTROCHEMISTRY:{ConsoleColors.RESET}
  {ConsoleColors.CYAN}/nernst <E0> <n> <Q> <T>{ConsoleColors.RESET}    - Nernst equation

{ConsoleColors.BOLD}{ConsoleColors.GREEN} SPECTROSCOPY:{ConsoleColors.RESET}
  {ConsoleColors.CYAN}/beer <A> <eps> <l>{ConsoleColors.RESET}         - Beer-Lambert law

{ConsoleColors.BOLD}{ConsoleColors.GREEN} GAS LAWS:{ConsoleColors.RESET}
  {ConsoleColors.CYAN}/gas P=? V=? n=? T=?{ConsoleColors.RESET}        - Ideal gas law (R=0.0821)

{ConsoleColors.BOLD}{ConsoleColors.GREEN} INFORMATION:{ConsoleColors.RESET}
  {ConsoleColors.CYAN}/list{ConsoleColors.RESET}                     - List all formulas
  {ConsoleColors.CYAN}/info <formula>{ConsoleColors.RESET}            - Compound info
  {ConsoleColors.CYAN}/elements{ConsoleColors.RESET}                 - List all elements
  {ConsoleColors.CYAN}/history{ConsoleColors.RESET}                  - Show calculation history
  {ConsoleColors.CYAN}/neofetch{ConsoleColors.RESET}                 - System information
  {ConsoleColors.CYAN}/clear{ConsoleColors.RESET}                    - Clear screen
  {ConsoleColors.CYAN}/exit{ConsoleColors.RESET}                     - Exit program

{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}
{ConsoleColors.DIM}Created by @concole_hack | Chemistry Calculator Pro v2.0{ConsoleColors.RESET}
"""
        print(help_text)

    def calc_molar_mass(self, args):
        if not args:
            print(f"{ConsoleColors.RED} Usage: /mass <formula>{ConsoleColors.RESET}")
            return
        formula = args[0].upper()
        try:
            mass = self.calc.calculate_molar_mass(formula)
            print(f"{ConsoleColors.GREEN} Molar mass of {formula}: {mass} g/mol{ConsoleColors.RESET}")
            self.calc.history.append(f"mass {formula} = {mass} g/mol")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def moles_to_mass_cmd(self, args):
        if len(args) < 2:
            print(f"{ConsoleColors.RED} Usage: /mol2mass <moles> <formula>{ConsoleColors.RESET}")
            return
        try:
            moles = float(args[0])
            formula = args[1].upper()
            molar_mass = self.calc.calculate_molar_mass(formula)
            mass = self.calc.moles_to_mass(moles, molar_mass)
            print(f"{ConsoleColors.GREEN} {moles} moles of {formula} = {mass:.3f} grams{ConsoleColors.RESET}")
            self.calc.history.append(f"mol2mass {moles} {formula} = {mass:.3f}g")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def mass_to_moles_cmd(self, args):
        if len(args) < 2:
            print(f"{ConsoleColors.RED} Usage: /mass2mol <mass_g> <formula>{ConsoleColors.RESET}")
            return
        try:
            mass = float(args[0])
            formula = args[1].upper()
            molar_mass = self.calc.calculate_molar_mass(formula)
            moles = self.calc.mass_to_moles(mass, molar_mass)
            print(f"{ConsoleColors.GREEN} {mass}g of {formula} = {moles:.3f} moles{ConsoleColors.RESET}")
            self.calc.history.append(f"mass2mol {mass}g {formula} = {moles:.3f} mol")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def concentration_cmd(self, args):
        if len(args) < 2:
            print(f"{ConsoleColors.RED} Usage: /conc <moles> <volume_L>{ConsoleColors.RESET}")
            return
        try:
            moles = float(args[0])
            volume = float(args[1])
            conc = self.calc.concentration(moles, volume)
            print(f"{ConsoleColors.GREEN} Concentration = {conc:.3f} M{ConsoleColors.RESET}")
            self.calc.history.append(f"conc {moles}mol/{volume}L = {conc:.3f}M")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def dilution_cmd(self, args):
        if len(args) < 3:
            print(f"{ConsoleColors.RED} Usage: /dilute <C1> <V1> <C2>{ConsoleColors.RESET}")
            return
        try:
            c1 = float(args[0])
            v1 = float(args[1])
            c2 = float(args[2])
            v2 = self.calc.dilution(c1, v1, c2)
            print(f"{ConsoleColors.GREEN} Final volume needed: {v2:.3f} L{ConsoleColors.RESET}")
            self.calc.history.append(f"dilute {c1}M {v1}L -> {c2}M = {v2:.3f}L")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def gas_law_cmd(self, args):
        params = {'P': None, 'V': None, 'n': None, 'T': None}
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=')
                key = key.upper()
                if key in params and value != '?':
                    params[key] = float(value)
        try:
            result = self.calc.ideal_gas_law(**params)
            for key, value in result.items():
                print(f"{ConsoleColors.GREEN} {key} = {value:.3f}{ConsoleColors.RESET}")
            self.calc.history.append(f"gas {params}")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def ph_cmd(self, args):
        if not args:
            print(f"{ConsoleColors.RED} Usage: /ph <H+_concentration>{ConsoleColors.RESET}")
            return
        try:
            h_conc = float(args[0])
            ph = self.calc.ph_calculation(h_conc)
            print(f"{ConsoleColors.GREEN} pH = {ph:.3f}{ConsoleColors.RESET}")
            if ph < 7:
                print(f"{ConsoleColors.RED}  Acidic solution{ConsoleColors.RESET}")
            elif ph > 7:
                print(f"{ConsoleColors.BLUE}  Basic solution{ConsoleColors.RESET}")
            else:
                print(f"{ConsoleColors.GREEN}  Neutral solution{ConsoleColors.RESET}")
            self.calc.history.append(f"ph {h_conc} = {ph:.3f}")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def poh_cmd(self, args):
        if not args:
            print(f"{ConsoleColors.RED} Usage: /poh <OH-_concentration>{ConsoleColors.RESET}")
            return
        try:
            oh_conc = float(args[0])
            poh = self.calc.poh_calculation(oh_conc)
            ph = 14 - poh
            print(f"{ConsoleColors.GREEN} pOH = {poh:.3f}{ConsoleColors.RESET}")
            print(f"{ConsoleColors.GREEN} pH = {ph:.3f}{ConsoleColors.RESET}")
            self.calc.history.append(f"poh {oh_conc} = {poh:.3f}")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def ph_to_h_cmd(self, args):
        if not args:
            print(f"{ConsoleColors.RED} Usage: /ph2h <pH>{ConsoleColors.RESET}")
            return
        try:
            ph = float(args[0])
            h_conc = self.calc.ph_to_h(ph)
            print(f"{ConsoleColors.GREEN} [H+] = {h_conc:.3e} M{ConsoleColors.RESET}")
            self.calc.history.append(f"ph2h {ph} = {h_conc:.3e}M")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def freeze_point_cmd(self, args):
        if len(args) < 2:
            print(f"{ConsoleColors.RED} Usage: /freeze <Kf> <molality>{ConsoleColors.RESET}")
            return
        try:
            kf = float(args[0])
            m = float(args[1])
            delta_t = self.calc.freezing_point_depression(kf, m)
            print(f"{ConsoleColors.GREEN} Freezing point depression = {delta_t:.3f} C{ConsoleColors.RESET}")
            self.calc.history.append(f"freeze Kf={kf} m={m} = {delta_t:.3f}C")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def boil_point_cmd(self, args):
        if len(args) < 2:
            print(f"{ConsoleColors.RED} Usage: /boil <Kb> <molality>{ConsoleColors.RESET}")
            return
        try:
            kb = float(args[0])
            m = float(args[1])
            delta_t = self.calc.boiling_point_elevation(kb, m)
            print(f"{ConsoleColors.GREEN} Boiling point elevation = {delta_t:.3f} C{ConsoleColors.RESET}")
            self.calc.history.append(f"boil Kb={kb} m={m} = {delta_t:.3f}C")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def osmotic_pressure_cmd(self, args):
        if len(args) < 2:
            print(f"{ConsoleColors.RED} Usage: /osmotic <Molarity> <Temp_K>{ConsoleColors.RESET}")
            return
        try:
            m = float(args[0])
            t = float(args[1])
            pressure = self.calc.osmotic_pressure(m, t)
            print(f"{ConsoleColors.GREEN} Osmotic pressure = {pressure:.3f} atm{ConsoleColors.RESET}")
            self.calc.history.append(f"osmotic M={m} T={t} = {pressure:.3f}atm")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def enthalpy_cmd(self, args):
        if len(args) < 2:
            print(f"{ConsoleColors.RED} Usage: /enthalpy <H_products> <H_reactants>{ConsoleColors.RESET}")
            return
        try:
            h_products = float(args[0])
            h_reactants = float(args[1])
            delta_h = self.calc.enthalpy_change(h_products, h_reactants)
            print(f"{ConsoleColors.GREEN} dH = {delta_h:.3f} kJ/mol{ConsoleColors.RESET}")
            if delta_h < 0:
                print(f"{ConsoleColors.RED}  Exothermic reaction{ConsoleColors.RESET}")
            else:
                print(f"{ConsoleColors.BLUE}  Endothermic reaction{ConsoleColors.RESET}")
            self.calc.history.append(f"enthalpy = {delta_h:.3f}kJ/mol")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def gibbs_cmd(self, args):
        if len(args) < 3:
            print(f"{ConsoleColors.RED} Usage: /gibbs <dH> <dS> <T>{ConsoleColors.RESET}")
            return
        try:
            delta_h = float(args[0])
            delta_s = float(args[1])
            t = float(args[2])
            delta_g = self.calc.gibbs_free_energy(delta_h, delta_s, t)
            print(f"{ConsoleColors.GREEN} dG = {delta_g:.3f} kJ/mol{ConsoleColors.RESET}")
            if delta_g < 0:
                print(f"{ConsoleColors.GREEN}  Spontaneous reaction{ConsoleColors.RESET}")
            else:
                print(f"{ConsoleColors.RED}  Non-spontaneous reaction{ConsoleColors.RESET}")
            self.calc.history.append(f"gibbs = {delta_g:.3f}kJ/mol")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def entropy_cmd(self, args):
        if len(args) < 2:
            print(f"{ConsoleColors.RED} Usage: /entropy <Q_rev> <T>{ConsoleColors.RESET}")
            return
        try:
            q_rev = float(args[0])
            t = float(args[1])
            delta_s = self.calc.entropy_change(q_rev, t)
            print(f"{ConsoleColors.GREEN} dS = {delta_s:.3f} J/(mol*K){ConsoleColors.RESET}")
            self.calc.history.append(f"entropy = {delta_s:.3f}J/(mol*K)")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def arrhenius_cmd(self, args):
        if len(args) < 3:
            print(f"{ConsoleColors.RED} Usage: /arrhenius <A> <Ea> <T>{ConsoleColors.RESET}")
            return
        try:
            A = float(args[0])
            Ea = float(args[1])
            T = float(args[2])
            k = self.calc.arrhenius(A, Ea, T)
            print(f"{ConsoleColors.GREEN} Rate constant k = {k:.3e} s^-1{ConsoleColors.RESET}")
            self.calc.history.append(f"arrhenius A={A} Ea={Ea} T={T} = {k:.3e}")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def nernst_cmd(self, args):
        if len(args) < 4:
            print(f"{ConsoleColors.RED} Usage: /nernst <E0> <n> <Q> <T>{ConsoleColors.RESET}")
            return
        try:
            E0 = float(args[0])
            n = float(args[1])
            Q = float(args[2])
            T = float(args[3])
            E = self.calc.nernst_equation(E0, n, Q, T)
            print(f"{ConsoleColors.GREEN} Cell potential E = {E:.3f} V{ConsoleColors.RESET}")
            self.calc.history.append(f"nernst E0={E0} n={n} Q={Q} T={T} = {E:.3f}V")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def half_life_cmd(self, args):
        if len(args) < 2:
            print(f"{ConsoleColors.RED} Usage: /half <k> <order> [A0]{ConsoleColors.RESET}")
            return
        try:
            k = float(args[0])
            order = int(args[1])
            if order == 1:
                t_half = self.calc.half_life_first_order(k)
                print(f"{ConsoleColors.GREEN} Half-life (1st order) = {t_half:.3f} s{ConsoleColors.RESET}")
            elif order == 2 and len(args) >= 3:
                A0 = float(args[2])
                t_half = self.calc.half_life_second_order(k, A0)
                print(f"{ConsoleColors.GREEN} Half-life (2nd order) = {t_half:.3f} s{ConsoleColors.RESET}")
            else:
                print(f"{ConsoleColors.RED} Invalid order or missing A0 for 2nd order{ConsoleColors.RESET}")
            self.calc.history.append(f"half k={k} order={order}")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def beer_cmd(self, args):
        if len(args) < 3:
            print(f"{ConsoleColors.RED} Usage: /beer <A> <epsilon> <l>{ConsoleColors.RESET}")
            return
        try:
            A = float(args[0])
            eps = float(args[1])
            l = float(args[2])
            conc = self.calc.beer_lambert(A, eps, l)
            print(f"{ConsoleColors.GREEN} Concentration = {conc:.3e} M{ConsoleColors.RESET}")
            self.calc.history.append(f"beer A={A} eps={eps} l={l} = {conc:.3e}M")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def eq_const_cmd(self, args):
        if len(args) < 2:
            print(f"{ConsoleColors.RED} Usage: /eqconst <dG> <T>{ConsoleColors.RESET}")
            return
        try:
            dG = float(args[0])
            T = float(args[1])
            K = self.calc.equilibrium_constant(dG, T)
            print(f"{ConsoleColors.GREEN} Equilibrium constant K = {K:.3e}{ConsoleColors.RESET}")
            self.calc.history.append(f"eqconst dG={dG} T={T} = {K:.3e}")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def list_formulas(self, args=None):
        print(f"\n{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}")
        print(f"{ConsoleColors.BOLD}{ConsoleColors.YELLOW} ALL CHEMICAL FORMULAS ({len(self.calc.formulas)}){ConsoleColors.RESET}")
        print(f"{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}\n")
        formulas_list = list(self.calc.formulas.keys())
        cols = 5
        for i in range(0, len(formulas_list), cols):
            row = formulas_list[i:i+cols]
            row_str = []
            for formula in row:
                info = self.calc.formulas[formula]
                type_color = {'molecular': ConsoleColors.GREEN, 'ionic': ConsoleColors.BLUE,
                              'organic': ConsoleColors.MAGENTA, 'acid': ConsoleColors.RED,
                              'base': ConsoleColors.CYAN, 'oxide': ConsoleColors.YELLOW,
                              'salt': ConsoleColors.WHITE, 'alcohol': ConsoleColors.MAGENTA,
                              'hydrocarbon': ConsoleColors.CYAN, 'aromatic': ConsoleColors.YELLOW,
                              'ketone': ConsoleColors.BLUE, 'peroxide': ConsoleColors.RED,
                              'mineral': ConsoleColors.GREEN, 'fertilizer': ConsoleColors.YELLOW,
                              'oxidizer': ConsoleColors.RED, 'elemental': ConsoleColors.WHITE}.get(info['type'], ConsoleColors.WHITE)
                row_str.append(f"{type_color}{formula:<12}{ConsoleColors.RESET}")
            print('    '.join(row_str))
        print(f"\n{ConsoleColors.CYAN}{'-'*80}{ConsoleColors.RESET}")

    def list_elements(self, args=None):
        print(f"\n{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}")
        print(f"{ConsoleColors.BOLD}{ConsoleColors.YELLOW} PERIODIC TABLE ELEMENTS ({len(self.calc.elements)}){ConsoleColors.RESET}")
        print(f"{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}\n")
        elements_list = sorted(self.calc.elements.values(), key=lambda x: x.atomic_number)
        cols = 6
        for i in range(0, len(elements_list), cols):
            row = elements_list[i:i+cols]
            row_str = []
            for elem in row:
                row_str.append(f"{ConsoleColors.GREEN}{elem.symbol:<3}{ConsoleColors.RESET}({elem.atomic_number})")
            print('   '.join(row_str))
        print(f"\n{ConsoleColors.CYAN}{'-'*80}{ConsoleColors.RESET}")

    def compound_info(self, args):
        if not args:
            print(f"{ConsoleColors.RED} Usage: /info <formula>{ConsoleColors.RESET}")
            return
        formula = args[0].upper()
        if formula in self.calc.formulas:
            info = self.calc.formulas[formula]
            mass = self.calc.calculate_molar_mass(formula)
            print(f"\n{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}")
            print(f"{ConsoleColors.BOLD}{ConsoleColors.YELLOW} COMPOUND INFORMATION{ConsoleColors.RESET}")
            print(f"{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}\n")
            print(f"{ConsoleColors.GREEN} Formula:{ConsoleColors.RESET} {ConsoleColors.BOLD}{formula}{ConsoleColors.RESET}")
            print(f"{ConsoleColors.GREEN} Name:{ConsoleColors.RESET} {info['name']}")
            print(f"{ConsoleColors.GREEN} Type:{ConsoleColors.RESET} {info['type'].capitalize()}")
            print(f"{ConsoleColors.GREEN} Molar Mass:{ConsoleColors.RESET} {mass} g/mol")
            print(f"\n{ConsoleColors.CYAN} Composition:{ConsoleColors.RESET}")
            for element, count in info['composition'].items():
                elem_mass = self.calc.elements[element].atomic_mass * count
                percentage = (elem_mass / mass) * 100
                print(f"  {ConsoleColors.YELLOW}{element}{ConsoleColors.RESET}{count if count > 1 else ''}: {elem_mass:.3f} g/mol ({percentage:.1f}%)")
            print()
        else:
            print(f"{ConsoleColors.RED} Formula '{formula}' not found. Use /list to see all formulas.{ConsoleColors.RESET}")

    def show_history(self, args=None):
        if not self.calc.history:
            print(f"{ConsoleColors.YELLOW} No calculations in history.{ConsoleColors.RESET}")
            return
        print(f"\n{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}")
        print(f"{ConsoleColors.BOLD}{ConsoleColors.YELLOW} CALCULATION HISTORY ({len(self.calc.history)} entries){ConsoleColors.RESET}")
        print(f"{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}\n")
        for i, entry in enumerate(self.calc.history[-20:], 1):
            print(f"  {ConsoleColors.GREEN}{i}.{ConsoleColors.RESET} {entry}")
        print(f"\n{ConsoleColors.CYAN}{'-'*80}{ConsoleColors.RESET}")

    def convert_units(self, args):
        if len(args) < 3:
            print(f"{ConsoleColors.RED} Usage: /convert <value> <from_unit> <to_unit>{ConsoleColors.RESET}")
            return
        try:
            value = float(args[0])
            unit_from = args[1].lower()
            unit_to = args[2].lower()
            conversions = {
                ('c', 'k'): lambda x: x + 273.15, ('k', 'c'): lambda x: x - 273.15,
                ('c', 'f'): lambda x: x * 9/5 + 32, ('f', 'c'): lambda x: (x - 32) * 5/9,
                ('k', 'f'): lambda x: x * 9/5 - 459.67, ('f', 'k'): lambda x: (x + 459.67) * 5/9,
                ('atm', 'pa'): lambda x: x * 101325, ('pa', 'atm'): lambda x: x / 101325,
                ('atm', 'bar'): lambda x: x * 1.01325, ('bar', 'atm'): lambda x: x / 1.01325,
                ('l', 'ml'): lambda x: x * 1000, ('ml', 'l'): lambda x: x / 1000,
                ('g', 'kg'): lambda x: x / 1000, ('kg', 'g'): lambda x: x * 1000,
            }
            result = conversions.get((unit_from, unit_to), lambda x: None)(value)
            if result is not None:
                print(f"{ConsoleColors.GREEN} {value} {unit_from} = {result:.3f} {unit_to}{ConsoleColors.RESET}")
                self.calc.history.append(f"convert {value} {unit_from} -> {unit_to} = {result:.3f}")
            else:
                print(f"{ConsoleColors.RED} Conversion not supported{ConsoleColors.RESET}")
        except Exception as e:
            print(f"{ConsoleColors.RED} Error: {e}{ConsoleColors.RESET}")

    def balance_equation(self, args):
        print(f"{ConsoleColors.YELLOW} Equation balancing is complex. Use online tools for now.{ConsoleColors.RESET}")

    def show_neofetch(self, args=None):
        neofetch_text = f"""
{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}
{ConsoleColors.BOLD}{ConsoleColors.YELLOW} CHEMISTRY CALCULATOR PRO v2.0{ConsoleColors.RESET}
{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}

{ConsoleColors.BOLD}{ConsoleColors.WHITE}Developer:{ConsoleColors.RESET} @concole_hack
{ConsoleColors.BOLD}{ConsoleColors.WHITE}Version:{ConsoleColors.RESET} 2.0.0
{ConsoleColors.BOLD}{ConsoleColors.WHITE}Formulas:{ConsoleColors.RESET} {len(self.calc.formulas)}+ chemical compounds
{ConsoleColors.BOLD}{ConsoleColors.WHITE}Elements:{ConsoleColors.RESET} {len(self.calc.elements)} elements supported
{ConsoleColors.BOLD}{ConsoleColors.WHITE}Features:{ConsoleColors.RESET} Mass Calc, pH, Gas Laws, Thermo, Kinetics, Electrochemistry
{ConsoleColors.BOLD}{ConsoleColors.WHITE}Commands:{ConsoleColors.RESET} 25+ powerful chemistry commands
{ConsoleColors.BOLD}{ConsoleColors.WHITE}History:{ConsoleColors.RESET} Last {len(self.calc.history)} calculations stored
{ConsoleColors.BOLD}{ConsoleColors.WHITE}Status:{ConsoleColors.RESET} {ConsoleColors.GREEN} Running{ConsoleColors.RESET}

{ConsoleColors.BOLD}{ConsoleColors.MAGENTA} TIP:{ConsoleColors.RESET} Type {ConsoleColors.CYAN}/help{ConsoleColors.RESET} to see all commands
{ConsoleColors.BOLD}{ConsoleColors.MAGENTA} TIP:{ConsoleColors.RESET} Type {ConsoleColors.CYAN}/list{ConsoleColors.RESET} to browse all formulas
{ConsoleColors.BOLD}{ConsoleColors.MAGENTA} TIP:{ConsoleColors.RESET} Type {ConsoleColors.CYAN}/elements{ConsoleColors.RESET} to list all elements
{ConsoleColors.BOLD}{ConsoleColors.MAGENTA} TIP:{ConsoleColors.RESET} Type {ConsoleColors.CYAN}/history{ConsoleColors.RESET} to see calculation history

{ConsoleColors.BOLD}{ConsoleColors.CYAN}{'='*80}{ConsoleColors.RESET}
"""
        print(neofetch_text)

    def clear_screen(self, args=None):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_banner()
        self.show_menu()

    def exit_app(self, args=None):
        print(f"\n{ConsoleColors.GREEN} Goodbye! Thanks for using Chemistry Calculator!{ConsoleColors.RESET}")
        print(f"{ConsoleColors.DIM}Created by @concole_hack{ConsoleColors.RESET}\n")
        self.running = False

    def process_command(self, command_line: str):
        if not command_line.startswith('/'):
            print(f"{ConsoleColors.RED} Commands must start with '/'. Type /help for assistance.{ConsoleColors.RESET}")
            return
        parts = command_line[1:].strip().split()
        if not parts:
            return
        cmd = parts[0].lower()
        args = parts[1:]
        if cmd in self.commands:
            self.commands[cmd](args)
        else:
            print(f"{ConsoleColors.RED} Unknown command: /{cmd}. Type /help for available commands.{ConsoleColors.RESET}")

    def run(self):
        self.clear_screen(None)
        print(f"\n{ConsoleColors.BOLD}{ConsoleColors.GREEN} Chemistry Calculator Ready!{ConsoleColors.RESET}")
        print(f"{ConsoleColors.DIM}Type /help to see all commands | /exit to quit{ConsoleColors.RESET}\n")
        while self.running:
            try:
                user_input = input(f"{ConsoleColors.BOLD}{ConsoleColors.CYAN}chem>{ConsoleColors.RESET} ").strip()
                if user_input:
                    self.process_command(user_input)
            except KeyboardInterrupt:
                print(f"\n{ConsoleColors.YELLOW} Use /exit to quit properly{ConsoleColors.RESET}")
            except EOFError:
                self.exit_app()
            except Exception as e:
                print(f"{ConsoleColors.RED} Unexpected error: {e}{ConsoleColors.RESET}")

if __name__ == "__main__":
    app = ChemistryApp()
    app.run()

By @concole_hack
