class TwoLevelCache[T]:
    def __init__(self) -> None:
        self.l1: dict[str, T] = {}
        self.redis = None # 接入 redis.asyncio
        self._l2_mock: dict[str, T] = {} # 演示用 L2; 生产删除, 改走 redis

    async def get(self, key: str) -> T | None:
        if key in self.l1:
            return self.l1[key]
        # val = await self.redis.get(key)
        val = self._l2_mock.get(key) if self.redis is None else None
        if val is not None:
            self.l1[key] = val
        return val

    async def set(self, key: str, value: T, ttl: int = 300) -> None:
        self.l1[key] = value
        # await self.redis.setex(key, ttl, value)
        if self.redis is None:
            self._l2_mock[key] = value