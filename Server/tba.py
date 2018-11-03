import json
from datetime import datetime

import requests

apiKey = "qMtpanDocP21adkOnPUrWYAsG5oUcanAuNOxIrALrrQoNddXPAQXpZQFxJQLD7Bg"
headers = {"X-TBA-Auth-Key": apiKey}


def getTeamInfo(teamNumber):
    # returns team name, number, record, etc
    toReturn = {}

    # get team name
    teaminfo = json.loads(requests.get("https://www.thebluealliance.com/api/v3/team/frc" + str(teamNumber) +
                                       "/simple", headers=headers).text)
    toReturn['teamName'] = teaminfo["nickname"]

    year = datetime.now().year

    # get events team attended and their records
    events = json.loads(requests.get("https://www.thebluealliance.com/api/v3/team/frc{}/events/{}/simple"
                                     .format(teamNumber, year), headers=headers).text)
    eventsStatues = json.loads(requests.get("https://www.thebluealliance.com/api/v3/team/frc{}/events/{}/statuses"
                                            .format(teamNumber, year), headers=headers).text)

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


if __name__ == "__main__":
    getTeamInfo(4618)
