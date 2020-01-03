import numpy as np
import random


# from math import pow
debug = True
# todo:
#  DANIEL:
#   general notes:
#       forward propagate does not throw error but has not been evaluated for accuracy.
#       backward propagate is riddled with errors mostly surrounding lack of initialization of gradient list and
#       inconsistencies regarding what is passed where. I have recorded comments regarding areas I see as
#       potentially problematic.

class NeuralNetwork:

    def __init__(self, layers):
        self.layers = layers
        self.cost = None

    def forward_propagate(self, inputs):
        first = True
        last_layer = None
        for layer in self.layers:
            if first:
                layer.forward_propagate_neurons(inputs)
                first = False
            else:
                outputs = last_layer.get_outputs()
                outputs = np.append(outputs, 1)
                layer.forward_propagate_neurons(outputs)
            last_layer = layer

    def backward_propagate(self, desired_output):
        # ASSUMPTION: The output layer has only one neuron

        # set initial back propagate value
        last_layer = self.layers[len(self.layers) - 1]  # is an object
        last_output = last_layer.get_outputs()  # float
        last_output = np.append(last_output, 1)  # np array float, 1 todo: seems strange to append a one to output
        # self.cost = pow(last_output - desired_output, 2)
        last_gradient = 2 * (last_output - desired_output)  # np array  float, 1
        last_layer.back_propagate_last(last_gradient)

        # back propagate additional layers
        for i in range(len(self.layers) - 1):
            j = len(self.layers) - i - 2
            is_input_layer = (i == 0)
            self.layers[j].back_propagate(self.layers[j + 1], is_input_layer)

    def train_layers(self):
        for layer in self.layers:
            inputs = []
            outputs = []
            iterations = 1000

            layer.train(inputs, outputs, iterations)


class Layer:

    def __init__(self, neurons):
        self.neurons = neurons

    def forward_propagate_neurons(self, inputs):
        for n in self.neurons:
            n.forward_propagate(inputs)

    def back_propagate_last(self, last_gradient):
        for n in self.neurons:
            n.update_gradient(last_gradient)
            n.calculate_gradients_at_input()

    def back_propagate(self, next_layer, is_input_layer=False):
        for i in range(len(self.neurons)):
            self.neurons[i].gradient = 0
            n1 = self.neurons[i]
            n1.gradient = 0
            for j in range(len(next_layer.neurons)):
                if debug:
                    try:
                        n2 = next_layer.neurons[j]
                        g1 = n2.gradsAtInput
                        print(g1)
                        # next_gradient = self.neurons[i].calculate_gradient( next_layer.neurons[j].gradsAtInput[i] )
                        n1.update_gradient(n2.gradsAtInput[i])
                        print(self.neurons[i].gradient)
                    except:
                        print("error in back_propagate")
            if not is_input_layer:
                self.neurons[i].calculate_gradients_at_input()

    def get_outputs(self):
        ret = []
        for n in self.neurons:
            ret.append(n.output)
        ret = np.asarray([ret]).T
        return ret

    def get_gradients_at_input(self):
        ret = []
        for n in self.neurons:
            ret.append(n.gradAtInput)
        return np.asarray(ret)


class Neuron:

    def __init__(self, number_of_inputs):
        self.synaptic_weights = 2 * np.random.random((1, number_of_inputs + 1)) - 1
        self.output = None
        self.gradients = []
        self.gradsAtInput = None

    # Used as an intermediate that serves the needs of both back propagation
    # and for updating self weights
    # Before calling update_gradient for all down-stream neurons, be sure to clear gradients.
    def update_gradient(self, gradient_at_output, output_index = 0):
        if len(self.gradients) == 0:
            # todo: what should gradient be initialized to?
            self.gradients.append(gradient_at_output)
            print("hard adding gradient to empty list of gradients.")
        else:
            x = gradient_at_output[output_index]
            y = Neuron.sigmoid_derivative(x)  # todo: changed to x confirm correct change
            p = x * y
            self.gradients[0] += p

    # Used after calculate_gradient only for back propagation
    def calculate_gradients_at_input(self):
        if debug:
            try:
                self.gradsAtInput = self.gradients * self.synaptic_weights
            except:
                print("error in calculate_gradients_at_input")
        # print(self.gradAtInput)
        return self.gradsAtInput

    # Uses self.gradients from calculate_gradient

    def train(self):
        pass

    def forward_propagate(self, inputs):
        self.output = self.synaptic_weights.dot(inputs)
        self.output = self.output[0]  # numpy [1x6] * [1x6].T -> python float
        print(self.output)

    @staticmethod
    def sigmoid(x):
        # there are other activation functions that may be used
        return 1 / (1 + np.exp(-x))

    @staticmethod
    def sigmoid_derivative(x):
        return x * (1 - x)


class NonBinaryTestObject:
    def __init__(self, rules=0):
        self.a = random.randint(1, 10)
        self.b = random.randint(1, 5)
        self.c = random.randint(1, 5)
        self.d = random.randint(1, 5)

        if rules == 0:
            self.o = self.apply_rules_0()

    def get_array(self):
        return self.a, self.b, self.c, self.d, 1

    def apply_rules_0(self):
        ret = 0
        if self.a > 7:
            ret += 1
        if self.b > 3:
            ret += 1
        if self.c + self.d < 3:
            ret += 1
        return ret


