"""Analyse tweets"""
import webhandler
import numpy as np

def edit_dist(a,b):
    sol=np.zeros((len(a),len(b)))
    for i in range(len(a)):
        for j in range(len(b)):
            add=0
            if a[i]==b[j]:
                add += 1
            if i==0 or j==0:
                sol[i][j]=add
            else:
                if add:
                    sol[i][j]=sol[i-1][j-1]+1
                else:
                    sol[i][j]=max(sol[i][j-1],sol[i-1][j])
    return sol[len(a)-1][len(b)-1] - abs(len(a) - len(b))


class SentimentAnalyser(object):
    def __init__(self):
        self.negative_words = webhandler.get_negative_words()
        self.neutral_words = webhandler.get_neutral_words()
        self.positive_words = webhandler.get_positive_words()
        self.companies = webhandler.get_company_info()

        self.company_names = [c.name for c in self.companies]

    def analyse_tweet(self, tweet):
        """Analyse a tweet, extracting the subject and sentiment"""
        sentiment = 0
        subject = self.tweet_subject(tweet)
        negated = False

        for word in tweet.split(" "):
            if word in self.positive_words:
                sentiment = sentiment + 1
            if word in self.negative_words:
                sentiment = sentiment - 1
            if word.upper() == 'NOT':
                negated = not negated

        if sentiment < 0:
            sentiment = -1
        elif sentiment > 0:
            sentiment = 1
        if negated:
            sentiment = -sentiment

        return [(subject, sentiment)]

    def tweet_subject(self, tweet):
        best = None
        best_my = None
        best_score = -1

        for name in self.company_names:
            candidates = tweet.split(' ')
            if ' ' in name:
                candidates = [a + ' ' + b for a, b in zip(candidates, candidates[1:])]

            for c in candidates:
                score = edit_dist(c, name)
                if score > best_score:
                    best_score = score
                    best = name
                    best_my = c

        # print(best, best_my, best_score)
        return best
