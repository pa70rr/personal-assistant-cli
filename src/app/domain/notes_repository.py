from sqlmodel import Session, or_, select

from app.domain.common.repository import BaseRepository
from app.domain.models import Note, NoteTagLink, Tag


class NotesRepository(BaseRepository):
    """Репозиторій нотаток — CRUD + пошук по тегах."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, note: Note) -> Note:
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        return note

    def get_by_id(self, note_id: int) -> Note | None:
        return self.session.get(Note, note_id)

    def list_all(self) -> list[Note]:
        statement = select(Note)
        return list(self.session.exec(statement).all())

    def search(self, query: str) -> list[Note]:
        statement = select(Note).where(
            or_(
                Note.title.contains(query),
                Note.body.contains(query),
            )
        )
        return list(self.session.exec(statement).all())

    def search_by_tag(self, tag: str) -> list[Note]:
        statement = select(Note).join(NoteTagLink).join(Tag).where(Tag.name == tag)
        return list(self.session.exec(statement).all())

    def add_with_tags(self, note: Note, tag_names: list[str]) -> Note:
        for name in tag_names:
            statement = select(Tag).where(Tag.name == name)
            tag = self.session.exec(statement).first()
            if tag is None:
                tag = Tag(name=name)
            note.tags.append(tag)

        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        return note

    def update(self, note: Note) -> Note:
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        return note

    def delete(self, note_id: int) -> None:
        note = self.get_by_id(note_id)
        if note:
            self.session.delete(note)
            self.session.commit()
