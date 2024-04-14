from enum import Enum
# import instructionParser

RegStatus = Enum('RegStatus', ['Free', 'Write', 'Read'])
RegType = Enum('RegType', ['Int', 'Float'])

class Register:
    def __init__(self, type, number):
        self.type = type
        self.number = number
        self.status = RegStatus.Free

    def changeStatus(self, status):
        self.status = status


def main():
    xRegisters = [Register(RegType.Int, i) for i in range(32)]
    fRegisters = [Register(RegType.Float, i) for i in range(32)]
    # instructions = instructionParser.parse_file('example.s')
    for x in xRegisters:
        print(x)

if __name__ == '__main__':
    main()