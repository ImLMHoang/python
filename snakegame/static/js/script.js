let boardSize = 10;  
let gameStarted = false;
let isAStarMode = false; 
let currentMode = null;
let isPaused = false;
let astarTimeout = null; // Biến lưu ID của timeout khi chạy A*
let autoMoveInterval = null; // Biến để lưu ID của interval
let currentDirection = null; // Lưu hướng hiện tại 
let scoreInterval = null;


// Hiển thị bảng trò chơi khi nhấn nút Start Game
function showGame() {
    resetGameState();
    document.getElementById("welcome-screen").style.display = "none";
    document.getElementById("game-screen").style.display = "block";
    startGame();
    fetchLeaderboard(); 
}

function resetGameState() {
    resetModeSelection();
    isPaused = false;

    // Dừng các interval hoặc timeout
    if (autoMoveInterval) clearInterval(autoMoveInterval);
    if (astarTimeout) clearTimeout(astarTimeout);
    stopScoreUpdate();

    // Đặt lại điểm số hiển thị về 0
    document.getElementById("score-display").textContent = "0";
}


function startAutoMove() {
    if (autoMoveInterval) {
        clearInterval(autoMoveInterval); // Đảm bảo không chạy nhiều interval
    }
    autoMoveInterval = setInterval(() => {
        if (gameStarted && currentDirection) {
            handleAutoMove(currentDirection);
        }
    }, 200); // Tốc độ di chuyển: 200ms
}


// Hàm xử lý di chuyển tự động
async function handleAutoMove(direction) {
    // Gửi yêu cầu đến API MoveSnakeView
    const response = await fetch('/api/move/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ direction: direction })
    });

    const data = await response.json();
    renderBoard(data.board);

    if (data.gameOver) {
        gameOver(data.score); // Xử lý khi kết thúc trò chơi
        clearInterval(autoMoveInterval); // Dừng tự động di chuyển
    }
}


// Khởi tạo trò chơi mới
async function startGame() {
    stopScoreUpdate(); // Đảm bảo không còn interval nào trước đó
    const response = await fetch('/api/create-board/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ boardSize: boardSize })  // Truyền boardSize từ giao diện người dùng
    });

    if (response.ok) {  // Kiểm tra xem API trả về kết quả thành công hay không
        const data = await response.json();
        renderBoard(data.board);  // Gọi hàm renderBoard để hiển thị bảng
        // Hiển thị boardSize
        document.getElementById("board-size-display").innerText = "Board Size: " + data.boardSize;
        gameStarted = true;
        currentDirection = null; // Đặt lại hướng khi bắt đầu mới
        startScoreUpdate();
    } else {
        console.error("Error in creating board:", response.status);
    }
}

// Vẽ bảng trò chơi
function renderBoard(board) {
    console.log("Board data:", board);
    const gameBoard = document.getElementById("game-board");
    gameBoard.style.gridTemplateColumns = `repeat(${boardSize}, 30px)`;
    gameBoard.style.gridTemplateRows = `repeat(${boardSize}, 30px)`;
    gameBoard.innerHTML = "";  // Xóa bảng hiện tại
    let maxSnakeValue = 0;
    board.forEach(row => {
        row.forEach(cellValue => {
            if (cellValue > maxSnakeValue) maxSnakeValue = cellValue;
        });
    });

    // Vẽ lại bảng
    board.forEach((row, rowIndex) => {
        row.forEach((cellValue, colIndex) => {
            const cell = document.createElement("div");
            cell.classList.add("cell");

            if (cellValue > 0) {
                // Phần đầu rắn
                if (cellValue === maxSnakeValue) {
                    cell.classList.add("snake-head");
                    console.log(`Snake head at (${rowIndex}, ${colIndex})`);
                }
                // Phần thân rắn
                else {
                    console.log(`Snake body at (${rowIndex}, ${colIndex})`);
                    cell.classList.add("snake-body");
                }
            } else if (cellValue === -1) {
                cell.classList.add("food");
            } else if (cellValue === -3) {
                cell.classList.add("obstacle");
            }

            console.log(`Cell at (${rowIndex}, ${colIndex}):`, cell); // Debug
            gameBoard.appendChild(cell);
        });
    });
}


