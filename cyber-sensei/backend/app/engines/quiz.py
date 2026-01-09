from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func

from ..models import QuizQuestion, Topic


class QuizEngine:
    def __init__(self, db: Session):
        self.db = db

    def _fetch_questions(self, topic_id: int, randomize: bool = False) -> list[QuizQuestion]:
        query = (
            self.db.query(QuizQuestion)
            .filter(QuizQuestion.topic_id == topic_id)
            .options(selectinload(QuizQuestion.options))
        )
        if randomize:
            query = query.order_by(func.random())
        else:
            query = query.order_by(QuizQuestion.id.asc())
        return query.all()

    def _resolve_topic_name(self, topic_id: int) -> str | None:
        topic = self.db.query(Topic).filter(Topic.id == topic_id).first()
        return topic.name if topic else None

    def get_quiz(self, topic_id: int, randomize: bool = False) -> list[dict]:
        questions = self._fetch_questions(topic_id, randomize)
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

    def get_question_by_id(self, question_id: int):
        return self.db.query(QuizQuestion).filter(QuizQuestion.id == question_id).options(selectinload(QuizQuestion.options)).first()

    def question_exists(self, question_id: int) -> bool:
        return self.db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first() is not None

    def get_question_count(self, topic_id: int) -> int:
        return self.db.query(QuizQuestion).filter(QuizQuestion.topic_id == topic_id).count()

    def get_quiz_subset(self, topic_id: int, limit: int = 5, randomize: bool = False):
        query = self.db.query(QuizQuestion).filter(QuizQuestion.topic_id == topic_id).options(selectinload(QuizQuestion.options))
        if randomize:
            query = query.order_by(func.random())
        return query.limit(limit).all()

    def add_question(self, topic_id: int, prompt: str, explanation: str, options_dict: dict):
        from ..models import QuizOption
        options = []
        for key, (text, is_correct) in options_dict.items():
            options.append(QuizOption(option_key=key, label=text, is_correct=is_correct))
        question = QuizQuestion(topic_id=topic_id, prompt=prompt, explanation=explanation, options=options)
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