class TestObject:
    # generate random objects which follow an arbitrary rule pattern defined below.
    def __init__(self, rules):
        self.a = random.randint(0, 1)
        self.b = random.randint(0, 1)
        self.c = random.randint(0, 1)
        self.d = random.randint(0, 1)

        if rules == 0:
            self.score1 = self.apply_rules_0()
        elif rules == 1:
            self.score1 = self.apply_rules_1()
        elif rules == 2:
            self.score1 = self.apply_rules_2()
        elif rules == 3:
            self.score1 = self.apply_rules_3()
        elif rules == 4:
            self.score1 = self.apply_rules_4()
        elif rules == 5:
            self.score1 = self.apply_rules_5()
        else:
            print("error: rule set not defined")

    def apply_rules_0(self):
        if self.a:
            return 0
        if self.b:
            return 1
        if self.c:
            return 0
        if self.d:
            return 1
        return random.randint(0, 1)

    def apply_rules_1(self):
        score = 0
        if self.a:
            score += random.randint(5, 10)
        if self.b:
            score -= random.randint(5, 10)
        if self.c:
            score += random.randint(3, 5)
        if self.d:
            score -= random.randint(3, 5)
        if score > 0:
            return 1
        return 0

    def apply_rules_2(self):
        if self.a == 1 and self.b == 1:
            return 1
        if self.a == 1 and self.c == 1:
            return 0
        if self.b == 0 and self.c == 1:
            return 0
        if self.d == 1:
            return 1
        return 0

    def apply_rules_3(self):
        if self.a + self.b + self.c > 1:
            return 1
        if self.d == 0:
            return 1
        return 0

    def apply_rules_4(self):
        score = self.a * 10 - self.b * 10 + self.c * 5
        if score > 0:
            score = random.randint(1, score) + int(score / 2)
            if score > 5:
                return 1
        return 0

    def apply_rules_5(self):
        score = 0
        self.a = random.randint(1, 10)
        self.b = random.randint(1, 10)
        self.c = random.randint(1, 10)
        self.d = random.randint(1, 5)
        for i in range(self.d * 5):
            if random.randint(1, self.a + 1) == 1:
                score += 6
            if random.randint(1, self.b + 1) == 1:
                score += 4
            if self.c > 5:
                if random.randint(1, self.d + 1) == 1:
                    score -= 2
                else:
                    score += 1
        return score

    def get_array(self):
        return [self.a, self.b, self.c, self.d, 1]


def create_input_and_output_sets(n, rule):
    inputs = []
    outputs = []
    for i in range(n):
        t = TestObject(rule)
        inputs.append(t.get_array())
        outputs.append(t.score1)
    return [np.array(inputs), np.array([outputs]).T]  # .T transforms from many cols to many rows.


def create_non_binary_data_sets(n, rule):
    inputs = []
    outputs = []
    for i in range(n):
        n = NonBinaryTestObject(rule)
        inputs.append(n.get_array())
        outputs.append(n.o)
    return [np.array(inputs), np.array([outputs]).T]


def train_neural_network(neural_network, rule, binary=True):
    number_of_cases = 1000
    training_iterations = 10000
    if binary:
        data = create_input_and_output_sets(number_of_cases, rule)  # creates data from rule for both inputs and outputs
    else:
        data = create_non_binary_data_sets(number_of_cases, rule)
    training_inputs = data[0]  # data returns inputs then outputs, thus 0 then 1.
    training_outputs = data[1]
    neural_network.train(training_inputs, training_outputs, training_iterations)


def evaluate_neural_network(neural_network, rules):
    # applies weights from trained neural network to new data set and then calculates accuracy.
    correct = 0
    trials = 10000
    for i in range(trials):
        t = TestObject(rules)
        prediction = 0
        if neural_network.apply_weights(np.array(t.get_array())) > .5:
            prediction = 1
        if t.score1 == prediction:
            correct += 1

    print("rules:", rules, "correct:", str(round(correct / trials, 4) * 100) + "%")


def evaluate_non_linear_layer(layer, rules):
    # applies weights from trained neural network to new data set and then calculates accuracy.
    correct = 0
    trials = 10000
    for i in range(trials):
        n = NonBinaryTestObject(rules)
        prediction = 0
        if layer.apply_weights(np.array(n.get_array())) > .5:
            prediction = 1
        if n.o == prediction:
            correct += 1

    print("Non-binary rules:", rules, "correct:", str(round(correct / trials, 4) * 100) + "%")


def run():
    pass


def test_case():
    layers = []
    for i in range(4):
        neurons = []
        for j in range(5):
            n = Neuron(5)
            # n.output = .3
            # n.calculate_gradient(.4)
            # n.calculate_gradients_at_input()
            neurons.append(n)
        layers.append(Layer(neurons))
    # last layer has one element
    neurons = [Neuron(5)]
    layers.append(Layer(neurons))
    network = NeuralNetwork(layers)

    na = [[1, 0, 0, 0, 1, 1]]
    na = np.asarray(na).T
    network.forward_propagate(np.asarray(na))
    network.backward_propagate(1)


test_case()
