"""
优化提示词测试脚本
对比中英文提示词优化效果，使用表格记录数据
"""
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

from app.services.prompt_optimizer import PromptOptimizer
from app import create_app

# 创建 Flask 应用上下文
app = create_app()






def test_compare_optimization():
    """对比中英文提示词优化"""
    api_key = os.getenv('ALIYUN_BAILIAN_API_KEY')
    if not api_key:
        print("错误：未设置 ALIYUN_BAILIAN_API_KEY 环境变量")
        return
    
    optimizer = PromptOptimizer(api_key)
    
    # 测试主题列表
    test_cases = [
        {"prompt": "大唐芙蓉园夜景", "keywords": "古风、唐代、灯光秀"},
        {"prompt": "深圳科技园", "keywords": "科技、未来感、智能"},
        {"prompt": "桂林山水", "keywords": "山水、烟雨、诗意"},
        {"prompt": "咖啡馆下午茶", "keywords": "小资、温馨、精致"},
        {"prompt": "故宫雪景", "keywords": "古建筑、雪景、历史"},
    ]
    
    print("=" * 80)
    print("中英文提示词优化对比测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 存储测试结果
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n【测试 {i}/{len(test_cases)}】{case['prompt']}")
        print("-" * 40)
        
        result_item = {
            "序号": i,
            "原始提示词": case['prompt'],
            "关键词": case['keywords']
        }


        # 定义中英文系统提示词
        SYSTEM_PROMPTS = {
            "chinese": f"""你是文旅短片提示词优化专员，专注城市、古镇、山水、乡村文旅创作。
        # 请按规则将{case['prompt']}优化成专业剧本提示词：
        # 1. 保留原有地点、特色、氛围、季节、主题，不额外加无关景点；
        # 2. 自动补齐人文特色、风景质感、光影时段、色调氛围、叙事调性、4K电影画质；
        # 3. 统一慢节奏、沉浸式治愈风，主打风景+人文，无多余剧情；
        # 4. 文案精炼饱满，适配生成文旅分镜剧本；
        # 只输出优化后完整提示词，无多余话术与解释。""",

            "english": f"""You are a prompt optimization specialist for cultural tourism short videos, focusing on urban, ancient town, landscape and rural cultural tourism creation.
        Optimize {case['prompt']} into a professional script prompt following the rules below:
        1. Retain the original location, features, atmosphere, season and theme; do not add irrelevant scenic spots arbitrarily.
        2. Automatically supplement humanistic characteristics, landscape texture, light & time period, color tone atmosphere, narrative style, and 4K cinematic image quality.
        3. Adopt a unified slow-paced, immersive healing style, focusing on scenery and humanistic vibes with no redundant plots.
        4. Keep the wording concise and substantial, suitable for generating cultural tourism storyboard scripts.
        Only output the complete optimized prompt, without extra remarks or explanations.(output chinese)"""
        }
        # 中文优化
        # 每次调用重新创建连接
        optimizer = PromptOptimizer(api_key)
        start_time = time.time()
        cn_result = optimizer.optimize_with_custom_prompt(
            prompt=case['prompt'],
            system_prompt=SYSTEM_PROMPTS["chinese"],
            user_template=f"关键词：{case['keywords']}\n优化提示词：{{prompt}}"
        )
        cn_duration = time.time() - start_time
        
        if cn_result.get('success'):
            result_item["中文-耗时(s)"] = f"{cn_duration:.2f}"
            result_item["中文-Input Tokens"] = cn_result.get('input_tokens', 0)
            result_item["中文-Output Tokens"] = cn_result.get('output_tokens', 0)
            result_item["中文-总Tokens"] = cn_result.get('input_tokens', 0) + cn_result.get('output_tokens', 0)
            result_item["中文-结果"] = cn_result['optimized'][:50] + "..."
            print(f"  中文: {cn_duration:.2f}s | {cn_result.get('input_tokens', 0)} + {cn_result.get('output_tokens', 0)} tokens")
        else:
            result_item["中文-耗时(s)"] = "失败"
            result_item["中文-结果"] = cn_result.get('error')
        print(f"\n⏳ 等待10秒...")
        # 关闭连接
        optimizer.client.close()
        time.sleep(10)

        # 英文优化
        # 每次调用重新创建连接
        optimizer = PromptOptimizer(api_key)
        start_time = time.time()
        en_result = optimizer.optimize_with_custom_prompt(
            prompt=case['prompt'],
            system_prompt=SYSTEM_PROMPTS["english"],
            user_template=f"Keywords: {case['keywords']}\nOptimize this prompt: {{prompt}}"
        )
        en_duration = time.time() - start_time
        
        if en_result.get('success'):
            result_item["英文-耗时(s)"] = f"{en_duration:.2f}"
            result_item["英文-Input Tokens"] = en_result.get('input_tokens', 0)
            result_item["英文-Output Tokens"] = en_result.get('output_tokens', 0)
            result_item["英文-总Tokens"] = en_result.get('input_tokens', 0) + en_result.get('output_tokens', 0)
            result_item["英文-结果"] = en_result['optimized'][:50] + "..."
            print(f"  英文: {en_duration:.2f}s | {en_result.get('input_tokens', 0)} + {en_result.get('output_tokens', 0)} tokens")
        else:
            result_item["英文-耗时(s)"] = "失败"
            result_item["英文-结果"] = en_result.get('error')
        
        results.append(result_item)
        
        # 关闭连接
        optimizer.client.close()
        print("🔌 连接已关闭")
        
        # 每次测试后等待10秒
        print(f"\n⏳ 等待10秒...")
        time.sleep(10)
    
    # 输出表格
    print("\n" + "=" * 80)
    print("📊 测试结果汇总表")
    print("=" * 80)
    
    # 简化表格（关键列）
    summary_table = []
    for r in results:
        summary_table.append([
            r["序号"],
            r["原始提示词"],
            r.get("中文-耗时(s)", "-"),
            r.get("中文-总Tokens", "-"),
            r.get("英文-耗时(s)", "-"),
            r.get("英文-总Tokens", "-"),
        ])
    
    headers = ["序号", "原始提示词", "中文耗时(s)", "中文Tokens", "英文耗时(s)", "英文Tokens"]
    print(tabulate(summary_table, headers=headers, tablefmt="grid"))
    
    # 详细表格（含结果预览）
    print("\n" + "=" * 80)
    print("📋 详细结果")
    print("=" * 80)
    
    detail_table = []
    for r in results:
        detail_table.append([
            r["原始提示词"],
            r.get("中文-结果", "-")[:30],
            r.get("英文-结果", "-")[:30],
        ])
    
    headers = ["原始提示词", "中文结果预览", "英文结果预览"]
    print(tabulate(detail_table, headers=headers, tablefmt="grid"))
    
    # 汇总统计
    print("\n" + "=" * 80)
    print("📈 性能统计")
    print("=" * 80)
    
    cn_total_duration = 0
    en_total_duration = 0
    cn_total_tokens = 0
    en_total_tokens = 0
    cn_count = 0
    en_count = 0
    
    for r in results:
        if r.get("中文-耗时(s)") and r["中文-耗时(s)"] != "失败":
            cn_total_duration += float(r["中文-耗时(s)"])
            cn_total_tokens += int(r.get("中文-总Tokens", 0))
            cn_count += 1
        if r.get("英文-耗时(s)") and r["英文-耗时(s)"] != "失败":
            en_total_duration += float(r["英文-耗时(s)"])
            en_total_tokens += int(r.get("英文-总Tokens", 0))
            en_count += 1
    
    stat_table = [
        ["指标", "中文优化", "英文优化", "差异"],
        ["测试数量", cn_count, en_count, "-"],
        ["总耗时(s)", f"{cn_total_duration:.2f}", f"{en_total_duration:.2f}", f"{cn_total_duration - en_total_duration:.2f}"],
        ["平均耗时(s)", f"{cn_total_duration/cn_count:.2f}" if cn_count else "-", 
                      f"{en_total_duration/en_count:.2f}" if en_count else "-", "-"],
        ["总Tokens", cn_total_tokens, en_total_tokens, cn_total_tokens - en_total_tokens],
        ["平均Tokens", f"{cn_total_tokens//cn_count}" if cn_count else "-", 
                      f"{en_total_tokens//en_count}" if en_count else "-", "-"],
    ]
    
    print(tabulate(stat_table, headers="firstrow", tablefmt="grid"))
    
    # 保存结果到CSV
    save_to_csv(results)
    print("\n✅ 结果已保存到 test_results.csv")


def save_to_csv(results):
    """保存结果到CSV"""
    import csv
    
    with open('test_results.csv', 'w', newline='', encoding='utf-8') as f:
        if results:
            fieldnames = list(results[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)


if __name__ == "__main__":
    with app.app_context():
        test_compare_optimization()
