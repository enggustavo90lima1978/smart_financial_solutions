from sqlalchemy import create_engine, text
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError

from src.settings import settings
from src.utils.exceptions import DatabaseFailedException

engine = create_engine(settings.database_uri)


def execute_query(
    user_query: str,
    parameters: dict[str, any] | None = None,
    commit: bool = False,
) -> Result:
    """
    Executes a SQL query against the database.

    Args:
        user_query: The SQL query string to be executed.
        parameters: A dictionary of parameters to bind to the query.
        commit: If True, commits the transaction after execution.

    Returns:
        The Result object from SQLAlchemy.

    Raises:
        SQLAlchemyError: If any database error occurs.
    """

    try:
        with engine.connect() as conn:
            query = text(user_query)
            result = conn.execute(query, parameters)
            if commit:
                conn.commit()
            return result
    except SQLAlchemyError as e:
        print(f'Database query failed: {e}')
        raise


def init_db() -> None:
    """Initializes the database by creating the 'charts' table if it doesn't exist."""
    query = """\
    CREATE TABLE IF NOT EXISTS charts(
    uuid VARCHAR(36) PRIMARY KEY,
    graph_json JSON,
    metadata VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    """

    try:
        execute_query(query)
        print('Database initialized successfully.')
    except SQLAlchemyError as e:
        print(f'Failed to initialize database: {e}')
        raise DatabaseFailedException


def get_graph_db(graph_id: str) -> str | None:
    """
    Retrieves the graph JSON for a given graph ID.

    Args:
        graph_id: The UUID of the graph to retrieve.

    Returns:
        The graph data as a JSON string, or None if not found.
    """

    query = 'SELECT graph_json FROM charts WHERE "uuid" = :graph_id LIMIT 1'
    try:
        result = execute_query(query, {'graph_id': graph_id})
        return result.scalar_one_or_none()
    except SQLAlchemyError:
        raise DatabaseFailedException


def get_graph_metadata(graph_id: str) -> str | None:
    """
    Retrieves the metadata for a given graph ID.

    Args:
        graph_id: The UUID of the graph to retrieve metadata for.

    Returns:
        The metadata as a string, or None if not found.
    """

    query = 'SELECT metadata FROM charts WHERE "uuid" = :graph_id LIMIT 1;'
    try:
        result = execute_query(query, {'graph_id': graph_id})
        return result.scalar_one_or_none()
    except SQLAlchemyError:
        raise DatabaseFailedException


def insert_graphs_db(
    graph_id: str, graph_json: str, metadata: str | None = None
) -> None:
    """Inserts a new graph record into the database."""

    query = 'INSERT INTO charts ("uuid", "graph_json", "metadata") VALUES (:graph_id, :graph_json, :metadata)'
    params = {'graph_id': graph_id, 'graph_json': graph_json, 'metadata': metadata}

    execute_query(query, params, commit=True)
