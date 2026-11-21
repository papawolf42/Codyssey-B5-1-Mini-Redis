"""문자열 값과 최근 사용 순서를 관리하는 Mini Redis 저장소."""

import time

from mini_redis.hash_map import HashMap
from mini_redis.linked_list import DoublyLinkedList
from mini_redis.min_heap import MinHeap


def _size_of(key, value):
    """키와 값이 차지하는 UTF-8 바이트 수를 반환한다."""
    return len(key.encode("utf-8")) + len(value.encode("utf-8"))


class OOMError(Exception):
    """키와 값 한 쌍이 메모리 한도를 넘을 때 발생한다."""


class Entry:
    """값, 최근 사용 리스트의 노드, 만료 시각을 한곳에 둔다."""

    def __init__(self, value, lru_node, expire_at=None):
        """만료 시각이 없으면 expire_at을 None으로 둔다."""
        self.value = value
        self.lru_node = lru_node
        self.expire_at = expire_at


class MiniRedis:
    """키는 해시맵으로 찾고, 최근에 사용한 키는 리스트 앞에 둔다."""

    def __init__(self, clock=time.monotonic):
        """빈 저장소를 만들고 초 단위 시각을 반환하는 시계를 받는다."""
        self._map = HashMap()
        self._lru = DoublyLinkedList()
        self._expiry_heap = MinHeap()
        self._clock = clock
        self._used_memory = 0
        self._maxmemory = 0
        self._evicted_keys = 0

    def set(self, key, value):
        """값을 저장하고 키를 최근 사용 리스트 맨 앞으로 보낸다."""
        self._purge_expired()
        size = _size_of(key, value)
        if self._maxmemory > 0 and size > self._maxmemory:
            raise OOMError("키와 값의 크기가 메모리 한도를 넘습니다.")

        entry = self._map.get(key)
        if entry is None:
            lru_node = self._lru.insert_front(key)
            self._map.put(key, Entry(value, lru_node))
            self._used_memory += size
        else:
            self._used_memory += size - _size_of(key, entry.value)
            entry.value = value
            entry.expire_at = None
            self._lru.move_to_front(entry.lru_node)

        self._evict_until_fit()

    def get(self, key):
        """있으면 키를 맨 앞으로 옮기고 값을 반환한다. 없으면 None을 반환한다."""
        self._purge_expired()
        entry = self._map.get(key)
        if entry is None:
            return None

        self._lru.move_to_front(entry.lru_node)
        return entry.value

    def _remove_key(self, key):
        """키를 해시맵과 최근 사용 리스트에서 빼고 메모리 사용량을 줄인다."""
        entry = self._map.get(key)
        if entry is None:
            return 0

        size = _size_of(key, entry.value)
        self._lru.remove_node(entry.lru_node)
        self._map.remove(key)
        self._used_memory -= size
        return 1

    def _evict_until_fit(self):
        """한도 안에 들어올 때까지 가장 오래 쓰지 않은 키부터 제거한다."""
        while self._maxmemory > 0 and self._used_memory > self._maxmemory:
            oldest = self._lru.peek_back()
            self._remove_key(oldest.data)
            self._evicted_keys += 1

    def _purge_expired(self):
        """현재 시각까지 만료된 키를 정리하고 검사에 쓴 시각을 반환한다."""
        now = self._clock()
        while True:
            earliest = self._expiry_heap.peek()
            if earliest is None or earliest[0] > now:
                return now

            expire_at, key = self._expiry_heap.pop()
            entry = self._map.get(key)
            if entry is not None and entry.expire_at == expire_at:
                self._remove_key(key)

    def delete(self, key):
        """키를 지웠으면 1, 없으면 0을 반환한다."""
        self._purge_expired()
        return self._remove_key(key)

    def exists(self, key):
        """키가 있으면 1, 없으면 0을 반환한다."""
        self._purge_expired()
        return int(self._map.contains(key))

    def dbsize(self):
        """저장된 키의 수를 반환한다."""
        self._purge_expired()
        return self._map.size()

    def keys(self):
        """저장된 모든 키를 리스트로 반환한다."""
        self._purge_expired()
        return self._map.keys()

    def expire(self, key, seconds):
        """만료를 설정하거나 즉시 삭제하면 1, 키가 없으면 0을 반환한다."""
        now = self._purge_expired()
        entry = self._map.get(key)
        if entry is None:
            return 0
        if seconds <= 0:
            return self._remove_key(key)

        expire_at = now + seconds
        self._expiry_heap.push((expire_at, key))
        entry.expire_at = expire_at
        return 1

    def ttl(self, key):
        """남은 초를 버림해 반환한다. 없거나 만료되면 -2, 만료 시각이 없으면 -1."""
        now = self._purge_expired()
        entry = self._map.get(key)
        if entry is None:
            return -2
        if entry.expire_at is None:
            return -1

        return int(entry.expire_at - now)

    def config_set_maxmemory(self, n):
        """바이트 한도를 즉시 적용한다. 0은 무제한이다."""
        self._purge_expired()
        self._maxmemory = n
        self._evict_until_fit()

    def info_memory(self):
        """사용 바이트 수, 메모리 한도, 자동 제거 횟수를 반환한다."""
        self._purge_expired()
        return self._used_memory, self._maxmemory, self._evicted_keys
