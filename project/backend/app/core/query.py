from sqlmodel import Session, SQLModel, select, func, col


def apply_ordering(statement, model: type[SQLModel], order_by: str, order_dir: str, default: str):
    """Order by a real column of the model; unknown fields fall back to the default"""
    field = order_by if order_by in model.model_fields else default
    column = col(getattr(model, field))
    return statement.order_by(column.asc() if order_dir.lower() == "asc" else column.desc())


def count_rows(session: Session, statement) -> int:
    """Total rows matched by a select statement (before pagination)"""
    return session.exec(select(func.count()).select_from(statement.subquery())).one()
