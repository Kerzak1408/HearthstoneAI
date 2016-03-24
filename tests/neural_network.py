from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure.modules.sigmoidlayer import SigmoidLayer
from PIL.ImageDraw import Outline
from pybrain.structure.networks.feedforward import FeedForwardNetwork
from pybrain.structure.connections.full import FullConnection

def main():
    a = 0
    for i in range(0,100):
        inLayer = SigmoidLayer(2)
        hiddenLayer = SigmoidLayer(3)
        outLayer = SigmoidLayer(1)
        
        net = FeedForwardNetwork()
        net.addInputModule(inLayer)
        net.addModule(hiddenLayer)
        net.addOutputModule(outLayer)
        
        in_to_hidden = FullConnection(inLayer,hiddenLayer)
        hidden_to_out = FullConnection(hiddenLayer,outLayer)
        
        net.addConnection(in_to_hidden)
        net.addConnection(hidden_to_out)
        
        net.sortModules()
        
        ds = SupervisedDataSet(2,1)
        ds.addSample((1,1), (0))
        ds.addSample((1,0), (1))
        ds.addSample((0,1), (1))
        ds.addSample((0,0), (0))
        
        trainer = BackpropTrainer(net,ds)
        trainer.trainUntilConvergence()
        
        out = net.activate((1,1))
        if (out < 0.5):
            a = a + 1
    print(str(a) + "/100")
if __name__ == "__main__":
    main()