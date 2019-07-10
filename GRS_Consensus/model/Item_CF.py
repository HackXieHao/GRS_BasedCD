import pandas as pd
import numpy as np
import time

class Item_CF():

    def __init__(self):
        self.rating_data = pd.read_csv('data/ratings.csv')
        self.movies_data = pd.read_csv('data/movies.csv',encoding='ISO-8859-1')
        self.users_data = pd.read_csv('data/users.csv')

    # def read_data(self):
    #     self.rating_data = pd.read_csv('data/ratings.csv')
    #     self.movies_data = pd.read_csv('data/movies.csv',encoding='ISO-8859-1')

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

    # old method
    def cal_sim_cfBasedItem(self, m1_id, m2_id):
        '''改进的基于项目的协同过滤算法相似度计算'''
        D_u = self.rating_data[self.rating_data['MovieID'] == m1_id]
        D_v = self.rating_data[self.rating_data['MovieID'] == m2_id]

        # 同时评论过两部电影的用户ID集合
        users_id = list(set(D_u['UserID']).intersection(set(D_v['UserID'])))
        Du_intersection_Dv_len = len(list(set(D_u['UserID']).intersection(set(D_v['UserID']))))

        Du_union_Dv_len = len(list(set(D_u['UserID']).union(set(D_v['UserID']))))

        sum_rate = 0
        for user_id in users_id:
            # 用户对movie_1的评分
            r1 = self.rating_data[(self.rating_data.MovieID == m1_id) & (self.rating_data.UserID == user_id)]['Rating']
            # 用户对movie2的评分
            r2 = self.rating_data[(self.rating_data.MovieID == m2_id) & (self.rating_data.UserID == user_id)]['Rating']
            sum_rate += abs(int(r1) - int(r2))

        avg_rate = 0
        if len(users_id) != 0:
            avg_rate = sum_rate / len(users_id)

        return Du_intersection_Dv_len / (Du_union_Dv_len + avg_rate)

    # new method
    def get_movie_user_dict(self):
        # 获取电影-用户字典，格式为{item1:{user1,user2,...,usern},item2...}
        movie_user_dict = {}
        movie_ids = list(self.movies_data['MovieID'])
        for movie_id in movie_ids:
            value = list(self.rating_data[self.rating_data['MovieID'] == movie_id]['UserID'])
            movie_user_dict[movie_id] = value
        # print(movie_ids)
        # print(value)
        return movie_user_dict
    
    # # 获取用户电影评级字典,键为userId,值为一个dict,该dict的键为movieId,值为rate
    # def getMovieUserAndRatingDict(rating_data, user_data):
    #     user_movie_rating_dict = {}
    #     # user_ids = list(user_data.loc[:]['userID'])
    #     movie_ids = list(user_data.loc[:]['userID'])
    #     for userId in user_ids:
    #         movies = list(rating_data[rating_data['UserID'] == userId]['MovieID'])
    #         ratings = list(rating_data[rating_data['UserID'] == userId]['Rating'])
    #         movie_rate_dict = {}
    #         for i in range(len(movies)):
    #             movie_rate_dict[movies[i]] = ratings[i]
    #         user_movie_rating_dict[userId] = movie_rate_dict
    #         set().intersection
    #     # print(user_movie_rating_dict)
    #     return user_movie_rating_dict

    def new_cal_sim_cfBasedItem(self, movie_user_dict, m1_id, m2_id):
        users_1 = movie_user_dict[m1_id]
        users_2 = movie_user_dict[m2_id]
        intersection_users = list(set(users_1).intersection(set(users_2)))
        intersection_users = [i for i in intersection_users if i < 501]
        # print(intersection_users)
        union_users = list(set(users_1).union(set(users_2)))
        union_users = [i for i in union_users if i < 501]
        if len(union_users) == 0:
            return 0

        # pass
        # print(intersection_users)
        sum_rate = 0
        # i = 0
        for user_id in intersection_users:
            # i += 1
            # print(i)
            # 用户对movie_1的评分
            r1 = self.rating_data[(self.rating_data.MovieID == m1_id) & (self.rating_data.UserID == user_id)]['Rating']
            # 用户对movie2的评分
            r2 = self.rating_data[(self.rating_data.MovieID == m2_id) & (self.rating_data.UserID == user_id)]['Rating']
            sum_rate += abs(int(r1) - int(r2))

        avg_rate = 0
        if len(intersection_users) != 0:
            avg_rate = sum_rate / len(intersection_users)

        return len(intersection_users)/(len(union_users) + avg_rate)



    def get_sim_basedItem(self, movie_user_dict, a, m1_id, m2_id):
        '''综合类型相似度与协同过滤算法相似度结果的最终相似度'''
        # return self.type_sim(m1_id, m2_id) * a + self.cal_sim_cfBasedItem(m1_id, m2_id) * (1 - a)
        return self.type_sim(m1_id, m2_id) * a + self.new_cal_sim_cfBasedItem(movie_user_dict, m1_id, m2_id) * (1 - a)

    def get_rateByItemSim(self, movie_user_dict, user_id, m_id):
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
            sim_degree = self.get_sim_basedItem(movie_user_dict, 0.05, m_id, m_i_id)
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


if __name__ == '__main__':
    item = Item_CF()
    print("aaa")
    movie_user_dict = item.get_movie_user_dict()
    print("bbb")
    # rate = item.new_cal_sim_cfBasedItem(movie_user_dict, 1,2)
    rate = item.get_rateByItemSim(movie_user_dict, 1, 2)
    print(rate)
    # print(item.cal_sim_cfBasedItem(1,2 ))
    # print(item.get_sim_basedItem(0.3, 1, 2))
    # print(item.get_rateByItemSim(1, 2))
    # item.read_data()
    # print(item.rating_data)
    # print(item.movies_data)
    # print(item.type_sim(item.movies_data.iloc[0], item.movies_data.iloc[1]))
    # print(item.cal_sim_cfBasedItem(item.movies_data.iloc[0], item.movies_data.iloc[1], item.rating_data))
    # m = item.movies_data[item.movies_data['MovieID'] == 2]
    # 获取用户1评级过的电影
    # rating_movie_ids = item.rating_data[item.rating_data['UserID'] == 1]['MovieID']
    # all_movie_ids = item.movies_data['MovieID']
    # print(rating_movie_ids)
    # print(all_movie_ids)
    # print(list(set(rating_movie_ids) ^ (set(all_movie_ids))))
    # 获取用户1没有评级的所有电影
    # not_rating_movie_ids = list(set(rating_movie_ids) ^ (set(all_movie_ids)))
    #
    # flag = True
    # df1 =None
    # for m_id in not_rating_movie_ids:
    #     if flag:
    #         df1 = item.get_rateByItemSim(1, m_id)
    #         flag = False
    #     else:
    #         pd.concat([df1, item.get_rateByItemSim(1, m_id)], axis=1)
    # print(df1)
    # print(item.get_rateByItemSim(1,200))

    # start = time.time()
    # print(item.get_rateByItemSim(1, 2))
    # print((time.time() - start))
    # print(item.type_sim(1,2))
    # print(pd.DataFrame(np.array(list((2, 3, 5))).reshape(1,3), columns=['UserID', 'MovieID', 'pre_rating']))