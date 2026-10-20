import time
from dataclasses import dataclass

from .state import State


@dataclass
class CircuitBreaker:
    """
    一个经典的三态熔断器（CLOSED / OPEN / HALF_OPEN），用来在下游（比如某个模型服务）持续故障时快速失败，避免把请求和资源继续砸向已经挂掉的服务
    """
    failure_threshold: int = 5 # CLOSED 状态下，连续失败达到多少次就跳闸
    success_threshold: int = 2 # HALF_OPEN 状态下，连续成功多少次才恢复为 CLOSED
    open_seconds: float = 30.0 # OPEN 状态持续多久后允许试探
    half_open_max_calls: int = 3 # HALF_OPEN 状态下最多允许多少个并发探测请求

    # dataclass模块约定的钩子函数，在@dataclass自动生成的__init__中调用
    # 定义运行时状态，它们不应该出现在构造函数参数里
    def __post_init__(self): 
        self.state = State.CLOSED # 当前状态
        self.failures = 0 # 失败次数
        self.successes_half = 0  # 半开阶段的连续成功计数
        self.open_until = 0.0 # OPEN 状态的截止时间（时间戳）
        self.half_open_inflight = 0  # 半开阶段当前在途的探测请求数

    def _trip(self):
        """统一的跳闸动作：打开熔断、重置计时器和所有计数"""
        self.state = State.OPEN
        self.open_until = time.time() + self.open_seconds
        self.failures = 0
        self.successes_half = 0
        self.half_open_inflight = 0

    def allow(self) -> bool:
        """每次调用下游之前，判断这次是否放行；并负责 OPEN -> HALF_OPEN 的到期转换"""
        now = time.time()
        if self.state == State.OPEN:
            if now >= self.open_until: # OPEN 是否到期
                self.state = State.HALF_OPEN
                self.successes_half = 0
                self.half_open_inflight = 0
            else:
                return False
        if self.state == State.HALF_OPEN:
            return self.half_open_inflight < self.half_open_max_calls
        return True

    def before_call(self):
        """allow() 返回 True 之后，在 HALF_OPEN 下登记一个“在途探测”"""
        if self.state == State.HALF_OPEN:
            self.half_open_inflight += 1

    def on_success(self):
        """下游调用成功后，更新成功计数，可能 HALF_OPEN -> CLOSED"""
        if self.state == State.HALF_OPEN:
            self.successes_half += 1
            if self.successes_half >= self.success_threshold:
                self.state = State.CLOSED
                self.successes_half = 0
        else:
            self.failures = 0

        if self.state == State.HALF_OPEN:
            self.half_open_inflight = max(0, self.half_open_inflight - 1) # 减少一次在途计数

    def on_failure(self):
        """下游调用失败后，更新失败计数，可能 CLOSED -> OPEN 或 HALF_OPEN -> OPEN"""
        self.failures += 1
        if self.state == State.HALF_OPEN or self.failures >= self.failure_threshold:
            self._trip()
        if self.state == State.HALF_OPEN:
            self.half_open_inflight = max(0, self.half_open_inflight - 1)