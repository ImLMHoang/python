from django.urls import path
from . import views

from .views import (
    CreateBoardView, GameOverView, SetSpeedView,
    GetBoardStateView, MoveSnakeView, AStarMoveView, RestartGameView, GetScoreView, LoginView, PlayerHistoryView, LeaderboardView
) 

urlpatterns = [
    path('', views.index, name='index'),
    path('api/create-board/', CreateBoardView.as_view(), name='create-board'),
    path('api/game-over/', GameOverView.as_view(), name='game-over'),
    path('api/set-speed/', SetSpeedView.as_view(), name='set-speed'),
    path('api/get-board-state/', GetBoardStateView.as_view(), name='get-board-state'),
    path('api/move/', MoveSnakeView.as_view(), name='move-snake'),
    path('api/a_star_move/', AStarMoveView.as_view(), name='a_star_move'),
    path('api/restart-game/', RestartGameView.as_view(), name='restart-game'),
    path('api/score/', GetScoreView.as_view(), name='get-score'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/player-history/', PlayerHistoryView.as_view(), name='player_history'),
    path('api/leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]