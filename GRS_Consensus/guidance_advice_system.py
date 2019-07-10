import pandas as pd
import numpy as np
# import mix_recommender
# def read_resultData(path):
#     return pd.read_csv(path)
from evaluation_test import EvaTest
import time
import math
import copy

def sort_result(user_ids, result_data, n):
    '''根据预测的评级获得群组用户对电影的偏好顺序'''
    # result_data = pd.read_csv('result.csv')
    # result_data = pd.read_csv('pre_result.csv')

    user_preference_lists = list()
    for user_id in user_ids:
        rate_info = result_data[result_data['UserID'] == user_id]
        # print(rate_info)
        # print(result_data['MovieID'])
        # 对每个用户的评级预测数据重新赋值索引，此时的索引即为电影的顺序标记
        # print(rate_info)
        rate_info.index = [i for i in range(1, n + 1)]
        # 对评级预测数据降序排列
        rate_info.sort_values('pre_rating', inplace = True, ascending = False)
        # 获取排序后的索引，此索引仍然表示电影标记，但顺序根据评级大小进行排序
        sort_index = list(rate_info.index)
        # print(rate_info)

        # 保存用户偏好顺序的list
        user_preference = list()
        for i in range(1, n + 1):
            # 获取用户对电影的偏好顺序，即获取电影索引所在的位置
            user_preference.append(sort_index.index(i) + 1)
        user_preference_lists.append(user_preference)
        # sort_userRateInfo = rate_info['pre_rating'].values
        # sort_resultData.append(sort_userRateInfo)
    return user_preference_lists

def get_fuzzyPreMatrix(user_preference_lists):
    '''根据群组用户对电影的偏好顺序，计算模糊偏好矩阵，表示对替代方案的看法（针对项目之间）'''
    # 保存所有用户的模糊偏好矩阵集合
    P_all_fuzzyPreMatrix = list()
    for P_i_user_preference in user_preference_lists:
    # P1_user_preference = user_preference_lists[0]
        n = len(P_i_user_preference)

        # 保存单个用户的模糊偏好矩阵
        P_i_fuzzyPreMatrix = list()
        for l in range(n):
            P_i_row = list()
            for k in range(n):
                P_i_lk = 1.1
                if l != k:
                    P_i_lk = 0.5 * (1 + ((P_i_user_preference[k] - P_i_user_preference[l]) / (n - 1)))
                    # 保留两位小数
                    P_i_lk = round(P_i_lk, 2)
                P_i_row.append(P_i_lk)

            P_i_fuzzyPreMatrix.append(P_i_row)

        P_all_fuzzyPreMatrix.append(P_i_fuzzyPreMatrix)
    
    return P_all_fuzzyPreMatrix
    # print(P_all_fuzzyPreMatrix[1])
    # print(P1_fuzzyPreMatrix)
    # for l in P1_fuzzyPreMatrix:
    #     print(l)
    # pass

def get_PairedSimMatrix(P_all_fuzzyPreMatrix):
    '''根据群组用户的模糊偏好矩阵，计算成对相似矩阵（针对用户之间）'''
    # print(len(P_all_fuzzyPreMatrix))
    # 总人数，也即总矩阵数
    n = len(P_all_fuzzyPreMatrix)
    
    # 保存所有成对相似矩阵集合，里面的元素均为ndarray对象
    SM_all = list()
    for i in range(n):
        for j in range(i + 1, n):
            # 获取i和j的模糊偏好矩阵
            P_i_fuzzyPreMatrix = P_all_fuzzyPreMatrix[i]
            P_j_fuzzyPreMatrix = P_all_fuzzyPreMatrix[j]

            # 用numpy进行封装
            P_i_fuzzyPreMatrix_array = np.array(P_i_fuzzyPreMatrix)
            P_j_fuzzyPreMatrix_array = np.array(P_j_fuzzyPreMatrix)

            # 对对角数据进行处理，即值为1.1的数据，赋值为NaN
            P_i_fuzzyPreMatrix_array[P_i_fuzzyPreMatrix_array == 1.1] = np.NaN
            P_j_fuzzyPreMatrix_array[P_j_fuzzyPreMatrix_array == 1.1] = np.NaN

            # 计算成对相似矩阵
            SM_ij = 1 - abs(P_i_fuzzyPreMatrix_array - P_j_fuzzyPreMatrix_array)

            SM_all.append(SM_ij)

    return SM_all
    

