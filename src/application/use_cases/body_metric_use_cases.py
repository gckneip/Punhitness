from typing import List, Optional
from src.domain.entities.body_metric import BodyMetricEntry
from src.domain.repositories.body_metric_repository import BodyMetricRepository
from src.application.dto.body_metric_dto import CreateBodyMetricDTO, BodyMetricDTO


class BodyMetricUseCases:
    def __init__(self, body_metric_repository: BodyMetricRepository):
        self._body_metric_repository = body_metric_repository

    def log_metric(self, dto: CreateBodyMetricDTO) -> BodyMetricDTO:
        entry = BodyMetricEntry(
            recorded_at=dto.recorded_at,
            bodyweight=dto.bodyweight,
            measurements=dto.measurements,
            notes=dto.notes,
        )
        self._body_metric_repository.save(entry)
        return self._to_dto(entry)

    def update_metric(self, entry_id: str, dto: CreateBodyMetricDTO) -> Optional[BodyMetricDTO]:
        entry = self._body_metric_repository.find_by_id(entry_id)
        if entry is None:
            return None
        entry.recorded_at = dto.recorded_at
        entry.bodyweight = dto.bodyweight
        entry.measurements = dto.measurements
        entry.notes = dto.notes
        self._body_metric_repository.save(entry)
        return self._to_dto(entry)

    def list_metrics(self, limit: Optional[int] = None) -> List[BodyMetricDTO]:
        return [self._to_dto(e) for e in self._body_metric_repository.find_all(limit=limit)]

    def delete_metric(self, entry_id: str) -> None:
        self._body_metric_repository.delete(entry_id)

    def _to_dto(self, entry: BodyMetricEntry) -> BodyMetricDTO:
        return BodyMetricDTO(
            id=entry.id,
            recorded_at=entry.recorded_at,
            bodyweight=entry.bodyweight,
            measurements=entry.measurements,
            notes=entry.notes,
        )
