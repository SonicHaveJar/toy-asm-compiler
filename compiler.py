# La verdad es que no es el mejor codigo que haya escrito
# pero hace su funcion

from typing import Optional
from os.path import isfile
import re

class Compiler:
  data_directive = ".data"
  code_directive = ".code"
  end_directive = ".end"

  opcodes = {
    "add": 0b00,
    "cmp": 0b01,
    "mov": 0b10,
    "beq": 0b11,
    "bneq":0b1101,
    "b":   0b1110,
  }

  def __init__(self, input_: Optional[str] = None):
    self.lines = [] # Codigo ensamblador

    if input_:
      if isfile(input_):
        with open(input_, 'r') as f:
          self.lines = f.readlines()
      else:
        self.lines = input_.split('\n')

    self.code = [] # Codigo 
    self.code_addr = 0 # Direccion de inicio del codigo

    self.data = {} # data y tags

  # Preprocesamiento del codigo
  def preprocess(self):
    # Removes spaces everywhere but between quotes
    def replacespaces(text):
      out = ""
      quote = False
      for c in text:
          if c == " " and not quote: continue
          if c == '"' or c == "'": quote = not quote
          out += c

      return out

    new_lines = []
    for line in self.lines:
      line = line.split(';')[0] # left side of ;
      line = line.replace('\n', '') # remove newline
      line = line.replace('\t', '') # remove tabs
      line = replacespaces(line) # remove spaces

      new_lines.append(line)

    self.lines = new_lines

  # Recorre el codigo guardando los tags y datos
  def data_pass(self):
    addr = 0
    data_addr = 0
    for line in self.lines:
      # Get data/code starting position and allocate tags
      if line.startswith(self.data_directive):
        line = line.split(self.data_directive)[1]
        data_addr = int(line) if line else 0
      elif line.startswith(self.code_directive):
        line = line.split(self.code_directive)[1]
        self.code_addr = int(line) if line else 0
        addr = self.code_addr
        continue
      elif ':' in line:
        if not '.' in line:
          line = line.split(':')[0]
          self.data[line] = (addr, addr)
          data_addr += 1
        else:
          if ".dw" in line:
            line = line.split(".dw")
            for i, data in enumerate(line[1].split(',')):
              self.data[f"{line[0][:-1]}{i}" if i else line[0][:-1]] = (data_addr, int(data))
              data_addr += 1

          elif ".rw" in line:
            line = line.split(".rw")
            for i in range(int(line[1])):
              self.data[f"{line[0][:-1]}{i}" if i else line[0][:-1]] = (data_addr, 0)
              data_addr += 1

          elif ".ascii16" in line:
            line = line.split(".ascii16")
            for i, char in enumerate(line[1].replace('"', '').replace("'", '')):
              self.data[f"{line[0][:-1]}{i}" if i else line[0][:-1]] = (data_addr, ord(char))
              data_addr += 1
      
      addr += 1

  # Recorre el codigo y genara las instrucciones en binario
  def code_pass(self):
    for line in self.lines:
      line = line.split(':')[-1]

      if "add" in line or "mov" in line or "cmp" in line:
        op = line[:3]

        line = line.split(op)[-1]
        x, y = line.split(',')

        instr = f"{self.opcodes[op]:02b}" + f"{self.data[x][0]:07b}" + f"{self.data[y][0]:07b}"

      elif "beq" in line:
        op = line[:3]
        x = line.split(op)[-1]

        instr = f"{self.opcodes[op]:02b}" + "0"*7 + f"{self.data[x][0]:07b}"

      elif "bneq" in line or "b" in line:
        op = line[:4] if "bneq" in line else line[:1]
        x = line.split(op)[-1]

        instr = f"{self.opcodes[op]:04b}" + "0"*5 + f"{self.data[x][0]:07b}"

      else:
        continue

      self.code.append(int(instr, 2))
        
  # Genera el binario
  def compile(self) -> str:
    output = "v2.0 raw\n"

    i = 0
    for code in self.code:
      output += f"{code:x} "
      if ((i + 1) % 8) == 0:
        output = output[:-1] + "\n"
      i += 1

    prev = len(self.code)
    for key, (addr, data) in self.data.items():
      pad = addr - prev

      if pad < 0: # tags
        break

      if pad > 1:
        output += f"{pad}*0 "
        i += 1
        if ((i + 1) % 8) == 0:
          output = output[:-1] + "\n"

      output += f"{(data & 0xffff):x} " # TODO

      if ((i + 1) % 8) == 0:
        output = output[:-1] + "\n"
      prev = addr
      i += 1

    return re.sub('[ 0]*(\d+["*"])[ 0]*$|(?<!\w)[ 0]+$', "", output.rstrip()) # TODO: Cambiar a algo mejor

  # Funcion para el uso mas comodo de la clase
  def __call__(self, output_file: Optional[str] = None):
    self.preprocess()
    self.data_pass()
    self.code_pass()

    binary = self.compile()

    if not output_file:
      return binary

    with open(output_file, 'w') as f:
      f.write(binary)

if __name__ == "__main__":
  import sys
  a = Compiler(sys.argv[1])
  print(a())
 