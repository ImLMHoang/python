import random
from .serializers import NodeSerializer
# from .models import Node

class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.fVal = 0
        self.hVal = 0
        self.gVal = 0
        self.parent = None

    def to_dict(self):
        return {
            'row': self.row,
            'col': self.col,
            'fVal': self.fVal,
            'hVal': self.hVal,
            'gVal': self.gVal,
            'parent': str(self.parent) if self.parent else None  # Convert parent to string
        }
        
class SnakeLogic(object):
    def __init__(self):
        self.gameOver = False
        self.score = 0
        self.gameStarted = False
        self.canMove = True
        self.boardSize = 10
        self.snakeBoard = []
        self.snakeHead = None 
        self.snakeSegments = []
        self.direction = ""
        self.foodPosition = None
        self.obstaclePosition = []
        self.loadSnakeBoard(self.boardSize)
    
    def get_game_state(self):
        return {
            "gameOver": self.gameOver,
            "score": self.score,
            "gameStarted": self.gameStarted,
            "canMove": self.canMove,
            "boardSize": self.boardSize,
            "board": self.snakeBoard,
            "snakeHead": self.snakeHead.to_dict() if isinstance(self.snakeHead, Node) else self.snakeHead,
            "snakeSegments": [segment.to_dict() for segment in self.snakeSegments if isinstance(segment, Node)],
            "foodPosition": self.foodPosition.to_dict() if isinstance(self.foodPosition, Node) else self.foodPosition,
            "obstaclePosition": [obstacle.to_dict() for obstacle in self.obstaclePosition if isinstance(obstacle, Node)]
    }
        
    # THÊM 
    def load_from_state(self, state):
        self.gameOver = state["gameOver"]
        self.score = state["score"]
        self.gameStarted = state["gameStarted"]
        self.canMove = state["canMove"]
        self.boardSize = state["boardSize"]
        self.snakeBoard = state["board"]
        self.snakeHead = Node(state["snakeHead"]["row"], state["snakeHead"]["col"]) if state["snakeHead"] else None
        self.snakeSegments = [Node(segment["row"], segment["col"]) for segment in state["snakeSegments"]]
        self.foodPosition = Node(state["foodPosition"]["row"], state["foodPosition"]["col"]) if state["foodPosition"] else None
        self.obstaclePosition = [Node(obstacle["row"], obstacle["col"]) for obstacle in state["obstaclePosition"]]
    # THÊM

    def isGameRunning(self):
        return self.gameStarted and not self.gameOver

    def isA_StarGameRunning(self):
        return self.comp

    def getBoard(self):
        return self.snakeBoard

    def snakeLength(self): 
        """Mục tiêu hàm này là trả về giá trị hiện tại của rắn"""
        highestVal = 0
        for row in range(self.boardSize):
            for col in range(self.boardSize):
                highestVal = max(highestVal, self.snakeBoard[row][col])
        return highestVal

    def isGameOver(self, headRow, headCol):
        """Kiểm tra xem trò chơi kết thúc chưa
           1) Rắn đâm đầu vào tường
           2) Rắn tự đâm vào cơ thể của nó
           3) Rắn đâm vào chướng ngại vật
        """
        if headRow < 0 or headRow >= self.boardSize:
            self.gameOver = True
            
            # 
            print("Game over: Rắn đã va chạm với tường") # Debug
            # 
            
            return True
        if headCol < 0 or headCol >= self.boardSize:
            self.gameOver = True
            
            #
            print("Game over: Rắn đã va chạm với tường") # Debug
            # 
            
            return True
        if self.isCollidingWithSelf(headRow, headCol):
            self.gameOver = True
            
            #
            print("Game over: Rắn va chạm với thân") # Debug
            # 
            
            return True
        if self.isCollidingWithObstacles(headRow, headCol):
            self.gameOver = True
            
            #
            print("Game over: Rắn va chạm với chướng ngại vật")  # Debug
            # 
            
            return True
        return False

    def isCollidingWithSelf(self, headRow, headCol):
        """Kiểm tra đầu rắn với thân rắn có va chạm không"""
        self.setPositions() 
        for segment in self.snakeSegments:
            if segment['row'] == headRow and segment['col'] == headCol:
                return True
        return False
    
    def isCollidingWithObstacles(self, headRow, headCol):
        self.setPositions()
        if self.snakeBoard[headRow][headCol] == -3:
            return True
        return False

    def makeMove(self, direction):
        if not self.canMove:
            return
        self.direction = direction
        move_mapping = {
            "Left": (0, -1),
            "Right": (0, 1),
            "Up": (-1, 0),
            "Down": (1, 0)
        }
        if direction in move_mapping:
            row_diff, col_diff = move_mapping[direction]
            self.moveSnake(row_diff, col_diff)

    def loadSnakeBoard(self, size):
        """Khởi tạo danh sách 2D của snakeboard, đặt mặc định đầu rắn sẽ ở giữa màn hình
           thức ăn đặt rando
           0 = empty space
           -1 = food
           -3 = obstacle
           >1 = snake"""
        self.boardSize = size
        self.snakeBoard = [[0 for _ in range(size)] for _ in range(size)]
        mid = size // 2
        self.snakeHead = Node(mid, mid)  # Đặt vị trí đầu rắn
        self.snakeSegments = [self.snakeHead]  # Khởi tạo thân rắn chỉ với đầu rắn ban đầu
        self.snakeBoard[mid][mid] = 1 
        
        self.makeFood()
        self.makeObstacles()

    def setPositions(self):
        """đảm bảo rằng các logic di chuyển, kiểm tra va chạm, và tìm đường trong trò chơi hoạt động đúng cách"""
        maxVal = self.snakeLength()
        self.snakeSegments = []
        for row in range(self.boardSize):
            for col in range(self.boardSize):
                if self.snakeBoard[row][col] == maxVal:
                    self.snakeHead = Node(row, col).to_dict()
                elif self.snakeBoard[row][col] >= 1 and self.snakeBoard[row][col] < maxVal:
                    snakePart = Node(row, col).to_dict()
                    self.snakeSegments.append(snakePart)

    def removeTail(self):
        """rắn di chuyển mà không để lại dấu vết trên bảng"""
        for row in range(self.boardSize):
            for col in range(self.boardSize):
                if self.snakeBoard[row][col] > 0:
                    self.snakeBoard[row][col] -= 1

    def getScore(self):
        return self.score

    def moveSnake(self, rowDiff, colDiff):
        """ Kiểm tra vị trị mới đầu rắn có gây kết thức game không
            Kiểm tra xem đã ăn thức ăn chưa
        """
        if not self.gameOver:
            self.setPositions()
            newHeadRow = self.snakeHead['row'] + rowDiff
            newHeadCol = self.snakeHead['col'] + colDiff
            if self.isGameOver(newHeadRow, newHeadCol):
                self.gameOver = True
                return
            headRank = self.snakeLength()
            if self.snakeBoard[newHeadRow][newHeadCol] == -1:
                self.snakeBoard[newHeadRow][newHeadCol] = headRank + 1
                self.score += 1
                self.makeFood()
            else:
                self.removeTail()
                self.snakeBoard[newHeadRow][newHeadCol] = headRank

    def makeFood(self):
        """Tạo thức ăn cho 1 vị trí trống"""
        width = self.boardSize
        row, col = random.choice(range(width)), random.choice(range(width))
        # kiểm tra xem có phải ô trống không
        while self.snakeBoard[row][col] != 0:
            row, col = random.choice(range(width)), random.choice(range(width))
        self.snakeBoard[row][col] = -1
        self.foodPosition = Node(row, col)
        self.calculateManhattanBoard()

    def makeObstacles(self):
        """Tạo chướng ngại vật"""
        for _ in range(3): 
            width = self.boardSize
            row, col = random.choice(range(width)), random.choice(range(width))
            
            # Kiểm tra xem có phải là ô trống không
            while self.snakeBoard[row][col] != 0:
                row, col = random.choice(range(width)), random.choice(range(width))
            self.snakeBoard[row][col] = -3
            self.obstaclePosition.append(Node(row, col).to_dict())
            

    # A star Algorithm
    def calculateManhattanBoard(self):
        foodRow = self.foodPosition.row
        foodCol = self.foodPosition.col
        
        self.manhattanBoard = [[0 for _ in range(self.boardSize)] for _ in range(self.boardSize)]
        for row in range(self.boardSize):
            for col in range(self.boardSize):
                manhattan_distance = abs(foodRow - row) + abs(foodCol - col)
                self.manhattanBoard[row][col] = manhattan_distance

    def heuristic(self, node):
        """calculates manhattan distance from the node to the food"""
        # inf = float('inf') #để đánh dấu các nút k hợp lệ
        large_value = 999999  # Giá trị thay thế cho 'inf'
        for segment in self.snakeSegments:
            if node.row == segment['row'] and node.col == segment['col']:
                return large_value
        if node.row == self.snakeHead['row'] and node.col == self.snakeHead['col']:
            return large_value
        if self.snakeBoard[node.row][node.col] == -3:  # Chướng ngại vật
            return large_value
        return abs(node.row - self.foodPosition.row) + abs(node.col - self.foodPosition.col)


    def setNodeBoard(self):
        self.nodeBoard = [[Node(row, col) for col in range(self.boardSize)] for row in range(self.boardSize)]

    def neighborNodes(self, node):
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for row_diff, col_diff in directions:
            new_row, new_col = node.row + row_diff, node.col + col_diff
            if 0 <= new_row < self.boardSize and 0 <= new_col < self.boardSize:
                neighbor = self.nodeBoard[new_row][new_col]
                if self.isValidNode(neighbor):
                    neighbors.append(neighbor)
        return neighbors

    def isValidNode(self, node):
        """Kiểm tra cái node hiện tại có thỏa không (không va chạm với thân và chướng ngại vật)"""
        return self.snakeBoard[node.row][node.col] <= 0

    def findMinNode(self, nodes):
        """tìm node với fVal là nhỏ nhất"""
        return min(nodes, key=lambda node: node.fVal)
    

    #Hàm lưu trữ đường đi từ đích đến điểm bắt đầu đang xét
    def printPathList(self, end):
        self.pathList = []
        while end.parent is not None:
            node_dict = end.to_dict()
            # print("Debug Node:", node_dict)  // Debug
            
            # Loại bỏ các node không hợp lệ trước khi thêm vào pathList
            if node_dict['fVal'] != float('inf'):
                self.pathList.append(node_dict)
            end = end.parent
        self.pathList.reverse()
        return NodeSerializer(self.pathList, many=True).data
        # 

    def calculateAstar(self):
        self.pathList = [] #lưu trữ đường đi tìm đc
        self.setPositions()
        self.setNodeBoard()
        open_list, closed_list = [], []
        goal = Node(self.foodPosition.row, self.foodPosition.col)
        start_node = self.nodeBoard[self.snakeHead['row']][self.snakeHead['col']]
        start_node.gVal, start_node.hVal = 0, self.manhattanBoard[start_node.row][start_node.col]
        start_node.fVal = start_node.gVal + start_node.hVal
        open_list.append(start_node)
        while open_list:
            current = self.findMinNode(open_list)
            if current.row == goal.row and current.col == goal.col:
                return self.printPathList(current)
            
            open_list.remove(current)
            closed_list.append(current)
            
            for neighbor in self.neighborNodes(current):
                if neighbor in closed_list:
                    continue
                tentative_g = current.gVal + 1
                if neighbor not in open_list or tentative_g < neighbor.gVal:
                    neighbor.gVal, neighbor.parent = tentative_g, current
                    neighbor.hVal = self.heuristic(neighbor)
                    neighbor.fVal = neighbor.gVal + neighbor.hVal
                    if neighbor not in open_list:
                        open_list.append(neighbor)
                        
    def setDirection(self):
        if not self.pathList:
            self.gameOver = True
            return
        next_node = self.pathList.pop(0)
        row_diff, col_diff = next_node['row'] - self.snakeHead['row'], next_node['col'] - self.snakeHead['col']
        direction_map = {(0, -1): "Left", (0, 1): "Right", (-1, 0): "Up", (1, 0): "Down"}
        self.moveSnake(row_diff, col_diff)
        

    def stall(self):
        """Kiểm tra tất cả các hướng di chuyển có thể và chọn hướng an toàn nhất.
           Nếu không có hướng đi an toàn thì chọn 1 hướng ngẫu nhiên"""
        safe_moves = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for row_diff, col_diff in directions:
            new_row, new_col = self.snakeHead['row'] + row_diff, self.snakeHead['col'] + col_diff
            if 0 <= new_row < self.boardSize and 0 <= new_col < self.boardSize:
                if self.snakeBoard[new_row][new_col] <= 0:
                    safe_moves.append((row_diff, col_diff))
        if safe_moves:
            move = random.choice(safe_moves)
            self.moveSnake(*move)
        else:
            self.gameOver = True

# Sử dụng lớp SnakeLogic
game = SnakeLogic()
game.gameStarted = True
while not game.gameOver:
    path = game.calculateAstar()
    if path:
        game.setDirection()
    else:
        game.stall()