def get_ConsensusMatrix(SM_all):
    '''根据成对相似矩阵获取共识矩阵，这里我们使用算术均值作为求解函数'''
    
    return sum(SM_all)/ len(SM_all)


def get_ConsensusDegree(consensusMatrix):
    '''根据共识矩阵，计算群组共识度，这里我们也使用算术平均作为求解函数'''

    # 将共识矩阵中值为NaN（即对角线上的）的替换为0，方便求和计算
    consensusMatrix[np.isnan(consensusMatrix)] = 0

    n = len(consensusMatrix)
    # 保存ca_i值，ca_i表示成对替代方案共识度
    ca_all = list()
    for i in range(n):
        ca_i = sum(consensusMatrix[i]) / (n - 1)
        # 保留两位小数
        ca_i = round(ca_i, 2)
        ca_all.append(ca_i)
    
    # 计算共识度
    cr = sum(ca_all) / len(ca_all)
    
    return ca_all, cr

def get_Proximity(P_all_fuzzyPreMatrix):
    '''计算近似度量，即Proximity measures'''

    # 获取群体偏好关系，这里我们使用算术均值作为求解函数
    P_all_fuzzyPreMatrix_array = list()
    # 首先对模糊偏好矩阵用numpy封装，方便计算
    for P_i_fuzzyPreMatrix in P_all_fuzzyPreMatrix:
        P_i_fuzzyPreMatrix_array = np.array(P_i_fuzzyPreMatrix)
        P_i_fuzzyPreMatrix_array[P_i_fuzzyPreMatrix_array == 1.1] = np.NaN
        P_all_fuzzyPreMatrix_array.append(P_i_fuzzyPreMatrix_array)
    # 计算群体偏好关系
    P_c = sum(P_all_fuzzyPreMatrix_array) / len(P_all_fuzzyPreMatrix_array)

    # print('P_c:', P_c)
    # P_c[np.isnan(P_c)] = 0 
    # print('P_c:', P_c)
    # print(np.sum(P_c, axis=1) / (len(P_c) - 1))


    # 计算群体偏好成对相似矩阵 
    PM_all = list()
    for P_i_fuzzyPreMatrix_array in P_all_fuzzyPreMatrix_array:
        PM_i = 1 - abs(P_i_fuzzyPreMatrix_array - P_c)
        PM_all.append(PM_i)
    
    # 获取替代方案的近似度，即Proximity on alternatives
    pa_i_all = list()
    for PM_i in PM_all:
        PM_i[np.isnan(PM_i)] = 0
        
        # 按行求均值
        pa_i_l = np.sum(PM_i, axis = 1) / (len(PM_i) - 1)

        pa_i_all.append(pa_i_l)

    # print(pa_i_all)
    # 计算近似度，即Proximity
    pr_all = list()
    for pa_i_l in pa_i_all:
        pr_i = sum(pa_i_l) / len(pa_i_l)
        pr_i = round(pr_i, 2)
        pr_all.append(pr_i)
    
    return P_c, pr_all

def get_recommenderList(P_c):
    # 获取群组共识推荐列表，使用nondominance标准

    # 构建共识偏好关系，new_P_c
    # 获取转置矩阵
    P_c_T = P_c.T

    new_P_c = P_c - P_c_T
    new_P_c[new_P_c < 0] = 0
    new_P_c[np.isnan(new_P_c)] = 0
    # 计算nondominance degree
    ND_l = 1 - np.max(new_P_c, axis=0)
    # print(ND_l)
    # 获取从小到大排序的索引，并加1（对应电影标记）
    index_sort = ND_l.argsort() + 1
    # print(index_sort)

    # 将上述数组逆序得到从大到小的索引
    index_sort = list(index_sort)
    index_sort.reverse()

    # 获取推荐列表
    O_c = list()
    for i in range(1, len(index_sort) + 1):
        O_c.append(index_sort.index(i) + 1)
    
    return O_c

