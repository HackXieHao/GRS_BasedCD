import pandas as pd
import math
import time
import numpy as np

class User_CF():

    def __init__(self):
        self.rating_data = pd.read_csv('data/ratings.csv')
        self.sim_user_table = pd.read_csv('sim_value.csv')
        self.i = 0

    # def simple_sim_user(self, target_rate_movies, other_rate_movie):
    #     '''使用Jaccard 公式简单计算相似度'''
    #     # 得到共同评级的电影ID
    #     common_movie_ids = list(set(target_rate_movies['MovieID']).intersection(set(other_rate_movie['MovieID'])))
    #     # print('common_movie_ids',common_movie_ids)
    #     if len(common_movie_ids) < 5:
    #         return 0
        
    #     union_movie_ids = list(set(target_rate_movies['MovieID']).union(set(other_rate_movie['MovieID'])))

    #     return len(common_movie_ids)/len(union_movie_ids)



    # @staticmethod
    def sim_user(self, target_rate_movies, other_rate_movie):
        '''计算两个用户之间的相似度，使用皮尔逊算法'''

       # 得到共同评级的电影ID
        common_movie_ids = list(set(target_rate_movies['MovieID']).intersection(set(other_rate_movie['MovieID'])))
        # print('common_movie_ids',common_movie_ids)
        if len(common_movie_ids) < 5:
            return 0
        # print(common_movie_ids)
        # 计算目标用户在共同评级电影中的平均评级
        target_common_rates = target_rate_movies[target_rate_movies['MovieID'].isin(common_movie_ids)]
        target_mean_rate = target_common_rates.mean()['Rating']
        # print('target_common_rates',target_common_rates)

        # 计算另一用户在共同评级电影中的平均评级
        other_common_rates = other_rate_movie[other_rate_movie['MovieID'].isin(common_movie_ids)]
        other_mean_rate = other_common_rates.mean()['Rating']
        # # print('other_common_rates',other_common_rates)

        # # print(target_common_rates)
        # # print(other_common_rates)

        # #余弦相似度
        # # cos_fz = 0
        # # sum_X_X = 0
        # # sum_Y_Y = 0
        # # for id in common_movie_ids:
        # #     X = int(target_common_rates[target_common_rates['MovieID'] == id]['Rating'])
        # #     Y = int(other_common_rates[other_common_rates['MovieID'] == id]['Rating'])
        # #     cos_fz += X * Y
        # #     sum_X_X += math.pow(X, 2)
        # #     sum_Y_Y += math.pow(Y, 2)
        # #
        # # cos_fm = math.sqrt(sum_X_X) * math.sqrt(sum_Y_Y)
        # # if cos_fm == 0:
        # #     return 0
        # # else:
        # #     return cos_fz / cos_fm

        # 皮尔逊相似度
        pearson_fz = 0
        sum_X_X = 0
        sum_Y_Y = 0
        for id in common_movie_ids:
            print(self.i)
            self.i += 1
            X = int(target_common_rates[target_common_rates['MovieID'] == id]['Rating']) - target_mean_rate
            Y = int(other_common_rates[other_common_rates['MovieID'] == id]['Rating']) - other_mean_rate
            pearson_fz += X * Y

            sum_X_X += math.pow(X, 2)
            sum_Y_Y += math.pow(Y, 2)

        pearson_fm = math.sqrt(sum_X_X) * math.sqrt(sum_Y_Y)
        if pearson_fm != 0:
            return pearson_fz / pearson_fm
        else:
            return 0

    def get_top_n_user(self, n, target_user_id):

        # 获取目标用户评级过的所有电影评级信息
        target_rate_movies = self.rating_data[self.rating_data['UserID'] == target_user_id]

        # 获取评级过的其他用户
        other_user_ids = [id for id in set(self.rating_data['UserID']) if id != target_user_id]
        print('aaa')

        # 获取其他用户的评级信息集合
        other_rate_movies = [self.rating_data[self.rating_data['UserID'] == id] for id in other_user_ids]
        print('bbb')

        # 相似度值集合
        # sim_list= [self.sim_user(target_rate_movies, other_rate_movie) for other_rate_movie in other_rate_movies]
        sim_list = [self.sim_user(target_rate_movies, other_rate_movie) for other_rate_movie in other_rate_movies]
        # sim_list = [self.simple_sim_user(target_rate_movies, other_rate_movie) for other_rate_movie in other_rate_movies]
        
        print('ccc')
        print(len(sim_list))

        sort_sim_list = sorted(zip(other_user_ids, sim_list), key=lambda x:x[1], reverse=True)
        print('ddd')

        # print(sort_sim_list)
        return sort_sim_list[:n]

    
    def new_get_top_n_users(self, n, target_user_id):
        '''基于用户相似度表获取Top-N相似用户'''
        sim_users = self.sim_user_table[self.sim_user_table['ID1'] == target_user_id]
        top_n_user_ids = list(sim_users.iloc[:n, 2])
        top_n_user_simValues = list(sim_users.iloc[:n, 3])

        return list(zip(top_n_user_ids, top_n_user_simValues))
        # print(sim_users)

    def get_top_n_usersBasedOnTest(self, n, target_user_id):
        '''基于用户相似度表获取Top-N相似用户'''
        sim_users = self.sim_user_table[(self.sim_user_table.ID1 == target_user_id) & (self.sim_user_table.ID2 <= 501)]
        top_n_user_ids = list(sim_users.iloc[:n, 2])
        # print(top_n_user_ids)
        top_n_user_simValues = list(sim_users.iloc[:n, 3])

        return list(zip(top_n_user_ids, top_n_user_simValues))
        # print(sim_users)

    def get_rateByUserSim(self, user_id, m_id):
        '''基于用户的协同过滤算法预测评分'''

        # 获取最相似的n个用户
        # top_n_user = self.get_top_n_user(35, user_id)
        # top_n_user = self.new_get_top_n_users(60, user_id)
        top_n_user = self.get_top_n_usersBasedOnTest(30, user_id)

        # 获取这n个用户的评级信息
        top_n_user_rate = [self.rating_data[self.rating_data['UserID'] == u_id] for u_id,_ in top_n_user]

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
            # return pd.DataFrame(np.array(list((user_id, m_id, 0))).reshape(1, 3),
            #                 columns=['UserID', 'MovieID', 'pre_rating'])


if __name__ == '__main__':
    user_cf = User_CF()
    print(user_cf.get_rateByUserSim(1, 2))
    # user_cf.get_top_n_usersBasedOnTest(10,1)
    # print(user_cf.get_rateByUserSim(386,1997))
    # print(user_cf.sim_user_table)
    # top_n_user = user_cf.new_get_top_n_users(10, 1)
    # top_n_user = list(top_n_user)
    # print(type(top_n_user))
    # for u_id, sim_value in top_n_user:
    #     print(u_id, sim_value)
    # print(top_n_user[0][1])
    # user_cf.read_data()
    # print(user_cf.rating_data)
    # t1 = user_cf.rating_data[user_cf.rating_data['UserID'] == 1]
    # t2 = user_cf.rating_data[user_cf.rating_data['UserID'] == 1024]

    # print(user_cf.sim_user(t1, t2))
    # print(user_cf.get_top_n_user(20, 1))
    # user_cf.get_rateByUserSiml(1, 2)

    # l = [(1,2), (20,30)]
    # print()
    # user_id = 1
    # print(user_cf.rating_data.query("UserID == "+ str(user_id) +" & MovieID == 2").empty)
    # start = time.time()
    # print(user_cf.get_rateByUserSim(1, 272))
    # print('Cost time: %f' % (time.time() - start))