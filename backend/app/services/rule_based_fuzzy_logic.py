import numpy as np
from typing import Dict, List, Tuple, Callable, Union, Optional

class FuzzyVariable:
    def __init__(self, name: str, range_min: float, range_max: float, sets: Dict[str, List[float]]):
        """
        Initialize a fuzzy variable with its linguistic sets.
        
        Args:
            name: Name of the variable
            range_min: Minimum value of the variable
            range_max: Maximum value of the variable
            sets: Dictionary of linguistic sets, where each set is defined by [a,b,c,d] trapezoid parameters
        """
        self.name = name
        self.range_min = range_min
        self.range_max = range_max
        self.sets = sets
        
    def get_membership(self, value: float) -> Dict[str, float]:
        """Calculate membership values for all sets given a crisp input."""
        memberships = {}
        for set_name, params in self.sets.items():
            memberships[set_name] = self._trapezoid(value, *params)
        return memberships
    
    def _trapezoid(self, x: float, a: float, b: float, c: float, d: float) -> float:
        """Calculate trapezoid membership value."""
        if x < a or x > d:
            return 0
        elif a <= x <= b:
            return (x - a) / (b - a) if b != a else 1
        elif b <= x <= c:
            return 1
        else:  # c < x <= d
            return (d - x) / (d - c) if d != c else 1

class FuzzyRule:
    def __init__(self, antecedents: List[Tuple[str, str]], consequent: Tuple[str, str]):
        """
        Initialize a fuzzy rule.
        
        Args:
            antecedents: List of (variable_name, set_name) pairs for IF conditions
            consequent: (variable_name, set_name) pair for THEN result
        """
        self.antecedents = antecedents
        self.consequent = consequent
    
    def evaluate(self, variable_states: Dict[str, Dict[str, float]]) -> float:
        """Evaluate the rule given the current variable states."""
        antecedent_values = [
            variable_states[var_name][set_name]
            for var_name, set_name in self.antecedents
        ]
        return min(antecedent_values)  # Using AND operator

class FuzzySystem:
    def __init__(self):
        self.input_variables: Dict[str, FuzzyVariable] = {}
        self.output_variable: Optional[FuzzyVariable] = None
        self.rules: List[FuzzyRule] = []

    def add_input_variable(self, name: str, range_min: float, range_max: float, 
                         sets: Dict[str, List[float]]) -> None:
        """Add an input variable to the system."""
        self.input_variables[name] = FuzzyVariable(name, range_min, range_max, sets)

    def set_output_variable(self, name: str, range_min: float, range_max: float,
                          sets: Dict[str, List[float]]) -> None:
        """Set the output variable for the system."""
        self.output_variable = FuzzyVariable(name, range_min, range_max, sets)

    def add_rule(self, antecedents: List[Tuple[str, str]], consequent: Tuple[str, str]) -> None:
        """Add a rule to the system."""
        self.rules.append(FuzzyRule(antecedents, consequent))

    def evaluate(self, inputs: Dict[str, float]) -> float:
        """Evaluate the system for given inputs."""
        # Calculate memberships for all input variables
        variable_states = {}
        for var_name, value in inputs.items():
            variable_states[var_name] = self.input_variables[var_name].get_membership(value)
        print(variable_states)
        
        # Evaluate all rules
        rule_outputs: Dict[str, List[float]] = {}
        for rule in self.rules:
            rule_strength = rule.evaluate(variable_states)
            consequent_set = rule.consequent[1]
            if consequent_set not in rule_outputs:
                rule_outputs[consequent_set] = []
            rule_outputs[consequent_set].append(rule_strength)
        print(rule_outputs)
        
        # Aggregate rule outputs using maximum
        aggregated_outputs = {
            set_name: max(strengths)
            for set_name, strengths in rule_outputs.items()
        }

        # Defuzzify using center of gravity
        x = np.linspace(self.output_variable.range_min, self.output_variable.range_max, 1000)
        
        output_curves = []
        for set_name, strength in aggregated_outputs.items():
            set_params = self.output_variable.sets[set_name]
            curve = np.minimum(
                strength,
                np.array([self.output_variable._trapezoid(xi, *set_params) for xi in x])
            )
            output_curves.append(curve)

        combined_curve = np.maximum.reduce(output_curves) if output_curves else np.zeros_like(x)
        
        numerator = np.sum(x * combined_curve)
        denominator = np.sum(combined_curve)
        
        return numerator / denominator if denominator != 0 else 0