def get_newUserPreferences(pr_all, ne, ca_all, γ, P_c, user_preference_lists, β):
    '''
    根据用户偏好与群体偏好的对比差距，进行偏好更新，得到新的偏好
    pr_all:Proximity值
    ne：需要改变偏好的群组用户比例
    ca_all:成对替代方案的共识度
    γ：共识阈值
    P_c:群体偏好关系
    user_preference_lists:用户偏好列表
    β:个人偏好与群体偏好所占比重
    '''

    # 找到需要改变偏好的群组用户集合，一个用户顺序的索引集合，以0开始
    need_change_pre_users = list()
    # print('pr_all:', pr_all)
    # 需要改变的人数，若存在pr值相同的情况，则n不一定为需要改变的人数，以下面的Proximity阈值为准
    n = int(len(pr_all) * ne)
    # 对Proximity值进行排序， 此时将pr_sorted[n]作为Proximity阈值
    pr_sorted = sorted(pr_all)
    # print('pr_sorted:', pr_sorted)
    # for i in range(n):
    #     need_change_pre_users.append(pr_all.index(pr_sorted[i])) 
    # print('pr_sorted[n]:', pr_sorted[n])
    # print('pr_all:', pr_all)
    pr_index = 0
    for pr in pr_all:
        if pr < pr_sorted[n] and len(need_change_pre_users) < n:
            need_change_pre_users.append(pr_index)
        pr_index += 1

    #找到需要改变偏好的物品集合，一个电影顺序的索引集合，以0开始
    need_change_items = list()
    # print('ca_all:', ca_all)
    for i, ca_i in enumerate(ca_all):
        # print('ca_i', ca_i)
        if ca_i < γ:
            need_change_items.append(i)
    

    print('need_change_pre_users:', need_change_pre_users)
    print('need_change_items:', need_change_items)

    # 获取群体推荐结果
    O_c = get_recommenderList(P_c)
    # print(O_c)

    print('user_preference_lists：', user_preference_lists)
    #偏好改变 Direction rules

    for user in need_change_pre_users:
        direc_list = dict()
        for item in need_change_items:
            # user = P_all_fuzzyPreMatrix[4]
            # user_array = np.array(user)
            # user_array[user_array == 1.1] = 0
            # # print(user_array)
            # print('user:',sum(list(user_array[item])) / (len(user_array) - 1))
            
            # print(user[item])
            user_preference = user_preference_lists[user]
            # 若用户偏好小于群组偏好，即个人心中的电影顺位排名大于群组
            # 目的：使偏好向群组偏好靠拢
            if user_preference[item] > O_c[item]:
                dis_value = user_preference[item] - O_c[item]
                # 用户偏好与用户与群组偏好距离的比重关系
                order_value = user_preference[item] * β - dis_value * (1 - β)
                direc_list[user_preference[item]] = order_value
            else:
                dis_value =  O_c[item] - user_preference[item]
                # 用户偏好与用户与群组偏好距离的比重关系，这里我们取0.7
                order_value = user_preference[item] * β + dis_value * (1 - β)
                direc_list[user_preference[item]] = order_value
        # print(user_preference)
        # print('direc_list:', direc_list)
        # direc_list对 key,value进行排序后索引一一对应
        key_sorted = sorted(direc_list.keys())
        value_sorted = sorted(direc_list.values())
        # print('key_sorted:', key_sorted)
        # print('value_sorted:', value_sorted)
        # 将用户原偏好copy一份，用于求原偏好的索引，方便对原偏好列表进行更改
        # user_pre_copy = user_preference.copy()
        user_pre_copy = copy.deepcopy(user_preference)
        for key, value in direc_list.items():
            # 获取根据键排序后的索引
            v_index = value_sorted.index(value)
            # 获取新的偏好顺序值（排序后键的索引与值的索引对应）
            new_key = key_sorted[v_index]

            # 在用户偏好列表中根据原来的偏好值获取该值所在索引
            user_pre_index = user_pre_copy.index(key)
            # print(user_pre_index)
            # 对用户偏好进行更新
            user_preference[user_pre_index] = new_key

        # print(user_preference)
        # 修改用户偏好集合
        user_preference_lists[user] = user_preference
    
    return user_preference_lists, need_change_pre_users, need_change_items

