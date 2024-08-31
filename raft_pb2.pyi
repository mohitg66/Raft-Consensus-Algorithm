from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LogEntry(_message.Message):
    __slots__ = ("operation", "term", "index", "key", "value")
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    operation: str
    term: int
    index: int
    key: str
    value: str
    def __init__(self, operation: _Optional[str] = ..., term: _Optional[int] = ..., index: _Optional[int] = ..., key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class AppendEntryArgs(_message.Message):
    __slots__ = ("term", "leader_id", "prev_log_index", "prev_log_term", "entries", "leader_commit", "lease_duration")
    TERM_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    PREV_LOG_INDEX_FIELD_NUMBER: _ClassVar[int]
    PREV_LOG_TERM_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    LEADER_COMMIT_FIELD_NUMBER: _ClassVar[int]
    LEASE_DURATION_FIELD_NUMBER: _ClassVar[int]
    term: int
    leader_id: int
    prev_log_index: int
    prev_log_term: int
    entries: _containers.RepeatedCompositeFieldContainer[LogEntry]
    leader_commit: int
    lease_duration: int
    def __init__(self, term: _Optional[int] = ..., leader_id: _Optional[int] = ..., prev_log_index: _Optional[int] = ..., prev_log_term: _Optional[int] = ..., entries: _Optional[_Iterable[_Union[LogEntry, _Mapping]]] = ..., leader_commit: _Optional[int] = ..., lease_duration: _Optional[int] = ...) -> None: ...

class AppendEntryReply(_message.Message):
    __slots__ = ("term", "success")
    TERM_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    term: int
    success: bool
    def __init__(self, term: _Optional[int] = ..., success: bool = ...) -> None: ...

class RequestVoteArgs(_message.Message):
    __slots__ = ("term", "candidate_id", "last_log_index", "last_log_term", "remaining_leader_lease_duration")
    TERM_FIELD_NUMBER: _ClassVar[int]
    CANDIDATE_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_LOG_INDEX_FIELD_NUMBER: _ClassVar[int]
    LAST_LOG_TERM_FIELD_NUMBER: _ClassVar[int]
    REMAINING_LEADER_LEASE_DURATION_FIELD_NUMBER: _ClassVar[int]
    term: int
    candidate_id: int
    last_log_index: int
    last_log_term: int
    remaining_leader_lease_duration: int
    def __init__(self, term: _Optional[int] = ..., candidate_id: _Optional[int] = ..., last_log_index: _Optional[int] = ..., last_log_term: _Optional[int] = ..., remaining_leader_lease_duration: _Optional[int] = ...) -> None: ...

class RequestVoteReply(_message.Message):
    __slots__ = ("term", "vote_granted")
    TERM_FIELD_NUMBER: _ClassVar[int]
    VOTE_GRANTED_FIELD_NUMBER: _ClassVar[int]
    term: int
    vote_granted: bool
    def __init__(self, term: _Optional[int] = ..., vote_granted: bool = ...) -> None: ...

class ClientRequest(_message.Message):
    __slots__ = ("operation", "key", "value")
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    operation: str
    key: str
    value: str
    def __init__(self, operation: _Optional[str] = ..., key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class ServeClientReply(_message.Message):
    __slots__ = ("data", "leader_id", "success")
    DATA_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    data: str
    leader_id: str
    success: bool
    def __init__(self, data: _Optional[str] = ..., leader_id: _Optional[str] = ..., success: bool = ...) -> None: ...
