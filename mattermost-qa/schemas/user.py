"""/users/* 응답의 JSON 스키마.

스키마 검증이 잡는 것: 필드 누락, 타입 변경(예: 숫자→문자열), 들어가면 안 되는 필드.
값 하나하나를 assert하지 않아도 "응답 형식 계약"이 깨지면 바로 실패한다.
"""
USER = {
    "type": "object",
    "required": ["id", "username", "email", "roles", "create_at", "update_at", "delete_at", "locale"],
    "properties": {
        "id": {"type": "string", "pattern": "^[a-z0-9]{26}$"},  # Mattermost ID는 26자 소문자·숫자
        "username": {"type": "string", "minLength": 1},
        "email": {"type": "string", "format": "email"},
        "roles": {"type": "string"},
        "create_at": {"type": "integer"},
        "update_at": {"type": "integer"},
        "delete_at": {"type": "integer"},
        "locale": {"type": "string"},
    },
    # 비밀번호나 해시가 응답에 실리면 심각한 결함이다. 스키마 차원에서 금지한다.
    "not": {"anyOf": [{"required": ["password"]}, {"required": ["mfa_secret"]}]},
}

ERROR = {
    "type": "object",
    "required": ["id", "message", "status_code"],
    "properties": {
        "id": {"type": "string"},
        "message": {"type": "string"},
        "status_code": {"type": "integer"},
    },
}
