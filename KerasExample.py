
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import random

class ExamplePlayer():
    def __init__(self):
        self.qbSkill = random.randint(1, 10)
        self.qbSkill += random.randint(1, 10)
        self.wrSkill = random.randint(1,10)
        self.week1 = self.getStats()[0]
        self.week2Score = self.getStats()[1]

    def getStats(self):
        drives = random.randint(5,10)
        atts = 0
        cmpl = 0
        yards = 0
        ints = 0
        tds = 0

        for d in range(drives):
            for i in range(5):
                if random.randint(1,self.qbSkill+2) > 1:
                    atts += random.randint(1,4)
                if random.randint(1,self.qbSkill+2) > 2 and random.randint(1,self.wrSkill+2)>2:
                    yards += random.randint(1,10)
                    if random.randint(1,10) == 10 and self.qbSkill > 5:
                        yards += 40
                        tds += 1
                        i = 8
                    cmpl += 1
                else:
                    if random.randint(1,self.qbSkill+1) == 1 and random.randint(1,4) == 1:
                        ints += 1
                    else:
                        if i ==7 and random.randint(1, self.qbSkill) > 2 and random.randint(1, self.wrSkill) > 2:
                            tds += 1

        score = yards/25 + tds*6 - ints*2
        if score > 20: score = 1
        else: score = 0
        return (atts, cmpl, yards, ints, tds, 1), score



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

def createPlayerDataSet():
    samples = []
    labels = []

    positive = 0
    for i in range(100):
        p = ExamplePlayer()
        samples.append(p.week1)
        labels.append(p.week2Score)
        positive += p.week2Score
    print(positive / 100)
    return samples, labels


model = Sequential([
    Dense(2, input_shape=(6,), activation='relu'),
    Dense(4, activation="relu"),
    Dense(2, activation="softmax")
])

model.compile(Adam(lr=.01), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

d = createPlayerDataSet()
samples = [d[0]]
labels = d[1]

model.fit(samples, labels, batch_size=10, epochs=500, shuffle=True, verbose=2)

