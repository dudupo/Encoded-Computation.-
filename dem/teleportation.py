from qiskit import ClassicalRegister, QuantumCircuit
from qiskit.visualization import circuit_drawer
from matplotlib import pyplot as plt


from qiskit import Aer, transpile
from qiskit.tools.visualization import plot_histogram, plot_state_city
import qiskit.quantum_info as qi



def genTunnel_single():
    circuit = QuantumCircuit(3, 2) 
    circuit.h(1)
    circuit.cx(1,2)
    circuit.cx(0,1)
    circuit.h(0)
    circuit.measure(0,0)
    circuit.measure(1,1)
    circuit.x(2).c_if(1,1)
    circuit.z(2).c_if(0,1)
    return circuit

def genTunnel_multiple(n : int):
    circuit = QuantumCircuit(3*n, 2*n)
    for i in range(n):
        circuit.append(  genTunnel_single(),
        [i + n*j for j in range(3)],
        [i + n*j for j in range(2)]  )
    return circuit


if __name__ == "__main__":

    

    # circuit = genTunnel_multiple(2).decompose()
    # circuit_drawer(circuit, output='mpl',style="bw", fold=-1)
    # plt.savefig('Tele.svg')

    EPR_transmit = QuantumCircuit(4,4)
    EPR_transmit.h(0)
    EPR_transmit.cx(0,1)
    # # EPR_transmit.append(genTunnel_multiple(2), list(range(6)), list(range(4)))
    EPR_transmit.append(genTunnel_single(), [1,2,3] , [0,1])

    # EPR_transmit
    # EPR_transmit.measure(5,5)
    # EPR_transmit.measure(4, 4)
    EPR_transmit.measure(0, 2)
    EPR_transmit.measure(3, 3)
    # Transpile for simulator
    simulator = Aer.get_backend('aer_simulator')
    circ = transpile(EPR_transmit, simulator)
    # Run and get counts
    result = simulator.run(circ).result()
    counts = result.get_counts(circ)
    print(counts)
    DD = { "00" : 0, "01" :0, "10" : 0, "11" : 0 }
    for key, val in counts.items():        
        DD[ key[:2] ] += val

    print(DD)
    plot_histogram(DD, title='Bell-State counts')
    plt.show()