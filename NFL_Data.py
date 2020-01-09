import nflgame
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import random

from CSV_HELPER import *


class Player():
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.weekStats = []

    def cleanWeeks(self, year):

        ret = []
        for i in range(16):
            ret.append(0)

        for w in self.weekStats:
            if w.year == year:
                ret[w.week - 1] = w
        self.weekStats = ret

class WeekStats(CSV_Object):
    PLAYER_NAME = 0
    FUMBLES = 1
    INTS = 2
    PASS_YDS = 3
    RUSH_YDS = 4
    REC_YDS = 5
    PASS_TD = 6
    RUSH_TD = 7
    REC_TD = 8

    def __init__(self, playerName, week, year, fumbles, ints, passYds, rushYds, recYds, passTD, rushTD, recTD):
        self.playerName = playerName
        self.week = week
        self.year = year
        self.fumbles = fumbles
        self.interceptions = ints
        self.passYds = passYds
        self.rushYds = rushYds
        self.recYds = recYds
        self.passTD = passTD
        self.rushTD = rushTD
        self.recTD = recTD
        goodWeek = self.getGreaterThanCutoff(20)
        self.values = (playerName, week, year, fumbles, ints, passYds, rushYds, recYds, passTD, rushTD, recTD, goodWeek)
        self.columnNames = ("playerName, week, year, fumbles, ints, passYds, rushYds, recYds, passTD, rushTD, recTD, goodWeek")
        weeks.append(self)
    # this is incomplete but will serve my purposes if I am interested later I can add long rushes/recepts/2pts etc

    def getPlayerScore(self):
        ret = (self.fumbles + self.interceptions) * -2 + self.passYds / 25 + self.passTD * 4 + self.rushYds / 10 + self.recYds / 10 + self.recTD * 6 + self.rushTD * 6
        return (round(ret, 2))

    def getGreaterThanCutoff(self,cutoff):
        if self.getPlayerScore() > cutoff: return 1
        return 0

    def getStatFromID(self, id):
        if id == WeekStats.FUMBLES:
            return self.fumbles
        elif id == WeekStats.INTS:
            return self.interceptions
        elif id == WeekStats.PASS_YDS:
            return self.passYds
        elif id == WeekStats.RUSH_YDS:
            return self.rushYds
        elif id == WeekStats.REC_YDS:
            return self.recYds
        elif id == WeekStats.PASS_TD:
            return self.passTD
        elif id == WeekStats.RUSH_TD:
            return self.rushTD
        elif id == WeekStats.REC_TD:
            return self.recTD
        print("ERROR: getStatFromID fed invalid ID")

    def getWeekAsArray(self):
        return [self.fumbles, self.interceptions, self.passYds, self.rushYds, self.recYds, self.passTD, self.rushTD,
                self.recTD]


def myRound(n):
    return int(n * 100) / 100

allQBWeeks = []
allQBs = []
def populateQBsForYear(year):
    global allQBs
    qbs = []
    qbNames = []
    for i in range(16):
        games = nflgame.games(2009 + year, week=i + 1)
        players = nflgame.combine_game_stats(games)

        # get list of all qbs who played this week
        qbIndex = 0
        for p in players.passing():
            if p.passing_att > 15:
                weekStats = WeekStats(p, i + 1, 2009 + year, p.fumbles_lost, p.passing_int, p.passing_yds,
                                      p.rushing_yds, p.receiving_yds, p.passing_tds, p.rushing_tds, p.receiving_tds)
                allQBWeeks.append(weekStats)
                if p.name in qbNames:
                    location = qbNames.index(p.name)
                    qbs[location].weekStats.append(weekStats)
                else:
                    qbNames.append(p.name)
                    newQb = Player(p.name, qbIndex)
                    newQb.weekStats.append(weekStats)
                    qbs.append(newQb)
                    qbIndex += 1

    for qb in qbs:
        allQBs.append(qb)
        qb.cleanWeeks(2009+year)
        m = qb.name + ": "
        sumOfScores = 0
        for week in qb.weekStats:
            if week == 0:
                score = 0
            else:
                score = myRound(week.getPlayerScore())
            sumOfScores += score
            m += str(score) + " , "
        m += str(myRound(sumOfScores))

    return qbs


def createDataSet(playerData):
    data = []
    labels = []
    names = []
    for player in playerData:
        for week in range(14):
            a = player.weekStats[week]
            if not a == 0:
                d = a.getWeekAsArray()

            l = player.weekStats[week+1]
            l2 = player.weekStats[week+2]
            if not l == 0 and not l2 == 0:
                w1 = l.getGreaterThanCutoff(21)
                w2 = l2.getGreaterThanCutoff(21)
                data.append(d)
                labels.append(max(w1,w2))
                names.append(player.name)
    return data, labels, names

players = []
weeks = []

qbs = populateQBsForYear(1)
q2 = populateQBsForYear(2)




model = Sequential([
    Dense(6, input_shape=(8,), activation='relu'),
    Dense(4, activation="relu"),
    Dense(2, activation="softmax")
])

model.compile(Adam(lr=.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

def calibrateToReasonableYesNo():
    while 1:
        d1 = createDataSet(allQBs)
        samples = [d1[0]]
        labels = d1[1]

        d2 = createDataSet(q2)
        samples2 = [d2[0]]
        labels2 = d2[1]

        model.fit(samples, labels, batch_size=50, epochs=10, shuffle=True, validation_split = 0.1, verbose=2)

        #score = model.evaluate(samples2, labels2, verbose=2)
        #print("loss:",str(score[0]),"accuracy",str(score[1]))

        predictions = model.predict_classes(samples2)
        p = sum(predictions/len(predictions))
        if p <.3 and p > .02:
            score = model.evaluate(samples2, labels2, verbose=2)
            print("loss:",str(score[0]),"accuracy",str(score[1]))
            print(predictions)
            print(sum(predictions))
            return predictions, d2[2]

tagged_names = []
def runInstance():
    global tagged_names
    p = calibrateToReasonableYesNo()
    predictions = p[0]
    matchedName = p[1]

    i = 0
    names = []
    for prediction in predictions:
        if prediction == 1:
            print(i, matchedName[i])
            names.append(matchedName[i])
        i += 1
    for n in names:
        tagged_names.append(n)

def sortSecond(val):
    return val[1]

def getQBPicks():
    ret = []
    for i in range(20):
        runInstance()

    tagged_names.sort()
    handled = []
    for name in tagged_names:
        if not handled.__contains__(name):
            handled.append(name)

    for name in handled:
        #print(name, str(tagged_names.count(name)))
        ret.append([name, tagged_names.count(name)])

    ret.sort(key=sortSecond)
    length = len(ret)
    for i in range(5):

        print(ret[length-(i+1)])

getQBPicks()