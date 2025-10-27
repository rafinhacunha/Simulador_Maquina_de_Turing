import sys
import json
from collections import defaultdict
import time
'''lê o arquivo JSON da máquina de Turing'''

def load_spec(path): 
    with open(path, 'r', encoding='utf-8') as f:
        spec = json.load(f)

    if 'initial' not in spec or 'final' not in spec or 'white' not in spec or 'transitions' not in spec:
        raise ValueError("JSON inválido: precisa conter 'initial', 'final', 'white', 'transitions'.")
    return spec

'''lê a fita de entrada'''
def load_input_tape(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()

    if data.endswith('\n'):
        data = data[:-1]
    return list(data)

'''transforma as transições em um formato fácil de acessar'''
def build_transition_map(transitions):

    tmap = defaultdict(list)
    for t in transitions:
        frm = t['from']
        rd = t['read']
        tmap[(frm, rd)].append((t['to'], t['write'], t['dir']))
    return tmap

'''corta os espaços em branco no início/fim da fita'''
def trim_tape(tape, white):

    if not tape:
        return [white]

    left = 0
    right = len(tape) - 1
    while left < len(tape) - 1 and tape[left] == white:
        left += 1
    while right > 0 and tape[right] == white:
        right -= 1
    return tape[left:right+1] if left <= right else [white]

'''executa a simulação da máquina passo a passo'''
def run_tm(spec, input_tape, max_steps=20000000):
    white = spec['white']
    initial = spec['initial']
    finals = set(spec['final'])
    transitions = spec['transitions']
    tmap = build_transition_map(transitions)

   
    tape = list(input_tape) if input_tape else [white]
    head = 0  
    state = initial

    steps = 0
    while True:

        if state in finals:
            return True, tape, state, steps

        if steps >= max_steps:
            return False, tape, state, steps

        if head < 0:
            
            add = [white]* (1 - head)
            tape = add + tape
            head = 0
        elif head >= len(tape):
            tape.extend([white] * (head - len(tape) + 1))

        cur_symbol = tape[head]

        choices = tmap.get((state, cur_symbol), None)
        if not choices:
        
            return False, tape, state, steps

        
        to_state, write_sym, direction = choices[0]

      
        tape[head] = write_sym

        
        if direction.upper() == 'R':
            head += 1
        elif direction.upper() == 'L':
            head -= 1
        else:
            raise ValueError(f"Direção inválida na transição: {direction} (esperado 'L' ou 'R')")

        
        state = to_state
        steps += 1
        
'''salva o resultado em um arquivo'''
def write_output_tape(path, tape, white):
    trimmed = trim_tape(tape, white)
    
    out = ''.join(trimmed)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(out)

def main():
    if not (4 <= len(sys.argv) <= 5):
        print("Uso: python3 tm_simulator.py spec.json input.txt output.txt [max_steps]", file=sys.stderr)
        sys.exit(2)

    spec_path = sys.argv[1]
    input_path = sys.argv[2]
    output_path = sys.argv[3]
    max_steps = int(sys.argv[4]) if len(sys.argv) == 5 else 20000000

    spec = load_spec(spec_path)
    input_tape = load_input_tape(input_path)
    inicio = time.time()
    accepted, final_tape, final_state, steps = run_tm(spec, input_tape, max_steps=max_steps)
    fim = time.time()
    tempo = fim - inicio
    print(tempo)

    write_output_tape(output_path, final_tape, spec['white'])

    print('1' if accepted else '0')

if __name__ == '__main__':
    main()