# Example usage
def create_workload_availability_system() -> FuzzySystem:
    system = FuzzySystem()
    
    # Add workload input variable
    system.add_input_variable(
        name="workload",
        range_min=0,
        range_max=5,
        sets={
            "low": [2.5, 3.5, 5, 5],
            "medium": [1.5, 2, 3, 3.5],
            "high": [0, 0, 1.5, 2.5]
        }
    )
    
    # Add availability input variable
    system.add_input_variable(
        name="availability",
        range_min=0,
        range_max=24,
        sets={
            "low": [0, 0, 6, 10],
            "medium": [8, 10, 14, 16],
            "high": [14, 18, 24, 24]
        }
    )
    
    # Set output variable
    system.set_output_variable(
        name="suitability",
        range_min=0,
        range_max=100,
        sets={
            "low": [0, 0, 20, 40],
            "medium": [30, 40, 60, 70],
            "high": [60, 80, 100, 100]
        }
    )
    
    # Add rules
    # High availability
    system.add_rule(
        antecedents=[("workload", "low"), ("availability", "high")],
        consequent=("suitability", "high")
    )
    system.add_rule(
        antecedents=[("workload", "medium"), ("availability", "high")],
        consequent=("suitability", "high")
    )
    system.add_rule(
        antecedents=[("workload", "high"), ("availability", "high")],
        consequent=("suitability", "medium")
    )
    
    # Medium availability
    system.add_rule(
        antecedents=[("workload", "low"), ("availability", "medium")],
        consequent=("suitability", "medium")
    )
    system.add_rule(
        antecedents=[("workload", "medium"), ("availability", "medium")],
        consequent=("suitability", "medium")
    )
    system.add_rule(
        antecedents=[("workload", "high"), ("availability", "medium")],
        consequent=("suitability", "medium")
    )
    
    # Low availability
    system.add_rule(
        antecedents=[("workload", "low"), ("availability", "low")],
        consequent=("suitability", "medium")
    )
    system.add_rule(
        antecedents=[("workload", "medium"), ("availability", "low")],
        consequent=("suitability", "low")
    )
    system.add_rule(
        antecedents=[("workload", "high"), ("availability", "low")],
        consequent=("suitability", "low")
    )
    
    return system

def simple_fuzzy(input_variables: List) -> FuzzySystem:
    system = FuzzySystem()
    
    for variables in input_variables:
        system.add_input_variable(
            name=variables[0],
            range_min=variables[1],
            range_max=variables[2],
            sets={
                "low": [0, 0, 0.2*variables[2], 0.4*variables[2]],
                "medium": [0.3*variables[2], 0.4*variables[2], 0.6*variables[2], 0.7*variables[2]],
                "high": [0.6*variables[2], 0.8*variables[2], variables[2], variables[2]]
            }
        )

    # Set output variable
    system.set_output_variable(
        name="suitability",
        range_min=0,
        range_max=100,
        sets={
            "low": [0, 0, 20, 40],
            "medium": [30, 40, 60, 70],
            "high": [60, 80, 100, 100]
        }
    )
    
    # Add rules
    # High var2
    system.add_rule(
        antecedents=[(input_variables[0][0], "low"), (input_variables[1][0], "high")],
        consequent=("suitability", "high")
    )
    system.add_rule(
        antecedents=[(input_variables[0][0], "medium"), (input_variables[1][0], "high")],
        consequent=("suitability", "high")
    )
    system.add_rule(
        antecedents=[(input_variables[0][0], "high"), (input_variables[1][0], "high")],
        consequent=("suitability", "medium")
    )
    
    # Medium var2
    system.add_rule(
        antecedents=[(input_variables[0][0], "low"), (input_variables[1][0], "medium")],
        consequent=("suitability", "medium")
    )
    system.add_rule(
        antecedents=[(input_variables[0][0], "medium"), (input_variables[1][0], "medium")],
        consequent=("suitability", "medium")
    )
    system.add_rule(
        antecedents=[(input_variables[0][0], "high"), (input_variables[1][0], "medium")],
        consequent=("suitability", "medium")
    )
    
    # Low var2
    system.add_rule(
        antecedents=[(input_variables[0][0], "low"), ("availability", "low")],
        consequent=("suitability", "medium")
    )
    system.add_rule(
        antecedents=[(input_variables[0][0], "medium"), ("availability", "low")],
        consequent=("suitability", "low")
    )
    system.add_rule(
        antecedents=[(input_variables[0][0], "high"), ("availability", "low")],
        consequent=("suitability", "low")
    )
    
    return system
    
if __name__ == '__main__':
    # Create and test the system
    system = create_workload_availability_system()
    result = system.evaluate({
        "workload": 1,
        "availability": 12
    })
    print(f"Suitability score: {result}")