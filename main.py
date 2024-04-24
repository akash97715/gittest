import sqlalchemy as sa
from alembic import op

def upgrade() -> None:
    op.add_column(
        "data_ingestion_status_table",
        sa.Column("table_figure_metadata", sa.JSONB, nullable=True),
    )
 
def downgrade() -> None:
    op.drop_column("data_ingestion_status_table", "table_figure_metadata")
