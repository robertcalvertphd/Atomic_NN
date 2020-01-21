import nflgame
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from CSV_HELPER import CSV_Object
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

    def updatePosition(self):
        self.position = "unassigned"
        qbv = 0
        rbv = 0
        wrv = 0
        for week in self.weekStats:
            if week.passYds > 150:
                qbv += 30
            else:
                if week.recYds > 70 and week.rushYds < 20:
                    wrv += 10
                    wrv += week.recTD * 3

                if week.rushYds > 80:
                    rbv += 10
                    rbv += week.rushTD * 3

                if week.rushYds > 10 and week.passYds > 10:
                    if week.recYds < week.rushYds:
                        rbv += 1
                    else:
                        wrv += 1

        if qbv + wrv + rbv > 10:
            if qbv > wrv and qbv > rbv:
                self.position = "QB"

            if wrv > qbv and wrv > rbv:
                self.position = "WR"

            if rbv > qbv and rbv > wrv:
                self.position = "RB"


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

    for w in range(16):
        games = nflgame.games(2009 + year, week=w + 1)
        players = nflgame.combine_game_stats(games)

        playerIndex = 0
        for p in players:
            if p.passing_att > 10 or p.rushing_att > 5 or p.receiving_yds > 10:
                weekStats = WeekStats(p, p.guess_position, w + 1, 2009 + year,
                                      p.fumbles_lost, p.passing_int, p.passing_yds,
                                      p.rushing_yds, p.receiving_yds, p.passing_tds,
                                      p.rushing_tds, p.receiving_tds)

                if p.name in playerNames:
                    location = playerNames.index(p.name)
                    playersData[location].weekStats.append(weekStats)
                else:
                    playerNames.append(p.name)
                    newPlayer = Player(p.name, playerIndex, p.guess_position)
                    newPlayer.weekStats.append(weekStats)
                    playersData.append(newPlayer)
                    playerIndex += 1
    for p in playersData:
        p.updatePosition()

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

    for player in playerData:
        for week in range(15):
            thisWeek = player.weekStats[week]
            nextWeek = player.weekStats[week + 1]
            if not thisWeek == 0 and not nextWeek == 0:
                # both this week and next week are valid
                goodNextWeek = nextWeek.getGreaterThanCutoff(cutoff)
                d: WeekStats = player.weekStats[week].getWeekAsArray()
                d[7] = goodNextWeek
                data.append(d)
                labels.append(goodNextWeek)
                names.append(player.name)
    return data, labels, names


def calibrate(training, test, model):
    tries = 0
    while 1:
        tries += 1

        samples = [training[0]]
        labels = [training[1]]

        for i in test[0]:
            i[7]=0

        testSamples = [test[0]]
        testLabels = [test[1]]

        model.fit(samples, labels, batch_size=50, epochs=10, shuffle=True, verbose=0)
        predictions = model.predict_classes(testSamples)

        p = sum(predictions / len(predictions))
        print(p)
        if .6 > p > .15:
            #evaluateModel(model, samples2, labels2)
            correct = 0
            attempted = 0
            for i in range(len(predictions)):
                attempted += 1
                prediction = predictions[i]
                test_v = test[1][i]
                if prediction == test_v:
                    correct += 1
            accuracy = correct / attempted
            return predictions, test[2]

        if tries > 20:
            print("failed calibration")
            #runNN(testYear)
            return False

