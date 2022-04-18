import numpy as np
from qiskit import QuantumCircuit
from qiskit.visualization import circuit_drawer
from matplotlib import pyplot as plt
from copy import deepcopy

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
        for g in gens:
            while stillyield:
                stillyield = (next(g) != None)
                # stillyield = False
                # stillyield = stillyield or (next(g) != None)
            stillyield = True
        self.circuit, self.outpinlist = circuit, outpinlist
        return circuit, outpinlist 

    def propogateX(self, qubit) -> QuantumCircuit:
        
        dim = self.matrix.shape[0]        
        circuit = QuantumCircuit(4*(dim+1))        
        

        ORIGIN, ORIGINDIM = 0, 0
        
        broad = Broadcast(ORIGIN, self.matrix[:, qubit], dim)
        g = broad.broadcast(ORIGINDIM, circuit) 
        
        gate = next(g)
        while gate != None:
            gate = next(g)
        return circuit, broad.outpinslist(ORIGINDIM)
    

    def adjoin(self, circuit, hist, outpins):
        for i in range(len(outpins)):
            circuit.cx(outpins[i] + hist, i)

    def classicX(self, qubit) -> QuantumCircuit:
        dim = self.matrix.shape[0]        

        prop, outpins = self.propogateX(qubit)
        circuit = QuantumCircuit(5*(dim+1))
        hist = dim +1  

        circuit.x(hist + qubit)

        circuit.append( prop, circuit.qubits[hist + qubit:] + circuit.qubits[:qubit])
        self.adjoin(circuit, hist, outpins) 
        
        return circuit
    
    def ClassicCnot(self, qui, quj) -> QuantumCircuit:
        '''
            Assume that the generator matrix is it's standard form.
        '''
        dim = self.matrix.shape[0]   
        prop, outpins = self.propogateX(quj)     
        circuit = QuantumCircuit(5*(dim+1))
        hist = dim +1  
        
        circuit.cx(qui, quj)
        circuit.cx(qui, hist + quj)
        circuit.append( prop, circuit.qubits[hist:] )
        
        self.adjoin(circuit, hist, outpins)
        return circuit
    


class CSSEncoder():
    def __init__(self, G1, G2, n) -> None:
        
        encoders = [EncoderGenerator(g) for g in [G1, G2] ]

        # enc = EncoderGenerator(G1) #testI
        (self.cirG1, outpin1) , (self.cirG2, outpin2) = ( enc.encoder() for enc in\
             encoders ) 
        
        self.circuit = QuantumCircuit( len(self.cirG1.qubits) +  len(self.cirG2.qubits) )
        for i in range(n):
            self.circuit.h(i)
        
        hist = len(self.cirG2.qubits)

        self.circuit.append( self.cirG2,
         self.circuit.qubits[:hist])
        self.circuit.append( self.cirG1,
         self.circuit.qubits[hist:])
        self.circuit = self.circuit.decompose()
        for i in range(len(outpin1)):
            self.circuit.cx( outpin1[i] + hist, outpin2[i]) 
            self.circuit.cx( outpin2[i], outpin1[i] + hist)
            self.circuit.swap( outpin2[i],2*n + i)
        # for i in range(n):
            
        cx = encoders[0].classicX(2).decompose()
        self.circuit.append( cx, self.circuit.qubits[2*n:3*n] + self.circuit.qubits[3*n:3*n + len(cx.qubits) - n ])
        self.circuit = self.circuit.decompose()
        # self.circuit.cx( )

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
    circuit_drawer(Ham.circuit, output='mpl',style="bw", fold=-1)
    
    plt.savefig('Ham.svg')

if __name__ == "__main__":
    main()

