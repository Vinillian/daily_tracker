from typing import List, Dict, Optional
from pydantic import Field
from datetime import datetime
from .base import SerializableModel


class Note(SerializableModel):
    """Модель заметки"""
    text: str = Field(..., description="Текст заметки")
    note_type: str = Field("💡 Обычная", description="Тип заметки")
    importance: str = Field("🟡 Средняя", description="Важность")
    time: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M"))

    @classmethod
    def from_old_format(cls, text: str) -> 'Note':
        """Создать из старого формата (просто строка)"""
        return cls(text=text)


class NotesSection(SerializableModel):
    """Раздел заметок"""
    notes: List[Note] = Field(default_factory=list)

    @classmethod
    def from_old_format(cls, old_notes: List[str]) -> 'NotesSection':
        """Конвертировать из старого формата"""
        notes = [Note.from_old_format(text) for text in old_notes]
        return cls(notes=notes)

    def to_old_format(self) -> List[str]:
        """Конвертировать в старый формат для обратной совместимости"""
        return [note.text for note in self.notes]