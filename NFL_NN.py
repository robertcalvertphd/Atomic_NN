import nflgame
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from CSV_HELPER import CSV_Object, createCSV
from NFL_Binary_Logistic_regression import createPlayerDataSets as createRegressionData

# import numpy as np


class PlayerCSV(CSV_Object):
    def __init__(self, name, d):
        name = name
        fumbles = d[0]
        interceptions = d[1]
        passYds = d[2]
        rushYds = d[3]
        recYds = d[4]
        passTD = d[5]
        rushTD = d[6]
        recTD = d[7]

        self.values = [name, fumbles, interceptions, passYds, rushYds, recYds, passTD, rushTD, recTD]
        self.columnNames = "name, fumbles, interceptions, passYds, rushYds, recYds, passTD, rushTD, recTD"


class Player:
    def __init__(self, name, _id, position):
        self.name = name
        self.id = _id
        self.weekStats = []
        self.position = position

    def cleanWeeks(self, year):

        ret = []
        for i in range(16):
            ret.append(0)

        for w in self.weekStats:
            if w.year == year:
                ret[w.week - 1] = w
        self.weekStats = ret

    def getYearScore(self):
        score = 0
        for w in self.weekStats:
            if not w == 0:
                score += w.getPlayerScore()
        return score


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

    def __init__(self, playerName, position, week, year, fumbles, ints, passYds, rushYds, recYds, passTD, rushTD,
                 recTD):
        self.playerName = playerName
        self.position = position
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
        self.goodNextWeek = 0

        self.values = [playerName, fumbles, ints, passYds, rushYds, recYds, passTD, rushTD, recTD, self.goodNextWeek]
        self.columnNames = "name, fumbles, ints, passYds, rushYds, recYds, passTD, rushTD, recTD, goodNextWeek"

    def getPlayerScore(self):
        ret = (self.fumbles + self.interceptions) * -2 + self.passYds / 25 + self.passTD * 4 + self.rushYds / 10 + \
              self.recYds / 10 + self.recTD * 6 + self.rushTD * 6

        return round(ret, 2)

    def getGreaterThanCutoff(self, cutoff):
        if self.getPlayerScore() > cutoff:
            return 1
        return 0

    def getWeekAsArray(self):
        return [self.fumbles, self.interceptions, self.passYds, self.rushYds, self.recYds, self.passTD, self.rushTD,
                self.recTD]

    def set_good_next_week(self, week, cutoff):
        if not week == 0:
            self.goodNextWeek = week.getGreaterThanCutoff(cutoff)
        return self.goodNextWeek


def populatePlayersForYear(year):
    playersData = []
    playerNames = []

    for i in range(16):
        games = nflgame.games(2009 + year, week=i + 1)
        players = nflgame.combine_game_stats(games)

        playerIndex = 0
        for p in players:
            if p.passing_att > 15 or p.rushing_att > 5 or p.receiving_yds > 10:
                weekStats = WeekStats(p, p.guess_position, i + 1, 2009 + year, p.fumbles_lost, p.passing_int,
                                      p.passing_yds,
                                      p.rushing_yds, p.receiving_yds, p.passing_tds, p.rushing_tds, p.receiving_tds)
                if p.name in playerNames:
                    location = playerNames.index(p.name)
                    playersData[location].weekStats.append(weekStats)
                else:
                    playerNames.append(p.name)
                    newPlayer = Player(p.name, playerIndex, p.guess_position)
                    newPlayer.weekStats.append(weekStats)
                    playersData.append(newPlayer)
                    playerIndex += 1

    return sort_players_into_position(playersData, year)


def sort_players_into_position(playersData, year):
    qbs = []
    rbs = []
    wrs = []

    for player in playersData:
        player.cleanWeeks(2009 + year)
        if player.position == 'QB':
            qbs.append(player)
        if player.position == "RB":
            rbs.append(player)
        if player.position == "WR":
            wrs.append(player)

    return playersData, qbs, rbs, wrs


