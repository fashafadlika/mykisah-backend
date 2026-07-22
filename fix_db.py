from sqlalchemy import create_engine, text

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost:3306/mykisah_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

try:
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE chapters ADD COLUMN cover_url VARCHAR(500) NULL"))
    print("Berhasil menambahkan kolom cover_url ke tabel chapters!")
except Exception as e:
    if "Duplicate column name" in str(e):
        print("Kolom cover_url sudah ada, aman!")
    else:
        print(f"Error: {e}")
