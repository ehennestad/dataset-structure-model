"""What a walk produces: entity records, unmatched entries, and the result envelope."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class Issue:
    code: str
    message: str = ""

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message}


@dataclass
class LocationEntry:
    data_location: str
    root_storage_path: str
    file_system_type: str
    paths: List[str]
    files: Optional[Dict[str, List[str]]] = None
    is_complete: Optional[bool] = None

    def to_dict(self) -> dict:
        doc = {"dataLocationIdentifier": self.data_location,
               "rootStoragePathIdentifier": self.root_storage_path,
               "fileSystemType": self.file_system_type,
               "paths": sorted(self.paths)}
        if self.files is not None:
            doc["files"] = {name: sorted(paths) for name, paths in self.files.items()}
        if self.is_complete is not None:
            doc["isComplete"] = self.is_complete
        return doc


@dataclass
class Record:
    entity_type: str
    identity: Dict[str, Any]
    parents: List[Tuple[str, Dict[str, Any]]]
    locations: List[LocationEntry]
    metadata: Dict[str, Any]
    issues: List[Issue] = field(default_factory=list)

    def to_dict(self) -> dict:
        doc = {"entityType": self.entity_type,
               "identity": dict(self.identity),
               "parents": [{"entityType": t, "identity": dict(i)} for t, i in self.parents],
               "locations": [loc.to_dict() for loc in self.locations],
               "metadata": dict(self.metadata)}
        if self.issues:
            doc["issues"] = [issue.to_dict() for issue in self.issues]
        return doc


@dataclass
class Unmatched:
    data_location: str
    root_storage_path: str
    path: str
    reason: str
    detail: str = ""

    def to_dict(self, include_detail: bool = True) -> dict:
        doc = {"dataLocationIdentifier": self.data_location,
               "rootStoragePathIdentifier": self.root_storage_path,
               "path": self.path,
               "reason": self.reason}
        if include_detail and self.detail:
            doc["detail"] = self.detail
        return doc


@dataclass
class WalkResult:
    records: List[Record]
    unmatched: List[Unmatched]
    environment: Optional[str] = None
    roots: List[Tuple[str, str, int]] = field(default_factory=list)
    unresolved_extractors: Set[str] = field(default_factory=set)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self, include_detail: bool = True) -> dict:
        return {"records": [r.to_dict() for r in self.records],
                "unmatched": [u.to_dict(include_detail) for u in self.unmatched]}
