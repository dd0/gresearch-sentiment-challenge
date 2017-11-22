"""Analyse tweets"""
import webhandler
import numpy as np

def edit_dist(a,b):
    # hack to avoid recognising these as same
    if a == 'Entertainment' and b == 'Oystertainment':
        return 10
    elif a == 'Oystertainment' and b == 'Entertainment':
        return 10
    
    sol=np.zeros((len(a),len(b)))
    for i in range(len(a)):
        for j in range(len(b)):
            add=0
            if a[i]==b[j]:
                add += 1
            if i==0 or j==0:
                sol[i][j]=add
                if i>0:
                    sol[i][j]=max(sol[i][j],sol[i-1][j])
                if j>0:
                    sol[i][j]=max(sol[i][j],sol[i][j-1])
            else:
                if add:
                    sol[i][j]=sol[i-1][j-1]+1
                else:
                    sol[i][j]=max(sol[i][j-1],sol[i-1][j])
    # return (sol[len(a)-1][len(b)-1] - abs(len(a) - len(b))) / len(b)
    return (len(a) + len(b) - 2 * sol[len(a) - 1][len(b) - 1]) / 2


class SentimentAnalyser(object):
    def __init__(self):
        self.negative_words = webhandler.get_negative_words()
        self.neutral_words = webhandler.get_neutral_words()
        self.positive_words = webhandler.get_positive_words()
        self.companies = webhandler.get_company_info()
        self.comparison_words = ['better', 'worse', 'prefer']
        self.company_names = [c.name for c in self.companies]

<<<<<<< HEAD
    def splitt(self, tweet):
        subject1 = None
        subject2 = None
        negated = False
        for word in tweet.split(" "):
            if word.upper() == "WORSE":
                negated = not negated
            if word.upper() == 'NOT':
                negated = not negated

        cs = self.tweet_subjects(tweet)
        for cand in cs:
            if subject1 == None:
                subject1 = cand
            else:
                subject2 = cand
        alen = tweet.find(subject1)
        blen = tweet.find(subject2)
        if alen > blen:
            tmp = subject1
            subject1 = subject2
            subject2 = tmp
        if negated:
            return [(subject1, -1), (subject2, 1)]
        else:
            return [(subject1, 1), (subject2, -1)]

    def analyse_tweet(self, tweet, multi=False):
        """Analyse a tweet, extracting the subject and sentiment"""
        sentiment = 0
        # subject = self.tweet_subject(tweet)
        subjects = self.tweet_subjects(tweet)
        subject = subjects[0] if len(subjects) > 0 else "NONE"
        negated = False

        for word in tweet.split(" "):
            if word in self.comparison_words:
                return self.splitt(tweet)

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

        if multi:
            return [(s, sentiment) for s in subjects]
        else:
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

    def remove_stop(self, words):
        res = []
        stop_words = ['i', 'is', 'that', 'ok', 'good', 'okay', 'bad',
                      'cool', 'not', 'do', 'to', 'worse', 'than',
                      'am', 'My', 'my', 'a', 'had', 'and', 'so',
                      'are']
        for word in words:
            if not word.lower() in stop_words:
                res.append(word)
        return res
    
    def tweet_contains(self, tweet, obj):
        candidates = self.remove_stop(tweet.split(' '))
        if ' ' in obj:
            candidates = [a + ' ' + b for a, b in zip(candidates, candidates[1:])]

        for c in candidates:
            if edit_dist(c, obj) < 3:
                if (len(obj) > 4 and len(c) > 4) or c == obj:
                    return True
        return False

    def tweet_subjects(self, tweet):
        res = []
        for company in self.companies:
            words = [company.name] + [p.name for p in company.products]
            recognised = False
            for word in words:
                recognised = recognised or self.tweet_contains(tweet, word)
            if recognised:
                res.append(company.name)

        return res
