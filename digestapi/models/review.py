from django.db import models
from django.contrib.auth.models import User

# look at ERD and each row should correspond to field in model
# "Book" is referencing the Book model because of the fk relationship
# on_delete=models.CASCADE handles what happens when "Book" is deleted, all associated "Review" objects are deleted to maintain integrity
# related_name="reviews" specifies name for inverse relationship(Book to Review)
# allows access to associated reviews for a book
class Review(models.Model):
    book = models.ForeignKey("Book", on_delete=models.CASCADE, related_name="reviews")
    # don't need quotes for User because built in from Django, 
    # if fk model is defined in same module or app where defining current model, good practice to use ""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    #? specifies positive integer
    rating = models.PositiveIntegerField() 
    comment = models.CharField(max_length=1000)
    #? auto_now_add sets date upon creation, doesn't update
    date = models.DateField(auto_now_add=True)