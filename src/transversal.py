from qiskit import QuantumCircuit

class TransversalGate(QuantumCircuit):
    def __init__(self) -> None:
        super().__init__()

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
