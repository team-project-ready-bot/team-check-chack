# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 18:23:25 2019

@author: Onedas
"""

##

import pandas as pd
import math, sys
from konlpy.tag import Okt
import pickle

class Filter:

    def __init__(self):
        self.words = set() #어떤 단어들이 있는지. 집합
        self.word_dict = {} #이중 dictionary; [카테고리][단어] 가 몇번 사용됬는지. 히스토그램
        self.category_dict = {} #[카테고리] 가 몇번 사용됬는지
    
    ## text를 조사 어미 구두점을 제외한 단어만 list로 반환
    def split(self, text):
        results = []
        twitter = Okt() #형태소 분석기
        malist = twitter.pos(text, norm=True, stem=True) #steam True로 text를 분석.
        
        # 실습 2
        # 아래 for 문을 한줄짜리 for 문으로 바꿔보세요 List Comprehension
        for word in malist:
#            if not word[1] in ["Josa", "Eomi","Punctuation"]:
#                results.append(word[0])
#            
            if word[1] in ['Noun','Adjective']:
                results.append(word[0])
            
        return results

    ## word_dict 히스토램(word_dict)과, word 목록에 추가하는 작업.
    def inc_word(self, word, category):
        if not category in self.word_dict:
            self.word_dict[category] = {}
        if not word in self.word_dict[category]:
            self.word_dict[category][word] = 0
        self.word_dict[category][word] += 1
        self.words.add(word)

    ## 카테고리 히스토그램 만들기.
    def inc_category(self, category):
        if not category in self.category_dict:
            self.category_dict[category] = 0
        self.category_dict[category] += 1

    ## 텍스트 넣어서 histogram 만들기
    def fit(self, text, category):
        word_list = self.split(text) ## 조사 어미 구두점 제외하여 list로 반환
        for word in word_list:
            self.inc_word(word,category)
        self.inc_category(category)
    
    ## score를 확률적 계산
    ## P(카테고리|전체문서) + P( 단어 | 해당카테고리)
    def score(self, words, category):
        score = math.log(self.category_prob(category)) #해당 카테고리가 나올 확률
        for word in words: # 각 단어에 대한 확률의 합.
            score += math.log(self.word_prob(word, category))
        return score

    def predict(self, text):
        best_category = None
        max_score = -sys.maxsize
        words = self.split(text) #형태소 분석 (조사 어미 구두점 빼고 단어 list)
        score_list = [] # [(카테고리,score) ...] 쌍으로 들어감. socre_list
        for category in self.category_dict.keys():
            score = self.score(words, category)
            score_list.append((category,score))
                        
            if score > max_score: #가장 높은 score와 카테고리를 저장.
                max_score = score
                best_category = category
                
        return best_category, score_list
    
    ## 해당 단어가, 카테고리에서 몇번이나 쓰였는지 가져오는 함수.
    def get_word_count(self, word, category):

        if word in self.word_dict[category]:
            return self.word_dict[category][word]
        else:
            return 0
    
    ## 전체 문서수에 대해 해당 카테고리가 몇번이나 나왔는지. 확률. #카테고리가 나올 확률
    def category_prob(self, category):
        sum_categories = sum(self.category_dict.values()) # 전체 문서의 숫자
        category_v = self.category_dict[category] # 해당 카테고리의 숫자
        return category_v / sum_categories # 카테고리 수 / 전체 문서의 수
    
    ## 
    def word_prob(self, word, category): # 
        n = self.get_word_count(word, category) + 1 # 해당 단어가 카테고리에서 몇번이나 쓰였는지. log(0)이 없으므로 +1 로 bias
        d = sum(self.word_dict[category].values()) + len(self.words) # 해당 카테고리의 단어의 수 + 전체 단어의 수
        return n/d

    def save_as_pickle(self,file_name='Filter_class'):
        with open(file_name+'.pickle', 'wb') as f:
            pickle.dump(self, f)

    

class Intent_Finder:
    
    def __init__(self):
        self.big_filter = Filter()
        self.category_filters={}
        
    def train(self, category, text, data_num):
        self.big_filter.fit(text, category)
        
        if category not in self.category_filters:
            self.category_filters[category]= Filter()
            
        self.category_filters[category].fit(str(text)+str(category),data_num)
        
    def find_indent(self,text):
        best_category,score_list = self.big_filter.predict(text)
        score_list.sort(key=lambda x:-x[1])
        
        return [big_category for big_category,_ in score_list[:3]]
        
    def find_answer(self,text):
        best3_big_categorys = self.find_indent(text)
        
        answers =[]
        for big_category in best3_big_categorys:
            _, small_score_list = self.category_filters[big_category].predict(text)
            small_score_list.sort(key=lambda x:-x[-1])
            answers.extend(small_score_list[:3])
        
        answers.sort(key=lambda x:-x[1])
#        print(answers)
        return [num for num, _ in answers]
    
    def save_as_pickle(self,file_name='Intent_finder'):
        with open(file_name+'.pickle', 'wb') as f:
            pickle.dump(self, f)
        
#%% 0
if __name__ =="__main__":
    print(__name__)
    import pandas as pd
    
    DB_file = 'ds120FAQ.xlsx'
    df = pd.read_excel(DB_file)
    intent_finder = Intent_Finder()
    
    for i in range(len(df)):
#    category = df.loc[i][0] #카테고리 -> 행정
#    Q = df.loc[i][1] #
#    A = df.loc[i][2] #
        try:
            intent_finder.train(df.loc[i][0], df.loc[i][1], i)
        except:
            pass
    print('train done')

# %% 1
if __name__=="__main__":
    print(test)
    intent_finder.find_answer('하이')
        
        