def guidance_advice_system(user_ids, cr, round_n, pr_all, ne, ca_all, γ, P_c, user_preference_lists, β):
    '''
    指导建议系统，替代人工主持人指导，自动更新迭代
    cr:目前方案达到的共识度
    round_n:迭代轮次
    pr_all:Proximity值
    ne：需要改变偏好的群组用户比例
    ca_all:成对替代方案的共识度
    γ：共识阈值
    P_c:群体偏好关系
    user_preference_lists:用户偏好列表
    β:个人偏好与群体偏好所占比重
    '''
    i = 0
    user_preferences = list()
    cr_list = list()
    need_change_pre_users_list = list()
    need_change_items_list = list()
    while cr < γ and i < round_n:
        print("迭代第" + str(i+1) +"轮开始：")
        user_new_preference_lists, need_change_pre_users, need_change_items = get_newUserPreferences(pr_all, ne, ca_all, γ, P_c, user_preference_lists, β)
        user_new_pre = copy.deepcopy(user_new_preference_lists)
        user_preferences.append(user_new_pre)
        print('user_new_preference_lists:',user_new_preference_lists)
        need_change_users_ids = list()
        for index in need_change_pre_users:
            need_change_users_ids.append(user_ids[index])
        need_change_pre_users_list.append(need_change_users_ids)
        need_change_items_list.append(need_change_items)

        # 重新计算模糊偏好矩阵
        P_all_fuzzyPreMatrix = get_fuzzyPreMatrix(user_new_preference_lists)

        # 重新计算成对相似矩阵
        SM_all = get_PairedSimMatrix(P_all_fuzzyPreMatrix)

        # 重新计算共识矩阵
        consensusMatrix = get_ConsensusMatrix(SM_all)

        # 重新计算替代品共识度及群体共识度
        ca_all, cr = get_ConsensusDegree(consensusMatrix)
        print('cr:', cr)
        cr_list.append(cr)

        # 重新计算群体偏好矩阵以及Proximity值
        P_c, pr_all = get_Proximity(P_all_fuzzyPreMatrix)

        print("迭代第" + str(i+1) +"轮结束！")

        # 轮次加1
        i += 1
    O_c_final = get_recommenderList(P_c)
    print("进行轮次：", i)

    return O_c_final,user_preferences, cr_list, need_change_pre_users_list, need_change_items_list

def get_finalMovieOrder(O_c_final, result_data, n):
    '''
        得到达成共识后最终的推荐列表MovieID
    '''
    finalMovieOrder = list()
    orgin_order = list(result_data['MovieID'])[:n]
    # print(orgin_order)
    for i in range(n):
        order = O_c_final.index(i+1)
        finalMovieOrder.append(int(orgin_order[order]))
    # print('O_c_final', O_c_final)
    # print('result_data', list(result_data['MovieID'][:n]))
    # print('finalMovieOrder', finalMovieOrder)
    return finalMovieOrder


def cal_Precision(finalMovieOrder, movie_ids_more3_set, movie_ids_set,  size):
    true_count = 0
    pre_count = 0
    for k in range(size):
        if finalMovieOrder[k] in movie_ids_more3_set:
            true_count += 1
        if finalMovieOrder[k] in movie_ids_set:
            pre_count += 1
    if pre_count != 0:
        precision = true_count / pre_count
    else:
        precision = -1
    return precision

