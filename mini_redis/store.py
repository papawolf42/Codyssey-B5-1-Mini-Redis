"""문자열 값과 최근 사용 순서를 관리하는 Mini Redis 저장소."""

from mini_redis.hash_map import HashMap
from mini_redis.linked_list import DoublyLinkedList


class Entry:
    """값, 최근 사용 리스트의 노드, 만료 시각을 한곳에 둔다."""

    def __init__(self, value, lru_node, expire_at=None):
        """만료 시각이 없으면 expire_at을 None으로 둔다."""
        self.value = value
        self.lru_node = lru_node
        self.expire_at = expire_at


class MiniRedis:
    """키는 해시맵으로 찾고, 최근에 사용한 키는 리스트 앞에 둔다."""

    def __init__(self):
        """빈 해시맵과 빈 최근 사용 리스트를 만든다."""
        self._map = HashMap()
        self._lru = DoublyLinkedList()

    def set(self, key, value):
        """값을 저장하고 키를 최근 사용 리스트 맨 앞으로 보낸다."""
        entry = self._map.get(key)
        if entry is None:
            lru_node = self._lru.insert_front(key)
            self._map.put(key, Entry(value, lru_node))
            return

        entry.value = value
        entry.expire_at = None
        self._lru.move_to_front(entry.lru_node)

    def get(self, key):
        """있으면 키를 맨 앞으로 옮기고 값을 반환한다. 없으면 None을 반환한다."""
        entry = self._map.get(key)
        if entry is None:
            return None

        self._lru.move_to_front(entry.lru_node)
        return entry.value