def createDataSet(playerData, cutoff):
    data = []
    labels = []
    names = []
    # print("create data set call")
    for player in playerData:
        for week in range(15):
            a = player.weekStats[week]
            if not a == 0:

                l1 = player.weekStats[week + 1]
                player.weekStats[week].set_good_next_week(l1, cutoff)
                goodNextWeek = a.set_good_next_week(l1, cutoff)
                d: WeekStats = player.weekStats[week].getWeekAsArray()
                d[7] = goodNextWeek
                '''
                l2 = player.weekStats[week + 2]
                if not l1 == 0 and not l2 == 0:
                    w1 = l1.getGreaterThanCutoff(cutoff)
                    w2 = l2.getGreaterThanCutoff(cutoff)
                
                    data.append(d)
                    labels.append(max(w1, w2))
                '''
                if not l1 == 0:
                    w1 = l1.getGreaterThanCutoff(cutoff)
                    data.append(d)
                    labels.append(w1)
                    names.append(player.name)

    return data, labels, names


def calibrate(training, test, model,testYear):
    tries = 0
    while 1:
        tries += 1
        d1 = training
        samples = [d1[0]]
        labels = d1[1]

        d2 = test
        samples2 = [d2[0]]
        labels2 = d2[1]

        model.fit(samples, labels, batch_size=50, epochs=10, shuffle=True, verbose=0)

        predictions = model.predict_classes(samples2)
        p = sum(predictions / len(predictions))
        if .6 > p > .02:
            return predictions, d2[2]

        if tries > 20:
            print("failed calibration")
            #runNN(testYear)
            return False

        evaluateModel(model, samples2, labels2)


def create_score_for_each_player(predictions, all_names):
    names = []
    scores = []
    for name in all_names:
        if not names.__contains__(name):
            names.append([name])

    for name in names:
        index = 0
        score = 0
        for entry in all_names:
            if entry == name:
                score += predictions[index]
            index += 1
        scores.append(score)


