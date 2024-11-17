from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SnakeLogicSerializer
from .snakeLogic import SnakeLogic 

def index(request):
    return render(request, 'index.html')

class CreateBoardView(APIView):
    def post(self, request):
        board_size = request.data.get("boardSize", 10)
        
        # Kiểm tra điều kiện kích thước bảng
        if not (10 <= board_size <= 14):
            return Response({"error": "Board size must be between 10 and 14"}, status=status.HTTP_400_BAD_REQUEST)

        # Khởi tạo logic của trò chơi
        logic = SnakeLogic()
        logic.loadSnakeBoard(board_size)
        
        request.session['boardSize'] = board_size
        request.session['game_logic'] = logic.get_game_state()

        response_data = logic.get_game_state()
        return Response(response_data, status=status.HTTP_200_OK)

        
class GameOverView(APIView):
    def get(self, request):
        logic = request.session.get('game_logic')
        if not logic or not logic.gameOver:
            return Response({"error": "Game is still ongoing"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "gameOver": True,
            "score": logic.getScore()
        }, status=status.HTTP_200_OK)

class SetSpeedView(APIView):
    def post(self, request):
        speed = request.data.get("speed", 60)  # Độ trễ: 80ms
        request.session['speed'] = speed  # Lưu trữ tốc độ để frontend sử dụng
        return Response({
            "message": "Speed set successfully",
            "speed": speed
        }, status=status.HTTP_200_OK)

class GetBoardStateView(APIView):
    def get(self, request):
        logic = request.session.get('game_logic')
        if not logic:
            return Response({"error": "Game not started"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "board": logic.getBoard(),
            "snakeSegments": logic.snakeSegments,
            "foodPosition": logic.foodPosition,
            "obstaclePositions": logic.obstaclePosition
        }, status=status.HTTP_200_OK)

class MoveSnakeView(APIView):
    def post(self, request):
        direction = request.data.get("direction")
        
        state = request.session.get('game_logic')
        # print("Direction received:", direction) # Debug

        if not state:
            # print("Game not started")  # Debug
            return Response({"error": "Game not started"}, status=status.HTTP_400_BAD_REQUEST)

        logic = SnakeLogic()
        logic.load_from_state(state)
        # print("Game Over status before move:", logic.gameOver) # Debug

         
        if logic.gameOver:
            # print("Game is already over, returning response.") # Debug
            return Response({"error": "Game is over"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Cập nhật hướng di chuyển và di chuyển rắn
        logic.makeMove(direction)
        # print("Game Over status after move:", logic.gameOver) # Debug
        # print("Score after move:", logic.getScore()) # Debug

        
        # Lưu trạng thái trò chơi sau khi di chuyển vào session
        request.session['game_logic'] = logic.get_game_state()
        request.session['boardSize'] = logic.boardSize 
        
        return Response({
            "board": logic.getBoard(),
            "gameOver": logic.gameOver,
            "score": logic.getScore()
        }, status=status.HTTP_200_OK)


class AStarMoveView(APIView):
    def post(self, request):
        state = request.session.get('game_logic')
        print("Session data:", request.session)
        
        # Kiểm tra nếu game chưa bắt đầu hoặc đã kết thúc
        if not state:
            return Response({"error": "Game not started"}, status=status.HTTP_400_BAD_REQUEST)

        # Tạo lại đối tượng logic từ trạng thái lưu trữ
        logic = SnakeLogic()
        logic.load_from_state(state)

        # Kiểm tra trạng thái game-over
        if logic.gameOver:
            # print("Game Over detected on backend with score:", logic.getScore()) # Debug
            return Response({"error": "Game is over"}, status=status.HTTP_400_BAD_REQUEST)

        # Thực hiện thuật toán A*
        path = logic.calculateAstar()  # Tìm đường đi tới thức ăn
        if path:
            logic.setDirection()  # Di chuyển rắn theo đường đi được tìm thấy
        else:
            logic.stall()  # Chọn hướng an toàn nếu không có đường trực tiếp

        # Lưu trạng thái trò chơi vào session sau khi thay đổi
        request.session['game_logic'] = logic.get_game_state()
        request.session['boardSize'] = logic.boardSize
        
        return Response({
            "board": logic.getBoard(),
            "gameOver": logic.gameOver,
            "score": logic.getScore()
        }, status=status.HTTP_200_OK)
        

class RestartGameView(APIView):
    def post(self, request):
        # Lấy boardSize từ session hoặc thiết lập mặc định là 10 nếu chưa có
        board_size = request.session.get('boardSize', 10)

        # Tạo lại logic của trò chơi với boardSize từ session
        logic = SnakeLogic()
        logic.loadSnakeBoard(board_size)

        # Lưu trạng thái trò chơi mới vào session
        request.session['game_logic'] = logic.get_game_state()

        # Trả về trạng thái mới của trò chơi và boardSize cho frontend
        return Response({
            "board": logic.getBoard(),
            "score": 0,  # Đặt lại điểm về 0
            "boardSize": board_size
        }, status=status.HTTP_200_OK)


class GetScoreView(APIView):
    def get(self, request):
        # Lấy trạng thái trò chơi từ session
        state = request.session.get('game_logic')

        if not state:
            return Response({"error": "Game not started"}, status=status.HTTP_400_BAD_REQUEST)

        # Tạo lại đối tượng logic từ trạng thái lưu trữ
        logic = SnakeLogic()
        logic.load_from_state(state)

        # Trả về điểm số hiện tại
        return Response({"score": logic.getScore()}, status=status.HTTP_200_OK)

