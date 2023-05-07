"""import_data_from_csv_to_character_table

Revision ID: 20230506213504
Revises: 20230506175017
Create Date: 2023-05-06 21:35:05.438059

"""
import csv
import os
from alembic import op
import sqlalchemy as sa

from chatgpt_wrapper.backends.openai.orm import Character


# revision identifiers, used by Alembic.
revision = '20230506213504'
down_revision = '20230506175017'
branch_labels = None
depends_on = None

dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))

def upgrade():
    conn = op.get_bind()
    csv_path = f'{dir_path}/../../database/{conn.dialect.name}/character.csv'
    with open(csv_path) as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        data = [dict(zip(headers, row)) for row in reader]
        stmt = sa.insert(Character).values(data)
        conn.execute(stmt)

def downgrade():
    conn = op.get_bind()
    stmt = sa.delete(Character)
    conn.execute(stmt)
