import pandas as pd
import numpy as np
import time
import random
from model.Item_CF import Item_CF
import json

class Mix_PreMethod():
    '''
        混合协同过滤算法生成评分预测矩阵
    '''

    def __init__(self):
        self.rating_data = pd.read_csv('data/ratings.csv')
        self.movies_data = pd.read_csv('data/movies.csv',encoding='ISO-8859-1')
        self.user_data = pd.read_csv('data/users.csv')
        self.sim_value = pd.read_csv('sim_value.csv')
        self.item_cf = Item_CF()
    
    def get_top_n_users(self, n, target_user_id):
        '''
            基于用户相似度表获取Top-N相似用户
        '''
        sim_users = self.sim_value[self.sim_value['ID1'] == target_user_id]
        top_n_user_ids = list(sim_users.iloc[:n, 2])
        top_n_user_simValues = list(sim_users.iloc[:n, 3])
        return list(zip(top_n_user_ids, top_n_user_simValues))
    
    def fileToDictJson(self, FileName):  #当字典的元素仍为字典时，使用json
        file = open(FileName, 'r')
        js = file.read()
        dic = json.loads(js)
        file.close()
        return dic


    def get_top_simi(self, user,simi):
        top_list = []

        top_list = sorted(simi[user].items(),key = lambda x:x[1],reverse=True)
        return top_list[:50]

    def get_rateByUserSim(self, user_id, m_id):
        '''基于用户的协同过滤算法预测评分'''

        # 获取最相似的n个用户
        top_n_user = self.get_top_n_users(30, user_id)
        # top_n_user = self.get_top_simi(str(user_id), simi)

        # 获取这n个用户的评级信息
        top_n_user_rate = [self.rating_data[self.rating_data['UserID'] == int(u_id)] for u_id,_ in top_n_user]

        rate_list = []
        count = 0
        # 遍历这n个用户的评级信息
        for user_rate in top_n_user_rate:
            # 若已对电影m_id做过评级，则将评级添加到rate集合，否则添加0
            if m_id in user_rate['MovieID'].values:
                rate_list.append(user_rate[user_rate['MovieID'] == m_id]['Rating'].values[0])
                count += 1
            else:
                rate_list.append(0)

        if count != 0:
            return  sum([top_n_user[i][1] * rate_list[i] for i in range(len(top_n_user))]) / count
            # return pd.DataFrame(np.array(list((user_id, m_id, sum([top_n_user[i][1] * rate_list[i] for i in range(len(top_n_user))]) / count))).reshape(1, 3),
            #                 columns=['UserID', 'MovieID', 'pre_rating'])
        else:
            return 0
            #  return pd.DataFrame(np.array(list((user_id, m_id, 0))).reshape(1, 3),
                            # columns=['UserID', 'MovieID', 'pre_rating'])

    def type_sim(self, m1_id, m2_id):
        '''计算两个电影之间的类型相似度'''
        m1 = self.movies_data[self.movies_data['MovieID'] == m1_id]
        m2 = self.movies_data[self.movies_data['MovieID'] == m2_id]
        type_m1 = m1.iloc[0][2].split('|')
        type_m2 = m2.iloc[0][2].split('|')
        # 类型的并集
        union_list = list(set(type_m1).union(set(type_m2)))
        # 类型的交集
        intersection_list = list(set(type_m1).intersection(set(type_m2)))
        return len(intersection_list) / len(union_list)
    
    # 获取用户电影评级字典,键为userId,值为一个dict,该dict的键为movieId,值为rate
    def getUserMovieAndRatingDict(self):
        user_movie_rating_dict = {}
        user_ids = list(self.user_data.loc[:]['userID'])
        for userId in user_ids:
            movies = list(self.rating_data[self.rating_data['UserID'] == userId]['MovieID'])
            ratings = list(self.rating_data[self.rating_data['UserID'] == userId]['Rating'])
            movie_rate_dict = {}
            for i in range(len(movies)):
                movie_rate_dict[movies[i]] = ratings[i]
            user_movie_rating_dict[userId] = movie_rate_dict
            set().intersection
        # print(user_movie_rating_dict)
        return user_movie_rating_dict

    def cal_sim_cfBasedItem(self, m1_id, m2_id):
        '''改进的基于项目的协同过滤算法相似度计算'''
        D_u = self.rating_data[self.rating_data['MovieID'] == m1_id]
        D_v = self.rating_data[self.rating_data['MovieID'] == m2_id]

        # 同时评论过两部电影的用户ID集合
        users_id = list(set(D_u['UserID']).intersection(set(D_v['UserID'])))
        Du_intersection_Dv_len = len(list(set(D_u['UserID']).intersection(set(D_v['UserID']))))

        Du_union_Dv_len = len(list(set(D_u['UserID']).union(set(D_v['UserID']))))

        # return Du_intersection_Dv_len / Du_union_Dv_len
        
        if Du_union_Dv_len == 0:
            return 0

        # sum_rate = 0
        # for user_id in users_id:
        #     # 用户对movie_1的评分
        #     r1 = self.rating_data[(self.rating_data.MovieID == m1_id) & (self.rating_data.UserID == user_id)]['Rating']
        #     # r1 = user_movie_rating_dict[user_id][m1_id]
        #     # 用户对movie2的评分
        #     r2 = self.rating_data[(self.rating_data.MovieID == m2_id) & (self.rating_data.UserID == user_id)]['Rating']
        #     # r2 = user_movie_rating_dict[user_id][m2_id]
        #     sum_rate += abs(int(r1) - int(r2))

        # avg_rate = 0
        # if len(users_id) != 0:
        #     avg_rate = sum_rate / len(users_id)

        # return Du_intersection_Dv_len / (Du_union_Dv_len + avg_rate)
        return Du_intersection_Dv_len / Du_union_Dv_len
    
    def get_sim_basedItem(self , a, m1_id, m2_id):
        '''综合类型相似度与协同过滤算法相似度结果的最终相似度'''
        return self.type_sim(m1_id, m2_id) * a + self.cal_sim_cfBasedItem(m1_id, m2_id) * (1 - a)
        # return self.type_sim(m1_id, m2_id) * a + self.cal_sim_cfBasedItem(user_movie_rating_dict, m1_id, m2_id) * (1 - a)
    
    def get_rateByItemSim(self, user_id, m_id):
        '''改进的基于项目协同过滤算法预测的用户评分'''
        # 获取该用户已评分的所有数据
        user_rates = self.rating_data[self.rating_data['UserID'] == user_id]

        # 选取20部，大约评分过的10%，若使用所有的则计算太慢了
        if len(user_rates) > 20:
            user_rates = user_rates[:20]

        # print(user_rates)
        sum_rate = 0
        sum_sim_degree = 0
        for i in range(len(user_rates)):
            # print(i)
            # 获取电影ID
            m_i_id = user_rates.iloc[i][1]
            # 计算相似度
            sim_degree = self.get_sim_basedItem(0.05, m_id, m_i_id)
            # print(sim_degree)
            sum_sim_degree += sim_degree
            # 获取评级
            rate = int(user_rates.iloc[i][2])
            sum_rate += rate * sim_degree
        # return pd.DataFrame(np.array(list((user_id, m_id, sum_rate / sum_sim_degree))).reshape(1,3), columns=['UserID', 'MovieID', 'pre_rating'])
        if sum_sim_degree != 0:
            return sum_rate / sum_sim_degree
        else:
            return 0

    # 获取所有用户对所有电影的预测评分，并保存
    def get_ratePreTable(self, user_ids, movie_ids):
        # pre_result = pd.DataFrame(columns=['UserID', 'MovieID', 'pre_rating'])
        pre_result = pd.DataFrame(index = user_ids, columns = movie_ids)
        i = 0
        for user_id in user_ids:
            for movie_id in movie_ids:
                i += 1
                print(i)
                # rate = self.get_rateByMixMethod(movie_user_dict, 0.15, user_id, movie_id)
                rate = self.get_rateByUserSim(user_id, movie_id)
                # rate = self.item_cf.get_rateByItemSim(user_id, movie_id)
                # print(rate)
                # time.sleep(1)
                # pre_result = pd.concat([pre_result, rate], axis=0)
                # pre_result.to_csv('user_cf_rate_matrix.csv', mode='a', header=None)
                pre_result.loc[user_id][movie_id] = rate
        pre_result.to_csv('user_cf_rate_matrix.csv',mode='a',header=None)


    def get_rateByMixMethod(self, a, user_id, m_id):
        '''混合的协同过滤算法预测评分'''
        pre_rateByItemCF = self.get_rateByItemSim(user_id, m_id)
        # print(pre_rateByItemCF)
        pre_rateByUserCF = self.get_rateByUserSim(user_id, m_id)
        # print(pre_rateByUserCF)
        if pre_rateByUserCF == 0:
            return pre_rateByItemCF * (0.8 - a)
        elif pre_rateByItemCF == 0:
            return pre_rateByUserCF
        else:
            return pre_rateByUserCF * a + pre_rateByItemCF * (1 - a)
    
    def get_candidateUser(self, n):
        '''随机生成群组'''

        user_ids = list()
        # old method
        # for i in range(n):
        #     user_id = random.choice(self.item_cf.users_data['userID'].values)
        #     user_ids.append(user_id)

        # new method
        all_user_ids = [i for i in range(428, 611)]
        i = 0
        while(i < n):
            user_id = random.choice(all_user_ids)
            if user_id not in user_ids:
                user_ids.append(user_id)
                i += 1


        return user_ids




