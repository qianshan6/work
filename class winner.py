import random
import time
#学生卡池
student_list =  [
"范留硕",
"段硕",
"黄廉体",
"庹雅欣",
"肖衔",
]
#权重
high_prob_dict = {
    "肖衔":100,
    "段硕":100
}                   #高概率权重
normal_weight = 1   #普通权重
weights = []
for name in student_list:
    if name in high_prob_dict:
        weights.append(high_prob_dict[name])
    else:
        weights.append(normal_weight)

#抽奖程序
while True:        
    print("=====课堂随机抽奖=====")
    print(f"参与人数：{len(student_list)} 人")
    input("按下回车键开始本轮抽奖")
#中奖人
    winner = random.choices(student_list,weights=weights,k=1)[0]
#滚动名字动画
    print("抽奖滚动中...", end="")
    for i in range(30):
        if i < 28:
            temp_name = random.choice(student_list)
        else:
            temp_name = winner
        print(f"\r当前:{temp_name:<12}", end="")
        time.sleep(0.06)

    print(f"\n\n 中奖同学：【{winner}】")
    print("-"*30)
    input("按回车键进行下一轮抽奖，如需推退出直接关闭窗口即可")
    print("\n")







