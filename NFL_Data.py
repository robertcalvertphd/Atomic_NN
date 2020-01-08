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

def populateQBsForYear(year):
    qbs = []
    qbNames = []
    for i in range(16):
        try:
            games = nflgame.games(2009 + year, week=i + 1)
        except:
            print("error" + str(year) + " " + str(i))
        players = nflgame.combine_game_stats(games)

        # get list of all qbs who played this week
        qbIndex = 0
        for p in players.passing():
            if p.passing_att > 5:
                weekStats = WeekStats(p, i + 1, 2009 + year, p.fumbles_lost, p.passing_int, p.passing_yds,
                                      p.rushing_yds, p.receiving_yds, p.passing_tds, p.rushing_tds, p.receiving_tds)
                if p.name in qbNames:
                    location = qbNames.index(p.name)
                    qbs[location].weekStats.append(weekStats)
                else:
                    qbNames.append(p.name)
                    newQb = Player(p.name, qbIndex)
                    newQb.weekStats.append(weekStats)
                    qbs.append(newQb)
                    #print(p.name)
                    qbIndex += 1
    for qb in qbs:
        qb.cleanWeeks(2010)
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
        #print(m)

    return qbs

players = []
weeks = []
qbs = populateQBsForYear(1)

def createDataSet():
    data = []
    labels = []
    for qb in qbs:
        for week in range(14):
            a = qb.weekStats[week]
            if not a == 0:
                data.append(a.getWeekAsArray())

            l = qb.weekStats[week+1]
            if not l == 0:
                labels.append(l.getGreaterThanCutoff(20))



    return data, labels

createDataSet()



model = Sequential([
    Dense(6, input_shape=(8,), activation='relu'),
    Dense(4, activation="relu"),
    Dense(2, activation="softmax")
])

model.compile(Adam(lr=.01), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

d = createDataSet()
samples = [d[0]]
labels = d[1]

model.fit(samples, labels, batch_size=50, epochs=25, shuffle=True, verbose=2)

