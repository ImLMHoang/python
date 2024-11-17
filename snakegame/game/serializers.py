from rest_framework import serializers


class NodeSerializer(serializers.Serializer):
    row = serializers.IntegerField()
    col = serializers.IntegerField()
    fVal = serializers.FloatField()  
    hVal = serializers.FloatField()
    gVal = serializers.FloatField() 
    parent = serializers.CharField()

# Serializer cho SnakeLogic
class SnakeLogicSerializer(serializers.Serializer):
    gameOver = serializers.BooleanField()
    score = serializers.IntegerField()
    gameStarted = serializers.BooleanField()
    canMove = serializers.BooleanField()
    boardSize = serializers.IntegerField()
    snakeHead = NodeSerializer()  # Dùng NodeSerializer cho snakeHead
    snakeSegments = NodeSerializer(many=True)  # Dùng NodeSerializer cho snakeSegments
    foodPosition = NodeSerializer()  # Dùng NodeSerializer cho foodPosition
    obstaclePosition = NodeSerializer(many=True)  # Dùng NodeSerializer cho obstaclePosition
