import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from config import SQLALCHEMY_DATABASE_URI

# SQLAlchemy setup
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


# Add/Edit Word and Category Functionality
st.title("Add/Edit Words and Categories")

session = SessionLocal()

# Fetch all categories
categories = session.query(Category).all()
category_names = [category.name for category in categories]

# Manage Words Container
with st.container():
    st.subheader("Manage Words")

    # Section to add a new word
    new_word = st.text_input("Swedish Word")
    new_translation = st.text_input("Translation")
    new_comment = st.text_area("Comment")
    selected_categories = st.multiselect("Select Categories", category_names)

    if st.button("Add Word"):
        if new_word and new_translation:
            new_entry = Word(
                word=new_word,
                translation=new_translation,
                starting_letter=new_word[0].upper(),
                comment=new_comment
            )
            session.add(new_entry)
            session.commit()

            for cat_name in selected_categories:
                category = session.query(Category).filter_by(name=cat_name).first()
                word_category = WordCategory(word_id=new_entry.id, category_id=category.id)
                session.add(word_category)
            session.commit()

            st.success(f"Added '{new_word}'")
            st.rerun()
        else:
            st.error("Please provide both the word and its translation.")

# Edit or Delete Existing Words in an Expander
with st.expander("Edit or Delete Existing Words"):
    st.subheader("Edit or Delete Existing Words")
    words = session.query(Word).all()
    word_to_edit = st.selectbox("Select a word to edit", [word.word for word in words])

    if word_to_edit:
        word = session.query(Word).filter_by(word=word_to_edit).first()
        edited_word = st.text_input("Edit Word", value=word.word)
        edited_translation = st.text_input("Edit Translation", value=word.translation)
        edited_comment = st.text_area("Edit Comment", value=word.comment)
        edited_categories = st.multiselect(
            "Edit Categories", category_names,
            default=[cat.category.name for cat in word.categories]
        )

        if st.button("Update Word"):
            if edited_word and edited_translation:
                word.word = edited_word
                word.translation = edited_translation
                word.comment = edited_comment
                word.starting_letter = edited_word[0].upper()
                session.commit()

                # Update categories
                session.query(WordCategory).filter_by(word_id=word.id).delete()
                for cat_name in edited_categories:
                    category = session.query(Category).filter_by(name=cat_name).first()
                    word_category = WordCategory(word_id=word.id, category_id=category.id)
                    session.add(word_category)
                session.commit()

                st.success(f"Updated '{word_to_edit}'")
                st.rerun()
            else:
                st.error("Please provide both the word and its translation.")

        if st.button("Delete Word"):
            session.query(WordCategory).filter_by(word_id=word.id).delete()
            session.delete(word)
            session.commit()
            st.success(f"Deleted '{word_to_edit}'")
            st.rerun()

# Manage Categories in an Expander
with st.expander("Manage Categories"):
    st.subheader("Manage Categories")

    # First Row: Add new category and View all categories
    col1, col2 = st.columns(2)

    with col1:
        new_category_name = st.text_input("New Category Name")
        if st.button("Add Category"):
            if new_category_name:
                if new_category_name not in category_names:
                    new_category = Category(name=new_category_name)
                    session.add(new_category)
                    session.commit()
                    st.success(f"Category '{new_category_name}' added.")
                    st.rerun()
                else:
                    st.error(f"Category '{new_category_name}' already exists.")
            else:
                st.error("Please enter a category name.")

    with col2:
        st.write("### All Categories")
        st.markdown("\n".join([f"- {category}" for category in category_names]))

    # Second Row: Rename category and Delete category
    col3, col4 = st.columns(2)

    with col3:
        selected_category_to_rename = st.selectbox("Select Category to Rename", category_names)
        new_category_name_for_rename = st.text_input("New Category Name for Rename")
        if st.button("Rename Category"):
            if selected_category_to_rename and new_category_name_for_rename:
                category = session.query(Category).filter_by(name=selected_category_to_rename).first()
                if category:
                    category.name = new_category_name_for_rename
                    session.commit()
                    st.success(f"Category '{selected_category_to_rename}' renamed to '{new_category_name_for_rename}'.")
                    st.rerun()
                else:
                    st.error("Category not found.")
            else:
                st.error("Please select a category and enter a new name.")

    with col4:
        selected_category_to_delete = st.selectbox("Select Category to Delete", category_names)
        if st.button("Delete Category"):
            if selected_category_to_delete:
                category = session.query(Category).filter_by(name=selected_category_to_delete).first()
                if category:
                    session.query(WordCategory).filter_by(category_id=category.id).delete()  # Delete related word-category mappings
                    session.delete(category)
                    session.commit()
                    st.success(f"Category '{selected_category_to_delete}' deleted.")
                    st.rerun()
                else:
                    st.error("Category not found.")
            else:
                st.error("Please select a category to delete.")

session.close()