if __name__ == "__main__":

    mix_PreMethod = Mix_PreMethod()
    simi = mix_PreMethod.fileToDictJson('data/similarity_pearson2.txt')
    # print(mix_PreMethod.get_top_simi("2", 'data/similarity_pearson.txt'))
    start = time.time()

    print(mix_PreMethod.get_rateByUserSim(7 ,141))
    end = time.time()
    print('时间消耗：', end - start)
    # print(mix_PreMethod.fileToDictJson('data/similarity_pearson.txt'))


    # mix_method = Mix_PreMethod()
    # # user_movie_rating_dict = mix_method.getUserMovieAndRatingDict()
    # movie_ids = list(mix_method.movies_data['MovieID'])
    # user_ids = [i for i in range(1,611)]
    # # movie_user_dict = mix_method.item_cf.get_movie_user_dict()
    # start = time.time()
    # # for i in range(10000):
    # #     print(mix_method.get_rateByUserSim(i, 2))
    # # mix_method.cal_sim_cfBasedItem(user_movie_rating_dict, 1,2)
    # # for movie_id in movie_ids:
    # #     print(mix_method.get_sim_basedItem(user_movie_rating_dict, 0.05, 1, movie_id))
    # # for movie_id in movie_ids:
    # #     print(movie_id)
    # #     # mix_method.get_rateByItemSim(user_movie_rating_dict,1,movie_id)
    # #     mix_method.get_rateByUserSim(1, movie_id)
    # # mix_method.type_sim(1,2)
    # # mix_method.get_ratePreTable(user_ids[120:130], movie_ids)
    # print(mix_method.get_rateByMixMethod(0.15, 1, 2))
    # # print(user_ids[10:20])
    # end = time.time()
    # print('时间消耗:',end - start)