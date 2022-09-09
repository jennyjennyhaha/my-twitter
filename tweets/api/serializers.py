from accounts.api.serializers import UserSerializer
from rest_framework import serializers
from tweets.models import Tweet


# serializer: inquery from database and output to frontend
class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')


class TweetCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Tweet
        fields = ('content',)

    # rewrite the create method in TweetCreateSerializer. the create() method will be called
    # when save() is called to save the post

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet
