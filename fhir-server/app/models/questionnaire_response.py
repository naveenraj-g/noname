from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    ForeignKey,
    Text,
    Boolean,
    Float,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import FHIRBase as Base


class QuestionnaireResponseModel(Base):
    __tablename__ = "questionnaire_response"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    # user_id = Column(String, nullable=True)
    org_id = Column(String, nullable=True)

    # Required
    questionnaire = Column(String, nullable=False)  # canonical URL
    status = Column(
        String, nullable=False
    )  # in-progress | completed | amended | entered-in-error | stopped

    # Subject
    subject_reference = Column(String, nullable=True)
    subject_display = Column(String, nullable=True)

    # Encounter
    encounter_reference = Column(String, nullable=True)

    # Authored / Author / Source
    authored = Column(DateTime(timezone=True), nullable=True)
    author_reference = Column(String, nullable=True)
    author_display = Column(String, nullable=True)
    source_reference = Column(String, nullable=True)
    source_display = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    items = relationship(
        "QuestionnaireResponseItemModel",
        back_populates="response",
        cascade="all, delete-orphan",
        foreign_keys="QuestionnaireResponseItemModel.response_id",
    )


class QuestionnaireResponseItemModel(Base):
    __tablename__ = "questionnaire_response_item"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    response_id = Column(
        Integer, ForeignKey("questionnaire_response.id"), nullable=False, index=True
    )
    parent_item_id = Column(
        Integer, ForeignKey("questionnaire_response_item.id"), nullable=True, index=True
    )
    org_id = Column(String, nullable=True)

    link_id = Column(String, nullable=False)
    text = Column(String, nullable=True)
    definition = Column(String, nullable=True)

    response = relationship(
        "QuestionnaireResponseModel",
        back_populates="items",
        foreign_keys=[response_id],
    )
    answers = relationship(
        "QuestionnaireResponseAnswerModel",
        back_populates="item",
        cascade="all, delete-orphan",
    )
    sub_items = relationship(
        "QuestionnaireResponseItemModel",
        cascade="all, delete-orphan",
        foreign_keys=[parent_item_id],
    )


class QuestionnaireResponseAnswerModel(Base):
    __tablename__ = "questionnaire_response_answer"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    item_id = Column(
        Integer,
        ForeignKey("questionnaire_response_item.id"),
        nullable=False,
        index=True,
    )
    org_id = Column(String, nullable=True)

    # Discriminator for which value[x] is stored
    value_type = Column(String, nullable=False)

    # Scalar values
    value_string = Column(
        Text, nullable=True
    )  # valueString, valueUri, valueTime, valueDate
    value_boolean = Column(Boolean, nullable=True)  # valueBoolean
    value_integer = Column(Integer, nullable=True)  # valueInteger
    value_decimal = Column(Float, nullable=True)  # valueDecimal
    value_datetime = Column(DateTime(timezone=True), nullable=True)  # valueDateTime

    # valueCoding
    value_coding_system = Column(String, nullable=True)
    value_coding_code = Column(String, nullable=True)
    value_coding_display = Column(String, nullable=True)

    # valueReference
    value_reference = Column(String, nullable=True)
    value_reference_display = Column(String, nullable=True)

    # valueQuantity
    value_quantity_value = Column(Float, nullable=True)
    value_quantity_unit = Column(String, nullable=True)
    value_quantity_system = Column(String, nullable=True)
    value_quantity_code = Column(String, nullable=True)

    item = relationship("QuestionnaireResponseItemModel", back_populates="answers")
