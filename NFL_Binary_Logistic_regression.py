import nflgame
from CSV_HELPER import CSV_Object, createCSV
import math
writingCSVs = False


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

    def updateGoodWeeks(self):
        cutoff = 0
        if self.position == 'QB':
            cutoff = 18
        if self.position == "RB":
            cutoff = 10
        if self.position == "WR":
            cutoff = 10
        if cutoff > 0:
            index = -1
            for week in self.weekStats:
                index += 1
                if index < 15:
                    nextWeek = self.weekStats[index + 1]
                    if not week == 0 and not nextWeek == 0:
                        nextWeekisGood = nextWeek.getGreaterThanCutoff(cutoff)
                        week.goodNextWeek = nextWeekisGood
                        week.updateCSVvalues()

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

    def __init__(self, playerName, position, week, year, fumbles, interceptions, passYds, rushYds, recYds, passTD,
                 rushTD, recTD):
        self.playerName = playerName
        self.position = position
        self.week = week
        self.year = year
        self.fumbles = fumbles
        self.interceptions = interceptions
        self.passYds = passYds
        self.rushYds = rushYds
        self.recYds = recYds
        self.passTD = passTD
        self.rushTD = rushTD
        self.recTD = recTD
        self.goodNextWeek = 0
        self.updateCSVvalues()
        self.columnNames = "name, fumbles, ints, passYds, rushYds, recYds, passTD, rushTD, recTD, goodNextWeek"

    def updateCSVvalues(self):
        self.values = [self.playerName, self.fumbles, self.interceptions, self.passYds, self.rushYds, self.recYds,
                       self.passTD, self.rushTD, self.recTD, self.goodNextWeek]

    def getPlayerScore(self):
        ret = (self.fumbles + self.interceptions) * -2 + self.passYds / 25 + self.passTD * 4 + self.rushYds / 10 + self.recYds / 10 + self.recTD * 6 + self.rushTD * 6

        return round(ret, 2)

    def getGreaterThanCutoff(self, cutoff):
        if self.getPlayerScore() > cutoff:
            return 1
        return 0

    def getWeekAsArray(self):
        return [self.fumbles, self.interceptions, self.passYds, self.rushYds, self.recYds, self.passTD, self.rushTD,
                self.recTD, self.goodNextWeek]


def rf(float, n = 5):
    ret = str(float)
    ret = ret[0:n+1]
    return ret


def sort_players_into_position(playersData, year):
    qbs = []
    rbs = []
    wrs = []

    for player in playersData:
        player.cleanWeeks(2009 + year)
        player.updateGoodWeeks()
        if player.position == 'QB':
            qbs.append(player)
        if player.position == "RB":
            rbs.append(player)
        if player.position == "WR":
            wrs.append(player)

    return playersData, qbs, rbs, wrs


def populatePlayersForYear(year):
    playersData = []
    playerNames = []

    for i in range(16):
        games = nflgame.games(2009 + year, week=i + 1)
        players = nflgame.combine_game_stats(games)

        playerIndex = 0
        for p in players:
            if p.passing_att > 15 or p.rushing_att > 5 or p.receiving_yds > 10:
                weekStats = WeekStats(p, p.guess_position, i + 1, 2009 + year, p.fumbles_lost, p.passing_ints, p.passing_yds, p.rushing_yds, p.receiving_yds, p.passing_tds, p.rushing_tds, p.receiving_tds)
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


def createPlayerDataSets(testYear):
    allQbs = []
    allWrs = []
    allRbs = []
    ret = []

    for year in range(7):
        qbs = []
        rbs = []
        wrs = []

        playerData = populatePlayersForYear(year)
        qbs = playerData[1]
        rbs = playerData[2]
        wrs = playerData[3]

        a = len(qbs) + len(rbs) + len(wrs)

        for q in qbs:
            allQbs.append(q)
        for r in rbs:
            allRbs.append(r)
        for w in wrs:
            allWrs.append(w)

        if year == testYear:
            if writingCSVs:
                createCSVs(qbs, wrs, rbs, year)
            ret = evaluateModelWithTestData(qbs, wrs, rbs)
    if writingCSVs:
        createCSVs(allQbs, allWrs, allRbs, "all_but_" + str(testYear))
    return ret


def createPositionCSV(positionData, fileName, year):
    weekData = []
    for p in positionData:
        for week in p.weekStats:
            if not week == 0:
                weekData.append(week)

    createCSV(fileName, weekData, year)


def createCSVs(qbs, wrs, rbs, testYear):
    createPositionCSV(qbs, "qbs", testYear)
    createPositionCSV(wrs, "wrs", testYear)
    createPositionCSV(rbs, "rbs", testYear)


def binaryLogistic(week, arrayOfCoefficients):
    ret = arrayOfCoefficients[0]

    weekArray = week.getWeekAsArray()

    for i in range(len(weekArray) - 1):
        ret += weekArray[i] * arrayOfCoefficients[i + 1]
    return ret


def sortSecond(val):
    return val[1]


def logit2prob(logit):
    odds = math.exp(logit)
    prob = odds / (1 + odds)
    return prob


def evaluatePosition(players, coefficients, probability_cutoff, position_cutoff):
    ret = []
    attempted = 0
    correct = 0
    for p in players:
        score = 0
        name = p.name
        for week in p.weekStats:
            if not week == 0:
                attempted += 1
                predicted = logit2prob(binaryLogistic(week, coefficients)) > probability_cutoff
                if predicted:
                    score += 1
                result = week.getPlayerScore() > position_cutoff
                if result == predicted:
                    correct += 1
        ret.append((name, score))

    p = round(correct/attempted,2)
    print(rf(correct), "of", rf(attempted), rf(p*100), "%")
    ret.sort(key=sortSecond, reverse=True)
    return ret


def evaluateModelWithTestData(qbs, wrs, rbs):
    qbCutoff = 18
    rbCutoff = 12
    wrCutoff = 12

    #                 intercept, fumbles, ints, passYd, rushYd, recYd, passTD, rushTD, recTD
    qbCoefficients = [-1.84, -.248, -.166, .0033947, .0062, 0, .0948, .111, 0]
    rbCoefficients = [-1.0116, 0, 0, 0, .0076457, .0099777, 0, 0, 0]
    wrCoefficients = [-2.2613, 0, 0, 0, .02128, .0112349, 0, 0, 0]

    qbValues = evaluatePosition(qbs, qbCoefficients, .3, qbCutoff)
    wrValues = evaluatePosition(wrs, wrCoefficients, .3, wrCutoff)
    rbValues = evaluatePosition(rbs, rbCoefficients, .3, rbCutoff
                                )
    qbValues.sort(key=sortSecond, reverse=True)
    wrValues.sort(key=sortSecond, reverse=True)
    rbValues.sort(key=sortSecond, reverse=True)

    return qbValues[:5], rbValues[:5], wrValues[:5]

