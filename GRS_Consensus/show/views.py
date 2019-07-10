from django.shortcuts import render
import guidance_advice_system as gas
from evaluation_test import EvaTest
from django.http import JsonResponse
from .forms import MovieNumberForm
import json
import copy

# Create your views here.

def index(request):
    return render(request, 'index.html')

def generate_users(request):
    test = EvaTest()
    user_ids = test.get_candidateUser(5)
    # print(user_ids)

    return render(request, 'index.html', {
        'user_ids':'群组用户为：' + str(user_ids)
    })
    # if user_ids:
    #     return JsonResponse({'status':'success', 'msg':'生成群组成功', 'userIds':user_ids})
    # else:
    #     return JsonResponse({'status':'failed', 'msg':'生成群组失败'})

def result(request):
    movie_number_form = MovieNumberForm(request.POST)
    test = EvaTest()
    if movie_number_form.is_valid():
        userIds = movie_number_form.cleaned_data['userIds']
        number = movie_number_form.cleaned_data['number']
        user_ids = json.loads(userIds[6:])

        # 获取推荐候选集项目
        final_movie_ids, movie_ids_set = test.get_candidateItems(user_ids, number)
        # 基于混合协同过滤算法重新计算评分并生成结果
        result = test.pre_rate_mix_method(user_ids, final_movie_ids)
        # 获取用户偏好列表顺序
        user_preference_lists = gas.sort_result(user_ids, result, number)
        user_origin_preference = copy.deepcopy(user_preference_lists)

        # 2. 共识阶段
        # 生成用户模糊偏好矩阵，衡量用户对项目之间的偏好程度
        P_all_fuzzyPreMatrix = gas.get_fuzzyPreMatrix(user_preference_lists)
        # 生成成对相似矩阵，衡量用户之间对项目偏好程度的距离
        SM_all = gas.get_PairedSimMatrix(P_all_fuzzyPreMatrix)
        # 生成共识矩阵，衡量群组整体对项目之间偏好的共识程度
        consensusMatrix = gas.get_ConsensusMatrix(SM_all)
        # 计算共识度，包括群组对各个项目的共识度及整体共识度
        ca_all, cr = gas.get_ConsensusDegree(consensusMatrix)

        # 近似度
        # 计算群体模糊偏好矩阵及群组各成员与整体的近似度
        P_c, pr_all = gas.get_Proximity(P_all_fuzzyPreMatrix)

        # 指导建议系统
        γ = 0.75
        ne = 0.8
        β = 0.2000001
        round_n = 5
        O_c_final, user_preferences, cr_list, need_change_pre_users_list, need_change_items_list = gas.guidance_advice_system(user_ids, cr, round_n, pr_all, ne, ca_all, γ, P_c, user_preference_lists, β)
        # 最终推荐的电影顺序
        finalMovieOrder = gas.get_finalMovieOrder(O_c_final, result, number)
        print(finalMovieOrder)
        print(cr_list)
        return render(request, 'index.html', {
            'user_ids':'群组用户为：' + str(user_ids),
            'userIds':user_ids,
            'final_movie_ids':final_movie_ids,
            'user_origin_preference':user_origin_preference,
            'cr':cr,
            'γ':γ,
            'user_preferences':user_preferences,
            'cr_list':cr_list,
            'O_c_final':O_c_final,
            'need_change_pre_users_list':need_change_pre_users_list,
            'need_change_items_list':need_change_items_list,
            'finalMovieOrder':finalMovieOrder
        })