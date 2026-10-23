# =============================================================================
#  精确缓存 vs 语义缓存：命中判据，以及「漏召回」与「误命中」的区别
# =============================================================================
#
#  - ExactCache：字面完全相等才命中，改一个字就 miss，但永远不会答错
#  - SemanticCache：_normalize 的 `+` 把整句中文当成一个 token，
#    所以「换了个说法」的同一问题相似度仍是 0 → 本节 demo 演示的是**漏召回**
#    （该命中却没命中），不是误命中
#  - 真正的**误命中**风险（答非所问）见 RISK_NOTES 第 1 条：
#    只有把分词细化（字符/bigram/jieba）并降低阈值之后才会出现
# =============================================================================

from semantic_cache import RISK_NOTES, ExactCache, SemanticCache

if __name__ == "__main__":
    exact = ExactCache()
    exact.set("sys", "什么是 RAG？", "gpt-4o", "RAG 是检索增强生成。")
    print("=== 精确缓存 ===")
    print(f"  同 prompt 命中: {exact.get('sys', '什么是 RAG？', 'gpt-4o')}")
    print(f"  换措辞 miss:    {exact.get('sys', 'RAG 是什么？', 'gpt-4o')}")
    print()

    sem = SemanticCache(threshold=0.6)
    sem.set("如何取消我的订单？", "请登录后在订单页点击取消。")
    q = "我想取消订单怎么办"
    ans, score, matched = sem.get(q)
    print("=== 语义缓存（演示漏召回：换措辞仍 miss）===")
    print(f"  新问法: {q}")
    print(f"  匹配到: {matched}  相似度={score:.2f}")
    print(f"  返回答案: {ans}")
    print()

    sem2 = SemanticCache(threshold=0.6)
    sem2.set("查询订单物流", "请在订单详情查看物流单号。")
    q2 = "取消订单"
    ans2, score2, matched2 = sem2.get(q2)
    print("=== 语义漏召回示例（查询 vs 取消 同样没命中）===")
    print(f"  问: {q2}  最佳匹配: {matched2}  score={score2:.2f}  答案: {ans2}")
    print("  → 分词把整句当成一个 token，两句话交集为空 → 相似度 0.00")
    print("  → 这是「漏召回」：该命中却没命中，代价是没省下钱")
    print("  → 若分词细化后命中「查询物流」的答案，那才是「误命中」：省了钱但答错")
    print()
    print("=== 语义缓存风险清单 ===")
    for i, note in enumerate(RISK_NOTES, 1):
        print(f"  {i}. {note}")
