from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SnakeLogicSerializer
from .snakeLogic import SnakeLogic 
from .firebase_helpers import save_player_history 
from firebase_admin import firestore
from django.http import JsonResponse


db = firestore.client()


def index(request):
    return render(request, 'index.html')
 
class LoginView(APIView):
    def post(self, request):
        name = request.data.get("name")
        email = request.data.get("email")

        if not name or not email:
            return Response({"error": "Name and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Tạo player_id từ email (chỉ lấy phần trước @)
        player_id = email.split('@')[0]

        # Lưu thông tin người chơi vào session
        request.session["player_id"] = player_id
        request.session["player_name"] = name
        request.session["player_email"] = email

        # print(f"Player ID: {player_id}, Name: {name}, Email: {email}")  # Debug

        return Response({"message": "Login successful", "player_id": player_id}, status=status.HTTP_200_OK)
    

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
        state = request.session.get('game_logic')
        if not state or not state['gameOver']:
            return Response({"error": "Game is still ongoing"}, status=status.HTTP_400_BAD_REQUEST)

        # Lấy thông tin từ session
        player_id = request.session.get("player_id", "guest")
        name = request.session.get("player_name", "Guest")
        email = request.session.get("player_email", "guest@example.com")

        # Lưu lịch sử vào Firebase
        save_player_history(player_id, name, email, state['score'])
        # print(f"GameOver - Player ID: {player_id}, Name: {name}, Email: {email}, Score: {state['score']}") // debug


        return Response({
            "gameOver": True,
            "score": state['score']
        }, status=status.HTTP_200_OK)


class PlayerHistoryView(APIView):
    def get(self, request):
        player_id = request.session.get('player_id', 'guest')
        doc_ref = db.collection('players').document(player_id)
        doc = doc_ref.get()

        if not doc.exists:
            return Response({"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(doc.to_dict(), status=status.HTTP_200_OK) 


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
        
        # # 
        # print("After restarting game:")
        # print("Score:", logic.score)
        # print("Game Over status:", logic.gameOver)
        # # debug

        # Lưu trạng thái trò chơi mới vào session
        request.session['game_logic'] = logic.get_game_state()
        request.session.modified = True

        # Trả về trạng thái mới của trò chơi và boardSize cho frontend
        return Response({
            "board": logic.getBoard(),
            # "score": 0,  # Đặt lại điểm về 0
            "score": logic.score,
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

class LeaderboardView(APIView):
    def get(self, request):
        try:
            # print("Fetching leaderboard data from Firestore...") # Debug
            # Lấy tất cả các document trong collection 'players'
            leaderboard_ref = db.collection('players')
            docs = leaderboard_ref.stream()

            leaderboard = []

            for doc in docs:
                data = doc.to_dict()
                name = data.get("name", "Unknown")
                history = data.get("history", [])

                # Lấy điểm cao nhất từ lịch sử
                highest_score = max([entry.get("score", 0) for entry in history], default=0)

                # Thêm vào danh sách leaderboard nếu có điểm
                if highest_score > 0:
                    leaderboard.append({
                        "name": name,
                        "score": highest_score
                    })

            # Sắp xếp theo điểm số giảm dần
            leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)

            # Chỉ trả về top 10
            leaderboard = leaderboard[:10]

            print("Final leaderboard data:", leaderboard)
            return JsonResponse({"leaderboard": leaderboard}, status=200)

        except Exception as e:
            print(f"Error fetching leaderboard: {e}")
            return JsonResponse({"error": "An error occurred while fetching the leaderboard."}, status=500)
