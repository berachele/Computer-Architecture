"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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
        #read memory address that's stored in register PC, store that result in IR (instruction register)
        running = True

        while running:
            ir = self.ram[self.pc]
            # print(f"IR: {ir}")
            
            #read bytes at PC+1 and PC+2 from RAM into variables operand_a and operand_b in case they're needed
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            #depending on value of opcode, perform actions needed for the instruction per LS8 spec (If-elif)
            HLT = 0b00000001
            LDI = 0b10000010
            PRN = 0b01000111
            #update the PC for next iteration
            #HLT handler
            if ir == HLT:
                #Halt command--stop the loop
                print('HALT--ending loop')
                running = False
            #LDI handler
            elif ir == LDI:
                #sets a specified register to a specified value
                # print(f'adding {operand_b} at position {operand_a}')
                # print(f'{self.reg[operand_a]}, {operand_b}')
                self.reg[operand_a] = operand_b
                self.pc += 3
            #PRN handler
            elif ir == PRN:
                # print(f'PRN--> {self.reg[operand_a]}')
                #prints the specified register's value
                print(self.reg[operand_a])
                self.pc += 2
    
    def ram_read(self, MAR):
        #Should accept address(MAR) to read and return the value stored there
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        #Should accept a value(MDR) to write and the address(MAR) to write it to
        self.ram[MAR] = MDR