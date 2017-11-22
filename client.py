"""This is the main module"""
import random
import webhandler
import sentimentanalyser

def main():
    """Run client"""
    if not webhandler.API_KEY:
        raise ValueError("Set your API_KEY in webhandler.py! Find it on https://devrecruitmentchallenge.com/account")

    analyser = sentimentanalyser.SentimentAnalyser()

    print("Getting challenge list")
    challenge_list = webhandler.get_challenge_list()
    print("There are {} challenges".format(len(challenge_list)))

    for info in challenge_list:
        print("Solving challenge {} - {}".format(info.cid, info.challenge_type))
        challenge = webhandler.get_challenge(info.cid)

        if info.challenge_type == "pertweet":
            handle_pertweet(challenge, analyser, False)
        elif info.challenge_type == "aggregated":
            handle_aggregated(challenge, analyser)
        else:
            print("Unrecognised challenge type '{}'".format(info.challenge_type))

def handle_pertweet(challenge, analyser, verbose=False):
    """Handle a per-tweet challenge"""
    sentiments = {}
    for tweet in challenge.tweets:
        sentiment_list = analyser.analyse_tweet(tweet.tweet, True, verbose)
        sentiments[tweet.tid] = [{'subject': subject, 'sentiment': sentiment} 
                for (subject, sentiment) in sentiment_list]
    submission = {'challengeId': challenge.info.cid, 'perTweetSentiment': sentiments}
    result = webhandler.post_pertweet_submission(submission)
    print("Mark = {}%".format(result.mark))

def handle_aggregated(challenge, analyser):
    """Handle an aggregated challenge"""
    sentiments = {}
    # Just guess
    min_time = min(t.time for t in challenge.tweets)
    max_time = max(t.time for t in challenge.tweets)
    for tweet in challenge.tweets:
        result_list  = analyser.analyse_tweet(tweet.tweet)
        mult = 1
        if (tweet.source.startswith("Verified")):
            mult = 1.5
        for (company,result) in result_list:
            if (not (company in sentiments)):
                sentiments[company] = {}
                for i in range(min_time,max_time+1):
                    sentiments[company][i] = []
            sentiments[company][tweet.time].append(mult*result);
    sols = {}
    for company in sentiments:
        lastval = 0
        for time in sentiments[company]:
            if (not(company in sols)):
                sols[company] = {}
            if (len(sentiments[company][time]) == 0):
                sols[company][time] = lastval
            else:
                lastval = 1.0*sum(sentiments[company][time])/len(sentiments[company][time])
                sols[company][time] = lastval

    submission = {'challengeId': challenge.info.cid, 'sentiments': sols}
    result = webhandler.post_aggregated_submission(submission)
    print ("Mark = {}%".format(result.mark))

if __name__ == "__main__":
    main()
