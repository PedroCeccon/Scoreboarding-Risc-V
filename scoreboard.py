from enum import Enum
import instructionParser
import config
from config import FUType
import sys

RegType = Enum('RegType', ['Int', 'Float'])
InstructionStep = Enum('InstructionStep', ['Issue', 'Read', 'Execute', 'Write', 'Done'])

class Instruction:
    def __init__(self, id, opcode, rd, rs1, rs2, imm):
        self.id = id
        self.opcode = opcode
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
        self.fu = None
        self.execCycles = 0
        self.step = InstructionStep.Issue

def getRegister(reg, regType, xReg, fReg):
    if regType == 'int':
        return xReg[reg]
    elif regType == 'float':
        return fReg[reg]
    else:
        return None
    
def issueInstruction(instruction, fu):
    fu.busy = True
    fu.Fi = instruction.rd
    fu.Fj = instruction.rs1
    fu.Fk = instruction.rs2
    fu.Qj = None
    fu.Qk = None
    fu.Rj = False
    fu.Rk = False
    if fu.Fj is not None:
        fu.Qj = fu.Fj['FU']
    if fu.Fk is not None:
        fu.Qk = fu.Fk['FU']
    if fu.Qj is None:
        fu.Rj = True
    if fu.Qk is None:
        fu.Rk = True
    instruction.fu = fu
    if instruction.rd is not None:
        instruction.rd['FU'] = fu
    instruction.step = InstructionStep.Read

def writeInstruction(instruction, functional_units):
    for fu in functional_units:
        if fu.Fj == instruction.rd:
            fu.Qj = None
            fu.Rj = True
        if fu.Fk == instruction.rd:
            fu.Qk = None
            fu.Rk = True
    instruction.fu.busy = False
    instruction.fu.Fi = None
    instruction.fu.Fj = None
    instruction.fu.Fk = None
    instruction.fu.Qj = None
    instruction.fu.Qk = None
    instruction.fu.Rj = False
    instruction.fu.Rk = False
    if instruction.rd is not None:
        instruction.rd['FU'] = None
    instruction.fu = None
    instruction.step = InstructionStep.Done

def checkHazard(instruction, step, functional_units = None):
    if step == 'Issue':
        if instruction.rd is not None and instruction.rd['FU'] is not None:
            return False
    elif step == 'Read':
        if instruction.fu.Rj == False or instruction.fu.Rk == False:
            return False
    elif step == 'Write':
        if instruction.rd is not None:
            for fu in functional_units:
                if fu.Fj == instruction.rd and fu.Rj == True:
                    return False
                if fu.Fk == instruction.rd and fu.Rk == True:
                    return False
    return True

def printScoreBoard(scoreBoard):
    print('\n|-------------------------Scoreboard-------------------------|\n')
    print('|     Instruction     |  Issue  |  Read  | Execute |  Write  |')
    print('|---------------------|---------|--------|---------|---------|')
    for inst in scoreBoard:
        print(f'|{inst["inst"]}', end='')
        for i in range(21 - len(inst["inst"])): print(' ', end='')
        print(f'|  {inst["issue"]}', end='')
        for i in range(7 - len(str(inst["issue"]))): print(' ', end='')
        print(f'|  {inst["read"]}', end='')
        for i in range(6 - len(str(inst["read"]))): print(' ', end='')
        print(f'|  {inst["execute"]}', end='')
        for i in range(7 - len(str(inst["execute"]))): print(' ', end='')
        print(f'|  {inst["write"]}', end='')
        for i in range(7 - len(str(inst["write"]))): print(' ', end='')
        print('|')
        print('|---------------------|---------|--------|---------|---------|')

def main():


    scoreBoard = []

    xReg = []
    fReg = []
    for i in range(32):
        xReg.append({'reg': i, 'type': RegType.Int, 'FU': None})
    for i in range(32):
        fReg.append({'reg': i, 'type': RegType.Float, 'FU': None})

    instructionsRead = []
    if len(sys.argv) > 1:
        instructionsParsed = instructionParser.parse_file(sys.argv[1], instructionsRead)
    else:
        instructionsParsed = instructionParser.parse_file('input/default.s', instructionsRead)

    c = 0
    instructions = []
    for inst in instructionsParsed:
        rd = getRegister(inst['rd'], inst['rd_type'], xReg, fReg)
        rs1 = getRegister(inst['rs1'], inst['rs1_type'], xReg, fReg)
        rs2 = getRegister(inst['rs2'], inst['rs2_type'], xReg, fReg)
        instructions.append(Instruction(c, inst['opcode'], rd, rs1, rs2, inst['imm']))
        scoreBoard.append({'inst': instructionsRead[c], 'issue': None, 'read': None, 'execute': None, 'write': None})
        c += 1

    if len(sys.argv) > 2:
        functional_units = config.configSetup(sys.argv[2])
    else:
        functional_units = config.configSetup('config/default.in')

    instructionsDone = 0
    cycleCount = 1
    currentInstruction = 0

    while instructionsDone < len(instructions):
        i = currentInstruction
        while i >= 0:
            step = instructions[i].step
            if step == InstructionStep.Issue and checkHazard(instructions[i], 'Issue'):
                fuType = FUType.int
                if instructions[i].opcode == 2 or instructions[i].opcode == 3:
                    fuType = FUType.add
                elif instructions[i].opcode == 4:
                    fuType = FUType.mult
                elif instructions[i].opcode == 5:
                    fuType = FUType.div
                for fu in functional_units:
                    if fu.type == fuType and not fu.busy:
                        issueInstruction(instructions[i], fu)
                        scoreBoard[i]['issue'] = cycleCount
                        if currentInstruction < len(instructions) - 1:
                            currentInstruction += 1
                        break
            elif step == InstructionStep.Read and checkHazard(instructions[i], 'Read'):
                instructions[i].fu.Rj = False
                instructions[i].fu.Rk = False
                scoreBoard[i]['read'] = cycleCount
                instructions[i].step = InstructionStep.Execute
            elif step == InstructionStep.Execute:
                instructions[i].execCycles += 1
                if instructions[i].execCycles == instructions[i].fu.cycle:
                    instructions[i].step = InstructionStep.Write
                    scoreBoard[i]['execute'] = cycleCount
            elif step == InstructionStep.Write and checkHazard(instructions[i], 'Write', functional_units):
                writeInstruction(instructions[i], functional_units)
                instructionsDone += 1
                scoreBoard[i]['write'] = cycleCount
            i -= 1
        cycleCount += 1
    printScoreBoard(scoreBoard)
    
if __name__ == '__main__':
    main()