def cal_nDCG(finalMovieOrder, user_ids, size, rating_data, user_preference_lists, result_data, n):
    nDCG = list()
    for i in range(len(user_ids)):
        user_id = user_ids[i]

        # user_preference = user_preference_lists[i]
        # print(user_preference)
        # userMovieOrder = get_finalMovieOrder(user_preference, result_data, n)

        movie_rate_dict = {}
        # 根据真实评分重新获取userMovieOrder
        for movie_id in finalMovieOrder[:size]:
            rate = rating_data[(rating_data['UserID'] == user_id) & (rating_data['MovieID'] == movie_id)]
            if not rate.empty:
                movie_rate_dict[movie_id] = int(rate['Rating'])
        movie_rate_dict_sort = dict(sorted(movie_rate_dict.items(), key=lambda d:d[1], reverse = True))
        userMovieOrder = list(movie_rate_dict_sort.keys())
        

        # print(userMovieOrder)
        DCG_i = 0
        IDCG_i = 0
        if size == 1:
            df_rate = rating_data[(rating_data['UserID'] == user_id) & (rating_data['MovieID'] == finalMovieOrder[size - 1])]
            if not df_rate.empty:
                DCG_i = int(rating_data[(rating_data['UserID'] == user_id) & (rating_data['MovieID'] == finalMovieOrder[size - 1])]['Rating'])
                IDCG_i = DCG_i
        else:
            if len(userMovieOrder) < 2:
                return -1
            flag = False
            # Iflag = False
            count = 0
            for k in range(size):
                df_rate = rating_data[(rating_data['UserID'] == user_id) & (rating_data['MovieID'] == finalMovieOrder[k])]
                # Idf_rate = rating_data[(rating_data['UserID'] == user_id) & (rating_data['MovieID'] == userMovieOrder[k])]
                if not df_rate.empty:
                    rate = int(df_rate['Rating'])
                    count += 1
                    if not flag:
                        DCG_i += rate
                        flag = True
                    else: 
                        DCG_i +=  rate/math.log2(count)
                # if not Idf_rate.empty:
                #     Irate = int(Idf_rate['Rating'])
                #     if not Iflag:
                #         IDCG_i += Irate
                #         Iflag = True
                #     else: 
                #         IDCG_i +=  Irate/math.log2(k + 1)
            Iflag = False
            for k in range(len(userMovieOrder)):
                Idf_rate = rating_data[(rating_data['UserID'] == user_id) & (rating_data['MovieID'] == userMovieOrder[k])]
                Irate = int(Idf_rate['Rating'])
                if not Iflag:
                    IDCG_i += Irate
                    Iflag = True
                else: 
                    IDCG_i +=  Irate/math.log2(k + 1)
        if IDCG_i == 0:
            print("无法评价！")
        else:
            nDCG_i = DCG_i / IDCG_i
            # print('nDCG_i:', nDCG_i)
            nDCG.append(nDCG_i)
    if len(nDCG) == 0:
        return -1
    else:
        return sum(nDCG)/len(nDCG)

if __name__ == "__main__":
    test = EvaTest()
    # 1. 推荐阶段
    # 生成群组
    user_ids = test.get_candidateUser(5)
    # 获取推荐候选集项目
    final_movie_ids, movie_ids_set = test.get_candidateItems(user_ids)
    # 基于混合协同过滤算法重新计算评分并生成结果
    result = test.pre_rate_mix_method(user_ids, final_movie_ids)
    # 获取用户偏好列表顺序
    user_preference_lists = sort_result(user_ids, result, 10)

    #2. 共识阶段
    # 生成用户模糊偏好矩阵，衡量用户对项目之间的偏好程度
    P_all_fuzzyPreMatrix = get_fuzzyPreMatrix(user_preference_lists)
    # 生成成对相似矩阵，衡量用户之间对项目偏好程度的距离
    SM_all = get_PairedSimMatrix(P_all_fuzzyPreMatrix)
    # 生成共识矩阵，衡量群组整体对项目之间偏好的共识程度
    consensusMatrix = get_ConsensusMatrix(SM_all)
    # 计算共识度，包括群组对各个项目的共识度及整体共识度
    ca_all, cr = get_ConsensusDegree(consensusMatrix)

    # 近似度
    # 计算群体模糊偏好矩阵及群组各成员与整体的近似度
    P_c, pr_all = get_Proximity(P_all_fuzzyPreMatrix)

    # 指导建议系统
    γ = 0.75
    ne = 0.8
    β = 0.2000001
    round_n = 5
    O_c_final = guidance_advice_system(user_ids,cr, round_n, pr_all, ne, ca_all, γ, P_c, user_preference_lists, β)
    # 最终推荐的电影顺序
    finalMovieOrder = get_finalMovieOrder(O_c_final, result, 10)
    print(finalMovieOrder)
