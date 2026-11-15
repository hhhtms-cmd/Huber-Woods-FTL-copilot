import numpy as np

# ==========================================
# 模块一：数据校验与守门员 (Data Guardrail)
# ==========================================
def check_rate_anomaly(current_rate, historical_avg_rate, threshold=0.15):
    """
    检查新录入的运费是否异常偏离历史均值，防止“脏数据”进入系统。
    """
    deviation = abs(current_rate - historical_avg_rate) / historical_avg_rate
    if deviation > threshold:
        return False, f"⚠️ 数据异常警报：当前运费 ({current_rate}) 偏离历史均值 ({historical_avg_rate}) 达 {deviation*100:.1f}%, 疑似录入错误！"
    return True, "✅ 数据校验通过"


# ==========================================
# 模块二：承运商接单概率预测模型 (Predictive Acceptance Engine)
# ==========================================
def predict_acceptance_probability(carrier_history_rate, price_competitiveness, is_peak_day=True):
    """
    基于历史履约率、价格竞争力和调度时间（如周三/周四高峰期），预测承运商接单概率。
    """
    base_prob = carrier_history_rate
    
    # 价格越有竞争力（比市场均价便宜），接单概率略有提升
    adjustment = (price_competitiveness - 1.0) * 0.15
    
    # 如果是周三/周四调度高峰期，整体拒单风险略微上升
    if is_peak_day:
        adjustment -= 0.05
        
    # 将概率限制在 5% 到 99% 之间
    final_prob = np.clip(base_prob + adjustment, 0.05, 0.99)
    return round(final_prob, 2)


# ==========================================
# 模块三：多目标加权评分与推荐引擎 (Optimization & Ranking Layer)
# ==========================================
def rank_carriers_for_shipment(carriers_data, weights={'cost': 0.4, 'commitment': 0.3, 'acceptance': 0.3}, historical_market_avg=1000):
    """
    核心加权评分逻辑（你的数学公式落地版）：
    Total Score = w1 * (成本得分) + w2 * (承诺达成得分) + w3 * (接单概率得分)
    """
    scored_carriers = []
    
    # 提取所有报价用于成本归一化
    costs = [c['quoted_cost'] for c in carriers_data]
    min_cost = min(costs) if costs else 1.0
    max_cost = max(costs) if max(costs) != min_cost else min_cost + 1.0

    for carrier in carriers_data:
        # 1. 成本得分：越便宜得分越高（归一化到 0 ~ 1 之间）
        cost_score = 1.0 - (carrier['quoted_cost'] - min_cost) / (max_cost - min_cost) if max_cost != min_cost else 1.0
        
        # 2. 合同承诺达成得分：如果本周分配量还没达到合同目标，给高分以帮其完成 KPI
        commitment_gap = max(0, carrier['target_allocation'] - carrier['current_allocated'])
        commitment_score = min(1.0, commitment_gap / carrier['target_allocation']) if carrier['target_allocation'] > 0 else 0.5
        
        # 3. AI 预测接单概率
        price_comp = historical_market_avg / carrier['quoted_cost'] # 价格竞争力指数
        acceptance_prob = predict_acceptance_probability(
            carrier_history_rate=carrier['historical_accept_rate'],
            price_competitiveness=price_comp,
            is_peak_day=True
        )
        
        # 4. 计算综合总得分 (乘以 100 变成百分制)
        total_score = (
            weights['cost'] * cost_score + 
            weights['commitment'] * commitment_score + 
            weights['acceptance'] * acceptance_prob
        ) * 100
        
        # 生成直观的推荐理由
        reasons = []
        if cost_score > 0.8:
            reasons.append("运费极具竞争力 💰")
        if acceptance_prob > 0.85:
            reasons.append(f"历史履约极稳 (预估接单率 {int(acceptance_prob*100)}%) 🛡️")
        else:
            reasons.append(f"⚠️ 注意：近期履约风险较高 (预估接单率 {int(acceptance_prob*100)}%)")
            
        scored_carriers.append({
            'carrier_name': carrier['name'],
            'total_score': round(total_score, 2),
            'details': {
                'quoted_cost': carrier['quoted_cost'],
                'cost_score': round(cost_score, 2),
                'commitment_score': round(commitment_score, 2),
                'predicted_acceptance': acceptance_prob
            },
            'recommendation_reason': "；".join(reasons)
        })
        
    # 按总得分从高到低排序（第一名就是 AI 首选）
    scored_carriers.sort(key=lambda x: x['total_score'], reverse=True)
    return scored_carriers


# ==========================================
# 🧪 模拟测试：拿一条订单让算法跑一下看结果
# ==========================================
if __name__ == "__main__":
    print("--- 🚀 开始运行 Huber Woods FTL 智能调度模拟测试 ---\n")
    
    # 1. 测试数据校验功能
    print("【测试 1：基础数据异常拦截】")
    status, msg = check_rate_anomaly(current_rate=1450, historical_avg_rate=1000)
    print(msg)
    print("-" * 50)
    
    # 2. 模拟当前有一票整车订单，有 3 家承运商参与竞标/可选
    mock_carriers = [
        {
            'name': 'Carrier A (老牌合规车队)',
            'quoted_cost': 1050,
            'historical_accept_rate': 0.95,
            'target_allocation': 50,
            'current_allocated': 20
        },
        {
            'name': 'Carrier B (低价个体车队)',
            'quoted_cost': 980,
            'historical_accept_rate': 0.60,
            'target_allocation': 20,
            'current_allocated': 18
        },
        {
            'name': 'Carrier C (平衡型车队)',
            'quoted_cost': 1020,
            'historical_accept_rate': 0.88,
            'target_allocation': 40,
            'current_allocated': 38
        }
    ]
    
    # 3. 你作为总设计师设定的策略权重（比如：成本占 40%，承诺达成占 30%，接单概率占 30%）
    my_weights = {
        'cost': 0.4,
        'commitment': 0.3,
        'acceptance': 0.3
    }
    
    print(f"【测试 2：多目标加权推荐结果 (权重设置: 成本 {my_weights['cost']*100}%, 承诺 {my_weights['commitment']*100}%, 履约 {my_weights['acceptance']*100}%)】\n")
    
    ranked_results = rank_carriers_for_shipment(mock_carriers, weights=my_weights, historical_market_avg=1020)
    
    # 打印排名前三的推荐结果
    for rank, item in enumerate(ranked_results, 1):
        print(f"第 {rank} 名: {item['carrier_name']}")
        print(f"  👉 综合得分: {item['total_score']} 分")
        print(f"  👉 报价: ${item['details']['quoted_cost']} | 预估接单率: {int(item['details']['predicted_acceptance']*100)}%")
        print(f"  👉 推荐评语: {item['recommendation_reason']}")
        print()