def evaluateModel2(model, data):
    d2 = data
    samples2 = [d2[0]]
    labels2 = d2[1]
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
        Dense(8, input_shape=(8,), activation='relu'),
        Dense(4, activation="relu"),
        Dense(16, activation="relu"),
        Dense(2, activation="softmax")
    ])

    model.compile(Adam(lr=.01), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

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
    trainingYearStats = []
    trainingYearLabels = []
    trainingYearNames = []
    testYearData = position_data[testYearInt]
    position_data.remove(position_data[testYearInt])

    for year in position_data:
        for d in year[0]:
            trainingYearStats.append(d)
        for e in year[1]:
            trainingYearLabels.append(e)
        for f in year[2]:
            trainingYearNames.append(f)
    assert len(trainingYearNames) == len(trainingYearLabels) == len(trainingYearNames)

    trainingYearData = [trainingYearStats, trainingYearLabels, trainingYearNames]
    ret = []
    for i in range(1):
        results = calibrate(trainingYearData, testYearData, model)
        if not results:
            print("invalid")
        else:
            scores = results[0]
            names = results[1]

            yearResults = getTotalFromPairedNamesAndScores(names, scores)
            for r in yearResults:
                ret.append(r)
    evaluateModel2(model, testYearData)
    return ret, getRankedList(players), model


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
    s = "MODEL EVALUATION " + " loss: " + rf(score[0]) + " accuracy " + rf(score[1])
    testWrite(s)

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

        qbsYearsDataSet.append(createDataSet(qbs, 12))
        rbsYearsDataSet.append(createDataSet(rbs, 9))
        wrsYearsDataSet.append(createDataSet(wrs, 9))

        if year == testYear:
            qbsFinalYear = qbs
            rbsFinalYear = rbs
            wrsFinalYear = wrs

    qbModelResults = apply_model_to_year_for_position(qbModel, qbsYearsDataSet, qbsFinalYear, testYear)
    rbModelResults = apply_model_to_year_for_position(rbModel, rbsYearsDataSet, rbsFinalYear, testYear)
    wrModelResults = apply_model_to_year_for_position(wrModel, wrsYearsDataSet, wrsFinalYear, testYear)


    adjusted_year = testYear - 1
    if testYear == 0:
        adjusted_year == 0

    evaluateModel2(qbModel, qbsYearsDataSet[adjusted_year])
    evaluateModel2(rbModel, rbsYearsDataSet[adjusted_year])
    evaluateModel2(wrModel, wrsYearsDataSet[adjusted_year])

    qbRanks = qbModelResults[1]
    rbRanks = rbModelResults[1]
    wrRanks = wrModelResults[1]

    qbResults = qbModelResults[0]
    rbResults = rbModelResults[0]
    wrResults = wrModelResults[0]

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

    nn_qb_total = handleResultsByPosition(qbResults[:5], qbRanks, testYear)
    nn_rb_total = handleResultsByPosition(rbResults[:5], rbRanks, testYear)
    nn_wr_total = handleResultsByPosition(wrResults[:5], wrRanks, testYear)

#    runLogisticRegression(qbs, rbs, wrs)
    regressionResults = createRegressionData(testYear)
    blr_qb_total = handleResultsByPosition(regressionResults[0], qbRanks, testYear, False)
    blr_rb_total = handleResultsByPosition(regressionResults[1], rbRanks, testYear, False)
    blr_wr_total = handleResultsByPosition(regressionResults[2], wrRanks, testYear, False)

    nn_totals = [nn_qb_total,nn_rb_total,nn_wr_total]
    blr_totals = [blr_qb_total, blr_rb_total, blr_wr_total]

    compareModels(nn_totals,blr_totals)


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
                print(player[0], "rank: ", count, rf(place[1]))
                positionTotal += place[1]
    print(rf(positionTotal))
    print("________")

    return positionTotal

def compareModels(NN_totals, BLR_totals):
    # expected format of [qbScore, rbScore, wrScore]
    nn_total = sum(NN_totals)
    br_total = sum(BLR_totals)
    nn_qb = rf(NN_totals[0])
    nn_rb = rf(NN_totals[1])
    nn_wr = rf(NN_totals[2])
    br_qb = rf(BLR_totals[0])
    br_rb = rf(BLR_totals[1])
    br_wr = rf(BLR_totals[2])
    print("NN Score:", "qb:", nn_qb, "rb:", nn_rb, "wr:",nn_wr)
    print("BLR Score:", "qb:", br_qb, "rb:", br_rb, "wr:",br_wr)
    print("NN:", rf(nn_total,6), "vs", "BLR:", rf(br_total,6))
    if nn_total > br_total:
        print("Team Neural Network wins.")
    else:
        print("Team Binary Logistic Regression wins")

    return NN_totals, BLR_totals


def testWrite(string, fileName = "log.txt"):
    file1 = open(fileName, "a")
    file1.write(string +"\n")
    file1.close()


def rf(float, n = 5):
    ret = str(float)
    ret = ret[0:n+1]
    return ret

runNN(3)

for i in range(7):
    pass
    #regressionResults = createRegressionData(i)
    #print(i)
    #runNN(i)

# ______________end of neural network code__________________________
