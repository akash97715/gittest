def upgrade() -> None:
    pass
 
 
def downgrade() -> None:
    pass
 
 
 
def upgrade() -> None:
    op.add_column(
        "data_ingestion_status_table",
        sa.Column("chunked_as_parent_child", sa.Boolean, nullable=True),
    )
    op.execute("UPDATE data_ingestion_status_table SET chunked_as_parent_child=False WHERE chunked_as_parent_child is null")
 
def downgrade() -> None:
    op.drop_column("data_ingestion_status_table", "chunked_as_parent_child")
