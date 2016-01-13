# -*- coding: utf-8 -*-

from radiople.db import Session
from radiople.service import Service

from radiople.model.category import Category

from sqlalchemy import asc


class CategoryService(Service):

    __model__ = Category

    def get_all(self):
        return Session.query(self.__model__) \
            .order_by(asc(Category.seq)).all()

    def exists(self, category_id):
        return Session.query(
            Session.query(self.__model__)
            .filter(Category.id == category_id).exists()
        ).scalar()


class ApiCategoryService(CategoryService):

    pass


class WebCategoryService(CategoryService):

    pass


class ConsoleCategoryService(CategoryService):

    pass


service = CategoryService()
api_service = ApiCategoryService()
web_service = WebCategoryService()
console_service = ConsoleCategoryService()
