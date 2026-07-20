import os
import sys
import random

# Pastikan path bisa mengimpor models dari story_service
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.genre import Genre
from models.story import Story, StoryStatus
from models.story_genre import StoryGenre
from sqlalchemy import text

def seed_data():
    db = SessionLocal()
    try:
        # Dapatkan satu user ID yang valid dari tabel users
        result = db.execute(text("SELECT id FROM users LIMIT 1")).fetchone()
        if not result:
            print("Tidak ada user di database. Mohon register dulu 1 akun.")
            return
        
        user_id = result[0]
        
        # Buat genres jika belum ada
        genre_names = ["Romance", "Horror", "Fantasy", "Thriller", "Comedy", "Action", "Drama", "Mystery"]
        genre_objects = []
        for name in genre_names:
            g = db.query(Genre).filter(Genre.name == name).first()
            if not g:
                g = Genre(name=name)
                db.add(g)
                db.commit()
                db.refresh(g)
            genre_objects.append(g)
            
        print("Genres seeded.")
        
        # Buat 8 cerita dengan genre berbeda
        story_titles = [
            ("Cinta di Ambang Pagi", "Romance"),
            ("Misteri Rumah Tua", "Horror"),
            ("Dunia Pararel", "Fantasy"),
            ("Pelarian Berdarah", "Thriller"),
            ("Tetanggaku Aneh", "Comedy"),
            ("Pasukan Bayangan", "Action"),
            ("Air Mata Bintang", "Drama"),
            ("Detektif Amatir", "Mystery")
        ]
        
        for idx, (title, genre_name) in enumerate(story_titles):
            # Cek apakah cerita sudah ada
            existing_story = db.query(Story).filter(Story.title == title).first()
            if not existing_story:
                # Tambahkan random=idx supaya gambar dari lorem picsum berbeda-beda
                new_story = Story(
                    user_id=user_id,
                    title=title,
                    synopsis=f"Ini adalah sinopsis pendek untuk cerita {title}. Kisah ini penuh dengan elemen dari genre {genre_name}.",
                    cover_url=f"https://picsum.photos/400/600?random={idx+1}",
                    status=StoryStatus.published
                )
                
                # Temukan objek genre yang sesuai
                g = next((x for x in genre_objects if x.name == genre_name), None)
                if g:
                    new_story.genres.append(g)
                
                db.add(new_story)
        
        db.commit()
        print("Berhasil menambahkan 8 data cerita!")
        
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