async function resetBoardSize() {
    const newSize = document.getElementById("board-size").value;
    boardSize = Math.min(14, Math.max(10, newSize)); // Đảm bảo kích thước hợp lệ
    resetModeSelection();

    // Đặt lại điểm số
    document.getElementById("score-display").textContent = "0";

    // Gửi yêu cầu để tạo bảng mới
    try {
        const response = await fetch('/api/create-board/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ boardSize: boardSize }),
        });

        if (response.ok) {
            const data = await response.json();
            renderBoard(data.board); // Vẽ lại bảng mới
            document.getElementById("board-size-display").innerText = "Board Size: " + data.boardSize;
        } else {
            console.error('Error in creating board:', response.status);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}


// Chế độ người chơi
function startPlayerMode() {
    if (currentMode === "a_star") {
        alert("Bạn không thể chuyển sang chế độ Người chơi khi A* đang chạy.");
        return;
    }
    currentMode = "player";
    highlightSelectedMode("player");
    isAStarMode = false;
    if (astarTimeout) {
        clearTimeout(astarTimeout); // Dừng A* nếu đang chạy
        astarTimeout = null; // Đặt lại giá trị
    }
    gameStarted = true;
    startScoreUpdate(); 
    document.addEventListener("keydown", handleKeyPress); // Cho phép di chuyển
}


// Chế độ AI (A* Run)
function startAStarMode() {
    if (currentMode === "player") {
        alert("Bạn không thể chuyển sang chế độ A* khi đang ở chế độ Người chơi.");
        return;
    }
    currentMode = "a_star";
    highlightSelectedMode("astar");
    isAStarMode = true;
    gameStarted = true;
    startScoreUpdate();
    runAStarMode();
}
 
function gameOver(score) {
    fetch("/api/game-over/", {
        method: "GET"
    }).then(response => response.json())
      .then(data => {
          if (data.gameOver) {
              console.log("Game over data:", data);
          } else {
              console.error("Game over API did not return gameOver status.");
          }
      }).catch(error => {
          console.error("Error in game-over API:", error);
      });

    // Hiển thị thông báo Game Over và hỏi người chơi có muốn chơi lại không
    if (confirm("Game Over! Your score: " + score + "\nDo you want to restart?")) {
        document.getElementById("score-display").textContent = "0";
        restartGame();
    } else {
        resetGameState();
        document.getElementById("welcome-screen").style.display = "block";
        document.getElementById("game-screen").style.display = "none";
        stopScoreUpdate();
        currentMode = null;
    }
    fetchLeaderboard();
}

// Điều khiển rắn với A*
async function runAStarMode() {
    if (isAStarMode && gameStarted) {
        const response = await fetch('/api/a_star_move/', { method: 'POST' });
        const data = await response.json();
        renderBoard(data.board);
        if (data.gameOver) {
        // console.log("Game over detected in frontend with score:", data.score); // Debug
        gameOver(data.score);  // Gọi hàm gameOver để xử lý kết thúc trò chơi
        gameStarted = false;

        } else {
            setTimeout(runAStarMode, 200);  // Tiếp tục di chuyển với độ trễ
        }
    }
}

// Xử lý di chuyển với sự kiện bàn phím
async function handleKeyPress(event) {
    if (!gameStarted || isAStarMode ) return;

    const directionMap = {
        ArrowUp: "Up",
        ArrowDown: "Down",
        ArrowLeft: "Left",
        ArrowRight: "Right"
    };
    const direction = directionMap[event.key];

    if (direction) {
        currentDirection = direction; // Lưu hướng hiện tại
        startAutoMove(); // Bắt đầu tự động di chuyển
    } 
}


async function restartGame() {
    document.getElementById("score-display").textContent = "0";
    resetModeSelection(); 

    if (astarTimeout) {
        clearTimeout(astarTimeout); // Dừng timeout của A*
        astarTimeout = null;
    }

    stopScoreUpdate(); // Đảm bảo không còn interval nào trước đó
    // console.log("Sending request to restart game..."); // Debug 

    try {
        const response = await fetch('/api/restart-game/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            const data = await response.json(); // Lấy dữ liệu JSON từ response
            // console.log("Restart data:", data); // Debug 

            console.log("Restart response:", data);

            renderBoard(data.board);
            document.getElementById("board-size-display").textContent = "Board Size: " + data.boardSize;

            if (data.score === 0) {
                document.getElementById("score-display").textContent = "0"; // Đặt lại điểm
            } else {
                document.getElementById("score-display").textContent = data.score || "0"; // Fallback
            }

            currentMode = null; // Đặt lại chế độ chơi
            fetchLeaderboard();
            
        } else {
            console.error("Error in restarting game:", response.status);
        }
    } catch (error) {
        console.error("Error in restartGame fetch call:", error);
    }
}


function togglePause() {
    if (!currentMode) {
        alert("Vui lòng chọn một chế độ (Người chơi hoặc A*) để bắt đầu trò chơi.");
        return;
    }

    if (currentMode === "player") {
        isPaused = !isPaused;  // Chuyển đổi trạng thái tạm dừng

        if (isPaused) {
            document.removeEventListener("keydown", handleKeyPress); // Tắt điều khiển
            alert("Trò chơi đã tạm dừng.");
        } else {
            document.addEventListener("keydown", handleKeyPress); // Bật lại điều khiển
            alert("Tiếp tục trò chơi.");
        }
    }

    if (currentMode === "a_star") {
        // Tạo thông báo và thêm vào giao diện
        const messageBox = document.createElement("div");
        messageBox.innerText = "Không thể tạm dừng trong chế độ A*.";
        messageBox.style.position = "fixed";
        messageBox.style.top = "20px";
        messageBox.style.right = "20px";
        messageBox.style.backgroundColor = "rgba(0, 0, 0, 0.7)";
        messageBox.style.color = "white";
        messageBox.style.padding = "10px";
        messageBox.style.borderRadius = "5px";
        messageBox.style.zIndex = "1000";
        document.body.appendChild(messageBox);

        // Tự động xóa thông báo sau 5 giây
        setTimeout(() => {
            document.body.removeChild(messageBox);
        }, 5000);
    }
}

function highlightSelectedMode(mode) {
    resetModeHighlight(); 

    // Lấy danh sách tất cả các nút chế độ
    const modeButtons = document.querySelectorAll(".mode-buttons button");

    if (mode === "player") {
        modeButtons[0].classList.add("selected"); // Nút "Người chơi"
    } else if (mode === "a_star") {
        modeButtons[1].classList.add("selected"); // Nút "A*"
    }
}

function resetModeHighlight() {
    const modeButtons = document.querySelectorAll(".mode-buttons button");
    modeButtons.forEach(button => button.classList.remove("selected"));
}


// Từ moveSnake (snakeLogic.py)
function updateScore() { 
    if (!gameStarted) return;

    fetch("/api/score") // Gọi API để lấy điểm từ backend
        .then(response => response.json())
        .then(data => {
            const scoreDisplay = document.getElementById("score-display");
            scoreDisplay.textContent = data.score; // Cập nhật điểm số trên giao diện
            document.getElementById("score-display").textContent = data.score || "0";
        })
        .catch(error => console.error("Lỗi khi cập nhật điểm số:", error));
}

// Quản lý gọi updateScore() định kỳ
function startScoreUpdate() {
    if (scoreInterval) return; // Nếu interval đang chạy, không tạo mới
    scoreInterval = setInterval(() => {
        if (gameStarted && (currentMode === "player" || currentMode === "a_star")) {
            updateScore(); // Chỉ cập nhật điểm khi game đang chạy và đã chọn chế độ 
        } else {
            stopScoreUpdate(); // Dừng nếu không cần thiết
        }
    }, 500); // Cập nhật điểm mỗi 500ms
}

function stopScoreUpdate() {
    if (scoreInterval) {
        clearInterval(scoreInterval); // Dừng interval
        scoreInterval = null;
    }
}


async function fetchPlayerHistory() {
    const response = await fetch("/api/player-history/");
    const data = await response.json();

    if (data.error) {
        console.error("Error fetching player history:", data.error);
        return;
    }

    const history = data.history;
    const historyContainer = document.getElementById("history-container");
    historyContainer.innerHTML = ""; // Xóa lịch sử cũ

    history.forEach(entry => {
        const historyItem = document.createElement("div");
        historyItem.textContent = `Date: ${entry.date}, Score: ${entry.score}`;
        historyContainer.appendChild(historyItem);
    });

    document.getElementById("player-history").style.display = "block";
}

// Hàm xử lý đăng nhập
function login(event) {
    event.preventDefault();

    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;

    // Gửi yêu cầu đăng nhập tới backend
    fetch("/api/login/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ name, email }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.message === "Login successful") {
                // Hiển thị màn hình welcome khi đăng nhập thành công
                document.getElementById("login-screen").style.display = "none";
                document.getElementById("welcome-screen").style.display = "block";
            } else {
                alert("Login failed. Please try again.");
            }
        })
        .catch((error) => {
            console.error("Error during login:", error);
            alert("An error occurred. Please try again.");
        });
}

