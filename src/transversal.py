from qiskit.circuit import * 


class TransversalGate(QuantumCircuit):
    zerolevel_gate : Gate = None
    def __init__(self, blocksize : int, depth : int) -> None:
        super().__init__()
        self.blocksize ,self.depth  = blocksize, depth
        self.InitGateInstractures()
    

    def append(self, transversal, qubits, inplace = True):
        if self.depth > 1:
            circuit = transversal(self.blocksize, self.depth - 1) 
        else:
            circuit = transversal.zerolevel_gate()
        super().compose( circuit, qubits=qubits, inplace=inplace ) 
            
    def InitGateInstractures(self):
        for constructor in [ NOT_p,CNOT_p,CNOT_p_inv,SWAP_p,MULC_p,Pc_p,CPc_p, GFTp ]:
            self[ constructor.__name__] = lambda qubits : self.append(constructor, qubits)  

class NOT_p(TransversalGate):
    def __init__(self) -> None:
        super().__init__()

class CNOT_p(TransversalGate):
    def __init__(self) -> None:
        super().__init__()

class CNOT_p_inv(TransversalGate):
    def __init__(self) -> None:
        super().__init__()

class SWAP_p(TransversalGate):
    def __init__(self) -> None:
        super().__init__()

class MULC_p(TransversalGate):
    def __init__(self) -> None:
        super().__init__()

class Pc_p(TransversalGate):
    ''' 
        generalized phase.
    '''
    def __init__(self) -> None:
        super().__init__()

class CPc_p(TransversalGate):
    '''
        generalized controlled phase.
    '''
    def __init__(self) -> None:
        super().__init__()

class GFTp(TransversalGate):
    '''
        generalized fourier transform. 
    '''
    def __init__(self) -> None:
        super().__init__()

class GT_p(TransversalGate):
    '''
        generalized Toffoli.
    '''
    def __init__(self) -> None:
        super().__init__()
