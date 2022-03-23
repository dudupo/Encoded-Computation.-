import numpy as np
from qiskit import QuantumCircuit
from qiskit.visualization import circuit_drawer
from matplotlib import pyplot as plt
IDMAP = lambda _ : _
LEFT, RIGHT = lambda _ : 2*_ , lambda _ : 2*_ + 1

class Broadcast():

    def __init__(self, origin, pins, dim) -> None:
        self.origin, self.pins, self.dim = origin, pins, dim
        self.ancilas = dim
        

    def __broadcast(self, circuit : QuantumCircuit,
     _ancmap = IDMAP, _outmap = IDMAP) -> QuantumCircuit:
        
        def In_map(x):
            if x == 1:
                return self.origin
            return ({ True : _ancmap, False : _outmap  } [bool(x < self.dim)])[x] 


        def In_circuitcx(x,y):
            circuit.cx(In_map(x), In_map(y))

        for j in range(1, self.dim//2):
            for func in [ LEFT, RIGHT]:
                In_circuitcx(j, func(j))        
                yield circuit
        for j in range(self.dim//2, self.dim): 
            for func in [ LEFT, RIGHT]:
                if self.pins[func(j) % self.dim ] :
                    In_circuitcx(j, func(j))        
                    yield circuit
        # uncompute phase.
        for j in reversed(range(1, self.dim//2)):
            for func in [ LEFT, RIGHT]:
                In_circuitcx(j, func(j))        
                yield circuit
        
        while True:
            yield None 

    def broadcast(self, origindim, circuit : QuantumCircuit ) -> QuantumCircuit:
        _ancmap, _outmap = {}, {}
        
        for j in range(2, self.dim):
            _ancmap[j] = (self.origin+1) * (self.dim) + j
        for j in range(self.dim, 2*self.dim):
            _outmap[j] = (origindim+2) * (self.dim) + j 

        yield from self.__broadcast(circuit, _ancmap, _outmap)
    
    def outpinslist(self, origindim):
        return [ (origindim+2) * (self.dim) + j for j in range(self.dim, 2*self.dim) ] 
              

class EncoderGenerator():
    def __init__(self, matrix) -> None:
        self.matrix = matrix 
    
    def encoder(self) -> QuantumCircuit:

        dim = self.matrix.shape[0]
        origin = self.matrix.shape[-1]
        circuit = QuantumCircuit((origin+4)*(dim+1))
        gens = [ ]
        
        for j in range(origin):
            broad = Broadcast(j, self.matrix[:, j], dim) 
            gens.append(broad.broadcast(origin, circuit))
        
        broad = Broadcast(0, self.matrix[:, 0], dim) 
        outpinlist = broad.outpinslist(origin)     
        
        stillyield = True
        while stillyield:
            stillyield = False
            for g in gens:
                stillyield = stillyield or (next(g) != None)
        return circuit, outpinlist 

class CSSEncoder():
    def __init__(self, G1, G2, n) -> None:
        

        # enc = EncoderGenerator(G1) #testI
        (self.cirG1, outpin1) , (self.cirG2, outpin2) = ( enc.encoder() for enc in\
             [EncoderGenerator(g) for g in [G1, G2] ] ) 
        self.circuit = QuantumCircuit( len(self.cirG1.qubits) +  len(self.cirG2.qubits) )
        for i in range(n):
            self.circuit.h(i)
        
        hist = len(self.cirG2.qubits)

        self.circuit.append( self.cirG2,
         self.circuit.qubits[:hist])
        self.circuit.append( self.cirG1,
         self.circuit.qubits[hist:])
        
        for i in range(len(outpin1)):
            self.circuit.cx( outpin1[i] + hist, outpin2[i]) 

        

def main():
    
    testI = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]])

    Hamming84 = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [1, 1, 0, 1],
        [1, 0, 1, 1],
        [0, 1, 1, 1],
        [1, 1, 1, 0]
    ])

    DualHamming84 = (Hamming84 + np.ones((8,4))) % 2
    Ham = CSSEncoder(Hamming84, DualHamming84, 8)
    print()
    circuit_drawer(Ham.circuit.decompose(), output='mpl', fold=-1)
    
    plt.savefig('Ham.svg')

if __name__ == "__main__":
    main()

