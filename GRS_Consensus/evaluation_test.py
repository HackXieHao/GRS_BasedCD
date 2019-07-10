import pandas as pd
import numpy as np
import time
import random
from pre_matrix import Mix_PreMethod
from model.Item_CF import Item_CF

class EvaTest():
    def __init__(self):
        self.rating_data = pd.read_csv('data/ratings.csv')
        self.rate_matrix = pd.read_csv('user_cf_rate_matrix_result.csv', index_col=0)
        self.sim_value = pd.read_csv('sim_value.csv')
        self.mix_method = Mix_PreMethod()
    
    def get_candidateUser(self, n):
        '''
            随机生成群组
        n: 群组大小
        '''

        user_ids = list()
        # old method
        # for i in range(n):
        #     user_id = random.choice(self.item_cf.users_data['userID'].values)
        #     user_ids.append(user_id)

        # new method
        all_user_ids = [i for i in range(1, 611)]
        i = 0
        while(i < n):
            user_id = random.choice(all_user_ids)
            if user_id not in user_ids:
                user_ids.append(user_id)
                i += 1

        return user_ids

    # 此函数用于测试工作时推荐项目使用
    def get_testCandidateItems(self, user_ids):
        '''
            在测试集上生成候选集项目，用于测试
            user_ids: 生成的用户群组
        '''

        recommend_movie_ids = set()
        data = self.rate_matrix.ix[user_ids]

        # print(data)
        recommend_movie_ids = data.mean().sort_values(axis = 0, ascending = False)[:1000].index
        # 将字符串变为整型
        recommend_movie_ids = list(map(int, recommend_movie_ids))
        # print(recommend_movie_ids)

        # 获取当前用户评级过的项目
        movie_ids_set = set()
        for user_id in user_ids:
            movie_ids = self.rating_data[self.rating_data['UserID'] == user_id]['MovieID'].values
            movie_ids_set = movie_ids_set.union(set(movie_ids))

        print('用户评级过的项目：', movie_ids_set)
        # 获取基于用户协同过滤的最终的电影推荐列表
        final_movie_ids = list(set(recommend_movie_ids))[:10]
        print(final_movie_ids)

        return final_movie_ids, movie_ids_set

    # 此函数用于在实际工作时推荐项目使用
    def get_candidateItems(self, user_ids, number):
        '''
            在实际推荐中生成候选集项目
            user_ids: 生成的用户群组
        '''

        recommend_movie_ids = set()
        data = self.rate_matrix.ix[user_ids]

        # print(data)
        recommend_movie_ids = data.mean().sort_values(axis = 0, ascending = False)[:1000].index
        # 将字符串变为整型
        recommend_movie_ids = list(map(int, recommend_movie_ids))
        # print(recommend_movie_ids)

        # 获取当前用户评级过的项目
        movie_ids_set = set()
        for user_id in user_ids:
            movie_ids = self.rating_data[self.rating_data['UserID'] == user_id]['MovieID'].values
            movie_ids_set = movie_ids_set.union(set(movie_ids))
        # print(len(movie_ids_set))
        # 获取基于用户协同过滤的最终的电影推荐列表
        # final_movie_ids = list(set(recommend_movie_ids) ^ set(movie_ids_set))
        final_movie_ids = [i for i in recommend_movie_ids if i not in movie_ids_set][:number]
        # print(final_movie_ids)

        return final_movie_ids, movie_ids_set
    
    def pre_rate_mix_method(self, user_ids, final_movie_ids):
        result = pd.DataFrame(columns=['UserID', 'MovieID', 'pre_rating'])
        # print(self.rate_matrix.index)
        # print(self.rate_matrix.columns)
        for user_id in user_ids:
            for movie_id in final_movie_ids:
                rate = self.mix_method.get_rateByMixMethod(0.55, user_id, movie_id)
                # rate = self.rate_matrix.loc[user_id][''+str(movie_id)]
                result = pd.concat([result, pd.DataFrame(np.array(list((user_id, movie_id, rate))).reshape(1, 3),
                            columns=['UserID', 'MovieID', 'pre_rating'])], axis=0)
        # print(result)
        return result

    def get_rateMoreThanThree(self, user_ids):
        '''
            获取群组中已评级电影评分大于4的id集合
        '''
        movie_ids_more3_set = set()
        for user_id in user_ids:
            movie_ids = self.rating_data[(self.rating_data['UserID'] == user_id) & (self.rating_data['Rating'] >= 4)]['MovieID'].values
            movie_ids_more3_set = movie_ids_more3_set.union(set(movie_ids))
        return movie_ids_more3_set


if __name__ == "__main__":
    test = EvaTest()
    start = time.time()
    # print(test.rate_matrix)
    user_ids = test.get_candidateUser(5)
    movie_ids_more3_set = test.get_rateMoreThanThree(user_ids)
    print(len(movie_ids_more3_set))
    final_movie_ids = test.get_candidateItems(user_ids)
    # test.pre_rate_mix_method(user_ids, final_movie_ids)
    # test.get_testCandidateItems(user_ids)
    end = time.time()
    print(end - start)