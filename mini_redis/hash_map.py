"""해시맵(Hash Map) 모듈."""

from mini_redis.linked_list import DoublyLinkedList


_FNV_OFFSET_BASIS = 2166136261
_FNV_PRIME = 16777619
_MASK_32 = 0xFFFFFFFF


def fnv1a_32(key):
    """문자열 key를 UTF-8 바이트로 변환해 32비트 FNV-1a 해시 정수를 반환한다.

    파이썬 내장 hash()는 프로세스마다 시드가 바뀌고 스펙상 직접 설계가 요구되므로
    고정된 비암호화 해시인 FNV-1a를 사용한다. 파이썬 int는 자릿수 제한이 없어
    매 곱셈마다 0xFFFFFFFF로 32비트 마스킹한다.
    """
    h = _FNV_OFFSET_BASIS
    for byte in key.encode("utf-8"):
        h ^= byte
        h = (h * _FNV_PRIME) & _MASK_32
    return h


class HashMap:
    """체이닝(이중 연결 리스트) 기반 해시맵.

    고정 길이 버킷 배열 각 칸에 DoublyLinkedList를 두어 해시 충돌을
    연결 리스트로 처리하고, 평균 O(1)에 삽입과 조회를 수행한다.
    """

    def __init__(self, capacity=8):
        """capacity 크기의 빈 버킷 배열로 해시맵을 초기화한다."""
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._buckets = [DoublyLinkedList() for _ in range(capacity)]
        self._size = 0

    @property
    def capacity(self):
        """현재 버킷 배열의 크기를 반환한다."""
        return len(self._buckets)

    def _index(self, key):
        """key의 FNV-1a 해시를 버킷 수로 나눈 인덱스를 반환한다."""
        return fnv1a_32(key) % self.capacity

    def _find_node(self, bucket, key):
        """버킷 연결 리스트에서 key가 일치하는 Node를 찾아 반환한다."""
        for node in bucket:
            if node.data[0] == key:
                return node
        return None

    def put(self, key, value):
        """key에 value를 저장한다. 이미 존재하면 값을 덮어쓴다."""
        bucket = self._buckets[self._index(key)]
        node = self._find_node(bucket, key)
        if node is not None:
            node.data = (key, value)
            return
        bucket.insert_back((key, value))
        self._size += 1

    def get(self, key):
        """key에 해당하는 값을 반환한다. 없으면 None을 반환한다."""
        bucket = self._buckets[self._index(key)]
        node = self._find_node(bucket, key)
        if node is None:
            return None
        return node.data[1]

    def contains(self, key):
        """key가 해시맵에 존재하면 True, 없으면 False를 반환한다."""
        bucket = self._buckets[self._index(key)]
        return self._find_node(bucket, key) is not None

    def keys(self):
        """저장된 모든 키를 리스트로 반환한다."""
        result = []
        for bucket in self._buckets:
            for node in bucket:
                result.append(node.data[0])
        return result

    def size(self):
        """저장된 키 개수를 정수로 반환한다."""
        return self._size