async function fetchLeaderboard() {
    try {
        // console.log("Fetching leaderboard data..."); // Debug

        const response = await fetch("/api/leaderboard/");
        // console.log("Response status:", response.status); // Debug

        if (!response.ok) {
            // console.error("Failed to fetch leaderboard:", response.status); // Debug
            return;
        }

        const data = await response.json();
        // console.log("API response data:", data); // Debug

        // Giả sử API trả về một object với key 'leaderboard'
        const leaderboard = data.leaderboard || data;

        if (!Array.isArray(leaderboard)) {
            // console.error("Error: Leaderboard is not an array:", leaderboard); // Debug
            return;
        }

        // console.log("Leaderboard data received:", leaderboard); // Debug

        const leaderboardBody = document.getElementById("leaderboard-body");
        if (!leaderboardBody) {
            // console.error("Element with id 'leaderboard-body' not found!"); // Debug
            return;
        }

        leaderboardBody.innerHTML = "";
        leaderboard.forEach((entry, index) => {
            // console.log(`Rendering rank: ${index + 1}, name: ${entry.name}, score: ${entry.score}`); // Debug

            const row = document.createElement("tr");
            const rankCell = document.createElement("td");
            const nameCell = document.createElement("td");
            const scoreCell = document.createElement("td");

            rankCell.textContent = index + 1;
            nameCell.textContent = entry.name;
            scoreCell.textContent = entry.score;

            row.appendChild(rankCell);
            row.appendChild(nameCell);
            row.appendChild(scoreCell);
            leaderboardBody.appendChild(row);
        });

        // console.log("Final leaderboard content:", leaderboardBody.innerHTML); // Debug
    } catch (error) {
        // console.error("Error fetching leaderboard:", error); // Debug
    }
}


