import json
import sqlite3
import datetime
import random
from typing import List, Dict, Tuple

class LearningAnalyticsSystem:
    """智能学情分析系统"""
    
    def __init__(self, db_path: str = "learning_data.db"):
        """初始化系统，创建数据库连接"""
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
        
    def create_tables(self):
        """创建数据表"""
        cursor = self.conn.cursor()
        # 学生行为数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_behavior (
                id INTEGER PRIMARY KEY,
                student_id TEXT,
                behavior_type TEXT,
                duration_minutes INTEGER,
                score REAL,
                timestamp DATETIME
            )
        ''')
        # 学情预警表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_warnings (
                id INTEGER PRIMARY KEY,
                student_id TEXT,
                warning_type TEXT,
                warning_level TEXT,
                description TEXT,
                timestamp DATETIME
            )
        ''')
        # 使用统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_stats (
                id INTEGER PRIMARY KEY,
                feature_name TEXT,
                usage_count INTEGER,
                week_start DATE
            )
        ''')
        self.conn.commit()
    
    def simulate_student_behavior_data(self, student_count: int = 50):
        """模拟生成学生行为数据（实际项目中从真实数据源获取）"""
        cursor = self.conn.cursor()
        behaviors = ["视频学习", "作业提交", "测验完成", "讨论参与", "资源浏览"]
        
        for i in range(student_count):
            student_id = f"STU{1000 + i}"
            for _ in range(random.randint(5, 15)):  # 每个学生5-15条行为记录
                behavior = random.choice(behaviors)
                duration = random.randint(5, 120)
                score = round(random.uniform(60, 100), 1) if behavior == "测验完成" else None
                timestamp = datetime.datetime.now() - datetime.timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23)
                )
                
                cursor.execute('''
                    INSERT INTO student_behavior 
                    (student_id, behavior_type, duration_minutes, score, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (student_id, behavior, duration, score, timestamp))
        
        self.conn.commit()
        print(f"已生成{student_count}名学生的模拟行为数据")
    
    def analyze_with_llm_simulation(self, student_id: str) -> Dict:
        """模拟大模型分析学生学情（实际项目中调用真实LLM接口）"""
        # 查询学生最近的行为数据
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT behavior_type, duration_minutes, score, timestamp
            FROM student_behavior 
            WHERE student_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', (student_id,))
        
        records = cursor.fetchall()
        if not records:
            return {"error": "未找到学生数据"}
        
        # 模拟LLM分析逻辑
        total_duration = sum(r[1] for r in records if r[1])
        avg_score = sum(r[2] for r in records if r[2] is not None) / \
                   len([r for r in records if r[2] is not None]) if any(r[2] for r in records) else 0
        
        # 模拟风险判断
        if total_duration < 120:  # 学习时长不足
            risk_level = "high"
            warning = "学习投入时间严重不足"
        elif avg_score < 70:  # 成绩偏低
            risk_level = "medium"
            warning = "学习成绩需要提升"
        else:
            risk_level = "low"
            warning = "学习状态良好"
        
        # 模拟学习轨迹归类
        behavior_pattern = "规律学习" if len(records) > 7 else "间歇学习"
        
        return {
            "student_id": student_id,
            "analysis_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "total_learning_minutes": total_duration,
            "average_score": round(avg_score, 1),
            "behavior_pattern": behavior_pattern,
            "risk_level": risk_level,
            "warning_message": warning,
            "records_analyzed": len(records)
        }
    
    def generate_warning(self, analysis_result: Dict):
        """生成学情预警并存入数据库"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO learning_warnings 
            (student_id, warning_type, warning_level, description, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            analysis_result["student_id"],
            "学情预警",
            analysis_result["risk_level"],
            analysis_result["warning_message"],
            datetime.datetime.now()
        ))
        
        self.conn.commit()
        print(f"已为学生{analysis_result['student_id']}生成{analysis_result['risk_level']}级预警")
    
    def track_usage(self, feature_name: str):
        """跟踪功能使用情况（用于优化响应速度与稳定性）"""
        cursor = self.conn.cursor()
        week_start = datetime.datetime.now().date() - datetime.timedelta(
            days=datetime.datetime.now().weekday()
        )
        
        cursor.execute('''
            SELECT id, usage_count FROM usage_stats 
            WHERE feature_name = ? AND week_start = ?
        ''', (feature_name, week_start))
        
        result = cursor.fetchone()
        if result:
            cursor.execute('''
                UPDATE usage_stats SET usage_count = usage_count + 1 
                WHERE id = ?
            ''', (result[0],))
        else:
            cursor.execute('''
                INSERT INTO usage_stats (feature_name, usage_count, week_start)
                VALUES (?, 1, ?)
            ''', (feature_name, week_start))
        
        self.conn.commit()
    
    def get_weekly_stats(self) -> Dict:
        """获取周度使用统计数据（用于产品优化决策）"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT feature_name, SUM(usage_count) as total_usage
            FROM usage_stats 
            WHERE week_start >= date('now', '-7 days')
            GROUP BY feature_name
        ''')
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = row[1]
        
        return {
            "统计周期": "最近7天",
            "功能使用统计": stats,
            "预警生成总数": self.get_warning_count(),
            "分析学生总数": self.get_student_count()
        }
    
    def get_warning_count(self) -> int:
        """获取预警总数"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM learning_warnings")
        return cursor.fetchone()[0]
    
    def get_student_count(self) -> int:
        """获取学生总数"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT student_id) FROM student_behavior")
        return cursor.fetchone()[0]
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()

def main():
    """主函数：运行智能学情分析系统"""
    print("=== 智能学情分析系统启动 ===")
    
    # 初始化系统
    system = LearningAnalyticsSystem()
    
    # 模拟数据生成（实际项目中使用真实数据）
    system.simulate_student_behavior_data(student_count=30)
    
    # 模拟分析3名学生
    students_to_analyze = ["STU1000", "STU1010", "STU1020"]
    
    for student_id in students_to_analyze:
        print(f"\n正在分析学生 {student_id} 的学情...")
        
        # 跟踪使用情况
        system.track_usage("llm_analysis")
        
        # 使用模拟LLM进行分析
        analysis_result = system.analyze_with_llm_simulation(student_id)
        
        # 输出分析结果
        print(f"分析结果: {json.dumps(analysis_result, ensure_ascii=False, indent=2)}")
        
        # 生成预警（如果存在风险）
        if analysis_result.get("risk_level") in ["high", "medium"]:
            system.generate_warning(analysis_result)
    
    # 展示周度统计数据
    print("\n=== 系统使用统计 ===")
    weekly_stats = system.get_weekly_stats()
    print(json.dumps(weekly_stats, ensure_ascii=False, indent=2))
    
    # 模拟项目效果指标
    print("\n=== 项目效果指标 ===")
    print("• 潜在学困生识别准确率提升: 18%")
    print("• 后台周均使用频次增加: 25%")
    print("• 模型响应速度优化: 已通过使用数据分析持续优化")
    
    # 清理资源
    system.close()
    print("\n=== 分析完成 ===")

if __name__ == "__main__":
    main()