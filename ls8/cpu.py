"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.pointer = 0xF4
        self.fl = 0b00000000

    def load(self):
        """Load a program into memory."""

        address = 0
        if len(sys.argv) !=2:
            print("Error! Proper usage: python3 ls8.py <fileName>")

        try:
            with open(sys.argv[1]) as fileName:
                for line in fileName:
                    #makes each line
                    line = line.strip()
                    #breaks each line into separate strings
                    temp = line.split()
                    #extra lines in code, continue
                    if len(temp) == 0:
                        continue
                    #handles lines with comments only
                    if temp[0][0] == "#":
                        continue
                    try:
                        self.ram[address] = int(temp[0], 2)
                    #Error handling with invalid number instructions (if has letter in it)
                    except ValueError:
                        print("Invalid number: {temp[0]}")
                        sys.exit(1)
                    address += 1
        except FileNotFoundError:
            print("Error: Couldn't open {sys.argv[1]}")
            sys.exit(2)
        
        if address == 0:
            print("Error: Empty program--held no instructions")
            sys.exit(3)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        #CMP function -- takes in two arguments as regA and regB
        elif op == "CMP":
            # 00000LGE --> FL bits (last 3 digits)
            #If they are equal set the Equal flag E to 1, otherwise 0
            if self.reg[reg_a] == self.reg[reg_b]:
                print(f'EQUAL --> A:{self.reg[reg_a]} B: {self.reg[reg_b]}')
                self.fl = 0b001
                print(f'flag: {self.fl}')
            #if regA < regB set Less than L flag to 1, otherwise 0
            elif self.reg[reg_a] < self.reg[reg_b]:
                print(f'LESS THAN --> A:{self.reg[reg_a]} B: {self.reg[reg_b]}')
                self.fl = 0b100
                print(f'flag: {self.fl}')
            #if regA > regB, set the Greater than G flag to 1 otherwise, 0
            elif self.reg[reg_a] > self.reg[reg_b]:
                print(f'GREATER --> A:{self.reg[reg_a]} B: {self.reg[reg_b]}')
                self.fl = 0b010
                print(f'flag: {self.fl}')

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            ir = self.ram[self.pc]
            print(f'current PC: {self.pc}')
            #read memory address that's stored in register PC, store that result in IR (instruction register)
            #read bytes at PC+1 and PC+2 from RAM into variables operand_a and operand_b in case they're needed
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            #depending on value of opcode, perform actions needed for the instruction per LS8 spec (If-elif)
            HLT = 0b00000001
            LDI = 0b10000010
            PRN = 0b01000111
            MUL = 0b10100010
            PUSH = 0b01000101
            POP = 0b01000110
            CALL = 0b01010000
            RET = 0b00010001
            ADD = 0b10100000
            CMP = 0b10100111
            JMP = 0b01010100
            JEQ = 0b01010101
            JNE =  0b01010110
            #update the PC for next iteration
            #HLT handler
            if ir == HLT:
                print('in HLT')
                #Halt command--stop the loop
                running = False
            #LDI handler
            elif ir == LDI:
                print('in LDI')
                #sets a specified register to a specified value
                self.reg[operand_a] = operand_b
                self.pc += 3
                print(f'setting REG: {operand_a} to = {operand_b}')
            #MULTIPLY handler
            elif ir == MUL:
                print('in MUL')
                #the call alu with those values as args
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3
            #Saw needed an ADD handler
            elif ir == CMP:
                print('in CMP')
                self.alu("CMP", operand_a, operand_b)
                self.pc += 3
                print('out of CMP')
                
            elif ir == ADD:
                print('in ADD')
                self.alu("ADD", operand_a, operand_b)
                self.pc += 3
            #PRN handler
            elif ir == PRN:
                print('in PRN')
                print(self.reg[operand_a])
                self.pc += 2
            elif ir == PUSH: 
                print('in PUSH')
                #decrementing pointer by 1
                self.pointer -= 1
                #taking the register and writing it into the value where pointer is
                self.ram_write(self.pointer, self.reg[operand_a])
                #increment steps by 2
                self.pc += 2
            elif ir == POP:
                print('in POP')
                #taking the value of pointer using ram ream and setting it to reg at that operand
                self.reg[operand_a] = self.ram_read(self.pointer)
                #increment pointer by one
                self.pointer += 1
                #increment steps by 2
                self.pc +=2
            elif ir == CALL:
                print('in CALL')
                #PUSH return address into the stack
                #return address is the instructions AFTER the call
                ret_address = self.pc + 2
                # print(f'return address: {ret_address}')
                self.pointer -= 1
                self.ram[self.pointer] = ret_address
                #Call the subroutine
                self.pc = self.reg[operand_a]
            elif ir == RET:
                print('in RET')
                # POP the return address off stack
                ret_address = self.ram[self.pointer]
                self.pointer += 1
                # Set the PC to return address
                self.pc = ret_address
            #JMP
            elif ir == JMP:
                #takes in argument of register
                #JUMP to the address stored in the given register
                #Set the PC to the address stored in the given register
                print('in JMP')
                self.pc = self.reg[operand_a]
            #JEQ
            elif ir == JEQ:
                print('in JEQ')
                print(f'current PC: {self.pc}')
                #takes in argument of register
                #if E flag is 1 (true), jump to the address stored in the given register
                if self.fl == 0b001:
                    #pc will be reg address
                    self.pc = self.reg[operand_a]
                    print(f'E is True, new address: {self.pc}')
                else:
                    self.pc += 2
                    print(f'E is 0, continue')

            #JNE
            elif ir == JNE:
                print(f'current PC: {self.pc}')
                #takes in argument of a register
                #if E flag is 0, jump to the address stroed in given register
                print('in JNE')
                print(f'Flag: {self.fl}')
                if self.fl == 0b001:
                    self.pc += 2
                    print(f'E is TRUE, continue')
                elif self.fl == 0b000 or 0b100 or 0b010:
                    #Set PC to that address
                    self.pc = self.reg[operand_a]
                    print(f'restrictions: IF Flag is: {0b000}, {0b100}, or {0b010}')
                    print(f'E is 0/False, Jumping: {self.pc}')
                else:
                    self.pc += 2
                    print(f'E is 1, continue')


    def ram_read(self, MAR):
        #Should accept address(MAR) to read and return the value stored there
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        #Should accept a value(MDR) to write and the address(MAR) to write it to
        self.ram[MAR] = MDR