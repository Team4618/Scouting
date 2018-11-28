import json
from datetime import datetime

import requests

apiKey = "qMtpanDocP21adkOnPUrWYAsG5oUcanAuNOxIrALrrQoNddXPAQXpZQFxJQLD7Bg"
headers = {"X-TBA-Auth-Key": apiKey}
baseUrl = "https://www.thebluealliance.com/api/v3/"


def getTeamInfo(teamNumber):
    # returns team name, number, record, etc
    # this is used when giving the general summary of a team
    try:
        toReturn = {}

        # get team name
        teaminfo = json.loads(requests.get(baseUrl + "team/frc" + str(teamNumber) + "/simple", headers=headers).text)
        toReturn['teamName'] = teaminfo["nickname"]

        year = datetime.now().year

        # get events team attended and their records
        events = json.loads(requests.get(baseUrl + "team/frc{}/events/{}/simple".format(teamNumber, year),
                                         headers=headers).text)
        eventsStatues = json.loads(requests.get(baseUrl + "team/frc{}/events/{}/statuses".format(teamNumber, year),
                                                headers=headers).text)

        attendedEvents = {}

        for i in events:
            # grab their record for that event
            # check if event hasn't happened
            if datetime.now() < datetime.strptime(i['start_date'], '%Y-%m-%d'):  # competition happens in the future
                continue

            # get the record
            eventStatus = eventsStatues[i['key']]

            try:
                losses = eventStatus['qual']['ranking']['record']['losses']
                ties = eventStatus['qual']['ranking']['record']['ties']
                wins = eventStatus['qual']['ranking']['record']['wins']
            except TypeError:  # usually for special events (like special events at districts
                continue

            attendedEvents[i['name']] = "{}-{}-{}".format(wins, ties, losses)

        toReturn['attendedEvents'] = attendedEvents

        # get teams media
        defualtPicture = "files/images/default.jpg"

        toReturn['media'] = defualtPicture
        return toReturn

    except requests.exceptions.ConnectionError:  # no internet access, or tba is down
        return None


def getTeamEvents(team):
    # request events for this year from tba
    eventsJson = json.loads(requests.get(baseUrl + "team/frc{}/events/{}/simple".format(str(team), str(datetime.today()
                                                                                                       .year)),
                                         headers=headers).text)

    events = {}

    for event in eventsJson:
        events[event['name']] = event['key']

    return events


def getTeams(eventKey):
    teamsJson = json.loads(requests.get(baseUrl + "event/{}/teams/simple".format(eventKey), headers=headers).text)
    teams = []
    for team in teamsJson:
        print(team)
        teams.append(team["team_number"])

    return teams


if __name__ == "__main__":
    print(getTeamInfo(4618))
    print()
    print(getTeamEvents(4618))
    print()
    print(getTeams('2018oncmp1'))
