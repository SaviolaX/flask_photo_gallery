from .models import Photo, Category
from core import db


def create_a_new_image_for_current_user(filename, description, current_user, category):
    new_image = Photo(image=filename,
                      description=description,
                      user_id=current_user.id,
                      category_id=category.id)
    db.session.add(new_image)
    db.session.commit()


def create_a_new_category_for_current_user(category_name, current_user):
    category = Category(name=category_name, user_id=current_user.id)
    db.session.add(category)
    db.session.commit()
    return category


def get_category_object_by_id(category_id):
    category = Category.query.filter_by(id=category_id).first()
    return category


def get_category_object_by_chosen_category(chosen_category):
    category = Category.query.filter_by(name=chosen_category).first()
    return category


def get_photo_by_id_and_current_user(photo_id, current_user):
    photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first()
    return photo


def get_all_categories_created_by_user(current_user):
    categories = Category.query.filter_by(user_id=current_user.id).order_by('name')
    return categories


def filter_by_user_key_words_from_search_bar(data_from_form):
    """Get a data from html form and filter photos by the data in description"""
    photos = Photo.query
    photos = photos.filter(
        Photo.description.like('%' + str(data_from_form) + '%'))
    photos = photos.order_by(Photo.description).all()
    return photos

def filter_photos_by_category(category):
    photos = Photo.query.filter_by(category_id=category.id)
    return photos


def filter_photos_by_current_user_category(category_id, current_user):
    """Filter photos by category"""
    if category_id == None:
        photos = Photo.query.filter_by(user_id=current_user.id)
    else:
        photos = Photo.query.filter_by(category_id=category_id,
                                       user_id=current_user.id)
    return photos