def createModel():
    model = Sequential([
        Dense(6, input_shape=(8,), activation='relu'),
        Dense(12, activation="relu"),
        Dense(4, activation="relu"),
        Dense(2, activation="softmax")
    ])

    model.compile(Adam(lr=.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    return model


def getRankedList(players_of_a_certain_position):
    name_score_list = []

    for player in players_of_a_certain_position:
        name = player.name
        score = player.getYearScore()
        name_score_list.append((name, score))

    name_score_list.sort(key=sortSecond, reverse=True)

    return name_score_list


def apply_model_to_year_for_position(model, position_data, players, testYearInt):
    trainingYear = []
    testYearData = position_data[testYearInt]
    position_data.remove(position_data[testYearInt])

    for player_list in position_data:
        for playerStats in player_list:
            trainingYear.append(playerStats)

    ret = []
    for i in range(10):
        results = calibrate(trainingYear, testYearData, model, testYearInt)
        if not results:
            print("invalid")
        else:
            scores = results[0]
            names = results[1]

            yearResults = getTotalFromPairedNamesAndScores(names, scores)
            for r in yearResults:
                ret.append(r)

    return ret, getRankedList(players)


def getTotalFromPairedNamesAndScores(names, scores):
    if len(names) == len(scores):
        newList = []
        counter = 0
        for s in scores:
            entry = [names[counter], s]
            newList.append(entry)
            counter += 1

        handledNames = []
        finalList = []
        for entry in newList:
            name = entry[0]
            if not handledNames.__contains__(name):
                entry = []
                entry = []
                score = 0
                entry.append(name)
                for check_entry in newList:
                    check_name = check_entry[0]
                    if name == check_name:
                        score += check_entry[1]
                entry.append(score)
                finalList.append(entry)
                handledNames.append(name)

        return finalList


def sortSecond(val):
    return val[1]


def separateTuples(tuples):
    names = []
    scores = []
    for t in tuples:
        names.append(t[0])
        scores.append(t[1])

    return names, scores


def evaluateModel(model, samples, labels):
    score = model.evaluate(samples, labels, verbose=2)
    print("loss:", str(score[0]), "accuracy", str(score[1]))


def getPlayer(name, allPlayers):
    for player in allPlayers:
        if player == name:
            return player


def runNN(testYear):
    # yearDataSets = []
    qbModel = createModel()
    rbModel = createModel()
    wrModel = createModel()

    qbsYearsDataSet = []
    wrsYearsDataSet = []
    rbsYearsDataSet = []

    qbsFinalYear = []
    rbsFinalYear = []
    wrsFinalYear = []


    for year in range(7):
        playerData = populatePlayersForYear(year)

        qbs = playerData[1]
        rbs = playerData[2]
        wrs = playerData[3]

        qbsYearsDataSet.append(createDataSet(qbs, 18))
        rbsYearsDataSet.append(createDataSet(rbs, 10))
        wrsYearsDataSet.append(createDataSet(wrs, 10))

        if year == testYear:
            qbsFinalYear = qbs
            rbsFinalYear = rbs
            wrsFinalYear = wrs

    qbResults = apply_model_to_year_for_position(qbModel, qbsYearsDataSet, qbsFinalYear, testYear)
    rbResults = apply_model_to_year_for_position(rbModel, rbsYearsDataSet, rbsFinalYear, testYear)
    wrResults = apply_model_to_year_for_position(wrModel, wrsYearsDataSet, wrsFinalYear, testYear)

    qbRanks = qbResults[1]
    rbRanks = rbResults[1]
    wrRanks = wrResults[1]

    qbResults = qbResults[0]
    rbResults = rbResults[0]
    wrResults = wrResults[0]

    if not qbResults or not rbResults or not wrResults:
        print("rerunning")
        runNN(testYear)

    qbResults = separateTuples(qbResults)
    rbResults = separateTuples(rbResults)
    wrResults = separateTuples(wrResults)

    qbResults = getTotalFromPairedNamesAndScores(qbResults[0], qbResults[1])
    rbResults = getTotalFromPairedNamesAndScores(rbResults[0], rbResults[1])
    wrResults = getTotalFromPairedNamesAndScores(wrResults[0], wrResults[1])

    qbResults.sort(key=sortSecond, reverse=True)
    wrResults.sort(key=sortSecond, reverse=True)
    rbResults.sort(key=sortSecond, reverse=True)

    handleResultsByPosition(qbResults[:5], qbRanks, testYear)
    handleResultsByPosition(rbResults[:5], rbRanks, testYear)
    handleResultsByPosition(wrResults[:5], wrRanks, testYear)

#    runLogisticRegression(qbs, rbs, wrs)
    regressionResults = createRegressionData(testYear)
    handleResultsByPosition(regressionResults[0], qbRanks, testYear, False)
    handleResultsByPosition(regressionResults[1], rbRanks, testYear, False)
    handleResultsByPosition(regressionResults[2], wrRanks, testYear, False)


def handleResultsByPosition(picks, trueValues, testYear, NN = True):
    if NN:
        print("top 5 NN picks for this position:" + str(testYear))
    else:
        print("top 5 BLR picks for this position:" + str(testYear))
    trueValues.sort(key=sortSecond, reverse=True)
    positionTotal = 0
    for player in picks:
        count = 0
        for place in trueValues:
            count += 1
            if player[0] == place[0]:
                print(player[0], "rank: ", count, place[1])
                positionTotal += place[1]
    print(positionTotal)
    print("________")

def calculateScoreForPicks(picks):
    for pick in picks:
        getPlayer()



for i in range(7):
    regressionResults = createRegressionData(i)
    print(i)
    #runNN(i)

# ______________end of neural network code__________________________