// Chế độ người chơi
function togglePlayerMode() {
    if (currentMode === "player") {
        resetModeSelection(); // Nếu đang chọn chế độ này, hủy chế độ
        console.log("Player mode deselected");
    } else {
        resetModeSelection(); // Đặt lại các chế độ trước đó
        currentMode = "player"; // Bật chế độ người chơi
        highlightSelectedMode("player");
        isAStarMode = false; // Đảm bảo chế độ A* không hoạt động
        gameStarted = true;
        console.log("Player mode selected");
        startScoreUpdate(); // Bắt đầu cập nhật điểm
        document.addEventListener("keydown", handleKeyPress); // Kích hoạt bàn phím
    }
}

// Chế độ A* Run
function toggleAStarMode() {
    if (currentMode === "a_star") {
        resetModeSelection(); // Nếu đang chọn chế độ này, hủy chế độ
        console.log("A* mode deselected");
    } else {
        resetModeSelection(); // Đặt lại các chế độ trước đó
        currentMode = "a_star"; // Bật chế độ AI
        highlightSelectedMode("a_star");
        isAStarMode = true;
        gameStarted = true;
        console.log("A* mode selected");
        startScoreUpdate(); // Bắt đầu cập nhật điểm
        runAStarMode(); // Chạy AI
    }
}

function resetModeSelection() {
    currentMode = null; // Xóa trạng thái chế độ hiện tại
    resetModeHighlight(); // Xóa class "selected" của các nút
    isAStarMode = false; // Đảm bảo chế độ AI tắt
    document.removeEventListener("keydown", handleKeyPress); // Gỡ sự kiện bàn phím
    stopScoreUpdate(); // Dừng cập nhật điểm
}