from rest_framework import viewsets, status, serializers, permissions
from rest_framework.response import Response
from digestapi.models import Review, Book

# SerializerMethodField allows added custom field in serialized representation of an object
class ReviewSerializer(serializers.ModelSerializer):
    # is_owner is custom field name being defined
    # serializers.SerializerMethodField part that specifies is_owner is custom field and value determined by get_is_owner method
    # telling Django that instead of regular database field, value of is_owner computed by custom method get_is_owner
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'book', 'user', 'rating', 'comment', 'date', 'is_owner']
        read_only_fields = ['user']

# calculates value of is_owner field, when is_owner accessed, it will execute this method to see if user making request is user that owns object being serialized
    def get_is_owner(self, obj):
        # Check if the user making request is the owner of the review being serialized
    
        return self.context['request'].user == obj.user


class ReviewViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        # Get all reviews
        reviews = Review.objects.all()
        # Serialize the objects, and pass request to determine owner
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})

        # Return the serialized data with 200 status code
        return Response(serializer.data, status=status.HTTP_200_OK)


# can create a fixture to seed reviews or use Postman
    def create(self, request):
        # Create a new instance of a review and assign property
        # values from the request payload using `request.data`
        # book_id and user_id established in Review model as fk so only need remaining fields
        # book_id is referencing the id for each book in the Book model
        # it can be renamed here to book_id for clarity purposes
        # ?can handle create like below or like Books model
        reviewed_book = Book.objects.get(pk=request.data['book_id'])

        review = Review()

        review.user = request.auth.user
        review.book = reviewed_book
        review.rating = request.data['rating']
        review.comment = request.data['comment']


        # Save the review
        review.save()
        review.date = review.date.strftime('%Y-%m-%d')
        try:
            # Serialize the objects, and pass request as context
            serializer = ReviewSerializer(review, context={'request': request})
            # Return the serialized data with 201 status code
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as ex:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            # Get the requested review
            # pk=pk way to use pk if included in request, if not, defaults to None
            review = Review.objects.get(pk=pk)
            # Serialize the object (make sure to pass the request as context)
            serializer = ReviewSerializer(review, context={'request': request})
            # Return the review with 200 status code
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Review.DoesNotExist:
            # if pk defults to None this except error is triggered
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            # Get the requested review
            review = Review.objects.get(pk=pk)

            # Check if the user has permission to delete
            # Will return 403 if authenticated user is not author
            if review.user.id != request.user.id:
                return Response(status=status.HTTP_403_FORBIDDEN)

            # Delete the review
            review.delete()

            # Return success but no body
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)