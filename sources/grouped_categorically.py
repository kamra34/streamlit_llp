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


# Grouped Categorically Functionality
st.title("Grouped Categorically")

session = SessionLocal()

# Fetch all categories
categories = session.query(Category).all()
category_names = [category.name for category in categories]

# Sidebar for selecting a category
selected_category = st.sidebar.selectbox("Select a category", category_names)

# Fetch words from the database that match the selected category
category = session.query(Category).filter_by(name=selected_category).first()
words = [wc.word for wc in category.words]

# Display the words and translations
st.header(f"Words in the category '{selected_category}'")
for word in words:
    st.write(f"**{word.word}**: {word.translation}")
    st.text_area("Comments", word.comment, key=f"comment_{word.id}")

session.close()
