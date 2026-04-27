"""Benchmark track configuration."""

DEFAULT_TRACK = "cgt"

SOURCE_TYPES = ["原创", "文献改编", "教材改编", "数据库条目改编"]

PRESET_REVISION_REASONS = [
    "题目描述不清晰",
    "采分点设置违规",
    "参考答案错误/不完整",
    "溯源信息缺失",
    "领域不符",
    "其他",
]

TRACKS = {
    "cgt": {
        "value": "cgt",
        "label": "CGT",
        "emoji": "🧫",
        "site_title": "CGT Agent Benchmark",
        "site_subtitle": "基因与细胞治疗 AI Agent 评测基准 · 题目收集与管理平台",
        "footer_text": "CGT Agent Benchmark · 基因与细胞治疗 AI Agent 评测基准 · v2.0",
        "target_count": 1000,
        "difficulties": [
            {"value": "L1", "label": "L1 精准事实检索", "desc": "围绕 CGT 基础事实、定义与已知信息检索"},
            {"value": "L2", "label": "L2 生物逻辑推演", "desc": "围绕机制、因果关系与路径进行生物逻辑分析"},
            {"value": "L3", "label": "L3 实验方案设计", "desc": "围绕载体构建、验证流程与实验设计展开"},
            {"value": "L4", "label": "L4 转化决策与创新", "desc": "围绕临床转化、工艺取舍与创新策略判断"},
        ],
        "domains": [
            "递送系统 C1",
            "基因治疗 C2",
            "细胞工程 C3",
        ],
        "placeholders": {
            "title": "提示：rAAV 表达盒的结构设计与元件优选",
            "subdomain": "例如：AAV载体设计 / CAR-T / 体内递送",
            "source_detail": "改编类题目填写 DOI / PMID / 教材章节等",
        },
    },
    "protein": {
        "value": "protein",
        "label": "Protein",
        "emoji": "🧬",
        "site_title": "ProteinDesign Benchmark",
        "site_subtitle": "蛋白质设计 AI Agent 评测基准 · 题目收集与管理平台",
        "footer_text": "ProteinDesign Benchmark · 蛋白质设计 AI Agent 评测基准 · v2.0",
        "target_count": 1000,
        "difficulties": [
            {"value": "L1", "label": "L1 基础知识及推理问答", "desc": "蛋白质及蛋白质设计领域基础概念"},
            {"value": "L2", "label": "L2 蛋白质单模块工具调用", "desc": "蛋白质设计领域主流单功能工具/模型调用"},
            {"value": "L3", "label": "L3 蛋白质设计固定工作流协同", "desc": "蛋白质设计领域标准化固定工作流的拆解"},
            {"value": "L4", "label": "L4 蛋白质设计自主研发全流程", "desc": "蛋白质设计方案、多工具全流程搭建"},
        ],
        "domains": [
            "细胞因子/膜蛋白设计 C1",
            "肽设计 / binder 设计 C2",
            "抗体 / 纳米抗体设计 C3",
            "酶设计 / 酶优化 C4",
        ],
        "placeholders": {
            "title": "例如：人源 COX-2 选择性抑制剂结合口袋关键设计位点检索",
            "subdomain": "例如：酶底物特异性改造",
            "source_detail": "改编类题目填写 DOI / PDB / 教材章节等",
        },
    },
}


def get_track_config(track: str):
    return TRACKS.get(track or "", TRACKS[DEFAULT_TRACK])
