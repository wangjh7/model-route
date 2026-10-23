# =============================================================================
#  语义缓存：把「换了个说法的同一个问题」也当成命中
# =============================================================================
#
#  - _normalize：把一句话切成 token 集合（演示用正则，生产可换 jieba / 向量）
#  - jaccard：集合相似度 J = |A∩B| / |A∪B|，取值 0.0 ~ 1.0
#  - SemanticCache：线性扫描所有条目取最高分，>= threshold 即命中
#
#  ⚠️ 本演示的切词很粗：正则里的 `+` 会把一整句中文切成「一个」token，
#     于是「换措辞」和「换意图」的句子相似度都是 0 —— 只会漏召回，不会误命中。
#     想看到误命中（答非所问），需要把切词细化（字符 / bigram / jieba）再调低阈值。
# =============================================================================

import re


def _normalize(text: str) -> set[str]:
    """切词 + 归一化：小写后按「字母/数字/汉字」连续段切成 token 集合。

    ⚠️ `+` 是贪心的，而中文没有空格，所以整句只会变成 1 个 token：
       "如何取消我的订单" -> {"如何取消我的订单"}
    两句话即便共享「取消」「订单」四个字，交集仍是空集。
    """
    return set(re.findall(r"[\w\u4e00-\u9fff]+", text.lower()))


def jaccard(a: str, b: str) -> float:
    """Jaccard 相似度 = |A∩B| / |A∪B|，0.0（毫不重合）~ 1.0（完全相同）。"""
    sa, sb = _normalize(a), _normalize(b)
    if not sa or not sb:  # 任一侧为空集时分母为 0，直接判为不相似
        return 0.0
    return len(sa & sb) / len(sa | sb)


class SemanticCache:
    """演示用语义缓存：Jaccard 相似度 >= 阈值即命中（生产用向量 + 阈值 + TTL）。

    与 ExactCache 的本质区别：这里判断「是不是同一个问题」靠的是相似度打分，
    命中的那一刻只代表「足够像」，不代表「确信相等」——
    阈值越低越省钱（漏召回少），也越容易答错（误命中多）。
    """

    def __init__(self, threshold: float = 0.85):
        # 命中阈值：0.85 偏保守（少误命中）；调低会同时减少漏召回、增加误命中
        self.threshold = threshold
        # 演示用内存列表；生产换成向量库 / Redis，并补上 TTL 与容量上限
        self._entries: list[tuple[str, str]] = []

    def get(self, query: str) -> tuple[str | None, float, str | None]:
        """查缓存，返回 (命中答案, 最高相似度, 最高分对应的旧问法)。

        - 命中：answer 不为 None
        - 未命中：answer 为 None，但仍带回 best_score / best_query，
          因为调阈值和排查误命中时，"差多少分"比"没命中"有用得多。
        """
        best_score = 0.0
        best_answer: str | None = None
        best_query: str | None = None

        # 线性扫描全部条目（O(n)）；生产应换成向量近邻检索（ANN）
        for cached_q, ans in self._entries:
            score = jaccard(query, cached_q)
            if score > best_score:  # 严格大于：同分时保留先写入的那条，结果可复现
                best_score = score
                best_answer = ans
                best_query = cached_q

        # 达到阈值才算命中；用 `>=` 表示"正好等于阈值"也算命中
        if best_score >= self.threshold:
            return best_answer, best_score, best_query

        # 未命中：仍然把最高分带出去，否则无法判断"还差多少"
        return None, best_score, best_query

    def set(self, query: str, answer: str) -> None:
        """写入缓存。演示版直接追加；生产要按 key upsert（覆盖）并设置 TTL。"""
        self._entries.append((query, answer))
