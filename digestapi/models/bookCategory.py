from django.db import models

class BookCategory(models.Model):
    # related_name needs to be unique aka not the same as other models like Review
    book = models.ForeignKey("Book", on_delete=models.CASCADE, related_name="book_category")
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="book_category")
    date = models.DateField(auto_now_add=True)