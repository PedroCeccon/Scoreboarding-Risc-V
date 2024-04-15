from enum import Enum
import instructionParser
import config

RegStatus = Enum('RegStatus', ['Free', 'Write', 'Read'])
RegType = Enum('RegType', ['Int', 'Float'])
InstructionStep = Enum('InstructionStep', ['Initial', 'Issue', 'Read', 'Execute', 'Write'])

        

class Instruction:
    def __init__(self, opcode, rd, rs1, rs2, imm):
        self.opcode = opcode
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
        self.step = InstructionStep.Initial


def main():
    instructionsRead = instructionParser.parse_file('input/program1.s')
    instructions = []
    for inst in instructionsRead:
        rd = {'reg': inst['rd'], 'type': inst['rd_type'], 'status': RegStatus.Free}
        rs1 = {'reg': inst['rs1'], 'type': inst['rs1_type'], 'status': RegStatus.Free}
        rs2 = {'reg': inst['rs2'], 'type': inst['rs2_type'], 'status': RegStatus.Free}
        instructions.append(Instruction(inst['opcode'], rd, rs1, rs2, inst['imm']))
    functional_units = config.configSetup('input/config1.in')

    print(instructions)
    print(functional_units)
        

if __name__ == '__main__':
    main()