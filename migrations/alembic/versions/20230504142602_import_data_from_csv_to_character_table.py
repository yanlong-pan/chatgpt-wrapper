"""import data from csv to character table

Revision ID: 20230504142602
Revises: 20230504141940
Create Date: 2023-05-04 14:26:03.886868

"""
import csv
import os
from alembic import op
from sqlalchemy import delete, insert

from chatgpt_wrapper.backends.openai.orm import Character


# revision identifiers, used by Alembic.
revision = '20230504142602'
down_revision = '20230504141940'
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
        stmt = insert(Character).values(data)
        conn.execute(stmt)

def downgrade():
    conn = op.get_bind()
    stmt = delete(Character)
    conn.execute(stmt)
