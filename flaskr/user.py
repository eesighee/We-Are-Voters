import functools
import requests
import json
import google.oauth2.credentials
from googleapiclient.discovery import build

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

#from flaskr.db import get_db

bp = Blueprint('user', __name__, url_prefix='/user')
custom_search_api_key = "AIzaSyCM67TJ63naO43I3IvoUWByWO3-WzBG_Ts"
civil_api_key = "AIzaSyCWQtcfGUSNeCNp7K-eRyD4BD9sywFNwG4"

class Contest():

    office = ""
    candidates = []

    def __init__(self, office, candidates):
        self.office = office
        self.candidates = candidates

class Candidate():

    name = ""
    party = ""
    website = ""
    media = {}

    def __init__(self, name, party, website, media):
        self.name = name
        self.party = party
        self.website = website
        self.media = media
        self.image_url = ""

    def setImage(self):
        default_image_path = "/Users/isaialegria/Downloads/not-available.jpg"
        # service = build("customsearch", "v1",
        #           developerKey=custom_search_api_key)

        # res = service.cse().list(
        #     q=self.name,
        #     cx='016870861425249565133:msfjkllfpqs',
        #   ).execute()
        
        # items = res['items']

        # implement logic to find the best image
        # j  = 1
        # for i in items:
        #     print "item", j, ":", i['pagemap']['cse_image'][0]['src']
        #     # if i['pagemap']['cse_image'] is not None:
        #     #   print "item", j, ":", i['pagemap']['cse_image'][0]['src']
        #     j += 1
        # print "It is I, " + self.name + " the culprit"
        # if "cse_image" in items[0]['pagemap']:
        #     self.image_url = items[0]['pagemap']['cse_image'][0]['src']
        # else:
        #     self.image_url = default_image_path
        self.image_url = default_image_path


@bp.route('/submitAddress', methods=['GET', 'POST'])
def submitAddress():
    if request.method == 'POST':
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip code']
        error = None

        if street is None:
            error = 'Please enter your street address'
        elif city is None:
            error = 'Whats yo city dawg'
        elif state is None:
            error = 'Enter yo state g'
        elif zip_code is None:
            error = 'Enter yo zip bruh'

        if error is None:
            session.clear()
            address = street + ' ' + city + ' ' + state + ' ' + zip_code
            session['address'] = address
            return redirect(url_for('user.getUserInfo'))

        flash(error)

    return render_template('user/submitAddress.html')

# this endpoint hits the google civic API and gets voter info for their address
@bp.route('/info', methods=['GET'])
def getUserInfo():
    if request.method == 'GET':

        user_address = session['address']
        split_address = user_address.split()
        percent_guy = "%20"
        google_base_url = "https://www.googleapis.com/civicinfo/v2/voterinfo?key="
        append_str = ''

        for segment in split_address:
            append_str += segment + percent_guy
        
        URL = google_base_url + civil_api_key + "&address=" + append_str + "&electionId=2000"

        r = requests.get(URL)
        data = r.json()
        request_contests = getContests(data)
        contests = createContests(request_contests)

    return render_template('user/info.html', contests=contests)

# takes in JSON returns a list of contests
def getContests(json_text):
    contests = json_text["contests"]
    contest_list = []

    for i in contests:
        contest_list.append(i)

    return contest_list

# extract information from each contest
def createContests(contest_list):

    # return lists
    list_of_contests = []
    list_of_candidates = []

    # variables for candidate
    office = ""
    name = ""
    party = ""
    website = ""
    media = {}

    for contest in contest_list:
        
        # get office from contest
        if 'office' in contest:
            office = contest['office']

        # get candidate info for each contest
        if 'candidates' in contest:
            candidates = contest['candidates']
            #get candidate information
            for i in range(len(candidates)):
                name = candidates[i]['name']
                party = candidates[i]['party']
                if 'candidateUrl' in candidates[i]:
                    candidates[i]['candidateUrl']
                    website = candidates[i]['candidateUrl']
                if 'channels' in candidates[i]: 
                    for j in range(len(candidates[i]['channels'])):
                        media[candidates[i]['channels'][j]['type']] = candidates[i]['channels'][j]['id']
                cand = Candidate(name, party, website, media)
                cand.setImage()
                list_of_candidates.append(cand)
                cont = Contest(office, list_of_candidates)
            list_of_contests.append(cont)
            list_of_candidates = []

    return list_of_contests