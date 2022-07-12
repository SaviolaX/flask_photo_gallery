import uuid
import boto3
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from decouple import config

from .. import ALLOWED_EXTENSIONS, db
from .services import (filter_by_user_key_words_from_search_bar,
                       filter_photos_by_current_user_category,
                       get_all_categories_created_by_user,
                       get_photo_by_id_and_current_user,
                       get_category_object_by_chosen_category,
                       create_a_new_category_for_current_user,
                       create_a_new_image_for_current_user,
                       get_category_object_by_id, filter_photos_by_category)

photos = Blueprint('photos', __name__)  # create route to current python module

BUCKET_NAME = config('BUCKET_NAME')

# AWS client connection
s3 = boto3.client('s3',
                  aws_access_key_id=config('ACCESS_KEY'),
                  aws_secret_access_key=config('SECRET_KEY'))


@photos.route('/', methods=['GET'])
def home_page():
    """Redirect from '/' to all user's photos page"""
    return redirect(url_for('photos.photo_list'))


@photos.route('/photos', methods=['GET', 'POST'])
@login_required
def photo_list():
    """Display all current user's photos"""
    if request.method == 'POST':
        search_bar_form = request.form.get('search')
        photos = filter_by_user_key_words_from_search_bar(search_bar_form)

    else:
        category = request.args.get('category')
        photos = filter_photos_by_current_user_category(category, current_user)

    categories = get_all_categories_created_by_user(current_user)

    return render_template('photos/photos.html',
                           user=current_user,
                           photos=photos,
                           categories=categories)


@photos.route('/photo/<int:photo_id>')
def photo_detail(photo_id):
    """Display a single photo"""
    photo = get_photo_by_id_and_current_user(photo_id, current_user)
    if photo:
        return render_template('photos/photo_detail.html',
                               user=current_user,
                               photo=photo)
    else:
        flash('Photo does not exist!', category='error')
        return redirect(url_for('photos.photo_list'))


def allowed_file(filename):
    """Return True or False if type of the file in list of ALLOWED_EXTENSIONS"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@photos.route('/add_photo', methods=['GET', 'POST'])
@login_required
def photo_add():
    """Add a new photo to db"""
    categories = get_all_categories_created_by_user(current_user)
    if request.method == 'POST':
        image = request.files.get('image')
        description = request.form.get('description')
        chosen_category = request.form.get('category-choose')
        create_category_name = request.form.get('category-create')

        if create_category_name == '':
            category = get_category_object_by_chosen_category(chosen_category)
        else:
            category = create_a_new_category_for_current_user(
                create_category_name, current_user)

        if image.filename == '':
            flash('No selected file', category='error')
            return redirect(request.url)

        if image and allowed_file(image.filename):
            filename = secure_filename(
                str(uuid.uuid1()) + '_' + image.filename)

            # Amazon s3 bucket
            # Upload image straght to bucket without saving locally
            s3.upload_fileobj(image,
                              BUCKET_NAME,
                              filename,
                              ExtraArgs={"ContentType": image.content_type})

            create_a_new_image_for_current_user(filename, description,
                                                current_user, category)
            flash('Photo was uploaded successfully!', category='success')

            return redirect(url_for('photos.photo_list'))

    return render_template('photos/photo_add.html',
                           user=current_user,
                           categories=categories)


@photos.route('/<int:photo_id>/edit_photo', methods=['GET', 'POST'])
@login_required
def photo_edit(photo_id):
    """Edit photo obj"""
    photo = get_photo_by_id_and_current_user(photo_id, current_user)
    categories = get_all_categories_created_by_user(current_user)
    if photo:
        if request.method == 'POST':
            image = request.files.get('image')
            description = request.form.get('description')
            chosen_category = request.form.get('category-choose')
            create_category_name = request.form.get('category-create')

            if create_category_name == '':
                category = get_category_object_by_chosen_category(
                    chosen_category)

            else:
                category = create_a_new_category_for_current_user(
                    create_category_name, current_user)

            if image.filename == '':
                filename = photo.image
            else:
                if allowed_file(image.filename):
                    filename = secure_filename(
                        str(uuid.uuid1()) + '_' + image.filename)

                    # Amazon s3 bucket
                    # Delete previous object from s3 storage
                    s3.delete_object(Bucket=BUCKET_NAME, Key=photo.image)
                    # Upload a new image instead old one
                    s3.upload_fileobj(
                        image,
                        BUCKET_NAME,
                        filename,
                        ExtraArgs={"ContentType": image.content_type})

            # save changes to current photo
            photo.image = filename
            photo.description = description
            photo.category_id = category.id
            db.session.commit()

            flash('Photo was updated successfully!', category='success')
            return redirect(url_for('photos.photo_list'))
    else:
        flash('Photo does not exist!', category='error')
        return redirect(url_for('photos.photo_list'))

    return render_template('photos/photo_edit.html',
                           user=current_user,
                           photo=photo,
                           categories=categories)


@photos.route('/<int:photo_id>/delete_photo', methods=['GET'])
@login_required
def photo_delete(photo_id):
    """Delete photo from db"""
    photo = get_photo_by_id_and_current_user(photo_id, current_user)

    if photo:
        if photo.user_id == current_user.id:
            # Delete object from s3 bucket
            s3.delete_object(Bucket=BUCKET_NAME, Key=photo.image)

            # Delete object from database
            db.session.delete(photo)
            db.session.commit()
            flash('Photo was deleted successfully!', category='success')
            return redirect(url_for('photos.photo_list'))

        else:
            flash('You can not delete photo, you are not the author!',
                  category='error')
            return redirect(url_for('photos.photo_list'))

    else:
        flash('Photo does not exist!', category='error')
        return redirect(url_for('photos.photo_list'))


@photos.route('/categories', methods=['GET'])
@login_required
def categories_list():
    """Get a list of all categories"""
    categories = get_all_categories_created_by_user(current_user)

    return render_template('photos/categories_settings.html',
                           user=current_user,
                           categories=categories)


@photos.route('/category/<int:category_id>/delete', methods=['GET'])
@login_required
def category_delete(category_id):
    """Delete category from db"""
    category = get_category_object_by_id(category_id)
    if category:
        # get all photos by category, change value each photo to None by iteration
        photos = filter_photos_by_category(category)
        for photo in photos:
            photo.category_id = None
        db.session.delete(category)
        db.session.commit()
        flash('Category was deleted successfully!', category='success')
        return redirect(url_for('photos.categories_list'))
    else:
        flash('Category does not exist!', category='error')
        return redirect(url_for('photos.categories_list'))
