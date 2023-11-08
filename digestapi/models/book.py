from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="books_created")
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn_number = models.CharField(max_length=13, null=True, blank=True)
    img_url = models.URLField(null=True, blank=True)
    # categories is not field in Books table, but property on instances of Book that automatically contain all related categories for the book
    # does this eliminate need to expand query for this?
    categories = models.ManyToManyField(
        # first argument is name of table on other side of many-to-many relationship
        "Category",
        # second argument tells Django which model will story the relationship(s)
        through='BookCategory',
        # third argument is what property will be added to instances of Category model to contain related list of books
        related_name="books"
    )