"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.sp = 7
        self.reg[self.sp] = 0xF4
        self.flag = 0


    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        with open(sys.argv[1]) as f:
            for line in f:
                string_val = line.split("#")[0].strip()
                if string_val == "":
                    continue
                v = int(string_val, 2)
                # self.ram[address] = v
                self.ram_write(address, v)
                address += 1
        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100
            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

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
        halt = False
        while not halt:
            instruction = self.ram[self.pc]
            opr_a = self.ram_read(self.pc + 1)
            opr_b = self.ram_read(self.pc + 2)
            if instruction == 0b10000010:
                # output = self.ram_write(self.ram[self.pc + 1], self.ram[self.pc + 2])
                self.reg[opr_a] = opr_b
                self.pc += 3
            elif instruction == 0b01000111:
                output = self.reg[opr_a]
                print(output)
                self.pc += 2
            elif instruction == 0b10100000:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu('ADD', reg_a, reg_b)
                self.pc += 3
            elif instruction == 0b10100010:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu('MUL', reg_a, reg_b)
                self.pc += 3
            elif instruction == 0b10100111:       #CMP
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu('CMP', reg_a, reg_b)
                self.pc += 3
            elif instruction == 0b01010100:       #JMP
                self.pc = self.reg[opr_a]
            elif instruction == 0b01010101:       #JEQ
                if self.flag == 0b00000001:
                    self.pc = self.reg[opr_a]
                else:
                    self.pc += 2
            elif instruction == 0b01010110:       #JNE
                if self.flag != 0b00000001:
                    self.pc = self.reg[opr_a]
                else:
                    self.pc += 2
            elif instruction == 0b01000101:
                self.reg[self.sp] -= 1
                reg_num = opr_a
                val = self.reg[reg_num]
                top_stack = self.reg[self.sp]
                self.ram[top_stack] = val
                self.pc += 2
            elif instruction == 0b01000110:
                top_stack = self.reg[self.sp]
                val = self.ram[top_stack]
                reg_num = opr_a
                self.reg[reg_num] = val
                self.reg[self.sp] += 1
                self.pc += 2
            elif instruction == 0b01010000:
                return_addr = self.pc + 2
                self.reg[self.sp] -= 1
                top_stack = self.reg[self.sp]
                self.ram[top_stack] = return_addr
                reg_num = opr_a
                subroutine_addr = self.reg[reg_num]
                self.pc = subroutine_addr
            elif instruction == 0b00010001:
                top_stack = self.reg[self.sp]
                return_addr = self.ram[top_stack]
                self.reg[self.sp] += 1
                self.pc = return_addr 
            elif instruction == 0b00000001:
                halt = True
            else:
                print(f"unknown instructions {instruction} at address {self.pc}")
                sys.exit(1)
