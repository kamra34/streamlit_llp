import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URI = "postgresql://kami:4444@eu1.pitunnel.com:20877/svenska"
engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define models
class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, index=True)
    translation = Column(String)
    starting_letter = Column(String(1))
    comment = Column(Text)
    categories = relationship('WordCategory', back_populates='word')


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    words = relationship('WordCategory', back_populates='category')


class WordCategory(Base):
    __tablename__ = 'word_categories'

    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey('words.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))

    word = relationship('Word', back_populates='categories')
    category = relationship('Category', back_populates='words')


# Grouped Alphabetically Functionality
st.title("Grouped Alphabetically")

session = SessionLocal()

# Swedish alphabetic categories (A-Z, Å, Ä, Ö)
swedish_alphabet = [chr(i) for i in range(65, 91)] + ['Å', 'Ä', 'Ö']

# Sidebar for selecting an alphabetic category
selected_letter = st.sidebar.selectbox("Select a letter", swedish_alphabet)

# Fetch words from the database that match the selected category
words = session.query(Word).filter_by(starting_letter=selected_letter).all()

# Display the words and translations
st.header(f"Words starting with '{selected_letter}'")
for word in words:
    st.write(f"**{word.word}**: {word.translation}")
    st.text_area("Comments", word.comment, key=f"comment_{word.id}")

session.close()
