from sqlalchemy.orm import Session, selectinload

from ..models import QuizQuestion, Topic


class QuizEngine:
    def __init__(self, db: Session):
        self.db = db

    def _fetch_questions(self, topic_id: int) -> list[QuizQuestion]:
        return (
            self.db.query(QuizQuestion)
            .filter(QuizQuestion.topic_id == topic_id)
            .options(selectinload(QuizQuestion.options))
            .order_by(QuizQuestion.id.asc())
            .all()
        )

    def _resolve_topic_name(self, topic_id: int) -> str | None:
        topic = self.db.query(Topic).filter(Topic.id == topic_id).first()
        return topic.name if topic else None

    def get_quiz(self, topic_id: int) -> list[dict]:
        questions = self._fetch_questions(topic_id)
        if not questions:
            raise ValueError("No quiz defined for this topic.")

        quiz_payload: list[dict] = []
        for question in questions:
            quiz_payload.append(
                {
                    "id": question.id,
                    "prompt": question.prompt,
                    "explanation": question.explanation,
                    "options": [
                        {"key": option.option_key, "label": option.label}
                        for option in question.options
                    ],
                }
            )
        return quiz_payload

    def get_answer_key(self, topic_id: int) -> dict[str, str]:
        questions = self._fetch_questions(topic_id)
        if not questions:
            raise ValueError("No quiz defined for this topic.")

        answer_key: dict[str, str] = {}
        for question in questions:
            correct_option = next(
                (option.option_key for option in question.options if option.is_correct),
                None,
            )
            if not correct_option:
                raise ValueError(
                    f"Question '{question.id}' does not have a correct option configured."
                )
            answer_key[str(question.id)] = correct_option
        return answer_key

    def grade_submission(self, topic_id: int, answers: dict[str, str]) -> tuple[int, int]:
        key = self.get_answer_key(topic_id)
        total = len(key)
        correct = sum(1 for q_id, correct_answer in key.items() if answers.get(q_id) == correct_answer)
        return correct, total

