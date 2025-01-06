import numpy as np

def trapezoid(x, a, b, c, d):
    # Changed the conditions to be inclusive at the boundaries
    if x < a or x > d:
        return 0
    elif a <= x <= b:
        return (x - a) / (b - a) if b != a else 1  # Slope up
    elif b <= x <= c:
        return 1  # Flat region
    else:  # c < x <= d
        return (d - x) / (d - c) if d != c else 1  # Slope down

def workload_membership(workload):
    # Workload is on a scale of 0-5
    # No need to normalize to 0-10 since we can adjust the trapezoid parameters
    print(f"Workload value: {workload}")
    
    # Adjusted trapezoid parameters for 0-5 scale
    high = trapezoid(workload, 0, 0, 1.5, 2.5)
    medium = trapezoid(workload, 1.5, 2, 3, 3.5)
    low = trapezoid(workload, 2.5, 3.5, 5, 5)
    
    print(f"Workload memberships - low: {low}, medium: {medium}, high: {high}")
    return {"low": low, "medium": medium, "high": high}

def availability_membership(availability):
    # Availability is on a scale of 0-12
    print(f"Availability value: {availability}")
    
    # Adjusted trapezoid parameters for 0-12 scale
    low = trapezoid(availability, 0, 0, 3, 5)
    medium = trapezoid(availability, 4, 5, 7, 8)
    high = trapezoid(availability, 7, 9, 12, 12)
    
    print(f"Availability memberships - low: {low}, medium: {medium}, high: {high}")
    return {"low": low, "medium": medium, "high": high}

def fuzzy_rules(workload, availability):
    rules = {
        "high_suitability": max(
            min(workload["low"], availability["high"]),
            min(workload["medium"], availability["high"])
        ),
        "medium_suitability": max(
            min(workload["low"], availability["medium"]),
            min(workload["medium"], availability["medium"])
        ),
        "low_suitability": max(
            min(workload["high"], availability["low"]),
            min(workload["medium"], availability["low"])
        )
    }
    print(f"Rule outputs: {rules}")
    return rules

def defuzzify(suitability):
    x = np.linspace(0, 100, 1000)  # Using percentage scale for suitability
    
    # Defining suitability membership functions
    suitability_high = np.array([trapezoid(xi, 60, 80, 100, 100) for xi in x])
    suitability_medium = np.array([trapezoid(xi, 30, 40, 60, 70) for xi in x])
    suitability_low = np.array([trapezoid(xi, 0, 0, 20, 40) for xi in x])

    # Apply truth values
    high_curve = np.minimum(suitability["high_suitability"], suitability_high)
    medium_curve = np.minimum(suitability["medium_suitability"], suitability_medium)
    low_curve = np.minimum(suitability["low_suitability"], suitability_low)

    # Combine using OR operator (max)
    combined_curve = np.maximum.reduce([high_curve, medium_curve, low_curve])

    # Center-of-Weight calculation
    numerator = np.sum(x * combined_curve)
    denominator = np.sum(combined_curve)
    
    result = numerator / denominator if denominator != 0 else 0
    print(f"Defuzzified result: {result}")
    return result

def calculate_suitability(workload_value, availability_value):
    workload = workload_membership(workload_value)
    availability = availability_membership(availability_value)
    rules = fuzzy_rules(workload, availability)
    suitability_score = defuzzify(rules)
    return suitability_score

# Example usage
if __name__ == '__main__':
    workload_value = 1  # High workload (scale 0-5)
    availability_value = 1  # High availability (scale 0-12)
    suitability = calculate_suitability(workload_value, availability_value)
    print(f"Final suitability score: {suitability}")