
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import random
class TestObject:
    def __init__(self):
        self.weight = random.randint(25,40) + 10
        self.height = random.randint(1,7) + 52
        self.male = random.randint(0,1)
        if self.male:
            increasedHeight = random.randint(5,15)
            increasedWeight = int(increasedHeight * 1.8)
            self.weight += increasedWeight
            self.height += increasedHeight

    def getStats(self):
        return [self.weight, self.height], self.male


def createDataSet():
    samples = []
    labels = []

    for i in range(1000):
        t = TestObject()
        s = t.getStats()
        samples.append(s[0])
        labels.append(s[1])
    return samples, labels



model = Sequential([
    Dense(2, input_shape=(2,), activation='relu'),
    Dense(4, activation="relu"),
    Dense(2, activation="softmax")
])

model.compile(Adam(lr=.01), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

d = createDataSet()
samples = [d[0]]
labels = d[1]

model.fit(samples, labels, batch_size=10, epochs=50, shuffle=True, verbose=2)

