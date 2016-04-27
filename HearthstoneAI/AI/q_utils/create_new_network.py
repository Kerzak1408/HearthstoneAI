import os;
from pybrain.tools.customxml import NetworkWriter
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure.modules.linearlayer import LinearLayer

def main():
    first_layer_size = 11 + 1 + 150 + 5 + 5 + 5 + 1
    net = buildNetwork(first_layer_size,100,1)
    path = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'network.xml')
    NetworkWriter.writeToFile(net, path)
    print ("Neural Network initialized.")
if __name__ == "__main__":
    main()