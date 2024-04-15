from enum import Enum

FUType = Enum('FUType', ['int', 'add', 'mult', 'div'])

class FunctionalUnit:
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.busy = False
        self.Fi = None
        self.Fj = None
        self.Fk = None
        self.Qj = None
        self.Qk = None
        self.Rj = False
        self.Rk = False

def parse_file(filename):
    config = []
    with open(filename, 'r') as f:
        for line in f:
            fields = line.strip().split()
            
            config.append({
                'type': fields[0],
                'qtd': int(fields[1]),
                'cycles': int(fields[2])
            })
    return config

def generate_functional_units(config):
    functional_units = []
    for unit in config:
        for i in range(unit['qtd']):
            functional_units.append(FunctionalUnit(i, FUType[unit['type']]))
    return functional_units

def configSetup(filename):
    return generate_functional_units(parse_file(filename))