from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers
from digestapi.models import Book
from .categories_view import CategorySerializer


    # Override default serialization to replace foreign keys
    # with expanded related resource. By default, this would
    # be a list of integers (e.g. [2, 4, 9]).
    # need to serialize regardless of relationship so Django can accurately convert into Python data and rendered into JSON
class BookSerializer(serializers.ModelSerializer):

    # Both Declare that an ad-hoc property that isn't directly on Book model and should be included in JSON
    categories = CategorySerializer(many=True)
    is_owner = serializers.SerializerMethodField()

    # Function containing instructions for ad-hoc property
    def get_is_owner(self, obj):
        # Check if the authenticated user is the owner
        return self.context['request'].user == obj.user

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn_number', 'img_url', 'is_owner', 'categories']


class BookViewSet(viewsets.ViewSet):

    def list(self, request):
        books = Book.objects.all()
        # in order for customized serializer to work, request object needs to provide context to serializer.
        # context allows serializer to access request
        serializer = BookSerializer(books, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
            serializer = BookSerializer(book, context={'request': request})
            return Response(serializer.data)

        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        # Get the data from the client's JSON payload
        title = request.data.get('title')
        author = request.data.get('author')
        isbn_number = request.data.get('isbn_number')
        img_url = request.data.get('img_url')

        # Create a book database row first, so you have a
        # primary key to work with
        book = Book.objects.create(
            user=request.user,
            title=title,
            author=author,
            img_url=img_url,
            isbn_number=isbn_number)

# categories is initially an array(with integers inside) in the JSON request body
# to handle this during creation, first gets list of integers from payload with request.data.get()
        # Establish the many-to-many relationships
        category_ids = request.data.get('categories', [])
        # after request.data.get() establish new relationship between book just created and categories using .set() on model property of categories
        book.categories.set(category_ids)

        serializer = BookSerializer(book, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:

            book = Book.objects.get(pk=pk)

            # Is the authenticated user allowed to edit this book?
            self.check_object_permissions(request, book)

            serializer = BookSerializer(data=request.data)
            if serializer.is_valid():
                book.title = serializer.validated_data['title']
                book.author = serializer.validated_data['author']
                book.isbn_number = serializer.validated_data['isbn_number']
                book.img_url = serializer.validated_data['img_url']
                book.save()

                category_ids = request.data.get('categories', [])
                book.categories.set(category_ids)

                serializer = BookSerializer(book, context={'request': request})
                return Response(None, status.HTTP_204_NO_CONTENT)

            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            book = Book.objects.get(pk=pk)
            self.check_object_permissions(request, book)
            book.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)