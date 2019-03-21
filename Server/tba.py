import json
from datetime import datetime

import requests

apiKey = "qMtpanDocP21adkOnPUrWYAsG5oUcanAuNOxIrALrrQoNddXPAQXpZQFxJQLD7Bg"
headers = {"X-TBA-Auth-Key": apiKey}
baseUrl = "https://www.thebluealliance.com/api/v3/"
year = str(datetime.today().year)

# get api status
online = False
try:
    status = json.loads(requests.get(baseUrl + "status", headers=headers).text)
    online = True
except requests.exceptions.ConnectionError:
    # no connection to tba (no internet or tba is down)
    status = "No internet connection"
    online = False


def isOnline():
    return online


def getTeamInfo(teamNumber):
    if not online:
        return

    # returns team name, number, record, etc
    # this is used when giving the general summary of a team
    try:
        toReturn = {}

        # get team name
        teaminfo = json.loads(requests.get(baseUrl + "team/frc{}/simple".format(str(teamNumber)), headers=headers).text)
        toReturn['teamName'] = teaminfo["nickname"]

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
        picture = "files/images/default.jpg"  # default image

        # requests all the images that you would usually see on the tba website
        teamMedia = requests.get(baseUrl + "team/frc{}/media/{}".format(teamNumber, year), headers=headers).json()

        # look through everything, take images that are hosted on either Imgur or Instagram, and download the first one
        for i in teamMedia:
            if i["type"] == "imgur" or i["type"] == "instagram-image":
                image = requests.get(i['direct_url'], allow_redirects=True)

                with open("files/images/{}.jpg".format(teamNumber), 'wb') as img:
                    img.write(image.content)

                picture = "files/images/{}.jpg".format(teamNumber)

        toReturn['media'] = picture
        return toReturn

    except requests.exceptions.ConnectionError:  # no internet access, or tba is down
        return None


def getTeamEvents(team):
    if not online:
        return

    # request events for this year from tba
    eventsJson = json.loads(requests.get(baseUrl + "team/frc{}/events/{}/simple".format(team, year),
                                         headers=headers).text)
    #eventsJson = json.loads(requests.get(baseUrl + "team/frc{}/events/simple".format(str(team)), headers=headers).text)

    events = {}

    for event in eventsJson:
        events[event['name']] = event['key']

    return events


def getTeams(eventKey):
    if not online:
        return

    teamsJson = json.loads(requests.get(baseUrl + "event/{}/teams/simple".format(eventKey), headers=headers).text)
    teams = []
    for team in teamsJson:
        teams.append(team["team_number"])

    return teams


if __name__ == "__main__":
    print(getTeamInfo(254))
    print()
    print(getTeamEvents(254))
    print()
    print(getTeams('2018oncmp1'))
