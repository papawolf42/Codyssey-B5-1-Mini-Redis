"""해시맵(Hash Map) 모듈."""


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
