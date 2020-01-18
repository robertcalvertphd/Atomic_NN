import nflgame
from CSV_HELPER import CSV_Object, createCSV


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
        if self. position == "RB":
            cutoff = 10
        if self.position == "WR":
            cutoff = 10
        if cutoff > 0:
            index = -1
            for week in self.weekStats:
                index += 1
                if index < 15:
                    nextWeek = self.weekStats[index+1]
                    if not week == 0 and not nextWeek == 0:
                        nextWeekisGood = nextWeek.getGreaterThanCutoff(cutoff)
                        week.goodNextWeek = nextWeekisGood
                        week.updateCSVvalues()


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

    def __init__(self, playerName, position, week, year, fumbles, interceptions, passYds, rushYds, recYds, passTD, rushTD, recTD):

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
        self.values = [self.playerName, self.fumbles, self.interceptions, self.passYds, self.rushYds, self.recYds, self.passTD, self.rushTD, self.recTD, self.goodNextWeek]


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
                self.recTD, self.goodNextWeek]


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
                weekStats = WeekStats(p, p.guess_position, i + 1, 2009 + year, p.fumbles_lost, p.passing_ints,
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


def createPlayerDataSets():
    allQbs = []
    allWrs = []
    allRbs = []

    for year in range(7):
        playerData = populatePlayersForYear(year)
        qbs = playerData[1]
        rbs = playerData[2]
        wrs = playerData[3]

        for q in qbs:
            allQbs.append(q)
        for r in rbs:
            allRbs.append(r)
        for w in wrs:
            allWrs.append(w)

        if year == 6:
            createCSVs(qbs, wrs, rbs, year)
    createCSVs(allQbs, allWrs, allRbs, "_1_6")


def createPositionCSV(positionData, fileName, year):
    weekData = []
    for p in positionData:
        for week in p.weekStats:
            if not week == 0:
                weekData.append(week)

    createCSV(fileName, weekData, year)


def createCSVs(qbs, wrs, rbs, year):
    createPositionCSV(qbs, "qbs", year)
    createPositionCSV(wrs, "wrs", year)
    createPositionCSV(rbs, "rbs", year)


createPlayerDataSets()

