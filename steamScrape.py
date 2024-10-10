import requests
import urllib.parse
from time import sleep
import os
from dotenv import load_dotenv
from urllib.parse import quote
import pickle
import re

load_dotenv()

KEY = os.getenv('KEY')

def getUserReviews(reviewAppid, params):
    #userReviewsUrl = f'https://store.steampowered.com/appreviews/{reviewAppid}'
    cursor = params['cursor']
    userReviewsUrl = f"https://store.steampowered.com/appreviews/{reviewAppid}?json=1&cursor={cursor}&filter_offtopic_activity=0&filter=recent&language=english&num_per_page=100"
    userReviewsResponse = requests.get(
            userReviewsUrl,
            #params=params
        )
    print(f"Status Code: {userReviewsResponse.status_code}")
    

    if (userReviewsResponse.status_code != 200) and (userReviewsResponse.status_code != 429):
        print(f'Fail to get response for {reviewAppid}. Status code: {userReviewsResponse.status_code}')
        return {'success' : 0}, userReviewsResponse.status_code
    try:
        userReviews = userReviewsResponse.json()
    except:
        return {"success": 0}, userReviewsResponse.status_code
    return userReviews, userReviewsResponse.status_code

gamesOfInterestFemale = {
    #'870780' : 'Control Ultimate Edition',
    #'752590' : 'A Plague Tale Innocence',
    '750920' : 'Shadow of the Tomb Raider',
    '414340' : "Hellblade: Senua's Sacrifice",
    '524220' : 'Nier:Automata',
    '1265920' : 'Life is Strange Remastered',
}

gamesOfInterestMale = {
    '108710' : 'Alan Wake',
    '532210' : 'Life is Strange 2',
    '1659420' : 'Uncharted: Legacy of Thieves Collection',
    '814380' : 'Sekiro: Shadows Die Twice - GOTY Edition',
    '1687950' : 'Persona 5 Royal',
    '2050650' : 'Resident Evil 4'
}

allGamesOfInterest = {
    'female' : gamesOfInterestFemale,
    'male' : gamesOfInterestMale    
}

def parseResponse(gameId, gameTitle):
    reviewsSkipped = 0
    reviews = []
    name = gameTitle
    reviewMax = 100
    #reviewMax = 20
    params = {
            #'json' : 1,
            #'language' : 'english',
            'cursor' : '*',
            #'filter_offtopic_activity' : 1,
            #'num_per_page': 100,
            #'key' : KEY,
            #'filter' : 'recent'
    }
    while(True):
        reviewMin = reviewMax - 100
        #reviewMin = reviewMax - 20
        print(f"Getting Reviews: {reviewMin}-{reviewMax} for {name}")
        print(f"Params: {params}")
        response,status = getUserReviews(gameId,params)
        if status == 429:
            print(f"Rate Limiting")
            sleep(300)
            continue
        print(f"Extracted {len(response['reviews'])} reviews")
        #print(response['reviews'])
        #if response['success'] != 1:
        #    print(f'Fail to get response for {gameId}.')
        #    return {'allReviewsGot' : 0}, []

        for review in response['reviews']:
            try:
                recommendationId = review['recommendationid']

                timestampCreated = review['timestamp_created']
                timestampUpdated = review['timestamp_updated']

                authorSteamId = review['author']['steamid']
                playtimeForever = review['author']['playtime_forever']
                playtimeLastTwoWeeks = review['author']['playtime_last_two_weeks']
                playtimeAtReviewMinutes = review['author']['playtime_at_review']
                lastPlayed = review['author']['last_played']

                reviewText = review['review']
                votedUp = review['voted_up']
                votesUp = review['votes_up']
                votesFunny = review['votes_funny']
                weightedVoteScore = review['weighted_vote_score']
                steamPurchase = review['steam_purchase']
                receivedForFree = review['received_for_free']
                writtenDuringEarlyAccess = review['written_during_early_access']

                myReviewDict = {
                    'recommendationid': recommendationId,
                    'authorSteamid': authorSteamId,
                    'playtimeAtReviewMinutes': playtimeAtReviewMinutes,
                    'playtimeForeverMinutes': playtimeForever,
                    'playtimeLastTwoWeeksMinutes': playtimeLastTwoWeeks,
                    'lastPlayed': lastPlayed,

                    'reviewText': reviewText,
                    'timestampCreated': timestampCreated,
                    'timestampUpdated': timestampUpdated,

                    'votedUp': votedUp,
                    'votesUp': votesUp,
                    'votesFunny': votesFunny,
                    'weightedVoteScore': weightedVoteScore,
                    'steamPurchase': steamPurchase,
                    'receivedForFree': receivedForFree,
                    'writtenDuringEarlyAccess': writtenDuringEarlyAccess,
                }
                reviews.append(myReviewDict)
            except:
                print("Skipped Review")
                reviewsSkipped += 1
                print(f'Reviews Skipped: {reviewsSkipped}')
        if response['cursor'] == params['cursor']:
            return reviews
        
        if response['query_summary']['num_reviews'] == 0:
            print(f'No more reviews: {response}')
            return reviews
        
        try:
            cursor = response['cursor']
            print(cursor)
            params['cursor'] = quote(cursor)
            print(params['cursor'])
        except:
            return reviews
        
        reviewMax += 100
        #reviewMax += 20
        sleep(1.5)



steamIDs = ['870780','752590','750920','414340','524220','1265920','108710','532210','1659420','814380','1687950','2050650']

'''
while (steamIDs):
    for key,items in allGamesOfInterest.items():
        for key,val in items.items():
            info, reviews = parseResponse(key,val)
            title = val.strip().replace(" ","_").lower()
            titleClean = re.sub(r'[^\w_. -]', '_', title)
            data = [key,info,reviews]
            if info['allReviewsGot'] == 1:
                with open(f'{titleClean}.pkl','wb') as f:
                    pickle.dump(data,f)
                try:
                    steamIDs.remove(key)
                except:
                    print("Crying is a free action")
            else:
                print(f"Failed to get all data, Only scraped: {len(reviews)} reviews")
                print()            
    sleep(3600)
'''
for key,items in allGamesOfInterest.items():
        for key,val in items.items():
            reviews = parseResponse(key,val)
            title = val.strip().replace(" ","_").lower()
            titleClean = re.sub(r'[^\w_. -]', '_', title)
            data = {key : reviews}
            with open(f'./data/pkl/{titleClean}.pkl','wb') as f:
                pickle.dump(data,f)
            try:
                steamIDs.remove(key)
                print(f"{len(steamIDs)} games left")
            except:
                print("Crying is a free action")